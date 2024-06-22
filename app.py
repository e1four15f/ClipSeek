from pathlib import Path

import numpy as np
import streamlit as st
from streamlit.runtime.media_file_storage import MediaFileStorageError

from src import config as cfg
from src.embedder import IEmbedder, LanguageBindEmbedder, Modality, RandomEmbedder
from src.retriever import FaissMediaRetriever, MilvusMediaRetriever, MultipleRetrievers


def main() -> None:
    st.set_page_config(layout="wide")
    if "query" not in st.session_state:
        st.session_state.query = "Cat in black suit is having meeting"

    if "modality" not in st.session_state:
        st.session_state.modality = Modality.TEXT

    embedder = load_embedder()
    retriever = load_retriever()

    render(embedder=embedder, retriever=retriever)


def render(embedder: IEmbedder, retriever: MultipleRetrievers) -> None:
    st.title("Video Search")
    if cfg.DEBUG:
        st.title("Debug Info")
        st.write(embedder, retriever)
        st.write("Session State")
        st.write(st.session_state)

    search_inputs, search_settings = st.columns([4, 1])

    with search_inputs:
        query = st.text_input("Query:", key="query")

    with search_settings:
        st.write("#### Settings")
        search_datasets, search_representation = st.columns(2)
        with search_datasets:
            st.write("**Datasets**")
            selected_datasets = []
            for d in cfg.DATASETS:
                is_selected = st.checkbox(f"{d['dataset']}[{d['version']}]", value=True)
                selected_datasets.append(is_selected)

        with search_representation:
            st.write("**Representation**")
            modalities = {
                modality: st.checkbox(modality, value=modality == Modality.HYBRID)
                for modality in [
                    Modality.HYBRID,
                    Modality.VIDEO,
                    Modality.IMAGE,
                    Modality.AUDIO,
                    # Modality.TEXT, TODO bm25 embeddings also?
                ]
            }
            selected_modalities = [modality for modality, mask in modalities.items() if mask]

    if query:
        # Search for videos based on query
        if ".jpg" in query:
            st.session_state.modality = Modality.IMAGE
            show_query = st.image
        elif ".mp4" in query:
            st.session_state.modality = Modality.VIDEO
            show_query = st.video
        else:
            st.session_state.modality = Modality.TEXT
            show_query = st.text

        st.write(f'#### Search results using "{st.session_state.modality}" modality')
        l, r = st.columns([1, 6])  # noqa
        with l:
            show_query(query)

        st.html("<hr>")

        query_embedding = embedder.embed(query, modality=st.session_state.modality)
        candidates = retriever.retrieve(
            query_embedding.detach().numpy(),
            ignore_retrievers=selected_datasets,
            modalities=selected_modalities,
            k=cfg.CANDIDATES_PER_PAGE,
        )

        def update(filename: str) -> None:
            st.session_state.query = filename

        if candidates:
            n_cols = 4
            n_rows = len(candidates) // int(n_cols)
            rows = [st.container() for _ in range(n_rows)]
            cols_per_row = [r.columns(n_cols) for r in rows]
            cols = [column for row in cols_per_row for column in row]

            for i, candidate in enumerate(candidates):
                filename, score, modality = candidate
                with cols[i]:
                    try:
                        if modality == Modality.VIDEO or "mp4" in filename:
                            st.video(filename)
                        elif modality == Modality.IMAGE or "jpg" in filename:
                            st.image(filename)
                        elif modality == Modality.AUDIO:
                            st.audio(filename)
                        else:
                            raise MediaFileStorageError("Unknown format")
                    except MediaFileStorageError:
                        st.write("X")

                    l, r = st.columns([6, 1])  # noqa
                    with l:
                        st.write(f"Filename: {filename}\n\n" f"Score: {score:.4f}\n\n" f"Modality: {modality}")
                    with r:
                        st.button(
                            "🔍",
                            type="primary",
                            key=f"SimBtn{i}",
                            on_click=update,
                            args=(filename,),
                        )

        else:
            st.write("No videos found for the query:", query)


@st.cache_resource()
def load_embedder() -> IEmbedder:
    if cfg.USE_DUMMY_MODEL:
        return RandomEmbedder(embeddings_dim=cfg.EMBEDDINGS_DIM)
    return LanguageBindEmbedder(models=cfg.CLIP_MODELS, device=cfg.DEVICE)


# @st.cache_resource()
# def load_retriever() -> MultipleRetrievers:
#     return MultipleRetrievers(
#         retrievers=[
#             get_retriever(
#                 dataset_path=DATASETS_PATH / d["dataset"],
#                 version=d["version"],
#                 modality=d["modality"],
#                 device=DEVICE,
#             )
#             for d in DATASETS
#         ]
#     )


@st.cache_resource()
def load_retriever() -> MultipleRetrievers:
    return MultipleRetrievers(
        retrievers=[
            get_milvus_retriever(
                dataset_name=f'{d["dataset"]}_{d["version"]}',
                dataset_path=cfg.DATASETS_PATH / d["dataset"],
                version=d["version"],
                modalities=d["modalities"],
                device=cfg.DEVICE,
            )
            for d in cfg.DATASETS
        ]
    )


def get_faiss_retriever(dataset_path: Path, version: str, modality: str, device: str) -> FaissMediaRetriever:
    index_path = dataset_path / "index" / version
    index_embeddings = np.load(index_path / f"{modality}_embeddings.npy")
    labels = [str(dataset_path / s) for s in (index_path / "labels.txt").open().read().splitlines()]
    return FaissMediaRetriever(embeddings=index_embeddings, labels=labels, device=device)


def get_milvus_retriever(
    dataset_name: str, dataset_path: Path, version: str, modalities: tuple[str], device: str
) -> MilvusMediaRetriever:
    index_path = dataset_path / "index" / version
    index_embeddings = {modality: np.load(index_path / f"{modality}_embeddings.npy") for modality in modalities}
    if len(modalities) > 1:
        index_embeddings[Modality.HYBRID] = np.mean(list(index_embeddings.values()), axis=0)

    labels = [str(dataset_path / s) for s in (index_path / "labels.txt").open().read().splitlines()]
    return MilvusMediaRetriever(
        url=cfg.MILVUS_URL,
        database_name=cfg.MILVUS_DB_NAME,
        index_name=dataset_name,
        modality_embeddings=index_embeddings,  # noqa
        embeddings_dim=cfg.EMBEDDINGS_DIM,
        labels=labels,
        device=device,
    )


if __name__ == "__main__":
    main()

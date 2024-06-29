from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import streamlit as st

from src import config as cfg
from src.custom_components import component_scroller
from src.embedder import IEmbedder, LanguageBindEmbedder, Modality, RandomEmbedder
from src.retriever import FaissMediaRetriever, MilvusMediaRetriever, MultipleRetrievers


def main() -> None:
    st.set_page_config(page_title="HERE", page_icon="🔥", layout="wide", initial_sidebar_state="auto")
    if "query" not in st.session_state:
        st.session_state.query = "Cat in black suit is having meeting"

    if "modality" not in st.session_state:
        st.session_state.modality = Modality.TEXT

    embedder = load_embedder()
    retriever = load_retriever()

    render(embedder=embedder, retriever=retriever)


def render(embedder: IEmbedder, retriever: MultipleRetrievers) -> None:
    with st.sidebar:
        st.title("Video Search")
        if cfg.DEBUG:
            st.title("Debug Info")
            st.write(embedder, retriever)
            st.write("Session State")
            st.write(st.session_state)

        query = st.text_input("Query:", key="query")

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

        # st.write(f'#### Search results using "{st.session_state.modality}" modality')
        # l, r = st.columns([1, 6])  # noqa
        # with l:
        #     show_query(query)
        #
        # st.html("<hr>")

        candidates = retrieve_candidates(
            embedder=embedder,
            retriever=retriever,
            query=query,
            selected_modalities=selected_modalities,
            selected_datasets=selected_datasets,
        )

        def update(filename: str) -> None:
            st.session_state.query = filename

        if candidates:
            props = {
                "media": [
                    {"src": filename, "dataContent": {"Modality": modality, "Score": score}}
                    for filename, score, modality in candidates
                ],
                "n_cols": cfg.N_RESULT_COLUMNS,
                "resources_url": urljoin(cfg.BACKEND_URL, '/resources')
            }
            print("Creating scroller component")
            value = component_scroller(key="scroller", **props)

        #     n_cols = 4
        #     n_rows = len(candidates) // int(n_cols)
        #     rows = [st.container() for _ in range(n_rows)]
        #     cols_per_row = [r.columns(n_cols) for r in rows]
        #     cols = [column for row in cols_per_row for column in row]
        #
        #     for i, candidate in enumerate(candidates):
        #         filename, score, modality = candidate
        #         with cols[i]:
        #             # Create the media HTML content
        #             if modality == "VIDEO" or "mp4" in filename:
        #                 media_html = f'<video controls style="width:100%; height:auto;"><source src="{filename}" type="video/mp4"></video>'
        #             elif modality == "IMAGE" or "jpg" in filename:
        #                 media_html = f'<img src="{filename}" alt="Detailed Image" style="width:100%; height:auto;">'
        #             elif modality == "AUDIO":
        #                 media_html = f'<audio controls style="width:100%;"><source src="{filename}" type="audio/mpeg"></audio>'
        #             else:
        #                 media_html = "<p>Unknown format</p>"
        #
        #             # Format the modal HTML with the candidate data
        #             modal_html = modal_template.format(index=i, filename=filename, media=media_html)

        # Render the HTML component
        # components.html(modal_html, height=400, width=300)

        #     modal = Modal(
        #         "",
        #         key=f"media-modal-{i}",
        #         # Optional
        #         padding=-200,  # default value
        #         max_width=744,  # default value
        #     )
        #     open_modal = st.button("Open", key=f"OpenBtn{i}")
        #     if open_modal:
        #         modal.open()
        #     try:
        #         if modal.is_open():
        #             with modal.container():
        #                 if modality == Modality.VIDEO or "mp4" in filename:
        #                     st.video(filename)
        #                 elif modality == Modality.IMAGE or "jpg" in filename:
        #                     st.image(filename)
        #                 elif modality == Modality.AUDIO:
        #                     st.audio(filename)
        #                 else:
        #                     raise MediaFileStorageError("Unknown format")
        #         else:
        #             st.write("Thumbnail")
        #     except MediaFileStorageError:
        #         st.write("X")
        #
        #     l, r = st.columns([6, 1])  # noqa
        #     with l:
        #         st.write(f"Filename: {filename}\n\n" f"Score: {score:.4f}\n\n" f"Modality: {modality}")
        #     with r:
        #         st.button(
        #             "🔍",
        #             type="primary",
        #             key=f"SimBtn{i}",
        #             on_click=update,
        #             args=(filename,),
        #         )

        else:
            st.write("No videos found for the query:", query)


def retrieve_candidates(
    embedder: IEmbedder,
    retriever: MultipleRetrievers,
    query: str,
    selected_modalities: list[str],
    selected_datasets: list[int],
) -> list[tuple[str, float]]:
    @st.cache_data()
    def _cached_retrieve(query: str, modalities: list[str], ignore_retrievers: list[int]) -> list[tuple[str, float]]:
        query_embedding = embedder.embed(query, modality=st.session_state.modality)
        return retriever.retrieve(
            query_embedding.detach().numpy(),
            ignore_retrievers=ignore_retrievers,
            modalities=modalities,
            k=cfg.CANDIDATES_PER_PAGE,
        )

    return _cached_retrieve(query=query, modalities=selected_modalities, ignore_retrievers=selected_datasets)


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

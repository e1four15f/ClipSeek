from pathlib import Path

import numpy as np
import streamlit as st
from streamlit.runtime.media_file_storage import MediaFileStorageError

from src.config import DATASETS_PATH, DATASETS, CANDIDATES_PER_PAGE, DEVICE, CLIP_MODELS
from src.embedder import LanguageBindEmbedder, Modality
from src.retriever import VideoRetriever, MultipleRetrievers


def main() -> None:
    st.set_page_config(layout="wide")
    if 'query' not in st.session_state:
        st.session_state.query = "Cat in black suit is having meeting"

    if 'modality' not in st.session_state:
        st.session_state.modality = Modality.TEXT

    embedder = load_embedder()
    retriever = load_retriever()

    render(embedder=embedder, retriever=retriever)


def render(embedder: LanguageBindEmbedder, retriever: MultipleRetrievers) -> None:
    st.title("Video Search")
    # st.write(DATASETS)
    # st.write(st.session_state)
    search_left, search_right = st.columns([3, 1])

    with search_left:
        query = st.text_input("Query:", key="query")

    with search_right:
        st.write("#### Datasets")
        datasets_mask = []
        for d in DATASETS:
            agree = st.checkbox(f"{d['dataset']}[{d['version']}]", value=True)
            datasets_mask.append(agree)

    if query:
        # Search for videos based on query
        if '.jpg' in query:
            st.session_state.modality = Modality.IMAGE
            show_query = st.image
        elif '.mp4' in query:
            st.session_state.modality = Modality.VIDEO
            show_query = st.video
        else:
            st.session_state.modality = Modality.TEXT
            show_query = st.text

        st.write(f'#### Search results using "{st.session_state.modality}" modality')
        l, r = st.columns([1, 6])  # noqa
        with l:
            show_query(query)

        st.html('<hr>')

        query_embedding = embedder.embed(query, modality=st.session_state.modality)
        candidates = retriever.retrieve(
            query_embedding.detach().numpy(),
            ignore_retrievers=datasets_mask,
            k=CANDIDATES_PER_PAGE
        )

        def update(filename):
            st.session_state.query = filename

        if candidates:
            n_cols = 4
            n_rows = len(candidates) // int(n_cols)
            rows = [st.container() for _ in range(n_rows)]
            cols_per_row = [r.columns(n_cols) for r in rows]
            cols = [column for row in cols_per_row for column in row]

            for i, candidate in enumerate(candidates):
                filename, score = candidate
                with cols[i]:
                    try:
                        if 'mp4' in filename:
                            st.video(filename)
                        elif 'jpg' in filename:
                            st.image(filename)
                        else:
                            raise MediaFileStorageError('Unknown format')
                    except MediaFileStorageError:
                        st.write("X")

                    l, r = st.columns([6, 1])  # noqa
                    with l:
                        st.write(
                            f"Filename: {filename}\n\n"
                            f"Score: {score:.4f}"
                        )
                    with r:
                        st.button("🔍", type="primary", key=f'SimBtn{i}', on_click=update, args=(filename,))

        else:
            st.write("No videos found for the query:", query)


@st.cache_resource()
def load_embedder() -> LanguageBindEmbedder:
    return LanguageBindEmbedder(
        models=CLIP_MODELS,
        device=DEVICE
    )


@st.cache_resource()
def load_retriever() -> MultipleRetrievers:
    return MultipleRetrievers(
        retrievers=[
            get_retriever(
                dataset_path=DATASETS_PATH / d['dataset'],
                version=d['version'],
                modality=d['modality'],
                device=DEVICE,
            )
            for d in DATASETS
        ]
    )


def get_retriever(dataset_path: Path, version: str, modality: str, device: str) -> VideoRetriever:
    index_path = dataset_path / 'index' / version
    index_embeddings = np.load(index_path / f'{modality}_embeddings.npy')
    labels = [
        str(dataset_path / s)
        for s in (index_path / 'labels.txt').open().read().splitlines()
    ]
    return VideoRetriever(embeddings=index_embeddings, labels=labels, device=device)


if __name__ == "__main__":
    main()

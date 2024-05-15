from pathlib import Path

import numpy as np
import streamlit as st

from src.config import DATASETS_PATH, DATASETS, CANDIDATES_PER_PAGE, DEVICE, CLIP_MODELS
from src.embedder import LanguageBindEmbedder, Modality
from src.retriever import VideoRetriever, MultipleRetrievers


def main() -> None:
    st.set_page_config(layout="wide")

    embedder = load_embedder()
    retriever = load_retriever()

    render(embedder=embedder, retriever=retriever)


def render(embedder: LanguageBindEmbedder, retriever: MultipleRetrievers) -> None:
    st.title("Video Search")
    # st.write(DATASETS)

    datasets_mask = []
    for d in DATASETS:
        agree = st.checkbox(f"{d['dataset']} {d['version']}")
        datasets_mask.append(agree)

    query = st.text_input("Text query:")

    if query:
        # Search for videos based on query
        query_embedding = embedder.embed(query, modality=Modality.TEXT)
        candidates = retriever.retrieve(
            query_embedding.detach().numpy(),
            ignore_retrievers=datasets_mask,
            k=CANDIDATES_PER_PAGE
        )

        if candidates:
            n_cols = 4
            n_rows = len(candidates) // int(n_cols)
            rows = [st.container() for _ in range(n_rows)]
            cols_per_row = [r.columns(n_cols) for r in rows]
            cols = [column for row in cols_per_row for column in row]

            for i, candidate in enumerate(candidates):
                filename, score = candidate
                with cols[i]:
                    if 'mp4' in filename:
                        st.video(filename)
                    elif 'jpg' in filename:
                        st.image(filename)
                    else:
                        raise Exception('Unknown format')
                    st.write(
                        f"Filename: {filename}\n\n"
                        f"Score: {score:.4f}"
                    )
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

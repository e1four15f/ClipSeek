import numpy as np
import streamlit as st

from src.config import DATASET_PATH, DATASET, DATASET_TYPE, CANDIDATES_PER_PAGE
from src.embedder import LanguageBindEmbedder, Modality
from src.retriever import VideoRetriever


def main() -> None:
    st.set_page_config(layout="wide")

    embedder = load_embedder()
    retriever = load_retriever()

    render(embedder=embedder, retriever=retriever)


def render(embedder: LanguageBindEmbedder, retriever: VideoRetriever) -> None:
    st.title("Video Search")
    query = st.text_input("Text query:")

    if query:
        # Search for videos based on query
        text_embedding = embedder.embed(query, modality=Modality.TEXT)
        candidates = retriever.retrieve(text_embedding.detach().numpy(), k=CANDIDATES_PER_PAGE)

        if candidates:
            n_cols = 4
            n_rows = len(candidates) // int(n_cols)
            rows = [st.container() for _ in range(n_rows)]
            cols_per_row = [r.columns(n_cols) for r in rows]
            cols = [column for row in cols_per_row for column in row]

            for i, candidate in enumerate(candidates):
                filename, score = candidate
                with cols[i]:
                    st.video(filename)
                    st.write(
                        f"Filename: {filename}\n\n"
                        f"Score: {score:.4f}"
                    )
        else:
            st.write("No videos found for the query:", query)


@st.cache_resource()
def load_embedder() -> LanguageBindEmbedder:
    return LanguageBindEmbedder(
        models={Modality.VIDEO: 'LanguageBind_Video'},
        device='cpu'
    )


@st.cache_resource()
def load_retriever() -> VideoRetriever:
    dataset_path = DATASET_PATH / DATASET
    index_path = dataset_path / 'index/videos' / DATASET_TYPE

    index_embeddings = np.load(index_path / 'video_embeddings.npy')
    labels = [
        str(dataset_path / s)
        for s in (index_path / 'labels.txt').open().read().splitlines()
    ]

    return VideoRetriever(embeddings=index_embeddings, labels=labels, device='cpu')


if __name__ == "__main__":
    main()

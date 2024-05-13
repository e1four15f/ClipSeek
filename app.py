import numpy as np
import pandas as pd
import streamlit as st
from src.embedder import LanguageBindEmbedder
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
        text_embedding = embedder.embed_text(text=query)
        candidates = retriever.retrieve(text_embedding.detach().numpy())

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
                        f"Filename: {filename}\n"
                        f"Score: {score:.4f}"
                    )
        else:
            st.write("No videos found for the query:", query)


@st.cache_resource()
def load_embedder() -> LanguageBindEmbedder:
    return LanguageBindEmbedder(
        models={'video': 'LanguageBind_Video'},
        device='cpu'
    )


@st.cache_resource()
def load_retriever() -> VideoRetriever:
    msrvtt_train_embeddings = np.load('data/MSRVTT/embeddings/all/MSR-VTT_train_video_embeddings.npy')
    labels = (
        pd.read_csv('data/MSRVTT/MSRVTT_train.9k.csv')['video_id']
        .apply(lambda x: str(f'data/MSRVTT/videos/all/{x}.mp4'))
        .values
        .tolist()
    )
    return VideoRetriever(
        embeddings=msrvtt_train_embeddings,
        labels=labels,
        device='cpu'
    )


if __name__ == "__main__":
    main()

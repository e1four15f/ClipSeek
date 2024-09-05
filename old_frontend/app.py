from urllib.parse import urljoin

import requests
import streamlit as st

import config as cfg
from src.entity.embedder import Modality
from old_frontend.scroller import component_scroller


def main() -> None:
    st.set_page_config(page_title="HERE", page_icon="🔥", layout="wide", initial_sidebar_state="auto")
    if "query" not in st.session_state:
        st.session_state.query = "Cat in black suit is having meeting"

    if "modality" not in st.session_state:
        st.session_state.modality = Modality.TEXT
    render()


def render() -> None:
    with st.sidebar:
        st.title("Video Search")
        if cfg.DEBUG:
            st.title("Debug Info")
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
                if is_selected:
                    selected_datasets.append({"dataset": d["dataset"], "version": d["version"]})

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

            st.html("<hr>")

            st.write(f'#### Search results using "{st.session_state.modality}" modality')
            l, r = st.columns([1, 6])
            with l:
                st.write("Query:")
            with r:
                show_query(query)

    if query:
        candidates, session_id = retrieve_candidates(
            query=query,
            modalities=selected_modalities,
            collections=selected_datasets,
        )

        if candidates:
            props = {
                "media": candidates,
                "n_cols": cfg.N_RESULT_COLUMNS,
                "resources_url": urljoin(cfg.BACKEND_URL, "/resources"),
                "session_id": session_id,
            }
            print("Creating scroller component")
            component_scroller(key="scroller", **props)
        else:
            st.write("No videos found for the query:", query)


def retrieve_candidates(
    query: str,
    modalities: list[str],
    collections: list[dict],
) -> tuple[list[tuple[str, float, str]], str]:
    request = {
        "query": query,
        "modalities": modalities,
        "collections": collections,
    }
    print(request)
    response = requests.post(
        urljoin(cfg.BACKEND_URL, "api/v1/search/by_text"),
        json=request,
        timeout=10,
    )
    response.raise_for_status()

    response = response.json()
    return response['data'], response['session_id']


if __name__ == "__main__":
    main()

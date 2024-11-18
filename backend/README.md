# Backend

ClipSeek's backend is the core service that integrates the entire system. It utilizes **FastAPI** for the web server, **Milvus** for efficient search, **PyTorch** for model inference, and **FFmpeg** for video processing.

### API Resources
ClipSeek's API follows REST principles and offers three main resources:

1. **Search**
- POST /search/by_text: Search by text.
- POST /search/by_file: Search by file upload.
- POST /search/by_reference: Search by indexed reference.
- POST /search/continue: Continue an ongoing search session.
2. **Indexes**
- GET /indexes/info: Retrieve information about available indexes.
3. **File-Proxy**
- GET /resources/raw: Retrieve the original media file.
- GET /resources/clip: Retrieve a video clip.
- GET /resources/thumbnail: Retrieve a thumbnail from a video.

### Scripts
The following scripts help you work with the system. You can run them with `poetry run` command. 

- **compute_embeddings**: Generates embeddings for different media modalities.
- **create_index**: Creates Milvus collections and indexes embeddings.
- **generate_thumbnails**: An optional script that generates thumbnails in advance to improve system performance.


## Developing

To start developing, you have the option to use a docker container or develop locally. Following is the setup for the local environment.

Install poetry dependencies
```bash
poetry install
```

Run the server
```bash
make run
```

Run lint checkers
```bash
make lint
```

Prettify the code
```bash
make pretty
```
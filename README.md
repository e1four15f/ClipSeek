# ClipSeek: A Text-to-Clip Retrieval System

| ![ClipSeek](frontend/static/favicon.png)  | ClipSeek is a text-to-clip retrieval system that allows users to search for specific moments in videos using text queries. The system segments videos into clips and matches them with textual input using a multimodal deep learning model. It features a web-based interface and visualization of search results. |
|----------|------|

Specific docs:
- [Frontend](frontend/README.md)
- [Backend](backend/README.md)
- [Indexes](indexes/INDEXES.md)
- [Datasets](data/DATASETS.md)

## Configuration

By default, all services have exposed ports. You can change them in `.env` file. 

| Service  | Port | Url                        |
|----------|------|----------------------------|
| Frontend | 9500 | http://localhost:9500      |
| Backend  | 9501 | http://localhost:9501/docs |
| Attu     | 9502 | http://localhost:9502      |
| Milvus   | 9503 | http://localhost:9503      |

## Example

### Embeddings
We use backend environment to run scripts. Start the docker container with the following command, which also ups the Milvus and dependend services.
```bash
make pull
make scripts
```

The scripts is runned by `poetry run` commands.

```bash
poetry run compute_embeddings --help
```

During the first run the scripts will download models
The models as downloaded to `HF_HOME` directory, which is mounted to `/hf` inside of the container.

For testing purpuses you 
```bash
poetry run compute_embeddings --path /data/ExampleDataset/videos --name VideoDataset --version v1 --mode video+audio --model LanguageBind
```
Similarly for images
```bash
poetry run compute_embeddings --path /data/ExampleDataset/images --name ImageDataset --version v1 --mode image --model LanguageBind
```

### Indexing

The scripts is runned by `poetry run` commands.

```bash
poetry run create_index --help
```

```bash
poetry run create_index --name VideoDataset --version v1 --model LanguageBind
```

```bash
poetry run create_index --name ImageDataset --version v1 --model LanguageBind
```

You can check created collections in Attu web interface: http://localhost:8080/#/databases/ClipSeek

### Configuration

After creating collection it needed to be added to configuration file `config.yaml`. You can directly copy and paste the dataset definition from `meta.yaml`.

For our example, it will look like that
```yaml
# Datasets Configuration
DATASETS:
-   data_path: /data/ExampleDataset/images
    dataset: ImageDataset
    version: v1
    modalities:
    - image
-   data_path: /data/ExampleDataset/videos
    dataset: VideoDataset
    version: v1
    modalities:
    - video
    - audio
```

### Running
Now we ready to start the whole application.

```bash
make up logs
```

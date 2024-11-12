# ClipSeek

# Getting Started

| Service  | Port  | Url                          |
|----------|-------|------------------------------|
| Frontend | 4173  | http://localhost:4173        |
| Backend  | 8500  | http://localhost:8500/docs   |
| Attu     | 8080  | http://localhost:9080        |


## Embeddings and Indexing
We use backend environment to run scripts. Start the docker container with the following command, which also ups the Milvus and dependend services
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
poetry run compute_embeddings --path /data/ExampleDataset/videos --name VideoDataset --version v1 --mode video+audio --model Random
```
Similarly for images
```bash
poetry run compute_embeddings --path /data/ExampleDataset/images --name ImageDataset --version v1 --mode image --model Random
```

## Indexing

The scripts is runned by `poetry run` commands.

```bash
poetry run create_index --help
```

```bash
poetry run create_index --name VideoDataset --version v1 --model Random
```

```bash
poetry run create_index --name ImageDataset --version v1 --model Random
```

You can check created collections in Attu web interface: http://localhost:8080/#/databases/ClipSeek

## Configuration

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

## Running
Now we ready to start the whole application.

```bash
make up logs
```

Additionally, you can follow logs for specific service with adding postfix, for example
```bash
make logs-backend
```


## MSR-VTT dataset example 

Download MSR-VTT dataset
```bash
wget -P data https://www.robots.ox.ac.uk/~maxbain/frozen-in-time/data/MSRVTT.zip
unzip data/MSRVTT.zip -d data
rm data/MSRVTT.zip
```

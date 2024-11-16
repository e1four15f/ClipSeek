# ClipSeek

# Getting Started

By default, all services have exposed ports. You can change them in `.env` file. 

| Service  | Port | Url                        |
|----------|------|----------------------------|
| Frontend | 9500 | http://localhost:9500      |
| Backend  | 9501 | http://localhost:9501/docs |
| Attu     | 9502 | http://localhost:9502      |
| Milvus   | 9503 | http://localhost:9503      |

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


# More Examples

V100 with 16gb 

## MSR-VTT dataset
Videos: 10004
Clips: 25290
took: 7:32:45

Dataset
```bash
wget -P data https://www.robots.ox.ac.uk/~maxbain/frozen-in-time/data/MSRVTT.zip
unzip data/MSRVTT.zip -d data
rm data/MSRVTT.zip
```
Embeddings
```bash
poetry run compute_embeddings --path /data/MSRVTT/videos --name MSRVTT --version all --mode video+audio --model LanguageBind --batch-size 64
```

Indexing
```bash
poetry run create_index --name MSRVTT --version all --model LanguageBind
```

## MSVD dataset
1970 Videos
4450 Clips
took: 1:27:08

Dataset
```bash
wget -P data https://www.cs.utexas.edu/~ml/clamp/videoDescription/YouTubeClips.tar
mkdir -p data/MSVD
tar -xvf data/YouTubeClips.tar -C data/MSVD
rm data/YouTubeClips.tar
```

Embeddings
```bash
poetry run compute_embeddings --path /data/MSVD --name MSVD --version v1 --mode video+audio --model LanguageBind --batch-size 64
```

Indexing
```bash
poetry run create_index --name MSVD --version v1 --model LanguageBind
```

## COCO train 2017
118287 images
took: 1:13:16

Dataset
```bash
wget -P data http://images.cocodataset.org/zips/train2017.zip
unzip data/train2017.zip -d data/COCO
rm data/train2017.zip
```

Embeddings
```bash
poetry run compute_embeddings --path /data/COCO/train2017 --name COCO --version train --mode image --model LanguageBind --batch-size 512
```

Indexing
```bash
poetry run create_index --name COCO --version train --model LanguageBind
```


http://images.cocodataset.org/zips/val2017.zip

unzip data/val2017.zip -d data/COCO
rm data/val2017.zip
# Scripts

We use poetry to run scripts
```bash
poetry run <script> 
```

### 1. compute_embeddings
```bash
Compute embeddings for a multimedia dataset.

optional arguments:
  -h, --help            show this help message and exit
  --dataset-path DATASET_PATH, --path DATASET_PATH, -p DATASET_PATH
                        Path to the dataset containing media files.
  --dataset-name DATASET_NAME, --name DATASET_NAME, -n DATASET_NAME
                        Name of the dataset (e.g., 'MyDataset').
  --dataset-version DATASET_VERSION, --version DATASET_VERSION, -v DATASET_VERSION
                        Version of the dataset (e.g., 'v1.0', '5s').
  --mode {video,video+audio,image}
                        Inferece mode
  --model {LanguageBind,Random}, -m {LanguageBind,Random}
                        Embedder model
  --clip-length CLIP_LENGTH, -cl CLIP_LENGTH
                        Set the maximum clip length for splitting videos (in seconds).
  --device DEVICE, -d DEVICE
                        Device to use for model inference: 'cuda' or 'cpu'.
  --batch-size BATCH_SIZE, -bs BATCH_SIZE
                        Batch size for model inference.
```

### 2. create_index
```bash
Build an index from precomputed embeddings for a specific dataset version.

optional arguments:
  -h, --help            show this help message and exit
  --dataset-name DATASET_NAME, --name DATASET_NAME, -n DATASET_NAME
                        Name of the dataset (e.g., 'VideoDataset').
  --dataset-version DATASET_VERSION, --version DATASET_VERSION, -v DATASET_VERSION
                        Version of the dataset (e.g., 'v1.0', '5s').
  --model {LanguageBind,Random}, -m {LanguageBind,Random}
                        Embedder model
  --index-type INDEX_TYPE, --index INDEX_TYPE, -i INDEX_TYPE
                        Index type (e.g., 'FLAT', 'IVF_FLAT', ...).
```


### 3. generate_thumbnails (Optional)
```bash
Generates thumbnails from video files based on provided dataset details.

optional arguments:
  -h, --help            show this help message and exit
  --data-path DATA_PATH, --path DATA_PATH, -p DATA_PATH
                        Name of the dataset (e.g., 'VideoDataset').
  --dataset-name DATASET_NAME, --name DATASET_NAME, -n DATASET_NAME
                        Name of the dataset (e.g., 'VideoDataset').
  --dataset-version DATASET_VERSION, --version DATASET_VERSION, -v DATASET_VERSION
                        Version of the dataset (e.g., 'v1.0', '5s').
```
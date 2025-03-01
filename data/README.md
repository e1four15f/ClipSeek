# Datasets

This directory contains raw datasets used exclusively for reading. If you're using docker, ensure that you mount your datasets to this directory. The dataset structure can be in any format, as the scripts recursively walk through the selected path to find files with the requested extensions.

The `ExampleDataset` includes videos and images in various formats and serves as an example.

## More Datasets

Below are commands for indexing datasets, which have been processed with ClipSeek using an Nvidia V100 GPU with 16GB of memory within a docker container (`make scripts`). Precomputed values are available for download from [Google Drive](https://drive.google.com/file/d/1qItXWAhPYmjaqGsloE1U8OQQk3iPNwxx/view?usp=sharing). Simply extract the downloaded files into the `indexes` directory.

For more information on the datasets used, visit: [Collaborative Experts Datasets](https://github.com/albanie/collaborative-experts/tree/master/misc/datasets)

### MSR-VTT dataset
- Videos: 10004
- Clips: 25290
- Processing Time: 7:32:45

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

Thumbnails (Optional)
```bash
poetry run generate_thumbnails --path /data/MSRVTT/videos --name MSRVTT --version all
```

### MSVD dataset
- Videos: 1970 
- Clips: 4450 
- Embeddings Processing Time: 1:27:08

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

Thumbnails (Optional)
```bash
poetry run generate_thumbnails --path /data/MSVD --name MSVD --version v1
```

### COCO valid 2017
- Images: 5000
- Processing Time: 3:06

Dataset
```bash
wget -P data http://images.cocodataset.org/zips/val2017.zip
unzip data/val2017.zip -d data/COCO
rm data/val2017.zip
```

Embeddings
```bash
poetry run compute_embeddings --path /data/COCO/val2017 --name COCO --version valid --mode image --model LanguageBind --batch-size 512
```

Indexing
```bash
poetry run create_index --name COCO --version valid --model LanguageBind
```

Thumbnails (Optional)
```bash
poetry run generate_thumbnails --path /data/COCO/val2017 --name COCO --version valid
```

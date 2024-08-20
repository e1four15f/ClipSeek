# Datasets 

Read about used datasets here: https://github.com/albanie/collaborative-experts/tree/master/misc/datasets


## File Structure

The datasets stored in separate directories, where the `index` directory is generated via indexing script.

```raw_data
- videos
    all
        1.mp4
        2.mp4
```

```
data/<dataset>/<version>
    - labels.jsonlines raw data - order assosiation | path, span, 
	- <model>_<modality>_embeddings.npy
	- meta.json always add after indexing, eg rewrite and add one more column
```

```
data
├── DATASETS.md
├── COCO
│   ├── test2017
│   │   ├── image_embeddings.npy
│   │   └── labels.txt
│   └── val2017
│       ├── image_embeddings.npy
│       └── labels.txt
├── MSRVTT
│   ├── 5sec
│   │   ├── labels.txt
│   │   └── video_embeddings.npy
│   ├── all
│   │   ├── MSR-VTT_test_audio_embeddings.npy
│   │   ├── MSR-VTT_test_video_embeddings.npy
│   │   ├── audio_embeddings.npy
│   │   ├── labels.txt
│   │   └── video_embeddings.npy
│   ├── audios5s
│   │   ├── labels.txt
│   │   └── parts
│   │       └── audio_embeddings.0.npy
│   └── test
│       ├── labels.txt
│       └── video_embeddings.npy
└── MSVD
    └── 5sec
        ├── labels.txt
        └── video_embeddings.npy
```

The example of generated `labels.jsonlines` file:
```txt
{ "path": "1.mp4", "span": [0, 5] }
{ "path": "1.mp4", "span": [5, 8] }
{ "path": "2.mp4", "span": [0, 3] }
```

The example of generated `meta.json` file:
```txt
aka save config?
{ 
    "datetime": "",
    "data_path": "../data/MSVD/5sec",
    "dataset": "MSVD",
    "version": "5sec",
    "modalities": ["video"],
    "embedder": "LanguageBind", 
}
datetime, embedder, folders etc
```
# Datasets 

Read about used datasets here: https://github.com/albanie/collaborative-experts/tree/master/misc/datasets


## File Structure

The datasets stored in separate directories, where the `index` directory is generated via indexing script.

```
data/<dataset>
├── index
│   └── videos
│       ├── all
│       │   ├── embeddings.npy
│       │   └── labels.txt
│       └── test
│           ├── embeddings.npy
│           └── labels.txt
└── videos
    ├── all
    │   ├── 0.mp4
    │   └── 1.mp4
    └── test
        ├── 0.mp4
        └── 1.mp4
```

The example of generated `index/all/labels.txt` file:
```txt
videos/all/1.mp4
videos/all/2.mp4
```
# Indexes 

Indexing scripts will generate files for each index in this directory, including embeddings, labels, and meta information.

The indexes follow this template
```
indexes/<dataset>/<version>
    - labels.jsonlines
    - errors.jsonlines
	- <model>_<modality>_embeddings.npy
	- meta.yaml
```

## Directory structure
Example of directory structure
```
indexes
├── README.md
├── COCO
│   └── valid
│       ├── thumbnails
│       ├── LanguageBind_image_embeddings.npy
│       ├── errors.jsonlines
│       ├── labels.jsonlines
│       └── meta.yaml
├── MSRVTT
│   └── all
│       ├── thumbnails
│       ├── LanguageBind_audio_embeddings.npy
│       ├── LanguageBind_video_embeddings.npy
│       ├── errors.jsonlines
│       ├── labels.jsonlines
│       └── meta.yaml
└── MSVD
    └── v1
        ├── thumbnails
        ├── LanguageBind_audio_embeddings.npy
        ├── LanguageBind_video_embeddings.npy
        ├── errors.jsonlines
        ├── labels.jsonlines
        └── meta.yaml
```

## Labels and Errors
The example of generated `labels.jsonlines` file:
```jsonlines 
{"path": "all/video156.mp4", "span": [0.0, 13.21]}
{"path": "all/video156.mp4", "span": [13.21, 19.06]}
{"path": "all/video7103.mp4", "span": [0.0, 8.34]}
{"path": "all/video7103.mp4", "span": [8.34, 8.77]}
{"path": "all/video7103.mp4", "span": [8.77, 16.06]}
{"path": "all/video1361.mp4", "span": [0.0, 12.3]}
{"path": "all/video1361.mp4", "span": [12.3, 13.08]}
```

The example of generated `errors.jsonlines` file:
```jsonlines 
{"path": "all/._video3.mp4", "error": "Command '['ffmpeg', '-y', '-fflags', '+genpts', '-i', '/data/MSRVTT/videos/all/._video3.mp4', '-map', '0', '-segment_time', '5', '-f', 'segment', '-reset_timestamps', '1', '-c:v', 'copy', '-c:a', 'copy', '-loglevel', 'error', '-nostats', '../indexes/MSRVTT/all/.tmp/clips/._video3.clip%03d.mp4']' returned non-zero exit status 1."}
{"path": "all/._video9560.mp4", "error": "Command '['ffmpeg', '-y', '-fflags', '+genpts', '-i', '/data/MSRVTT/videos/all/._video9560.mp4', '-map', '0', '-segment_time', '5', '-f', 'segment', '-reset_timestamps', '1', '-c:v', 'copy', '-c:a', 'copy', '-loglevel', 'error', '-nostats', '../indexes/MSRVTT/all/.tmp/clips/._video9560.clip%03d.mp4']' returned non-zero exit status 1."}
```


## Meta
The example of generated `meta.yaml` file:
```yaml
Dataset:
-   data_path: /data/MSRVTT/videos
    dataset: MSRVTT
    version: all
    modalities:
    - video
    - audio
    - hybrid
Dataset Meta:
    Video Count: 10004
    Clips Count: 25290
    Errors Count: 4
    Embeddings Shape: '{''video'': (25290, 768), ''audio'': (25290, 768)}'
Script Run Configuration:
    Date: '2024-11-16 04:48:29'
    Indexes Root: ../indexes
    Dataset Path: /data/MSRVTT/videos
    Dataset Name: MSRVTT
    Dataset Version: all
    Mode: Mode.VIDEO_WITH_AUDIO
    Model: EmbedderType.LANGUAGE_BIND
    Clip Length: 5.0
    Device: cuda
    Batch Size: 64

```
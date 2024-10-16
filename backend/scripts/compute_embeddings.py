import argparse
from datetime import datetime
import json
import subprocess
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from typing import Union, Optional

import numpy as np
import yaml
from more_itertools import chunked
from tqdm import tqdm

from src.entity.embedder import LanguageBindEmbedder, Modality, RandomEmbedder


class Mode(str, Enum):
    VIDEO = 'video'
    VIDEO_WITH_AUDIO = 'video+audio'
    IMAGE = 'image'

    def get_extentions(self) -> list[str]:
        return {
            Mode.VIDEO: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
            Mode.VIDEO_WITH_AUDIO: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
            Mode.IMAGE: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
        }[self]

    def get_modalities(self) -> list[Modality]:
        return {
            Mode.VIDEO: [Modality.VIDEO],
            Mode.VIDEO_WITH_AUDIO: [Modality.VIDEO, Modality.AUDIO],
            Mode.IMAGE: [Modality.IMAGE],
        }[self]


class Model(str, Enum):
    LANGUAGE_BIND = 'LanguageBind'
    RANDOM = 'random'


def main(
    indexes_root: Path,
    dataset_path: Path,
    dataset_name: str,
    dataset_version: str,
    mode: Mode,
    model: Model,
    clip_length: float,
    device: str,
    batch_size: int,
) -> None:
    print(
        "####################\n"
        f"Indexes Root: {indexes_root}\n"
        f"Dataset Path: {dataset_path}\n"
        f"Dataset Name: {dataset_name}\n"
        f"Dataset Version: {dataset_version}\n"
        f"Mode: {mode}\n"
        f"Model: {model}\n"
        f"Clip Length: {clip_length}\n"
        f"Device: {device}\n"
        f"Batch Size: {batch_size}\n"
        "####################"
    )
    media_paths = find_media_files(directory=dataset_path, extensions=mode.get_extentions())
    print(f'Found "{len(media_paths)}" {mode} files')
    if not len(media_paths):
        raise ValueError(
            f'No {mode.get_modalities()} files found in directory: {dataset_path}. '
            'Please check the dataset path and modality.'
        )

    index_path = indexes_root / dataset_name / dataset_version
    tmp_path = index_path / ".tmp"
    (tmp_path / "embeddings").mkdir(parents=True, exist_ok=True)
    (tmp_path / "clips").mkdir(parents=True, exist_ok=True)
    (tmp_path / "audios").mkdir(parents=True, exist_ok=True)
    labels_path = index_path / "labels.jsonlines"
    labels_path.open("w").close()
    errors_path = index_path / "errors.jsonlines"
    errors_path.open("w").close()

    print("Loading model...")
    if model == Model.LANGUAGE_BIND:
        embedder = LanguageBindEmbedder(device=device)
    elif model == Model.RANDOM:
        embedder = RandomEmbedder(embeddings_dim=768)
    else:
        raise NotImplementedError

    print(f'Computing embeddings to "{index_path}"...')
    embeddings = {modality: [] for modality in mode.get_modalities()}
    if mode == Mode.IMAGE:
        for i, batch in enumerate(tqdm(list(chunked(media_paths, n=batch_size)))):
            try:
                image_embeddings = (
                    embedder.embed([str(path) for path in batch], modality=Modality.IMAGE)
                    .detach()
                    .cpu()
                    .numpy()
                )
            except Exception as e:
                print(f"Batch skipped! Exception while processing image batch {i}")
                for path in batch:
                    write_error(errors_path, media_path=path.relative_to(dataset_path), message=str(e))
                continue
            np.save(tmp_path / "embeddings" / f"{model}_{Modality.IMAGE}_embeddings.{i}", image_embeddings)
            embeddings[Modality.IMAGE].append(image_embeddings)
            for path in batch:
                write_labels(
                    labels_path, media_path=path.relative_to(dataset_path)
                )
    elif mode == mode.VIDEO:
        for i, clips_info in enumerate(clip_generator(media_paths, output_path=(tmp_path/"clips"), batch_size=batch_size)):
            if isinstance(clips_info, dict):
                clip_info = clips_info
                write_error(
                    errors_path, media_path=clip_info["media_path"].relative_to(dataset_path),
                    message=clip_info["error"]
                )
                continue

            try:
                video_embeddings = (
                    embedder.embed([str(clip["clip_path"]) for clip in clips_info], modality=Modality.VIDEO)
                    .detach()
                    .cpu()
                    .numpy()
                )
            except Exception as e:
                print(f"Batch skipped! Exception while processing video batch {i}")
                for clip_info in clips_info:
                    write_error(errors_path, media_path=clip_info["media_path"].relative_to(dataset_path),
                                message=str(e))
                continue
            np.save(tmp_path / "embeddings" / f"{model}_{Modality.VIDEO}_embeddings.{i}", video_embeddings)
            embeddings[Modality.VIDEO].append(video_embeddings)
            for clip_info in clips_info:
                write_labels(
                    labels_path, media_path=clip_info["media_path"].relative_to(dataset_path), span=clip_info["span"]
                )
                if clip_info["clip_path"].exists():
                    clip_info["clip_path"].unlink()
    elif mode == mode.VIDEO_WITH_AUDIO:
        for i, clips_info in enumerate(clip_generator(media_paths, output_path=(tmp_path / "clips"), batch_size=batch_size)):
            if isinstance(clips_info, dict):
                clip_info = clips_info
                write_error(
                    errors_path, media_path=clip_info["media_path"].relative_to(dataset_path),
                    message=clip_info["error"]
                )
                continue

            # Video
            try:
                video_embeddings = (
                    embedder.embed([str(clip["clip_path"]) for clip in clips_info], modality=Modality.VIDEO)
                    .detach()
                    .cpu()
                    .numpy()
                )
            except Exception as e:
                print(f"Batch skipped! Exception while processing video batch {i}")
                for clip_info in clips_info:
                    write_error(errors_path, media_path=clip_info["media_path"].relative_to(dataset_path),
                                message=str(e))
                continue

            # Audio
            try:
                audio_paths = []
                valid_indexes_mask = []
                for j, clip in enumerate(clips_info):
                    try:
                        audio_path = extract_audio(clip["clip_path"], output_path=(tmp_path / 'audios'))
                        audio_paths.append(str(audio_path))
                        valid_indexes_mask.append(j)
                    except Exception as e:
                        print(f'Video {clip["clip_path"]} does not have audio stream')
                audio_embeddings = np.zeros((len(clips_info), video_embeddings.shape[1]))
                if audio_paths:
                    audio_embeddings[valid_indexes_mask] = (
                        embedder.embed(audio_paths, modality=Modality.AUDIO)
                        .detach()
                        .cpu()
                        .numpy()
                    )
            except Exception as e:
                print(f"Batch skipped! Exception while processing audio batch {i}")
                for clip_info in clips_info:
                    write_error(errors_path, media_path=clip_info["media_path"].relative_to(dataset_path),
                                message=str(e))
                continue

            np.save(tmp_path / "embeddings" / f"{model}_{Modality.VIDEO}_embeddings.{i}", video_embeddings)
            embeddings[Modality.VIDEO].append(video_embeddings)

            np.save(tmp_path / "embeddings" / f"{model}_{Modality.AUDIO}_embeddings.{i}", audio_embeddings)
            embeddings[Modality.AUDIO].append(audio_embeddings)

            for clip_info in clips_info:
                write_labels(
                    labels_path, media_path=clip_info["media_path"].relative_to(dataset_path), span=clip_info["span"]
                )
                if clip_info["clip_path"].exists():
                    clip_info["clip_path"].unlink()
            for path in audio_paths:
                if Path(path).exists():
                    Path(path).unlink()
    else:
        raise NotImplementedError

    emb_shapes = {}
    for modality in mode.get_modalities():
        modality_embeddings = np.vstack(embeddings[modality])
        emb_shapes[str(modality.value)] = modality_embeddings.shape
        np.save(index_path / f"{model}_{modality}_embeddings.npy", modality_embeddings)

    print("Saving metadata")
    with (index_path / "meta.yaml").open("w") as file:
        dataset_meta = {}
        if mode == Mode.IMAGE:
            dataset_meta["Images Count"] = len(media_paths)
        else:
            dataset_meta["Video Count"] = len(media_paths)
            dataset_meta["Clips Count"] = sum(1 for _ in labels_path.open())
        dataset_meta["Errors Count"] = sum(1 for _ in errors_path.open())
        dataset_meta["Embeddings Shape"] = f"{emb_shapes}"
        yaml.dump(
            {
                "Dataset": [
                    {
                        "data_path": str(dataset_path.resolve()),
                        "dataset": dataset_name,
                        "version": dataset_version,
                        "modalities": [str(m.value) for m in mode.get_modalities()],
                    }
                ],
                "Dataset Meta": dataset_meta,
                "Script Run Configuration": {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Indexes Root": str(indexes_root),
                    "Dataset Path": str(dataset_path),
                    "Dataset Name": dataset_name,
                    "Dataset Version": dataset_version,
                    "Mode": str(mode),
                    "Model": model,
                    "Clip Length": clip_length,
                    "Device": device,
                    "Batch Size": batch_size,
                },
            },
            file,
            sort_keys=False,
            indent=4,
        )
    print((index_path / "meta.yaml").read_text())
    print("Done!")


def clip_generator(paths: list[Path], output_path: Path, batch_size: int) -> Generator[Union[list[dict], dict], None, None]:
    buffer = []
    for path in tqdm(paths):
        try:
            clip_paths_and_timings = get_video_clips_with_timing(input_path=path, output_path=output_path)
            buffer += clip_paths_and_timings
        except Exception as e:
            print(f"Error processing {path}: {e}")
            yield {"media_path": path, "error": str(e)}
            continue  # Skip to the next media file

        while len(buffer) >= batch_size:
            yield buffer[:batch_size]
            buffer = buffer[batch_size:]

    if buffer:
        yield buffer


def write_error(errors_path: Path, media_path: Path, message: str) -> None:
    with errors_path.open("a") as f:
        json_line = json.dumps({"path": str(media_path), "error": message})
        f.write(json_line + "\n")


def write_labels(labels_path: Path, media_path: Path, span: Optional[tuple[float, float]] = None) -> None:
    with labels_path.open("a") as f:
        data = {"path": str(media_path)}
        if span:
            data['span'] = span
        json_line = json.dumps(data)
        f.write(json_line + "\n")


def find_media_files(directory: Path, extensions: list[str]) -> list[Path]:
    return [file_path for file_path in directory.rglob("*") if file_path.suffix.lower() in extensions]


def get_video_clips_with_timing(input_path: Path, output_path: Path, segment_duration: float = 5) -> list[dict]:
    video_segments = []
    start_time = 0.0

    for clip_path in split_video(input_path, output_path, segment_duration):
        duration = get_video_duration(clip_path)
        end_time = round(start_time + duration, 2)
        start_time = round(start_time, 2)
        video_segments.append({"media_path": input_path, "clip_path": clip_path, "span": [start_time, end_time]})
        start_time = end_time

    return video_segments


def split_video(input_path: Path, output_path: Path, segment_duration: float) -> list[Path]:
    command = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-i", str(input_path),
        "-map", "0",
        "-segment_time", str(segment_duration),
        "-f", "segment",
        "-reset_timestamps", "1",
        "-c:v", "copy",
        "-c:a", "copy",
        "-loglevel", "error",
        "-nostats",
    ]  # fmt: skip

    output_pattern = output_path / f"{input_path.stem}.clip%03d{input_path.suffix}"
    command += [str(output_pattern)]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise ValueError(f"FFmpeg error: {result.stderr}")

    return list(output_path.glob(f"{input_path.stem}.clip*{input_path.suffix}"))


def extract_audio(input_path: Path, output_path: Path) -> Path:
    command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-loglevel", "error",
        "-nostats",
    ]

    output_file = output_path / f"{input_path.stem}.audio.wav"
    command += [str(output_file)]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise ValueError(f"FFmpeg error: {result.stderr}")

    return output_file


def get_video_duration(file_path: Path) -> float:
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration",
        "-of", "json",
        str(file_path)
    ]  # fmt: skip

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise ValueError(f"FFprobe error: {result.stderr}")

    duration_info = json.loads(result.stdout)
    return float(duration_info["format"]["duration"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute embeddings for a multimedia dataset.")
    parser.add_argument(
        "--indexes-root",
        type=Path,
        default="../indexes",
        help="Path to the root directory where computed indexes will be stored."
    )
    parser.add_argument(
        "--dataset-path",
        "--path",
        "-p",
        type=Path,
        required=True,
        default="raw_data/<dataset>/videos/all",
        help="Path to the dataset containing media files."
    )
    parser.add_argument(
        "--dataset-name",
        "--name",
        "-n",
        type=str,
        required=True,
        help="Name of the dataset (e.g., 'MyDataset')."
    )
    parser.add_argument(
        "--dataset-version",
        "--version",
        "-v",
        type=str,
        required=True,
        help="Version of the dataset (e.g., 'v1.0', '5s')."
    )
    parser.add_argument(
        "--mode",
        "-m",
        type=Mode,
        required=True,
        choices=list(Mode),  # noqa
        help="Inferece mode"
    )
    parser.add_argument(
        "--model",
        type=Model,
        required=True,
        choices=list(Model),  # noqa
        default=Model.LANGUAGE_BIND,
        help="Embedder model"
    )
    parser.add_argument(
        "--clip-length", "-cl",
        type=float,
        default=5.0,
        help="Set the maximum clip length for splitting videos (in seconds)."
    )
    parser.add_argument(
        "--device",
        "-d",
        type=str,
        default="cuda",
        help="Device to use for model inference: 'cuda' or 'cpu'."
    )
    parser.add_argument(
        "--batch-size",
        "-bs",
        type=int,
        default=32,
        help="Batch size for model inference."
    )

    args = parser.parse_args()
    main(
        indexes_root=Path(args.indexes_root),
        dataset_path=Path(args.dataset_path),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
        mode=args.mode,
        model=args.model,
        clip_length=args.clip_length,
        device=args.device,
        batch_size=args.batch_size,
    )

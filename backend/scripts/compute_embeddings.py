import argparse
import json
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import Union

import numpy as np
import yaml
from tqdm import tqdm

from src.entity.embedder import LanguageBindEmbedder, Modality


def main(
    indexes_root: Path,
    dataset_path: Path,
    dataset_name: str,
    dataset_version: str,
    modality: Modality,
    device: str,
    batch_size: int,
) -> None:
    print(
        "####################\n"
        f"Indexes Root: {indexes_root}\n"
        f"Dataset Path: {dataset_path}\n"
        f"Dataset Name: {dataset_name}\n"
        f"Dataset Version: {dataset_version}\n"
        f"Modality: {modality}\n"
        f"Device: {device}\n"
        f"Batch Size: {batch_size}\n"
        "####################"
    )

    print("Loading model...")
    models = {"video": "LanguageBind_Video", "audio": "LanguageBind_Audio", "image": "LanguageBind_Image"}
    embedder = LanguageBindEmbedder(models=models, device=device)
    media_paths = find_media_files(directory=dataset_path, modality=modality)
    print(f'Found "{len(media_paths)}" {modality.value} files')

    index_path = indexes_root / dataset_name / dataset_version

    tmp_path = index_path / ".tmp"
    (tmp_path / "embeddings").mkdir(parents=True, exist_ok=True)
    (tmp_path / "clips").mkdir(parents=True, exist_ok=True)

    labels_path = index_path / "labels.jsonlines"
    labels_path.open("w").close()

    errors_path = index_path / "errors.jsonlines"
    errors_path.open("w").close()

    print(f'Computing embeddings to "{index_path}"...')

    def clip_generator(paths: list[Path]) -> Generator[Union[list[dict], dict], None, None]:
        buffer = []
        for path in tqdm(paths):
            try:
                clip_paths_and_timings = get_video_clips_with_timing(input_path=path, output_path=(tmp_path / "clips"))
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

    embeddings = []
    for i, clips_info in enumerate(clip_generator(media_paths)):
        if isinstance(clips_info, dict):
            clip_info = clips_info
            write_error(
                errors_path, media_path=clip_info["media_path"].relative_to(dataset_path), message=clip_info["error"]
            )
            continue

        try:
            batch_embeddings = (
                embedder.embed([str(clip["clip_path"]) for clip in clips_info], modality=modality)
                .detach()
                .cpu()
                .numpy()
            )
        except Exception as e:
            for clip_info in clips_info:
                write_error(errors_path, media_path=clip_info["media_path"].relative_to(dataset_path), message=str(e))
            continue
        # TODO LanguageBind_
        np.save(tmp_path / "embeddings" / f"LanguageBind_{modality}_embeddings.{i}", batch_embeddings)
        embeddings.append(batch_embeddings)
        for clip_info in clips_info:
            write_labels(
                labels_path, media_path=clip_info["media_path"].relative_to(dataset_path), span=clip_info["span"]
            )
            if clip_info["clip_path"].exists():
                clip_info["clip_path"].unlink()

    embeddings = np.vstack(embeddings)
    np.save(index_path / f"{modality}_embeddings.npy", embeddings)
    # TODO check presets

    print("Saving metadata")
    with (index_path / "meta.yaml").open("w") as file:
        yaml.dump(
            {
                "Dataset": [
                    {
                        "data_path": str(dataset_path.resolve()),
                        "dataset": dataset_name,
                        "version": dataset_version,
                        "modalities": [str(modality.value)],
                    }
                ],
                "Dataset Meta": {
                    "Video Count": len(media_paths),
                    "Clips Count": sum(1 for _ in labels_path.open()),
                    "Errors Count": sum(1 for _ in errors_path.open()),
                    "Embeddings Shape": f"{embeddings.shape}",
                },
                "Script Run Configuration": {
                    "Indexes Root": str(indexes_root),
                    "Dataset Path": str(dataset_path),
                    "Dataset Name": dataset_name,
                    "Dataset Version": dataset_version,
                    "Modality": str(modality.value),
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


def write_error(errors_path: Path, media_path: Path, message: str) -> None:
    with errors_path.open("a") as f:
        json_line = json.dumps({"path": str(media_path), "error": message})
        f.write(json_line + "\n")


def write_labels(labels_path: Path, media_path: Path, span: tuple[float, float]) -> None:
    with labels_path.open("a") as f:
        json_line = json.dumps({"path": str(media_path), "span": span})
        f.write(json_line + "\n")


def find_media_files(directory: Path, modality: Modality) -> list[Path]:
    extensions = {
        Modality.VIDEO: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
        Modality.AUDIO: [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
        Modality.IMAGE: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    }

    return [file_path for file_path in directory.rglob("*") if file_path.suffix.lower() in extensions[modality]]


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

    if input_path.suffix.lower() in [".mp4", ".avi", ".mov"]:
        command += ["-bsf:v", "h264_mp4toannexb"]

    output_pattern = output_path / f"{input_path.stem}.clip%03d{input_path.suffix}"
    command += [str(output_pattern)]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise ValueError(f"FFmpeg error: {result.stderr}")

    return list(output_path.glob(f"{input_path.stem}.clip*{input_path.suffix}"))


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the model with specified parameters.")
    # PYTHONPATH=. python scripts/compute_embeddings.py -p ../../data/TEST/sample -n TEST -v 5s -d cpu
    parser.add_argument("--indexes-root", type=Path, default="../indexes", help="Path to the indexes root directory")
    parser.add_argument(
        "--dataset-path",
        "--path",
        "-p",
        type=Path,
        required=True,
        default="raw_data/<dataset>/videos/all",
        help="",
    )
    parser.add_argument(
        "--dataset-name",
        "--name",
        "-n",
        type=str,
        required=True,
        help="",
    )
    parser.add_argument(
        "--dataset-version",
        "--version",
        "-v",
        type=str,
        required=True,
        help="",
    )
    parser.add_argument(
        "--modality",
        "-m",
        type=Modality,
        choices=[Modality.VIDEO, Modality.IMAGE, Modality.AUDIO],
        default=Modality.VIDEO,
        help="",
    )

    parser.add_argument("--device", "-d", type=str, default="cuda", help="Device to use (e.g., 'cuda' or 'cpu')")
    parser.add_argument("--batch-size", "-bs", type=int, default=32, help="Batch size for model inference")

    args = parser.parse_args()
    main(
        indexes_root=Path(args.indexes_root),
        dataset_path=Path(args.dataset_path),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
        modality=args.modality,
        device=args.device,
        batch_size=args.batch_size,
    )

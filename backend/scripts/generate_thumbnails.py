import argparse
import json
import subprocess
from pathlib import Path

from tqdm import tqdm


def main(
    indexes_root: Path,
    data_path: Path,
    dataset_name: str,
    dataset_version: str,
) -> None:
    labels_path = indexes_root / dataset_name / dataset_version / "labels.jsonlines"
    thumbnails_path = indexes_root / dataset_name / dataset_version / "thumbnails"
    thumbnails_path.mkdir(exist_ok=True)

    labels = labels_path.open().readlines()
    for row in tqdm(labels):
        label = json.loads(row)
        input_file = data_path / label["path"]

        if "span" in label:
            time = label["span"][0]
            if time:
                output_file = thumbnails_path / (label["path"] + ".jpg")
            else:
                output_file = thumbnails_path / (label["path"] + str(time) + ".jpg")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            command = [
                "ffmpeg", "-y",
                "-ss", str(label['span'][0]),
                "-i", str(input_file),
                "-vf", "thumbnail,scale=320:-1",
                "-frames:v", "1",
                str(output_file),
            ]  # fmt: skip
        else:
            output_file = thumbnails_path / (label["path"] + ".jpg")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            command = [
                "ffmpeg", "-y",
                "-i", str(input_file),
                "-vf", "scale=320:-1",
                str(output_file),
            ]  # fmt: skip
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            if result.returncode != 0:
                raise ValueError(f"FFmpeg error: {result.stderr}")
        except Exception:
            print(f"Error while generating thumbnail for {label['path']}")

    print("Done!")


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Build an index from precomputed embeddings for a specific dataset version."
    )

    parser.add_argument(
        "--data-path", "--path", "-p", type=str, required=True, help="Name of the dataset (e.g., 'VideoDataset')."
    )

    parser.add_argument(
        "--dataset-name", "--name", "-n", type=str, required=True, help="Name of the dataset (e.g., 'VideoDataset')."
    )
    parser.add_argument(
        "--dataset-version",
        "--version",
        "-v",
        type=str,
        required=True,
        help="Version of the dataset (e.g., 'v1.0', '5s').",
    )

    args = parser.parse_args()
    main(
        indexes_root=Path("../indexes"),
        data_path=Path(args.data_path),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
    )


if __name__ == "__main__":
    run()

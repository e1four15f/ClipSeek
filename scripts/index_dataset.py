import argparse
import json
from pathlib import Path

import numpy as np
from more_itertools import chunked
from tqdm.auto import tqdm

from src.embedder import LanguageBindEmbedder, Modality

EMBEDDINGS_DIM = 768
MODALITY_PATTERN = {
    # TODO (v.karmazin): avi, png and other formats
    Modality.VIDEO: "*.mp4",
    Modality.IMAGE: "*.jpg",
}


def main(  # noqa: PLR0913
    models: dict[Modality, str],
    dataset_path: Path,
    media_path: Path,
    modality: Modality,
    device: str,
    batch_size: int,
) -> None:
    print(
        "####################\n"
        f"Models: {models}\n"
        f"Dataset path: {dataset_path}\n"
        f"Media path: {media_path}\n"
        f"Modality: {modality}\n"
        f"Device: {device}\n"
        f"Batch size: {batch_size}\n"
        "####################"
    )

    print("Loading model...")
    embedder = LanguageBindEmbedder(models=models, device=device)
    data_paths = [str(s) for s in sorted(media_path.rglob(f"**/{MODALITY_PATTERN[modality]}"))]
    print(f'Found "{len(data_paths)}" files')

    index_path = dataset_path / "index" / media_path.relative_to(dataset_path)
    part_path = index_path / "parts"
    part_path.mkdir(parents=True, exist_ok=True)
    labels_path = index_path / "labels.txt"
    labels_path.write_text("\n".join([str(Path(s).relative_to(dataset_path)) for s in data_paths]))
    print(f'Wrote labels to "{labels_path}"')

    print(f'Computing embeddings to "{index_path}"...')
    embeddings = []
    for i, batch in enumerate(tqdm(list(chunked(data_paths, batch_size)))):
        batch_embeddings = embedder.embed(batch, modality=modality).detach().cpu().numpy()  # noqa
        np.save(part_path / f"{modality}_embeddings.{i}", batch_embeddings)
        embeddings.append(batch_embeddings)
    embeddings = np.vstack(embeddings)
    np.save(index_path / f"{modality}_embeddings.npy", embeddings)
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the model with specified parameters.")

    parser.add_argument(
        "--models",
        type=json.loads,
        default=json.dumps(
            {
                Modality.VIDEO: "LanguageBind_Video",
                Modality.AUDIO: "LanguageBind_Audio",
                Modality.IMAGE: "LanguageBind_Image",
            }
        ),
        help="JSON string of models by modality",
    )
    parser.add_argument(
        "--data-path", type=str, default="data/<dataset>", help="Path to the dataset directory"
    )
    parser.add_argument(
        "--media-path",
        type=str,
        default="data/<dataset>/videos/all",
        help="Path to the dataset raw media directory",
    )
    parser.add_argument(
        "--modality",
        type=Modality,
        choices=[m.value for m in Modality],
        default=Modality.VIDEO,
        help="Modality to use",
    )  # noqa
    parser.add_argument(
        "--device", type=str, default="cuda", help="Device to use (e.g., 'cuda' or 'cpu')"
    )
    parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch size for model inference"
    )

    args = parser.parse_args()
    main(
        models=args.models,
        dataset_path=Path(args.data_path),
        media_path=Path(args.media_path),
        modality=args.modality,
        device=args.device,
        batch_size=args.batch_size,
    )

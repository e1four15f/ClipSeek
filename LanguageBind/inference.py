import torch

from languagebind import LanguageBind, LanguageBindImageTokenizer, to_device, transform_dict

if __name__ == "__main__":
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("Using", device)
    clip_type = {
        "video": "LanguageBind_Video",  # LanguageBind_Video_FT
        "audio": "LanguageBind_Audio",  # LanguageBind_Audio_FT
        "thermal": "LanguageBind_Thermal",
        "image": "LanguageBind_Image",
        "depth": "LanguageBind_Depth",
    }

    model = LanguageBind(clip_type=clip_type)
    model = model.to(device)
    model.eval()
    pretrained_ckpt = "LanguageBind/LanguageBind_Image"
    tokenizer = LanguageBindImageTokenizer.from_pretrained(pretrained_ckpt)
    modality_transform = {c: transform_dict[c](model.modality_config[c]) for c in clip_type}

    image = ["assets/image/0.jpg", "assets/image/1.jpg"]
    audio = ["assets/audio/0.wav", "assets/audio/1.wav"]
    video = ["assets/video/0.mp4", "assets/video/1.mp4"]
    depth = ["assets/depth/0.png", "assets/depth/1.png"]
    thermal = ["assets/thermal/0.jpg", "assets/thermal/1.jpg"]
    language = [
        "Training a parakeet to climb up a ladder.",
        "A lion climbing a tree to catch a monkey.",
    ]

    inputs = {
        "image": to_device(modality_transform["image"](image), device),
        "video": to_device(modality_transform["video"](video), device),
        "audio": to_device(modality_transform["audio"](audio), device),
        "depth": to_device(modality_transform["depth"](depth), device),
        "thermal": to_device(modality_transform["thermal"](thermal), device),
        "language": to_device(
            tokenizer(
                language, max_length=77, padding="max_length", truncation=True, return_tensors="pt"
            ),
            device,
        ),
    }

    with torch.no_grad():
        embeddings = model(inputs)

    print(
        "Video x Text: \n",
        torch.softmax(embeddings["video"] @ embeddings["language"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )
    print(
        "Image x Text: \n",
        torch.softmax(embeddings["image"] @ embeddings["language"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )
    print(
        "Depth x Text: \n",
        torch.softmax(embeddings["depth"] @ embeddings["language"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )
    print(
        "Audio x Text: \n",
        torch.softmax(embeddings["audio"] @ embeddings["language"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )
    print(
        "Thermal x Text: \n",
        torch.softmax(embeddings["thermal"] @ embeddings["language"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )

    print(
        "Video x Audio: \n",
        torch.softmax(embeddings["video"] @ embeddings["audio"].T, dim=-1).detach().cpu().numpy(),
    )
    print(
        "Image x Depth: \n",
        torch.softmax(embeddings["image"] @ embeddings["depth"].T, dim=-1).detach().cpu().numpy(),
    )
    print(
        "Image x Thermal: \n",
        torch.softmax(embeddings["image"] @ embeddings["thermal"].T, dim=-1)
        .detach()
        .cpu()
        .numpy(),
    )

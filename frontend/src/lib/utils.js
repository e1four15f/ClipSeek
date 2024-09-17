import {
  VideoCameraSolid,
  FileMusicSolid,
  ImageSolid,
  GridSolid,
  QuestionCircleSolid,
} from "flowbite-svelte-icons";

export const getModalityIcon = (modality) => {
  switch (modality) {
    case "video":
      return VideoCameraSolid;
    case "audio":
      return FileMusicSolid;
    case "image":
      return ImageSolid;
    case "hybrid":
      return GridSolid;
    default:
      return QuestionCircleSolid;
  }
};

export const isVideo = (src) => src.match(/\.(mp4|webm|ogg)$/i);
export const isAudio = (src) => src.match(/\.(mp3|wav|ogg)$/i);
export const isImage = (src) => src.match(/\.(jpeg|jpg|png|gif|webp)$/i);

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

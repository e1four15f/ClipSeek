<script>
  import { Button, Modal } from "flowbite-svelte";
  import { getModalityIcon } from "$lib/utils.js";

  export let item;

  let showModal = false;

  const isVideo = (src) => src.match(/\.(mp4|webm|ogg)$/i);
  const isAudio = (src) => src.match(/\.(mp3|wav|ogg)$/i);
  const isImage = (src) => src.match(/\.(jpeg|jpg|png|gif|webp)$/i);
</script>

<button
  class="relative w-full cursor-pointer"
  on:click={() => (showModal = true)}
  aria-label="Open media"
>
  <div
    class="absolute left-1 top-1 z-10 flex rounded bg-black bg-opacity-70 px-2 py-1 text-xs text-white"
  >
    <svelte:component
      this={getModalityIcon(item.modality)}
      class="mr-1 h-4 w-4 text-white"
    />
    {item.score.toFixed(4)}
  </div>
  <div
    class="h-auto w-full rounded object-cover transition duration-300 ease-in-out hover:outline hover:outline-4 hover:outline-offset-[-2px] hover:outline-red-500"
  >
    {#if isVideo(item.src)}
      <video src={item.src} class="w-full rounded" />
    {:else if isImage(item.src)}
      <img src={item.src} class="w-full rounded" />
    {/if}
  </div>
</button>

<Modal bind:open={showModal} size="xl" outsideclose>
  <div class="h-auto w-full">
    {#if isVideo(item.src)}
      <video src={item.src} autoplay controls class="w-75 h-auto" />
    {:else if isAudio(item.src)}
      <audio src={item.src} autoplay controls class="w-75" />
    {:else if isImage(item.src)}
      <img src={item.src} alt={item.src} class="w-75 h-auto" />
    {/if}
  </div>
</Modal>

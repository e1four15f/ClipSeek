<script>
  import { Button, Modal } from "flowbite-svelte";
  import { getModalityIcon, isAudio, isImage, isVideo } from "$lib/utils.js";
  import { onMount, afterUpdate, onDestroy } from "svelte";

  export let item;
  const baseUrl = "http://localhost:8500/resources";
  $: thumbnailUrl = `${baseUrl}/thumbnail/${item.dataset}/${item.version}/${item.path}`;
  $: clipUrl = `${baseUrl}/clip/${item.dataset}/${item.version}/${item.path}?start=${item.span[0]}&end=${item.span[1]}`;
  $: rawUrl = `${baseUrl}/raw/${item.dataset}/${item.version}/${item.path}`;

  let showModal = false;
  let videoElement;
  let Plyr;
  let player;

  onMount(async () => {
    const module = await import("plyr");
    Plyr = module.default;
  });

  afterUpdate(() => {
    if (showModal && isVideo(item.path)) {
      player = new Plyr(videoElement);
    }

    if (showModal && player) {
      player.source = {
        type: "video",
        sources: [{ src: clipUrl, type: "video/mp4" }],
      };
    }
  });

  onDestroy(() => {
    if (player) {
      player.destroy();
    }
  });
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
    <img src={thumbnailUrl} als={thumbnailUrl} class="w-full rounded" />
  </div>
  <div
    class="absolute bottom-1 right-1 z-10 flex rounded bg-black bg-opacity-70 px-2 py-1 text-xs text-white"
  >
    {item.dataset}
  </div>
</button>

<Modal bind:open={showModal} size="xl" outsideclose>
  <div class="h-auto w-full">
    {#if isVideo(item.path)}
      <video bind:this={videoElement} autoplay controls>
        <source src={clipUrl} autoplay class="w-75 h-auto" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <Button href={rawUrl} target="_blank" rel="noopener noreferrer">
        Full Video Link
      </Button>
    {:else if isAudio(item.path)}
      <audio src={rawUrl} autoplay controls class="w-75" />
    {:else if isImage(item.path)}
      <img src={rawUrl} alt={item.src} class="w-75 h-auto" />
    {/if}
  </div>
</Modal>

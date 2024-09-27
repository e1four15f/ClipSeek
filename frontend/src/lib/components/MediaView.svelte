<script>
  import { Button, Modal, P, Heading } from "flowbite-svelte";
  import { getModalityIcon, isAudio, isImage, isVideo } from "$lib/utils.js";
  import {
    onMount,
    afterUpdate,
    onDestroy,
    createEventDispatcher,
  } from "svelte";

  const dispatch = createEventDispatcher();

  export let item;
  const baseUrl = "http://localhost:8500/resources";
  $: thumbnailUrl = `${baseUrl}/thumbnail/${item.dataset}/${item.version}/${item.path}?time=${item.span[0]}`;
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
      player = new Plyr(videoElement, {
        hideControls: false,
        controls: [
          "progress",
          "current-time",
          "duration",
          "mute",
          "volume",
          "captions",
          "fullscreen",
        ],
        autoplay: true,
        loop: { active: true },
      });
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
  <div class="h-[80vh] w-full">
    <div class="flex h-[98%]">
      <div
        class="flex max-h-full w-3/4 items-center justify-center overflow-hidden rounded bg-black"
      >
        {#if isVideo(item.path)}
          <video bind:this={videoElement}>
            <source src={clipUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        {:else if isAudio(item.path)}
          <audio src={rawUrl} autoplay controls />
        {:else if isImage(item.path)}
          <img
            src={rawUrl}
            alt={item.src}
            class="h-full w-full object-contain"
          />
        {:else}
          Unknown media format for file: {item.path}
        {/if}
      </div>

      <div class="flex w-1/4 flex-col justify-between pl-4">
        <div class="info-box">
          <Heading tag="h4" class="mb-2">Information</Heading>
          <P><strong>Dataset:</strong> {item.dataset}</P>
          <P><strong>Version:</strong> {item.version}</P>
          <P><strong>Filename:</strong> {item.path.split("/").pop()}</P>
          <P><strong>Path:</strong> {item.path}</P>
          <P><strong>Score:</strong> {item.score.toFixed(4)}</P>
          <P class="flex items-center">
            <strong>Modality:</strong>
            <svelte:component
              this={getModalityIcon(item.modality)}
              class="mx-1 mt-0.5 h-4 w-4 text-black"
            />
            {item.modality}
          </P>
          {#if isVideo(item.path)}
            <P
              ><strong>Span:</strong>
              {item.span[0]} - {item.span[1]} ({item.span[1] - item.span[0]} seconds)</P
            >
          {/if}
        </div>

        <div class="mt-auto">
          <Button
            href={rawUrl}
            target="_blank"
            rel="noopener noreferrer"
            class="mb-4 w-full"
          >
            Source Link
          </Button>
          <Button
            class="w-full"
            on:click={(event) => {
              showModal = false;
              dispatch("similar", { item });
            }}>Find Similar</Button
          >
        </div>
      </div>
    </div>
  </div>
</Modal>

<style>
  :global(.plyr) {
    object-fit: contain;
    width: 100%;
    height: 100%;
    --plyr-color-main: rgb(235 79 39);
  }
</style>

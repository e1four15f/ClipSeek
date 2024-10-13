<script>
  import { Button, Modal, P, Heading } from "flowbite-svelte";
  import { getModalityIcon, isAudio, isImage, isVideo } from "$lib/utils.js";
  import { getThumbnailUrl, getClipUrl, getRawUrl } from "@config";
  import { onMount, afterUpdate, createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let items;
  $: firstItem = items[0];
  $: currentItem = firstItem;
  $: thumbnailUrls = items.map((item) =>
    getThumbnailUrl(item.dataset, item.version, item.path, item.span[0]),
  );
  $: clipUrl = getClipUrl(
    currentItem.dataset,
    currentItem.version,
    currentItem.path,
    currentItem.span,
  );
  $: rawUrl = getRawUrl(
    currentItem.dataset,
    currentItem.version,
    currentItem.path,
  );

  let showModal = false;
  let thumbnailLoaded = false;
  let thumbnailBroken = false;
  let videoElement;
  let Plyr;
  let player;

  onMount(async () => {
    const module = await import("plyr");
    Plyr = module.default;
  });

  afterUpdate(() => {
    if (!player && showModal && isVideo(currentItem.path)) {
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
      player.source = {
        type: "video",
        sources: [{ src: clipUrl, type: "video/mp4" }],
      };
    }
  });

  $: {
    if (player) {
      player.source = {
        type: "video",
        sources: [{ src: clipUrl, type: "video/mp4" }],
      };
    }
  }
</script>

<button
  class="group relative w-full cursor-pointer"
  on:click={() => (showModal = true)}
  aria-label="Open media"
>
  {#if thumbnailLoaded || thumbnailBroken}
    <div
      class="absolute left-1 top-1 z-10 flex rounded bg-black bg-opacity-70 px-2 py-1 text-xs text-white"
    >
      <svelte:component
        this={getModalityIcon(firstItem.modality)}
        class="mr-1 h-4 w-4 text-white"
      />
      {Math.abs(firstItem.score.toFixed(4)).toFixed(4)}
    </div>
  {/if}

  <div
    class="h-auto w-full rounded object-cover transition duration-300 ease-in-out hover:outline hover:outline-4 hover:outline-offset-[-2px] hover:outline-red-500"
  >
    {#if !thumbnailBroken}
      <img
        src={thumbnailUrls[0]}
        alt={thumbnailUrls[0]}
        class="w-full rounded"
        on:load={() => (thumbnailLoaded = true)}
        on:error={() => (thumbnailBroken = true)}
      />
    {:else}
      <div class="flex h-32 w-full items-center justify-center bg-gray-200">
        <div class="text-center">
          <p>Failed to load the thumbnail</p>
          <p>{currentItem.path.split("/").pop()}</p>
        </div>
      </div>
    {/if}
  </div>

  {#if thumbnailLoaded || thumbnailBroken}
    <div
      class="absolute bottom-1 left-1 z-10 w-32 transform rounded bg-black bg-opacity-70 px-2 py-1 text-xs text-white opacity-0 transition-opacity duration-300 group-hover:opacity-100 group-hover:delay-1000"
    >
      {currentItem.path.split("/").pop()}
    </div>
    <div
      class="absolute bottom-1 right-1 z-10 flex rounded bg-black bg-opacity-70 px-2 py-1 text-xs text-white"
    >
      {firstItem.dataset}
    </div>
  {/if}
</button>

<Modal
  bind:open={showModal}
  size="xl"
  outsideclose
  on:close={() => {
    showModal = false;
    if (player) {
      player.destroy();
      player = null;
    }
  }}
>
  <div class="h-[80vh] w-full">
    <div class="flex h-[98%]">
      <div
        class="flex max-h-full w-3/4 items-center justify-center overflow-hidden rounded bg-black"
      >
        {#if isVideo(currentItem.path)}
          <!-- svelte-ignore a11y-media-has-caption -->
          <video bind:this={videoElement}>
            Your browser does not support the video tag.
          </video>
        {:else if isAudio(currentItem.path)}
          <audio src={rawUrl} autoplay controls />
        {:else if isImage(currentItem.path)}
          <img
            src={rawUrl}
            alt={currentItem.src}
            class="h-full w-full object-contain"
          />
        {:else}
          Unknown media format for file: {currentItem.path}
        {/if}
      </div>

      <div class="flex w-1/4 flex-col justify-between pl-4">
        <div>
          <Heading tag="h4" class="mb-2">Information</Heading>
          <P class="break-words"
            ><strong>Dataset:</strong> {currentItem.dataset}</P
          >
          <P class="break-words"
            ><strong>Version:</strong> {currentItem.version}</P
          >
          <P class="break-words"
            ><strong>Filename:</strong> {currentItem.path.split("/").pop()}</P
          >
          <P class="break-words"><strong>Path:</strong> {currentItem.path}</P>
          <P
            ><strong>Score:</strong>
            {Math.abs(currentItem.score.toFixed(4)).toFixed(4)}</P
          >
          <P class="flex items-center">
            <strong>Modality:</strong>
            <svelte:component
              this={getModalityIcon(currentItem.modality)}
              class="mx-1 mt-0.5 h-4 w-4 text-black"
            />
            {currentItem.modality}
          </P>
          {#if isVideo(currentItem.path)}
            <P
              ><strong>Span:</strong>
              {currentItem.span[0]} - {currentItem.span[1]} ({currentItem
                .span[1] - currentItem.span[0]} seconds)</P
            >
          {/if}
        </div>

        {#if items.length > 2}
          <Heading tag="h5" class="mt-4">More clips from this video</Heading>
          <div class="my-2 max-h-full flex-grow overflow-y-auto">
            {#each items as item, index}
              <div class="relative p-1 pr-4">
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
                {#if item === currentItem}
                  <img
                    src={thumbnailUrls[index]}
                    alt={thumbnailUrls[index]}
                    class="mb-2 w-full cursor-pointer rounded outline outline-4 outline-offset-[-2px] outline-red-500"
                    on:click={() => (currentItem = item)}
                  />
                {:else}
                  <img
                    src={thumbnailUrls[index]}
                    alt={thumbnailUrls[index]}
                    class="mb-2 w-full cursor-pointer rounded"
                    on:click={() => (currentItem = item)}
                  />
                {/if}
                <div
                  class="absolute right-5 top-2 z-10 flex rounded bg-black bg-opacity-70 px-2 text-xs text-white"
                >
                  {item.span[0]} - {item.span[1]}
                </div>
              </div>
            {/each}
          </div>
        {/if}

        <div class="mt-auto flex w-full space-x-2">
          <Button
            href={rawUrl}
            target="_blank"
            rel="noopener noreferrer"
            class="w-1/3"
          >
            Source
          </Button>
          <Button
            class="w-2/3"
            on:click={(event) => {
              showModal = false;
              dispatch("similar", { item: currentItem });
            }}
          >
            Find Similar
          </Button>
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

  * {
    scrollbar-width: thin;
  }
</style>

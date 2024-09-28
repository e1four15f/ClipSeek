<script>
  import { createEventDispatcher, onMount } from "svelte";
  import { Gallery } from "flowbite-svelte";
  import { MediaView } from "$lib/components";
  import { N_RESULT_COLUMNS } from "@config";

  let galleryElement;

  const dispatch = createEventDispatcher();
  const n_cols = N_RESULT_COLUMNS;

  export let items = [];
  $: itemsPerColumn = Array.from({ length: n_cols }, (_, i) =>
    items.filter((_, index) => index % n_cols === i),
  );

  let isLoading = false;
  const handleScroll = () => {
    if (isLoading) return;

    const bottom =
      window.innerHeight + window.scrollY + 500 >= galleryElement.offsetHeight;
    if (bottom) {
      isLoading = true;
      dispatch("continue");

      setTimeout(() => {
        isLoading = false;
      }, 1000);
    }
  };

  onMount(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  });
</script>

<div bind:this={galleryElement} class="flex flex-col items-center">
  <Gallery class="grid grid-cols-{n_cols} gap-4">
    {#each itemsPerColumn as column}
      <div class="flex flex-col gap-4">
        {#each column as item}
          <MediaView
            {item}
            on:similar={(event) =>
              dispatch("similar", { item: event.detail.item })}
          />
        {/each}
      </div>
    {/each}
  </Gallery>
  {#if !items.length}
    <span class="mt-4">No results!</span>
  {/if}
</div>

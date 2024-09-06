<script>
  import { createEventDispatcher, onMount } from "svelte";
  import { Gallery } from "flowbite-svelte";
  import { MediaView } from "$lib/components";

  const dispatch = createEventDispatcher();
  const n_cols = 4;

  export let items = [];
  $: itemsPerColumn = Array.from({ length: n_cols }, (_, i) =>
    items.filter((_, index) => index % n_cols === i),
  );

  let isLoading = false;
  $: if (items.length) {
    isLoading = false;
  }

  const handleScroll = () => {
    if (isLoading) return;

    const bottom =
      window.innerHeight + window.scrollY + 300 >= document.body.offsetHeight;
    if (bottom) {
      isLoading = true;
      dispatch("continue");
    }
  };

  onMount(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  });
</script>

<div class="flex flex-col items-center">
  <Gallery class="grid grid-cols-{n_cols} gap-4">
    {#each itemsPerColumn as column}
      <div class="flex flex-col gap-4">
        {#each column as item}
          <MediaView {item} />
        {/each}
      </div>
    {/each}
  </Gallery>
  {#if !items.length}
    <span class="mt-4">No results!</span>
  {/if}
</div>

<script>
  import { createEventDispatcher, onMount } from "svelte";
  import { Gallery } from "flowbite-svelte";
  import { MediaView } from "$lib/components";
  import { RESULT_COLUMNS } from "@config";

  const dispatch = createEventDispatcher();
  const n_cols = RESULT_COLUMNS;

  export let items = [];
  $: itemsPerColumn = Array.from({ length: n_cols }, (_, i) =>
    items.filter((_, index) => index % n_cols === i),
  );

  let columns = [];
  let isLoading = false;
  const handleScroll = () => {
    if (isLoading) return false;

    const columnHeights = Array.from({ length: n_cols }, (_, i) => {
      const buttons = columns[i]?.querySelectorAll("button.group");
      if (buttons) {
        return Array.from(buttons).reduce(
          (height, el) => height + el.offsetHeight,
          0,
        );
      }
      return 0;
    });
    const minHeight = Math.min(...columnHeights);
    if (window.innerHeight + window.scrollY + 200 >= minHeight) {
      isLoading = true;
      dispatch("continue");

      setTimeout(() => {
        isLoading = false;
      }, 1000);
      return true;
    }
    return false;
  };

  onMount(() => {
    window.addEventListener("scroll", handleScroll);

    const interval = setInterval(() => {
      if (!isLoading) {
        const IsScrolled = handleScroll();
        if (!IsScrolled) {
          clearInterval(interval);
        }
      }
    }, 1000);

    return () => window.removeEventListener("scroll", handleScroll);
  });
</script>

<div class="flex flex-col items-center">
  <Gallery class="grid grid-cols-{n_cols} gap-4">
    {#each itemsPerColumn as column, colIndex}
      <div class="flex flex-col gap-4" bind:this={columns[colIndex]}>
        {#each column as items}
          <MediaView
            {items}
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

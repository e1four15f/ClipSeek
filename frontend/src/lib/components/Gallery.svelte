<script>
    import { createEventDispatcher } from 'svelte';
    import { Gallery, Button } from 'flowbite-svelte';
    import { MediaView } from '$lib/components';

    const dispatch = createEventDispatcher();
    const n_cols = 4;

    export let items = [];
    $: itemsPerColumn = Array.from({ length: n_cols }, (_, i) => 
        items.filter((_, index) => index % n_cols === i)
    );
</script>

<div class="flex flex-col items-center">
    <Gallery class="gap-4 grid-cols-{n_cols}">
        {#each itemsPerColumn as columnItems}
        <Gallery>
            {#each columnItems as item}
            <MediaView {item} />
            {/each}
        </Gallery>
        {/each}
    </Gallery>
    {#if items.length}
    <Button size="xl" on:click={() => dispatch('continue')} class="mt-4 px-20">Find More</Button>
    {:else}
    <span class="mt-4">No results!</span>
    {/if}
</div>

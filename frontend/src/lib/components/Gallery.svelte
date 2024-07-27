<script>
    import { createEventDispatcher } from 'svelte';
    import { Gallery, Button } from 'flowbite-svelte';
    import { MediaView } from '$lib/components';

    const dispatch = createEventDispatcher();

    export let items = [];
</script>

<div class="flex flex-col items-center">
    <!-- TODO Masonary Grid -->
    <Gallery class="gap-4 grid-cols-4">
        {#each items as item}
        <MediaView {item} />
        {/each}
    </Gallery>
    {#if items.length}
    <Button size="xl" on:click={() => dispatch('continue')} class="mt-4 px-20">Find More</Button>
    {:else}
    <span class="mt-4">No results!</span>
    {/if}
</div>

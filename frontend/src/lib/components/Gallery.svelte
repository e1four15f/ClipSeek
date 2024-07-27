<script>
    import { createEventDispatcher } from 'svelte';
    import { Gallery, Button } from 'flowbite-svelte';

    const dispatch = createEventDispatcher();

    export let items = [];
</script>

<div class="flex flex-col items-center">
    <!-- TODO Masonary Grid -->
    <Gallery class="gap-4 grid-cols-4">
        {#each items as item}
        <div class="ring-4 ring-red-600 p-1">
            <video src={item.src} alt={item.alt} class="h-auto max-w-full" />
        </div>
        {/each}
    </Gallery>
    {#if items.length}
    <Button size="xl" on:click={() => dispatch('continue')} class="mt-4 px-20">Find More</Button>
    {:else}
    <span class="mt-4">No results!</span>
    {/if}
</div>

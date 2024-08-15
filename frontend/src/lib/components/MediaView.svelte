<script>
    import { Button, Modal } from 'flowbite-svelte';

    export let item;

    let showModal = false;

    const isVideo = (src) => src.match(/\.(mp4|webm|ogg)$/i);
    const isAudio = (src) => src.match(/\.(mp3|wav|ogg)$/i);
    const isImage = (src) => src.match(/\.(jpeg|jpg|png|gif|webp)$/i);
</script>

<button class="relative cursor-pointer w-full" on:click={() => (showModal = true)} aria-label="Open media">
    <div class="absolute top-1 left-1 bg-black bg-opacity-70 text-white text-xs rounded px-2 py-1 z-10">
        {item.score.toFixed(4)}
    </div>
    {#if isVideo(item.src)}
        <video src={item.src} class="h-auto w-full" />
    {:else if isImage(item.src)}
        <img src={item.src} class="h-auto w-full" />
    {/if}
</button>

<Modal bind:open={showModal} size="xl" outsideclose>
    <div class="h-auto w-full">
    {#if isVideo(item.src)}
        <video src={item.src} autoplay controls />
    {:else if isAudio(item.src)}
        <audio src={item.src} autoplay controls />
    {:else if isImage(item.src)}
        <img src={item.src} alt={item.src} />
    {/if}
    </div>
</Modal>

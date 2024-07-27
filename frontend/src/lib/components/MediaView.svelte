<script>
    import { Button, Modal } from 'flowbite-svelte';
    
    export let item;

    let showModal = false;
</script>

<div style="cursor: pointer" on:click={() => (showModal = true)}>
    <!-- Thumbnail or webp or gif? -->
    <video src={item.src} class="h-auto w-full" />
</div>

<Modal bind:open={showModal} size="xl" outsideclose>
    <video src={item.src} autoplay controls class="h-auto w-full"></video>
</Modal>

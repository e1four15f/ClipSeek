<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { P, Heading, Label, Button, Textarea, Checkbox } from 'flowbite-svelte';
    import { getIndexesInfo } from '$lib/api.js';
  
    const dispatch = createEventDispatcher();

    let query = "Cat in black suit is having meeting";
    let datasets = [];
    let selectedModalities = [];

    onMount(() => {
        async function fetchDatasets() {
            try {
                const response = await getIndexesInfo();
                datasets = response.map(item => ({
                    "dataset": item.dataset,
                    "version": item.version,
                    "label": `${item.dataset}[${item.version}]`,
                    "checked": false,
                }));
                datasets.sort((a, b) => a.value - b.value);
            } catch (error) {
                console.error('Error fetching datasets:', error);
            }
        }
        fetchDatasets();

        return () => {};
    });
    // Check https://flowbite-svelte.com/docs/forms/textarea#Comment_box for Image/Video/Audio as inputs
</script>

<form 
    on:submit|preventDefault={(event) => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const selectedDatasets = datasets.filter(d => d.checked).map(d => ({"dataset": d.dataset, "version": d.version}));
        dispatch('search', { query, selectedDatasets, selectedModalities });
    }}>
    <Label for="query" class="mb-2">Query: {selectedModalities}</Label>
    <Textarea 
        id="query" 
        name="query" 
        placeholder="Your query"
        bind:value={query} 
        on:input={(e) => { 
            e.target.style.height = 'auto'; 
            e.target.style.height = e.target.scrollHeight + 'px'; 
        }}
        on:keydown={(e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.target.closest('form').dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            }
        }}
        required 
        rows="1" 
        cols="50"/>
    <div class="flex justify-end">
        <Button type="submit">Search</Button>
    </div>
    <hr class="my-8"/>
    <Heading tag="h4" class="mb-4">Settings</Heading>
    <div class="flex flex-wrap gap-5">
        <div id="dataset-settings">
            <P class="mb-4 font-semibold text-gray-900">Dataset</P>
            <ul class="w-48">
                {#each datasets as dataset, index}
                <li>
                    <Checkbox name="dataset" id={`checkbox-${index}`} class="p-2" value={index} bind:checked={dataset.checked}>
                        {`${dataset.dataset}[${dataset.version}]`}
                    </Checkbox>
                </li>
                {/each}
            </ul>
        </div>

        <div id="modality-settings">
            <P class="mb-4 font-semibold text-gray-900">Representation</P>
            <ul class="w-48">
                <li><Checkbox name="modality" value="Hybrid" class="p-2" bind:group={selectedModalities}>Hybrid</Checkbox></li>
                <li><Checkbox name="modality" value="Video" class="p-2" bind:group={selectedModalities}>Video</Checkbox></li>
                <li><Checkbox name="modality" value="Image" class="p-2" bind:group={selectedModalities}>Image</Checkbox></li>
                <li><Checkbox name="modality" value="Audio" class="p-2" bind:group={selectedModalities}>Audio</Checkbox></li>
            </ul>
        </div>
    </div>
</form>

<style>
    :global(#query) {
        overflow: hidden;
        resize: none;
    }
</style>

<script>
    import { createEventDispatcher } from 'svelte';
    import { P, Heading, Label, Button, Textarea, Checkbox } from 'flowbite-svelte';
  
    const dispatch = createEventDispatcher();

    export let query = "";
    export let datasets = [];
    export let modalities = [];

    // Check https://flowbite-svelte.com/docs/forms/textarea#Comment_box for Image/Video/Audio as inputs
</script>

<form 
    on:submit|preventDefault={(event) => {
        window.scrollTo({ top: 0 });
        const selectedDatasets = datasets.filter(d => d.checked).map(d => ({"dataset": d.dataset, "version": d.version}));
        const selectedModalities = modalities.filter(m => m.checked).map(m => m.value)
        dispatch('search', { query, selectedDatasets, selectedModalities });
    }}>
    <Label for="query" class="mb-2">Query:</Label>
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
                    <Checkbox name="dataset" id={`checkbox-dataset-${index}`} class="p-2" value={index} bind:checked={dataset.checked}>
                        {`${dataset.dataset}[${dataset.version}]`}
                    </Checkbox>
                </li>
                {/each}
            </ul>
        </div>

        <div id="modality-settings">
            <P class="mb-4 font-semibold text-gray-900">Representation</P>
            <ul class="w-48">
                {#each modalities as modality, index}
                <li>
                    <Checkbox name="modality" id={`checkbox-modality-${index}`} class="p-2" value={index} bind:checked={modality.checked}>
                        {modality.value}
                    </Checkbox>
                </li>
                {/each}
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

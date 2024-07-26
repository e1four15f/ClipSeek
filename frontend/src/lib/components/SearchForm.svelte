<script>
    import { createEventDispatcher } from 'svelte';
    import { Input, Label, Button, Checkbox } from 'flowbite-svelte';
  
    const dispatch = createEventDispatcher();

    let query = "Cat in black suit is having meeting";
    let selectedDatasets = [];
    let selectedModalities = [];
</script>
  
<form on:submit|preventDefault={(event) => dispatch('search', { query, selectedDatasets, selectedModalities })}>
    <Label for="query" class="mb-2">Query:</Label>
    <Input type="text" id="query" name="query" bind:value={query} required/>

    <h2>Settings</h2>
    <div id="dataset-settings">
        <p class="mb-4 font-semibold text-gray-900 dark:text-white">Dataset</p>
        <ul class="w-48 bg-white rounded-lg border border-gray-200 dark:bg-gray-800 dark:border-gray-600 divide-y divide-gray-200 dark:divide-gray-600">
            <li><Checkbox name="dataset" value="MSVD" class="p-3" bind:group={selectedDatasets}>MSVD</Checkbox></li>
            <li><Checkbox name="dataset" value="MSRVTT" class="p-3" bind:group={selectedDatasets}>MSRVTT</Checkbox></li>
            <li><Checkbox name="dataset" value="COCO[val2017]" class="p-3" bind:group={selectedDatasets}>COCO[val2017]</Checkbox></li>
            <li><Checkbox name="dataset" value="COCO[test2017]" class="p-3" bind:group={selectedDatasets}>COCO[test2017]</Checkbox></li>
        </ul>
    </div>

    <div id="modality-settings">
        <p class="mb-4 font-semibold text-gray-900 dark:text-white">Representation</p>
        <ul class="w-48 bg-white rounded-lg border border-gray-200 dark:bg-gray-800 dark:border-gray-600 divide-y divide-gray-200 dark:divide-gray-600">
            <li><Checkbox name="modality" value="Hybrid" class="p-3" bind:group={selectedModalities}>Hybrid</Checkbox></li>
            <li><Checkbox name="modality" value="Video" class="p-3" bind:group={selectedModalities}>Video</Checkbox></li>
            <li><Checkbox name="modality" value="Image" class="p-3" bind:group={selectedModalities}>Image</Checkbox></li>
            <li><Checkbox name="modality" value="Audio" class="p-3" bind:group={selectedModalities}>Audio</Checkbox></li>
        </ul>
    </div>

    <Button type="submit">Search</Button>
</form>

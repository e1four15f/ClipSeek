<script>
    import { createEventDispatcher } from 'svelte';
    import { P, Heading, Label, Button, Textarea, Checkbox } from 'flowbite-svelte';
  
    const dispatch = createEventDispatcher();

    let query = "Cat in black suit is having meeting";
    let selectedDatasets = [];
    let selectedModalities = [];
</script>

<!-- Check https://flowbite-svelte.com/docs/forms/textarea#Comment_box for Image/Video/Audio as inputs -->
<form on:submit|preventDefault={(event) => dispatch('search', { query, selectedDatasets, selectedModalities })}>
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
        required 
        rows="1" 
        cols="50">
    </Textarea>
    <div class="flex justify-end">
        <Button type="submit">Search</Button>
    </div>

    <Heading tag="h4" class="mb-4">Settings</Heading>
    <div class="flex flex-wrap gap-5">
        <div id="dataset-settings">
            <P class="mb-4 font-semibold text-gray-900">Dataset</P>
            <ul class="w-48 bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                <li><Checkbox name="dataset" value="MSVD" class="p-3" bind:group={selectedDatasets}>MSVD</Checkbox></li>
                <li><Checkbox name="dataset" value="MSRVTT" class="p-3" bind:group={selectedDatasets}>MSRVTT</Checkbox></li>
                <li><Checkbox name="dataset" value="COCO[val2017]" class="p-3" bind:group={selectedDatasets}>COCO[val2017]</Checkbox></li>
                <li><Checkbox name="dataset" value="COCO[test2017]" class="p-3" bind:group={selectedDatasets}>COCO[test2017]</Checkbox></li>
            </ul>
        </div>

        <div id="modality-settings">
            <P class="mb-4 font-semibold text-gray-900">Representation</P>
            <ul class="w-48 bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                <li><Checkbox name="modality" value="Hybrid" class="p-3" bind:group={selectedModalities}>Hybrid</Checkbox></li>
                <li><Checkbox name="modality" value="Video" class="p-3" bind:group={selectedModalities}>Video</Checkbox></li>
                <li><Checkbox name="modality" value="Image" class="p-3" bind:group={selectedModalities}>Image</Checkbox></li>
                <li><Checkbox name="modality" value="Audio" class="p-3" bind:group={selectedModalities}>Audio</Checkbox></li>
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
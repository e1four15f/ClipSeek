<script>
  export let data;
  data = data['data'];

  import { Gallery, Input, Fileupload, Label, Checkbox, Search, Drawer, Button, CloseButton, A } from 'flowbite-svelte';
  import { Pane, Splitpanes } from 'svelte-splitpanes';

  const baseUrl = "http://localhost:8500/resources/";

  const splitData = (data, parts) => {
    const result = [];
    for (let i = 0; i < parts; i++) {
      result.push([]);
    }
    data.forEach((item, index) => {
      result[index % parts].push(item);
    });
    return result;
  };

  const dataSplit = splitData(data, 4);
  const images1 = dataSplit[0].map(item => ({
      alt: item.modality,
      src: baseUrl + item.path.replace("../", "")
  }));
  const images2 = dataSplit[1].map(item => ({
      alt: item.modality,
      src: baseUrl + item.path.replace("../", "")
  }));
  const images3 = dataSplit[2].map(item => ({
      alt: item.modality,
      src: baseUrl + item.path.replace("../", "")
  }));
  const images4 = dataSplit[3].map(item => ({
      alt: item.modality,
      src: baseUrl + item.path.replace("../", "")
  }));

  import { onMount } from 'svelte';

  let query = "Cat in black suit is having meeting";
  let selectedDatasets = [];
  let selectedModalities = [];

  const handleSubmit = async (event) => {
      event.preventDefault();

      const formData = new FormData(event.target);
      const response = await fetch('/your-endpoint', {
          method: 'POST',
          body: formData,
      });

      if (response.ok) {
          const result = await response.json();
          // Handle the response data here
          console.log(result);
          // Update your components with the result
      } else {
          console.error('Form submission failed');
      }
  };
</script>

<Splitpanes dblClickSplitter={false}>
  <Pane size={25} snapSize={10}>
    <div id="sidemenu" class="p-5">
      <h1>Video Search</h1>
      <form on:submit|preventDefault={handleSubmit}>
        <Label for="query" class="mb-2">Query:</Label>
        <Input type="text" id="query" name="query" bind:value={query} required/>
    
        Settings
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
    
        <button type="submit">Search</button>
      </form>
    </div>
  </Pane>
  <Pane>
    <div id="content" class="p-10">
      <Gallery class="gap-4 grid-cols-2 md:grid-cols-4">
          <Gallery items={images1} let:item>
            <div class="ring-4 ring-red-600 dark:ring-red-400 p-1">
              <video src={item.src} alt={item.alt} class="h-auto max-w-full" />
            </div>
          </Gallery>
          <Gallery items={images2} let:item>
            <div class="ring-4 ring-red-600 dark:ring-red-400 p-1">
              <video src={item.src} alt={item.alt} class="h-auto max-w-full" />
            </div>
          </Gallery>
          <Gallery items={images3} let:item>
            <div class="ring-4 ring-red-600 dark:ring-red-400 p-1">
              <video src={item.src} alt={item.alt} class="h-auto max-w-full" />
            </div>
          </Gallery>
          <Gallery items={images4} let:item>
            <div class="ring-4 ring-red-600 dark:ring-red-400 p-1">
              <video src={item.src} alt={item.alt} class="h-auto max-w-full" />
            </div>
          </Gallery>
      </Gallery>
    </div>
  </Pane>
</Splitpanes>
  

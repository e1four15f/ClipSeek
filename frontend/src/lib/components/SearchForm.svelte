<script>
  import { createEventDispatcher } from "svelte";
  import {
    P,
    Heading,
    Label,
    Button,
    Textarea,
    Checkbox,
    Dropzone,
  } from "flowbite-svelte";
  import { getModalityIcon } from "$lib/utils.js";

  const dispatch = createEventDispatcher();

  export let text = "";
  export let file = null;
  export let datasets = [];
  export let modalities = [];
</script>

<form
  on:submit|preventDefault={(event) => {
    window.scrollTo({ top: 0 });
    const selectedDatasets = datasets
      .filter((d) => d.checked)
      .map((d) => ({ dataset: d.dataset, version: d.version }));
    const selectedModalities = modalities
      .filter((m) => m.checked)
      .map((m) => m.value);
    dispatch("search", { text, file, selectedDatasets, selectedModalities });
  }}
>
  <Label for="query" class="mb-2">Query or File:</Label>
  <Textarea
    id="query"
    name="query"
    placeholder="Your query"
    bind:value={text}
    on:input={(e) => {
      e.target.style.height = "auto";
      e.target.style.height = e.target.scrollHeight + "px";
    }}
    on:keydown={(e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        e.target
          .closest("form")
          .dispatchEvent(
            new Event("submit", { cancelable: true, bubbles: true }),
          );
      }
    }}
    required
    rows="1"
    cols="50"
  />
  <Dropzone
    id="dropzone"
    name="dropzone"
    class="relative mb-2 h-auto w-full rounded-md border border-dashed border-gray-300 p-2"
    bind:file
    on:drop={(event) => {
      event.preventDefault();
      if (
        event.dataTransfer.items &&
        event.dataTransfer.items[0].kind === "file"
      ) {
        file = event.dataTransfer.items[0].getAsFile();
      } else if (event.dataTransfer.files.length > 0) {
        file = event.dataTransfer.files[0];
      }
    }}
    on:change={(event) => {
      file = event.target.files[0];
    }}
    on:dragover={(event) => {
      event.preventDefault();
    }}
    maxFiles="1"
    acceptedFileTypes="image/*, video/*, audio/*"
  >
    {#if file == null}
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
        <span class="font-semibold">Click to upload</span>
      </p>
      <p class="text-xs text-gray-500 dark:text-gray-400">
        Video, image or audio file
      </p>
    {:else}
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
        <span class="font-semibold">Selected file</span>
      </p>
      <p class="text-xs text-gray-500 dark:text-gray-400">{file.name}</p>
    {/if}
  </Dropzone>
  <div class="flex justify-end">
    <Button
      class="m-1"
      outline
      on:click={(event) => {
        file = null;
      }}>Clear</Button
    >
    <Button type="submit" class="m-1">Search</Button>
  </div>

  <hr class="my-8" />
  <Heading tag="h4" class="mb-4">Settings</Heading>
  <div class="flex flex-wrap gap-5">
    <div id="dataset-settings">
      <P class="mb-4 font-semibold text-gray-900">Dataset</P>
      <ul class="w-48">
        {#each datasets as dataset, index}
          <li>
            <Checkbox
              name="dataset"
              id={`checkbox-dataset-${index}`}
              class="p-2"
              value={index}
              bind:checked={dataset.checked}
            >
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
            <Checkbox
              name="modality"
              id={`checkbox-modality-${index}`}
              class="p-2"
              value={index}
              bind:checked={modality.checked}
            >
              <svelte:component
                this={getModalityIcon(modality.value)}
                class="mr-1 h-4 w-4 text-black"
              />
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

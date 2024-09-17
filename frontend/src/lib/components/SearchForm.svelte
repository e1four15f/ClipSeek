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
    CloseButton,
  } from "flowbite-svelte";
  import { SearchOutline } from "flowbite-svelte-icons";
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
  <div class="relative w-full">
    <Label for="query" class="mb-2">Search by Text or File</Label>
    <div class="relative">
      <Textarea
        id="query"
        name="query"
        placeholder="Your text"
        bind:value={text}
        class="w-full rounded-md border border-gray-300 p-2 pr-10"
        on:input={(e) => {
          file = null;
          const target = e.target;
          const minHeight = target.style.minHeight || "auto";
          target.style.height = minHeight;
          target.style.height =
            Math.max(target.scrollHeight, target.offsetHeight) + "px";
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
        rows="1"
        cols="50"
      />
      {#if text !== ""}
        <CloseButton
          class="absolute right-1 top-1 m-0.5 rounded-lg p-1.5 text-gray-500 hover:bg-gray-300"
          outline
          on:click={() => {
            text = "";
            document.getElementById("query").style.height = "auto";
          }}
        />
      {/if}
    </div>
  </div>

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
      if (file != null) {
        text = "";
      }
    }}
    on:dragover={(event) => {
      event.preventDefault();
    }}
    maxFiles="1"
    acceptedFileTypes="image/*, video/*, audio/*"
  >
    {#if file == null}
      <p class="mb-2 text-sm text-gray-500">
        <span class="font-semibold">Click to upload</span>
      </p>
      <p class="text-xs text-gray-500">Video, image or audio file</p>
    {:else}
      <p class="mb-2 text-sm text-gray-500">
        <span class="font-semibold">Selected file</span>
      </p>
      <p class="text-xs text-gray-500">{file.name}</p>
      <CloseButton
        class="absolute right-1 top-1 m-0.5 rounded-lg p-1.5 text-gray-500 hover:bg-gray-300"
        outline
        on:click={(event) => {
          event.stopPropagation();
          file = null;
        }}
      />
    {/if}
  </Dropzone>
  <div class="flex justify-end">
    <Button type="submit" class="m-1 text-base"
      ><SearchOutline class="mr-1" />Search</Button
    >
  </div>

  <hr class="my-8" />
  <Heading tag="h3" class="mb-4">Settings</Heading>
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
      <Button
        class="mx-1.5 my-3 px-4 py-0.5 text-xs font-medium"
        on:click={(event) => {
          event.preventDefault();
          datasets = datasets.map((dataset) => ({ ...dataset, checked: true }));
        }}>Select All</Button
      >
    </div>

    <div id="modality-settings">
      <P class="mb-4 font-semibold text-gray-900">Representation</P>
      <ul class="w-48">
        {#each modalities as modality, index}
          {#if index === 0}
            <P class="text-sm">Composite</P>
          {/if}
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
          {#if index === 0}
            <P class="mt-2 text-sm">Separate</P>
          {/if}
        {/each}
      </ul>
      <Button
        class="mx-1.5 my-3 px-4 py-0.5 text-xs font-medium"
        on:click={(event) => {
          event.preventDefault();
          modalities = modalities.map((modality) => ({
            ...modality,
            checked: true,
          }));
        }}
      >
        Select All
      </Button>
    </div>
  </div>
</form>

<style>
  :global(#query) {
    overflow: hidden;
    resize: none;
  }
</style>

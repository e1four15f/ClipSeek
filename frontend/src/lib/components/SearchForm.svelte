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
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    TableSearch,
  } from "flowbite-svelte";
  import { SearchOutline, CaretRightSolid } from "flowbite-svelte-icons";
  import { getModalityIcon, isAudio, isImage, isVideo } from "$lib/utils.js";
  import { getThumbnailUrl } from "@config";

  const dispatch = createEventDispatcher();

  export let text = "";
  export let file = null;
  export let reference = null;
  export let datasets = [];
  export let modalities = [];

  $: rawReferenceUrl = reference
    ? getThumbnailUrl(
        reference.dataset,
        reference.version,
        reference.path,
        reference.span[0],
      )
    : null;

  let searchTerm = "";
  let allChecked = false;
  $: filteredDatasets = datasets.filter((d) =>
    d.dataset.toLowerCase().includes(searchTerm.toLowerCase()),
  );
</script>

<form
  class="flex flex-col overflow-hidden"
  on:submit|preventDefault={(event) => {
    dispatch("search", {
      text,
      file,
      reference,
      datasets,
      modalities,
    });
  }}
>
  <Label for="query" class="mb-2">Search by Text or File</Label>
  <div class="relative mx-0.5">
    <Textarea
      name="query"
      placeholder="Your text"
      bind:value={text}
      class="resize-none overflow-hidden rounded-md border border-gray-300 p-2"
      on:input={(e) => {
        file = null;
        reference = null;
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

  <div class="relative mx-0.5">
    <Dropzone
      id="dropzone"
      name="dropzone"
      class="flex h-20 items-center justify-center rounded-md border border-dashed border-gray-300 py-2"
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
          reference = null;
        }
      }}
      on:dragover={(event) => {
        event.preventDefault();
      }}
      maxFiles="1"
      acceptedFileTypes="image/*, video/*, audio/*"
    >
      {#if file !== null || reference !== null}
        <div class="flex items-center">
          {#if file !== null}
            {#if isVideo(file.name) || isAudio(file.name) || isImage(file.name)}
              {#await Promise.resolve(URL.createObjectURL(file)) then fileUrl}
                {#if isVideo(file.name)}
                  <video src={fileUrl} class="mr-2 h-16 w-16 object-cover" />
                {:else if isAudio(file.name)}
                  <audio src={fileUrl} class="mr-2 h-16 w-16 object-cover" />
                {:else if isImage(file.name)}
                  <img
                    src={fileUrl}
                    alt={file.name}
                    class="mr-2 h-16 w-16 object-cover"
                  />
                {/if}
              {/await}
            {/if}
            <div>
              <p class="mb-1 text-sm text-gray-500">
                <span class="font-semibold">Selected file</span>
              </p>
              <p class="w-32 truncate text-xs text-gray-500">{file.name}</p>
            </div>
          {:else if reference !== null}
            <img
              src={rawReferenceUrl}
              alt={reference.path}
              class="mr-2 h-16 w-16 object-cover"
            />
            <div>
              <p class="mb-1 text-sm text-gray-500">
                <span class="font-semibold">Similar to</span>
              </p>
              <p class="w-32 truncate text-xs text-gray-500">
                {reference.path}
              </p>
            </div>
          {/if}
        </div>

        <CloseButton
          class="absolute right-1 top-1 m-0.5 rounded-lg p-1.5 text-gray-500 hover:bg-gray-300"
          outline
          on:click={(event) => {
            event.stopPropagation();
            URL.revokeObjectURL(file);
            file = null;
            reference = null;
          }}
        />
      {:else}
        <p class="mb-2 text-sm text-gray-500">
          <span class="font-semibold">Click to upload</span>
        </p>
        <p class="text-xs text-gray-500">Video, image or audio file</p>
      {/if}
    </Dropzone>

    <div class="flex justify-end">
      <Button type="submit" class="my-1 text-base"
        ><SearchOutline class="mr-1" />Search</Button
      >
    </div>
  </div>

  <hr class="my-2" />

  <Heading tag="h4" class="mb-2">Settings</Heading>
  <div class="flex flex-wrap gap-5">
    <div>
      <P class="mb-2 font-semibold text-gray-900">Representation</P>
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

  <hr class="my-2" />

  <Heading tag="h4">Datasets</Heading>
  <div class="mx-0.5 flex items-center">
    <CaretRightSolid class="mt-1 w-4" />
    <TableSearch
      placeholder="Search by name"
      bind:inputValue={searchTerm}
      innerDivClass="py-1"
      svgClass="w-0"
      divClass="shadow-none m-1 p-0"
      inputClass="bg-gray-50 rounded border border-gray-200 text-gray-900 text-xs p-1 focus:ring-orange-500 focus:border-orange-500"
    />
  </div>
  <div class="h-screen rounded border border-gray-300 bg-white">
    <Table class="w-full overflow-hidden rounded">
      <TableHead class="h-8 border-b-2 border-gray-200">
        <TableHeadCell class="w-10 p-0 pl-3"
          ><Checkbox
            bind:checked={allChecked}
            on:change={(event) => {
              const checked = event.target.checked;
              datasets = datasets.map((dataset) => {
                const existsInFiltered = filteredDatasets.some(
                  (filtered) => filtered.dataset === dataset.dataset,
                );
                return {
                  ...dataset,
                  checked: existsInFiltered ? checked : dataset.checked,
                };
              });
            }}
          /></TableHeadCell
        >
        <TableHeadCell class="w-100 pl-1">Name</TableHeadCell>
        <TableHeadCell class="pl-1">Version</TableHeadCell>
        <TableHeadCell class="w-16 pl-1">Modalities</TableHeadCell>
      </TableHead>
      <TableBody tableBodyClass="divide-y">
        {#each filteredDatasets as dataset, index}
          <TableBodyRow class="h-8 border-gray-100">
            <TableBodyCell class="w-10 p-3 pl-3"
              ><Checkbox
                type="checkbox"
                bind:checked={dataset.checked}
                id={`checkbox-dataset-${index}`}
                on:change={(event) => (allChecked = false)}
              /></TableBodyCell
            >
            <TableBodyCell class="w-100 whitespace-normal break-all p-1"
              >{dataset.dataset}</TableBodyCell
            >
            <TableBodyCell class="whitespace-normal break-all p-1"
              >{dataset.version}</TableBodyCell
            >
            <TableBodyCell class="w-16 p-1">
              <div class="flex">
                {#each dataset.modalities as modality}
                  <svelte:component
                    this={getModalityIcon(modality)}
                    class="mr-0.5 h-3.5 w-3.5 text-black"
                  />
                {/each}
              </div>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
        <TableBodyRow class="">
          <TableBodyCell colspan="4" class="p-0"></TableBodyCell>
        </TableBodyRow>
      </TableBody>
    </Table>
  </div>
</form>

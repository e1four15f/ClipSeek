<script>
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { Heading, P } from "flowbite-svelte";
  import { Pulse } from "svelte-loading-spinners";
  import { Gallery, SearchForm, Logger } from "$lib/components";
  import {
    searchByText,
    searchByFile,
    continueSearch,
    getIndexesInfo,
  } from "$lib/api.js";

  const baseUrl = "http://localhost:8500/resources"; // TODO config? Const?

  let logger;
  let isLoaded = false;

  let text = "Cat in black suit is having meeting";
  let datasets = [];
  let modalities = ["hybrid", "video", "image", "audio"];
  let results = [];
  let sessionId = null;

  onMount(async () => {
    await fetchFormData();
    await handleSearch({
      detail: {
        text: text,
        selectedDatasets: [
          { dataset: "MSRVTT", version: "all" },
          { dataset: "MSVD", version: "5sec" },
        ],
        selectedModalities: ["video"],
      },
    });
    isLoaded = true;
  });

  async function handleSearch(event) {
    const { text, file, selectedDatasets, selectedModalities } = event.detail;
    const input = file == null ? text : file;
    const searchFunc = file == null ? searchByText : searchByFile;
    try {
      const response = await searchFunc(
        input,
        selectedDatasets,
        selectedModalities,
      );
      results = response.data.map((item) => ({
        src: `${baseUrl}/${item.dataset}/${item.version}/${item.path}`,
        dataset: item.dataset,
        version: item.version,
        modality: item.modality,
        score: item.score,
      }));
      sessionId = response.session_id;
      logger.info(`Search: ${file == null ? text : file.name}`);
    } catch (error) {
      results = [];
      logger.error(error);
    }
  }

  async function handleContinueSearch() {
    try {
      const response = await continueSearch(sessionId);
      results = [
        ...results,
        ...response.data.map((item) => ({
          src: `${baseUrl}/${item.dataset}/${item.version}/${item.path}`,
          dataset: item.dataset,
          version: item.version,
          modality: item.modality,
          score: item.score,
        })),
      ];
      logger.info("Continue");
    } catch (error) {
      logger.error(error);
    }
  }

  async function fetchFormData() {
    try {
      const response = await getIndexesInfo();
      datasets = response.map((d) => ({
        dataset: d.dataset,
        version: d.version,
        label: `${d.dataset}[${d.version}]`,
        checked: false,
      }));
      modalities = modalities.map((m) => ({
        value: m,
        checked: false,
      }));
      datasets.sort((a, b) => a.label.localeCompare(b.label));
    } catch (error) {
      logger.error(error);
    }
  }
</script>

<Logger bind:this={logger} />
{#if !isLoaded}
  <div
    class="flex h-screen flex-col items-center justify-center text-center"
    out:fade={{ duration: 500 }}
  >
    <Heading tag="h2" class="mb-4">Video Search</Heading>
    <Pulse size="60" color="#FF3E00" unit="px" duration="1s" />
    <P class="mt-4">Loading</P>
  </div>
{:else}
  <div id="main" class="flex">
    <div id="sidemenu" class="fixed left-0 top-0 h-full w-1/4 p-5">
      <Heading tag="h2" class="mb-4">Video Search</Heading>
      <SearchForm {text} {datasets} {modalities} on:search={handleSearch} />
    </div>
    <div id="content" class="ml-[25%] w-[75%] p-10">
      <Gallery items={results} on:continue={handleContinueSearch} />
    </div>
  </div>
{/if}

<style>
  #sidemenu {
    @apply bg-gray-100;
    /* TODO what is style what in classes? What is the best for readability? */
  }
</style>

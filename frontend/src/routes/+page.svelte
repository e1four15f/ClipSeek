<script>
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { Button, Heading, P } from "flowbite-svelte";
  import { CaretUpSolid } from "flowbite-svelte-icons";
  import { Pulse } from "svelte-loading-spinners";
  import { Gallery, SearchForm, Logger } from "$lib/components";
  import {
    searchByText,
    searchByFile,
    searchByReference,
    continueSearch,
    getIndexesInfo,
  } from "$lib/api.js";

  let logger;
  let isLoaded = false;
  let isScrolled = false;

  let text = "Cat in black suit is having meeting";
  let file = null;
  let reference = null;
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
          { dataset: "MSRVTT", version: "train" },
          { dataset: "MSVD", version: "all" },
        ],
        selectedModalities: ["video"],
      },
    });
    isLoaded = true;
    window.addEventListener("scroll", () => {
      isScrolled = window.scrollY > 200;
    });
  });

  async function handleSearch(event) {
    const { text, file, reference, selectedDatasets, selectedModalities } =
      event.detail;

    let input;
    let searchFunc;
    let message;

    if (file) {
      input = file;
      searchFunc = searchByFile;
      message = file.name;
    } else if (reference) {
      input = reference;
      searchFunc = searchByReference;
      message = reference.path;
    } else {
      input = text;
      searchFunc = searchByText;
      message = text;
    }

    try {
      const response = await searchFunc(
        input,
        selectedDatasets,
        selectedModalities,
      );
      results = response.data;
      sessionId = response.session_id;
      logger.info(`Search: ${message}`);
    } catch (error) {
      results = [];
      logger.error(error);
    }
  }

  async function handleContinue() {
    try {
      const response = await continueSearch(sessionId);
      results = [...results, ...response.data];
      // logger.info("Continue");
    } catch (error) {
      logger.error(error);
    }
  }

  async function handleSimilar(event) {
    const { item } = event.detail;
    text = "";
    file = null;
    reference = item;
  }

  async function fetchFormData() {
    try {
      const response = await getIndexesInfo();
      datasets = response.map((d) => ({ ...d, checked: false }));
      modalities = modalities.map((m) => ({ value: m, checked: false }));
      datasets.sort((a, b) => a.dataset.localeCompare(b.dataset));
    } catch (error) {
      logger.error(error);
    }
  }
</script>

<Logger bind:this={logger} />
{#if !isLoaded}
  <div
    class="relative -mt-40 flex h-screen flex-col items-center justify-center text-center"
    out:fade={{ duration: 500 }}
  >
    <Heading tag="h2" class="mb-4">ClipSeek</Heading>
    <Pulse size="60" color="#FF3E00" unit="px" duration="1s" />
    <P class="mt-4">Loading</P>
  </div>
{:else}
  <div class="flex h-screen">
    <div class="fixed flex h-full w-1/4 flex-col bg-gray-100 p-4">
      <Heading tag="h2" class="mb-4">ClipSeek</Heading>
      <SearchForm
        bind:text
        bind:file
        bind:reference
        bind:datasets
        bind:modalities
        on:search={handleSearch}
      />
    </div>
    <div class="ml-[25%] w-3/4 px-10 py-3">
      <Gallery
        bind:items={results}
        on:continue={handleContinue}
        on:similar={handleSimilar}
      />
    </div>
  </div>
  {#if isScrolled}
    <Button
      class="fixed bottom-10 right-12 z-20 rounded bg-opacity-95 px-10 py-3 text-white shadow-lg"
      on:click={() => window.scrollTo({ top: 0, behavior: "smooth" })}
    >
      <CaretUpSolid /> Scroll to Top
    </Button>
  {/if}
{/if}

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
    continueSearch,
    getIndexesInfo,
  } from "$lib/api.js";

  let logger;
  let isLoaded = false;
  let isScrolled = false;

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
    window.addEventListener("scroll", () => {
      isScrolled = window.scrollY > 200;
    });
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
      results = response.data;
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
      results = [...results, ...response.data];
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
    class="relative -mt-40 flex h-screen flex-col items-center justify-center text-center"
    out:fade={{ duration: 500 }}
  >
    <Heading tag="h2" class="mb-4">ClipSeek</Heading>
    <Pulse size="60" color="#FF3E00" unit="px" duration="1s" />
    <P class="mt-4">Loading</P>
  </div>
{:else}
  <div id="main" class="flex">
    <div id="sidemenu" class="fixed left-0 top-0 h-full w-1/4 p-5">
      <Heading tag="h2" class="mb-4">ClipSeek</Heading>
      <SearchForm {text} {datasets} {modalities} on:search={handleSearch} />
    </div>
    {#if isScrolled}
      <Button
        class="fixed bottom-10 right-12 z-20 rounded bg-opacity-95 px-10 py-3 text-white shadow-lg"
        on:click={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      >
        <CaretUpSolid /> Scroll to Top
      </Button>
    {/if}
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

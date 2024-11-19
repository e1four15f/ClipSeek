<script>
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { Button, Heading, P } from "flowbite-svelte";
  import { CaretUpSolid } from "flowbite-svelte-icons";
  import { Pulse } from "svelte-loading-spinners";
  import { Gallery, SearchForm, Logger } from "$lib/components";

  let logger;
  let isLoaded = false;
  let isScrolled = false;
  let isSearching = false;
  let searchTime = 0;

  let text = "Cat in black suit is having meeting";
  let file = null;
  let reference = null;
  let datasets = [];
  let modalities = ["hybrid", "video", "image", "audio"].map((m) => ({
    value: m,
    checked: true,
  }));
  let results = [];
  let sessionId = null;

  onMount(async () => {
    await fetchFormData();
    await handleSearch({
      detail: {
        text,
        file,
        reference,
        datasets,
        modalities,
      },
    });
    isLoaded = true;
    window.addEventListener("scroll", () => {
      isScrolled = window.scrollY > 200;
    });
  });

  async function handleSearch(event) {
    isSearching = true;
    searchTime = 0;
    const timer = setInterval(() => {
      searchTime += 1;
    }, 1);
    window.scrollTo({ top: 0 });
    const { text, file, reference, datasets, modalities } = event.detail;

    let input;
    let type;
    let message;

    if (file) {
      input = file;
      type = "ByFile";
      message = file.name;
    } else if (reference) {
      input = reference;
      type = "ByReference";
      message = reference.path;
    } else {
      input = text;
      type = "ByText";
      message = text;
    }

    try {
      const formData = new FormData();
      if (input instanceof File) {
        formData.append("file", input);
      }
      const params = JSON.stringify({
        type: type,
        input: input,
        modalities: modalities.filter((m) => m.checked).map((m) => m.value),
        collections: datasets
          .filter((d) => d.checked)
          .map(({ dataset, version }) => ({ dataset, version })),
      });
      formData.append("params", params);

      let response = await fetch("/search", {
        method: "POST",
        body: formData,
      });

      if (response.status == 404) {
        const errorData = await response.json();
        throw new Error(`Not found! ${errorData.detail}`);
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to fetch search data! ${errorData.detail}`);
      }

      const data = await response.json();

      results = Object.values(
        data.data.reduce((acc, item) => {
          const key = `${item.dataset}-${item.version}-${item.path}`;
          (acc[key] = acc[key] || []).push(item);
          return acc;
        }, {}),
      );
      sessionId = data.session_id;
      logger.info(`Search done in ${searchTime} ms\n${message}`);
    } catch (error) {
      results = [];
      logger.error(error);
    } finally {
      isSearching = false;
      clearInterval(timer);
    }
  }

  async function handleContinue() {
    try {
      if (sessionId == null) {
        logger.warning("SessionId is null");
        return;
      }
      const response = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "Continue",
          sessionId: sessionId,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Failed to fetch continue searching data! ${errorData.detail}`,
        );
      }
      const data = await response.json();

      const newResults = Object.values(
        data.data.reduce((acc, item) => {
          const key = `${item.dataset}-${item.version}-${item.path}`;
          (acc[key] = acc[key] || []).push(item);
          return acc;
        }, {}),
      );
      results = [...results, ...newResults];
      logger.info("Continue", 500);
    } catch (error) {
      logger.error(error);
      if (error.message.includes("Continue limit reached")) {
        sessionId = null;
      }
    }
  }

  async function handleSimilar(event) {
    const { item } = event.detail;
    text = "";
    file = null;
    reference = item;
    await handleSearch({
      detail: {
        text,
        file,
        reference,
        datasets,
        modalities,
      },
    });
  }

  async function fetchFormData() {
    try {
      const response = await fetch("/indexes", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      datasets = data
        .map((d) => ({ ...d, checked: false }))
        .sort((a, b) => a.dataset.localeCompare(b.dataset))
        .map((d, index) => ({ ...d, checked: index === 0 }));
    } catch (error) {
      logger.error(error);
    }
  }

  function formatTime(milliseconds) {
    const minutes = Math.floor(milliseconds / 60000);
    const seconds = Math.floor((milliseconds % 60000) / 1000);
    const ms = Math.floor((milliseconds % 1000) / 10);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}:${ms < 10 ? "0" : ""}${ms}`;
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
      <div class="mb-4 flex items-center">
        <img src="favicon.png" alt="favicon.png" class="mr-1 h-10 w-10" />
        <Heading tag="h2" class="mb-1">ClipSeek</Heading>
      </div>
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
      {#if isSearching}
        <div class="flex h-full flex-col items-center justify-center">
          <Pulse size="60" color="#FF3E00" unit="px" duration="1s" />
          <P class="mt-4">Searching</P>
          <P class="font-mono">{formatTime(searchTime)}</P>
        </div>
      {:else}
        <Gallery
          bind:items={results}
          on:continue={handleContinue}
          on:similar={handleSimilar}
        />
      {/if}
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

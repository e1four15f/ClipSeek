<script>
    import { Pane, Splitpanes } from 'svelte-splitpanes';
    import Gallery from '$lib/components/Gallery.svelte';
    import SearchForm from '$lib/components/SearchForm.svelte';
    import Logger from '$lib/components/Logger.svelte';
    import { searchByText, continueSearch } from '$lib/api.js';

    let logger;

    let results = [];
    let sessionId = null;
    const baseUrl = "http://localhost:8500/resources/";
  
    async function handleSearch(event) {
        const { query, selectedDatasets, selectedModalities } = event.detail;
        try {
            const response = await searchByText(query, selectedDatasets, selectedModalities);
            results = response.data.map((item) => ({
                alt: item.modality,
                src: baseUrl + item.path.replace("../", ""),
            }));
            sessionId = response.session_id;
            logger.info('WAAAAAAZZZAAAAAA creatureSilly');
        } catch (error) {
            logger.error(error);
        }
    }
  
    async function handleContinueSearch() {
        try {
            const response = await continueSearch(sessionId);
            results = [
                ...results,
                ...response.data.map((item) => ({
                    alt: item.modality,
                    src: baseUrl + item.path.replace("../", ""),
                })),
            ];
            logger.info('WAAAAAAZZZAAAAAA creatureSilly');
        } catch (error) {
            logger.error(error);
        }
    }
</script>
  
<Logger bind:this={logger}/>

<!-- <div class="fixed top-4 right-4 flex flex-col gap-3 z-50">
    {#each logs as log (log.id)}
      {#if log.status}
      <div class="text-xs text-gray-300 mt-1">{log.timestamp}</div>
        <Toast class={`toast toast.${log.level.toLowerCase()}`} transition={slide} duration={300} on:close={() => closeLog(log.id)}>
          <div slot="header" class="flex justify-between items-center">
            <span class="font-bold">{log.level.toUpperCase()}</span>
            <button on:click={() => closeLog(log.id)}>×</button>
          </div>
          <hr class="my-2 border-t border-gray-200">
          <div class="text-sm">{log.message}</div>
        </Toast>
      {/if}
    {/each}
</div> -->

<Splitpanes dblClickSplitter={false}>
    <Pane size={25} snapSize={10}>
        <div id="sidemenu" class="p-5">
            <h1>Video Search</h1>
            <SearchForm on:search={handleSearch} />
        </div>
    </Pane>
    <Pane>
        <div id="content" class="p-10">
            <Gallery items={results} on:continue={handleContinueSearch} />
        </div>
    </Pane>
</Splitpanes>

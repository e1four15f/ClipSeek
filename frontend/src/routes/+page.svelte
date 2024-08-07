<script>
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    import { Heading, P } from 'flowbite-svelte';
    import { Pulse } from 'svelte-loading-spinners';
    import { Gallery, SearchForm, Logger } from '$lib/components';
    import { searchByText, continueSearch, getIndexesInfo } from '$lib/api.js';

    const baseUrl = "http://localhost:8500/resources/";  // TODO config? Const? 

    let logger;
    let isLoaded = false;
    
    let query = "Cat in black suit is having meeting";
    let datasets = [];
    let modalities = ["hybrid", "video", "image", "audio"];
    let results = [];
    let sessionId = null;

    onMount(async () => {
        await fetchFormData();
        await handleSearch({
            detail: {
                query: query,
                selectedDatasets: [ 
                    { "dataset": "MSRVTT", "version": "all" }, 
                    { "dataset": "MSVD", "version": "5sec" } 
                ],
                selectedModalities: [ "video" ]
            }
        });
        isLoaded = true;
    });
  
    async function handleSearch(event) {
        const { query, selectedDatasets, selectedModalities } = event.detail;
        try {
            const response = await searchByText(query, selectedDatasets, selectedModalities);
            results = response.data.map((item) => ({
                alt: item.modality,
                src: baseUrl + item.path.replace("../", ""),  // TODO
            }));
            sessionId = response.session_id;
            logger.info('Search');
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
                    alt: item.modality,
                    src: baseUrl + item.path.replace("../", ""),  // TODO
                })),
            ];
            logger.info('Continue');
        } catch (error) {
            logger.error(error);
        }
    }

    async function fetchFormData() {
        try {
            const response = await getIndexesInfo();
            datasets = response.map(d => ({
                "dataset": d.dataset,
                "version": d.version,
                "label": `${d.dataset}[${d.version}]`,
                "checked": false,
            }));
            modalities = modalities.map(m => ({
                "value": m,
                "checked": false,
            }))
            datasets.sort((a, b) => a.label.localeCompare(b.label));
        } catch (error) {
            logger.error(error);
        }
    }
</script>

<Logger bind:this={logger}/>
{#if !isLoaded}
<div class="flex flex-col items-center justify-center h-screen text-center" out:fade={{ duration: 500 }}>
    <Heading tag="h2" class="mb-4">Video Search</Heading>
    <Pulse size="60" color="#FF3E00" unit="px" duration="1s" />
    <P class="mt-4">Loading</P>
</div>
{:else}
<div id="main" class="flex">
    <div id="sidemenu" class="p-5 fixed top-0 left-0 h-full w-1/4">
        <Heading tag="h2" class="mb-4">Video Search</Heading>
        <SearchForm query={query} datasets={datasets} modalities={modalities} on:search={handleSearch} />
    </div>
    <div id="content" class="p-10 ml-[25%] w-[75%]">
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

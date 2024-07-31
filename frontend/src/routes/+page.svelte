<script>
    import { onMount } from 'svelte';
    import { Heading } from 'flowbite-svelte';
    import { Gallery, SearchForm, Logger } from '$lib/components';
    import { searchByText, continueSearch } from '$lib/api.js';

    let logger;

    let results = [];
    let sessionId = null;
    const baseUrl = "http://localhost:8500/resources/";  // TODO config? Const? 

    onMount(() => {
        handleSearch({
            detail: {
                query: "Cat in black suit is having meeting",
                selectedDatasets: [ "video" ],
                selectedModalities: [ 
                    { "dataset": "MSRVTT", "version": "all" }, 
                    { "dataset": "MSVD", "version": "5sec" } 
                ]
            }
        })
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
</script>

<Logger bind:this={logger}/>
<div id="main" class="flex">
    <div id="sidemenu" class="p-5 fixed top-0 left-0 h-full w-1/4">
        <Heading tag="h2" class="mb-4">Video Search</Heading>
        <SearchForm on:search={handleSearch} />
    </div>
    <div id="content" class="p-10 ml-[25%] w-[75%]">
        <Gallery items={results} on:continue={handleContinueSearch} />
    </div>
</div>

<style>
    #sidemenu {
        @apply bg-gray-100;  
        /* TODO what is style what in classes? What is the best for readability? */
    }
</style>

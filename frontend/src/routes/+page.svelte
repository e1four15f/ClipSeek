<script>
    import { Pane, Splitpanes } from 'svelte-splitpanes';
    import Gallery from '$lib/components/Gallery.svelte';
    import SearchForm from '$lib/components/SearchForm.svelte';
    import Logger from '$lib/components/Logger.svelte';
    import { searchByText, continueSearch } from '$lib/api.js';

    let logger;

    let results = [];
    let sessionId = null;
    const baseUrl = "http://localhost:8500/resources/";  // TODO config? Const? 
  
    async function handleSearch(event) {
        const { query, selectedDatasets, selectedModalities } = event.detail;
        try {
            const response = await searchByText(query, selectedDatasets, selectedModalities);
            results = response.data.map((item) => ({
                alt: item.modality,
                src: baseUrl + item.path.replace("../", ""),  // TODO
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
                    src: baseUrl + item.path.replace("../", ""),  // TODO
                })),
            ];
            logger.info('WAAAAAAZZZAAAAAA creatureSilly');
        } catch (error) {
            logger.error(error);
        }
    }
</script>

<div>
    <Logger bind:this={logger}/>

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
</div>
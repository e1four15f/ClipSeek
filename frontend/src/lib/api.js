export async function searchByText(query, selectedDatasets, selectedModalities, timeout = 5000) {
    const url = 'http://localhost:8500/api/v1/search/by_text';
    const body = JSON.stringify({
        query,
        modalities: [ "video" ], // TODO selectedModalities,
        collections: [ 
            { "dataset": "MSRVTT", "version": "all" }, 
            { "dataset": "MSVD", "version": "5sec" } 
        ], // TODO selectedDatasets.map(dataset => ({ dataset, version: "all" })),
    });
    console.debug('Sending request to', url, 'body', body);
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
        signal: AbortSignal.timeout(timeout),
    });
  
    if (!response.ok) {
      throw new Error('Failed to fetch search data!');
    }
  
    const data = await response.json();
    return data;
}
  
export async function continueSearch(sessionId, timeout = 5000) {
    const url = 'http://localhost:8500/api/v1/search/continue';
    const body = JSON.stringify({ session_id: sessionId });
    console.debug('Sending request to', url, 'body', body);
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
        signal: AbortSignal.timeout(timeout),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch continue searching data!');
    }

    const data = await response.json();
    return data;
}

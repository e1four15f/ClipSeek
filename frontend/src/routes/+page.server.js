// import { sessionId } from '../stores.js';

// export function load() {
//     return search("Cat in black suit is having meeting");
// };

// export const actions = {
//     default: async ({ request }) => {
//         const data = await request.formData();
//         const query = data.get('query');
//         const datasets = data.getAll('dataset');
//         const modalities = data.getAll('modality');

//         const result = await search(query);
//         return {
//             success: true,
//             data: result,
//         };
//     }
// };

// async function search(query) {
//     const response = await fetch('http://localhost:8500/api/v1/search/by_text', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//             query: query,
//             modalities: ["video"],
//             collections: [
//                 { dataset: "MSRVTT", version: "all" },
//                 { dataset: "MSVD", version: "5sec" }
//             ]
//         })
//     });

//     if (!response.ok) {
//         throw new Error('Failed to fetch search data!');
//     }

//     const data = await response.json();
//     return data;
// }

// async function continueSearch(sessionId) {
//     const response = await fetch('http://localhost:8500/api/v1/search/continue', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//             session_id: sessionId
//         })
//     });

//     if (!response.ok) {
//         throw new Error('Failed to fetch continue searching data!');
//     }

//     const data = await response.json();
//     return data;
// }

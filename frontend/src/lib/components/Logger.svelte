<script>
    import { Toast } from 'flowbite-svelte';
    import { v4 as uuid } from 'uuid';

    let logs = [];

    export const info = logWithConsole('info');
    export const warning = logWithConsole('warn');
    export const error = logWithConsole('error');

    function logWithConsole(level) {
        return (message, timeout = 5000) => {
            console[level](message);
            return addLog(level, message, timeout);
        };
    }
    
    function addLog(level, message, timeout) {
        const id = uuid();
        const timestamp = new Date().toLocaleTimeString();
        logs = [{ id, level, message, status: true, timestamp }, ...logs];
        
        if (timeout) {
            setTimeout(() => {
                logs = logs.map(log => log.id === id ? { ...log, status: false } : log);
            }, timeout);
        }
    }
</script>

<div class="fixed top-2 right-4 flex flex-col gap-3 z-50">
    {#each logs as log (log.id)}
    <Toast 
        bind:toastStatus={log.status}
        color="none" 
        class={`toast ${log.level.toLowerCase()} relative`} 
        position="top-right" 
        align={false}>
        <!-- <div class="text-xs mt-1">{log.timestamp}</div> -->
        <span class="font-bold">{log.level.toUpperCase()}</span>
        <!-- <hr class={`my-2 border-t ${log.level.toLowerCase()}`}> -->
        <div class="text-sm">{log.message}</div>      
    </Toast>
    {/each}
</div>

<style>
    :global(.toast) {
        @apply w-80 p-4 rounded-lg shadow-lg text-white;
    }

    :global(.error) {
        @apply bg-rose-400 bg-opacity-95 text-red-800 border-red-800;
    }

    :global(.warn) {
        @apply bg-amber-400 bg-opacity-95 text-yellow-800 border-yellow-800;
    }

    :global(.info) {
        @apply bg-emerald-400 bg-opacity-95 text-green-800 border-green-800;
    }
</style>

<script>
  import { Toast } from "flowbite-svelte";
  import { v4 as uuid } from "uuid";

  let logs = [];

  export const info = (message, timeout = 2000) =>
    logWithConsole("info", message, timeout);
  export const warning = (message, timeout = 4000) =>
    logWithConsole("warn", message, timeout);
  export const error = (message, timeout = 5000) =>
    logWithConsole("error", message, timeout);

  function logWithConsole(level, message, timeout) {
    console[level](message);
    return addLog(level, message, timeout);
  }

  function addLog(level, message, timeout) {
    const id = uuid();
    const timestamp = new Date().toLocaleTimeString();
    logs = [{ id, level, message, status: true, timestamp }, ...logs];

    if (timeout) {
      setTimeout(() => {
        logs = logs.map((log) =>
          log.id === id ? { ...log, status: false } : log,
        );
      }, timeout);
    }
  }
</script>

<div class="fixed right-4 top-2 z-50 flex flex-col gap-3">
  {#each logs as log (log.id)}
    <Toast
      bind:toastStatus={log.status}
      color="none"
      class={`toast ${log.level.toLowerCase()} relative`}
      position="top-right"
      align={false}
    >
      <div class="flex items-center">
        <span class="font-bold">{log.level.toUpperCase()}</span>
        <span class="ml-1 text-xs">{log.timestamp}</span>
      </div>
      <div class="w-60 whitespace-pre-wrap break-words text-sm">
        {log.message}
      </div>
    </Toast>
  {/each}
</div>

<style>
  :global(.toast) {
    @apply w-80 rounded-lg p-4 text-white shadow-lg;
  }

  :global(.error) {
    @apply border-red-800 bg-rose-400 bg-opacity-95 text-red-800;
  }

  :global(.warn) {
    @apply border-yellow-800 bg-amber-400 bg-opacity-95 text-yellow-800;
  }

  :global(.info) {
    @apply border-green-800 bg-emerald-400 bg-opacity-95 text-green-800;
  }
</style>

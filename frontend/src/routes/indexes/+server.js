import { BACKEND_URL, REQUESTS_TIMEOUT } from "@config";

export async function GET() {
  const url = `${BACKEND_URL()}/indexes/info`;

  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    signal: AbortSignal.timeout(REQUESTS_TIMEOUT()),
  });

  if (!response.ok) {
    return new Response(await response.text(), { status: response.status });
  }

  return response;
}

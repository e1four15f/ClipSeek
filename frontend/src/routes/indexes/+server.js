import { backendUrl, REQUESTS_TIMEOUT } from "@config";

export async function GET() {
  const url = `${backendUrl}/indexes/info`;

  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    signal: AbortSignal.timeout(REQUESTS_TIMEOUT),
  });

  if (!response.ok) {
    return new Response(await response.text(), { status: response.status });
  }

  return response;
}

import {
  BACKEND_URL,
  getThumbnailUrl,
  getClipUrl,
  getRawUrl,
  REQUESTS_TIMEOUT,
} from "@config";

export async function GET({ request, params }) {
  const { type, dataset, version, path } = params;
  const { time, start, end } = Object.fromEntries(
    new URLSearchParams(new URL(request.url).search),
  );

  let resourceUrl;

  switch (type) {
    case "raw":
      resourceUrl = getRawUrl(dataset, version, path, time);
      console.log(resourceUrl);
      break;
    case "clip":
      resourceUrl = getClipUrl(dataset, version, path, start, end);
      break;
    case "thumbnail":
      resourceUrl = getThumbnailUrl(dataset, version, path);
      break;
  }

  const response = await fetch(`${BACKEND_URL()}${resourceUrl}`, {
    method: "GET",
    signal: AbortSignal.timeout(REQUESTS_TIMEOUT()),
  });

  if (!response.ok) {
    return new Response(JSON.stringify({ error: "Resource not found" }), {
      status: 404,
    });
  }

  return response;
}

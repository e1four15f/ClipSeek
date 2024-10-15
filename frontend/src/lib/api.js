import { backendUrl, CANDIDATES_PER_PAGE, REQUESTS_TIMEOUT } from "@config";

const backendSearchUrl = `${backendUrl}/api/v1/search`;

export async function searchByText(
  text,
  modalities,
  collections,
  n_candidates = CANDIDATES_PER_PAGE,
  timeout = REQUESTS_TIMEOUT,
) {
  const url = `${backendSearchUrl}/by_text`;
  const body = new URLSearchParams();
  body.append("text", text);
  body.append(
    "config",
    JSON.stringify({
      n_candidates,
      modalities,
      collections,
    }),
  );

  console.debug("Sending request to", url, "body", body);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
    signal: AbortSignal.timeout(timeout),
  });

  if (response.status == 404) {
    const errorData = await response.json();
    throw new Error(`Not found! ${errorData.detail}`);
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`Failed to fetch search data! ${errorData.detail}`);
  }

  const data = await response.json();
  return data;
}

export async function searchByFile(
  file,
  modalities,
  collections,
  n_candidates = CANDIDATES_PER_PAGE,
  timeout = REQUESTS_TIMEOUT,
) {
  const url = `${backendSearchUrl}/by_file`;
  const body = new FormData();
  body.append("file", file);
  body.append(
    "config",
    JSON.stringify({
      n_candidates,
      modalities,
      collections,
    }),
  );

  console.debug("Sending request to", url, "body", body);
  const response = await fetch(url, {
    method: "POST",
    body: body,
    signal: AbortSignal.timeout(timeout),
  });

  if (response.status == 404) {
    const errorData = await response.json();
    throw new Error(`Not found! ${errorData.detail}`);
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`Failed to fetch search data! ${errorData.detail}`);
  }

  const data = await response.json();
  return data;
}

export async function searchByReference(
  reference,
  modalities,
  collections,
  n_candidates = CANDIDATES_PER_PAGE,
  timeout = REQUESTS_TIMEOUT,
) {
  const url = `${backendSearchUrl}/by_reference`;
  const body = new FormData();
  body.append("id", reference.id);
  body.append("dataset", reference.dataset);
  body.append("version", reference.version);
  body.append(
    "config",
    JSON.stringify({
      n_candidates,
      modalities,
      collections,
    }),
  );

  console.debug("Sending request to", url, "body", body);
  const response = await fetch(url, {
    method: "POST",
    body: body,
    signal: AbortSignal.timeout(timeout),
  });

  if (response.status == 404) {
    const errorData = await response.json();
    throw new Error(`Not found! ${errorData.detail}`);
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`Failed to fetch search data! ${errorData.detail}`);
  }

  const data = await response.json();
  return data;
}

export async function continueSearch(sessionId, timeout = REQUESTS_TIMEOUT) {
  const url = `${backendSearchUrl}/continue`;
  const body = JSON.stringify({ session_id: sessionId });

  console.debug("Sending request to", url, "body", body);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body,
    signal: AbortSignal.timeout(timeout),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      `Failed to fetch continue searching data! ${errorData.detail}`,
    );
  }

  const data = await response.json();
  return data;
}

export async function getIndexesInfo(timeout = REQUESTS_TIMEOUT) {
  const url = `${backendUrl}/indexes/info`;

  console.debug("Sending request to", url);
  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    signal: AbortSignal.timeout(timeout),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`Failed to fetch indexes data! ${errorData.detail}`);
  }

  const data = await response.json();
  return data;
}

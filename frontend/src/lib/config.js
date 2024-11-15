let config = null;

export async function fetchConfig(fetch) {
  const response = await fetch("/", { method: "OPTIONS" });
  config = await response.json();
  return config;
}

export const RESULT_COLUMNS = () => config?.RESULT_COLUMNS;
export const DEVELOPER_MODE = () => config?.DEVELOPER_MODE;
export const CANDIDATES_PER_PAGE = () => config?.CANDIDATES_PER_PAGE;
export const REQUESTS_TIMEOUT = () => config?.REQUESTS_TIMEOUT;
export const BACKEND_URL = () => config?.BACKEND_URL;

export const getThumbnailUrl = (dataset, version, path, time) => {
  let url = `/resources/thumbnail/${dataset}/${version}/${path}`;
  if (time) {
    url += `?time=${time}`;
  }
  return url;
};

export const getClipUrl = (dataset, version, path, start, end) => {
  return `/resources/clip/${dataset}/${version}/${path}?start=${start}&end=${end}`;
};

export const getRawUrl = (dataset, version, path) => {
  return `/resources/raw/${dataset}/${version}/${path}`;
};

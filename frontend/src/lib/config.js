const cfg = _CONFIG;

export const RESULT_COLUMNS = cfg.RESULT_COLUMNS;
export const DEVELOPER_MODE = cfg.DEVELOPER_MODE;
export const CANDIDATES_PER_PAGE = cfg.CANDIDATES_PER_PAGE;
export const REQUESTS_TIMEOUT = cfg.REQUESTS_TIMEOUT;

export const backendUrl = cfg.BACKEND_URL;

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

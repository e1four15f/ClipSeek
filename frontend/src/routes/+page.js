import { fetchConfig } from "@config";

export async function load({ fetch }) {
  const config = await fetchConfig(fetch);
  console.log("Config", config);

  return {
    props: {},
  };
}

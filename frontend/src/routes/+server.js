import yaml from "js-yaml";
import fs from "fs";

export async function OPTIONS({ request }) {
  const config = yaml.load(fs.readFileSync("../config.yaml", "utf8"));

  if (import.meta.env.VITE_BACKEND_URL) {
    config.BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  }

  return new Response(JSON.stringify(config), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

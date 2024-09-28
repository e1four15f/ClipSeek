import yaml from "js-yaml";
import fs from "fs";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import path from "path";

const config = yaml.load(fs.readFileSync("../config.yaml", "utf8"));

console.log("Config", config);

export default defineConfig({
  plugins: [sveltekit()],
  resolve: {
    alias: {
      "@config": path.resolve(__dirname, "./src/lib/config.js"),
    },
  },
  define: {
    _CONFIG: config,
  },
});

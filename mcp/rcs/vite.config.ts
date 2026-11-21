import { defineConfig } from "vite";
import { cloudflare } from "@cloudflare/vite-plugin";

// Cloudflare CLI uses the Vite plugin for local bundling and Worker emulation.
// No public deployment is authorized until the billing $0 gate is verified.
export default defineConfig({
  plugins: [cloudflare()],
});

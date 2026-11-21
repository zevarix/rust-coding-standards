import { defineConfig } from "cf/config";

// No storage, paid services, DNS changes, or scheduled triggers. The endpoint
// is only deployable after the account's $0 Workers boundary is verified.
export default defineConfig({
  worker: {
    name: "rcs-standards-mcp",
    entrypoint: "./src/index.mjs",
    compatibilityDate: "2026-11-20",
    compatibilityFlags: ["nodejs_compat"],
  },
});

import { defineConfig } from "vite";

// Dev server proxies API calls to the local bridge so the browser can use
// same-origin "/api/*" paths (no CORS in dev). In prod the viewer is served
// by the bridge itself (see bridge/main.py static mount) or the hosted site.
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
    },
  },
});

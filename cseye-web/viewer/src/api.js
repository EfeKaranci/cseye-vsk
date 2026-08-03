// In dev, Vite proxies /api -> bridge. Override with VITE_BRIDGE for direct use.
const BASE = import.meta.env.VITE_BRIDGE ?? "/api";
async function j(path, opts) {
    const r = await fetch(BASE + path, opts);
    if (!r.ok)
        throw new Error(`${path} → ${r.status} ${await r.text().catch(() => "")}`);
    return r.json();
}
const post = (path, body) => j(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) });
export const api = {
    health: () => j("/health"),
    models: () => j("/models"),
    attach: () => post("/session/attach"),
    open: (path) => post("/session/open", { path }),
    meta: (sid) => j(`/m/${sid}/meta`),
    geometry: (sid) => j(`/m/${sid}/geometry`),
    extract: (sid, result_sets) => post(`/m/${sid}/extract`, result_sets ? { result_sets } : {}),
    steps: (sid, result) => j(`/m/${sid}/steps?result=${encodeURIComponent(result)}`),
    plan: (sid, story, result, step) => j(`/m/${sid}/plan?story=${encodeURIComponent(story)}&result=${encodeURIComponent(result)}${step ? `&step=${encodeURIComponent(step)}` : ""}`),
    reactions: (sid, result, step) => j(`/m/${sid}/reactions?result=${encodeURIComponent(result)}${step ? `&step=${encodeURIComponent(step)}` : ""}`),
};

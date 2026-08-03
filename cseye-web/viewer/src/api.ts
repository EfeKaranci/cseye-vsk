import type { Meta, Geometry, PlanColumn, Support, ModelInfo } from "./types";

// In dev, Vite proxies /api -> bridge. Override with VITE_BRIDGE for direct use.
const BASE = (import.meta.env.VITE_BRIDGE as string | undefined) ?? "/api";

async function j<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, opts);
  if (!r.ok) throw new Error(`${path} → ${r.status} ${await r.text().catch(() => "")}`);
  return r.json() as Promise<T>;
}
const post = (path: string, body?: unknown) =>
  j(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) });

export const api = {
  health: () => j<{ ok: boolean; etabs: unknown }>("/health"),
  models: () => j<{ count: number; models: ModelInfo[] }>("/models"),
  attach: () => post("/session/attach") as Promise<{ snapshot: string; status: any }>,
  open: (path: string) => post("/session/open", { path }) as Promise<{ snapshot: string; status: any }>,
  meta: (sid: string) => j<Meta>(`/m/${sid}/meta`),
  geometry: (sid: string) => j<Geometry>(`/m/${sid}/geometry`),
  extract: (sid: string, result_sets?: string[]) =>
    post(`/m/${sid}/extract`, result_sets ? { result_sets } : {}) as Promise<{ extracted: string[]; columns: number; supports: number }>,
  steps: (sid: string, result: string) =>
    j<{ result: string; steps: string[] }>(`/m/${sid}/steps?result=${encodeURIComponent(result)}`),
  plan: (sid: string, story: string, result: string, step?: string) =>
    j<{ story: string; result: string; columns: PlanColumn[] }>(
      `/m/${sid}/plan?story=${encodeURIComponent(story)}&result=${encodeURIComponent(result)}${step ? `&step=${encodeURIComponent(step)}` : ""}`),
  reactions: (sid: string, result: string, step?: string) =>
    j<{ result: string; supports: Support[] }>(
      `/m/${sid}/reactions?result=${encodeURIComponent(result)}${step ? `&step=${encodeURIComponent(step)}` : ""}`),
};

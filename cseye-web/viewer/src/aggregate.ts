// Client-side level-slice + step aggregation for the SHARE viewer (reads a
// published bundle). Mirrors the bridge's store.plan / store.reactions so the
// same PlanRenderer works against either data source.
import type { Frame, PlanColumn, Support } from "./types";

interface CForce { P: number; V2: number; V3: number; M2: number; M3: number; }
interface RForce { Fx: number; Fy: number; Fz: number; Mx: number; My: number; Mz: number; }
export interface Bundle {
  result_sets: string[];
  result_kinds: Record<string, string>;
  steps: Record<string, string[]>;
  col_forces: Record<string, Record<string, Record<string, CForce>>>;
  reactions: Record<string, { x: number; y: number; z: number; results: Record<string, Record<string, RForce>> }>;
}
export interface GeomBundle {
  model: string; etabs_version: string; units: string;
  extents: { xmin: number; xmax: number; ymin: number; ymax: number };
  stories: { name: string; elev: number }[];
  frames: Frame[]; grid_lines: any[];
  result_sets: { name: string; kind: string; finished: number | null; extracted?: boolean }[];
  combos?: Record<string, { type: string | null; items: { case: string; sf: number | null }[] }>;
}

export const stepsFor = (b: Bundle, result: string): string[] => (b.steps[result] ?? []).filter(s => s !== "");

export function planColumns(b: Bundle, frames: Frame[], story: string, result: string, step: string | null): PlanColumn[] {
  const out: PlanColumn[] = [];
  for (const f of frames) {
    if (f.type !== "column" || f.story !== story) continue;
    const sm = b.col_forces[f.name]?.[result];
    let pmin: number | null = null, pmax: number | null = null;
    let v2: number | null = null, v3: number | null = null, m2: number | null = null, m3: number | null = null;
    if (sm) {
      const entries = Object.entries(sm);
      if (step != null) {
        const d = sm[step];
        if (d) { pmin = pmax = d.P; v2 = d.V2; v3 = d.V3; m2 = d.M2; m3 = d.M3; }
      } else if (entries.length) {
        const ps = entries.map(([, d]) => d.P);
        pmin = Math.min(...ps); pmax = Math.max(...ps);
        const gov = entries.reduce((a, b2) => Math.abs(b2[1].P) > Math.abs(a[1].P) ? b2 : a)[1];
        v2 = gov.V2; v3 = gov.V3; m2 = gov.M2; m3 = gov.M3;
      }
    }
    out.push({ name: f.name, label: f.label, section: f.section, ix: f.ix, iy: f.iy, iz: f.iz, jx: f.jx, jy: f.jy, jz: f.jz, pmin, pmax, v2, v3, m2, m3 });
  }
  return out;
}

export function reactionSupports(b: Bundle, result: string, step: string | null): Support[] {
  const out: Support[] = [];
  for (const [joint, r] of Object.entries(b.reactions)) {
    const sm = r.results[result]; if (!sm) continue;
    const entries = Object.entries(sm); if (!entries.length) continue;
    const row = step != null ? (sm[step] ?? entries[0][1]) : entries.reduce((a, b2) => Math.abs(b2[1].Fz) > Math.abs(a[1].Fz) ? b2 : a)[1];
    const fzs = entries.map(([, d]) => d.Fz);
    out.push({ joint, x: r.x, y: r.y, z: r.z, fx: row.Fx, fy: row.Fy, fz: row.Fz, mx: row.Mx, my: row.My, mz: row.Mz, fzmin: Math.min(...fzs), fzmax: Math.max(...fzs) });
  }
  return out;
}

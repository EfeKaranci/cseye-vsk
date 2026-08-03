// Share viewer — read-only. Loads a published bundle from Supabase public
// Storage by token (?s=...) and drives the same PlanRenderer via client-side
// aggregation. No bridge, no ETABS.
import { PlanRenderer, type Layer, type ValMode, type Hit, type MeasureMode } from "./render";
import { planColumns, reactionSupports, stepsFor, type Bundle, type GeomBundle } from "./aggregate";
import type { Frame, PlanColumn, Support } from "./types";

const $ = (id: string) => document.getElementById(id)!;
const toast = (m: string) => { const t = $("toast"); t.textContent = m; t.classList.add("show"); clearTimeout((t as any)._t); (t as any)._t = setTimeout(() => t.classList.remove("show"), 2400); };
const busy = (on: boolean) => $("progress").classList.toggle("hide", !on);

const SUPA = (import.meta.env.VITE_SUPABASE_URL as string | undefined) ?? "";
const BUCKET = (import.meta.env.VITE_SUPABASE_BUCKET as string | undefined) ?? "cseye";

const R = new PlanRenderer($("cv") as HTMLCanvasElement);
let geom!: GeomBundle;
let forces!: Bundle;
let colsByStory = new Map<string, Frame[]>();
let level = "", layer: Layer = "geom", result = "", curStep: string | null = null, stepList: string[] = [];

async function boot() {
  const token = new URLSearchParams(location.search).get("s");
  if (!token) {
    $("fileName").textContent = "CSEYE — Shared Viewer";
    $("fileMeta").textContent = "read-only";
    $("status").textContent = "Open a share link (…/share?s=<token>) to view a published model.";
    $("selBody").innerHTML = '<p class="empty">This page shows a shared, read-only ETABS results snapshot — per-level column forces and base reactions.<br><br>Open a <b>/share?s=&lt;token&gt;</b> link generated with the CSEYE <b>Publish</b> button. The full interactive tool (browse models, attach ETABS, extract, publish) runs locally on a machine with ETABS.</p>';
    return;
  }
  if (!SUPA) { $("status").textContent = "Viewer misconfigured: no Supabase URL was baked in at build time."; toast("Misconfigured build"); return; }
  const base = `${SUPA}/storage/v1/object/public/${BUCKET}/snapshots/${token}`;
  busy(true);
  try {
    [geom, forces] = await Promise.all([
      fetch(`${base}/geometry.json`).then(r => { if (!r.ok) throw new Error("geometry " + r.status); return r.json(); }),
      fetch(`${base}/forces.json`).then(r => { if (!r.ok) throw new Error("forces " + r.status); return r.json(); }),
    ]);
  } catch (e: any) { $("status").textContent = "Could not load shared model: " + e.message; toast("Load failed"); busy(false); return; }

  R.extents = geom.extents; R.grids = geom.grid_lines;
  colsByStory = new Map();
  for (const f of geom.frames) if (f.type === "column") (colsByStory.get(f.story) ?? colsByStory.set(f.story, []).get(f.story)!).push(f);
  $("fileName").textContent = geom.model.split(/[\\/]/).pop() ?? geom.model;
  $("fileMeta").textContent = `ETABS ${geom.etabs_version} · ${geom.units} · ${geom.frames.length} frames · ${geom.stories.length} stories`;
  (($("pdfBtn")) as HTMLButtonElement).disabled = false;
  buildLevels(); buildResults();
  let best = geom.stories[0]?.name ?? "", bn = -1;
  for (const st of geom.stories) { const n = colsByStory.get(st.name)?.length ?? 0; if (n > bn) { bn = n; best = st.name; } }
  level = best;
  R.resize(); refresh(); R.fit();
  $("status").textContent = `Shared read-only view · ${forces.result_sets.length} result sets`;
  busy(false);
}

function frameToPlan(f: Frame): PlanColumn {
  return { name: f.name, label: f.label, section: f.section, ix: f.ix, iy: f.iy, iz: f.iz, jx: f.jx, jy: f.jy, jz: f.jz, pmin: null, pmax: null, v2: null, v3: null, m2: null, m3: null };
}
function buildLevels() {
  const host = $("levels"); host.innerHTML = "";
  const sorted = [...geom.stories].sort((a, b) => a.elev - b.elev);
  $("lvCount").textContent = `${sorted.length} lv`;
  for (const st of sorted) {
    const n = colsByStory.get(st.name)?.length ?? 0;
    const el = document.createElement("div"); el.className = "lv";
    el.innerHTML = `<span class="nm">${st.name}</span><span class="lvr"><span class="el mono">${st.elev.toFixed(1)}'</span>${n ? `<span class="cnt mono">${n} col</span>` : ""}</span>`;
    el.onclick = () => { level = st.name; markLevel(); refresh(); };
    host.appendChild(el);
  }
  markLevel();
}
function markLevel() {
  document.querySelectorAll(".lv").forEach(el => el.classList.toggle("on", el.querySelector(".nm")!.textContent === level));
  const st = geom.stories.find(s => s.name === level);
  $("hudLevel").textContent = level; $("hudElev").textContent = "el. " + (st?.elev.toFixed(2) ?? "—") + " ft";
}
function buildResults() {
  const cs = $("caseSel") as HTMLSelectElement; cs.innerHTML = "";
  const mk = (label: string, kind: string) => {
    const names = forces.result_sets.filter(n => (forces.result_kinds[n] ?? "case") === kind);
    if (!names.length) return;
    const g = document.createElement("optgroup"); g.label = label;
    for (const n of names) { const o = document.createElement("option"); o.value = n; o.textContent = n; g.appendChild(o); }
    cs.appendChild(g);
  };
  mk("Load cases", "case"); mk("Load combinations", "combo");
  result = forces.result_sets[0] ?? ""; cs.value = result;
}
function buildStepSel() {
  const sel = $("stepSel") as HTMLSelectElement; sel.innerHTML = "";
  const opt = (v: string, t: string) => { const o = document.createElement("option"); o.value = v; o.textContent = t; sel.appendChild(o); };
  opt("", "Envelope (all)"); for (const s of stepList) opt(s, s);
  sel.value = curStep ?? "";
  $("stepGrp").classList.toggle("hide", !(layer !== "geom" && stepList.length > 1));
}
function cycleStep(dir: number) {
  const opts: (string | null)[] = [null, ...stepList];
  let i = opts.indexOf(curStep); if (i < 0) i = 0;
  curStep = opts[(i + dir + opts.length) % opts.length];
  ($("stepSel") as HTMLSelectElement).value = curStep ?? ""; refresh();
}

function refresh() {
  R.layer = layer;
  R.beams = geom.frames.filter(f => f.type === "beam" && f.story === level);
  markLevel();
  if (layer === "geom") { R.columns = (colsByStory.get(level) ?? []).map(frameToPlan); R.supports = []; }
  else {
    stepList = stepsFor(forces, result); buildStepSel();
    if (layer === "axial") { R.columns = planColumns(forces, geom.frames, level, result, curStep); R.supports = []; }
    else { R.supports = reactionSupports(forces, result, curStep); R.columns = []; }
  }
  const sfx = curStep && layer !== "geom" ? ` · ${curStep}` : "";
  R.title = (layer === "react" ? `Base Reactions — ${result}` : layer === "axial" ? `Column Axial (base) — ${level} — ${result}` : `Column Plan — ${level}`) + sfx;
  R.draw(); updateSummary(); updateLegend();
}
function updateSummary() {
  const el = $("summary"), st = geom.stories.find(s => s.name === level);
  if (layer === "react") {
    $("sumTitle").textContent = "Reactions summary";
    const fz = R.supports.map(s => s.fz), sum = fz.reduce((a, b) => a + b, 0);
    el.innerHTML = `<dt>Result</dt><dd style="font-size:11px">${result}${curStep ? " · " + curStep : ""}</dd><dt>Supports</dt><dd>${R.supports.length}</dd>
      <dt>Σ Fz</dt><dd>${sum.toFixed(0)} k</dd><dt>Max Fz</dt><dd>${Math.max(0, ...fz).toFixed(0)} k</dd><dt>Min Fz</dt><dd>${Math.min(0, ...fz).toFixed(0)} k</dd>`;
    return;
  }
  $("sumTitle").textContent = "Level summary";
  let extra = "";
  if (layer === "axial") { const ps = R.columns.map(c => c.pmin).filter((v): v is number => v != null); if (ps.length) extra = `<dt>Axial min</dt><dd>${Math.min(...ps).toFixed(0)} k</dd><dt>Axial max</dt><dd>${Math.max(...R.columns.map(c => c.pmax ?? 0)).toFixed(0)} k</dd>`; }
  el.innerHTML = `<dt>Elevation</dt><dd>${st?.elev.toFixed(2)} ft</dd><dt>Columns</dt><dd>${R.columns.length}</dd>${extra}`;
}
function updateLegend() {
  const el = $("legend");
  if (layer === "axial") { const m = Math.max(1, ...R.columns.flatMap(c => [Math.abs(c.pmin ?? 0), Math.abs(c.pmax ?? 0)])); el.innerHTML = `<div class="note">Base axial, <b>${result}</b> (kip). Size ∝ |P|.</div><div class="grad"></div><div class="gradrow"><span>−${m.toFixed(0)} comp</span><span>0</span><span>+${m.toFixed(0)} tens</span></div>`; }
  else if (layer === "react") el.innerHTML = `<div><span class="swatch" style="background:var(--up)"></span>Downward (Fz+)</div><div style="margin-top:5px"><span class="swatch" style="background:var(--tens)"></span>Uplift (Fz−)</div>`;
  else el.innerHTML = `<div><span class="swatch" style="background:var(--accent)"></span>Column</div><div style="margin-top:5px"><span class="swatch" style="background:var(--grid)"></span>Beam / grid</div>`;
}

R.onPick = (h: Hit | null) => {
  const el = $("selBody");
  if (!h) { el.innerHTML = '<p class="empty">Pick an element.</p>'; return; }
  if (h.kind === "support") {
    const s = h.data as Support; const env = curStep == null && s.fzmax != null && Math.abs((s.fzmax ?? 0) - (s.fzmin ?? 0)) > 0.05;
    el.innerHTML = `<dl class="kv"><dt>Support</dt><dd>${s.joint}</dd><dt>Plan X,Y</dt><dd>${s.x.toFixed(1)}, ${s.y.toFixed(1)}</dd>
      <dt>Result</dt><dd style="font-size:11px">${result}${curStep ? " · " + curStep : ""}</dd>
      <dt>${env ? "Fz gov" : "Fz"}</dt><dd>${s.fz.toFixed(1)} k</dd>
      ${env ? `<dt>Fz max</dt><dd style="color:var(--up)">${s.fzmax!.toFixed(1)} k</dd><dt>Fz min</dt><dd style="color:var(--tens)">${s.fzmin!.toFixed(1)} k</dd>` : ""}
      <dt>Fx</dt><dd>${s.fx.toFixed(1)} k</dd><dt>Fy</dt><dd>${s.fy.toFixed(1)} k</dd></dl>`;
  } else {
    const c = h.data as PlanColumn; const P = c.pmin == null ? null : (Math.abs(c.pmin) >= Math.abs(c.pmax!) ? c.pmin : c.pmax!);
    const fr = P == null ? "" : `<dt>Axial P</dt><dd>${P.toFixed(1)} k ${P < 0 ? "C" : "T"}</dd><dt>P range</dt><dd>${c.pmin!.toFixed(0)} / ${c.pmax!.toFixed(0)}</dd><dt>M2, M3</dt><dd>${(c.m2 ?? 0).toFixed(0)}, ${(c.m3 ?? 0).toFixed(0)}</dd>`;
    el.innerHTML = `<dl class="kv"><dt>Label</dt><dd>${c.label}</dd><dt>Section</dt><dd style="font-size:11px">${c.section || "—"}</dd><dt>Plan X,Y</dt><dd>${c.ix.toFixed(1)}, ${c.iy.toFixed(1)}</dd>${fr}</dl>`;
  }
};
R.onCursor = (x, y) => { $("cursor").textContent = `x ${x.toFixed(1)}, y ${y.toFixed(1)}`; };
R.onNotify = (m) => toast(m);
const mBtns: [string, MeasureMode][] = [["mDist", "dist"], ["mPerim", "perim"], ["mArea", "area"], ["mAngle", "angle"]];
const syncMeasureBtns = () => { for (const [id, mode] of mBtns) $(id).classList.toggle("active", R.measureMode === mode); };
for (const [id, mode] of mBtns) $(id).onclick = () => { R.setMeasure(mode); syncMeasureBtns(); };
R.onMeasure = (text) => { $("status").textContent = text ?? "Read-only shared view — no ETABS required."; };

$("zin").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1.2);
$("zout").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1 / 1.2);
$("zfit").onclick = () => R.fit();
($("layerSel") as HTMLSelectElement).onchange = e => { layer = (e.target as HTMLSelectElement).value as Layer; $("caseGrp").classList.toggle("hide", layer === "geom"); $("valGrp").classList.toggle("hide", layer !== "axial"); if (layer === "geom") $("stepGrp").classList.add("hide"); $("hudTag").textContent = layer === "react" ? "Reactions" : "Plan @"; refresh(); };
($("caseSel") as HTMLSelectElement).onchange = e => { result = (e.target as HTMLSelectElement).value; curStep = null; refresh(); };
($("valSel") as HTMLSelectElement).onchange = e => { R.vmode = (e.target as HTMLSelectElement).value as ValMode; R.draw(); updateSummary(); };
$("stepPrev").onclick = () => cycleStep(-1); $("stepNext").onclick = () => cycleStep(1);
($("stepSel") as HTMLSelectElement).onchange = e => { curStep = (e.target as HTMLSelectElement).value || null; refresh(); };
$("lyBeams").addEventListener("change", e => { R.showBeams = (e.target as HTMLInputElement).checked; R.draw(); });
$("lyGrids").addEventListener("change", e => { R.showGrids = (e.target as HTMLInputElement).checked; R.draw(); });
$("lyLabels").addEventListener("change", e => { R.showLabels = (e.target as HTMLInputElement).checked; R.draw(); });
$("pdfBtn").onclick = () => R.exportPDF(`CSEYE_${layer}_${level.replace(/\s+/g, "")}.pdf`);
$("themeBtn").onclick = () => { const cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light"); document.documentElement.setAttribute("data-theme", cur === "dark" ? "light" : "dark"); R.draw(); updateLegend(); };

R.resize();
boot();

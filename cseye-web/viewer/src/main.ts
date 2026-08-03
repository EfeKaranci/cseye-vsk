import { api } from "./api";
import { PlanRenderer, type Layer, type ValMode, type Hit, type MeasureMode, type Underlay } from "./render";
import type { Meta, Geometry, PlanColumn, Frame, ModelInfo, Support } from "./types";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorkerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

const $ = (id: string) => document.getElementById(id)!;
const toast = (m: string) => { const t = $("toast"); t.textContent = m; t.classList.add("show"); clearTimeout((t as any)._t); (t as any)._t = setTimeout(() => t.classList.remove("show"), 2400); };
const status = (m: string) => { $("status").textContent = m; };
let busyN = 0;
const busy = (on: boolean) => { busyN = Math.max(0, busyN + (on ? 1 : -1)); $("progress").classList.toggle("hide", busyN === 0); };

const R = new PlanRenderer($("cv") as HTMLCanvasElement);
let sid: string | null = null;
let meta: Meta | null = null;
let geom: Geometry | null = null;
let colsByStory = new Map<string, Frame[]>();
let level = "";
let layer: Layer = "geom";
let result = "";
let allModels: ModelInfo[] = [];
let publishEnabled = false;
interface PdfState { pdf: any; page: number; pages: number; data: Uint8Array; }
interface UDoc { name: string; u: Underlay; st: PdfState; levels: Set<string>; }
const uDocs: UDoc[] = [];
let selDoc: UDoc | null = null;
let stepList: string[] = [];
let curStep: string | null = null;   // null = envelope (aggregate across steps)
const stepsCache = new Map<string, string[]>();

// ---------- connect / models ----------
function setConn(ok: boolean) {
  const c = $("conn"); c.classList.toggle("ok", ok); c.classList.toggle("bad", !ok);
  $("connTxt").textContent = ok ? "Bridge: connected" : "Bridge: offline";
}
function renderModels(q = "") {
  const term = q.trim().toLowerCase();
  const list = term ? allModels.filter(m => m.name.toLowerCase().includes(term) || m.dir.toLowerCase().includes(term)) : allModels;
  $("modelCount").textContent = term ? `${list.length}/${allModels.length}` : `${allModels.length}`;
  const host = $("models"); host.innerHTML = "";
  for (const m of list.slice(0, 500)) {
    const el = document.createElement("div"); el.className = "model";
    el.title = m.path;
    el.innerHTML = `<div class="nm">${m.name}</div><div class="dir">${m.dir}</div>`;
    el.onclick = () => openModel(m.path, el);
    host.appendChild(el);
  }
}
async function connect() {
  busy(true);
  try {
    await api.health();
    setConn(true);
    try { publishEnabled = (await api.config()).publish_enabled; } catch { publishEnabled = false; }
    ($("connectBtn") as HTMLButtonElement).textContent = "Reconnect";
    ($("attachBtn") as HTMLButtonElement).disabled = false;
    status("Bridge connected. Attach the open ETABS model, or pick one to open.");
    const { models } = await api.models();
    allModels = models;
    renderModels(($("modelSearch") as HTMLInputElement).value);
  } catch {
    setConn(false);
    status("Cannot reach bridge at /api. Start the bridge (python run.py) and Reconnect.");
    toast("Bridge not reachable");
  } finally { busy(false); }
}

async function openModel(path: string, el?: HTMLElement) {
  document.querySelectorAll(".model").forEach(m => m.classList.remove("on")); el?.classList.add("on");
  status("Opening in ETABS… (extracting geometry, ~15–30s)"); busy(true);
  try { const r = await api.open(path); await loadSnapshot(r.snapshot); }
  catch (e: any) { toast("Open failed: " + e.message); status(String(e.message)); }
  finally { busy(false); }
}
async function attach() {
  status("Attaching to open ETABS… (extracting geometry, ~15–30s)"); busy(true);
  try { const r = await api.attach(); await loadSnapshot(r.snapshot); }
  catch (e: any) { toast("Attach failed: " + e.message); status(String(e.message)); }
  finally { busy(false); }
}

// ---------- load a snapshot ----------
async function loadSnapshot(s: string) {
  sid = s;
  uDocs.length = 0; selDoc = null; R.underlays = []; R.active = null;   // new model → drop underlays
  meta = await api.meta(s);
  geom = await api.geometry(s);
  buildGridSystems();
  R.extents = meta.extents; R.grids = geom.grid_lines;
  colsByStory = new Map();
  for (const f of geom.frames) {
    if (f.type !== "column") continue;
    (colsByStory.get(f.story) ?? colsByStory.set(f.story, []).get(f.story)!).push(f);
  }
  $("fileName").textContent = meta.model;
  $("fileMeta").textContent = `ETABS ${meta.etabs_version} · ${meta.units} · ${geom.frames.length} frames · ${meta.stories.length} stories`;
  ($("pdfBtn") as HTMLButtonElement).disabled = false;
  ($("publishBtn") as HTMLButtonElement).disabled = !publishEnabled;
  buildLevels(); buildResults();
  // default: most-framed level
  let best = meta.stories[0]?.name ?? "", bn = -1;
  for (const st of meta.stories) { const n = colsByStory.get(st.name)?.length ?? 0; if (n > bn) { bn = n; best = st.name; } }
  level = best;
  R.resize(); await refresh(); R.fit();
  status(`Loaded ${meta.model}. ${meta.locked ? "Analyzed (locked)." : "Not analyzed — geometry only."}`);
}

function buildLevels() {
  const host = $("levels"); host.innerHTML = "";
  const sorted = [...meta!.stories].sort((a, b) => a.elev - b.elev);
  $("lvCount").textContent = `${sorted.length} lv`;
  for (const st of sorted) {
    const n = colsByStory.get(st.name)?.length ?? 0;
    const el = document.createElement("div"); el.className = "lv";
    el.innerHTML = `<span class="nm">${st.name}</span><span class="lvr"><span class="el mono">${st.elev.toFixed(1)}'</span>${n ? `<span class="cnt mono">${n} col</span>` : ""}</span>`;
    el.onclick = () => { level = st.name; markLevel(); applyLevelUnderlay(); refresh(); };
    host.appendChild(el);
  }
  markLevel();
}
function markLevel() {
  document.querySelectorAll(".lv").forEach(el => el.classList.toggle("on", el.querySelector(".nm")!.textContent === level));
  const st = meta!.stories.find(s => s.name === level);
  $("hudLevel").textContent = level; $("hudElev").textContent = "el. " + (st?.elev.toFixed(2) ?? "—") + " ft";
}

function buildResults() {
  const cs = $("caseSel") as HTMLSelectElement; cs.innerHTML = "";
  const mk = (label: string, kind: string) => {
    const names = meta!.result_sets.filter(r => r.kind === kind);
    if (!names.length) return;
    const g = document.createElement("optgroup"); g.label = label;
    for (const r of names) { const o = document.createElement("option"); o.value = r.name; o.textContent = r.name + (r.finished ? "" : r.kind === "case" ? " ·not run" : ""); g.appendChild(o); }
    cs.appendChild(g);
  };
  mk("Load cases", "case"); mk("Load combinations", "combo");
  result = meta!.result_sets.find(r => r.kind === "case" && r.finished)?.name ?? meta!.result_sets[0]?.name ?? "";
  cs.value = result;
}

// ---------- steps (multi-step cases / envelope combos) ----------
async function loadSteps(res: string) {
  if (!stepsCache.has(res)) {
    try { const r = await api.steps(sid!, res); stepsCache.set(res, r.steps.filter(s => s !== "")); }
    catch { stepsCache.set(res, []); }
  }
  stepList = stepsCache.get(res)!;
  buildStepSel();
}
function buildStepSel() {
  const sel = $("stepSel") as HTMLSelectElement; sel.innerHTML = "";
  const opt = (v: string, t: string) => { const o = document.createElement("option"); o.value = v; o.textContent = t; sel.appendChild(o); };
  opt("", "Envelope (all)");
  for (const s of stepList) opt(s, s);
  sel.value = curStep ?? "";
  $("stepGrp").classList.toggle("hide", !(layer !== "geom" && stepList.length > 1));
}
function cycleStep(dir: number) {
  const opts: (string | null)[] = [null, ...stepList];
  let i = opts.indexOf(curStep); if (i < 0) i = 0;
  curStep = opts[(i + dir + opts.length) % opts.length];
  ($("stepSel") as HTMLSelectElement).value = curStep ?? "";
  refresh();
}

// ---------- refresh current view ----------
async function refresh() {
  if (!sid || !meta) return;
  busy(true);
  try {
  R.layer = layer;
  R.beams = geom!.frames.filter(f => f.type === "beam" && f.story === level);
  markLevel();
  if (layer === "geom") {
    R.columns = (colsByStory.get(level) ?? []).map(frameToPlan);
    R.supports = [];
  } else {
    await ensureExtracted(result);
    await loadSteps(result);
    const stepArg = curStep ?? undefined;
    if (layer === "axial") {
      const r = await api.plan(sid, level, result, stepArg); R.columns = r.columns; R.supports = [];
    } else {
      const r = await api.reactions(sid, result, stepArg); R.supports = r.supports; R.columns = [];
    }
  }
  const stepSfx = curStep && layer !== "geom" ? ` · ${curStep}` : "";
  R.title = (layer === "react" ? `Base Reactions — ${result}` : layer === "axial" ? `Column Axial (base) — ${level} — ${result}` : `Column Plan — ${level}`) + stepSfx;
  R.draw(); updateSummary(); updateLegend();
  } finally { busy(false); }
}
function frameToPlan(f: Frame): PlanColumn {
  return { name: f.name, label: f.label, section: f.section, ix: f.ix, iy: f.iy, iz: f.iz, jx: f.jx, jy: f.jy, jz: f.jz, pmin: null, pmax: null, v2: null, v3: null, m2: null, m3: null };
}
async function ensureExtracted(name: string) {
  const rs = meta!.result_sets.find(r => r.name === name);
  if (rs && !rs.extracted) {
    status(`Extracting ${name} from ETABS…`); toast(`Extracting ${name}…`);
    await api.extract(sid!, [name]);
    meta = await api.meta(sid!);           // refresh extracted flags
    status(`Extracted ${name}.`);
  }
}

// ---------- side panels ----------
function updateSummary() {
  const el = $("summary"), st = meta!.stories.find(s => s.name === level);
  if (layer === "react") {
    $("sumTitle").textContent = "Reactions summary";
    const fz = R.supports.map(s => s.fz); const sum = fz.reduce((a, b) => a + b, 0);
    el.innerHTML = `<dt>Result</dt><dd style="font-size:11px">${result}</dd><dt>Supports</dt><dd>${R.supports.length}</dd>
      <dt>Σ Fz</dt><dd>${sum.toFixed(0)} k</dd><dt>Max Fz</dt><dd>${Math.max(0, ...fz).toFixed(0)} k</dd><dt>Min Fz</dt><dd>${Math.min(0, ...fz).toFixed(0)} k</dd>`;
    return;
  }
  $("sumTitle").textContent = "Level summary";
  let extra = "";
  if (layer === "axial") {
    const ps = R.columns.map(c => c.pmin).filter((v): v is number => v != null);
    if (ps.length) extra = `<dt>Axial min</dt><dd>${Math.min(...ps).toFixed(0)} k</dd><dt>Axial max</dt><dd>${Math.max(...R.columns.map(c => c.pmax ?? 0)).toFixed(0)} k</dd><dt>With result</dt><dd>${ps.length}/${R.columns.length}</dd>`;
  }
  el.innerHTML = `<dt>Elevation</dt><dd>${st?.elev.toFixed(2)} ft</dd><dt>Columns</dt><dd>${R.columns.length}</dd>${extra}`;
}
function updateLegend() {
  const el = $("legend");
  if (layer === "axial") {
    const m = Math.max(1, ...R.columns.flatMap(c => [Math.abs(c.pmin ?? 0), Math.abs(c.pmax ?? 0)]));
    el.innerHTML = `<div class="note">Base axial, <b>${result}</b> (kip). Size ∝ |P|.</div><div class="grad"></div><div class="gradrow"><span>−${m.toFixed(0)} comp</span><span>0</span><span>+${m.toFixed(0)} tens</span></div>`;
  } else if (layer === "react") {
    el.innerHTML = `<div><span class="swatch" style="background:var(--up)"></span>Downward (Fz+)</div><div style="margin-top:5px"><span class="swatch" style="background:var(--tens)"></span>Uplift (Fz−)</div>`;
  } else {
    el.innerHTML = `<div><span class="swatch" style="background:var(--accent)"></span>Column</div><div style="margin-top:5px"><span class="swatch" style="background:var(--grid)"></span>Beam / grid</div>`;
  }
}

R.onPick = (h: Hit | null) => {
  const el = $("selBody");
  if (!h) { el.innerHTML = '<p class="empty">Hover or click an element.</p>'; return; }
  if (h.kind === "support") {
    const s = h.data as Support;
    const env = curStep == null && s.fzmax != null && Math.abs((s.fzmax ?? 0) - (s.fzmin ?? 0)) > 0.05;
    el.innerHTML = `<dl class="kv"><dt>Support</dt><dd>${s.joint}</dd><dt>Plan X,Y</dt><dd>${s.x.toFixed(1)}, ${s.y.toFixed(1)}</dd>
      <dt>Result</dt><dd style="font-size:11px">${result}${curStep ? " · " + curStep : ""}</dd>
      <dt>${env ? "Fz gov" : "Fz"}</dt><dd>${s.fz.toFixed(1)} k</dd>
      ${env ? `<dt>Fz max</dt><dd style="color:var(--up)">${s.fzmax!.toFixed(1)} k</dd><dt>Fz min</dt><dd style="color:var(--tens)">${s.fzmin!.toFixed(1)} k</dd>` : ""}
      <dt>Fx</dt><dd>${s.fx.toFixed(1)} k</dd><dt>Fy</dt><dd>${s.fy.toFixed(1)} k</dd>
      <dt>Mx</dt><dd>${s.mx.toFixed(1)}</dd><dt>My</dt><dd>${s.my.toFixed(1)}</dd></dl>`;
  } else {
    const c = h.data as PlanColumn; const P = c.pmin == null ? null : (Math.abs(c.pmin) >= Math.abs(c.pmax!) ? c.pmin : c.pmax!);
    const fr = P == null ? (layer === "geom" ? "" : `<dt>Axial</dt><dd style="color:var(--ink-faint)">no result</dd>`)
      : `<dt>Axial P</dt><dd>${P.toFixed(1)} k ${P < 0 ? "C" : "T"}</dd><dt>P range</dt><dd>${c.pmin!.toFixed(0)} / ${c.pmax!.toFixed(0)}</dd><dt>M2, M3</dt><dd>${(c.m2 ?? 0).toFixed(0)}, ${(c.m3 ?? 0).toFixed(0)}</dd>`;
    el.innerHTML = `<dl class="kv"><dt>Label</dt><dd>${c.label}</dd><dt>Section</dt><dd style="font-size:11px">${c.section || "—"}</dd>
      <dt>Plan X,Y</dt><dd>${c.ix.toFixed(1)}, ${c.iy.toFixed(1)}</dd>${fr}</dl>`;
  }
};
R.onCursor = (x, y) => { $("cursor").textContent = `x ${x.toFixed(1)}, y ${y.toFixed(1)}`; };
R.onNotify = (m) => toast(m);
const mBtns: [string, MeasureMode][] = [["mDist", "dist"], ["mPerim", "perim"], ["mArea", "area"], ["mAngle", "angle"]];
const syncMeasureBtns = () => { for (const [id, mode] of mBtns) $(id).classList.toggle("active", R.measureMode === mode); };
for (const [id, mode] of mBtns) $(id).onclick = () => { R.setMeasure(mode); syncMeasureBtns(); };
R.onMeasure = (text) => status(text ?? "");

// ---------- background PDF underlays (named, multiple, per level) ----------
async function renderPage(st: PdfState): Promise<HTMLCanvasElement> {
  const page = await st.pdf.getPage(st.page);
  const vp = page.getViewport({ scale: 2 });
  const c = document.createElement("canvas"); c.width = vp.width; c.height = vp.height;
  await page.render({ canvasContext: c.getContext("2d")!, viewport: vp }).promise;
  return c;
}
async function loadPdf(file: File) {
  busy(true); status("Rendering PDF…");
  try {
    const data = new Uint8Array(await file.arrayBuffer());
    const pdf = await pdfjsLib.getDocument({ data: data.slice() }).promise;
    const st: PdfState = { pdf, page: 1, pages: pdf.numPages, data };
    const img = await renderPage(st);
    const nm = file.name.replace(/\.pdf$/i, "");
    const doc: UDoc = { name: nm, u: R.makeUnderlay(nm, img, img.width, img.height), st, levels: new Set([level]) };
    uDocs.push(doc); selDoc = doc;
    applyLevelUnderlay(); R.setUnderlayMode("move"); syncPdfModeBtns();
    status("PDF placed — drag to move, corner handles to scale, or 2-point align.");
  } catch (e: any) { toast("PDF load failed: " + e.message); }
  finally { busy(false); }
}
async function changePage(delta: number) {
  if (!selDoc) return;
  const st = selDoc.st, np = st.page + delta;
  if (np < 1 || np > st.pages) return;
  st.page = np;
  const img = await renderPage(st);
  selDoc.u.img = img; selDoc.u.w = img.width; selDoc.u.h = img.height;
  R.draw(); refreshPdfPanel();
}
function applyLevelUnderlay() {
  const docs = uDocs.filter(d => d.levels.has(level));
  R.underlays = docs.map(d => d.u);
  if (!(selDoc && selDoc.levels.has(level))) selDoc = docs[docs.length - 1] ?? null;
  R.active = selDoc?.u ?? null;
  syncPdfModeBtns(); refreshPdfPanel(); R.draw();
}
function selectDoc(d: UDoc) { selDoc = d; R.active = d.u; refreshPdfPanel(); R.draw(); }
function syncPdfModeBtns() {
  $("pdfMove").classList.toggle("active", R.underlayMode === "move");
  $("pdfAlign").classList.toggle("active", R.underlayMode === "align");
}
function refreshPdfPanel() {
  const docs = uDocs.filter(d => d.levels.has(level));
  const list = $("uList"); list.innerHTML = "";
  for (const d of docs) {
    const row = document.createElement("div"); row.className = "urow" + (d === selDoc ? " sel" : "");
    const eye = document.createElement("input"); eye.type = "checkbox"; eye.checked = d.u.visible;
    eye.onclick = ev => { ev.stopPropagation(); d.u.visible = eye.checked; R.draw(); };
    const nm = document.createElement("span"); nm.className = "unm"; nm.textContent = d.name;
    const lv = document.createElement("span"); lv.className = "ulv"; lv.textContent = d.levels.size > 1 ? `${d.levels.size} lv` : "";
    row.appendChild(eye); row.appendChild(nm); row.appendChild(lv);
    row.onclick = () => selectDoc(d);
    list.appendChild(row);
  }
  const on = !!(selDoc && selDoc.levels.has(level));
  $("uCtl").classList.toggle("hide", !on);
  if (on && selDoc) {
    ($("uName") as HTMLInputElement).value = selDoc.name;
    $("pdfPage").textContent = `${selDoc.st.page}/${selDoc.st.pages}`;
    ($("pdfOpacity") as HTMLInputElement).value = String(Math.round(selDoc.u.opacity * 100));
    const deg = Math.round(selDoc.u.rot * 180 / Math.PI);
    ($("pdfRotate") as HTMLInputElement).value = String(deg); $("pdfRotVal").textContent = deg + "°";
  }
}
$("pdfLoad").onclick = () => ($("pdfFile") as HTMLInputElement).click();
($("pdfFile") as HTMLInputElement).addEventListener("change", e => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) loadPdf(f); (e.target as HTMLInputElement).value = ""; });
$("pdfPrev").onclick = () => changePage(-1);
$("pdfNext").onclick = () => changePage(1);
($("uName") as HTMLInputElement).addEventListener("change", e => { if (selDoc) { selDoc.name = (e.target as HTMLInputElement).value || selDoc.name; refreshPdfPanel(); } });
($("pdfOpacity") as HTMLInputElement).addEventListener("input", e => R.setUnderlayOpacity(+(e.target as HTMLInputElement).value / 100));
($("pdfRotate") as HTMLInputElement).addEventListener("input", e => { const d = +(e.target as HTMLInputElement).value; R.rotateUnderlay(d); $("pdfRotVal").textContent = d + "°"; });
$("pdfPlus").onclick = () => R.scaleUnderlayBy(1.05);
$("pdfMinus").onclick = () => R.scaleUnderlayBy(1 / 1.05);
$("pdfMove").onclick = () => { R.setUnderlayMode(R.underlayMode === "move" ? "off" : "move"); syncPdfModeBtns(); };
$("pdfAlign").onclick = () => { R.setUnderlayMode(R.underlayMode === "align" ? "off" : "align"); syncPdfModeBtns(); };
$("pdfClear").onclick = () => { if (!selDoc) return; const i = uDocs.indexOf(selDoc); if (i >= 0) uDocs.splice(i, 1); selDoc = null; applyLevelUnderlay(); };
R.onUnderlay = (msg) => { status(msg); $("pdfHint").textContent = msg; syncPdfModeBtns(); };

// copy the selected drawing to other levels (same alignment)
$("pdfCopy").onclick = () => {
  if (!selDoc || !meta) return;
  const host = $("copyOpts"); host.innerHTML = "";
  for (const st of [...meta.stories].sort((a, b) => b.elev - a.elev)) {
    const row = document.createElement("label"); row.className = "row";
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.className = "copychk"; cb.value = st.name;
    cb.checked = selDoc.levels.has(st.name); cb.disabled = st.name === level;
    const s = document.createElement("span"); s.textContent = `${st.name}  (${st.elev.toFixed(1)}')`;
    row.appendChild(cb); row.appendChild(s); host.appendChild(row);
  }
  $("copyModal").classList.remove("hide");
};
$("copyCancel").onclick = () => $("copyModal").classList.add("hide");
$("copyGo").onclick = () => {
  if (selDoc) {
    const chosen = ([...document.querySelectorAll(".copychk")] as HTMLInputElement[]).filter(c => c.checked).map(c => c.value);
    selDoc.levels = new Set([level, ...chosen]);
  }
  $("copyModal").classList.add("hide"); applyLevelUnderlay();
};

// grid-system toggles (only shown when a model has more than one grid system)
function buildGridSystems() {
  const host = $("gridSys"); host.innerHTML = ""; R.hiddenGridSystems.clear();
  const sys = [...new Set((geom?.grid_lines ?? []).map(g => g.sys).filter((x): x is string => !!x))];
  if (sys.length < 2) return;
  for (const s of sys) {
    const row = document.createElement("label"); row.className = "gsys";
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.checked = true;
    cb.onchange = () => { cb.checked ? R.hiddenGridSystems.delete(s) : R.hiddenGridSystems.add(s); R.draw(); };
    const t = document.createElement("span"); t.textContent = "grid: " + s;
    row.appendChild(cb); row.appendChild(t); host.appendChild(row);
  }
}

function u8ToB64(u8: Uint8Array): string {
  let s = ""; const chunk = 0x8000;
  for (let i = 0; i < u8.length; i += chunk) s += String.fromCharCode(...u8.subarray(i, i + chunk));
  return btoa(s);
}
function gatherUnderlays(): unknown[] | undefined {
  const out = uDocs.map(d => ({
    name: d.name, pdf: u8ToB64(d.st.data), page: d.st.page,
    tx: d.u.tx, ty: d.u.ty, s: d.u.s, rot: d.u.rot, opacity: d.u.opacity, levels: [...d.levels],
  }));
  return out.length ? out : undefined;
}

// ---------- controls ----------
$("connectBtn").onclick = connect;
$("attachBtn").onclick = attach;
($("modelSearch") as HTMLInputElement).addEventListener("input", e => renderModels((e.target as HTMLInputElement).value));
$("modelsHdr").onclick = () => {
  const c = $("modelsWrap").classList.toggle("hide");
  $("modelsCaret").textContent = c ? "▸" : "▾";
  $("modelsHdr").setAttribute("aria-expanded", String(!c));
};
$("zin").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1.2);
$("zout").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1 / 1.2);
$("zfit").onclick = () => R.fit();
($("layerSel") as HTMLSelectElement).onchange = e => {
  layer = (e.target as HTMLSelectElement).value as Layer;
  $("caseGrp").classList.toggle("hide", layer === "geom");
  $("valGrp").classList.toggle("hide", layer !== "axial");
  if (layer === "geom") $("stepGrp").classList.add("hide");
  $("hudTag").textContent = layer === "react" ? "Reactions" : "Plan @";
  refresh();
};
($("caseSel") as HTMLSelectElement).onchange = e => { result = (e.target as HTMLSelectElement).value; curStep = null; refresh(); };
$("stepPrev").onclick = () => cycleStep(-1);
$("stepNext").onclick = () => cycleStep(1);
($("stepSel") as HTMLSelectElement).onchange = e => { curStep = (e.target as HTMLSelectElement).value || null; refresh(); };
($("valSel") as HTMLSelectElement).onchange = e => { R.vmode = (e.target as HTMLSelectElement).value as ValMode; R.draw(); updateSummary(); };
$("lyBeams").addEventListener("change", e => { R.showBeams = (e.target as HTMLInputElement).checked; R.draw(); });
$("lyGrids").addEventListener("change", e => { R.showGrids = (e.target as HTMLInputElement).checked; R.draw(); });
$("lyLabels").addEventListener("change", e => { R.showLabels = (e.target as HTMLInputElement).checked; R.draw(); });
$("pdfBtn").onclick = () => R.exportPDF(`CSEYE_${layer}_${level.replace(/\s+/g, "")}.pdf`);
function openPublish() {
  if (!sid || !meta) return;
  ($("pubLabel") as HTMLInputElement).value = meta.model;
  const host = $("pubOpts"); host.innerHTML = "";
  const section = (title: string, kind: "case" | "combo") => {
    const sets = meta!.result_sets.filter(r => r.kind === kind && (kind === "combo" || r.finished));
    if (!sets.length) return;
    const h = document.createElement("h4"); h.textContent = title; host.appendChild(h);
    for (const r of sets) {
      const row = document.createElement("label"); row.className = "row";
      const cb = document.createElement("input"); cb.type = "checkbox"; cb.className = "pubchk"; cb.value = r.name; cb.checked = !!r.extracted;
      const nm = document.createElement("span"); nm.textContent = r.name;
      row.appendChild(cb); row.appendChild(nm);
      if (r.extracted) { const t = document.createElement("span"); t.className = "tag"; t.textContent = "extracted"; row.appendChild(t); }
      host.appendChild(row);
    }
  };
  section("Load cases", "case"); section("Load combinations", "combo");
  $("pubModal").classList.remove("hide");
}
const chks = () => [...document.querySelectorAll(".pubchk")] as HTMLInputElement[];
$("publishBtn").onclick = openPublish;
$("pubCancel").onclick = () => $("pubModal").classList.add("hide");
$("pubSelAll").onclick = () => chks().forEach(c => c.checked = true);
$("pubSelNone").onclick = () => chks().forEach(c => c.checked = false);
$("pubSelExtracted").onclick = () => chks().forEach(c => c.checked = !!meta!.result_sets.find(r => r.name === c.value)?.extracted);
$("pubGo").onclick = async () => {
  const sel = chks().filter(c => c.checked).map(c => c.value);
  if (!sel.length) { toast("Select at least one result set."); return; }
  $("pubModal").classList.add("hide"); busy(true);
  try {
    const missing = sel.filter(n => !meta!.result_sets.find(r => r.name === n)?.extracted);
    for (const n of missing) { status(`Extracting ${n} from ETABS…`); await api.extract(sid!, [n]); }
    if (missing.length) meta = await api.meta(sid!);
    status("Publishing to Supabase…");
    const label = ($("pubLabel") as HTMLInputElement).value.trim() || undefined;
    const r = await api.publish(sid!, { label, results: sel, underlays: gatherUnderlays() });
    const url = r.share_url ?? r.public_base;
    try { await navigator.clipboard.writeText(url); } catch { /* clipboard may be blocked */ }
    status("Published → " + url);
    toast(r.share_url ? `Share link copied — ${sel.length} result sets` : "Published (set CSEYE_SHARE_URL for a link)");
  } catch (e: any) { toast("Publish failed: " + e.message); status(String(e.message)); }
  finally { busy(false); }
};
$("themeBtn").onclick = () => {
  const cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", cur === "dark" ? "light" : "dark"); R.draw(); updateLegend();
};

R.resize();
connect();

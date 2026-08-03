import { api } from "./api";
import { PlanRenderer } from "./render";
const $ = (id) => document.getElementById(id);
const toast = (m) => { const t = $("toast"); t.textContent = m; t.classList.add("show"); clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove("show"), 2400); };
const status = (m) => { $("status").textContent = m; };
let busyN = 0;
const busy = (on) => { busyN = Math.max(0, busyN + (on ? 1 : -1)); $("progress").classList.toggle("hide", busyN === 0); };
const R = new PlanRenderer($("cv"));
let sid = null;
let meta = null;
let geom = null;
let colsByStory = new Map();
let level = "";
let layer = "geom";
let result = "";
let allModels = [];
let stepList = [];
let curStep = null; // null = envelope (aggregate across steps)
const stepsCache = new Map();
// ---------- connect / models ----------
function setConn(ok) {
    const c = $("conn");
    c.classList.toggle("ok", ok);
    c.classList.toggle("bad", !ok);
    $("connTxt").textContent = ok ? "Bridge: connected" : "Bridge: offline";
}
function renderModels(q = "") {
    const term = q.trim().toLowerCase();
    const list = term ? allModels.filter(m => m.name.toLowerCase().includes(term) || m.dir.toLowerCase().includes(term)) : allModels;
    $("modelCount").textContent = term ? `${list.length}/${allModels.length}` : `${allModels.length}`;
    const host = $("models");
    host.innerHTML = "";
    for (const m of list.slice(0, 500)) {
        const el = document.createElement("div");
        el.className = "model";
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
        $("connectBtn").textContent = "Reconnect";
        $("attachBtn").disabled = false;
        status("Bridge connected. Attach the open ETABS model, or pick one to open.");
        const { models } = await api.models();
        allModels = models;
        renderModels($("modelSearch").value);
    }
    catch {
        setConn(false);
        status("Cannot reach bridge at /api. Start the bridge (python run.py) and Reconnect.");
        toast("Bridge not reachable");
    }
    finally {
        busy(false);
    }
}
async function openModel(path, el) {
    document.querySelectorAll(".model").forEach(m => m.classList.remove("on"));
    el?.classList.add("on");
    status("Opening in ETABS… (extracting geometry, ~15–30s)");
    busy(true);
    try {
        const r = await api.open(path);
        await loadSnapshot(r.snapshot);
    }
    catch (e) {
        toast("Open failed: " + e.message);
        status(String(e.message));
    }
    finally {
        busy(false);
    }
}
async function attach() {
    status("Attaching to open ETABS… (extracting geometry, ~15–30s)");
    busy(true);
    try {
        const r = await api.attach();
        await loadSnapshot(r.snapshot);
    }
    catch (e) {
        toast("Attach failed: " + e.message);
        status(String(e.message));
    }
    finally {
        busy(false);
    }
}
// ---------- load a snapshot ----------
async function loadSnapshot(s) {
    sid = s;
    meta = await api.meta(s);
    geom = await api.geometry(s);
    R.extents = meta.extents;
    R.grids = geom.grid_lines;
    colsByStory = new Map();
    for (const f of geom.frames) {
        if (f.type !== "column")
            continue;
        (colsByStory.get(f.story) ?? colsByStory.set(f.story, []).get(f.story)).push(f);
    }
    $("fileName").textContent = meta.model;
    $("fileMeta").textContent = `ETABS ${meta.etabs_version} · ${meta.units} · ${geom.frames.length} frames · ${meta.stories.length} stories`;
    $("pdfBtn").disabled = false;
    buildLevels();
    buildResults();
    // default: most-framed level
    let best = meta.stories[0]?.name ?? "", bn = -1;
    for (const st of meta.stories) {
        const n = colsByStory.get(st.name)?.length ?? 0;
        if (n > bn) {
            bn = n;
            best = st.name;
        }
    }
    level = best;
    R.resize();
    await refresh();
    R.fit();
    status(`Loaded ${meta.model}. ${meta.locked ? "Analyzed (locked)." : "Not analyzed — geometry only."}`);
}
function buildLevels() {
    const host = $("levels");
    host.innerHTML = "";
    const sorted = [...meta.stories].sort((a, b) => a.elev - b.elev);
    $("lvCount").textContent = `${sorted.length} lv`;
    for (const st of sorted) {
        const n = colsByStory.get(st.name)?.length ?? 0;
        const el = document.createElement("div");
        el.className = "lv";
        el.innerHTML = `<span class="nm">${st.name}</span><span class="el mono">${st.elev.toFixed(1)}'</span>` + (n ? `<span class="cnt mono">${n} col</span>` : "");
        el.onclick = () => { level = st.name; markLevel(); refresh(); };
        host.appendChild(el);
    }
    markLevel();
}
function markLevel() {
    document.querySelectorAll(".lv").forEach(el => el.classList.toggle("on", el.querySelector(".nm").textContent === level));
    const st = meta.stories.find(s => s.name === level);
    $("hudLevel").textContent = level;
    $("hudElev").textContent = "el. " + (st?.elev.toFixed(2) ?? "—") + " ft";
}
function buildResults() {
    const cs = $("caseSel");
    cs.innerHTML = "";
    const mk = (label, kind) => {
        const names = meta.result_sets.filter(r => r.kind === kind);
        if (!names.length)
            return;
        const g = document.createElement("optgroup");
        g.label = label;
        for (const r of names) {
            const o = document.createElement("option");
            o.value = r.name;
            o.textContent = r.name + (r.finished ? "" : r.kind === "case" ? " ·not run" : "");
            g.appendChild(o);
        }
        cs.appendChild(g);
    };
    mk("Load cases", "case");
    mk("Load combinations", "combo");
    result = meta.result_sets.find(r => r.kind === "case" && r.finished)?.name ?? meta.result_sets[0]?.name ?? "";
    cs.value = result;
}
// ---------- steps (multi-step cases / envelope combos) ----------
async function loadSteps(res) {
    if (!stepsCache.has(res)) {
        try {
            const r = await api.steps(sid, res);
            stepsCache.set(res, r.steps.filter(s => s !== ""));
        }
        catch {
            stepsCache.set(res, []);
        }
    }
    stepList = stepsCache.get(res);
    buildStepSel();
}
function buildStepSel() {
    const sel = $("stepSel");
    sel.innerHTML = "";
    const opt = (v, t) => { const o = document.createElement("option"); o.value = v; o.textContent = t; sel.appendChild(o); };
    opt("", "Envelope (all)");
    for (const s of stepList)
        opt(s, s);
    sel.value = curStep ?? "";
    $("stepGrp").classList.toggle("hide", !(layer !== "geom" && stepList.length > 1));
}
function cycleStep(dir) {
    const opts = [null, ...stepList];
    let i = opts.indexOf(curStep);
    if (i < 0)
        i = 0;
    curStep = opts[(i + dir + opts.length) % opts.length];
    $("stepSel").value = curStep ?? "";
    refresh();
}
// ---------- refresh current view ----------
async function refresh() {
    if (!sid || !meta)
        return;
    busy(true);
    try {
        R.layer = layer;
        R.beams = geom.frames.filter(f => f.type === "beam" && f.story === level);
        markLevel();
        if (layer === "geom") {
            R.columns = (colsByStory.get(level) ?? []).map(frameToPlan);
            R.supports = [];
        }
        else {
            await ensureExtracted(result);
            await loadSteps(result);
            const stepArg = curStep ?? undefined;
            if (layer === "axial") {
                const r = await api.plan(sid, level, result, stepArg);
                R.columns = r.columns;
                R.supports = [];
            }
            else {
                const r = await api.reactions(sid, result, stepArg);
                R.supports = r.supports;
                R.columns = [];
            }
        }
        const stepSfx = curStep && layer !== "geom" ? ` · ${curStep}` : "";
        R.title = (layer === "react" ? `Base Reactions — ${result}` : layer === "axial" ? `Column Axial (base) — ${level} — ${result}` : `Column Plan — ${level}`) + stepSfx;
        R.draw();
        updateSummary();
        updateLegend();
    }
    finally {
        busy(false);
    }
}
function frameToPlan(f) {
    return { name: f.name, label: f.label, section: f.section, ix: f.ix, iy: f.iy, iz: f.iz, jx: f.jx, jy: f.jy, jz: f.jz, pmin: null, pmax: null, v2: null, v3: null, m2: null, m3: null };
}
async function ensureExtracted(name) {
    const rs = meta.result_sets.find(r => r.name === name);
    if (rs && !rs.extracted) {
        status(`Extracting ${name} from ETABS…`);
        toast(`Extracting ${name}…`);
        await api.extract(sid, [name]);
        meta = await api.meta(sid); // refresh extracted flags
        status(`Extracted ${name}.`);
    }
}
// ---------- side panels ----------
function updateSummary() {
    const el = $("summary"), st = meta.stories.find(s => s.name === level);
    if (layer === "react") {
        $("sumTitle").textContent = "Reactions summary";
        const fz = R.supports.map(s => s.fz);
        const sum = fz.reduce((a, b) => a + b, 0);
        el.innerHTML = `<dt>Result</dt><dd style="font-size:11px">${result}</dd><dt>Supports</dt><dd>${R.supports.length}</dd>
      <dt>Σ Fz</dt><dd>${sum.toFixed(0)} k</dd><dt>Max Fz</dt><dd>${Math.max(0, ...fz).toFixed(0)} k</dd><dt>Min Fz</dt><dd>${Math.min(0, ...fz).toFixed(0)} k</dd>`;
        return;
    }
    $("sumTitle").textContent = "Level summary";
    let extra = "";
    if (layer === "axial") {
        const ps = R.columns.map(c => c.pmin).filter((v) => v != null);
        if (ps.length)
            extra = `<dt>Axial min</dt><dd>${Math.min(...ps).toFixed(0)} k</dd><dt>Axial max</dt><dd>${Math.max(...R.columns.map(c => c.pmax ?? 0)).toFixed(0)} k</dd><dt>With result</dt><dd>${ps.length}/${R.columns.length}</dd>`;
    }
    el.innerHTML = `<dt>Elevation</dt><dd>${st?.elev.toFixed(2)} ft</dd><dt>Columns</dt><dd>${R.columns.length}</dd>${extra}`;
}
function updateLegend() {
    const el = $("legend");
    if (layer === "axial") {
        const m = Math.max(1, ...R.columns.flatMap(c => [Math.abs(c.pmin ?? 0), Math.abs(c.pmax ?? 0)]));
        el.innerHTML = `<div class="note">Base axial, <b>${result}</b> (kip). Size ∝ |P|.</div><div class="grad"></div><div class="gradrow"><span>−${m.toFixed(0)} comp</span><span>0</span><span>+${m.toFixed(0)} tens</span></div>`;
    }
    else if (layer === "react") {
        el.innerHTML = `<div><span class="swatch" style="background:var(--up)"></span>Downward (Fz+)</div><div style="margin-top:5px"><span class="swatch" style="background:var(--tens)"></span>Uplift (Fz−)</div>`;
    }
    else {
        el.innerHTML = `<div><span class="swatch" style="background:var(--accent)"></span>Column</div><div style="margin-top:5px"><span class="swatch" style="background:var(--grid)"></span>Beam / grid</div>`;
    }
}
R.onPick = (h) => {
    const el = $("selBody");
    if (!h) {
        el.innerHTML = '<p class="empty">Hover or click an element.</p>';
        return;
    }
    if (h.kind === "support") {
        const s = h.data;
        const env = curStep == null && s.fzmax != null && Math.abs((s.fzmax ?? 0) - (s.fzmin ?? 0)) > 0.05;
        el.innerHTML = `<dl class="kv"><dt>Support</dt><dd>${s.joint}</dd><dt>Plan X,Y</dt><dd>${s.x.toFixed(1)}, ${s.y.toFixed(1)}</dd>
      <dt>Result</dt><dd style="font-size:11px">${result}${curStep ? " · " + curStep : ""}</dd>
      <dt>${env ? "Fz gov" : "Fz"}</dt><dd>${s.fz.toFixed(1)} k</dd>
      ${env ? `<dt>Fz max</dt><dd style="color:var(--up)">${s.fzmax.toFixed(1)} k</dd><dt>Fz min</dt><dd style="color:var(--tens)">${s.fzmin.toFixed(1)} k</dd>` : ""}
      <dt>Fx</dt><dd>${s.fx.toFixed(1)} k</dd><dt>Fy</dt><dd>${s.fy.toFixed(1)} k</dd>
      <dt>Mx</dt><dd>${s.mx.toFixed(1)}</dd><dt>My</dt><dd>${s.my.toFixed(1)}</dd></dl>`;
    }
    else {
        const c = h.data;
        const P = c.pmin == null ? null : (Math.abs(c.pmin) >= Math.abs(c.pmax) ? c.pmin : c.pmax);
        const fr = P == null ? (layer === "geom" ? "" : `<dt>Axial</dt><dd style="color:var(--ink-faint)">no result</dd>`)
            : `<dt>Axial P</dt><dd>${P.toFixed(1)} k ${P < 0 ? "C" : "T"}</dd><dt>P range</dt><dd>${c.pmin.toFixed(0)} / ${c.pmax.toFixed(0)}</dd><dt>M2, M3</dt><dd>${(c.m2 ?? 0).toFixed(0)}, ${(c.m3 ?? 0).toFixed(0)}</dd>`;
        el.innerHTML = `<dl class="kv"><dt>Label</dt><dd>${c.label}</dd><dt>Section</dt><dd style="font-size:11px">${c.section || "—"}</dd>
      <dt>Plan X,Y</dt><dd>${c.ix.toFixed(1)}, ${c.iy.toFixed(1)}</dd>${fr}</dl>`;
    }
};
R.onCursor = (x, y) => { $("cursor").textContent = `x ${x.toFixed(1)}, y ${y.toFixed(1)}`; };
R.onNotify = (m) => toast(m);
// ---------- controls ----------
$("connectBtn").onclick = connect;
$("attachBtn").onclick = attach;
$("modelSearch").addEventListener("input", e => renderModels(e.target.value));
$("modelsHdr").onclick = () => {
    const c = $("modelsWrap").classList.toggle("hide");
    $("modelsCaret").textContent = c ? "▸" : "▾";
    $("modelsHdr").setAttribute("aria-expanded", String(!c));
};
$("zin").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1.2);
$("zout").onclick = () => R.zoomAt(R.W() / 2, R.H() / 2, 1 / 1.2);
$("zfit").onclick = () => R.fit();
$("layerSel").onchange = e => {
    layer = e.target.value;
    $("caseGrp").classList.toggle("hide", layer === "geom");
    $("valGrp").classList.toggle("hide", layer !== "axial");
    if (layer === "geom")
        $("stepGrp").classList.add("hide");
    $("hudTag").textContent = layer === "react" ? "Reactions" : "Plan @";
    refresh();
};
$("caseSel").onchange = e => { result = e.target.value; curStep = null; refresh(); };
$("stepPrev").onclick = () => cycleStep(-1);
$("stepNext").onclick = () => cycleStep(1);
$("stepSel").onchange = e => { curStep = e.target.value || null; refresh(); };
$("valSel").onchange = e => { R.vmode = e.target.value; R.draw(); updateSummary(); };
$("lyBeams").addEventListener("change", e => { R.showBeams = e.target.checked; R.draw(); });
$("lyGrids").addEventListener("change", e => { R.showGrids = e.target.checked; R.draw(); });
$("lyLabels").addEventListener("change", e => { R.showLabels = e.target.checked; R.draw(); });
$("pdfBtn").onclick = () => R.exportPDF(`CSEYE_${layer}_${level.replace(/\s+/g, "")}.pdf`);
$("themeBtn").onclick = () => {
    const cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", cur === "dark" ? "light" : "dark");
    R.draw();
    updateLegend();
};
R.resize();
connect();

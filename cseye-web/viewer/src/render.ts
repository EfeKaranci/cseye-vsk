import type { Extents, Frame, GridLine, PlanColumn, Support } from "./types";

export type Layer = "geom" | "axial" | "react";
export type ValMode = "gov" | "comp" | "tens";
export type MeasureMode = "dist" | "area" | "perim" | "angle" | null;
type P = { x: number; y: number };

const css = (v: string) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

const VIRIDIS: [number, number, number][] = [[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]];
function viridis(t: number): string {
  t = Math.max(0, Math.min(1, t));
  const seg = t * (VIRIDIS.length - 1), i = Math.min(Math.floor(seg), VIRIDIS.length - 2), f = seg - i;
  const a = VIRIDIS[i], b = VIRIDIS[i + 1];
  return `rgb(${Math.round(a[0] + (b[0] - a[0]) * f)},${Math.round(a[1] + (b[1] - a[1]) * f)},${Math.round(a[2] + (b[2] - a[2]) * f)})`;
}

export interface Hit { kind: "column" | "support"; data: PlanColumn | Support; }

/** A PDF/image underlay placed in world space (px→world: uniform scale s, rotation rot,
 *  translation of the image's bottom-left corner to (tx,ty)). */
export interface Underlay {
  name: string; img: CanvasImageSource; w: number; h: number;
  tx: number; ty: number; s: number; rot: number; opacity: number; visible: boolean;
}

/** Canvas plan renderer. World=model coords (ft), Y up. Feeds off bridge slices. */
export class PlanRenderer {
  cv: HTMLCanvasElement; ctx: CanvasRenderingContext2D;
  dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
  scale = 1; ox = 0; oy = 0;
  extents: Extents = { xmin: 0, xmax: 1, ymin: 0, ymax: 1 };
  beams: Frame[] = []; grids: GridLine[] = [];
  columns: PlanColumn[] = []; supports: Support[] = [];
  layer: Layer = "geom"; vmode: ValMode = "gov";
  showLabels = true; showBeams = true; showGrids = true;
  hiddenGridSystems = new Set<string>();
  markerScale = 1; labelScale = 1; fillAlpha = 0.9;
  colorScheme: "sign" | "mag" | "magv" = "sign";
  zoomWindowMode = false;
  private zw: { x0: number; y0: number; x1: number; y1: number } | null = null;
  onZoomWindow?: (on: boolean) => void;
  hover: Hit["data"] | null = null; pick: Hit["data"] | null = null;
  measureMode: MeasureMode = null;
  private mPts: P[] = [];
  private mCursor: P | null = null;
  private mDone = false;
  onPick?: (h: Hit | null) => void;
  onCursor?: (x: number, y: number) => void;
  onNotify?: (m: string) => void;
  onMeasure?: (text: string | null) => void;
  underlays: Underlay[] = [];
  active: Underlay | null = null;
  underlayMode: "off" | "move" | "align" = "off";
  private uDrag: { x: number; y: number; tx: number; ty: number } | null = null;
  private cDrag: { opp: P; oppLocal: P; dloc: P } | null = null;
  private alignStage = 0; private alignPdf: P[] = []; private alignWorld: P[] = [];
  onUnderlay?: (msg: string) => void;
  title = "";

  constructor(cv: HTMLCanvasElement) {
    this.cv = cv; this.ctx = cv.getContext("2d")!;
    this.bindEvents();
  }

  // ---- transform ----
  W() { return this.cv.width / this.dpr; }
  H() { return this.cv.height / this.dpr; }
  wx(x: number) { return this.ox + x * this.scale; }
  wy(y: number) { return this.H() - (this.oy + y * this.scale); }
  inv(px: number, py: number) { return { x: (px - this.ox) / this.scale, y: (this.H() - py - this.oy) / this.scale }; }

  resize() {
    const r = this.cv.parentElement!.getBoundingClientRect();
    this.cv.width = Math.round(r.width * this.dpr);
    this.cv.height = Math.round(r.height * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.draw();
  }
  fit() {
    const e = this.extents, pad = 44;
    const bw = (e.xmax - e.xmin) || 1, bh = (e.ymax - e.ymin) || 1;
    const s = Math.min((this.W() - 2 * pad) / bw, (this.H() - 2 * pad) / bh);
    this.scale = s;
    this.ox = pad - e.xmin * s + (this.W() - 2 * pad - bw * s) / 2;
    this.oy = pad - e.ymin * s + (this.H() - 2 * pad - bh * s) / 2;
    this.draw();
  }
  setZoomWindow(on: boolean) { this.zoomWindowMode = on; this.zw = null; this.cv.style.cursor = on ? "crosshair" : "default"; this.onZoomWindow?.(on); this.draw(); }
  private zoomToScreenRect(x0: number, y0: number, x1: number, y1: number) {
    const a = this.inv(x0, y0), b = this.inv(x1, y1);
    const wx0 = Math.min(a.x, b.x), wx1 = Math.max(a.x, b.x), wy0 = Math.min(a.y, b.y), wy1 = Math.max(a.y, b.y);
    const bw = (wx1 - wx0) || 1, bh = (wy1 - wy0) || 1, pad = 18;
    const s = Math.min((this.W() - 2 * pad) / bw, (this.H() - 2 * pad) / bh);
    this.scale = s;
    this.ox = pad - wx0 * s + (this.W() - 2 * pad - bw * s) / 2;
    this.oy = pad - wy0 * s + (this.H() - 2 * pad - bh * s) / 2;
    this.draw();
  }
  private drawZoomRect() {
    const z = this.zw!, ctx = this.ctx;
    ctx.save(); ctx.fillStyle = css("--accent"); ctx.globalAlpha = 0.15; ctx.fillRect(z.x0, z.y0, z.x1 - z.x0, z.y1 - z.y0);
    ctx.globalAlpha = 1; ctx.strokeStyle = css("--accent"); ctx.lineWidth = 1.5; ctx.setLineDash([5, 3]);
    ctx.strokeRect(z.x0, z.y0, z.x1 - z.x0, z.y1 - z.y0); ctx.setLineDash([]); ctx.restore();
  }
  zoomAt(px: number, py: number, f: number) {
    const w = this.inv(px, py); this.scale *= f;
    this.ox = px - w.x * this.scale; this.oy = (this.H() - py) - w.y * this.scale; this.draw();
  }

  // ---- color scales (per current slice) ----
  private maxP = 1; private maxFz = 1;
  private computeScales() {
    this.maxP = Math.max(1, ...this.columns.flatMap(c =>
      [Math.abs(c.pmin ?? 0), Math.abs(c.pmax ?? 0)]));
    this.maxFz = Math.max(1, ...this.supports.map(s => Math.abs(s.fz)));
  }
  private colP(c: PlanColumn): number | null {
    if (c.pmin == null || c.pmax == null) return null;
    if (this.vmode === "comp") return c.pmin;
    if (this.vmode === "tens") return c.pmax;
    return Math.abs(c.pmin) >= Math.abs(c.pmax) ? c.pmin : c.pmax;
  }
  ramp(v: number, max: number) {
    const t = Math.min(1, Math.abs(v) / max);
    if (this.colorScheme === "sign") return v < 0 ? `hsl(214,80%,${72 - 40 * t}%)` : `hsl(4,74%,${70 - 34 * t}%)`;
    if (this.colorScheme === "mag") return `hsl(${210 - 210 * t},74%,${62 - 16 * t}%)`;
    return viridis(t);
  }
  private rad(v: number, max: number, lo: number, hi: number) { return (lo + (hi - lo) * Math.min(1, Math.abs(v) / max)) * this.markerScale; }

  // ---- draw ----
  draw() {
    const { ctx } = this; if (!ctx) return;
    this.computeScales();
    ctx.clearRect(0, 0, this.W(), this.H());
    if (this.underlays.length) this.drawUnderlays();
    if (this.showGrids) this.drawGrids();
    if (this.showBeams) this.drawBeams();
    if (this.layer === "react") this.drawReactions();
    else this.drawColumns();
    if (this.measureMode) this.drawMeasure();
    if (this.zw) this.drawZoomRect();
    this.drawScaleBar();
  }

  // ---- measure tools: distance / area / perimeter / angle ----
  setMeasure(mode: MeasureMode) {
    this.measureMode = (this.measureMode === mode) ? null : mode;   // click active icon to toggle off
    this.mPts = []; this.mCursor = null; this.mDone = false;
    this.cv.style.cursor = this.measureMode ? "crosshair" : "default";
    this.onMeasure?.(this.measureReadout());
    this.draw();
  }
  private snapPoint(px: number, py: number): P {
    const cand: P[] = this.layer === "react" ? this.supports.map(s => ({ x: s.x, y: s.y })) : this.columns.map(c => ({ x: c.ix, y: c.iy }));
    let best: P | null = null, bd = 13 * 13;
    for (const c of cand) { const dx = this.wx(c.x) - px, dy = this.wy(c.y) - py, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = c; } }
    return best ?? this.inv(px, py);
  }
  private placePoint(px: number, py: number) {
    if (this.mDone) { this.mPts = []; this.mDone = false; }
    this.mPts.push(this.snapPoint(px, py));
    if (this.measureMode === "dist" && this.mPts.length >= 2) this.mDone = true;
    if (this.measureMode === "angle" && this.mPts.length >= 3) this.mDone = true;
    this.onMeasure?.(this.measureReadout()); this.draw();
  }
  private finishPoly() {   // double-click ends area / perimeter (pops the dbl-click duplicate)
    if (this.measureMode !== "area" && this.measureMode !== "perim") return;
    const need = this.measureMode === "area" ? 3 : 2;
    if (this.mPts.length > need) this.mPts.pop();
    if (this.mPts.length >= need) { this.mDone = true; this.onMeasure?.(this.measureReadout()); this.draw(); }
  }
  private dist(a: P, b: P) { return Math.hypot(b.x - a.x, b.y - a.y); }
  private polylen(p: P[]) { let s = 0; for (let i = 1; i < p.length; i++) s += this.dist(p[i - 1], p[i]); return s; }
  private polyarea(p: P[]) { let s = 0; for (let i = 0; i < p.length; i++) { const q = p[(i + 1) % p.length]; s += p[i].x * q.y - q.x * p[i].y; } return Math.abs(s) / 2; }
  private angleAt(a: P, b: P, c: P) { let d = Math.abs(Math.atan2(a.y - b.y, a.x - b.x) - Math.atan2(c.y - b.y, c.x - b.x)) * 180 / Math.PI; return d > 180 ? 360 - d : d; }
  private effPts(): P[] {
    if (this.mDone || !this.mCursor || !this.measureMode) return this.mPts;
    if (this.measureMode === "dist") return this.mPts.length ? [this.mPts[0], this.mCursor] : [this.mCursor];
    if (this.measureMode === "angle") return [...this.mPts, this.mCursor].slice(0, 3);
    return [...this.mPts, this.mCursor];
  }
  private measureReadout(): string | null {
    const m = this.measureMode; if (!m) return null;
    const p = this.effPts();
    if (m === "dist") { if (p.length < 2) return "Distance: click first point…"; const dx = p[1].x - p[0].x, dy = p[1].y - p[0].y; return `Distance ${Math.hypot(dx, dy).toFixed(2)} ft   (Δx ${dx.toFixed(2)}, Δy ${dy.toFixed(2)})`; }
    if (m === "angle") { if (p.length < 3) return `Angle: pick ${3 - p.length} more point(s) — vertex is the 2nd`; return `Angle ${this.angleAt(p[0], p[1], p[2]).toFixed(1)}°`; }
    if (m === "perim") { if (p.length < 2) return "Perimeter: click points, double-click to finish"; return `Perimeter ${this.polylen(p).toFixed(2)} ft   (${p.length} pts)`; }
    if (p.length < 3) return "Area: click ≥3 points, double-click to finish";
    return `Area ${this.polyarea(p).toFixed(1)} ft²   ·   Perimeter ${(this.polylen(p) + this.dist(p[p.length - 1], p[0])).toFixed(1)} ft`;
  }
  private drawMeasure() {
    const m = this.measureMode; if (!m) return;
    const p = this.effPts(); if (!p.length) return;
    const { ctx } = this; const S = (pt: P) => ({ x: this.wx(pt.x), y: this.wy(pt.y) });
    ctx.save();
    if (m === "area" && p.length >= 3) { ctx.beginPath(); p.forEach((pt, i) => { const s = S(pt); i ? ctx.lineTo(s.x, s.y) : ctx.moveTo(s.x, s.y); }); ctx.closePath(); ctx.fillStyle = css("--amber"); ctx.globalAlpha = .14; ctx.fill(); ctx.globalAlpha = 1; }
    ctx.strokeStyle = css("--amber"); ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
    ctx.beginPath(); p.forEach((pt, i) => { const s = S(pt); i ? ctx.lineTo(s.x, s.y) : ctx.moveTo(s.x, s.y); });
    if (m === "area" && p.length >= 3) ctx.closePath();
    ctx.stroke(); ctx.setLineDash([]);
    for (const pt of p) { const s = S(pt); ctx.beginPath(); ctx.fillStyle = css("--amber"); ctx.arc(s.x, s.y, 3.5, 0, 7); ctx.fill(); ctx.lineWidth = 1.2; ctx.strokeStyle = css("--ink"); ctx.stroke(); }
    const short =
      m === "dist" && p.length >= 2 ? `${this.dist(p[0], p[1]).toFixed(2)} ft` :
      m === "angle" && p.length >= 3 ? `${this.angleAt(p[0], p[1], p[2]).toFixed(1)}°` :
      m === "perim" && p.length >= 2 ? `${this.polylen(p).toFixed(1)} ft` :
      m === "area" && p.length >= 3 ? `${this.polyarea(p).toFixed(0)} ft²` : "";
    if (short) {
      let cx = 0, cy = 0; for (const pt of p) { const s = S(pt); cx += s.x; cy += s.y; } cx /= p.length; cy /= p.length;
      ctx.font = "700 12px " + css("--font-mono"); const w = ctx.measureText(short).width + 12;
      ctx.fillStyle = css("--panel"); ctx.strokeStyle = css("--amber"); ctx.lineWidth = 1;
      ctx.beginPath(); (ctx as any).roundRect(cx - w / 2, cy - 10, w, 19, 5); ctx.fill(); ctx.stroke();
      ctx.fillStyle = css("--ink"); ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(short, cx, cy);
    }
    ctx.restore();
  }
  private drawBeams() {
    const { ctx } = this; ctx.save(); ctx.strokeStyle = css("--grid"); ctx.lineWidth = 1; ctx.globalAlpha = .8; ctx.beginPath();
    for (const f of this.beams) { ctx.moveTo(this.wx(f.ix), this.wy(f.iy)); ctx.lineTo(this.wx(f.jx), this.wy(f.jy)); }
    ctx.stroke(); ctx.restore();
  }
  private drawGrids() {
    // Grid lines span the whole viewport (stay visible at any zoom/pan) and the
    // labelled bubbles are pinned to the top/left edge so they never scroll away.
    const { ctx } = this, W = this.W(), H = this.H();
    ctx.save(); ctx.lineWidth = 1; ctx.font = "600 11px " + css("--font-mono");
    for (const g of this.grids) {
      if (!g.visible) continue;
      if (g.sys && this.hiddenGridSystems.has(g.sys)) continue;
      let bx: number, by: number;
      ctx.setLineDash([7, 5]); ctx.strokeStyle = css("--grid"); ctx.globalAlpha = .8; ctx.beginPath();
      if (g.dir === "X") {                 // constant X → vertical line across the view
        const sx = this.wx(g.x1); if (sx < -1 || sx > W + 1) continue;
        ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke(); bx = sx; by = 13;
      } else if (g.dir === "Y") {          // constant Y → horizontal line across the view
        const sy = this.wy(g.y1); if (sy < -1 || sy > H + 1) continue;
        ctx.moveTo(0, sy); ctx.lineTo(W, sy); ctx.stroke(); bx = 13; by = sy;
      } else {                             // general segment
        ctx.moveTo(this.wx(g.x1), this.wy(g.y1)); ctx.lineTo(this.wx(g.x2), this.wy(g.y2)); ctx.stroke();
        bx = this.wx(g.x1); by = this.wy(g.y1);
      }
      ctx.setLineDash([]); ctx.globalAlpha = 1;
      ctx.beginPath(); ctx.fillStyle = css("--canvas"); ctx.strokeStyle = css("--grid-strong"); ctx.arc(bx, by, 10, 0, 7); ctx.fill(); ctx.stroke();
      ctx.fillStyle = css("--ink-soft"); ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(g.id.slice(0, 4), bx, by);
    }
    ctx.restore();
  }
  private drawColumns() {
    const { ctx } = this, axial = this.layer === "axial";
    const drawn: { x: number; y: number; r: number; val: number | null; on: boolean; label: string }[] = [];
    for (const c of this.columns) {
      const x = this.wx(c.ix), y = this.wy(c.iy), on = c === this.pick || c === this.hover;
      let color: string, r: number, val: number | null = null;
      if (axial) { val = this.colP(c); if (val == null) { color = css("--ink-faint"); r = (on ? 5 : 3) * this.markerScale; } else { color = this.ramp(val, this.maxP); r = this.rad(val, this.maxP, 3.2, 9.5); } }
      else { color = css("--accent"); r = (on ? 6.5 : 4.6) * this.markerScale; }
      ctx.beginPath(); ctx.fillStyle = color; ctx.globalAlpha = on ? 1 : this.fillAlpha; ctx.arc(x, y, on ? r + 1.5 : r, 0, 7); ctx.fill();
      if (on) { ctx.globalAlpha = 1; ctx.lineWidth = 2; ctx.strokeStyle = css("--ink"); ctx.stroke(); }
      ctx.globalAlpha = 1;
      drawn.push({ x, y, r, val, on, label: axial ? (val == null ? "–" : String(Math.round(Math.abs(val)))) : c.label });
    }
    this.declutterLabels(drawn);
  }
  private drawReactions() {
    const { ctx } = this;
    const drawn: { x: number; y: number; r: number; val: number; on: boolean; label: string }[] = [];
    for (const s of this.supports) {
      const x = this.wx(s.x), y = this.wy(s.y), on = s === this.pick || s === this.hover;
      const r = this.rad(s.fz, this.maxFz, 3.5, 11);
      ctx.beginPath(); ctx.fillStyle = s.fz >= 0 ? css("--up") : css("--tens"); ctx.globalAlpha = on ? 1 : this.fillAlpha;
      ctx.arc(x, y, on ? r + 1.5 : r, 0, 7); ctx.fill();
      if (on) { ctx.lineWidth = 2; ctx.strokeStyle = css("--ink"); ctx.stroke(); } ctx.globalAlpha = 1;
      drawn.push({ x, y, r, val: s.fz, on, label: String(Math.round(Math.abs(s.fz))) });
    }
    this.declutterLabels(drawn);
  }
  private declutterLabels(items: { x: number; y: number; r: number; val: number | null; on: boolean; label: string }[]) {
    if (!this.showLabels) return;
    const { ctx } = this; ctx.font = `600 ${(10 * this.labelScale).toFixed(1)}px ` + css("--font-mono"); ctx.textAlign = "center"; ctx.textBaseline = "bottom";
    const order = items.slice().sort((a, b) => (+b.on - +a.on) || (Math.abs(b.val ?? 0) - Math.abs(a.val ?? 0)));
    const placed: [number, number][] = []; const GX = 30 * this.labelScale, GY = 13 * this.labelScale;
    for (const d of order) {
      if (d.x < -30 || d.x > this.W() + 30 || d.y < -20 || d.y > this.H() + 20) continue;
      let ok = d.on;
      if (!ok) { ok = true; for (const p of placed) if (Math.abs(p[0] - d.x) < GX && Math.abs(p[1] - d.y) < GY) { ok = false; break; } }
      if (!ok) continue; placed.push([d.x, d.y]);
      ctx.fillStyle = d.on ? css("--ink") : css("--ink-soft"); ctx.fillText(d.label, d.x, d.y - d.r - 2);
    }
  }
  private drawScaleBar() {
    const target = 90 / this.scale, pow = Math.pow(10, Math.floor(Math.log10(target)));
    let L = pow; for (const m of [1, 2, 5, 10]) if (m * pow <= target) L = m * pow;
    const el = document.getElementById("sbBar"), t = document.getElementById("sbTxt");
    if (el) el.style.width = (L * this.scale) + "px"; if (t) t.textContent = L + " ft";
  }

  // ---- picking ----
  private nearest(px: number, py: number): Hit["data"] | null {
    if (this.layer === "react") {
      let best: Support | null = null, bd = 16 * 16;
      for (const s of this.supports) { const dx = this.wx(s.x) - px, dy = this.wy(s.y) - py, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = s; } }
      return best;
    }
    let best: PlanColumn | null = null, bd = 14 * 14;
    for (const c of this.columns) { const dx = this.wx(c.ix) - px, dy = this.wy(c.iy) - py, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = c; } }
    return best;
  }

  // ---- events ----
  private drag: { x: number; y: number; ox: number; oy: number; moved: boolean } | null = null;
  private bindEvents() {
    const cv = this.cv;
    cv.addEventListener("pointerdown", e => {
      if (this.zoomWindowMode) { this.zw = { x0: e.offsetX, y0: e.offsetY, x1: e.offsetX, y1: e.offsetY }; cv.setPointerCapture(e.pointerId); return; }
      if (this.underlayMode === "move" && this.active && this.underlays.includes(this.active)) {
        const u = this.active, i = this.hitCorner(e.offsetX, e.offsetY, u);
        if (i >= 0) {
          const px = [[0, 0], [u.w, 0], [u.w, u.h], [0, u.h]] as [number, number][];
          const dP = px[i], oP = px[(i + 2) % 4], oLoc = { x: oP[0], y: u.h - oP[1] };
          this.cDrag = { opp: this.worldOf(u, oP[0], oP[1]), oppLocal: oLoc, dloc: { x: dP[0] - oLoc.x, y: (u.h - dP[1]) - oLoc.y } };
          cv.setPointerCapture(e.pointerId); return;
        }
        this.uDrag = { x: e.offsetX, y: e.offsetY, tx: u.tx, ty: u.ty }; cv.setPointerCapture(e.pointerId); return;
      }
      this.drag = { x: e.offsetX, y: e.offsetY, ox: this.ox, oy: this.oy, moved: false }; cv.setPointerCapture(e.pointerId);
    });
    cv.addEventListener("pointermove", e => {
      const w = this.inv(e.offsetX, e.offsetY); this.onCursor?.(w.x, w.y);
      if (this.zw) { this.zw.x1 = e.offsetX; this.zw.y1 = e.offsetY; this.draw(); return; }
      if (this.cDrag && this.active) { this.cornerScale(e.offsetX, e.offsetY); return; }
      if (this.uDrag && this.active) { const S = this.scale; this.active.tx = this.uDrag.tx + (e.offsetX - this.uDrag.x) / S; this.active.ty = this.uDrag.ty - (e.offsetY - this.uDrag.y) / S; this.draw(); return; }
      if (this.drag) { this.ox = this.drag.ox + (e.offsetX - this.drag.x); this.oy = this.drag.oy - (e.offsetY - this.drag.y); this.drag.moved = true; this.draw(); return; }
      if (this.measureMode) { if (!this.mDone) { this.mCursor = this.snapPoint(e.offsetX, e.offsetY); this.onMeasure?.(this.measureReadout()); this.draw(); } return; }
      const h = this.nearest(e.offsetX, e.offsetY);
      if (h !== this.hover) { this.hover = h; cv.style.cursor = h ? "pointer" : "default"; if (!this.pick) this.emit(h); this.draw(); }
    });
    cv.addEventListener("pointerup", e => {
      if (this.zw) { const z = this.zw; this.zw = null; if (Math.abs(z.x1 - z.x0) > 6 && Math.abs(z.y1 - z.y0) > 6) this.zoomToScreenRect(z.x0, z.y0, z.x1, z.y1); this.setZoomWindow(false); return; }
      if (this.cDrag) { this.cDrag = null; return; }
      if (this.uDrag) { this.uDrag = null; return; }
      if (this.drag && !this.drag.moved) {
        if (this.underlayMode === "align" && this.active) this.alignClick(e.offsetX, e.offsetY);
        else if (this.measureMode) this.placePoint(e.offsetX, e.offsetY);
        else { const h = this.nearest(e.offsetX, e.offsetY); this.pick = h; this.emit(h); this.draw(); }
      }
      this.drag = null;
    });
    cv.addEventListener("dblclick", () => this.finishPoly());
    cv.addEventListener("wheel", e => { e.preventDefault(); this.zoomAt(e.offsetX, e.offsetY, e.deltaY < 0 ? 1.12 : 1 / 1.12); }, { passive: false });
    window.addEventListener("resize", () => this.resize());
    window.addEventListener("keydown", e => {
      const tag = (document.activeElement as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
      if (e.key === "z" || e.key === "Z") this.setZoomWindow(!this.zoomWindowMode);
      else if (e.key === "Escape" && this.zoomWindowMode) this.setZoomWindow(false);
    });
  }
  private emit(d: Hit["data"] | null) {
    if (!d) { this.onPick?.(null); return; }
    this.onPick?.({ kind: this.layer === "react" ? "support" : "column", data: d });
  }

  // ---- PDF / image underlays (named, multiple, per-level; app manages the list) ----
  makeUnderlay(name: string, img: CanvasImageSource, w: number, h: number): Underlay {
    const e = this.extents, s = ((e.xmax - e.xmin) / w) || 1;   // default: fit width to model extents
    return { name, img, w, h, tx: e.xmin, ty: e.ymin, s, rot: 0, opacity: 0.55, visible: true };
  }
  setUnderlayOpacity(o: number) { if (this.active) { this.active.opacity = o; this.draw(); } }
  rotateUnderlay(deg: number) { if (this.active) { this.active.rot = deg * Math.PI / 180; this.draw(); } }
  scaleUnderlayBy(f: number) { if (this.active) { this.active.s *= f; this.draw(); } }
  setUnderlayMode(mode: "off" | "move" | "align") {
    this.underlayMode = mode; this.alignStage = 0; this.alignPdf = []; this.alignWorld = [];
    this.cv.style.cursor = mode === "align" ? "crosshair" : mode === "move" ? "move" : "default";
    if (mode === "align" && this.active) this.onUnderlay?.("Align: click the FIRST reference point on the PDF.");
    this.draw();
  }
  private uMatrix(u: Underlay) {
    const S = this.scale, H = this.H(), c = Math.cos(u.rot), sn = Math.sin(u.rot);
    const ex = u.tx - u.s * sn * u.h, ey = u.ty + u.s * c * u.h;
    return { A: S * u.s * c, C: S * u.s * sn, E: this.ox + S * ex, B: -S * u.s * sn, D: S * u.s * c, F: H - this.oy - S * ey };
  }
  private worldOf(u: Underlay, px: number, py: number): P {
    const c = Math.cos(u.rot), sn = Math.sin(u.rot), ly = u.h - py;
    return { x: u.tx + u.s * (c * px - sn * ly), y: u.ty + u.s * (sn * px + c * ly) };
  }
  private cornersScreen(u: Underlay) {
    return ([[0, 0], [u.w, 0], [u.w, u.h], [0, u.h]] as [number, number][]).map(([px, py]) => {
      const w = this.worldOf(u, px, py); return { x: this.wx(w.x), y: this.wy(w.y) };
    });
  }
  private drawUnderlays() {
    const d = this.dpr, ctx = this.ctx;
    for (const u of this.underlays) {
      if (!u.visible) continue;
      const m = this.uMatrix(u);
      ctx.save(); ctx.globalAlpha = u.opacity;
      ctx.setTransform(d * m.A, d * m.B, d * m.C, d * m.D, d * m.E, d * m.F);
      ctx.drawImage(u.img, 0, 0); ctx.restore();
    }
    if (this.active && this.underlayMode !== "off" && this.underlays.includes(this.active)) {
      const cs = this.cornersScreen(this.active);
      ctx.save(); ctx.strokeStyle = css("--accent"); ctx.lineWidth = 1.5; ctx.setLineDash([5, 4]);
      ctx.beginPath(); cs.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)); ctx.closePath(); ctx.stroke(); ctx.setLineDash([]);
      for (const p of cs) { ctx.beginPath(); ctx.fillStyle = css("--panel"); ctx.strokeStyle = css("--accent"); ctx.lineWidth = 1.5; ctx.rect(p.x - 5, p.y - 5, 10, 10); ctx.fill(); ctx.stroke(); }
      ctx.restore();
    }
  }
  private hitCorner(sx: number, sy: number, u: Underlay): number {
    const cs = this.cornersScreen(u);
    for (let i = 0; i < 4; i++) if (Math.abs(cs[i].x - sx) < 9 && Math.abs(cs[i].y - sy) < 9) return i;
    return -1;
  }
  private screenToPdf(u: Underlay, sx: number, sy: number): P {
    const m = this.uMatrix(u), det = m.A * m.D - m.C * m.B, X = sx - m.E, Y = sy - m.F;
    return { x: (m.D * X - m.C * Y) / det, y: (-m.B * X + m.A * Y) / det };
  }
  private cornerScale(sx: number, sy: number) {
    const u = this.active!, cd = this.cDrag!, C = this.inv(sx, sy), c = Math.cos(u.rot), sn = Math.sin(u.rot);
    const Rdl = { x: c * cd.dloc.x - sn * cd.dloc.y, y: sn * cd.dloc.x + c * cd.dloc.y };
    const denom = Rdl.x * Rdl.x + Rdl.y * Rdl.y || 1;
    u.s = Math.max(1e-6, ((C.x - cd.opp.x) * Rdl.x + (C.y - cd.opp.y) * Rdl.y) / denom);
    const Ro = { x: c * cd.oppLocal.x - sn * cd.oppLocal.y, y: sn * cd.oppLocal.x + c * cd.oppLocal.y };
    u.tx = cd.opp.x - u.s * Ro.x; u.ty = cd.opp.y - u.s * Ro.y;
    this.draw();
  }
  private alignClick(sx: number, sy: number) {
    const u = this.active; if (!u) return;
    if (this.alignStage % 2 === 0) { this.alignPdf.push(this.screenToPdf(u, sx, sy)); this.onUnderlay?.(`Align: click the MODEL location for reference point ${this.alignPdf.length} (snaps to columns/grids).`); }
    else { this.alignWorld.push(this.snapPoint(sx, sy)); this.onUnderlay?.(this.alignWorld.length < 2 ? "Align: click the SECOND reference point on the PDF." : ""); }
    this.alignStage++;
    if (this.alignWorld.length === 2) {
      const l = (p: P): P => ({ x: p.x, y: u.h - p.y });
      const l1 = l(this.alignPdf[0]), l2 = l(this.alignPdf[1]);
      const dd = { x: l2.x - l1.x, y: l2.y - l1.y }, D = { x: this.alignWorld[1].x - this.alignWorld[0].x, y: this.alignWorld[1].y - this.alignWorld[0].y };
      const s = Math.hypot(D.x, D.y) / (Math.hypot(dd.x, dd.y) || 1), rot = Math.atan2(D.y, D.x) - Math.atan2(dd.y, dd.x);
      const c = Math.cos(rot), sn = Math.sin(rot);
      u.s = s; u.rot = rot; u.tx = this.alignWorld[0].x - s * (c * l1.x - sn * l1.y); u.ty = this.alignWorld[0].y - s * (sn * l1.x + c * l1.y);
      this.alignStage = 0; this.alignPdf = []; this.alignWorld = []; this.underlayMode = "move"; this.cv.style.cursor = "move";
      this.onUnderlay?.("Aligned to 2 points — fine-tune with drag / corner handles.");
    }
    this.draw();
  }

  // ---- PDF export (self-contained; sandbox-safe) ----
  exportPDF(fname: string) {
    const root = document.documentElement, prev = root.getAttribute("data-theme");
    root.setAttribute("data-theme", "light"); this.draw();
    const headH = 72, Wc = this.W(), Hc = this.H();
    const oc = document.createElement("canvas"); oc.width = this.cv.width; oc.height = this.cv.height + Math.round(headH * this.dpr);
    const o = oc.getContext("2d")!; o.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    o.fillStyle = "#fff"; o.fillRect(0, 0, Wc, Hc + headH); o.fillStyle = "#0e7c86"; o.fillRect(0, 0, Wc, 3);
    o.fillStyle = "#111827"; o.font = '700 22px system-ui,sans-serif'; o.fillText(this.title, 18, 36);
    o.drawImage(this.cv, 0, headH, Wc, Hc);
    if (prev) root.setAttribute("data-theme", prev); else root.removeAttribute("data-theme"); this.draw();
    const b64 = oc.toDataURL("image/jpeg", 0.92).split(",")[1], bin = atob(b64);
    const jpg = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) jpg[i] = bin.charCodeAt(i);
    const pdf = buildPDF(jpg, oc.width, oc.height);
    const url = URL.createObjectURL(new Blob([pdf.buffer as ArrayBuffer], { type: "application/pdf" }));
    // Primary: real download (works on a normal top-level page).
    try { const a = document.createElement("a"); a.href = url; a.download = fname; a.rel = "noopener"; document.body.appendChild(a); a.click(); a.remove(); } catch { /* ignore */ }
    // Embedded (sandboxed iframe): downloads are blocked — open the PDF in a new tab so it's reachable.
    const embedded = window.self !== window.top;
    let opened = false;
    if (embedded) { try { opened = !!window.open(url, "_blank"); } catch { /* popup blocked */ } }
    setTimeout(() => URL.revokeObjectURL(url), 20000);
    this.onNotify?.(embedded
      ? (opened ? "PDF opened in a new tab — press Ctrl+S to save it." : "Pop-up blocked — allow pop-ups to get the PDF, or open the app in its own tab.")
      : `Saved “${fname}” — check your Downloads folder.`);
  }
}

function buildPDF(jpg: Uint8Array, iw: number, ih: number): Uint8Array {
  const PW = 792, PH = Math.round(PW * ih / iw);
  const enc = (s: string) => { const a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i) & 255; return a; };
  const parts: Uint8Array[] = []; let off = 0; const xr: number[] = [];
  const put = (u: Uint8Array) => { parts.push(u); off += u.length; }; const puts = (s: string) => put(enc(s));
  puts("%PDF-1.3\n");
  const obj = (n: number, b: string) => { xr[n] = off; puts(`${n} 0 obj\n` + b + "\nendobj\n"); };
  obj(1, "<</Type/Catalog/Pages 2 0 R>>");
  obj(2, "<</Type/Pages/Kids[3 0 R]/Count 1>>");
  obj(3, `<</Type/Page/Parent 2 0 R/MediaBox[0 0 ${PW} ${PH}]/Resources<</XObject<</Im0 4 0 R>>>>/Contents 5 0 R>>`);
  xr[4] = off; puts(`4 0 obj\n<</Type/XObject/Subtype/Image/Width ${iw}/Height ${ih}/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/DCTDecode/Length ${jpg.length}>>\nstream\n`);
  put(jpg); puts("\nendstream\nendobj\n");
  const content = `q ${PW} 0 0 ${PH} 0 0 cm /Im0 Do Q`;
  xr[5] = off; puts(`5 0 obj\n<</Length ${content.length}>>\nstream\n` + content + "\nendstream\nendobj\n");
  const xs = off; let x = "xref\n0 6\n0000000000 65535 f \n";
  for (let i = 1; i <= 5; i++) x += String(xr[i]).padStart(10, "0") + " 00000 n \n";
  puts(x); puts(`trailer\n<</Size 6/Root 1 0 R>>\nstartxref\n${xs}\n%%EOF`);
  const tot = parts.reduce((n, p) => n + p.length, 0), out = new Uint8Array(tot); let p = 0;
  for (const u of parts) { out.set(u, p); p += u.length; } return out;
}

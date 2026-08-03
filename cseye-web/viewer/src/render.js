const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
/** Canvas plan renderer. World=model coords (ft), Y up. Feeds off bridge slices. */
export class PlanRenderer {
    constructor(cv) {
        this.dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
        this.scale = 1;
        this.ox = 0;
        this.oy = 0;
        this.extents = { xmin: 0, xmax: 1, ymin: 0, ymax: 1 };
        this.beams = [];
        this.grids = [];
        this.columns = [];
        this.supports = [];
        this.layer = "geom";
        this.vmode = "gov";
        this.showLabels = true;
        this.showBeams = true;
        this.showGrids = true;
        this.hover = null;
        this.pick = null;
        this.title = "";
        // ---- color scales (per current slice) ----
        this.maxP = 1;
        this.maxFz = 1;
        // ---- events ----
        this.drag = null;
        this.cv = cv;
        this.ctx = cv.getContext("2d");
        this.bindEvents();
    }
    // ---- transform ----
    W() { return this.cv.width / this.dpr; }
    H() { return this.cv.height / this.dpr; }
    wx(x) { return this.ox + x * this.scale; }
    wy(y) { return this.H() - (this.oy + y * this.scale); }
    inv(px, py) { return { x: (px - this.ox) / this.scale, y: (this.H() - py - this.oy) / this.scale }; }
    resize() {
        const r = this.cv.parentElement.getBoundingClientRect();
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
    zoomAt(px, py, f) {
        const w = this.inv(px, py);
        this.scale *= f;
        this.ox = px - w.x * this.scale;
        this.oy = (this.H() - py) - w.y * this.scale;
        this.draw();
    }
    computeScales() {
        this.maxP = Math.max(1, ...this.columns.flatMap(c => [Math.abs(c.pmin ?? 0), Math.abs(c.pmax ?? 0)]));
        this.maxFz = Math.max(1, ...this.supports.map(s => Math.abs(s.fz)));
    }
    colP(c) {
        if (c.pmin == null || c.pmax == null)
            return null;
        if (this.vmode === "comp")
            return c.pmin;
        if (this.vmode === "tens")
            return c.pmax;
        return Math.abs(c.pmin) >= Math.abs(c.pmax) ? c.pmin : c.pmax;
    }
    ramp(v, max) {
        const t = Math.min(1, Math.abs(v) / max);
        return v < 0 ? `hsl(214,80%,${72 - 40 * t}%)` : `hsl(4,74%,${70 - 34 * t}%)`;
    }
    rad(v, max, lo, hi) { return lo + (hi - lo) * Math.min(1, Math.abs(v) / max); }
    // ---- draw ----
    draw() {
        const { ctx } = this;
        if (!ctx)
            return;
        this.computeScales();
        ctx.clearRect(0, 0, this.W(), this.H());
        if (this.showGrids)
            this.drawGrids();
        if (this.showBeams)
            this.drawBeams();
        if (this.layer === "react")
            this.drawReactions();
        else
            this.drawColumns();
        this.drawScaleBar();
    }
    drawBeams() {
        const { ctx } = this;
        ctx.save();
        ctx.strokeStyle = css("--grid");
        ctx.lineWidth = 1;
        ctx.globalAlpha = .8;
        ctx.beginPath();
        for (const f of this.beams) {
            ctx.moveTo(this.wx(f.ix), this.wy(f.iy));
            ctx.lineTo(this.wx(f.jx), this.wy(f.jy));
        }
        ctx.stroke();
        ctx.restore();
    }
    drawGrids() {
        const { ctx } = this, e = this.extents;
        ctx.save();
        ctx.lineWidth = 1;
        ctx.setLineDash([7, 5]);
        ctx.strokeStyle = css("--grid");
        ctx.globalAlpha = .8;
        ctx.font = "600 11px " + css("--font-mono");
        for (const g of this.grids) {
            if (!g.visible)
                continue;
            ctx.beginPath();
            ctx.moveTo(this.wx(g.x1), this.wy(g.y1));
            ctx.lineTo(this.wx(g.x2), this.wy(g.y2));
            ctx.stroke();
        }
        ctx.setLineDash([]);
        for (const g of this.grids) {
            if (!g.visible)
                continue;
            const px = this.wx(g.dir === "X" ? g.x1 : e.xmax), py = this.wy(g.dir === "X" ? e.ymax : g.y1);
            const cx = g.dir === "X" ? px : px + 13, cy = g.dir === "X" ? py - 13 : py;
            ctx.beginPath();
            ctx.fillStyle = css("--canvas");
            ctx.strokeStyle = css("--grid-strong");
            ctx.arc(cx, cy, 10, 0, 7);
            ctx.fill();
            ctx.stroke();
            ctx.fillStyle = css("--ink-soft");
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(g.id.slice(0, 4), cx, cy);
        }
        ctx.restore();
    }
    drawColumns() {
        const { ctx } = this, axial = this.layer === "axial";
        const drawn = [];
        for (const c of this.columns) {
            const x = this.wx(c.ix), y = this.wy(c.iy), on = c === this.pick || c === this.hover;
            let color, r, val = null;
            if (axial) {
                val = this.colP(c);
                if (val == null) {
                    color = css("--ink-faint");
                    r = on ? 5 : 3;
                }
                else {
                    color = this.ramp(val, this.maxP);
                    r = this.rad(val, this.maxP, 3.2, 9.5);
                }
            }
            else {
                color = css("--accent");
                r = on ? 6.5 : 4.6;
            }
            ctx.beginPath();
            ctx.fillStyle = color;
            ctx.globalAlpha = on ? 1 : .92;
            ctx.arc(x, y, on ? r + 1.5 : r, 0, 7);
            ctx.fill();
            if (on) {
                ctx.globalAlpha = 1;
                ctx.lineWidth = 2;
                ctx.strokeStyle = css("--ink");
                ctx.stroke();
            }
            ctx.globalAlpha = 1;
            drawn.push({ x, y, r, val, on, label: axial ? (val == null ? "–" : String(Math.round(Math.abs(val)))) : c.label });
        }
        this.declutterLabels(drawn);
    }
    drawReactions() {
        const { ctx } = this;
        const drawn = [];
        for (const s of this.supports) {
            const x = this.wx(s.x), y = this.wy(s.y), on = s === this.pick || s === this.hover;
            const r = this.rad(s.fz, this.maxFz, 3.5, 11);
            ctx.beginPath();
            ctx.fillStyle = s.fz >= 0 ? css("--up") : css("--tens");
            ctx.globalAlpha = on ? 1 : .9;
            ctx.arc(x, y, on ? r + 1.5 : r, 0, 7);
            ctx.fill();
            if (on) {
                ctx.lineWidth = 2;
                ctx.strokeStyle = css("--ink");
                ctx.stroke();
            }
            ctx.globalAlpha = 1;
            drawn.push({ x, y, r, val: s.fz, on, label: String(Math.round(Math.abs(s.fz))) });
        }
        this.declutterLabels(drawn);
    }
    declutterLabels(items) {
        if (!this.showLabels)
            return;
        const { ctx } = this;
        ctx.font = "600 10px " + css("--font-mono");
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        const order = items.slice().sort((a, b) => (+b.on - +a.on) || (Math.abs(b.val ?? 0) - Math.abs(a.val ?? 0)));
        const placed = [];
        const GX = 30, GY = 13;
        for (const d of order) {
            if (d.x < -30 || d.x > this.W() + 30 || d.y < -20 || d.y > this.H() + 20)
                continue;
            let ok = d.on;
            if (!ok) {
                ok = true;
                for (const p of placed)
                    if (Math.abs(p[0] - d.x) < GX && Math.abs(p[1] - d.y) < GY) {
                        ok = false;
                        break;
                    }
            }
            if (!ok)
                continue;
            placed.push([d.x, d.y]);
            ctx.fillStyle = d.on ? css("--ink") : css("--ink-soft");
            ctx.fillText(d.label, d.x, d.y - d.r - 2);
        }
    }
    drawScaleBar() {
        const target = 90 / this.scale, pow = Math.pow(10, Math.floor(Math.log10(target)));
        let L = pow;
        for (const m of [1, 2, 5, 10])
            if (m * pow <= target)
                L = m * pow;
        const el = document.getElementById("sbBar"), t = document.getElementById("sbTxt");
        if (el)
            el.style.width = (L * this.scale) + "px";
        if (t)
            t.textContent = L + " ft";
    }
    // ---- picking ----
    nearest(px, py) {
        if (this.layer === "react") {
            let best = null, bd = 16 * 16;
            for (const s of this.supports) {
                const dx = this.wx(s.x) - px, dy = this.wy(s.y) - py, d = dx * dx + dy * dy;
                if (d < bd) {
                    bd = d;
                    best = s;
                }
            }
            return best;
        }
        let best = null, bd = 14 * 14;
        for (const c of this.columns) {
            const dx = this.wx(c.ix) - px, dy = this.wy(c.iy) - py, d = dx * dx + dy * dy;
            if (d < bd) {
                bd = d;
                best = c;
            }
        }
        return best;
    }
    bindEvents() {
        const cv = this.cv;
        cv.addEventListener("pointerdown", e => { this.drag = { x: e.offsetX, y: e.offsetY, ox: this.ox, oy: this.oy, moved: false }; cv.setPointerCapture(e.pointerId); });
        cv.addEventListener("pointermove", e => {
            const w = this.inv(e.offsetX, e.offsetY);
            this.onCursor?.(w.x, w.y);
            if (this.drag) {
                this.ox = this.drag.ox + (e.offsetX - this.drag.x);
                this.oy = this.drag.oy - (e.offsetY - this.drag.y);
                this.drag.moved = true;
                this.draw();
                return;
            }
            const h = this.nearest(e.offsetX, e.offsetY);
            if (h !== this.hover) {
                this.hover = h;
                cv.style.cursor = h ? "pointer" : "default";
                if (!this.pick)
                    this.emit(h);
                this.draw();
            }
        });
        cv.addEventListener("pointerup", e => {
            if (this.drag && !this.drag.moved) {
                const h = this.nearest(e.offsetX, e.offsetY);
                this.pick = h;
                this.emit(h);
                this.draw();
            }
            this.drag = null;
        });
        cv.addEventListener("wheel", e => { e.preventDefault(); this.zoomAt(e.offsetX, e.offsetY, e.deltaY < 0 ? 1.12 : 1 / 1.12); }, { passive: false });
        window.addEventListener("resize", () => this.resize());
    }
    emit(d) {
        if (!d) {
            this.onPick?.(null);
            return;
        }
        this.onPick?.({ kind: this.layer === "react" ? "support" : "column", data: d });
    }
    // ---- PDF (self-contained; sandbox-safe) ----
    exportPDF(fname) {
        const root = document.documentElement, prev = root.getAttribute("data-theme");
        root.setAttribute("data-theme", "light");
        this.draw();
        const headH = 72, Wc = this.W(), Hc = this.H();
        const oc = document.createElement("canvas");
        oc.width = this.cv.width;
        oc.height = this.cv.height + Math.round(headH * this.dpr);
        const o = oc.getContext("2d");
        o.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
        o.fillStyle = "#fff";
        o.fillRect(0, 0, Wc, Hc + headH);
        o.fillStyle = "#0e7c86";
        o.fillRect(0, 0, Wc, 3);
        o.fillStyle = "#111827";
        o.font = '700 22px system-ui,sans-serif';
        o.fillText(this.title, 18, 36);
        o.drawImage(this.cv, 0, headH, Wc, Hc);
        if (prev)
            root.setAttribute("data-theme", prev);
        else
            root.removeAttribute("data-theme");
        this.draw();
        const b64 = oc.toDataURL("image/jpeg", 0.92).split(",")[1], bin = atob(b64);
        const jpg = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++)
            jpg[i] = bin.charCodeAt(i);
        const pdf = buildPDF(jpg, oc.width, oc.height);
        const url = URL.createObjectURL(new Blob([pdf.buffer], { type: "application/pdf" }));
        // Primary: real download (works on a normal top-level page).
        try {
            const a = document.createElement("a");
            a.href = url;
            a.download = fname;
            a.rel = "noopener";
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
        catch { /* ignore */ }
        // Embedded (sandboxed iframe): downloads are blocked — open the PDF in a new tab so it's reachable.
        const embedded = window.self !== window.top;
        let opened = false;
        if (embedded) {
            try {
                opened = !!window.open(url, "_blank");
            }
            catch { /* popup blocked */ }
        }
        setTimeout(() => URL.revokeObjectURL(url), 20000);
        this.onNotify?.(embedded
            ? (opened ? "PDF opened in a new tab — press Ctrl+S to save it." : "Pop-up blocked — allow pop-ups to get the PDF, or open the app in its own tab.")
            : `Saved “${fname}” — check your Downloads folder.`);
    }
}
function buildPDF(jpg, iw, ih) {
    const PW = 792, PH = Math.round(PW * ih / iw);
    const enc = (s) => { const a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++)
        a[i] = s.charCodeAt(i) & 255; return a; };
    const parts = [];
    let off = 0;
    const xr = [];
    const put = (u) => { parts.push(u); off += u.length; };
    const puts = (s) => put(enc(s));
    puts("%PDF-1.3\n");
    const obj = (n, b) => { xr[n] = off; puts(`${n} 0 obj\n` + b + "\nendobj\n"); };
    obj(1, "<</Type/Catalog/Pages 2 0 R>>");
    obj(2, "<</Type/Pages/Kids[3 0 R]/Count 1>>");
    obj(3, `<</Type/Page/Parent 2 0 R/MediaBox[0 0 ${PW} ${PH}]/Resources<</XObject<</Im0 4 0 R>>>>/Contents 5 0 R>>`);
    xr[4] = off;
    puts(`4 0 obj\n<</Type/XObject/Subtype/Image/Width ${iw}/Height ${ih}/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/DCTDecode/Length ${jpg.length}>>\nstream\n`);
    put(jpg);
    puts("\nendstream\nendobj\n");
    const content = `q ${PW} 0 0 ${PH} 0 0 cm /Im0 Do Q`;
    xr[5] = off;
    puts(`5 0 obj\n<</Length ${content.length}>>\nstream\n` + content + "\nendstream\nendobj\n");
    const xs = off;
    let x = "xref\n0 6\n0000000000 65535 f \n";
    for (let i = 1; i <= 5; i++)
        x += String(xr[i]).padStart(10, "0") + " 00000 n \n";
    puts(x);
    puts(`trailer\n<</Size 6/Root 1 0 R>>\nstartxref\n${xs}\n%%EOF`);
    const tot = parts.reduce((n, p) => n + p.length, 0), out = new Uint8Array(tot);
    let p = 0;
    for (const u of parts) {
        out.set(u, p);
        p += u.length;
    }
    return out;
}

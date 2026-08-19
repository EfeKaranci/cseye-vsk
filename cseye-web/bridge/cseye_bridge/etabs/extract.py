"""
ETABS extraction — pure functions of SapModel (call them via EtabsSession.run).
Mirrors the validated standalone scripts: geometry, result sets, column base
forces (cases AND combos), and support reactions. Read-only.
"""
from __future__ import annotations
import math
from collections import defaultdict

R = lambda v: round(float(v), 4)
R3 = lambda v: round(float(v), 3)
ORIENT = {1: "column", 2: "beam", 3: "brace", 4: "null", 5: "other"}


def _table(sm, name):
    try:
        t = sm.DatabaseTables.GetTableForDisplayArray(name, "", "", 21, "")
        ncol = len(t[2]); headers = list(t[2]); flat = list(t[4])
        rows = [flat[i:i + ncol] for i in range(0, len(flat), ncol)]
        return [dict(zip(headers, r)) for r in rows]
    except Exception:
        return []


def geometry(sm) -> dict:
    st = sm.Story.GetStories_2()
    stories = [{"name": n.strip(), "elev": R(e)} for n, e in zip(st[2], st[3])]
    ptnames = sm.PointObj.GetNameList()[1]
    points = {}
    for nm in ptnames:
        c = sm.PointObj.GetCoordCartesian(nm, 0., 0., 0.)
        points[nm] = [R(c[0]), R(c[1]), R(c[2])]
    frames = []
    for nm in sm.FrameObj.GetNameList()[1]:
        try:
            o = sm.FrameObj.GetDesignOrientation(nm)[0]
        except Exception:
            o = -1
        pts = sm.FrameObj.GetPoints(nm, "", "")
        lbl = sm.FrameObj.GetLabelFromName(nm)
        sec = sm.FrameObj.GetSection(nm)[0]
        i, j = points.get(pts[0]), points.get(pts[1])
        frames.append({
            "name": nm, "label": lbl[0], "story": lbl[1].strip(),
            "type": ORIENT.get(o, "unknown"),
            "ix": i[0] if i else 0, "iy": i[1] if i else 0, "iz": i[2] if i else 0,
            "jx": j[0] if j else 0, "jy": j[1] if j else 0, "jz": j[2] if j else 0,
            "section": sec,
        })
    xs = [p[0] for p in points.values()]; ys = [p[1] for p in points.values()]
    extents = {"xmin": R(min(xs)), "xmax": R(max(xs)), "ymin": R(min(ys)), "ymax": R(max(ys))}
    grids = _grid_lines(_table(sm, "Grid Definitions - Grid Lines"), extents, _grid_systems(sm))
    return {
        "model": sm.GetModelFilename(), "etabs_version": sm.GetVersion()[0], "units": "kip, ft",
        "locked": bool(sm.GetModelIsLocked()), "extents": extents,
        "stories": stories, "frames": frames, "grid_lines": grids, "combos": combos(sm),
    }


def _grid_systems(sm) -> dict:
    """Per grid system: global origin (ux,uy), rotation (deg), and the local
    ordinate span, so grid lines can be placed in GLOBAL coordinates."""
    out: dict = {}
    try:
        names = sm.GridSys.GetNameList()[1]
    except Exception:
        return out
    for nm in names:
        try:
            r = sm.GridSys.GetGridSys_2(nm, 0.0, 0.0, 0.0)
        except Exception:
            continue
        try:
            xo = [float(v) for v in (r[8] or [])]; yo = [float(v) for v in (r[9] or [])]
        except Exception:
            xo, yo = [], []
        out[str(nm).strip()] = {
            "ux": float(r[0]), "uy": float(r[1]), "rz": float(r[2]),
            "xmin": min(xo) if xo else 0.0, "xmax": max(xo) if xo else 0.0,
            "ymin": min(yo) if yo else 0.0, "ymax": max(yo) if yo else 0.0,
        }
    return out


def _to_global(S, lx, ly):
    """Local (grid-system) coords -> global, via origin + rotation."""
    th = math.radians(S["rz"]); c = math.cos(th); s = math.sin(th)
    return R(S["ux"] + lx * c - ly * s), R(S["uy"] + lx * s + ly * c)


def _grid_lines(rows, e, systems):
    out = []
    def num(v):
        try: return float(v)
        except Exception: return None
    for g in rows:
        lt = g.get("LineType", ""); vis = g.get("Visible") == "Yes"; gid = str(g.get("ID", "")).strip()
        sysn = str(g.get("Name", "")).strip(); S = systems.get(sysn)
        if lt.startswith("X"):
            o = num(g.get("Ordinate"))
            if o is None: continue
            if S is not None:
                x1, y1 = _to_global(S, o, S["ymin"]); x2, y2 = _to_global(S, o, S["ymax"])
            else:                                        # no system transform available → global axis-aligned
                x1, y1, x2, y2 = o, e["ymin"], o, e["ymax"]
            out.append({"id": gid, "dir": "G", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "visible": vis, "sys": sysn})
        elif lt.startswith("Y"):
            o = num(g.get("Ordinate"))
            if o is None: continue
            if S is not None:
                x1, y1 = _to_global(S, S["xmin"], o); x2, y2 = _to_global(S, S["xmax"], o)
            else:
                x1, y1, x2, y2 = e["xmin"], o, e["xmax"], o
            out.append({"id": gid, "dir": "G", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "visible": vis, "sys": sysn})
        else:                                            # general / free grid line: already global
            x1, y1, x2, y2 = num(g.get("X1")), num(g.get("Y1")), num(g.get("X2")), num(g.get("Y2"))
            if None not in (x1, y1, x2, y2): out.append({"id": gid, "dir": "G", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "visible": vis, "sys": sysn})
    return out


def combos(sm) -> dict:
    """Composition of each load combination: {name: {type, items:[{case, sf}]}}."""
    out: dict = {}
    for r in _table(sm, "Load Combination Definitions"):
        name = r.get("Name"); ln = r.get("LoadName")
        if not name:
            continue
        c = out.setdefault(name, {"type": None, "items": []})
        typ = r.get("Type")
        if typ and str(typ) != "None":
            c["type"] = typ
        if ln:
            try:
                sf = round(float(r.get("SF")), 4)
            except Exception:
                sf = r.get("SF")
            c["items"].append({"case": ln, "sf": sf})
    return out


def staged_labels(sm) -> dict:
    """Ordered output-stage labels per nonlinear staged-construction case:
    {case: ['1YR','2YR',...]} (comment, else stage name)."""
    by_case: dict = {}
    for r in _table(sm, "Load Case Definitions - Nonlinear Staged Construction"):
        name = r.get("Name"); stg = r.get("Stage")
        if not name or stg in (None, "None", ""):
            continue
        d = by_case.setdefault(name, {})
        e = d.setdefault(stg, {"stage": stg, "name": None, "comment": None, "output": None})
        for k, col in (("name", "StageName"), ("comment", "Comments"), ("output", "Output")):
            if not e[k] and r.get(col) not in (None, "None"):
                e[k] = r.get(col)
    def _num(st):
        try:
            return str(int(float(st)))
        except Exception:
            return str(st)

    def _lbl(s):
        parts = [_num(s["stage"])]
        for k in ("name", "comment"):
            v = s.get(k)
            if v not in (None, "", "None"):
                parts.append(str(v))
        return " - ".join(parts)

    labels: dict = {}
    for name, stages in by_case.items():
        try:
            ordered = sorted(stages.values(), key=lambda s: float(s["stage"]))
        except Exception:
            ordered = list(stages.values())
        outs = [s for s in ordered if str(s.get("output")).lower() == "yes"]
        labels[name] = [_lbl(s) for s in outs]
    return labels


def result_sets(sm) -> list[dict]:
    cst = sm.Analyze.GetCaseStatus()
    status = {n: s for n, s in zip(cst[1], cst[2])}
    combos = set(sm.RespCombo.GetNameList()[1])
    out = []
    for n in sm.LoadCases.GetNameList()[1]:
        out.append({"name": n, "kind": "case", "finished": status.get(n) == 4})
    for n in combos:
        out.append({"name": n, "kind": "combo", "finished": None})
    return out


def _select(sm, names):
    setup = sm.Results.Setup
    setup.DeselectAllCasesAndCombosForOutput()
    # Return INDIVIDUAL steps for multi-step cases (e.g. multi-direction wind like
    # W-user = Step 1..N) instead of only Max/Min envelopes. The envelope is then
    # recovered as min/max across the stored steps. Combos stay as envelopes.
    for setter, opt in (("SetOptionMultiStepStatic", 2),   # 2 = Step-by-Step
                        ("SetOptionNLStatic", 2),
                        ("SetOptionMultiValuedCombo", 1)):  # 1 = Envelopes (Max/Min)
        fn = getattr(setup, setter, None)
        if fn is not None:
            try:
                fn(opt)
            except Exception:
                pass
    cases = set(sm.LoadCases.GetNameList()[1]); combos = set(sm.RespCombo.GetNameList()[1])
    for n in names:
        if n in combos: setup.SetComboSelectedForOutput(n)
        elif n in cases: setup.SetCaseSelectedForOutput(n)


def step_label(st, sn) -> str:
    """Human label for a result step: '' (single value), 'Max'/'Min' (envelope),
    'Mode 3', 'Step 2' (multi-step / nonlinear staged construction stages)."""
    st = (str(st) or "").strip()
    try:
        n = float(sn)
    except Exception:
        n = 0.0
    if st in ("Max", "Min"):
        return st
    if not st:                                   # empty type → distinguish by step number
        return "" if n == 0 else f"Step {n:g}"
    return f"{st} {n:g}" if n else st


def _columns(sm) -> list[str]:
    out = []
    for nm in sm.FrameObj.GetNameList()[1]:
        try:
            if sm.FrameObj.GetDesignOrientation(nm)[0] == 1:
                out.append(nm)
        except Exception:
            pass
    return out


def column_forces(sm, names) -> tuple[dict, dict]:
    """Base-station forces per column, per result set, PER STEP.
    Returns (forces, steps) where
      forces = { frame: { result: { step: {P,V2,V3,M2,M3} } } }
      steps  = { result: [ordered step labels] }.
    """
    _select(sm, names)
    staged = staged_labels(sm)
    forces: dict = {}
    steps: dict = {}
    for nm in _columns(sm):
        pts = sm.FrameObj.GetPoints(nm, "", "")
        zi = sm.PointObj.GetCoordCartesian(pts[0], 0., 0., 0.)[2]
        zj = sm.PointObj.GetCoordCartesian(pts[1], 0., 0., 0.)[2]
        ff = sm.Results.FrameForce(nm, 0); n = ff[0]
        if not n: continue
        sta = ff[2]; base = min(sta) if zi <= zj else max(sta)
        base_by_rs: dict = {}                       # result set -> [row idx] at base station, in order
        for r in range(n):
            if abs(sta[r] - base) > 1e-4: continue
            base_by_rs.setdefault(ff[5][r], []).append(r)
        d: dict = {}
        for rs, rows in base_by_rs.items():
            labs = [step_label(ff[6][r], ff[7][r]) for r in rows]
            if len(rows) > 1 and len(set(labs)) < len(rows):   # staged construction: blank labels
                sl = staged.get(rs)
                labs = sl if (sl and len(sl) == len(rows)) else [f"Step {i + 1}" for i in range(len(rows))]
            rd = d.setdefault(rs, {}); slist = steps.setdefault(rs, [])
            for r, lab in zip(rows, labs):
                rd[lab] = {"P": R3(ff[8][r]), "V2": R3(ff[9][r]), "V3": R3(ff[10][r]),
                           "M2": R3(ff[12][r]), "M3": R3(ff[13][r])}
                if lab not in slist: slist.append(lab)
        forces[nm] = d
    return forces, steps


def reactions(sm, names) -> dict:
    """Support reactions per result set, PER STEP.
    Returns { joint: {x,y,z, results:{ result:{ step:{Fx..Mz} } } } } (supports only)."""
    _select(sm, names)
    staged = staged_labels(sm)
    jr = sm.Results.JointReact("All", 2); n = jr[0]
    order: dict = {}                                 # joint -> result set -> [row idx] in order
    for i in range(n):
        order.setdefault(jr[1][i], {}).setdefault(jr[3][i], []).append(i)
    acc: dict = {}
    for j, per_rs in order.items():
        for rs, rows in per_rs.items():
            labs = [step_label(jr[4][i], jr[5][i]) for i in rows]
            if len(rows) > 1 and len(set(labs)) < len(rows):   # staged construction
                sl = staged.get(rs)
                labs = sl if (sl and len(sl) == len(rows)) else [f"Step {k + 1}" for k in range(len(rows))]
            for i, lab in zip(rows, labs):
                acc.setdefault(j, {}).setdefault(rs, {})[lab] = {
                    "Fx": R3(jr[6][i]), "Fy": R3(jr[7][i]), "Fz": R3(jr[8][i]),
                    "Mx": R3(jr[9][i]), "My": R3(jr[10][i]), "Mz": R3(jr[11][i])}
    out: dict = {}
    for j, per in acc.items():
        mx = 0.0
        for steps in per.values():
            for v in steps.values():
                mx = max(mx, abs(v["Fz"]), abs(v["Fx"]), abs(v["Fy"]))
        if mx > 0.5:
            c = sm.PointObj.GetCoordCartesian(j, 0., 0., 0.)
            out[j] = {"x": R3(c[0]), "y": R3(c[1]), "z": R3(c[2]), "results": per}
    return out

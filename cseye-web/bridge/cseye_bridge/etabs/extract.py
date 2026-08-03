"""
ETABS extraction — pure functions of SapModel (call them via EtabsSession.run).
Mirrors the validated standalone scripts: geometry, result sets, column base
forces (cases AND combos), and support reactions. Read-only.
"""
from __future__ import annotations
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
    grids = _grid_lines(_table(sm, "Grid Definitions - Grid Lines"), extents)
    return {
        "model": sm.GetModelFilename(), "etabs_version": sm.GetVersion()[0], "units": "kip, ft",
        "locked": bool(sm.GetModelIsLocked()), "extents": extents,
        "stories": stories, "frames": frames, "grid_lines": grids,
    }


def _grid_lines(rows, e):
    out = []
    def num(v):
        try: return float(v)
        except Exception: return None
    for g in rows:
        lt = g.get("LineType", ""); vis = g.get("Visible") == "Yes"; gid = str(g.get("ID", "")).strip()
        if lt.startswith("X"):
            o = num(g.get("Ordinate"))
            if o is not None: out.append({"id": gid, "dir": "X", "x1": o, "y1": e["ymin"], "x2": o, "y2": e["ymax"], "visible": vis})
        elif lt.startswith("Y"):
            o = num(g.get("Ordinate"))
            if o is not None: out.append({"id": gid, "dir": "Y", "x1": e["xmin"], "y1": o, "x2": e["xmax"], "y2": o, "visible": vis})
        else:
            x1, y1, x2, y2 = num(g.get("X1")), num(g.get("Y1")), num(g.get("X2")), num(g.get("Y2"))
            if None not in (x1, y1, x2, y2): out.append({"id": gid, "dir": "G", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "visible": vis})
    return out


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
    cases = set(sm.LoadCases.GetNameList()[1]); combos = set(sm.RespCombo.GetNameList()[1])
    for n in names:
        if n in combos: setup.SetComboSelectedForOutput(n)
        elif n in cases: setup.SetCaseSelectedForOutput(n)


def column_forces(sm, names) -> tuple[dict, set]:
    """Base-station P/V/M per column for the selected result sets. Returns (forces, seen)."""
    _select(sm, names)
    zmap = {}
    cols = []
    for nm in sm.FrameObj.GetNameList()[1]:
        try:
            if sm.FrameObj.GetDesignOrientation(nm)[0] == 1:
                cols.append(nm)
        except Exception:
            pass
    forces = {}; seen = set()
    for nm in cols:
        pts = sm.FrameObj.GetPoints(nm, "", "")
        zi = sm.PointObj.GetCoordCartesian(pts[0], 0., 0., 0.)[2]
        zj = sm.PointObj.GetCoordCartesian(pts[1], 0., 0., 0.)[2]
        ff = sm.Results.FrameForce(nm, 0); n = ff[0]
        if not n: continue
        sta = ff[2]; base = min(sta) if zi <= zj else max(sta)
        per = defaultdict(lambda: {"Pmin": 1e30, "Pmax": -1e30, "V2": 0, "V3": 0, "M2": 0, "M3": 0})
        for r in range(n):
            if abs(sta[r] - base) > 1e-4: continue
            cse = ff[5][r]; P = ff[8][r]; seen.add(cse); d = per[cse]
            if P < d["Pmin"]: d["Pmin"] = P
            if P > d["Pmax"]:
                d["Pmax"] = P; d["V2"] = ff[9][r]; d["V3"] = ff[10][r]; d["M2"] = ff[12][r]; d["M3"] = ff[13][r]
        forces[nm] = {c: {k: R3(v) for k, v in d.items()} for c, d in per.items()}
    return forces, seen


def reactions(sm, names) -> dict:
    _select(sm, names)
    jr = sm.Results.JointReact("All", 2); n = jr[0]
    acc = defaultdict(dict)
    for i in range(n):
        acc[jr[1][i]][jr[3][i]] = {"Fx": R3(jr[6][i]), "Fy": R3(jr[7][i]), "Fz": R3(jr[8][i]),
                                   "Mx": R3(jr[9][i]), "My": R3(jr[10][i]), "Mz": R3(jr[11][i])}
    out = {}
    for j, cs in acc.items():
        if max((abs(v["Fz"]) for v in cs.values()), default=0) > 0.5 or \
           max((max(abs(v["Fx"]), abs(v["Fy"])) for v in cs.values()), default=0) > 0.5:
            c = sm.PointObj.GetCoordCartesian(j, 0., 0., 0.)
            out[j] = {"x": R3(c[0]), "y": R3(c[1]), "z": R3(c[2]), "cases": cs}
    return out

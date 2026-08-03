"""Upsert extracted results and serve per-slice queries to the viewer."""
from __future__ import annotations
import json, hashlib, os, datetime, threading
from .schema import connect

_con = None
_lock = threading.Lock()


def con():
    global _con
    if _con is None:
        _con = connect()
    return _con


def snapshot_id(path: str) -> str:
    try:
        st = os.stat(path)
        key = f"{path}|{int(st.st_mtime)}|{st.st_size}"
    except OSError:
        key = path
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def save_geometry(geom: dict) -> str:
    sid = snapshot_id(geom["model"])
    with _lock:
        c = con()
        c.execute("DELETE FROM snapshot WHERE id=?", (sid,))
        for t in ("story", "grid_line", "frame"):
            c.execute(f"DELETE FROM {t} WHERE sid=?", (sid,))
        c.execute(
            "INSERT INTO snapshot VALUES(?,?,?,?,?,?,?,?)",
            (sid, geom["model"], os.path.basename(geom["model"]), geom["etabs_version"],
             geom["units"], json.dumps(geom["extents"]), int(geom["locked"]),
             datetime.datetime.now().isoformat(timespec="seconds")),
        )
        c.executemany("INSERT INTO story VALUES(?,?,?)",
                      [(sid, s["name"], s["elev"]) for s in geom["stories"]])
        c.executemany("INSERT INTO grid_line VALUES(?,?,?,?,?,?,?,?)",
                      [(sid, g["id"], g["dir"], g["x1"], g["y1"], g["x2"], g["y2"], int(g["visible"]))
                       for g in geom["grid_lines"]])
        c.executemany(
            "INSERT INTO frame VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            [(sid, f["name"], f["label"], f["story"], f["type"],
              f["ix"], f["iy"], f["iz"], f["jx"], f["jy"], f["jz"], f["section"]) for f in geom["frames"]],
        )
        c.commit()
    return sid


def save_result_sets(sid: str, sets: list[dict]):
    with _lock:
        c = con()
        c.execute("DELETE FROM result_set WHERE sid=?", (sid,))
        c.executemany("INSERT INTO result_set VALUES(?,?,?,?)",
                      [(sid, s["name"], s["kind"], None if s["finished"] is None else int(s["finished"])) for s in sets])
        c.commit()


def save_column_forces(sid: str, forces: dict, steps: dict, result_names: list[str]):
    with _lock:
        c = con()
        for name in result_names:
            c.execute("DELETE FROM column_force WHERE sid=? AND result_set=?", (sid, name))
            c.execute("DELETE FROM step WHERE sid=? AND result_set=?", (sid, name))
        rows = []
        for frame, per in forces.items():
            for rs, stepmap in per.items():
                for st, d in stepmap.items():
                    rows.append((sid, rs, frame, st, d["P"], d["V2"], d["V3"], d["M2"], d["M3"]))
        c.executemany("INSERT OR REPLACE INTO column_force VALUES(?,?,?,?,?,?,?,?,?)", rows)
        srows = [(sid, rs, lab, i) for rs, labels in steps.items() for i, lab in enumerate(labels)]
        c.executemany("INSERT OR REPLACE INTO step VALUES(?,?,?,?)", srows)
        c.commit()


def save_reactions(sid: str, reactions: dict, result_names: list[str]):
    with _lock:
        c = con()
        for name in result_names:
            c.execute("DELETE FROM reaction WHERE sid=? AND result_set=?", (sid, name))
        rows = []
        for joint, r in reactions.items():
            for rs, stepmap in r["results"].items():
                for st, f in stepmap.items():
                    rows.append((sid, rs, joint, st, r["x"], r["y"], r["z"],
                                 f["Fx"], f["Fy"], f["Fz"], f["Mx"], f["My"], f["Mz"]))
        c.executemany("INSERT OR REPLACE INTO reaction VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        c.commit()


# ---------------- queries ----------------
def meta(sid: str) -> dict | None:
    c = con()
    s = c.execute("SELECT * FROM snapshot WHERE id=?", (sid,)).fetchone()
    if not s: return None
    stories = [dict(r) for r in c.execute("SELECT name,elev FROM story WHERE sid=? ORDER BY elev", (sid,))]
    rs = [dict(r) for r in c.execute("SELECT name,kind,finished FROM result_set WHERE sid=?", (sid,))]
    have = {r["result_set"] for r in c.execute("SELECT DISTINCT result_set FROM column_force WHERE sid=?", (sid,))}
    for r in rs:
        r["extracted"] = r["name"] in have
    return {"id": sid, "model": s["model"], "path": s["path"], "etabs_version": s["etabs_ver"],
            "units": s["units"], "locked": bool(s["locked"]), "extents": json.loads(s["extents"]),
            "stories": stories, "result_sets": rs}


def geometry(sid: str) -> dict:
    c = con()
    frames = [dict(r) for r in c.execute("SELECT name,label,story,type,ix,iy,iz,jx,jy,jz,section FROM frame WHERE sid=?", (sid,))]
    grids = [dict(r) for r in c.execute("SELECT gid as id,dir,x1,y1,x2,y2,visible FROM grid_line WHERE sid=?", (sid,))]
    return {"frames": frames, "grid_lines": grids}


def steps(sid: str, result: str) -> list[str]:
    c = con()
    return [r["label"] for r in c.execute(
        "SELECT label FROM step WHERE sid=? AND result_set=? ORDER BY idx", (sid, result))]


def plan(sid: str, story: str, result: str, step: str | None = None) -> list[dict]:
    """Columns at a story with base forces. Aggregate across steps by default
    (pmin/pmax + governing V/M); a specific `step` returns that step's values."""
    c = con()
    rows = c.execute(
        """SELECT f.name,f.label,f.section,f.ix,f.iy,f.iz,f.jx,f.jy,f.jz,
                  cf.step,cf.p,cf.v2,cf.v3,cf.m2,cf.m3
           FROM frame f LEFT JOIN column_force cf
             ON cf.sid=f.sid AND cf.frame=f.name AND cf.result_set=?
           WHERE f.sid=? AND f.story=? AND f.type='column'""",
        (result, sid, story),
    ).fetchall()
    byf: dict = {}
    for r in rows:
        d = byf.setdefault(r["name"], {"name": r["name"], "label": r["label"], "section": r["section"],
                                       "ix": r["ix"], "iy": r["iy"], "iz": r["iz"],
                                       "jx": r["jx"], "jy": r["jy"], "jz": r["jz"], "_s": []})
        if r["p"] is not None:
            d["_s"].append({"step": r["step"], "p": r["p"], "v2": r["v2"], "v3": r["v3"], "m2": r["m2"], "m3": r["m3"]})
    out = []
    for d in byf.values():
        s = d.pop("_s")
        pick = None
        if s and step is not None:
            pick = next((x for x in s if x["step"] == step), None)
        elif s:
            pick = max(s, key=lambda x: abs(x["p"]))
        if not s or (step is not None and pick is None):
            d.update({"pmin": None, "pmax": None, "v2": None, "v3": None, "m2": None, "m3": None})
        elif step is not None:
            d.update({"pmin": pick["p"], "pmax": pick["p"], "v2": pick["v2"], "v3": pick["v3"], "m2": pick["m2"], "m3": pick["m3"]})
        else:
            ps = [x["p"] for x in s]
            d.update({"pmin": min(ps), "pmax": max(ps), "v2": pick["v2"], "v3": pick["v3"], "m2": pick["m2"], "m3": pick["m3"]})
        out.append(d)
    return out


def reactions(sid: str, result: str, step: str | None = None) -> list[dict]:
    c = con()
    rows = c.execute(
        "SELECT joint,x,y,z,step,fx,fy,fz,mx,my,mz FROM reaction WHERE sid=? AND result_set=?",
        (sid, result),
    ).fetchall()
    byj: dict = {}
    for r in rows:
        byj.setdefault(r["joint"], {"joint": r["joint"], "x": r["x"], "y": r["y"], "z": r["z"], "_s": []})["_s"].append(dict(r))
    out = []
    for d in byj.values():
        s = d.pop("_s")
        row = next((x for x in s if x["step"] == step), s[0]) if step is not None else max(s, key=lambda x: abs(x["fz"]))
        fzs = [x["fz"] for x in s]
        d.update({"fx": row["fx"], "fy": row["fy"], "fz": row["fz"], "mx": row["mx"], "my": row["my"], "mz": row["mz"],
                  "fzmin": min(fzs), "fzmax": max(fzs)})
        out.append(d)
    return out

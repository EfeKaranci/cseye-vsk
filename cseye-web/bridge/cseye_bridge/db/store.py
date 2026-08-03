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


def save_forces(sid: str, forces: dict, reactions: dict, result_names: list[str]):
    with _lock:
        c = con()
        for name in result_names:
            c.execute("DELETE FROM column_force WHERE sid=? AND result_set=?", (sid, name))
            c.execute("DELETE FROM reaction WHERE sid=? AND result_set=?", (sid, name))
        rows = []
        for frame, per in forces.items():
            for rs, d in per.items():
                rows.append((sid, rs, frame, d["Pmin"], d["Pmax"], d["V2"], d["V3"], d["M2"], d["M3"]))
        c.executemany("INSERT OR REPLACE INTO column_force VALUES(?,?,?,?,?,?,?,?,?)", rows)
        rr = []
        for joint, r in reactions.items():
            for rs, f in r["cases"].items():
                rr.append((sid, rs, joint, r["x"], r["y"], r["z"], f["Fx"], f["Fy"], f["Fz"], f["Mx"], f["My"], f["Mz"]))
        c.executemany("INSERT OR REPLACE INTO reaction VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", rr)
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


def plan(sid: str, story: str, result: str) -> list[dict]:
    """Columns at a story with base forces for one result set."""
    c = con()
    rows = c.execute(
        """SELECT f.name,f.label,f.section,f.ix,f.iy,f.iz,f.jx,f.jy,f.jz,
                  cf.pmin,cf.pmax,cf.v2,cf.v3,cf.m2,cf.m3
           FROM frame f LEFT JOIN column_force cf
             ON cf.sid=f.sid AND cf.frame=f.name AND cf.result_set=?
           WHERE f.sid=? AND f.story=? AND f.type='column'""",
        (result, sid, story),
    ).fetchall()
    return [dict(r) for r in rows]


def reactions(sid: str, result: str) -> list[dict]:
    c = con()
    rows = c.execute(
        "SELECT joint,x,y,z,fx,fy,fz,mx,my,mz FROM reaction WHERE sid=? AND result_set=?",
        (sid, result),
    ).fetchall()
    return [dict(r) for r in rows]

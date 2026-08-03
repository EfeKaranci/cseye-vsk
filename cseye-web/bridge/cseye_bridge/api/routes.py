"""REST endpoints. The viewer talks only to these."""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body

from .. import config
from ..etabs.session import get_session
from ..etabs import extract
from ..db import store
from .. import publish as publisher

router = APIRouter()


@router.get("/health")
def health():
    sess = get_session()
    return {"ok": True, "version": "0.1.0", "etabs": sess.status()}


@router.get("/models")
def models(root: str | None = None):
    """Browse configured roots for .EDB files (scoped, capped)."""
    roots = [Path(root)] if root else config.ROOTS
    for r in roots:
        if not any(str(r).lower().startswith(str(a).lower()) for a in config.ROOTS):
            raise HTTPException(403, "root not allowed")
    out = []
    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*.EDB"):
            try:
                st = p.stat()
            except OSError:
                continue
            y00 = p.with_suffix(".Y00")
            out.append({
                "path": str(p), "name": p.name, "dir": str(p.parent),
                "size_mb": round(st.st_size / 1e6, 1),
                "mtime": int(st.st_mtime),
                "has_results_guess": y00.exists(),
            })
            if len(out) >= 2000:
                break
    out.sort(key=lambda m: m["mtime"], reverse=True)
    return {"roots": [str(r) for r in roots], "count": len(out), "models": out}


@router.post("/session/attach")
def session_attach():
    sess = get_session()
    status = sess.attach()
    geom = sess.run(extract.geometry)
    sid = store.save_geometry(geom)
    store.save_result_sets(sid, sess.run(extract.result_sets))
    return {"snapshot": sid, "status": status}


@router.post("/session/open")
def session_open(payload: dict = Body(...)):
    path = payload.get("path")
    if not path or not os.path.exists(path):
        raise HTTPException(400, "path not found")
    sess = get_session()
    status = sess.open(path)
    geom = sess.run(extract.geometry)
    sid = store.save_geometry(geom)
    store.save_result_sets(sid, sess.run(extract.result_sets))
    return {"snapshot": sid, "status": status}


@router.get("/m/{sid}/meta")
def meta(sid: str):
    m = store.meta(sid)
    if not m:
        raise HTTPException(404, "unknown snapshot")
    return m


@router.get("/m/{sid}/geometry")
def geometry(sid: str):
    return store.geometry(sid)


@router.post("/m/{sid}/extract")
def do_extract(sid: str, payload: dict = Body(default={})):
    """Extract forces+reactions for the named result sets (default: all finished)."""
    m = store.meta(sid)
    if not m:
        raise HTTPException(404, "unknown snapshot")
    names = payload.get("result_sets")
    if not names:
        names = [r["name"] for r in m["result_sets"] if r["kind"] == "case" and r["finished"]]
    sess = get_session()
    forces, steps = sess.run(lambda sm: extract.column_forces(sm, names))
    seen = list(steps.keys())
    reacts = sess.run(lambda sm: extract.reactions(sm, seen))
    store.save_column_forces(sid, forces, steps, seen)
    store.save_reactions(sid, reacts, seen)
    return {"extracted": sorted(seen), "columns": len(forces), "supports": len(reacts),
            "steps": {rs: len(labels) for rs, labels in steps.items() if len(labels) > 1}}


@router.get("/m/{sid}/steps")
def result_steps(sid: str, result: str):
    return {"result": result, "steps": store.steps(sid, result)}


@router.get("/m/{sid}/plan")
def plan(sid: str, story: str, result: str, step: str | None = None):
    return {"story": story, "result": result, "step": step, "columns": store.plan(sid, story, result, step)}


@router.get("/m/{sid}/reactions")
def reactions(sid: str, result: str, step: str | None = None):
    return {"result": result, "step": step, "supports": store.reactions(sid, result, step)}


@router.get("/config")
def bridge_config():
    """Whether cloud publishing is configured (so the UI can show/hide Publish)."""
    return {"publish_enabled": bool(config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY),
            "share_viewer": config.SHARE_VIEWER_URL or None}


@router.post("/m/{sid}/publish")
def do_publish(sid: str, payload: dict = Body(default={})):
    if not store.meta(sid):
        raise HTTPException(404, "unknown snapshot")
    try:
        return publisher.publish(sid, label=payload.get("label"),
                                 expires_days=payload.get("expires_days"),
                                 results=payload.get("results"),
                                 underlays=payload.get("underlays"))
    except RuntimeError as e:
        raise HTTPException(400, str(e))

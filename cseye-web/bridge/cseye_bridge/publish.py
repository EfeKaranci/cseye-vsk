"""
Publish a snapshot to Supabase for sharing: upload geometry + forces JSON
bundles to a public Storage bucket under a random token, and record a `share`
row. The service_role key stays here — it never reaches the browser.
"""
from __future__ import annotations
import json, uuid, datetime, urllib.request, urllib.error
from . import config
from .db import store


def _req(method: str, url: str, body: bytes | None, headers: dict) -> tuple[int, bytes]:
    r = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {url} -> {e.code}: {e.read().decode(errors='replace')[:300]}")


def _svc_headers() -> dict:
    key = config.SUPABASE_SERVICE_KEY
    return {"Authorization": f"Bearer {key}", "apikey": key, "Content-Type": "application/json"}


def ensure_bucket() -> None:
    """Create the public Storage bucket if it doesn't exist (idempotent)."""
    url, bucket = config.SUPABASE_URL, config.SUPABASE_BUCKET
    body = json.dumps({"id": bucket, "name": bucket, "public": True}).encode()
    try:
        _req("POST", f"{url}/storage/v1/bucket", body, _svc_headers())
    except RuntimeError as e:
        if "already exist" not in str(e).lower() and "duplicate" not in str(e).lower():
            raise


def publish(sid: str, label: str | None = None, expires_days: int | None = None) -> dict:
    url, key, bucket = config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY, config.SUPABASE_BUCKET
    if not url or not key:
        raise RuntimeError("Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
    geom = store.export_geometry(sid)
    forces = store.export_forces(sid)
    if not forces["result_sets"]:
        raise RuntimeError("Nothing to publish yet — extract at least one result set first.")

    ensure_bucket()
    token = str(uuid.uuid4())
    base = f"{url}/storage/v1/object/{bucket}/snapshots/{token}"
    up_hdr = {**_svc_headers(), "x-upsert": "true"}
    for name, obj in (("geometry.json", geom), ("forces.json", forces)):
        _req("POST", f"{base}/{name}", json.dumps(obj, separators=(",", ":")).encode(), up_hdr)

    # Best-effort share registry row (optional — the token path alone drives the viewer).
    share_recorded = False
    try:
        row = {"token": token, "model": geom["model"], "label": label or geom["model"],
               "results": forces["result_sets"]}
        if expires_days:
            row["expires_at"] = (datetime.datetime.utcnow() + datetime.timedelta(days=expires_days)).isoformat() + "Z"
        _req("POST", f"{url}/rest/v1/share", json.dumps(row).encode(),
             {**_svc_headers(), "Prefer": "return=minimal"})
        share_recorded = True
    except RuntimeError:
        pass  # `share` table not created — fine, sharing still works by token

    share_url = (config.SHARE_VIEWER_URL.rstrip("/") + f"?s={token}") if config.SHARE_VIEWER_URL else None
    return {"token": token, "share_url": share_url, "results": forces["result_sets"],
            "share_recorded": share_recorded,
            "public_base": f"{url}/storage/v1/object/public/{bucket}/snapshots/{token}"}

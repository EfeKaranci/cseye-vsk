# CSEYE Web

Browser-based viewer for ETABS results — per-level column forces, base reactions,
(and later bracing-elevation & diaphragm forces) on the real model geometry, with
PDF export and shareable links.

See the full spec: **CSEYE Web — Technical Specification** (rev 0.2).

## Why a local "bridge"

The CSI OAPI is Windows COM/.NET — results can only be read by opening a model in
ETABS via the API. A browser can't do that. So a small local **bridge service**
(FastAPI) drives ETABS, extracts results into a normalized store, and serves them
to the web viewer over `localhost`. For sharing, a snapshot is published to the
cloud (Supabase) and viewed with no ETABS needed.

```
Browser (viewer)  ──http──►  bridge (FastAPI)  ──COM──►  ETABS 23
                                 │
                                 └── SQLite cache (normalized results)
```

## Layout

```
cseye-web/
  bridge/                 # local FastAPI service (this phase)
    cseye_bridge/
      config.py           # roots to browse (e.g. C:\Analysis), settings
      etabs/session.py    # single-thread ETABS COM session (attach/open)
      etabs/extract.py    # geometry / result-sets / column forces / reactions
      db/schema.py        # SQLite schema (normalized, query-on-demand)
      db/store.py         # upsert + slice queries
      api/routes.py       # REST endpoints
      main.py             # FastAPI app (CORS, static viewer)
    run.py                # uvicorn entry
    requirements.txt
  viewer/                 # Vite + TS front-end (renderer port — next)
    legacy/               # the working single-file Canvas viewer (reference)
```

## Run (dev)

```
cd cseye-web/bridge
pip install -r requirements.txt          # into your ETABS-enabled venv
python run.py                            # serves http://127.0.0.1:8765
```

Open the model you want in ETABS (analyzed/locked), then in the viewer:
**Attach → browse → pick model → load level**. Endpoints are documented at
`http://127.0.0.1:8765/docs`.

## Status

- [x] ETABS attach/open, geometry + forces (cases **and** combos) + reactions extraction (proven)
- [x] Normalized SQLite schema + query-on-demand
- [x] Model browser over configured roots
- [ ] Vite+TS renderer port (currently: single-file Canvas viewer in `viewer/legacy/`)
- [ ] Publish → Supabase + shareable hosted viewer (Phase 3)

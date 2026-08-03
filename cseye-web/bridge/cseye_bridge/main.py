"""FastAPI app: CORS, routes, and (optionally) the static viewer."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .api.routes import router

app = FastAPI(title="CSEYE bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(router)

# Serve the built viewer if present (viewer/dist), else the legacy single-file viewer.
_here = Path(__file__).resolve().parent.parent.parent
for cand in (_here / "viewer" / "dist", _here / "viewer" / "legacy"):
    if cand.exists():
        app.mount("/", StaticFiles(directory=str(cand), html=True), name="viewer")
        break

"""CSEYE portable launcher.

Starts the local bridge (FastAPI/uvicorn) and opens the viewer in the default
browser. No install and no admin rights required — everything runs from this
folder. Cloud "Publish" is disabled unless a `.env` is placed next to this file
(kept out of the shared package so the Supabase key stays private).
"""
import os
import sys
import time
import socket
import threading
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent          # ...\app\bridge
sys.path.insert(0, str(HERE))                    # make `cseye_bridge` importable

# Optional per-machine overrides: a `.env` next to this launcher (advanced use).
# The local .env is the ONLY source of configuration here.
_env = HERE / ".env"
_local: dict[str, str] = {}
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            _local[_k.strip()] = _v.strip()
for _k, _v in _local.items():
    os.environ[_k] = _v

# Never publish with ambient/inherited credentials: unless the local .env
# explicitly provides Supabase settings, strip them so publishing stays OFF.
for _var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_BUCKET", "CSEYE_SHARE_URL"):
    if _var not in _local:
        os.environ.pop(_var, None)

os.environ.setdefault("CSEYE_PORT", "8766")
# Where the "Models" browser looks for .EDB files if not overridden. The primary
# workflow is "Attach open model", which needs no roots; adjust for browsing.
os.environ.setdefault("CSEYE_ROOTS", str(Path.home()))

from cseye_bridge import config  # noqa: E402  (import after env is set)


def _open_when_up() -> None:
    url = f"http://{config.HOST}:{config.PORT}/"
    for _ in range(160):                         # wait up to ~40s for the server
        try:
            with socket.create_connection((config.HOST, config.PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.25)
    webbrowser.open(url)


if __name__ == "__main__":
    print("CSEYE  ->  http://%s:%s/" % (config.HOST, config.PORT))
    print("A browser tab will open shortly. Keep this window open; close it to stop CSEYE.")
    threading.Thread(target=_open_when_up, daemon=True).start()
    import uvicorn
    uvicorn.run("cseye_bridge.main:app", host=config.HOST, port=config.PORT, reload=False)

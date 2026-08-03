"""Dev entry point:  python run.py   ->  http://127.0.0.1:8765
Loads bridge/.env (if present) before importing config."""
import os
from pathlib import Path


def _load_env():
    p = Path(__file__).with_name(".env")
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

import uvicorn                       # noqa: E402
from cseye_bridge import config      # noqa: E402

if __name__ == "__main__":
    print(f"CSEYE bridge  ->  http://{config.HOST}:{config.PORT}   (docs at /docs)")
    print(f"  roots   : {[str(r) for r in config.ROOTS]}")
    print(f"  db      : {config.DB_PATH}")
    print(f"  publish : {'ON' if config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY else 'off (set SUPABASE_URL/SUPABASE_SERVICE_KEY)'}")
    uvicorn.run("cseye_bridge.main:app", host=config.HOST, port=config.PORT, reload=False)

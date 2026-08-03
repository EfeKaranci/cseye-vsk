"""Bridge configuration: browsable roots, ETABS executables, DB + server."""
import os
from pathlib import Path

# Roots the model browser is allowed to traverse (scoped — no arbitrary disk access).
ROOTS = [Path(p) for p in os.environ.get("CSEYE_ROOTS", r"C:\Analysis").split(";") if p]

# Known ETABS executables (newest first) for launching a fresh instance.
ETABS_EXES = [
    r"C:\Program Files\Computers and Structures\ETABS 23\ETABS.exe",
    r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe",
    r"C:\Program Files\Computers and Structures\ETABS 21\ETABS.exe",
]

DB_PATH = Path(os.environ.get("CSEYE_DB", Path.home() / ".cseye" / "cseye.db"))
HOST = os.environ.get("CSEYE_HOST", "127.0.0.1")
PORT = int(os.environ.get("CSEYE_PORT", "8765"))

# Allowed browser origins (viewer). Localhost dev + the hosted viewer later.
CORS_ORIGINS = os.environ.get(
    "CSEYE_CORS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8765"
).split(",")

UNITS_KIP_FT = 4  # ETABS eUnits: kip, ft, F

# --- Supabase publish (Phase 3). Set these in the environment to enable /publish. ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")            # https://<ref>.supabase.co
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")  # service_role key (bridge only, never the browser)
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "cseye") # public Storage bucket
SHARE_VIEWER_URL = os.environ.get("CSEYE_SHARE_URL", "")     # Cloudflare Pages URL of the share viewer

# Default "curated governing" set hints (used when a model has these; else all finished).
CURATED_COMBO_HINTS = [
    "ENVELOPE", "ENV", "ULS-2", "1.4D", "1.2D", "ASD", "SEISM", "WIND", "W_USER",
]

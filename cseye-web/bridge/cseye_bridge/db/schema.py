"""SQLite schema (normalized, query-on-demand). Frames carry inline coords so a
per-level slice is a single indexed table scan — no point join needed."""
import sqlite3
from .. import config

DDL = """
CREATE TABLE IF NOT EXISTS snapshot(
  id TEXT PRIMARY KEY, path TEXT, model TEXT, etabs_ver TEXT, units TEXT,
  extents TEXT, locked INTEGER, created_at TEXT
);
CREATE TABLE IF NOT EXISTS story(
  sid TEXT, name TEXT, elev REAL
);
CREATE TABLE IF NOT EXISTS grid_line(
  sid TEXT, gid TEXT, dir TEXT, x1 REAL, y1 REAL, x2 REAL, y2 REAL, visible INTEGER
);
CREATE TABLE IF NOT EXISTS frame(
  sid TEXT, name TEXT, label TEXT, story TEXT, type TEXT,
  ix REAL, iy REAL, iz REAL, jx REAL, jy REAL, jz REAL, section TEXT
);
CREATE TABLE IF NOT EXISTS result_set(
  sid TEXT, name TEXT, kind TEXT, finished INTEGER
);
CREATE TABLE IF NOT EXISTS column_force(
  sid TEXT, result_set TEXT, frame TEXT,
  pmin REAL, pmax REAL, v2 REAL, v3 REAL, m2 REAL, m3 REAL,
  PRIMARY KEY (sid, result_set, frame)
);
CREATE TABLE IF NOT EXISTS reaction(
  sid TEXT, result_set TEXT, joint TEXT, x REAL, y REAL, z REAL,
  fx REAL, fy REAL, fz REAL, mx REAL, my REAL, mz REAL,
  PRIMARY KEY (sid, result_set, joint)
);
CREATE INDEX IF NOT EXISTS ix_frame_slice ON frame(sid, story, type);
CREATE INDEX IF NOT EXISTS ix_cf_slice ON column_force(sid, result_set);
CREATE INDEX IF NOT EXISTS ix_rx_slice ON reaction(sid, result_set);
"""


def connect() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(DDL)
    return con

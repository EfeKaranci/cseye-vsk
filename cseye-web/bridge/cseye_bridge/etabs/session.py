"""
Single-thread ETABS COM session. All OAPI calls run on one dedicated thread
(COM is STA / single-threaded-apartment), serialized via a 1-worker executor.
Endpoints submit callables through `run(fn)`; the model is never saved.
"""
from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Optional

from .. import config


class EtabsSession:
    def __init__(self) -> None:
        self._ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="etabs")
        self._sm = None
        self._path: Optional[str] = None
        self._ex.submit(self._init_com).result()

    # --- runs on the worker thread ---
    def _init_com(self):
        try:
            import comtypes
            comtypes.CoInitialize()
        except Exception:
            pass

    def _helper(self):
        import comtypes.client
        h = comtypes.client.CreateObject("ETABSv1.Helper")
        return h.QueryInterface(comtypes.gen.ETABSv1.cHelper)

    # --- public (thread-safe) API ---
    def run(self, fn: Callable[[Any], Any]) -> Any:
        """Execute fn(SapModel) on the ETABS thread and return its result."""
        def work():
            if self._sm is None:
                raise RuntimeError("No ETABS model attached. Call attach or open first.")
            return fn(self._sm)
        return self._ex.submit(work).result()

    def attach(self) -> dict:
        def work():
            obj = self._helper().GetObject("CSI.ETABS.API.ETABSObject")
            if obj is None:
                raise RuntimeError("No running ETABS instance found. Open a model in ETABS first.")
            self._sm = obj.SapModel
            self._sm.SetPresentUnits(config.UNITS_KIP_FT)
            self._path = self._sm.GetModelFilename()
            return self._status()
        return self._ex.submit(work).result()

    def open(self, path: str) -> dict:
        def work():
            exe = next((e for e in config.ETABS_EXES if os.path.exists(e)), None)
            if not exe:
                raise RuntimeError("No ETABS executable found.")
            obj = self._helper().CreateObject(exe)
            obj.ApplicationStart()
            self._sm = obj.SapModel
            self._sm.InitializeNewModel()
            ret = self._sm.File.OpenFile(path)
            if ret != 0:
                raise RuntimeError(f"OpenFile failed (ret={ret})")
            self._sm.SetPresentUnits(config.UNITS_KIP_FT)
            self._path = self._sm.GetModelFilename()
            return self._status()
        return self._ex.submit(work).result()

    def _status(self) -> dict:
        cst = self._sm.Analyze.GetCaseStatus()
        finished = sum(1 for s in cst[2] if s == 4)
        return {
            "path": self._path,
            "model": os.path.basename(self._path) if self._path else None,
            "etabs_version": self._sm.GetVersion()[0],
            "locked": bool(self._sm.GetModelIsLocked()),
            "cases_total": cst[0],
            "cases_finished": finished,
        }

    def status(self) -> Optional[dict]:
        if self._sm is None:
            return None
        try:
            return self._ex.submit(self._status).result()
        except Exception:
            # ETABS was closed / the COM object went stale → drop it so /health
            # stays healthy ("connected, no model") and the user can re-attach.
            self._sm = None
            self._path = None
            return None


# Process-wide singleton (one ETABS connection per bridge).
_session: Optional[EtabsSession] = None


def get_session() -> EtabsSession:
    global _session
    if _session is None:
        _session = EtabsSession()
    return _session

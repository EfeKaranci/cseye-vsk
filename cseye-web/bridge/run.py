"""Dev entry point:  python run.py   ->  http://127.0.0.1:8765"""
import uvicorn
from cseye_bridge import config

if __name__ == "__main__":
    print(f"CSEYE bridge  ->  http://{config.HOST}:{config.PORT}   (docs at /docs)")
    print(f"  roots : {[str(r) for r in config.ROOTS]}")
    print(f"  db    : {config.DB_PATH}")
    uvicorn.run("cseye_bridge.main:app", host=config.HOST, port=config.PORT, reload=False)

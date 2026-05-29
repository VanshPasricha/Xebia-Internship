"""Root-level backend entrypoint for uvicorn and direct Python execution."""

from __future__ import annotations

import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_api.app.main import app


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("FACETRACK_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("FACETRACK_SERVER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)

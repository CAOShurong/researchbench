"""Put this checkout's src/ first on PYTHONPATH.

A different researchbench install may already be on site-packages. CLI tests
that spawn `python -m researchbench` inherit this environment so they hit
the local tree instead of the other install.
"""

from __future__ import annotations

import os
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = str(_SRC) if not _existing else str(_SRC) + os.pathsep + _existing

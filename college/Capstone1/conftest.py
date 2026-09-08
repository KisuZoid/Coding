"""Add the repository root to ``sys.path`` so ``apps.*`` and ``ml.*`` imports
resolve when pytest is invoked directly (not only via ``python -m pytest``)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

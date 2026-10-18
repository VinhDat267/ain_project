"""Pytest configuration ensuring PROJECT_ROOT is on sys.path.

Contract: INTERFACE.md section 1:
"Entry point (app, script, test) thêm PROJECT_ROOT vào sys.path, rồi import qua package starter".
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

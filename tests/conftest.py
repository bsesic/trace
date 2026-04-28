"""Shared pytest fixtures."""

import sys
from pathlib import Path

# Prepend src/ so the trace package takes precedence over stdlib trace.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

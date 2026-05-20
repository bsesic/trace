"""Sphinx configuration for the TRACE documentation."""

from __future__ import annotations

import importlib.metadata

project = "TRACE"
author = "Benjamin Schnabel"
copyright = "2026, Benjamin Schnabel"

try:
    release = importlib.metadata.version("tracealign")
except importlib.metadata.PackageNotFoundError:
    release = "0.0.0"

version = ".".join(release.split(".")[:2])

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
    "smartquotes",
    "tasklist",
]
myst_heading_anchors = 3

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "superpowers/**",
    "ROADMAP.md",
]

html_theme = "furo"
html_title = f"TRACE {release}"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

autodoc_typehints = "description"
autodoc_member_order = "bysource"

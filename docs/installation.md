# Installation

## Requirements

- Python 3.10, 3.11, or 3.12
- A platform that NumPy and lxml ship wheels for (Linux x86_64, macOS, Windows — all standard)

## From PyPI

```bash
pip install tracealign
```

This pulls the runtime dependencies automatically:

| Dependency | Why |
|---|---|
| `pydantic` (≥ 2.13) | Token / Match / AlignmentResult model + JSON round-trip |
| `numpy` (≥ 2.0) | DP matrix storage for the aligner |
| `lxml` (≥ 5.0) | TEI XML importer |
| `rapidfuzz` (≥ 3.10) | Fast string ratio for the ORTHOGRAPHIC scoring tier |

## From source

For unreleased features or to hack on TRACE itself:

```bash
git clone https://github.com/bsesic/trace.git
cd trace
pip install -e ".[dev]"
```

The `dev` extra adds `pytest` and `flake8`, which are required for the project's quality gates.

## Verifying the install

```bash
python -c "import tracealign; print(tracealign.__version__, tracealign.list_languages())"
```

You should see something like `0.1.2 ['hbo']`. The Hebrew pack registers itself on import.

## Running the tests

After the editable install:

```bash
pytest -q
flake8 src/ tests/
```

The full suite runs in well under one second on modern hardware.

## Optional: building the docs locally

```bash
pip install sphinx furo myst-parser
sphinx-build -W -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser.

# TRACE

**Textual Reuse, Alignment, and Collation Engine** — a Python library for philological alignment with pluggable language packs. Pairwise (v0.1) and simultaneous multi-witness (v0.2) alignment.

[![CI](https://github.com/bsesic/trace/actions/workflows/workflow.yml/badge.svg)](https://github.com/bsesic/trace/actions/workflows/workflow.yml)
[![PyPI version](https://img.shields.io/pypi/v/tracealign.svg)](https://pypi.org/project/tracealign/)
[![Python versions](https://img.shields.io/pypi/pyversions/tracealign.svg)](https://pypi.org/project/tracealign/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation Status](https://readthedocs.org/projects/tracealign/badge/?version=latest)](https://tracealign.readthedocs.io/en/latest/)
[![DOI](https://zenodo.org/badge/1222456359.svg)](https://doi.org/10.5281/zenodo.20315408)

TRACE is designed for textual criticism, manuscript witness comparison, and the creation of digital synopses and critical editions. The core is language-agnostic; the first shipped language pack covers Biblical and Rabbinic Hebrew (`hbo`).

---

## Highlights

- **Tokenizer pipeline** with editorial-marker awareness (`[reconstructed]`, `⟦deletion⟧`, `〈insertion〉`, `(expanded)`, lacunae).
- **Tiered scoring** returning `(score, reason)` per token pair — `EXACT`, `NIQQUD_STRIPPED`, `PLENE_DEFECTIVE`, `ABBREVIATION`, `ORTHOGRAPHIC`, `INSERTION`, `OMISSION`, `NO_MATCH`.
- **Pairwise aligner** — semi-global Needleman–Wunsch with affine gap penalties (Gotoh) and a multi-token abbreviation lookahead (`ר"י` ↔ `רבי ישמעאל`).
- **Multi-witness aligner** (v0.2) — N witnesses aligned simultaneously into a canonical variant graph (DAG) plus a derived aligned table view, via pairwise distances → UPGMA guide tree → POA-based progressive merge. Determinism is pinned by a permutation-invariance property test; correctness by a lossless-reconstruction property test.
- **Hebrew language pack** with niqqud strip, plene/defective skeleton matching, gershayim/maqqef tokenizer hooks, and a seed lexicon of rabbinic abbreviations (extendable via `Lexica.merge()`).
- **I/O** for plain text, JSON (round-trip for both pairwise and multi-witness results), eScriptorium exports, TEI XML, and Sefaria's public API (`tracealign.io.sefaria.load_versions`).
- **Reproducible** — every `AlignmentResult` / `MultiAlignmentResult` carries `trace_version` and `language_pack_version` in its params.

## Installation

```bash
pip install tracealign
```

Requires Python 3.10, 3.11, or 3.12. Pulls `pydantic`, `numpy`, `lxml`, and `rapidfuzz`.

### From source

```bash
git clone https://github.com/bsesic/trace.git
cd trace
pip install -e ".[dev]"
```

The `dev` extra adds `pytest` and `flake8` (the project's quality gates). For documentation contributions, use `pip install -e ".[docs]"` to add Sphinx, furo, and myst-parser.

### Verifying the install

```bash
python -c "import tracealign; print(tracealign.__version__, tracealign.list_languages())"
```

Should print the current version and `['hbo']` (the Hebrew language pack registers itself on import).

## Quick start — pairwise

```python
import tracealign

w1 = tracealign.tokenize("שלום עולם רַבִּי דויד ר\"י אמר", lang="hbo", seq_label="W1")
w2 = tracealign.tokenize("שלום עולם רבי דוד רבי ישמעאל אמר", lang="hbo", seq_label="W2")

result = tracealign.align(w1, w2, lang="hbo")

print(f"total score: {result.total_score:.2f}")
print(f"summary: {dict(result.summary)}")
for m in result.matches:
    a = m.token_a.text if m.token_a else "—"
    b = m.token_b.text if m.token_b else "—"
    print(f"  {a:>10} ↔ {b:<10}  {m.reason.value:<18} {m.score:.2f}")
```

Output (abridged):

```
total score: 0.91
summary: {EXACT: 3, NIQQUD_STRIPPED: 1, PLENE_DEFECTIVE: 1, ABBREVIATION: 1}
       שלום ↔ שלום        exact              1.00
       עולם ↔ עולם        exact              1.00
      רַבִּי ↔ רבי         niqqud_stripped    0.95
       דויד ↔ דוד          plene_defective    0.85
        ר"י ↔ רבי          abbreviation       0.85   (primary)
        ר"י ↔ ישמעאל       abbreviation       0.00   (continuation)
        אמר ↔ אמר          exact              1.00
```

## Quick start — multi-witness (v0.2)

```python
import tracealign

witnesses = {
    "W1": tracealign.tokenize("שלום עולם רַבִּי דויד אמר",  lang="hbo", seq_label="W1"),
    "W2": tracealign.tokenize("שלום עולם רבי דוד אמר",       lang="hbo", seq_label="W2"),
    "W3": tracealign.tokenize("שלום עולם ר\"י אמר",          lang="hbo", seq_label="W3"),
    "W4": tracealign.tokenize("שלום עולם רבי דוד אמר טוב",   lang="hbo", seq_label="W4"),
}

result = tracealign.align_multi(witnesses, lang="hbo")

print(result.guide_tree.format_text())
print(result.table.format_text())

for node in result.graph.variants():
    readings = {wid: t.text for wid, t in node.tokens.items()}
    print(node.id, readings)
```

The `MultiAlignmentResult` exposes a canonical `VariantGraph` (DAG with witness trails), a derived `AlignedTable` (re-anchorable to any witness for presentation), a `GuideTree` (UPGMA-built, carrying the original distance matrix — useful for downstream stemmatic work), and the same reproducibility-aware `params` snapshot the pairwise aligner produces.

JSON persistence works the same way as the pairwise aligner, in its own module:

```python
from tracealign.io import multi_result as mr_io

mr_io.dump(result, "alignment.json")
restored = mr_io.load("alignment.json")
```

See **[the documentation](https://tracealign.readthedocs.io/en/latest/)** for the full API, more usage examples, the algorithm details, FAQs, and the design rationale.

## Documentation

| Section | What it covers |
|---|---|
| [Installation](https://tracealign.readthedocs.io/en/latest/installation.html) | pip / from source / dev setup / docs build |
| [Usage](https://tracealign.readthedocs.io/en/latest/usage.html) | Tokenize, pairwise align, multi-witness align, work with the result, custom lexica, I/O |
| [Details](https://tracealign.readthedocs.io/en/latest/details.html) | Tokenizer pipeline, scoring tiers, pairwise DP algorithm, multi-witness POA pipeline |
| [FAQ](https://tracealign.readthedocs.io/en/latest/faq.html) | Common questions about scope, language packs, performance, multi-witness semantics |
| [Contributing](https://tracealign.readthedocs.io/en/latest/contributing.html) | Development workflow, TDD discipline, branch model |

## Project status

| | |
|---|---|
| Current PyPI release | 0.1.3 (v0.2.0 in flight on `feature/v0.2-multi-witness`) |
| Roadmap | [docs/ROADMAP.md](docs/ROADMAP.md) — ten-stage long-term vision |
| v0.1 design spec | [docs/superpowers/specs/2026-04-28-trace-v0.1-design.md](docs/superpowers/specs/2026-04-28-trace-v0.1-design.md) |
| v0.2 design spec | [docs/superpowers/specs/2026-05-21-trace-v0.2-multi-witness-design.md](docs/superpowers/specs/2026-05-21-trace-v0.2-multi-witness-design.md) |
| Released stages | 1 (pairwise + Hebrew pack) |
| In progress | 2 (master alignment graph / multi-witness) |
| Future sub-projects | Geniza anchor detection · Text-reuse · Apparatus / critical edition · Cross-tradition Hexapla · Stemmatic reconstruction · Allusion detection · Citation graphs · Reception history |

## Citation

If you use TRACE in academic work, please cite via the [Zenodo concept DOI](https://doi.org/10.5281/zenodo.20315408) (always resolves to the latest archived release) or pick a specific version DOI from the Zenodo record. A `CITATION.cff` is at the repo root — GitHub's "Cite this repository" button generates APA / BibTeX / RIS automatically from it.

## License

[MIT](LICENSE) © 2026 Benjamin Schnabel.

# TRACE

**Textual Reuse, Alignment, and Collation Engine** — a Python library for pairwise philological alignment with pluggable language packs.

[![CI](https://github.com/bsesic/trace/actions/workflows/workflow.yml/badge.svg)](https://github.com/bsesic/trace/actions/workflows/workflow.yml)
[![PyPI version](https://img.shields.io/pypi/v/tracealign.svg)](https://pypi.org/project/tracealign/)
[![Python versions](https://img.shields.io/pypi/pyversions/tracealign.svg)](https://pypi.org/project/tracealign/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation Status](https://readthedocs.org/projects/tracealign/badge/?version=latest)](https://tracealign.readthedocs.io/en/latest/)

TRACE is designed for textual criticism, manuscript witness comparison, and the creation of digital synopses and critical editions. The core is language-agnostic; the first shipped language pack covers Biblical and Rabbinic Hebrew (`hbo`).

---

## Highlights

- **Tokenizer pipeline** with editorial-marker awareness (`[reconstructed]`, `⟦deletion⟧`, `〈insertion〉`, `(expanded)`, lacunae).
- **Tiered scoring** returning `(score, reason)` per token pair — `EXACT`, `NIQQUD_STRIPPED`, `PLENE_DEFECTIVE`, `ABBREVIATION`, `ORTHOGRAPHIC`, `INSERTION`, `OMISSION`, `NO_MATCH`.
- **Semi-global Needleman–Wunsch** with affine gap penalties (Gotoh) and a **multi-token abbreviation lookahead** (`ר"י` ↔ `רבי ישמעאל`).
- **Hebrew language pack** with niqqud strip, plene/defective skeleton matching, gershayim/maqqef tokenizer hooks, and a seed lexicon of rabbinic abbreviations (extendable via `Lexica.merge()`).
- **I/O** for plain text, JSON (round-trip), eScriptorium exports (with bbox + line metadata), and TEI XML (`<tei:w>` mode + flow-text fallback).
- **Reproducible** — every `AlignmentResult` carries `trace_version` and `language_pack_version` in its params.

## Installation

```bash
pip install tracealign
```

Requires Python 3.10+. Pulls `pydantic`, `numpy`, `lxml`, and `rapidfuzz`.

## Quick start

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

See **[the documentation](https://tracealign.readthedocs.io/en/latest/)** for installation details, the full API, FAQs, and the design rationale.

## Documentation

| Section | What it covers |
|---|---|
| [Installation](https://tracealign.readthedocs.io/en/latest/installation.html) | pip / from source / dev setup |
| [Usage](https://tracealign.readthedocs.io/en/latest/usage.html) | Tokenize, align, work with the result, custom lexica |
| [Details](https://tracealign.readthedocs.io/en/latest/details.html) | Tokenizer pipeline, scoring tiers, DP algorithm |
| [FAQ](https://tracealign.readthedocs.io/en/latest/faq.html) | Common questions about scope, language packs, performance |
| [Contributing](https://tracealign.readthedocs.io/en/latest/contributing.html) | Development workflow, TDD discipline, branch model |

## Project status

| | |
|---|---|
| Current release | 0.1.1 |
| Roadmap | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Design spec | [docs/superpowers/specs/2026-04-28-trace-v0.1-design.md](docs/superpowers/specs/2026-04-28-trace-v0.1-design.md) |
| Future sub-projects | Multi-witness master graph · Geniza anchor detection · Text-reuse · Critical edition / apparatus |

## License

[MIT](LICENSE) © 2026 Benjamin Schnabel.

## Citation

If you use TRACE in academic work, please cite the repository — a Zenodo DOI will follow with the first non-pre-release tag.

# TRACE

**Textual Reuse, Alignment, and Collation Engine** — a Python library for pairwise philological alignment with pluggable language packs.

TRACE is built for textual criticism, manuscript witness comparison, and the creation of digital synopses and critical editions. The core is language-agnostic; the first shipped language pack covers Biblical and Rabbinic Hebrew (`hbo`).

## At a glance

- **Tokenizer pipeline** with editorial-marker awareness (`[reconstructed]`, `⟦deletion⟧`, `〈insertion〉`, `(expanded)`, lacunae).
- **Tiered scoring** that returns *(score, reason)* per token pair — `EXACT`, `NIQQUD_STRIPPED`, `PLENE_DEFECTIVE`, `ABBREVIATION`, `ORTHOGRAPHIC`, `INSERTION`, `OMISSION`, `NO_MATCH`.
- **Semi-global Needleman–Wunsch** with affine gap penalties (Gotoh) and a multi-token abbreviation lookahead (`ר"י` ↔ `רבי ישמעאל`).
- **Hebrew language pack** with niqqud strip, plene/defective skeleton matching, gershayim/maqqef tokenizer hooks, and a seed lexicon of rabbinic abbreviations (extendable via `Lexica.merge()`).
- **I/O** for plain text, JSON (round-trip), eScriptorium exports, and TEI XML.
- **Reproducible**: every `AlignmentResult` carries `trace_version` and `language_pack_version` in its params.

## Get going

```{toctree}
:maxdepth: 2
:caption: Documentation

installation
usage
details
faq
contributing
```

## Project status

TRACE is an early-stage research library. v0.1.x ships the pairwise aligner and the Hebrew pack; future sub-projects cover multi-witness master graphs, Geniza fragment anchor detection, text-reuse detection, and apparatus / critical-edition generation. See the [roadmap](https://github.com/bsesic/trace/blob/main/docs/ROADMAP.md) for the long-term plan.

## License

[MIT](https://github.com/bsesic/trace/blob/main/LICENSE) © 2026 Benjamin Schnabel.

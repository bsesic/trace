# TRACE

**Textual Reuse, Alignment, and Collation Engine** — a Python library for philological alignment with pluggable language packs. Pairwise (v0.1) and simultaneous multi-witness (v0.2) alignment.

TRACE is built for textual criticism, manuscript witness comparison, and the creation of digital synopses and critical editions. The core is language-agnostic; the first shipped language pack covers Biblical and Rabbinic Hebrew (`hbo`).

## At a glance

- **Tokenizer pipeline** with editorial-marker awareness (`[reconstructed]`, `⟦deletion⟧`, `〈insertion〉`, `(expanded)`, lacunae).
- **Tiered scoring** that returns *(score, reason)* per token pair — `EXACT`, `NIQQUD_STRIPPED`, `PLENE_DEFECTIVE`, `ABBREVIATION`, `ORTHOGRAPHIC`, `INSERTION`, `OMISSION`, `NO_MATCH`.
- **Pairwise aligner** — semi-global Needleman–Wunsch with affine gap penalties (Gotoh) and a multi-token abbreviation lookahead (`ר"י` ↔ `רבי ישמעאל`).
- **Multi-witness aligner** (v0.2) — N witnesses aligned simultaneously into a canonical variant graph plus a derived aligned table, via pairwise distances → UPGMA guide tree → POA-based progressive merge. Determinism and lossless reconstruction are pinned by property tests.
- **Hebrew language pack** with niqqud strip, plene/defective skeleton matching, gershayim/maqqef tokenizer hooks, and a seed lexicon of rabbinic abbreviations (extendable via `Lexica.merge()`).
- **I/O** for plain text, JSON (round-trip for both pairwise and multi-witness results), eScriptorium exports, and TEI XML.
- **Reproducible**: every `AlignmentResult` / `MultiAlignmentResult` carries `trace_version` and `language_pack_version` in its params.

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

TRACE is an early-stage research library. v0.1.x ships the pairwise aligner and the Hebrew pack; v0.2 adds the multi-witness master alignment graph. Future stages cover Geniza fragment anchor detection, text-reuse detection, apparatus / critical-edition generation, cross-tradition Hexapla-style alignment, stemmatic reconstruction, allusion detection, citation graphs, and multi-millennial reception history. See the [roadmap](https://github.com/bsesic/trace/blob/main/docs/ROADMAP.md) for the long-term ten-stage plan.

## License

[MIT](https://github.com/bsesic/trace/blob/main/LICENSE) © 2026 Benjamin Schnabel.

# TRACE Roadmap

**Last updated:** 2026-05-20
**Current release:** [0.1.3](https://github.com/bsesic/trace/releases/tag/0.1.3) — live on [PyPI](https://pypi.org/project/tracealign/), archived on [Zenodo](https://doi.org/10.5281/zenodo.20315408), documented on [Read the Docs](https://tracealign.readthedocs.io)

This roadmap is in two layers:

1. **Where we are** — the released foundation (v0.1.x).
2. **Where we're going** — the long-term research vision: a complete computational textual criticism platform for theology and Jewish studies.

For the v0.1 design rationale see [`docs/superpowers/specs/2026-04-28-trace-v0.1-design.md`](superpowers/specs/2026-04-28-trace-v0.1-design.md). Each future stage will get its own spec / plan documents alongside it.

---

## v0.1 — Foundation (released 2026-05-20)

**Goal achieved:** Pairwise philological alignment with a Hebrew language pack, tokenizer pipeline, semi-global Needleman–Wunsch with affine gaps and abbreviation-span lookahead, JSON / TEI / eScriptorium I/O, full Read-the-Docs documentation, Zenodo archive.

109 tests passing across Python 3.10 / 3.11 / 3.12; flake8 clean.

Released artefacts:

- [`tracealign` on PyPI](https://pypi.org/project/tracealign/) (0.1.0 / 0.1.1 / 0.1.2 / 0.1.3)
- [Zenodo concept DOI](https://doi.org/10.5281/zenodo.20315408) (always-latest)
- [Sphinx documentation](https://tracealign.readthedocs.io)
- [GitHub Actions CI](https://github.com/bsesic/trace/actions) on every push and PR

---

## Long-term vision: computational textual criticism for theology and Jewish studies

The full ambition spans ten stages, each its own brainstorm → spec → plan → implementation cycle. Stages are listed in roughly the order they unlock subsequent stages; staging numbers are guidance, not strict dependencies.

| # | Stage | Capability it unlocks | Status |
|---|---|---|---|
| 1 | **Pairwise aligner + Hebrew pack** | TRACE v0.1 — paarweise Alignment-Kernel | ✅ released 0.1.3 |
| 2 | **Master alignment graph** | Simultaneous multi-witness alignment (Sifra full witness set, Tanhuma) | planned (v0.2) |
| 3 | **Geniza fragment anchor detection** | Matching small fragments against a large candidate pool (hundreds of Sifra Genizah fragments) | planned |
| 4 | **Text-reuse detection** | Finding recurring phrases and verbatim citations across a corpus (biblical citations in rabbinic literature, recurring rabbinic formulae) | planned |
| 5 | **Apparatus / critical-edition generation** | Producing publication-grade critical editions (lemmas, sigla, Fließtext) directly from alignment output | planned |
| 6 | **Cross-tradition (Hexapla-style)** | MT × LXX × Vulgata × Targume parallel alignment (Strong's-lemma layer first, surface-form cross-script later) | planned |
| 7 | **Stemmatic reconstruction** | Inferring the genealogical tree of witnesses from alignment output; phylogenetic-network support for contaminated traditions | planned |
| 8 | **Allusion + echo detection** | Non-verbatim citation detection via semantic similarity (Pesher exegesis, NT-OT allusions, midrashic reformulation) | planned |
| 9 | **Cross-genre citation graphs** | Tracking how the same source is cited across Sifra, Tosefta, Yerushalmi, Bavli, Tanhuma, medieval commentaries — a citation graph spanning the rabbinic corpus | planned |
| 10 | **Multi-millennial reception history** | A reception-history graph for individual biblical verses across MT → LXX → Targum → Pesher → NT → patristic → rabbinic → medieval → modern exegesis | planned (vision crown) |

### Language packs

| Pack | Status | Unlocks |
|---|---|---|
| Hebrew (`hbo`) | ✅ released 0.1.3 | Sifra, Mishna, Tanhuma, Hebrew Bible (MT) |
| Aramaic (`arc`) | planned | Targumim, Talmud Bavli/Yerushalmi, Qumran (mixed corpora), Biblical Aramaic |
| Greek (`grc`) | planned | LXX, NT, patristic |
| Latin (`lat`) | planned | Vulgata, patristic, scholastic |
| Arabic (`ara`) | possible | broader Semitic studies, Judaeo-Arabic texts |
| Persian (`fas`) | possible | Judaeo-Persian, broader Iranian Jewish texts |

### Corpus importers

| Importer | Status |
|---|---|
| Plaintext | ✅ |
| JSON (round-trip) | ✅ |
| eScriptorium JSON | ✅ |
| TEI XML | ✅ |
| Sefaria API | planned |
| OpenScriptures Hebrew Bible (OSHB) | planned |
| STEPBible | planned |
| SQE (Scripta Qumranica Electronica) | planned |
| Sifra Django backend | planned (long-term, after the core stages stabilise) |

### Short-term mini-demos (do not require new sub-projects)

These bridge v0.1 to the larger sub-projects and produce concrete public artefacts:

- **Sefaria-Mishna pairwise demo** — Kaufmann vs. Vilna of a single mishna, end-to-end through the Hebrew pack.
- **Strong's Hexapla-light** — Genesis 1:1 in MT / LXX / Vulgata / Onkelos, lemma-aligned via Strong's numbers (no new packs needed).
- **Text-reuse mini-spike** — Tanakh citations in Mishna Berakhot 1, via a naïve n-gram index plus the existing aligner as a verifier.

---

## Branch model

| Branch | Role |
|---|---|
| `main` | Stable releases. Updated only via merge from `develop` when a release is cut. Tags are cut here (`0.1.0`, `0.1.1`, `0.1.2`, `0.1.3`, ...). |
| `develop` | Integration branch with the latest development work. |
| `feature/<topic>` | Branched off `develop`, merged back into `develop` via PR. |
| `release/<version>` | Short-lived branch for cherry-picking changes into a tagged release. |

Pull requests target `develop`.

## Quality gates

Every commit must pass before merge:

1. **Linting** — `flake8 src/ tests/` reports zero issues.
2. **Tests** — full pytest suite passes locally and on the GitHub Actions matrix (Python 3.10, 3.11, 3.12).

No commits with AI-assistant attribution in commit messages, PR descriptions, or any shipping artefact.

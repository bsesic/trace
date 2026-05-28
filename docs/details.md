# Details

This page describes how TRACE works under the hood — the tokenizer pipeline, the scoring model, and the alignment DP. Read this if you want to extend a language pack, change scoring tiers, or debug an unexpected alignment.

## Architectural overview

```
text (str)
   │
   ▼
┌─────────────────────────────────┐
│ tokenize/plaintext.pretokenize  │   language-agnostic
│  - NFC                          │
│  - editorial bracket scan       │
│  - whitespace + punctuation split │
│  - marker reattach              │
└─────────────────────────────────┘
   │ list[RawToken]
   ▼
┌─────────────────────────────────┐
│ pack.post_tokenize              │   language-specific
│  (Hebrew: split maqqef compounds)│
└─────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────┐
│ pack.normalize                  │   language-specific
│  (Hebrew: niqqud strip, skeleton, │
│   detect abbreviation candidates) │
└─────────────────────────────────┘
   │ list[Token]
   ▼
   ↪ public API tracealign.tokenize()
     overrides id / position with
     sequence-index keyed by seq_label
```

Two Token sequences then feed into the aligner:

```
seq_a, seq_b
   │
   ▼
┌─────────────────────────────────┐
│ align/needleman_wunsch          │
│  - tiered_score per cell        │
│  - Gotoh DP (M / X / Y)         │
│  - abbreviation-span lookahead   │
│  - semi-global edges            │
│  - backtrace + continuation     │
└─────────────────────────────────┘
   │
   ▼
AlignmentResult
```

## Token model

`Token` is a Pydantic model with `extra="forbid"`. Fields:

| Field | Meaning |
|---|---|
| `id` | Stable identifier `{seq_label}:{position:06d}`, e.g. `W1:000003`. |
| `position` | Index in the token sequence (0-based). |
| `raw` | Original surface form, niqqud and editorial markers preserved. |
| `text` | Normalized form (niqqud stripped for Hebrew). |
| `representations` | Dict of alternative forms — Hebrew adds `"skeleton"` (yod/waw also removed). |
| `flags` | Free-form set of strings (`abbreviation`, `compound_part`, `lacuna`, editorial markers like `reconstructed`/`deletion`/`insertion`/`abbreviation_expanded`). |
| `source_span` | `(start, end)` byte offsets into the original text — for round-tripping back to scans / TEI markup. |
| `metadata` | Dict for I/O-specific extras (`witness_id`, `surface_label`, `line_pk`, `bbox`, `abbrev_candidates`, …). |

`flags` is deliberately a `set[str]`, not an enum — language packs and project-specific tooling can attach their own labels without needing a core change.

## The tokenizer pipeline

### Stage 1 — NFC normalization

Every input is `unicodedata.normalize("NFC", text)` before anything else. This canonicalises composed vs decomposed forms so a niqqud-bearing Hebrew letter compares equal regardless of how the source encoded it.

### Stage 2 — Editorial-marker scan

The default `EditorialBracketRules` matches:

| Surface | Resulting flag |
|---|---|
| `[content]` | `reconstructed` |
| `⟦content⟧` | `deletion` |
| `〈content〉` | `insertion` |
| `(content)` | `abbreviation_expanded` |
| `…`, `[…]` | `lacuna` (as a zero-content token) |

The brackets themselves are removed from the surface text; the inner content tokenizes normally but each resulting token inherits the bracket's flag.

You can override the rules:

```python
from tracealign.tokenize.base import EditorialBracketRules

my_rules = EditorialBracketRules(
    pairs=[("{", "}", "deletion"), ("⟨", "⟩", "insertion")],
    lacuna_markers=["...", "…"],
)
tokens = tracealign.tokenize(text, lang="hbo", rules=my_rules)
```

### Stage 3 — Whitespace / punctuation split

Splits on whitespace and on a default punctuation set (`,.;:!?،؛`). A language pack contributes `mid_word_chars` that are *not* split — Hebrew adds gershayim, geresh, and maqqef. A character is otherwise considered word-internal if its Unicode category starts with `L`, `N`, or `M`.

### Stage 4 — Marker reattach

The editorial flags from stage 2 are attached to whichever tokens overlap the corresponding bracket span.

### Stage 5 — Language-pack `post_tokenize`

The Hebrew pack splits maqqef compounds into separate `RawToken` parts here, each tagged with `compound_part`.

### Stage 6 — Language-pack `normalize`

Turns each `RawToken` into a `Token`. The Hebrew pack:

- strips niqqud / te'amim from `raw` to produce `text`;
- computes the `skeleton` representation (text with yod / waw also removed) — used for plene/defective matching;
- flags tokens containing gershayim as `abbreviation`;
- looks up `text` in the lexicon's abbreviation table and attaches the expansions to `metadata["abbrev_candidates"]`.

## Scoring

Scoring is **tiered**: tiers are tried in order, and the first one that returns a non-`None` `TierResult` wins. The result becomes a `Match(reason, score, details)`.

The Hebrew pack ships seven tiers in this order:

| Order | Reason | When it fires | Score |
|---|---|---|---|
| 1 | `EXACT` | `a.raw == b.raw` | 1.00 |
| 2 | `NIQQUD_STRIPPED` | `a.text == b.text` but `a.raw != b.raw` | 0.95 |
| 3 | `PLENE_DEFECTIVE` | same skeleton, differ by exactly one yod/waw | 0.85 |
| 4 | `ABBREVIATION` | 1:1 abbreviation expansion (`ר"ש` ↔ `שמעון` style) | 0.85 |
| 5 | `ORTHOGRAPHIC` | rapidfuzz ratio ≥ 0.6 | ratio × 0.9 |
| — | `NO_MATCH` | none of the above | 0.00 |

`INSERTION` and `OMISSION` are not scoring tiers — they're emitted by the aligner when it inserts a gap in one of the sequences. `SCRIPT_VARIANT` is reserved for future cross-script use (e.g. Hebrew ↔ Greek transliteration).

Multi-token abbreviation matches (`ר"י` ↔ `רבי ישמעאל`) are *not* a tier — they're a separate transition in the DP (see below).

## The alignment DP

TRACE uses a **semi-global Needleman–Wunsch with affine gap penalties (Gotoh)** plus a fourth optional transition for multi-token abbreviation lookahead. Three NumPy matrices store the running scores:

| Matrix | Meaning |
|---|---|
| `M[i, j]` | best score ending with `a[i-1]` aligned to `b[j-1]` |
| `X[i, j]` | best score ending with a gap in B (`a[i-1]` consumed against a gap) |
| `Y[i, j]` | best score ending with a gap in A (`b[j-1]` consumed against a gap) |

`gap_open` is the penalty for *opening* a gap; `gap_extend` is the per-position cost of continuing one. Defaults: `gap_open=-2.0`, `gap_extend=-0.5`.

**Semi-global edges**: by default the first and last column / row are free (`X[i, 0] = 0`, `Y[0, j] = 0`). This means leading and trailing gaps don't cost anything — important for fragment alignment where one witness is a strict subset of the other.

**Abbreviation lookahead** (the fourth transition, `A`): when `a[i-1]` is flagged as an `abbreviation` and a span `b[j-k..j]` matches one of its known expansions, the cell can transition directly from `(i-1, j-k)` to `(i, j)` with the `ABBREVIATION`-tier score (0.85). The traceback emits one primary `Match` plus *k − 1* continuation matches so the output stays 1:1 to consumed tokens. Continuations carry `details["role"] = "continuation"` and a `primary_index` pointer.

The traceback chooses the best of M[m, n], X[m, n], Y[m, n] (or, in semi-global mode, the best value along the bottom row / right column). Tokens left over after the chosen traceback start are appended as `INSERTION` (rim of A) or `OMISSION` (rim of B) without DP penalty.

## Reproducibility

`AlignmentResult.params` contains:

- the input config (`gap_open`, `gap_extend`, `abbrev_lookahead`, `abbrev_max_span`, `semi_global_a/b`);
- the language pack code and its `version` string;
- `trace_version` (the installed package version).

This is sufficient to reproduce any alignment from the same inputs.

## Package layout

```
src/tracealign/
  __init__.py            # public API: tokenize, align, get_language, list_languages, register_language
  model.py               # Token, Match, AlignmentResult, Lexica, Reason
  tokenize/
    base.py              # RawToken, EditorialBracketRules
    plaintext.py         # the 4-stage language-agnostic pretokenizer
  lang/
    base.py              # LanguagePack ABC, ScoringTier, TierResult
    registry.py          # register_language, get_language, list_languages
    hebrew/
      pack.py            # HebrewLanguagePack
      tokenize.py        # gershayim mid-word, maqqef split
      normalize.py       # niqqud strip, skeleton
      scoring.py         # the five tier predicates
      data/              # seed JSON lexica
  score/
    tiered.py            # generic tier-walk function
  align/
    needleman_wunsch.py  # Gotoh DP + abbreviation lookahead
  io/
    result.py            # AlignmentResult JSON dump/load
    escriptorium.py      # eScriptorium JSON importer
    tei.py               # TEI XML importer
```

## Multi-witness alignment (v0.2)

`align_multi` extends the pairwise aligner to N witnesses. The pipeline is three-phase:

### Phase 1 — Pairwise distances

Every pair of witnesses is aligned with `tracealign.align()` (the v0.1 pairwise aligner) and the distance is computed as `1 − total_score`. The result is a symmetric `N × N` distance matrix; the diagonal is zero. Witness ids are sorted lexicographically before computing, making the matrix independent of dict insertion order.

### Phase 2 — UPGMA guide tree

A binary guide tree is built from the distance matrix using **UPGMA** (Unweighted Pair Group Method with Arithmetic Mean). At every iteration the closest cluster pair is merged. Ties are broken on the canonical `(min, max)` lexicographic order of cluster members, guaranteeing determinism. The tree's `height` field carries the cumulative UPGMA distance — a starting point for later stemmatic work.

### Phase 3 — Progressive POA-based merge

The guide tree is walked in post-order to produce a canonical merge sequence (closely-related witnesses are merged first). The first witness seeds the graph as a linear chain. Each subsequent witness is aligned to the current graph via **partial-order alignment (POA)** — a DP over the topologically sorted graph nodes. Three transitions:

| Transition | Effect on graph |
|---|---|
| Match | Merge the new token into an existing node's `tokens[witness_id]`; extend the witness set on the incoming edge. |
| Insertion in sequence (gap in graph) | Add a new node holding only this witness's token; new edge `prev → new`. |
| Deletion (skip graph node) | The new witness's path bypasses this node — recorded by an edge that skips it. |

`node_match_score` aggregates the per-constituent tiered score across the witnesses already in the target node. The default mode `"max"` is permissive (CollateX-aligned); `"mean"` and `"min"` are configurable.

### Correctness guarantees

Two properties are pinned by tests:

- **Lossless reconstruction.** For every input witness `w`, the path through the result graph yields exactly the original token sequence.
- **Permutation invariance.** The same set of witnesses in any input dict order produces the same alignment (same witness paths, same variant loci).

### Data flow

```
align_multi(witnesses, lang, config)
   │
   ▼
pairwise_distances        — Phase 1: O(N²/2) pairwise alignments
   │
   ▼
build_upgma               — Phase 2: deterministic binary tree
   │
   ▼
progressive_merge         — Phase 3: post-order POA-based merge
   │
   ▼
VariantGraph
   │
   ├──► AlignedTable      — derived view, re-anchorable
   └──► MultiAlignmentResult (graph + table + guide_tree + summary + params)
```

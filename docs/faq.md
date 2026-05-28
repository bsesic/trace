# FAQ

## Why is the package on PyPI called `tracealign` but the project is `TRACE`?

The Python standard library already has a [`trace`](https://docs.python.org/3/library/trace.html) module, so `import trace` would have shadowed (or been shadowed by) the stdlib depending on `sys.path` order. The PyPI name and the import path are both `tracealign`; the project itself is still TRACE.

## Does TRACE work for languages other than Hebrew?

The core is language-agnostic — tokenizer, scoring loop, and DP know nothing about Hebrew. Everything Hebrew-specific lives in `tracealign.lang.hebrew`. Adding a new language is one new language pack:

1. Implement a class that subclasses `LanguagePack`.
2. Override `post_tokenize` (optional), `normalize` (required), and `scoring_tiers` (required).
3. Call `register_language(MyPack())` once at import time.

v0.2 candidates include Arabic and Greek packs as reference implementations.

## Why semi-global instead of global or local alignment?

Global Needleman–Wunsch forces both sequences to align edge-to-edge — leading and trailing gaps are penalized like internal ones. That's wrong for textual witnesses where one is a fragment of the other. Local (Smith–Waterman) discards the global structure and looks only for the best matching subsequence, losing the witness-level correspondence we want.

Semi-global is the right middle ground: leading and trailing gaps are free (so a fragment can match a substring of a longer witness), but internal gaps still cost.

## How does the abbreviation lookahead work?

When a token like `ר"י` (Rabbi Ishmael, abbreviated) is flagged as an `abbreviation` and its `metadata["abbrev_candidates"]` contains the expansion `"רבי ישמעאל"`, the DP can consume *two* tokens of the other witness in a single transition with the `ABBREVIATION`-tier score (0.85). The output preserves a 1:1 mapping by emitting one *primary* match plus *k − 1* *continuation* matches; the summary counts only the primary so the abbreviation looks like a single linguistic event.

## How is `total_score` computed?

```
total_score = sum(m.score for m in matches if not continuation) / max(len(seq_a), len(seq_b))
```

Two identical sequences score 1.0. Two completely-unrelated sequences of equal length score 0.0. Continuations don't contribute (their score is 0 by convention so they don't double-count the primary's contribution).

## Is TRACE fast enough for production alignments?

v0.1 targets:

| Size | Target | Memory |
|---|---|---|
| 500 × 500 | < 1 s | well under 50 MB |
| 2 000 × 2 000 | < 30 s | < 200 MB |

These are sanity targets, not gates. The DP inner loop is currently pure Python over NumPy storage. A NumPy-vectorized or Cython implementation is on the v0.2 candidate list if real-world Sifra / Geniza alignments push past the targets.

## How do I extend the Hebrew abbreviation lexicon?

```python
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.lang.registry import register_language
from tracealign.model import Lexica

extra = Lexica(abbreviations={"רמב\"ם": ["רבי משה בן מימון"]})
pack = HebrewLanguagePack()
pack.lexica = pack.lexica.merge(extra)
register_language(pack)
```

`Lexica.merge()` unions abbreviation expansions and dedupes — your additions sit alongside the seed lexicon.

## What about `<choice>`, `<corr>`, `<reg>`, `<expan>` in TEI?

The v0.1 TEI importer reads only `<tei:w>` (each `<w>` is one token) or falls back to flow text. Resolving TEI `<choice>` constructs (pick `<lem>` vs `<rdg>` vs `<orig>` vs `<reg>`, expand `<abbr>` via `<expan>`) is out of scope for v0.1 — that's a feature waiting on user demand.

## Can I use TRACE for plagiarism / text-reuse detection?

Not yet. v0.1 is strict pairwise alignment. **Text-reuse detection** (finding recurring rabbinic formulae, biblical citations, etc., across a corpus) is sub-project #4 in the long-term roadmap and will get its own brainstorming → spec → plan cycle.

## How are alignment results meant to be persisted?

Use the JSON I/O module:

```python
from tracealign.io import result as result_io

result_io.dump(result, "alignment.json")
restored = result_io.load("alignment.json")
```

The resulting file includes the full match list, the summary, both sequence metadata blobs, and the `params` snapshot (`trace_version`, language pack version, gap penalties). That's enough to reconstruct the alignment with the exact same configuration.

## What's the v0.2 outlook?

Not specced yet. Candidates from the v0.1 spec:

- Multi-language packs (Arabic, Greek as reference implementations).
- Learned scoring weights via full feature-vector capture.
- Per-project editorial-bracket preset bundles.
- Performance pass (NumPy vectorization or Cython hot path).

The master alignment graph (multi-witness alignment) shipped as v0.2 — see below. Future long-term stages: Geniza anchor detection, text-reuse, apparatus generation, cross-tradition Hexapla, stemmatic reconstruction, allusion detection, citation graphs, reception history.

## How does multi-witness alignment differ from pairwise?

`tracealign.align()` aligns exactly two witnesses. `tracealign.align_multi()` (v0.2) aligns N witnesses at once into a single canonical structure — a variant graph (DAG) where every witness has a trail through the graph, plus a derived aligned table view. Variant loci surface as nodes whose constituent witnesses disagree.

For two witnesses the two paths give similar information; for three or more the multi-witness graph is much more useful than running every pair separately, because it gives one consistent set of variant positions rather than O(N²) overlapping pairwise alignments.

## Is `align_multi` deterministic?

Yes. The result is independent of the dict insertion order of the witnesses. Three sources of order-stability are pinned by tests:

1. `pairwise_distances` sorts witness ids lexicographically before computing the matrix.
2. UPGMA tie-breaking uses the canonical `(min, max)` lexicographic order of cluster members.
3. The topological sort during sequence-vs-graph alignment is stable with respect to node id.

A dedicated property test (`test_permutation_invariance`) re-runs `align_multi` with reordered inputs and asserts that witness paths and variant loci are identical.

## How big can multi-witness alignments get?

The v0.2 target is Sifra-scale: 5–15 witnesses, 1000–5000 tokens each. Larger witness sets (NT-scale, hundreds of witnesses) need anchor-based decomposition, which is a future stage. Geniza fragments specifically are handled in their own future stage (anchor detection against a large candidate pool), not by adding them all to one master graph.

## Why UPGMA and not Neighbor-Joining for the guide tree?

UPGMA is simpler and gives a binary tree with clear cumulative-distance heights — useful as a draft stemma input for the eventual stemmatic-reconstruction stage. UPGMA's "molecular clock" assumption is a known limitation in phylogenetics but is acceptable for ordering the merge sequence in v0.2. Neighbor-Joining is a future v0.x candidate when proper stemmatic reconstruction goes live.

## Can I add a new witness to an existing alignment incrementally?

Not in v0.2.0 — `align_multi` builds the entire graph in a single call. An incremental "add one witness" API is a v0.2.x candidate; it builds naturally on the existing `align_sequence_to_graph` primitive but requires API design (e.g. should the guide tree be re-balanced? should existing alignment relationships be allowed to change?). Open a discussion or issue if you need this.

## How do I persist a multi-witness result?

```python
from tracealign.io import multi_result as mr_io

mr_io.dump(result, "alignment.json")
restored = mr_io.load("alignment.json")
```

`tracealign.io.multi_result` is a dedicated module separate from `tracealign.io.result` (the pairwise JSON I/O). The round-trip preserves the entire result, including the guide tree's distance matrix — important for later stages that reuse it.

# Usage

## A minimal example

```python
import tracealign

w1 = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
w2 = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2")

result = tracealign.align(w1, w2, lang="hbo")

print(result.total_score)   # 1.0
print(dict(result.summary)) # {EXACT: 2}
```

## Tokenizing

`tracealign.tokenize(text, lang, seq_label=...)` runs the full pipeline (NFC normalization → editorial-marker scan → whitespace/punctuation split → language-pack post-processing → normalization) and returns a `list[Token]`.

The `seq_label` argument is what distinguishes two witnesses — the resulting token IDs start with that label (e.g. `W1:000000`). When you align two sequences they must have different labels or their token IDs will collide.

```python
tokens = tracealign.tokenize(
    "שלום עולם רַבִּי דויד ר\"י אמר",
    lang="hbo",
    seq_label="W1",
)
for t in tokens:
    print(t.id, t.text, t.flags)
```

```{note}
Niqqud (vowel points) and te'amim (cantillation marks) survive into `Token.raw` but are stripped from `Token.text` and from the skeleton form. This lets EXACT match the raw form while NIQQUD_STRIPPED can fall back to the stripped form.
```

## Aligning

```python
result = tracealign.align(seq_a, seq_b, lang="hbo")
```

The returned `AlignmentResult` exposes:

| Field | Description |
|---|---|
| `matches` | List of `Match` objects, 1:1 to consumed tokens. Multi-token abbreviation expansions emit one primary match plus *k − 1* continuation matches. |
| `summary` | `dict[Reason, int]` — count of each Reason. Continuations do not inflate ABBREVIATION. |
| `total_score` | Normalized in `[0, 1]`. Computed as the sum of non-continuation match scores divided by `max(len(seq_a), len(seq_b))`. |
| `seq_a_meta`, `seq_b_meta` | Free-form metadata you pass when calling `align()`. |
| `params` | Snapshot of the config (gap penalties, abbrev settings) plus `trace_version` and `language_pack_version` for reproducibility. |

## Inspecting matches

```python
for m in result.matches:
    a = m.token_a.text if m.token_a else "—"
    b = m.token_b.text if m.token_b else "—"
    print(f"{a:>10} ↔ {b:<10}  {m.reason.value:<18} {m.score:.2f}")
```

`m.details` carries Reason-specific extra information. For ABBREVIATION matches that's `role: "primary"` or `"continuation"`, the `expansion` string (e.g. `"רבי ישמעאל"`), and `span_size`. For ORTHOGRAPHIC matches it's the rapidfuzz ratio.

## I/O

### JSON round-trip

```python
from tracealign.io import result as result_io

result_io.dump(result, "out.json")
restored = result_io.load("out.json")
```

`dumps(result) -> str` and `loads(payload) -> AlignmentResult` are also available for in-memory round-trips.

### eScriptorium JSON exports

```python
from tracealign.io.escriptorium import load as load_escr

tokens = load_escr("witness1.json", lang="hbo")
```

Expects an export with a top-level `witness_id`, a `regions` array whose entries have `label` and a `lines` array, each line carrying `content` plus optional `line_pk` and `bbox`. The eScriptorium-specific fields are preserved on each `Token.metadata` so you can map alignment matches back to scan coordinates.

### TEI XML

```python
from tracealign.io.tei import load as load_tei

a = load_tei("W1.xml", lang="hbo", seq_label="W1")
b = load_tei("W2.xml", lang="hbo", seq_label="W2")
```

If the TEI body contains `<tei:w>` elements, each `<w>` is treated as one token boundary. If it does not, the body's flow text is tokenized through the standard plaintext pipeline.

## Custom lexica

The Hebrew pack ships with a seed lexicon (six rabbinic abbreviations, two plene/defective pairs). You almost certainly want to extend it with project-specific entries:

```python
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.lang.registry import register_language
from tracealign.model import Lexica

extra = Lexica(
    abbreviations={"רמב\"ם": ["רבי משה בן מימון"]},
    plene_defective_pairs=[("ירושלים", "ירושלם")],
)
pack = HebrewLanguagePack()
pack.lexica = pack.lexica.merge(extra)
register_language(pack)  # replaces the auto-registered one
```

`Lexica.merge()` is union-on-conflict — order-preserving deduplication for both abbreviation expansions and plene/defective pairs.

You can also load lexica from JSON files:

```python
lex = Lexica.load({
    "abbreviations": "my_abbrev.json",
    "plene_defective_pairs": "my_plene.json",
})
```

JSON shapes:

```json
{"ר\"י": ["רבי ישמעאל", "רבי יהודה"]}
```

```json
[["דויד", "דוד"], ["משיח", "מאשיח"]]
```

## Configuring the aligner

```python
from tracealign.align import AlignerConfig

cfg = AlignerConfig(
    gap_open=-2.5,
    gap_extend=-0.4,
    abbrev_lookahead=True,
    abbrev_max_span=5,
)
result = tracealign.align(a, b, lang="hbo", config=cfg)
```

Defaults (`gap_open=-2.0`, `gap_extend=-0.5`, `abbrev_max_span=4`, semi-global on both sides) work well for the Hebrew pack out of the box. Adjust if you see persistent gap mis-placements or if your texts use abbreviations that expand to more than four tokens.

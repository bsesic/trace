# Contributing

TRACE is a research library. Contributions are welcome — especially new language packs, fixture corpora, and apparatus-format conversions. This page describes the development workflow.

## Branch model

TRACE follows a `main` / `develop` / feature-branch model:

| Branch | Role |
|---|---|
| `main` | Stable releases. Updated only via merge from `develop`. Never pushed to directly. Tags are cut here (`0.1.0`, `0.1.1`, …). |
| `develop` | Integration branch with the latest development work. |
| `feature/<topic>` | Branched off `develop`, merged back into `develop` via PR. |
| `release/<version>` | Short-lived branch off `main` for cherry-picking patches into a tagged release. |

Pull requests target `develop`, not `main`. The PR description should summarise what changed and link to the relevant spec / plan / issue.

## Quality gates

Every commit must pass before merge:

1. **flake8** — `flake8 src/ tests/` returns no output (PEP 8 compliant).
2. **pytest** — the full suite passes (`pytest -q`).

The GitHub Actions CI runs both on every push and pull request across Python 3.10, 3.11, and 3.12.

## TDD discipline

For new features and bug fixes:

1. **Red** — write a failing test that pins the desired behaviour.
2. **Verify red** — run the test, watch it fail with a meaningful error.
3. **Green** — write the minimal production code that makes the test pass.
4. **Verify green** — run the test, watch it pass; run the full suite, confirm nothing regressed.
5. **Refactor** — clean up while keeping the tests green.

If you're tempted to write the test after the implementation, write the test first instead. Tests-after answer "what does this do?"; tests-first answer "what *should* this do?"

## Commit conventions

Conventional-commit prefixes are encouraged but not enforced:

| Prefix | Use for |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | New tests, no production change |
| `refactor:` | Internal restructure with no behaviour change |
| `chore:` | Build / tooling / dependency / release prep |
| `style:` | Code formatting / whitespace |
| `ci:` | CI configuration |

Commit messages should explain *why* in addition to *what* — the diff already shows the *what*.

**No AI / assistant attribution** in commit messages, PR descriptions, or any shipping artefact. Plain factual summaries only.

## Adding a new language pack

1. Create `src/tracealign/lang/<code>/` with `__init__.py`, `pack.py`, and your normaliser / tokenizer hooks / scoring tiers.
2. Subclass `LanguagePack`. Set `code`, `aliases`, `version`. Override `post_tokenize` (optional), `normalize` (required), `scoring_tiers` (required).
3. Register at import time: `register_language(MyLanguagePack())` in your `__init__.py`.
4. Update `src/tracealign/__init__.py`'s `_BUILTIN_PACK_MODULES` tuple so the test registry-reset helper can reload your pack.
5. Add tests under `tests/lang/<code>/`. The Hebrew pack tests are a useful template.

## Adding to the Hebrew lexicon

The seed lexicon lives in `src/tracealign/lang/hebrew/data/`:

- `abbreviations.json` — `{ "abbrev_form": ["expansion_1", "expansion_2", ...] }`
- `plene_defective.json` — `[["plene_form", "defective_form"], ...]`

Additions to the seed lexicon should be limited to entries that genuinely belong in a *core* Hebrew pack — well-known rabbinic abbreviations, broadly attested plene/defective pairs. Project-specific entries should live in the user's own `Lexica.merge()` call, not in core.

## Working with the design documents

The full design spec lives at `docs/superpowers/specs/2026-04-28-trace-v0.1-design.md`, the v0.1 task breakdown at `docs/superpowers/plans/2026-04-28-trace-v0.1.md`. Both are kept in sync with the code; if a behaviour and the spec disagree, file an issue first.

The roadmap (`docs/ROADMAP.md`) tracks which sub-projects are done, in progress, and queued.

## Reporting bugs

Open an issue at [github.com/bsesic/trace/issues](https://github.com/bsesic/trace/issues). A useful bug report includes:

- The TRACE version (`python -c "import tracealign; print(tracealign.__version__)"`).
- A *minimal* code snippet that reproduces the behaviour.
- What you expected vs what happened.
- The language pack (if applicable) and any custom lexicon.

For alignment-correctness issues, the JSON dump of the offending `AlignmentResult` is the most useful single artefact.

## Asking questions

Use [GitHub Discussions](https://github.com/bsesic/trace/discussions) for design questions, requests for new language packs, and feedback on the abbreviation lexicon. Issues are reserved for things that need a code change.

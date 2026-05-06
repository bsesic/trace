"""Tests for AlignmentResult assembly: summary and total_score."""

from tracealign.align.needleman_wunsch import align as run_align
from tracealign.lang.hebrew.normalize import skeleton
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import AlignmentResult, Reason, Token


def _tok(text: str, position: int, raw: str | None = None, **extra) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=raw if raw is not None else text,
        text=text,
        representations={"skeleton": skeleton(text)},
        **extra,
    )


def _seq(words: list[str]) -> list[Token]:
    return [_tok(w, i) for i, w in enumerate(words)]


def test_identical_sequences_total_score_one():
    a = _seq(["שלום", "עולם"])
    b = _seq(["שלום", "עולם"])
    result = run_align(a, b, pack=HebrewLanguagePack())
    assert isinstance(result, AlignmentResult)
    assert result.total_score == 1.0
    assert result.summary[Reason.EXACT] == 2


def test_summary_counts_each_reason():
    a = _seq(["a", "b", "c"])
    b = _seq(["a", "b", "d"])  # last pair non-exact
    result = run_align(a, b, pack=HebrewLanguagePack())
    assert result.summary[Reason.EXACT] == 2


def test_total_score_normalized_zero_one():
    a = _seq(["a", "b"])
    b = _seq(["c", "d"])
    result = run_align(a, b, pack=HebrewLanguagePack())
    assert 0.0 <= result.total_score <= 1.0


def test_summary_excludes_continuation_matches():
    abbrev = _tok("ר\"י", 0, flags={"abbreviation"}, metadata={"abbrev_candidates": ["רבי ישמעאל"]})
    a = [abbrev]
    b = [_tok("רבי", 0), _tok("ישמעאל", 1)]
    result = run_align(a, b, pack=HebrewLanguagePack())
    # 1 primary; the continuation must not inflate the count.
    assert result.summary.get(Reason.ABBREVIATION, 0) == 1


def test_params_includes_versions_and_config():
    a = _seq(["a"])
    b = _seq(["a"])
    result = run_align(a, b, pack=HebrewLanguagePack())
    assert "trace_version" in result.params
    assert "language_pack_version" in result.params
    assert result.params["language_pack_version"] == "hbo-0.1.0"
    assert result.params["gap_open"] == -2.0
    assert result.params["gap_extend"] == -0.5

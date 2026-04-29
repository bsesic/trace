"""Tests for the language-pack registry."""

import pytest

from tracealign.lang.base import LanguagePack, ScoringTier, TierResult
from tracealign.lang.registry import (
    UnknownLanguageError,
    get_language,
    list_languages,
    register_language,
    _reset_registry_for_tests,
)
from tracealign.model import Reason, Token
from tracealign.tokenize.base import RawToken


class _FakePack(LanguagePack):
    code = "xx"
    aliases = ("fake", "x-test")
    version = "xx-0.0.1"
    word_chars = ""
    mid_word_chars = ""

    def __init__(self):
        from tracealign.model import Lexica
        self.lexica = Lexica()

    def normalize(self, raw: RawToken) -> Token:
        return Token(id=f"x:{raw.span[0]:06d}", position=0, raw=raw.raw, text=raw.raw)

    def scoring_tiers(self) -> list[ScoringTier]:
        return [
            ScoringTier(
                reason=Reason.EXACT,
                predicate=lambda a, b, p: TierResult(score=1.0) if a.raw == b.raw else None,
            )
        ]


@pytest.fixture(autouse=True)
def _reset():
    _reset_registry_for_tests()
    yield
    _reset_registry_for_tests()


def test_register_and_get_by_code():
    pack = _FakePack()
    register_language(pack)
    assert get_language("xx") is pack


def test_register_and_get_by_alias():
    pack = _FakePack()
    register_language(pack)
    assert get_language("fake") is pack
    assert get_language("x-test") is pack


def test_get_language_with_pack_passthrough():
    pack = _FakePack()
    assert get_language(pack) is pack


def test_get_language_unknown_raises():
    with pytest.raises(UnknownLanguageError):
        get_language("zz")


def test_list_languages_returns_codes_only():
    register_language(_FakePack())
    codes = list_languages()
    assert "xx" in codes


def test_re_register_replaces():
    p1 = _FakePack()
    p2 = _FakePack()
    register_language(p1)
    register_language(p2)
    assert get_language("xx") is p2

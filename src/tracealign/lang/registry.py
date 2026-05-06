"""Registry for language packs."""

from __future__ import annotations

from tracealign.lang.base import LanguagePack


class UnknownLanguageError(KeyError):
    pass


_REGISTRY: dict[str, LanguagePack] = {}


def register_language(pack: LanguagePack) -> None:
    _REGISTRY[pack.code] = pack
    for alias in pack.aliases:
        _REGISTRY[alias] = pack


def get_language(code_or_pack: str | LanguagePack) -> LanguagePack:
    if isinstance(code_or_pack, LanguagePack):
        return code_or_pack
    try:
        return _REGISTRY[code_or_pack]
    except KeyError as exc:
        raise UnknownLanguageError(code_or_pack) from exc


def list_languages() -> list[str]:
    return sorted({p.code for p in _REGISTRY.values()})


def _reset_registry_for_tests() -> None:
    """Test helper. Not part of the public API."""
    _REGISTRY.clear()

"""TRACE — Textual Reuse, Alignment, and Collation Engine."""

from __future__ import annotations

import importlib
import sys
from typing import Any

from tracealign.align import AlignerConfig
from tracealign.align import align as _align
from tracealign.lang.base import LanguagePack
from tracealign.lang.registry import (
    UnknownLanguageError,
    get_language as _get_language,
    list_languages as _list_languages,
    register_language,
)
from tracealign.model import AlignmentResult, Lexica, Match, Reason, Token
from tracealign.multi.api import (
    MultiAlignerConfig,
    MultiAlignmentResult,
    align_multi,
)
from tracealign.multi.graph import GraphEdge, GraphNode, VariantGraph
from tracealign.multi.guide_tree import GuideTree, GuideTreeNode
from tracealign.multi.table import AlignedTable, TableCell, TableColumn
from tracealign.tokenize.base import (
    DEFAULT_EDITORIAL_RULES,
    EditorialBracketRules,
    RawToken,
)
from tracealign.tokenize.plaintext import pretokenize

__version__ = "0.3.0.dev0"

# Force Hebrew pack registration on first import.
import tracealign.lang.hebrew  # noqa: F401  -- side effect: registers HBO pack

# Built-in pack module names; used to restore registrations after test resets.
_BUILTIN_PACK_MODULES = ("tracealign.lang.hebrew",)


def _reload_builtin_packs() -> None:
    """Re-register built-in packs if they were cleared (test isolation helper)."""
    for mod_name in _BUILTIN_PACK_MODULES:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])


def get_language(code_or_pack: str | LanguagePack) -> LanguagePack:
    """Return the registered LanguagePack for *code_or_pack*.

    Falls back to reloading built-in packs when the registry was reset (test
    isolation), then retries once before propagating UnknownLanguageError.
    """
    try:
        return _get_language(code_or_pack)
    except UnknownLanguageError:
        _reload_builtin_packs()
        return _get_language(code_or_pack)


def list_languages() -> list[str]:
    """Return sorted list of registered language codes.

    If the registry was cleared (test isolation), built-in packs are reloaded
    automatically before listing.
    """
    codes = _list_languages()
    if not codes:
        _reload_builtin_packs()
        codes = _list_languages()
    return codes


def tokenize(
    text: str,
    lang: str | LanguagePack = "hbo",
    *,
    seq_label: str = "seq",
    rules: EditorialBracketRules | None = None,
) -> list[Token]:
    pack = get_language(lang)
    effective_rules = rules or pack.editorial_rules
    raws = pretokenize(
        text,
        mid_word_chars=pack.mid_word_chars,
        rules=effective_rules,
    )
    raws = pack.post_tokenize(raws)
    tokens: list[Token] = []
    for position, raw in enumerate(raws):
        tok = pack.normalize(raw)
        # Override the pack-assigned ID with the seq_label-based scheme; preserve
        # everything else.
        tokens.append(
            tok.model_copy(
                update={
                    "id": f"{seq_label}:{position:06d}",
                    "position": position,
                }
            )
        )
    return tokens


def align(
    seq_a: list[Token],
    seq_b: list[Token],
    lang: str | LanguagePack = "hbo",
    config: AlignerConfig | None = None,
    seq_a_meta: dict[str, Any] | None = None,
    seq_b_meta: dict[str, Any] | None = None,
) -> AlignmentResult:
    pack = get_language(lang)
    return _align(
        seq_a,
        seq_b,
        pack=pack,
        config=config,
        seq_a_meta=seq_a_meta,
        seq_b_meta=seq_b_meta,
    )


__all__ = [
    "AlignedTable",
    "AlignerConfig",
    "AlignmentResult",
    "DEFAULT_EDITORIAL_RULES",
    "EditorialBracketRules",
    "GraphEdge",
    "GraphNode",
    "GuideTree",
    "GuideTreeNode",
    "LanguagePack",
    "Lexica",
    "Match",
    "MultiAlignerConfig",
    "MultiAlignmentResult",
    "RawToken",
    "Reason",
    "TableCell",
    "TableColumn",
    "Token",
    "UnknownLanguageError",
    "VariantGraph",
    "__version__",
    "align",
    "align_multi",
    "get_language",
    "list_languages",
    "register_language",
    "tokenize",
]

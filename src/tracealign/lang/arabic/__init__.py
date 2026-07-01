"""Arabic language pack — auto-registers on import."""

from tracealign.lang.arabic.pack import ArabicLanguagePack
from tracealign.lang.registry import register_language

register_language(ArabicLanguagePack())

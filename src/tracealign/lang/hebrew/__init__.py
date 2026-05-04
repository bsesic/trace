"""Hebrew language pack — auto-registers on import."""

from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.lang.registry import register_language

register_language(HebrewLanguagePack())

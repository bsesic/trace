"""Arabic normalization: tashkil strip and orthographic skeleton folding."""

from __future__ import annotations

import unicodedata

TATWEEL = "ـ"  # ARABIC TATWEEL (kashida), decorative elongation

# Orthographic folding table applied on top of a tashkil-free string.
# Alif variants -> bare alif; taa marbuta -> haa; alif maqsura -> ya;
# hamza seats -> their carrier letter; bare hamza dropped.
_FOLD = {
    "أ": "ا",  # ALEF WITH HAMZA ABOVE  أ -> ا
    "إ": "ا",  # ALEF WITH HAMZA BELOW  إ -> ا
    "آ": "ا",  # ALEF WITH MADDA ABOVE  آ -> ا
    "ٱ": "ا",  # ALEF WASLA            ٱ -> ا
    "ة": "ه",  # TEH MARBUTA           ة -> ه
    "ى": "ي",  # ALEF MAKSURA          ى -> ي
    "ؤ": "و",  # WAW WITH HAMZA        ؤ -> و
    "ئ": "ي",  # YEH WITH HAMZA        ئ -> ي
    "ء": "",        # HAMZA                 ء -> (dropped)
}


def strip_tashkil(text: str) -> str:
    """NFC-normalize, then remove combining marks (Mn) and tatweel."""
    text = unicodedata.normalize("NFC", text)
    return "".join(
        ch
        for ch in text
        if unicodedata.category(ch) != "Mn" and ch != TATWEEL
    )


def skeleton(text_no_tashkil: str) -> str:
    """Apply orthographic folding to a tashkil-free string."""
    return "".join(_FOLD.get(ch, ch) for ch in text_no_tashkil)

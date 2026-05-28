"""Pairwise distance matrix for multi-witness alignment."""

from __future__ import annotations

import numpy as np

from tracealign.align import AlignerConfig
from tracealign.align import align as pairwise_align
from tracealign.lang.base import LanguagePack
from tracealign.model import Token


def pairwise_distances(
    witnesses: dict[str, list[Token]],
    pack: LanguagePack,
    pairwise_cfg: AlignerConfig,
) -> tuple[np.ndarray, list[str]]:
    """Compute the N x N pairwise distance matrix using v0.1's pairwise aligner.

    Returns the matrix and the canonical witness_id ordering (sorted
    lexicographically) used for rows and columns.
    """
    wids = sorted(witnesses.keys())
    n = len(wids)
    D = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            result = pairwise_align(witnesses[wids[i]], witnesses[wids[j]], pack, pairwise_cfg)
            d = 1.0 - result.total_score
            D[i, j] = d
            D[j, i] = d
    return D, wids

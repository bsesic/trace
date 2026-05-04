"""Semi-global Needleman-Wunsch with affine gaps (Gotoh) and abbreviation lookahead.

This module implements the public alignment kernel. Tasks 11-15 build it up
incrementally: basic global DP, then semi-global edges, then abbrev lookahead,
then summary computation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tracealign.lang.base import LanguagePack
from tracealign.model import Match, Reason, Token
from tracealign.score.tiered import tiered_score


NEG_INF = -1e18


@dataclass
class AlignerConfig:
    gap_open: float = -2.0
    gap_extend: float = -0.5
    semi_global_a: bool = True
    semi_global_b: bool = True
    abbrev_lookahead: bool = True
    abbrev_max_span: int = 4


def _dp_score(score_unit: float) -> float:
    """Map a tier score in [0,1] to the DP scale [-1,+1]."""
    return 2.0 * score_unit - 1.0


def _pair_score(
    a: Token,
    b: Token,
    pack: LanguagePack,
    cache: dict[tuple[str, str], Match],
) -> Match:
    key = (a.id, b.id)
    cached = cache.get(key)
    if cached is None:
        cached = tiered_score(a, b, pack)
        cache[key] = cached
    return cached


def _abbrev_span_score_a_to_b(
    a_tok: Token,
    b_span: list[Token],
) -> tuple[float, str] | None:
    """Return (score, expansion) if any abbrev_candidate matches the span 1:1 by `text`.

    The score is the ABBREVIATION-tier score (0.85), still on the [0, 1] tier scale.
    """
    if "abbreviation" not in a_tok.flags:
        return None
    candidates = a_tok.metadata.get("abbrev_candidates", [])
    span_texts = [t.text for t in b_span]
    for cand in candidates:
        parts = cand.split()
        if parts == span_texts:
            return (0.85, cand)
    return None


def align_sequences(
    seq_a: list[Token],
    seq_b: list[Token],
    pack: LanguagePack,
    config: AlignerConfig,
) -> list[Match]:
    m, n = len(seq_a), len(seq_b)
    cache: dict[tuple[str, str], Match] = {}

    M = np.full((m + 1, n + 1), NEG_INF, dtype=np.float64)
    X = np.full((m + 1, n + 1), NEG_INF, dtype=np.float64)
    Y = np.full((m + 1, n + 1), NEG_INF, dtype=np.float64)
    # Traceback codes: 1=came from M, 2=came from X, 3=came from Y
    TBM = np.zeros((m + 1, n + 1), dtype=np.int8)
    TBX = np.zeros((m + 1, n + 1), dtype=np.int8)
    TBY = np.zeros((m + 1, n + 1), dtype=np.int8)

    # Abbreviation-span lookahead support.
    AB = np.full((m + 1, n + 1), NEG_INF, dtype=np.float64)
    TBAB_K = np.zeros((m + 1, n + 1), dtype=np.int8)   # span size (k)
    TBAB_SIDE = np.zeros((m + 1, n + 1), dtype=np.int8)  # 0=a-is-abbrev, 1=b-is-abbrev
    TBAB_EXPANSION: dict[tuple[int, int], str] = {}

    M[0, 0] = 0.0
    if config.semi_global_a:
        for i in range(1, m + 1):
            X[i, 0] = 0.0
            TBX[i, 0] = 2
    else:
        for i in range(1, m + 1):
            X[i, 0] = config.gap_open + config.gap_extend * (i - 1)
            TBX[i, 0] = 2
    if config.semi_global_b:
        for j in range(1, n + 1):
            Y[0, j] = 0.0
            TBY[0, j] = 3
    else:
        for j in range(1, n + 1):
            Y[0, j] = config.gap_open + config.gap_extend * (j - 1)
            TBY[0, j] = 3

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = _pair_score(seq_a[i - 1], seq_b[j - 1], pack, cache)
            s = _dp_score(match.score) if match.reason != Reason.NO_MATCH else -1.0

            # M
            best_prev = max(M[i - 1, j - 1], X[i - 1, j - 1], Y[i - 1, j - 1])
            M[i, j] = s + best_prev
            if best_prev == M[i - 1, j - 1]:
                TBM[i, j] = 1
            elif best_prev == X[i - 1, j - 1]:
                TBM[i, j] = 2
            else:
                TBM[i, j] = 3

            # X (gap in B): consume a[i-1]
            ox = M[i - 1, j] + config.gap_open
            ex = X[i - 1, j] + config.gap_extend
            yx = Y[i - 1, j] + config.gap_open
            best = max(ox, ex, yx)
            X[i, j] = best
            if best == ox:
                TBX[i, j] = 1
            elif best == ex:
                TBX[i, j] = 2
            else:
                TBX[i, j] = 3

            # Y (gap in A): consume b[j-1]
            oy = M[i, j - 1] + config.gap_open
            xy = X[i, j - 1] + config.gap_open
            ey = Y[i, j - 1] + config.gap_extend
            best = max(oy, xy, ey)
            Y[i, j] = best
            if best == oy:
                TBY[i, j] = 1
            elif best == xy:
                TBY[i, j] = 2
            else:
                TBY[i, j] = 3

            if config.abbrev_lookahead:
                # a[i-1] is the abbreviation; consume k tokens of b ending at j-1.
                if "abbreviation" in seq_a[i - 1].flags:
                    for k in range(2, min(config.abbrev_max_span, j) + 1):
                        span = seq_b[j - k:j]
                        sc = _abbrev_span_score_a_to_b(seq_a[i - 1], span)
                        if sc is None:
                            continue
                        score_unit, expansion = sc
                        s_dp = _dp_score(score_unit)
                        prev = max(M[i - 1, j - k], X[i - 1, j - k], Y[i - 1, j - k])
                        cand = s_dp + prev
                        if cand > AB[i, j]:
                            AB[i, j] = cand
                            TBAB_K[i, j] = k
                            TBAB_SIDE[i, j] = 0
                            TBAB_EXPANSION[(i, j)] = expansion

                # symmetric: b[j-1] is the abbreviation; consume k tokens of a.
                if "abbreviation" in seq_b[j - 1].flags:
                    for k in range(2, min(config.abbrev_max_span, i) + 1):
                        span = seq_a[i - k:i]
                        sc = _abbrev_span_score_a_to_b(seq_b[j - 1], span)
                        if sc is None:
                            continue
                        score_unit, expansion = sc
                        s_dp = _dp_score(score_unit)
                        prev = max(M[i - k, j - 1], X[i - k, j - 1], Y[i - k, j - 1])
                        cand = s_dp + prev
                        if cand > AB[i, j]:
                            AB[i, j] = cand
                            TBAB_K[i, j] = k
                            TBAB_SIDE[i, j] = 1
                            TBAB_EXPANSION[(i, j)] = expansion

                # Promote AB[i, j] into M[i, j] if it wins.
                if AB[i, j] > M[i, j]:
                    M[i, j] = AB[i, j]
                    TBM[i, j] = 4  # abbreviation-span transition

    # Choose traceback start.
    if config.semi_global_a or config.semi_global_b:
        best_val = NEG_INF
        best_pos = (m, n, "M")
        for jj in range(0, n + 1):
            for name, mat in (("M", M), ("X", X), ("Y", Y)):
                val = mat[m, jj]
                if val > best_val:
                    best_val = val
                    best_pos = (m, jj, name)
        for ii in range(0, m + 1):
            for name, mat in (("M", M), ("X", X), ("Y", Y)):
                val = mat[ii, n]
                if val > best_val:
                    best_val = val
                    best_pos = (ii, n, name)
        start_i, start_j, matrix = best_pos
        # Free trailing rim: tokens after the chosen traceback start are appended
        # as INSERTION (rim of A) / OMISSION (rim of B) without DP penalty,
        # so every input token still appears in the output.
        trailing: list[Match] = []
        ti, tj = start_i, start_j
        while ti < m:
            trailing.append(
                Match(token_a=seq_a[ti], token_b=None, score=0.0, reason=Reason.INSERTION)
            )
            ti += 1
        while tj < n:
            trailing.append(
                Match(token_a=None, token_b=seq_b[tj], score=0.0, reason=Reason.OMISSION)
            )
            tj += 1
        i, j = start_i, start_j
    else:
        i, j = m, n
        matrix = max(
            ("M", M[m, n]), ("X", X[m, n]), ("Y", Y[m, n]), key=lambda kv: kv[1]
        )[0]
        trailing = []

    matches: list[Match] = []
    while i > 0 or j > 0:
        if matrix == "M":
            tb = TBM[i, j]
            if tb == 4:
                k = int(TBAB_K[i, j])
                side = int(TBAB_SIDE[i, j])
                expansion = TBAB_EXPANSION[(i, j)]
                if side == 0:
                    abbrev_tok = seq_a[i - 1]
                    span_tokens = seq_b[j - k:j]
                    primary = Match(
                        token_a=abbrev_tok,
                        token_b=span_tokens[0],
                        score=0.85,
                        reason=Reason.ABBREVIATION,
                        details={
                            "role": "primary",
                            "expansion": expansion,
                            "span_size": k,
                            "span_token_ids": [t.id for t in span_tokens],
                        },
                    )
                    matches.append(primary)
                    for cont_tok in span_tokens[1:]:
                        matches.append(
                            Match(
                                token_a=abbrev_tok,
                                token_b=cont_tok,
                                score=0.0,
                                reason=Reason.ABBREVIATION,
                                details={"role": "continuation", "primary_index": -1},
                            )
                        )
                    i -= 1
                    j -= k
                else:
                    abbrev_tok = seq_b[j - 1]
                    span_tokens = seq_a[i - k:i]
                    primary = Match(
                        token_a=span_tokens[0],
                        token_b=abbrev_tok,
                        score=0.85,
                        reason=Reason.ABBREVIATION,
                        details={
                            "role": "primary",
                            "expansion": expansion,
                            "span_size": k,
                            "span_token_ids": [t.id for t in span_tokens],
                        },
                    )
                    matches.append(primary)
                    for cont_tok in span_tokens[1:]:
                        matches.append(
                            Match(
                                token_a=cont_tok,
                                token_b=abbrev_tok,
                                score=0.0,
                                reason=Reason.ABBREVIATION,
                                details={"role": "continuation", "primary_index": -1},
                            )
                        )
                    i -= k
                    j -= 1
                matrix = "M"
                continue
            mres = _pair_score(seq_a[i - 1], seq_b[j - 1], pack, cache)
            matches.append(mres)
            i -= 1
            j -= 1
            matrix = {1: "M", 2: "X", 3: "Y"}[tb]
        elif matrix == "X":
            tb = TBX[i, j]
            matches.append(
                Match(token_a=seq_a[i - 1], token_b=None, score=0.0, reason=Reason.INSERTION)
            )
            i -= 1
            matrix = {1: "M", 2: "X", 3: "Y"}[tb]
        else:  # Y
            tb = TBY[i, j]
            matches.append(
                Match(token_a=None, token_b=seq_b[j - 1], score=0.0, reason=Reason.OMISSION)
            )
            j -= 1
            matrix = {1: "M", 2: "X", 3: "Y"}[tb]

    matches.reverse()

    # Rebind primary_index for continuation matches to their post-reverse list index.
    last_primary_index: int | None = None
    for idx, mm in enumerate(matches):
        if mm.details and mm.details.get("role") == "primary":
            last_primary_index = idx
        elif mm.details and mm.details.get("role") == "continuation":
            if last_primary_index is not None:
                mm.details["primary_index"] = last_primary_index

    matches.extend(trailing)
    return matches

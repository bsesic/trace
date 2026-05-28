"""Tests for node_match_score aggregation."""

import tracealign
from tracealign.multi.graph import GraphNode
from tracealign.multi.merge import node_match_score


def _tokens(text: str):
    return tracealign.tokenize(text, lang="hbo", seq_label="seq")


def test_node_match_score_exact_match_max():
    pack = tracealign.get_language("hbo")
    tok = _tokens("שלום")[0]
    node = GraphNode(id="n:0", tokens={"W1": tok, "W2": tok})
    score = node_match_score(tok, node, pack, mode="max")
    # _dp_score(1.0) = 1.0
    assert score == 1.0


def test_node_match_score_max_picks_best_constituent():
    pack = tracealign.get_language("hbo")
    a = _tokens("שלום")[0]
    b = _tokens("aaa")[0]  # very different
    new = a
    node = GraphNode(id="n:0", tokens={"W1": a, "W2": b})
    s_max = node_match_score(new, node, pack, mode="max")
    s_min = node_match_score(new, node, pack, mode="min")
    s_mean = node_match_score(new, node, pack, mode="mean")
    assert s_max >= s_mean >= s_min


def test_node_match_score_rejects_unknown_mode():
    pack = tracealign.get_language("hbo")
    tok = _tokens("שלום")[0]
    node = GraphNode(id="n:0", tokens={"W1": tok})
    try:
        node_match_score(tok, node, pack, mode="median")
        raised = False
    except ValueError:
        raised = True
    assert raised

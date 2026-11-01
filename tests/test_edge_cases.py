"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import azr_algorithm as A
import azr_constants as C
from azr_scenario import Rules, make_banned_pairs, make_rules, parse_patterns


def _count(rules: Rules, n: int) -> int:
    return A.count_dp(A.build_automaton(rules), n)


def test_length_zero_has_exactly_one_word_and_length_one_counts_the_allowed_letters():
    assert _count(Rules("FSN", ("NF", "NNN")), 0) == 1 and _count(Rules("FSN", ("NF", "NNN")), 1) == 3
    assert _count(Rules("AB", ("A",)), 1) == 1


def test_no_patterns_means_all_words():
    assert _count(Rules("ABC", ()), 7) == 3 ** 7
    assert A.build_automaton(Rules("ABC", ())).states == ("",)


def test_forbidding_every_letter_leaves_only_the_empty_word():
    rules = Rules("AB", ("A", "B"))
    assert [_count(rules, n) for n in range(4)] == [1, 0, 0, 0]


def test_pattern_longer_than_the_word_cuts_nothing():
    assert _count(Rules("AB", ("AAAAAA",)), 5) == 2 ** 5
    assert _count(Rules("AB", ("AAAAAA",)), 6) == 2 ** 6 - 1


def test_pattern_as_long_as_the_word_cuts_exactly_one_word():
    """Ein Verbot der Länge n schneidet genau ein Wort: Grenze inklusive."""
    assert _count(Rules("AB", ("ABAB",)), 4) == 2 ** 4 - 1


def test_overlapping_patterns_are_all_enforced():
    rules = Rules("AB", ("AAB", "ABA"))
    assert A.sequence(A.build_automaton(rules), 6) == [A.brute_count(rules, n) for n in range(7)]


def test_negative_length_is_an_error_everywhere():
    auto = A.build_automaton(Rules("AB", ("AA",)))
    for call in (lambda: A.sequence(auto, -1), lambda: A.count_matrix(auto, -1), lambda: A.brute_count(Rules("AB", ()), -1),
                 lambda: A.dfs_count(Rules("AB", ()), -1), lambda: A.perm_count_dp(-1, frozenset())):
        with pytest.raises(ValueError):
            call()


def test_trace_word_rejects_foreign_letters_and_accepts_the_empty_word():
    auto = A.build_automaton(Rules("AB", ("AA",)))
    with pytest.raises(ValueError):
        A.trace_word(auto, "AX")
    assert A.trace_word(auto, "") == ([""], None)


def test_parse_patterns_rules():
    assert parse_patterns("NF, NNN", "FSN") == (("NF", "NNN"), [])
    assert parse_patterns("nf;nnn  NF", "FSN") == (("NF", "NNN"), [])                    # Kleinbuchstaben, Trenner, Doppelte
    patterns, problems = parse_patterns("NF, XY, AAAAAAA", "FSN")
    assert patterns == ("NF",) and len(problems) == 2
    many, problems = parse_patterns(", ".join(["F", "S", "N", "FF", "SS", "NN", "FS"]), "FSN")
    assert len(many) == C.PATTERN_MAX_COUNT and len(problems) == 1
    assert parse_patterns("", "FSN") == ((), [])


def test_parse_patterns_boundaries_are_inclusive():
    longest = "F" * C.PATTERN_MAX_LEN
    assert parse_patterns(longest, "FSN")[0] == (longest,)
    assert parse_patterns(longest + "F", "FSN")[0] == ()
    six = ["F", "S", "N", "FF", "SS", "NN"]
    assert len(parse_patterns(", ".join(six), "FSN")[0]) == C.PATTERN_MAX_COUNT


def test_make_rules_falls_back_to_the_default_alphabet_for_unknown_labels():
    rules, problems = make_rules("gibt es nicht", "NF")
    assert rules.alphabet == "FSN" and problems == []


def test_banned_pairs_are_deterministic_and_respect_the_density_edges():
    assert make_banned_pairs(8, 30, 35) == make_banned_pairs(8, 30, 35)
    assert make_banned_pairs(8, 0, 35) == frozenset()
    assert len(make_banned_pairs(8, 100, 35)) == 8 * 7                                  # alle Paare a ≠ b
    assert all(a != b for a, b in make_banned_pairs(10, 50, 7))


def test_perm_with_everything_banned_has_no_order_for_two_or_more_symbols():
    full = make_banned_pairs(5, 100, 1)
    assert A.perm_count_dp(5, full) == 0 and A.perm_count_dp(1, full) == 1

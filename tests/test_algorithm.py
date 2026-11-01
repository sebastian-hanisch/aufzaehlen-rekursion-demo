"""Kern gegen Handrechnung (DEMO-PLAYBOOK §1b): Mini-Instanzen aus conftest.py, jeder Erwartungswert als Rechnung."""

from fractions import Fraction

import pytest

import azr_algorithm as A
from azr_scenario import Rules


def test_fibonacci_by_hand_n4_lists_the_eight_words(fib):
    assert A.enumerate_valid(fib, 4) == ["ABAB", "ABBA", "ABBB", "BABA", "BABB", "BBAB", "BBBA", "BBBB"]


def test_fibonacci_sequence(fib):
    assert A.sequence(A.build_automaton(fib), 8) == [1, 2, 3, 5, 8, 13, 21, 34, 55]


def test_schicht_first_terms_by_hand(schicht):
    auto = A.build_automaton(schicht)
    assert A.sequence(auto, 3) == [1, 3, 8, 20]          # 3, 9 − 1, 27 − 6 − 1


def test_schicht_states_and_transitions(schicht):
    auto = A.build_automaton(schicht)
    assert auto.states == ("", "N", "NN")
    assert auto.trans[("", "F")] == "" and auto.trans[("", "S")] == "" and auto.trans[("", "N")] == "N"
    assert auto.trans[("N", "F")] is None and auto.trans[("N", "S")] == "" and auto.trans[("N", "N")] == "NN"
    assert auto.trans[("NN", "F")] is None and auto.trans[("NN", "S")] == "" and auto.trans[("NN", "N")] is None


def test_schicht_recurrence_by_hand(schicht):
    """Aus den Übergängen: s' = 2s + n1 + n2, n1' = s, n2' = n1, also a(n) = 2a(n−1) + a(n−2) + a(n−3)."""
    a = A.sequence(A.build_automaton(schicht), 30)
    assert all(a[n] == 2 * a[n - 1] + a[n - 2] + a[n - 3] for n in range(3, 31))
    r, c = A.smallest_recurrence(a, 6)
    assert r == 3 and c == [Fraction(2), Fraction(1), Fraction(1)]


def test_brute_dfs_and_dp_agree_on_the_minis(fib, schicht):
    for rules in (fib, schicht):
        auto = A.build_automaton(rules)
        for n in range(0, 8):
            assert A.brute_count(rules, n) == A.dfs_count(rules, n) == A.count_dp(auto, n) == A.count_matrix(auto, n), (rules, n)


def test_trace_word_follows_the_states(schicht):
    auto = A.build_automaton(schicht)
    assert A.trace_word(auto, "FSNN") == (["", "", "", "N", "NN"], None)
    states, bad = A.trace_word(auto, "FSNNF")             # NF vollendet an Stelle 5 (Index 4)
    assert bad == 4 and states == ["", "", "", "N", "NN"]
    assert A.trace_word(auto, "NNN")[1] == 2


def test_growth_ratio_is_exact_for_the_last_two_terms():
    assert A.growth_ratio([1, 2, 3, 5, 8, 13]) == 1.625    # 13 / 8
    assert A.growth_ratio([1]) is None and A.growth_ratio([0, 0]) is None
    assert A.growth_ratio([10 ** 400, 2 * 10 ** 400]) == 2.0   # kein float-Überlauf


def test_solve_recurrence_and_fits_until_by_hand():
    fibs = [1, 1, 2, 3, 5, 8, 13, 21]
    assert A.solve_recurrence(fibs, 2) == [1, 1]
    assert A.fits_until(fibs, [Fraction(1), Fraction(1)]) == 7
    doubling = [1, 2, 4, 8, 16, 31]                         # a(5) = 31 statt 32
    assert A.fits_until(doubling, [Fraction(2)]) == 4
    assert A.solve_recurrence([1, 1, 1], 2) is None         # a(0..3) fehlen
    assert A.solve_recurrence([1, 1, 1, 1], 2) is None      # singulär: alle Zeilen gleich


def test_smallest_recurrence_rejects_orders_that_only_fit_the_start():
    a = A.sequence(A.build_automaton(Rules("FSN", ("NF", "NNN"))), 40)
    c1 = A.solve_recurrence(a, 1)
    assert c1 is not None and A.fits_until(a, c1) < len(a) - 1
    r, _ = A.smallest_recurrence(a, 6)
    assert r == 3


def test_perm_dp_by_hand():
    assert A.perm_count_dp(3, frozenset()) == 6
    assert A.perm_count_dp(3, frozenset({(0, 1), (1, 2)})) == 3      # 6 − 123, 312 (enthält 12), 231 (enthält 23): 6 − 3 = 3
    assert A.perm_count_dp(1, frozenset()) == 1 and A.perm_count_dp(0, frozenset()) == 1


def test_perm_state_count():
    assert A.perm_state_count(19) == 9_961_472                    # 2^19 · 19 = 524 288 · 19
    assert A.perm_state_count(4) == 64


def test_check_count_accepts_the_truth_and_flags_a_wrong_number(schicht):
    auto = A.build_automaton(schicht)
    assert A.check_count(schicht, auto, 6, 331, 8) == []
    assert A.check_count(schicht, auto, 6, 332, 8) != []
    assert A.check_count(schicht, auto, 6, 3 ** 6 + 1, 8) != []
    assert A.check_count(schicht, auto, 12, 90328 + 1, 8) != []     # n > 8: nur die Matrixpotenz fängt es
    assert A.check_count(schicht, auto, 12, 90328, 8) == []


@pytest.mark.parametrize("bad", [("",), ("AX",)])
def test_automaton_rejects_invalid_patterns(bad):
    with pytest.raises(ValueError):
        A.build_automaton(Rules("AB", bad))

"""Orakel-Tests: die Rekursion über den Zustand gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: Aufzählen aller Wörter (itertools), die Matrixpotenz der Übergangsmatrix (anderer Rechenweg als die Vektorschritte), bekannte Folgen aus der
Literatur (Fibonacci, Tribonacci, A000255 der OEIS) und die geschlossene Formel n + 1 für „kein AB“. Feste Zufallsstände (range(40)), zusammen unter 10 Sekunden."""

import random

import pytest

import azr_algorithm as A
from azr_scenario import Rules


def _random_rules(seed: int) -> Rules:
    rng = random.Random(seed)
    alphabet = "AB" if rng.random() < 0.4 else "ABC"
    patterns = tuple("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(0, 3)))
    return Rules(alphabet, patterns)


@pytest.mark.parametrize("seed", range(40))
def test_recursion_equals_brute_force_and_matrix_power(seed):
    rules = _random_rules(seed)
    auto = A.build_automaton(rules)
    seq = A.sequence(auto, 8)
    for n in range(9):
        assert seq[n] == A.brute_count(rules, n), (rules, n)
        assert seq[n] == A.dfs_count(rules, n), (rules, n)
    for n in (0, 1, 5, 17, 30):
        assert A.count_matrix(auto, n) == A.sequence(auto, n)[-1], (rules, n)


def test_fibonacci_from_the_literature():
    fibs = [1, 1]
    for _ in range(40):
        fibs.append(fibs[-1] + fibs[-2])
    seq = A.sequence(A.build_automaton(Rules("AB", ("AA",))), 40)
    assert seq == fibs[1:42]                       # a(n) = F(n + 2) mit F(1) = F(2) = 1


def test_tribonacci_words_without_aaa():
    seq = A.sequence(A.build_automaton(Rules("AB", ("AAA",))), 12)
    assert seq[:8] == [1, 2, 4, 7, 13, 24, 44, 81]
    assert all(seq[n] == seq[n - 1] + seq[n - 2] + seq[n - 3] for n in range(3, 13))


def test_words_without_ab_are_counted_by_n_plus_one():
    """Ohne AB steht jedes B vor jedem A: B…BA…A, also n + 1 Wörter."""
    seq = A.sequence(A.build_automaton(Rules("AB", ("AB",))), 25)
    assert seq == [n + 1 for n in range(26)]


def test_forbidden_letter_leaves_one_word():
    seq = A.sequence(A.build_automaton(Rules("AB", ("A",))), 10)
    assert seq == [1] * 11


def _a000255(n: int) -> int:
    """OEIS A000255: a(0) = a(1) = 1, a(n) = n · a(n−1) + (n−1) · a(n−2). Permutationen von {0, …, n} ohne i direkt vor i + 1."""
    a = [1, 1]
    for k in range(2, n + 1):
        a.append(k * a[k - 1] + (k - 1) * a[k - 2])
    return a[n]


@pytest.mark.parametrize("m", range(1, 11))
def test_permutations_without_consecutive_pairs_follow_a000255(m):
    banned = frozenset((i, i + 1) for i in range(m - 1))
    assert A.perm_count_dp(m, banned) == _a000255(m - 1)


@pytest.mark.parametrize("seed", range(40))
def test_perm_dp_equals_brute_force_on_random_bans(seed):
    rng = random.Random(seed)
    m = rng.randint(1, 7)
    density = rng.choice((0.0, 0.2, 0.5, 0.8))
    banned = frozenset((a, b) for a in range(m) for b in range(m) if a != b and rng.random() < density)
    assert A.perm_count_dp(m, banned) == A.perm_count_brute(m, banned), (m, sorted(banned))


def test_recurrence_search_finds_the_known_orders():
    """Fibonacci: Ordnung 2; Tribonacci: Ordnung 3; die Zustandszahl ist eine obere Schranke der Ordnung (Cayley–Hamilton)."""
    for rules, order in ((Rules("AB", ("AA",)), 2), (Rules("AB", ("AAA",)), 3)):
        auto = A.build_automaton(rules)
        r, _ = A.smallest_recurrence(A.sequence(auto, 60), 12)
        assert r == order <= auto.size

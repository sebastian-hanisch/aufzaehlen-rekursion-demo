"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jede Regelmenge gelten, auf festen Zufallsständen."""

import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

import azr_algorithm as A
from azr_scenario import Rules

ROOT = Path(__file__).resolve().parent.parent


def _rules(seed: int) -> Rules:
    rng = random.Random(seed)
    alphabet = rng.choice(("AB", "ABC"))
    return Rules(alphabet, tuple("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(0, 4))))


def _seq(rules: Rules, n: int = 10) -> list:
    return A.sequence(A.build_automaton(rules), n)


@pytest.mark.parametrize("seed", range(30))
def test_count_is_between_zero_and_k_to_the_n(seed):
    rules = _rules(seed)
    assert all(0 <= v <= rules.k ** n for n, v in enumerate(_seq(rules)))


@pytest.mark.parametrize("seed", range(30))
def test_adding_a_pattern_never_increases_the_count(seed):
    rules = _rules(seed)
    rng = random.Random(1000 + seed)
    extra = "".join(rng.choice(rules.alphabet) for _ in range(rng.randint(1, 4)))
    more = Rules(rules.alphabet, rules.patterns + (extra,))
    assert all(b <= a for a, b in zip(_seq(rules), _seq(more)))


@pytest.mark.parametrize("seed", range(30))
def test_renaming_symbols_changes_nothing(seed):
    rules = _rules(seed)
    swap = str.maketrans("AB", "BA")
    renamed = Rules(rules.alphabet.translate(swap), tuple(p.translate(swap) for p in rules.patterns))
    assert _seq(rules) == _seq(renamed)


@pytest.mark.parametrize("seed", range(30))
def test_order_duplicates_and_redundant_patterns_change_nothing(seed):
    rules = _rules(seed)
    reordered = Rules(rules.alphabet, tuple(reversed(rules.patterns)) + rules.patterns)      # umgekehrt und doppelt
    assert _seq(rules) == _seq(reordered)
    if rules.patterns:
        first = rules.patterns[0]
        redundant = Rules(rules.alphabet, rules.patterns + (first + rules.alphabet[0], rules.alphabet[-1] + first))   # Obermuster eines Verbots
        assert _seq(rules) == _seq(redundant)


@pytest.mark.parametrize("seed", range(30))
def test_automaton_size_is_bounded_by_the_pattern_lengths(seed):
    rules = _rules(seed)
    auto = A.build_automaton(rules)
    assert auto.size <= 1 + sum(len(p) - 1 for p in rules.patterns)
    assert auto.states[0] == ""


def test_forbidding_a_letter_equals_a_smaller_alphabet():
    with_c = Rules("ABC", ("C", "AB", "BBA"))
    without_c = Rules("AB", ("AB", "BBA"))
    assert _seq(with_c, 12) == _seq(without_c, 12)


def test_recurrence_of_order_at_most_the_state_count_holds_from_n_equal_state_count():
    """Cayley–Hamilton: a(n) = Σ c_j a(n−j) mit Ordnung ≤ Zustandszahl s gilt ab n = s (hier die aus den ersten 2s Gliedern bestimmte)."""
    checked = 0
    for seed in range(30):
        rules = _rules(seed)
        auto = A.build_automaton(rules)
        s = auto.size
        a = A.sequence(auto, 4 * s + 12)
        c = A.solve_recurrence(a, s)
        if c is None:                                      # singulär: z. B. a(n) = 0 für n ≥ 1
            continue
        checked += 1
        assert A.fits_until(a, c) == len(a) - 1, rules
    assert checked >= 10                                   # der Test prüft wirklich etwas (nicht alles singulär)


def test_result_does_not_depend_on_the_hash_seed():
    """Mengen von Zeichenketten ordnen sich je Prozess anders (Hash-Randomisierung): dasselbe Szenario in zwei Prozessen muss dasselbe geben."""
    code = (
        "import azr_algorithm as A; from azr_scenario import Rules; "
        "r = Rules('ABC', ('AB', 'BC', 'CA', 'AAA', 'BBBC')); a = A.build_automaton(r); "
        "print(a.states, sorted((k, v) for k, v in a.trans.items() if v is not None), A.sequence(a, 12))"
    )
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()

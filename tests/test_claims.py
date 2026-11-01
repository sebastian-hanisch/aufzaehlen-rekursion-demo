"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Zeiten stehen nie als feste Zahl hier; nur Rangfolgen mit großem Abstand."""

import math
import random
import time

import azr_algorithm as A
import azr_constants as C
import azr_evaluation as ev
from azr_scenario import Rules

SCHICHT = Rules("FSN", ("NF", "NNN"))


def _auto(rules: Rules = SCHICHT) -> A.Automaton:
    return A.build_automaton(rules)


def test_readme_standard_terms_and_the_value_in_the_app():
    a = A.sequence(_auto(), 12)
    assert a[:11] == [1, 3, 8, 20, 51, 130, 331, 843, 2147, 5468, 13926]
    assert a[12] == 90328 and 3 ** 12 == 531441 and ev.pct(a[12] / 3 ** 12) == "17,0 %"


def test_readme_recurrence_and_growth_value():
    a = A.sequence(_auto(), 200)
    assert all(a[n] == 2 * a[n - 1] + a[n - 2] + a[n - 3] for n in range(3, 201))
    root = 2.5468182769
    for n in (20, 50, 200):
        assert abs(A.growth_ratio(a[: n + 1], 12) - root) < 1e-6, n
    assert abs(root ** 3 - (2 * root ** 2 + root + 1)) < 1e-6          # positive Wurzel von x³ = 2x² + x + 1
    assert abs(A.growth_ratio(a[:11], 12) - 2.5468) < 5e-4              # schon bei n = 10 auf vier Stellen


def test_readme_fibonacci_preset():
    a = A.sequence(_auto(Rules("AB", ("AA",))), 8)
    assert a == [1, 2, 3, 5, 8, 13, 21, 34, 55] and _auto(Rules("AB", ("AA",))).size == 2


def test_readme_state_counts_of_the_presets():
    sizes = {name: ev.analyse(ev.Settings(**p)).auto.size for name, p in C.PRESETS.items()}
    assert sizes == {"Standardfall: Schichtfolgen": 3, "Fibonacci: A, B ohne AA": 2, "Rekursion mit Anlauf": 5,
                     "Viele Verbote, mehr Zustände": 11, "Zu lang zum Aufzählen (n = 40)": 3}


def test_readme_state_bound_for_random_long_patterns():
    """README: vier Verbote der Länge 8 über F, S, N: naiv 3^7 = 2187 Zustände, der Automat nie mehr als 1 + 4·7 = 29."""
    assert 3 ** 7 == 2187
    sizes = []
    for seed in range(60):
        rng = random.Random(seed)
        patterns = tuple("".join(rng.choice("FSN") for _ in range(8)) for _ in range(4))
        sizes.append(A.build_automaton(Rules("FSN", patterns)).size)
    assert max(sizes) <= 1 + 4 * 7 and min(sizes) > 8


def test_readme_digits_of_large_counts():
    auto = _auto()
    assert [A.digit_count(A.count_dp(auto, n)) for n in (20, 100, 1000, 3000, 10000)] == [9, 41, 407, 1219, 4061]
    assert A.digit_count(3 ** 10000) == 4772                              # README: Python verweigert die Umwandlung ab 4300 Stellen in Text


def test_readme_float_limits_are_inside_bands():
    res = ev.float_experiment(_auto())
    assert 38 <= res["first_diff"] <= 44 and 740 <= res["first_overflow"] <= 780
    a = A.sequence(_auto(), 41)
    assert a[40] > 2 ** 53 and a[39] < 2 ** 53 < a[41]                    # ab 2^53 sind nicht mehr alle ganzen Zahlen darstellbar


def test_readme_guessing_findings():
    std = ev.guess_experiment(_auto())
    assert [(r["r"], r["fits_until"]) for r in std["rows"][:2]] == [(1, 1), (2, 3)] and std["r_min"] == 3 and std["states"] == 3
    anlauf = ev.guess_experiment(_auto(Rules("ABC", ("AB", "BC", "CA", "AAA"))))
    assert [(r["r"], r["fits_until"]) for r in anlauf["rows"][:3]] == [(1, 1), (2, 3), (3, 6)]
    assert anlauf["r_min"] == 5 and anlauf["effective_order"] == 4 and anlauf["holds_from"] == 5
    assert [str(c) for c in anlauf["coeffs"]] == ["2", "-1", "1", "1", "0"]
    assert [ev.guess_experiment(_auto(Rules("AB", ("AA",))))["r_min"], std["r_min"], anlauf["r_min"]] == [2, 3, 5]


def test_readme_second_wall_numbers():
    assert A.perm_state_count(19) == 9_961_472 and math.factorial(19) == 121_645_100_408_832_000
    assert A.perm_state_count(12) == 49_152 and math.factorial(12) == 479_001_600
    assert C.WALL_BRUTE_MAX == 8 and math.factorial(8) == 40_320


def test_readme_hook_correction_enumeration_is_far_slower_than_the_recursion():
    """Nur die Rangfolge mit großem Abstand (README: Faktor in Tausenden bei n = 13), nie eine feste Zeit."""
    auto = _auto()
    t0 = time.perf_counter()
    A.dfs_count(SCHICHT, 12)
    t_dfs = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(50):
        A.count_dp(auto, 12)
    t_rec = (time.perf_counter() - t0) / 50
    assert t_dfs > 50 * t_rec


def test_app_text_limits_come_from_the_constants():
    assert (C.PATTERN_MAX_COUNT, C.PATTERN_MAX_LEN) == (6, 6) and 1 + C.PATTERN_MAX_COUNT * (C.PATTERN_MAX_LEN - 1) == 31
    assert C.GUESS_MAX_STATES == 12 and C.GUESS_RMAX == 12 and C.GUESS_TERMS == 60 and C.FLOAT_N_MAX == 1100

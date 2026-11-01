"""Große ganze Zahlen: Python wandelt Zahlen mit mehr als 4300 Stellen nicht in Text um (ValueError). 3^10000 hat 4772 Stellen, also darf nirgends str(x) auf
Zählwerte laufen. Regressionstest: auf dem Stand vor der Korrektur stürzte Experiment 2 bei Regeln ohne Einschränkung ab (gefunden beim AppTest-Lauf)."""

import math
import sys

import pytest

import azr_algorithm as A
import azr_evaluation as ev
import azr_visualization as V
from azr_scenario import Rules


def _digits_by_string(x: int) -> int:
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        return len(str(x))
    finally:
        sys.set_int_max_str_digits(old)


@pytest.mark.parametrize("x", [
    pytest.param(v, id=label) for v, label in [
        (0, "0"), (1, "1"), (9, "9"), (10, "10"), (99, "99"), (100, "100"), (10 ** 17 - 1, "1e17-1"), (10 ** 17, "1e17"), (2 ** 100, "2^100"),
        (3 ** 10000, "3^10000"), (10 ** 5000, "1e5000"), (10 ** 5000 - 1, "1e5000-1"),
    ]
])
def test_digit_count_equals_the_string_length(x):
    assert A.digit_count(x) == _digits_by_string(x)


def test_digit_count_rejects_negative_numbers():
    with pytest.raises(ValueError):
        A.digit_count(-1)


def test_leading_digits():
    assert A.leading_digits(12345, 3) == (5, 123)
    assert A.leading_digits(12, 3) == (2, 12)
    assert A.leading_digits(10 ** 5000, 3) == (5001, 100)


def test_large_experiment_survives_numbers_beyond_the_string_limit():
    auto = A.build_automaton(Rules("ABC", ()))                                  # a(n) = 3^n
    rows = ev.large_experiment(auto, sizes=(10000,), budget=60.0)
    assert rows[0]["digits"] == 4772 and rows[0]["skipped"] is False            # floor(10000 · log10 3) + 1


def test_big_text_and_log10_handle_five_thousand_digits():
    assert ev.big_text(10 ** 5000) == "1,00·10⁵⁰⁰⁰ (5001 Stellen)"
    assert abs(V._log10(10 ** 5000) - 5000.0) < 1e-9
    assert abs(V._log10(3 ** 10000) - 10000 * 0.47712125471966244) < 1e-6


def test_log10_of_small_numbers():
    assert V._log10(1) == 0.0 and abs(V._log10(1000) - 3.0) < 1e-12
    assert abs(V._log10(12345) - math.log10(12345)) < 1e-12                       # Orakel: die Standardbibliothek, solange die Zahl in float passt

"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import azr_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_standard_case_shows_the_hand_values_and_no_error():
    at = _app()
    assert not at.error
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Gültige Folgen a(n)"] == "90.328" and metrics["Alle Folgen"] == "531.441" and metrics["Zustände"] == "3"


def test_enumeration_experiment_runs_and_shows_a_verdict():
    at = _app()
    at.button(key="enum_run").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert not at.error
    assert any("Hochgerechnet auf n = 30" in e.value for e in list(at.success) + list(at.info))


def test_wall_experiment_runs_for_a_small_m():
    at = _app()
    at.slider(key="wall_m").set_value(8).run(timeout=TIMEOUT)
    at.button(key="wall_run").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert "Der Zustand selbst ist hier die Wand." in " ".join(w.value for w in at.warning)


def test_wall_result_is_hidden_when_the_wall_settings_change():
    at = _app()
    at.slider(key="wall_m").set_value(6).run(timeout=TIMEOUT)
    at.button(key="wall_run").click().run(timeout=TIMEOUT)
    at.slider(key="wall_density").set_value(10).run(timeout=TIMEOUT)
    assert "Noch nicht gemessen für diese Einstellungen." in " ".join(i.value for i in at.info)


def test_permalink_loads_and_clamps_the_values():
    at = _app({"alphabet": "A, B", "patterns": "AA", "n": "9999"})
    assert at.sidebar.selectbox(key="alphabet_select").value == "A, B"
    assert at.sidebar.text_input(key="patterns_input").value == "AA"
    assert at.sidebar.slider(key="n_slider").value == C.N_MAX


def test_permalink_with_garbage_is_ignored_or_cut():
    at = _app({"alphabet": "kein Alphabet", "patterns": "X" * 500, "n": "abc"})
    assert at.sidebar.selectbox(key="alphabet_select").value == C.DEFAULT_ALPHABET
    assert len(at.sidebar.text_input(key="patterns_input").value) <= C.PATTERN_TEXT_MAX
    assert at.sidebar.slider(key="n_slider").value == C.DEFAULT_N


def test_invalid_patterns_are_reported_and_do_not_crash():
    at = _app()
    at.sidebar.text_input(key="patterns_input").set_value("QQ, NF, AAAAAAAA").run(timeout=TIMEOUT)
    assert not at.exception
    assert len(at.warning) >= 2 and any("außerhalb des Alphabets" in w.value for w in at.warning)


def test_all_letters_forbidden_gives_the_zero_verdict_without_division_errors():
    at = _app()
    at.sidebar.text_input(key="patterns_input").set_value("F, S, N").run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert "keine gültige Folge" in " ".join(w.value for w in at.warning)
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Gültige Folgen a(n)"] == "0" and metrics["Wachstum a(n)/a(n−1)"] == "–"


def test_no_patterns_gives_the_info_verdict():
    at = _app()
    at.sidebar.text_input(key="patterns_input").set_value("").run(timeout=TIMEOUT)
    assert not at.exception and "Keine Regel schränkt etwas ein" in " ".join(i.value for i in at.info)


def test_playground_word_with_a_violation_and_with_foreign_letters():
    at = _app()
    at.text_input(key="play_word").set_value("fsnnf").run(timeout=TIMEOUT)
    assert not at.exception and "vollendet ein Verbot" in " ".join(w.value for w in at.warning)
    at.text_input(key="play_word").set_value("XYZ").run(timeout=TIMEOUT)
    assert not at.exception and any("Nur Zeichen des Alphabets" in w.value for w in at.warning)
    at.text_input(key="play_word").set_value("").run(timeout=TIMEOUT)
    assert not at.exception


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "1"}, {"n": "60"}, {"patterns": "F, S, N"}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query


@pytest.mark.parametrize("alphabet", list(C.ALPHABETS))
def test_every_alphabet_renders(alphabet):
    at = _app({"alphabet": alphabet, "patterns": ""})
    assert not at.exception

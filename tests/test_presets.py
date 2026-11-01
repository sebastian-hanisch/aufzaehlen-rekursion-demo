"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Regelparser nimmt jedes Preset ohne Meldung."""

import azr_constants as C
import azr_evaluation as ev
import azr_presets as P
from azr_scenario import make_rules


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["alphabet"] in C.ALPHABETS, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX, name
        assert len(preset["patterns"]) <= C.PATTERN_TEXT_MAX, name


def test_every_preset_parses_without_a_message_and_builds_an_automaton():
    for name, preset in C.PRESETS.items():
        rules, problems = make_rules(preset["alphabet"], preset["patterns"])
        assert problems == [], name
        assert ev.analyse(ev.Settings(**preset)).problems == [], name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall: Schichtfolgen"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_differ_in_the_property_they_are_meant_to_show():
    """Jedes Preset zeigt etwas anderes (kein totes Preset): Zustandszahl, Anlauf oder Länge unterscheiden sich von den Standardregeln."""
    stats = {}
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        stats[name] = (a.auto.size, preset["n"], a.rules.alphabet)
    assert len(set(stats.values())) == len(C.PRESETS)
    assert stats["Viele Verbote, mehr Zustände"][0] > 3 and stats["Fibonacci: A, B ohne AA"][0] == 2 and stats["Rekursion mit Anlauf"][0] == 5

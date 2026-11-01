"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

import azr_algorithm as A
import azr_evaluation as ev
from azr_scenario import Rules


# ----------------------------------------------------------------------------- Formatierung

def test_big_text_groups_digits_and_switches_to_powers_of_ten_at_12_digits():
    assert ev.big_text(0) == "0" and ev.big_text(999) == "999" and ev.big_text(1234567) == "1.234.567"
    assert ev.big_text(999_999_999_999) == "999.999.999.999"
    assert ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.big_text(12345678901234567890) == "1,23·10¹⁹ (20 Stellen)"
    assert ev.big_text(10 ** 400) == "1,00·10⁴⁰⁰ (401 Stellen)"                  # weit über float


def test_count_text_and_pct_and_time_text():
    assert ev.count_text(9999) == "9999" and ev.count_text(10_000) == "10,0 Tausend" and ev.count_text(32_212_254_720) == "32,2 Milliarden"
    assert ev.pct(0.17) == "17,0 %" and ev.pct(0.005) == "0,50 %" and ev.pct(0.00001) == "unter 0,01 %" and ev.pct(0.0) == "0,00 %"
    assert ev.time_text(5e-6) == "5,0 Mikrosekunden" and ev.time_text(200e-6) == "200 Mikrosekunden"
    assert ev.time_text(0.0123) == "12,3 Millisekunden" and ev.time_text(0.5) == "500 Millisekunden"
    assert ev.time_text(5) == "5,0 Sekunden" and ev.time_text(90) == "1,5 Minuten" and ev.time_text(7200) == "2,0 Stunden"
    assert ev.time_text(3_200_000) == "37,0 Tagen" and ev.time_text(1e9) == "31,7 Jahren"


# ----------------------------------------------------------------------------- Kernfrage

def _analysis(alphabet: str, patterns: str, n: int):
    return ev.analyse(ev.Settings(alphabet, patterns, n))


def test_verdict_count_names_total_count_share_and_states():
    kind, text = ev.verdict_count(_analysis("F, S, N (Früh, Spät, Nacht)", "NF, NNN", 12))          # 90 328 von 531 441 = 16,997 %
    assert kind == "success"
    assert text == "Von den 3^12 = 531.441 möglichen Folgen der Länge 12 sind **90.328** gültig, das sind 17,0 %. Die Rekursion merkt sich dafür nur **3 Zustände**."
    kind, text = ev.verdict_count(_analysis("F, S, N (Früh, Spät, Nacht)", "NF, NNN", 40))             # große Zahlen als Zehnerpotenz mit Stellenzahl
    assert kind == "success" and text.startswith("Von den 3^40 = 1,21·10¹⁹ (20 Stellen) möglichen Folgen der Länge 40 sind **")


def test_verdict_count_without_rules_is_info_and_with_everything_forbidden_a_warning():
    kind, text = ev.verdict_count(_analysis("A, B", "", 5))
    assert kind == "info" and "alle 32 Folgen der Länge 5" in text
    kind, text = ev.verdict_count(_analysis("A, B", "A, B", 3))
    assert kind == "warning" and "Länge 3" in text


def test_analysis_flags_nothing_for_the_standard_case_and_has_the_right_bound():
    a = _analysis("F, S, N (Früh, Spät, Nacht)", "NF, NNN", 12)
    assert a.problems == [] and a.parse_problems == [] and a.state_bound == 1 + 1 + 2 == 4 and a.auto.size == 3
    assert abs(a.share - 90328 / 531441) < 1e-12


# ----------------------------------------------------------------------------- Experiment 1

def _enum_res(t_dfs, t_rec, t_target=3600.0):
    return {"rows": [{"n": 10, "t_dfs": t_dfs, "t_rec": t_rec, "t_brute": None, "all": 59049, "valid": 13926}],
            "extrapolation": [{"n": 30, "t_dfs": t_target, "t_rec": 0.0002, "t_brute": None, "valid": 5}]}


def test_verdict_enum_text_and_threshold():
    kind, text = ev.verdict_enum(_enum_res(0.05, 0.0001))
    assert kind == "success"
    assert text == ("Bei n = 10 braucht das Aufzählen mit Abschneiden 50,0 Millisekunden, die Rekursion 100 Mikrosekunden (etwa Faktor 500). "
                    "Hochgerechnet auf n = 30: Aufzählen etwa 1,0 Stunden, die Rekursion braucht gemessen 200 Mikrosekunden.")
    assert ev.verdict_enum(_enum_res(5.0, 0.5))[0] == "success"        # Faktor genau 10: inklusive
    assert ev.verdict_enum(_enum_res(4.5, 0.5))[0] == "info"           # Faktor 9


def test_verdict_enum_without_measurement_says_so():
    res = {"rows": [{"n": 4, "t_dfs": None, "t_rec": 0.0, "t_brute": None, "all": 81, "valid": 0}], "extrapolation": [{"n": 30, "t_dfs": None, "t_rec": 0.0, "t_brute": None, "valid": 0}]}
    kind, text = ev.verdict_enum(res)
    assert kind == "info" and "nichts zum Hochrechnen" in text


def test_extrapolate_enum_scales_the_rate_of_the_last_row(schicht):
    auto = A.build_automaton(schicht)
    rows = [{"n": 5, "all": 243, "valid": 130, "t_brute": 2.43, "t_dfs": 0.65, "t_rec": 0.0}]
    ex = ev.extrapolate_enum(schicht, auto, rows, targets=(20,))[0]
    assert ex["t_brute"] == 2.43 / 243 * 3 ** 20                          # 0,01 s je Wort mal 3^20 Wörter
    assert abs(ex["t_dfs"] - 0.65 / 130 * A.count_dp(auto, 20)) < 1e-6    # 0,005 s je gültiges Wort mal a(20)
    assert ev.extrapolate_enum(schicht, auto, [], targets=(20,))[0]["t_brute"] is None


def test_enum_experiment_agrees_with_the_recursion_and_stops_at_the_budget(schicht):
    res = ev.enum_experiment(schicht, budget=1e-4, n_max=9)
    assert res["problems"] == [] and [r["n"] for r in res["rows"]][0] == 4
    auto = A.build_automaton(schicht)
    assert all(r["valid"] == A.count_dp(auto, r["n"]) and r["all"] == 3 ** r["n"] for r in res["rows"])
    assert len(res["rows"]) < 6 or res["rows"][-1]["t_brute"] is not None   # entweder alle Längen gemessen oder bei Überschreitung beendet


# ----------------------------------------------------------------------------- Experiment 2 und 3

def test_verdict_large_text_and_edge_cases():
    rows = [{"n": 20, "digits": 9, "seconds": 0.0001, "skipped": False}, {"n": 10000, "digits": 4061, "seconds": 0.05, "skipped": False}]
    kind, text = ev.verdict_large(rows)
    assert kind == "success" and text.startswith("Bei n = 10000 hat die Anzahl 4061 Stellen und ist in 50,0 Millisekunden exakt ausgerechnet.")
    assert ev.verdict_large([{"n": 20, "digits": None, "seconds": None, "skipped": True}])[0] == "warning"
    assert ev.verdict_large([{"n": 20, "digits": 1, "seconds": 0.0001, "skipped": False}])[0] == "info"


def test_large_experiment_skips_sizes_once_the_budget_is_spent(schicht):
    rows = ev.large_experiment(A.build_automaton(schicht), sizes=(20, 100, 1000), budget=0.0)
    assert [r["skipped"] for r in rows] == [False, True, True]
    full = ev.large_experiment(A.build_automaton(schicht), sizes=(20, 100), budget=60.0)
    assert not any(r["skipped"] for r in full)
    assert [r["digits"] for r in full] == [len(str(A.count_matrix(A.build_automaton(schicht), n))) for n in (20, 100)]   # Stellenzahl über die Matrixpotenz gezählt
    assert rows[0]["digits"] == full[0]["digits"]


def test_verdict_float_three_cases():
    kind, text = ev.verdict_float({"first_diff": 41, "first_overflow": 760, "n_max": 1100})
    assert kind == "warning" and text == ("Mit Gleitkommazahlen gilt: ab n = 41 weicht das Gleitkommaergebnis vom exakten ab und ab n = 760 läuft es über (unendlich). "
                                          "Ganze Zahlen kennen beide Grenzen nicht.")
    assert "ab n = 41 weicht" in ev.verdict_float({"first_diff": 41, "first_overflow": None, "n_max": 1100})[1]
    assert "läuft es über" not in ev.verdict_float({"first_diff": 41, "first_overflow": None, "n_max": 1100})[1]
    kind, text = ev.verdict_float({"first_diff": None, "first_overflow": None, "n_max": 1100})
    assert kind == "info" and "Bis n = 1100" in text


def test_float_experiment_slow_growth_stays_exact():
    auto = A.build_automaton(Rules("AB", ("AB",)))                         # a(n) = n + 1
    res = ev.float_experiment(auto, 300)
    assert res["first_diff"] is None and res["first_overflow"] is None


# ----------------------------------------------------------------------------- Experiment 4

def test_verdict_guess_cases():
    assert ev.verdict_guess(None)[0] == "info"
    assert ev.verdict_guess({"r_min": None, "terms": 60})[0] == "warning"
    rows = [{"r": 1, "fits_until": 1, "ok": False}, {"r": 2, "fits_until": 3, "ok": False}, {"r": 3, "fits_until": 59, "ok": True}]
    res = {"r_min": 3, "terms": 60, "states": 3, "rows": rows, "effective_order": 3, "holds_from": 3}
    kind, text = ev.verdict_guess(res)
    assert kind == "warning"
    assert text == ("Die kleinste Rekursion, die alle 60 Glieder trifft, hat Ordnung 3; der Automat hat 3 Zustände. "
                    "Kleinere Ordnungen treffen nur den Anfang: Ordnung 2 gilt bis n = 3 und scheitert dann. Wer nur die ersten Glieder prüft, nimmt die falsche.")
    res_anlauf = dict(res, effective_order=2, holds_from=5)
    assert text + " Die wirksame Rekursion (Ordnung 2) gilt erst ab n = 5: davor gibt es einen Anlauf." == ev.verdict_guess(res_anlauf)[1]
    only_one = dict(res, rows=[{"r": 1, "fits_until": None, "ok": False}, rows[2]])
    assert ev.verdict_guess(only_one)[0] == "success"                      # keine kleinere Ordnung, die den Anfang trifft


def test_guess_experiment_finds_the_known_orders_and_the_run_in():
    def run(alphabet, patterns):
        return ev.guess_experiment(A.build_automaton(Rules(alphabet, patterns)))
    assert run("AB", ("AA",))["r_min"] == 2 and run("FSN", ("NF", "NNN"))["r_min"] == 3
    anlauf = run("ABC", ("AB", "BC", "CA", "AAA"))
    assert anlauf["r_min"] == 5 and anlauf["effective_order"] == 4 and anlauf["holds_from"] == 5
    assert ev.guess_experiment(A.build_automaton(Rules("ABC", ("AAAAAA", "BBBBBB", "CCCCCC")))) is None      # 16 Zustände: zu teuer


# ----------------------------------------------------------------------------- Experiment 5 und Spielwiese

def test_extrapolate_wall_scales_time_by_states_and_steps():
    rows = [{"m": 12, "t_dp": 1.0}]
    ex = {e["m"]: e for e in ev.extrapolate_wall(rows, targets=(14, 24))}
    assert abs(ex[14]["t_dp"] - 2 ** 2 * (14 / 12) ** 2) < 1e-9
    assert abs(ex[24]["t_dp"] - 2 ** 12 * 4) < 1e-6
    assert ex[14]["states"] == 2 ** 14 * 14 and ev.extrapolate_wall([]) == []


def test_verdict_wall_text():
    res = {"rows": [{"m": 12, "states": 49152, "fact": 479001600, "t_dp": 0.07}], "extrapolation": [{"m": 30, "states": 2 ** 30 * 30, "t_dp": 3_200_000.0, "fact": 1}]}
    kind, text = ev.verdict_wall(res)
    assert kind == "warning"
    assert text == ("Bei 12 Symbolen hat die Rekursion 49.152 Zustände und braucht 70,0 Millisekunden; Aufzählen müsste 479.001.600 Reihenfolgen prüfen. "
                    "Hochgerechnet auf 30 Symbole: 32,2 Milliarden Zustände, etwa 37,0 Tagen. Der Zustand selbst ist hier die Wand.")


def test_wall_experiment_checks_enumeration_against_the_recursion():
    res = ev.wall_experiment(8, 30, 35)
    assert res["problems"] == [] and [r["m"] for r in res["rows"]] == [4, 5, 6, 7, 8]
    assert all(r["states"] == 2 ** r["m"] * r["m"] and r["t_brute"] is not None for r in res["rows"])
    none_banned = ev.wall_experiment(7, 0, 1)
    assert [r["count"] for r in none_banned["rows"]] == [24, 120, 720, 5040]


def test_verdict_play_cases(schicht):
    auto = A.build_automaton(schicht)
    states, bad = A.trace_word(auto, "FSNN")
    kind, text = ev.verdict_play(auto, "FSNN", states, bad)
    assert kind == "success" and text == "Gültig. Der Automat merkt sich am Ende: „NN“. Er unterscheidet 3 Zustände."
    states, bad = A.trace_word(auto, "FSNNF")
    kind, text = ev.verdict_play(auto, "FSNNF", states, bad)
    assert kind == "warning" and text.startswith("Das Zeichen 5 („F“) vollendet ein Verbot")
    states, bad = A.trace_word(auto, "FS")
    assert "nichts (leerer Zustand)" in ev.verdict_play(auto, "FS", states, bad)[1]
    assert ev.verdict_play(auto, "", [""], None)[0] == "info"

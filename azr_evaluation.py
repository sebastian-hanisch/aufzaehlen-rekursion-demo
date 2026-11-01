"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import math
import time
from dataclasses import dataclass

import azr_algorithm as A
import azr_constants as C
from azr_scenario import Rules, make_banned_pairs, make_rules


@dataclass(frozen=True)
class Settings:
    alphabet: str = C.DEFAULT_ALPHABET     # Bezeichnung aus C.ALPHABETS
    patterns: str = C.DEFAULT_PATTERNS     # Eingabetext der Verbotsmuster
    n: int = C.DEFAULT_N


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    rules: Rules
    parse_problems: list
    auto: A.Automaton
    seq: list                              # a(0), ..., a(n) als ganze Zahlen
    problems: list                         # Meldungen des unabhängigen Prüfers

    @property
    def count(self) -> int:
        return self.seq[-1]

    @property
    def total(self) -> int:
        return self.rules.k ** self.settings.n

    @property
    def share(self) -> float:
        return self.count / self.total if self.total < 10 ** 300 else float(self.count * 10 ** 15 // self.total) / 10 ** 15

    @property
    def state_bound(self) -> int:
        """Obere Schranke der Zustandszahl: 1 + Summe über die Verbote von (Länge − 1)."""
        return 1 + sum(len(p) - 1 for p in self.rules.patterns)


def analyse(settings: Settings) -> Analysis:
    rules, parse_problems = make_rules(settings.alphabet, settings.patterns)
    auto = A.build_automaton(rules)
    seq = A.sequence(auto, settings.n)
    problems = A.check_count(rules, auto, settings.n, seq[-1], C.CHECK_BRUTE_MAX_N)
    return Analysis(settings, rules, parse_problems, auto, seq, problems)


# ----------------------------------------------------------------------------- Formatierung

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def de(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def pct(frac: float) -> str:
    """Anteil als Prozentzahl: ab 1 % mit einer Nachkommastelle, darunter mit zwei, unter 0,01 % als „unter 0,01 %“."""
    p = 100.0 * frac
    if 0 < p < 0.01:
        return "unter 0,01 %"
    return de(p, 1 if p >= 1.0 else 2) + " %"


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit der Zahl der Stellen. Exakt ab der angegebenen Stelle, nie über float."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d, lead = A.leading_digits(x, 3)
    s = str(lead)
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def count_text(n: float) -> str:
    """Große Zahlen in Worten: bis 9999 ausgeschrieben, darüber Tausend, Millionen, Milliarden, Billionen, darüber Zehnerpotenz."""
    if n < 10_000:
        return str(int(n))
    for scale, name in ((1e3, "Tausend"), (1e6, "Millionen"), (1e9, "Milliarden"), (1e12, "Billionen")):
        if n < scale * 1000:
            value = n / scale
            return f"{de(value, 0 if value >= 100 else 1)} {name}"
    e = int(math.floor(math.log10(n)))
    return f"{de(n / 10 ** e, 1)}·10{str(e).translate(_SUPER)}"


def time_text(seconds: float) -> str:
    """Dauer in der passenden Einheit; ab einem Jahr in Jahren."""
    if seconds < 1e-3:
        return f"{de(seconds * 1e6, 0 if seconds * 1e6 >= 100 else 1)} Mikrosekunden"
    if seconds < 1:
        return f"{de(seconds * 1e3, 0 if seconds * 1e3 >= 100 else 1)} Millisekunden"
    for limit, unit, div in ((60, "Sekunden", 1), (3600, "Minuten", 60), (86400, "Stunden", 3600), (365.25 * 86400, "Tagen", 86400)):
        if seconds < limit:
            return f"{de(seconds / div, 0 if seconds / div >= 100 else 1)} {unit}"
    years = seconds / (365.25 * 86400)
    return f"{de(years, 1)} Jahren" if years < 10_000 else f"{count_text(years)} Jahren"


def timed(f, *args):
    t0 = time.perf_counter()
    value = f(*args)
    return value, time.perf_counter() - t0


# ----------------------------------------------------------------------------- Experiment 1: Aufzählen gegen Rekursion

def enum_experiment(rules: Rules, budget: float = C.ENUM_BUDGET, n_max: int = C.ENUM_N_MAX) -> dict:
    """Misst Aufzählen (alle Wörter prüfen), Aufzählen mit Abschneiden und die Rekursion für n = ENUM_N_MIN, ...; jede Spalte hört auf, wenn eine
    Zeile länger als `budget` Sekunden gebraucht hat. Alle drei Zahlen müssen übereinstimmen, sonst steht eine Meldung in `problems`."""
    auto = A.build_automaton(rules)
    rows, problems = [], []
    stop_brute = stop_dfs = False
    for n in range(C.ENUM_N_MIN, n_max + 1):
        valid, t_rec = timed(A.count_dp, auto, n)
        row = {"n": n, "all": rules.k ** n, "valid": valid, "t_brute": None, "t_dfs": None, "t_rec": t_rec}
        if not stop_brute:
            v, row["t_brute"] = timed(A.brute_count, rules, n)
            stop_brute = row["t_brute"] > budget
            if v != valid:
                problems.append(f"n = {n}: Brute Force {v}, Rekursion {valid}")
        if not stop_dfs:
            v, row["t_dfs"] = timed(A.dfs_count, rules, n)
            stop_dfs = row["t_dfs"] > budget
            if v != valid:
                problems.append(f"n = {n}: Abschneiden {v}, Rekursion {valid}")
        rows.append(row)
        if stop_brute and stop_dfs:
            break
    return {"rules": rules, "rows": rows, "problems": problems, "extrapolation": extrapolate_enum(rules, auto, rows)}


def rate_per_unit(rows: list, time_key: str, unit_of) -> float | None:
    """Sekunden je Einheit (Wort bzw. gültiges Wort) in der letzten gemessenen Zeile; None, wenn nichts gemessen wurde oder die Einheit 0 ist."""
    for row in reversed(rows):
        if row.get(time_key) is not None and unit_of(row) > 0:
            return row[time_key] / unit_of(row)
    return None


def extrapolate_enum(rules: Rules, auto: A.Automaton, rows: list, targets=C.ENUM_TARGETS) -> list:
    """Hochrechnung (nicht gemessen): Zeit je Wort der letzten Messzeile mal Zahl der Wörter bei der Zielgröße; die Rekursion wird dagegen am Ziel gemessen."""
    rate_brute = rate_per_unit(rows, "t_brute", lambda r: r["all"])
    rate_dfs = rate_per_unit(rows, "t_dfs", lambda r: r["valid"])
    out = []
    for target in targets:
        valid, t_rec = timed(A.count_dp, auto, target)
        out.append({
            "n": target, "valid": valid, "t_rec": t_rec,
            "t_brute": None if rate_brute is None else rate_brute * rules.k ** target,
            "t_dfs": None if rate_dfs is None or valid == 0 else rate_dfs * valid,
        })
    return out


def verdict_enum(res: dict, target: int = 30) -> tuple[str, str]:
    rows = res["rows"]
    last = next((r for r in reversed(rows) if r["t_dfs"] is not None), None)
    ex = next((e for e in res["extrapolation"] if e["n"] == target), None)
    if last is None or ex is None or ex["t_dfs"] is None:
        return "info", "Mit diesen Regeln gibt es nichts zum Hochrechnen: Es gibt keine gültigen Folgen, oder es wurde nichts gemessen."
    factor = last["t_dfs"] / max(last["t_rec"], 1e-9)
    text = (f"Bei n = {last['n']} braucht das Aufzählen mit Abschneiden {time_text(last['t_dfs'])}, die Rekursion {time_text(last['t_rec'])} "
            f"(etwa Faktor {count_text(factor)}). Hochgerechnet auf n = {target}: Aufzählen etwa {time_text(ex['t_dfs'])}, "
            f"die Rekursion braucht gemessen {time_text(ex['t_rec'])}.")
    return ("success" if factor >= 10 else "info"), text


# ----------------------------------------------------------------------------- Experiment 2: Rekursion im Großen

def large_experiment(auto: A.Automaton, sizes=C.LARGE_SIZES, budget: float = C.LARGE_BUDGET) -> list:
    """Exakte ganze Zahlen für große n; Größen, die das Zeitbudget sprengen würden, werden übersprungen (skipped=True)."""
    rows, spent = [], 0.0
    for n in sizes:
        if spent > budget:
            rows.append({"n": n, "digits": None, "seconds": None, "skipped": True})
            continue
        value, t = timed(A.count_dp, auto, n)
        spent += t
        rows.append({"n": n, "digits": A.digit_count(value), "seconds": t, "skipped": False})
    return rows


def verdict_large(rows: list) -> tuple[str, str]:
    done = [r for r in rows if not r["skipped"]]
    if not done:
        return "warning", "Alle Größen wurden übersprungen."
    last = done[-1]
    if last["digits"] == 1:
        return "info", f"Bei n = {last['n']} gibt es höchstens eine einstellige Zahl von Folgen: Mit diesen Regeln ist nichts zu zählen."
    return "success", (f"Bei n = {last['n']} hat die Anzahl {last['digits']} Stellen und ist in {time_text(last['seconds'])} exakt ausgerechnet. "
                       "Aufzählen müsste jede dieser Folgen einzeln anfassen.")


# ----------------------------------------------------------------------------- Experiment 3: Gleitkomma statt ganzer Zahlen

def float_experiment(auto: A.Automaton, n_max: int = C.FLOAT_N_MAX) -> dict:
    """Dieselbe Rekursion mit Gleitkommazahlen: erstes n, bei dem der ganzzahlige Anteil vom exakten Wert abweicht, und erstes n mit Überlauf (inf)."""
    exact = A.sequence(auto, n_max)
    approx = A.sequence(auto, n_max, float)
    first_diff = first_overflow = None
    for n, f in enumerate(approx):
        if f == math.inf:
            first_overflow = n
            break
        if first_diff is None and int(f) != exact[n]:
            first_diff = n
    return {"first_diff": first_diff, "first_overflow": first_overflow, "n_max": n_max}


def verdict_float(res: dict) -> tuple[str, str]:
    d, o, n_max = res["first_diff"], res["first_overflow"], res["n_max"]
    if d is None and o is None:
        return "info", f"Bis n = {n_max} stimmt die Gleitkommarechnung hier auf die letzte Stelle: Die Zahlen wachsen so langsam, dass 53 Bit reichen."
    parts = []
    if d is not None:
        parts.append(f"ab n = {d} weicht das Gleitkommaergebnis vom exakten ab")
    if o is not None:
        parts.append(f"ab n = {o} läuft es über (unendlich)")
    return "warning", "Mit Gleitkommazahlen gilt: " + " und ".join(parts) + ". Ganze Zahlen kennen beide Grenzen nicht."


# ----------------------------------------------------------------------------- Experiment 4: Rekursion raten statt herleiten

def guess_experiment(auto: A.Automaton, rmax: int = C.GUESS_RMAX, terms: int = C.GUESS_TERMS) -> dict | None:
    """Für r = 1, 2, ...: die Rekursion der Ordnung r aus den ersten 2r Gliedern bestimmen und prüfen, bis wohin sie die Folge trifft.
    None, wenn der Automat zu viele Zustände hat (Bruchrechnung zu teuer für die App)."""
    if auto.size > C.GUESS_MAX_STATES:
        return None
    a = A.sequence(auto, terms - 1)
    rows, r_min, coeffs = [], None, None
    for r in range(1, rmax + 1):
        if len(a) < 2 * r + 1:
            break
        c = A.solve_recurrence(a, r)
        if c is None:
            rows.append({"r": r, "singular": True, "fits_until": None, "ok": False})
            continue
        fu = A.fits_until(a, c)
        ok = fu == len(a) - 1
        rows.append({"r": r, "singular": False, "fits_until": fu, "ok": ok})
        if ok and r_min is None:
            r_min, coeffs = r, c
    eff = holds_from = None
    if coeffs is not None:
        eff = max((j + 1 for j, v in enumerate(coeffs) if v != 0), default=0)
        holds_from = eff
        for n in range(len(a) - 1, eff - 1, -1):
            if eff == 0 or a[n] != sum(coeffs[j - 1] * a[n - j] for j in range(1, eff + 1)):
                holds_from = n + 1
                break
    return {"states": auto.size, "terms": len(a), "rows": rows, "r_min": r_min, "coeffs": coeffs, "effective_order": eff, "holds_from": holds_from}


def verdict_guess(res: dict | None) -> tuple[str, str]:
    if res is None:
        return "info", f"Mit mehr als {C.GUESS_MAX_STATES} Zuständen ist die Bruchrechnung für das Raten in der App zu teuer."
    if res["r_min"] is None:
        return "warning", f"Bis Ordnung {C.GUESS_RMAX} passt keine Rekursion zu den ersten {res['terms']} Gliedern: Raten findet hier nichts."
    wrong = [r for r in res["rows"] if r["r"] < res["r_min"] and r["fits_until"] is not None]
    text = f"Die kleinste Rekursion, die alle {res['terms']} Glieder trifft, hat Ordnung {res['r_min']}; der Automat hat {res['states']} Zustände. "
    if wrong:
        best = max(wrong, key=lambda r: r["fits_until"])
        text += (f"Kleinere Ordnungen treffen nur den Anfang: Ordnung {best['r']} gilt bis n = {best['fits_until']} und scheitert dann. "
                 "Wer nur die ersten Glieder prüft, nimmt die falsche.")
    if res["holds_from"] is not None and res["holds_from"] > res["effective_order"]:
        text += f" Die wirksame Rekursion (Ordnung {res['effective_order']}) gilt erst ab n = {res['holds_from']}: davor gibt es einen Anlauf."
    return ("warning" if wrong else "success"), text


# ----------------------------------------------------------------------------- Experiment 5: zweite Wand

def wall_experiment(m_max: int, density: int, seed: int) -> dict:
    """Reihenfolgen von m Symbolen, jedes genau einmal, mit verbotenen Nachbarpaaren: Zustand = (Menge, letztes Symbol).
    Rekursion für m = WALL_M_MIN, ..., m_max; die Aufzählung (m! Reihenfolgen) nur bis WALL_BRUTE_MAX und gegen die Rekursion geprüft."""
    rows, problems = [], []
    for m in range(C.WALL_M_MIN, m_max + 1):
        banned = make_banned_pairs(m, density, seed)
        count, t_dp = timed(A.perm_count_dp, m, banned)
        row = {"m": m, "fact": math.factorial(m), "states": A.perm_state_count(m), "count": count, "t_dp": t_dp, "t_brute": None}
        if m <= C.WALL_BRUTE_MAX:
            brute, row["t_brute"] = timed(A.perm_count_brute, m, banned)
            if brute != count:
                problems.append(f"m = {m}: Aufzählung {brute}, Rekursion {count}")
        rows.append(row)
    return {"rows": rows, "problems": problems, "extrapolation": extrapolate_wall(rows)}


def extrapolate_wall(rows: list, targets=C.WALL_TARGETS) -> list:
    """Hochrechnung (nicht gemessen): Zeit der letzten Zeile mal 2^(Ziel − m) mal (Ziel / m)², denn es sind 2^m · m Zustände mit je m Schritten."""
    if not rows:
        return []
    ref = rows[-1]
    return [{"m": t, "states": A.perm_state_count(t), "t_dp": ref["t_dp"] * 2.0 ** (t - ref["m"]) * (t / ref["m"]) ** 2, "fact": math.factorial(t)} for t in targets]


def verdict_wall(res: dict, target: int = 30) -> tuple[str, str]:
    rows = res["rows"]
    if not rows:
        return "info", "Nichts gemessen."
    last = rows[-1]
    ex = next(e for e in res["extrapolation"] if e["m"] == target)
    return "warning", (f"Bei {last['m']} Symbolen hat die Rekursion {big_text(last['states'])} Zustände und braucht {time_text(last['t_dp'])}; Aufzählen müsste "
                       f"{big_text(last['fact'])} Reihenfolgen prüfen. Hochgerechnet auf {target} Symbole: {count_text(ex['states'])} Zustände, "
                       f"etwa {time_text(ex['t_dp'])}. Der Zustand selbst ist hier die Wand.")


# ----------------------------------------------------------------------------- Kernfrage und Spielwiese

def verdict_count(a: Analysis) -> tuple[str, str]:
    n, k = a.settings.n, a.rules.k
    if a.count == 0:
        return "warning", f"Mit diesen Regeln gibt es keine gültige Folge der Länge {n}: die Verbote schließen alles aus."
    if a.count == a.total:
        return "info", f"Keine Regel schränkt etwas ein: alle {big_text(a.total)} Folgen der Länge {n} sind gültig."
    return "success", (f"Von den {k}^{n} = {big_text(a.total)} möglichen Folgen der Länge {n} sind **{big_text(a.count)}** gültig, das sind {pct(a.share)}. "
                       f"Die Rekursion merkt sich dafür nur **{a.auto.size} Zustände**.")


def verdict_play(auto: A.Automaton, word: str, states: list, bad: int | None) -> tuple[str, str]:
    if not word:
        return "info", "Noch kein Wort eingegeben."
    if bad is not None:
        return "warning", f"Das Zeichen {bad + 1} („{word[bad]}“) vollendet ein Verbot: Die Folge ist ungültig, der Automat merkt sich nichts mehr."
    last = states[-1]
    return "success", f"Gültig. Der Automat merkt sich am Ende: {'„' + last + '“' if last else 'nichts (leerer Zustand)'}. Er unterscheidet {auto.size} Zustände."

"""Kern der Demo (nur Standardbibliothek): Folgen mit verbotenen Teilfolgen zählen, durch Aufzählen und durch Rekursion über einen Zustand.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b):
`brute_count` und `dfs_count` zählen auf, `build_automaton` leitet das Gedächtnis der Regeln ab, `count_dp` rechnet damit,
`count_matrix` ist der unabhängige Prüfer (Matrixpotenz statt Vektorschritten), `trace_word` lässt den Automaten ein Wort lesen.
Dazu die Rekursion raten (`smallest_recurrence`) und die zweite Wand (`perm_count_dp`: Zustand = Menge × letztes Symbol)."""

import itertools
import math
from dataclasses import dataclass
from fractions import Fraction

from azr_scenario import Rules


# ----------------------------------------------------------------------------- Aufzählen

def is_valid(word: str, patterns) -> bool:
    return not any(p in word for p in patterns)


def brute_count(rules: Rules, n: int) -> int:
    """Alle k^n Wörter erzeugen und jedes einzeln prüfen."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    return sum(1 for w in itertools.product(rules.alphabet, repeat=n) if is_valid("".join(w), rules.patterns))


def dfs_count(rules: Rules, n: int) -> int:
    """Nur gültige Präfixe erweitern (Aufzählen mit Abschneiden): zählt die Blätter in der Tiefe n."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")

    def rek(prefix: str, rest: int) -> int:
        if rest == 0:
            return 1
        total = 0
        for c in rules.alphabet:
            t = prefix + c
            if any(t.endswith(p) for p in rules.patterns):
                continue
            total += rek(t, rest - 1)
        return total

    return rek("", n)


def enumerate_valid(rules: Rules, n: int) -> list[str]:
    """Alle gültigen Wörter der Länge n in lexikografischer Reihenfolge (für kleine n: Anzeige und Handprüfung)."""
    return [w for w in ("".join(t) for t in itertools.product(rules.alphabet, repeat=n)) if is_valid(w, rules.patterns)]


# ----------------------------------------------------------------------------- Automat = das Gedächtnis der Regeln

@dataclass(frozen=True, eq=False)
class Automaton:
    alphabet: str
    states: tuple[str, ...]                          # erreichbare Zustände, kürzeste zuerst, leeres Wort = Startzustand
    trans: dict                                      # (Zustand, Zeichen) -> Folgezustand oder None (Verbot)

    @property
    def size(self) -> int:
        return len(self.states)


def build_automaton(rules: Rules) -> Automaton:
    """Zustand = längstes Ende des bisher gelesenen Wortes, das ein Anfang eines Verbots ist.

    Mehr muss man sich nicht merken: ob ein Verbot gleich vollständig wird, hängt nur davon ab. Die Zahl der Zustände ist höchstens
    1 + Summe über die Verbote von (Länge − 1)."""
    for p in rules.patterns:
        if not p or set(p) - set(rules.alphabet):
            raise ValueError(f"ungültiges Verbotsmuster {p!r}")
    prefixes = {p[:i] for p in rules.patterns for i in range(len(p))}   # echte Anfänge inklusive leerem Wort

    def step(state: str, c: str):
        t = state + c
        if any(t.endswith(p) for p in rules.patterns):
            return None
        for i in range(len(t) + 1):
            if t[i:] in prefixes:
                return t[i:]
        return ""

    reached = {""}
    todo = [""]
    trans = {}
    while todo:
        z = todo.pop()
        for c in rules.alphabet:
            t = step(z, c)
            trans[(z, c)] = t
            if t is not None and t not in reached:
                reached.add(t)
                todo.append(t)
    return Automaton(rules.alphabet, tuple(sorted(reached, key=lambda s: (len(s), s))), trans)


def sequence(auto: Automaton, n: int, number=int) -> list:
    """a(0), ..., a(n): Zahl der gültigen Wörter jeder Länge, in einem Lauf. `number` ist int (exakt) oder float."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    vec = {z: number(0) for z in auto.states}
    vec[""] = number(1)
    out = [number(1)]
    for _ in range(n):
        new = {z: number(0) for z in auto.states}
        for z, w in vec.items():
            if w == 0:
                continue
            for c in auto.alphabet:
                t = auto.trans[(z, c)]
                if t is not None:
                    new[t] += w
        vec = new
        out.append(sum(vec.values()))
    return out


def count_dp(auto: Automaton, n: int) -> int:
    return sequence(auto, n)[-1]


def count_matrix(auto: Automaton, n: int) -> int:
    """Unabhängiger Prüfer: dieselbe Zahl als Matrixpotenz der Übergangsmatrix (ganze Zahlen), nicht als Vektorschritte."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    idx = {z: i for i, z in enumerate(auto.states)}
    size = len(idx)
    m = [[0] * size for _ in range(size)]
    for (z, _c), t in auto.trans.items():
        if t is not None:
            m[idx[z]][idx[t]] += 1

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(size) if a[i][k]) for j in range(size)] for i in range(size)]

    result = [[int(i == j) for j in range(size)] for i in range(size)]
    base, e = m, n
    while e:
        if e & 1:
            result = mul(result, base)
        base = mul(base, base)
        e >>= 1
    return sum(result[idx[""]])


def check_count(rules: Rules, auto: Automaton, n: int, count: int, brute_max_n: int) -> list[str]:
    """Unabhängiger Prüfer des angezeigten Ergebnisses (läuft auch in der App): Meldungen, leer wenn alles stimmt."""
    problems = []
    if not 0 <= count <= rules.k ** n:
        problems.append(f"{count} liegt nicht zwischen 0 und {rules.k}^{n}")
    if count_matrix(auto, n) != count:
        problems.append("Matrixpotenz und Vektorrekursion gaben verschiedene Zahlen")
    if n <= brute_max_n and brute_count(rules, n) != count:
        problems.append("Aufzählen und Rekursion gaben verschiedene Zahlen")
    return problems


def trace_word(auto: Automaton, word: str):
    """Der Automat liest `word`: (Zustände nach jedem Zeichen einschließlich Start, Index des ersten Zeichens, das ein Verbot vollendet, sonst None).

    Zeichen außerhalb des Alphabets sind ein Fehler des Aufrufers (ValueError)."""
    states = [""]
    for i, c in enumerate(word):
        if c not in auto.alphabet:
            raise ValueError(f"Zeichen {c!r} gehört nicht zum Alphabet")
        t = auto.trans[(states[-1], c)]
        if t is None:
            return states, i
        states.append(t)
    return states, None


def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x ≥ 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen, 3^10000 hat 4772)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def leading_digits(x: int, count: int) -> tuple[int, int]:
    """(Zahl der Stellen von x, die ersten `count` Stellen als ganze Zahl; x selbst, wenn es nicht länger ist). Ohne Umwandlung der ganzen Zahl in einen String."""
    d = digit_count(x)
    return d, (x if d <= count else x // 10 ** (d - count))


def growth_ratio(a: list[int], digits: int = 10) -> float | None:
    """a(n) / a(n-1) für die letzten beiden Glieder, auch für riesige ganze Zahlen (ohne Überlauf); None ohne Vorgänger oder bei a(n-1) = 0."""
    if len(a) < 2 or a[-2] == 0:
        return None
    scale = 10 ** digits
    return (a[-1] * scale // a[-2]) / scale


# ----------------------------------------------------------------------------- Rekursion raten

def solve_recurrence(a: list[int], r: int):
    """Koeffizienten c_1..c_r mit a(n) = Σ c_j a(n−j) aus den Gliedern a(0)..a(2r−1) (Brüche); None, wenn das System singulär ist."""
    if r < 1 or len(a) < 2 * r:
        return None
    m = [[Fraction(a[n - j]) for j in range(1, r + 1)] + [Fraction(a[n])] for n in range(r, 2 * r)]
    for i in range(r):
        p = next((k for k in range(i, r) if m[k][i] != 0), None)
        if p is None:
            return None
        m[i], m[p] = m[p], m[i]
        d = m[i][i]
        m[i] = [x / d for x in m[i]]
        for k in range(r):
            if k != i and m[k][i] != 0:
                f = m[k][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][r] for i in range(r)]


def fits_until(a: list[int], c) -> int | None:
    """Größtes n, bis zu dem die Rekursion mit den Koeffizienten c alle Glieder ab n = len(c) trifft; None, wenn sie schon beim ersten Glied scheitert,
    len(a) − 1, wenn sie alle trifft."""
    r = len(c)
    last_ok = None
    for n in range(r, len(a)):
        if a[n] != sum(c[j - 1] * a[n - j] for j in range(1, r + 1)):
            return last_ok if last_ok is not None else r - 1
        last_ok = n
    return len(a) - 1


def smallest_recurrence(a: list[int], rmax: int):
    """Kleinste Ordnung r ≤ rmax, deren aus 2r Gliedern bestimmte Rekursion alle weiteren Glieder von a trifft; (r, Koeffizienten) oder (None, None)."""
    for r in range(1, rmax + 1):
        if len(a) < 2 * r + 1:
            break
        c = solve_recurrence(a, r)
        if c is not None and fits_until(a, c) == len(a) - 1:
            return r, c
    return None, None


# ----------------------------------------------------------------------------- zweite Wand: jedes Symbol genau einmal

def perm_count_brute(m: int, banned) -> int:
    """Alle m! Reihenfolgen prüfen: kein verbotenes (Vorgänger, Nachfolger)-Paar darf vorkommen."""
    if m < 0:
        raise ValueError("m darf nicht negativ sein")
    return sum(1 for p in itertools.permutations(range(m)) if all((p[i], p[i + 1]) not in banned for i in range(m - 1)))


def perm_count_dp(m: int, banned) -> int:
    """Zustand = (Menge schon benutzter Symbole, letztes Symbol): 2^m · m Zustände, O(2^m · m²) Schritte."""
    if m < 0:
        raise ValueError("m darf nicht negativ sein")
    if m == 0:
        return 1
    dp = [[0] * m for _ in range(1 << m)]
    for i in range(m):
        dp[1 << i][i] = 1
    for mask in range(1, 1 << m):
        row = dp[mask]
        for last in range(m):
            w = row[last]
            if w:
                for nxt in range(m):
                    if not (mask >> nxt) & 1 and (last, nxt) not in banned:
                        dp[mask | (1 << nxt)][nxt] += w
    return sum(dp[(1 << m) - 1])


def perm_state_count(m: int) -> int:
    return (1 << m) * m


def factorial(m: int) -> int:
    return math.factorial(m)

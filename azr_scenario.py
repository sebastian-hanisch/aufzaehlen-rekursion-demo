"""Szenario: Regelsätze für Folgen über einem kleinen Alphabet (verbotene Teilfolgen) und verbotene Nachbarpaare für die zweite Wand."""

import random
import re
from dataclasses import dataclass

import azr_constants as C


@dataclass(frozen=True)
class Rules:
    """Alphabet und verbotene Teilfolgen: eine Folge ist gültig, wenn keines der Muster als zusammenhängende Teilfolge vorkommt."""
    alphabet: str
    patterns: tuple[str, ...]

    @property
    def k(self) -> int:
        return len(self.alphabet)


def alphabet_of(label: str) -> str:
    """Alphabet zur Auswahl im Regler; unbekannte Bezeichnungen fallen auf das Standardalphabet zurück."""
    return C.ALPHABETS.get(label, C.ALPHABETS[C.DEFAULT_ALPHABET])


def parse_patterns(text: str, alphabet: str) -> tuple[tuple[str, ...], list[str]]:
    """Verbotsmuster aus einem Eingabetext (getrennt durch Komma, Semikolon oder Leerraum), Groß-/Kleinschreibung egal.

    Gibt (Muster in Eingabereihenfolge ohne Doppelte, Meldungen) zurück. Ungültige Muster werden verworfen und gemeldet, nie still ersetzt."""
    patterns: list[str] = []
    problems: list[str] = []
    for raw in re.split(r"[,;\s]+", text[: C.PATTERN_TEXT_MAX * 4].upper()):
        if not raw:
            continue
        bad = sorted(set(raw) - set(alphabet))
        if bad:
            problems.append(f"„{raw}“ enthält Zeichen außerhalb des Alphabets ({' '.join(bad)}) und zählt nicht.")
            continue
        if len(raw) > C.PATTERN_MAX_LEN:
            problems.append(f"„{raw}“ ist länger als {C.PATTERN_MAX_LEN} Zeichen und zählt nicht.")
            continue
        if raw not in patterns:
            patterns.append(raw)
    if len(patterns) > C.PATTERN_MAX_COUNT:
        problems.append(f"Mehr als {C.PATTERN_MAX_COUNT} Muster: nur die ersten {C.PATTERN_MAX_COUNT} zählen.")
        patterns = patterns[: C.PATTERN_MAX_COUNT]
    return tuple(patterns), problems


def make_rules(alphabet_label: str, patterns_text: str) -> tuple[Rules, list[str]]:
    alphabet = alphabet_of(alphabet_label)
    patterns, problems = parse_patterns(patterns_text, alphabet)
    return Rules(alphabet, patterns), problems


def make_banned_pairs(m: int, density_percent: int, seed: int) -> frozenset[tuple[int, int]]:
    """Verbotene (Vorgänger, Nachfolger)-Paare unter m Symbolen: jedes geordnete Paar a ≠ b ist mit der Wahrscheinlichkeit density/100 verboten.

    Deterministisch aus (m, density, seed); die Paare für m Symbole sind kein Anfang der Paare für m + 1 Symbole."""
    rng = random.Random(f"{seed}/{m}/{density_percent}")
    return frozenset((a, b) for a in range(m) for b in range(m) if a != b and rng.random() * 100 < density_percent)

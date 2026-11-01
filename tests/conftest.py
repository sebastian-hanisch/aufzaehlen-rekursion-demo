"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from azr_scenario import Rules  # noqa: E402


@pytest.fixture
def fib():
    """Wörter aus A und B ohne AA. Handrechnung für n = 4: ABAB, ABBA, ABBB, BABA, BABB, BBAB, BBBA, BBBB = 8 Wörter (Fibonacci).
    Zustände: das leere Wort und „A“; ein A darf nur im leeren Zustand folgen."""
    return Rules("AB", ("AA",))


@pytest.fixture
def schicht():
    """Schichtfolgen aus F, S, N ohne NF und ohne NNN. Handrechnung: n = 1: 3; n = 2: 9 − 1 (NF) = 8; n = 3: 27 − 6 (NF an Stelle 1–2 oder 2–3, je 3 Wörter)
    − 1 (NNN) = 20. Zustände: leer, „N“, „NN“."""
    return Rules("FSN", ("NF", "NNN"))

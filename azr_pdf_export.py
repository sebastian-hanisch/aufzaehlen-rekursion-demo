"""PDF-Export der aktuellen Regeln mit Anzahl, Zuständen und den ersten Gliedern (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from azr_evaluation import Analysis, big_text, pct

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "✗": "x", "⁻": "-"}
MAX_ROWS = 40


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    for sup, digit in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"):
        out = out.replace(sup, digit)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    s = a.settings
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Folgen mit verbotenen Teilfolgen zählen"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    patterns = ", ".join(a.rules.patterns) if a.rules.patterns else "keine"
    pdf.multi_cell(0, 5, _s(f"Alphabet: {' '.join(a.rules.alphabet)}. Verbotene Teilfolgen: {patterns}. Länge n = {s.n}. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    lines = [
        f"Alle Folgen: {big_text(a.total)}.",
        f"Gültige Folgen: {big_text(a.count)} ({pct(a.share)}).",
        f"Zustände des Automaten: {a.auto.size} (höchstens {a.state_bound}).",
    ]
    for line in lines:
        pdf.multi_cell(0, 5, _s(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    head, widths = ["Länge", "alle Folgen", "gültige Folgen"], [22, 60, 60]
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(head, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for n in range(min(len(a.seq), MAX_ROWS)):
        row = [str(n), big_text(a.rules.k ** n), big_text(a.seq[n])]
        for v, w in zip(row, widths):
            pdf.cell(w, 5.5, _s(v), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Zustand = längstes Ende des gelesenen Wortes, das ein Anfang eines Verbots ist. Quelle: aufzaehlen-rekursion-demo, Sebastian Hanisch."),
                   new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())

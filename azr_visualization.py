"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import azr_algorithm as A
import azr_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)", separators=",.")
    return lock_axes(fig)


def _log10(x: int) -> float:
    """log10 einer beliebig großen ganzen Zahl (float(x) liefe für x > 1e308 über); 0 für x = 0 wird als None-Lücke übergeben."""
    d, lead = A.leading_digits(x, 15)
    return d - len(str(lead)) + math.log10(lead)


def build_counts(seq: list, k: int):
    """Zahl aller Folgen k^n und der gültigen a(n) über die Länge n (logarithmische Achse; Länge 0 ausgelassen, a(n) = 0 als Lücke)."""
    ns = list(range(1, len(seq)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[n * math.log10(k) for n in ns], mode="lines", name=f"alle Folgen ({k}ⁿ)", line=dict(color=C.COLOR_ALL, width=2.5, dash="dash")))
    fig.add_trace(go.Scatter(x=ns, y=[None if seq[n] == 0 else _log10(seq[n]) for n in ns], mode="lines+markers", name="gültige Folgen a(n)",
                             line=dict(color=C.COLOR_VALID, width=2.5), marker=dict(size=5)))
    fig.update_xaxes(title_text="Länge n")
    fig.update_yaxes(title_text="Anzahl (Zehnerpotenz, log₁₀)")
    return _base(fig)


def build_automaton(auto):
    """Zustände auf einem Kreis, Übergänge als Pfeile mit dem Zeichen; verbotene Übergänge zählen nicht (stehen in der Tabelle)."""
    fig = go.Figure()
    size = auto.size
    pos = {z: (math.cos(2 * math.pi * i / size - math.pi / 2), math.sin(2 * math.pi * i / size - math.pi / 2)) for i, z in enumerate(auto.states)}
    grouped: dict = {}
    for (z, c), t in auto.trans.items():
        if t is not None:
            grouped.setdefault((z, t), []).append(c)
    for (z, t), letters in grouped.items():
        x0, y0 = pos[z]
        x1, y1 = pos[t]
        label = ", ".join(sorted(letters))
        if z == t:
            fig.add_annotation(x=x0 * 1.28, y=y0 * 1.28, text=f"↻ {label}", showarrow=False, font=dict(size=12, color=C.COLOR_LINE))
            continue
        # Pfeil als Linie mit Pfeilspitze (Marker, der der Linie folgt): Annotationen mit leerem Text erzeugen im Browser Konsolenfehler (y = -Infinity)
        fig.add_trace(go.Scatter(
            x=[x0 * 0.88 + x1 * 0.12, x0 * 0.2 + x1 * 0.8, x1 * 0.88 + x0 * 0.12], y=[y0 * 0.88 + y1 * 0.12, y0 * 0.2 + y1 * 0.8, y1 * 0.88 + y0 * 0.12],
            mode="lines+markers", line=dict(color=C.COLOR_LINE, width=1.3),
            marker=dict(symbol="arrow", size=[0, 11, 0], angleref="previous", color=C.COLOR_LINE), hoverinfo="skip", showlegend=False))
        fig.add_annotation(x=(x0 + x1) / 2 + 0.07 * (y1 - y0), y=(y0 + y1) / 2 - 0.07 * (x1 - x0), text=label, showarrow=False, font=dict(size=13, color=C.COLOR_LINE))
    fig.add_trace(go.Scatter(
        x=[pos[z][0] for z in auto.states], y=[pos[z][1] for z in auto.states], mode="markers+text",
        text=[("Start" if z == "" else z) for z in auto.states], textposition="middle center",
        marker=dict(size=46, color=C.COLOR_NODE, line=dict(width=2, color=C.COLOR_VALID)), textfont=dict(color="#222"), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, range=[-1.6, 1.6])
    fig.update_yaxes(visible=False, range=[-1.6, 1.6], scaleanchor="x", scaleratio=1)
    return _base(fig, 420)


def build_timing(rows: list, extrapolation: list):
    """Gemessene Zeiten (Punkte) und Hochrechnung (gestrichelt) über die Länge; logarithmische Zeitachse."""
    fig = go.Figure()
    for key, name, color in (("t_brute", "alle Wörter prüfen", C.COLOR_FORBIDDEN), ("t_dfs", "Aufzählen mit Abschneiden", C.COLOR_LINE), ("t_rec", "Rekursion", C.COLOR_VALID)):
        xs = [r["n"] for r in rows if r[key] is not None]
        ys = [max(r[key], 1e-7) for r in rows if r[key] is not None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=name + " (gemessen)", line=dict(color=color, width=2.5), marker=dict(size=6)))
        if key != "t_rec" and xs and extrapolation:
            ex = [(e["n"], e[key]) for e in extrapolation if e[key] is not None]
            if ex:
                fig.add_trace(go.Scatter(x=[xs[-1]] + [x for x, _ in ex], y=[ys[-1]] + [y for _, y in ex], mode="lines", name=name + " (hochgerechnet)",
                                         line=dict(color=color, width=1.5, dash="dash")))
    ex_rec = [(e["n"], max(e["t_rec"], 1e-7)) for e in extrapolation]
    if ex_rec:
        fig.add_trace(go.Scatter(x=[x for x, _ in ex_rec], y=[y for _, y in ex_rec], mode="markers", name="Rekursion (am Ziel gemessen)", marker=dict(size=8, symbol="diamond", color=C.COLOR_VALID)))
    fig.update_xaxes(title_text="Länge n")
    fig.update_yaxes(title_text="Sekunden (logarithmisch)", type="log")
    return _base(fig, 400)


def build_wall(rows: list, extrapolation: list):
    """Zahl der Reihenfolgen m! gegen die Zustandszahl 2^m · m (logarithmisch) mit der gemessenen Rekursionszeit auf der zweiten Achse."""
    ms = [r["m"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ms, y=[_log10(r["fact"]) for r in rows], mode="lines+markers", name="Reihenfolgen m! (log₁₀)", line=dict(color=C.COLOR_FORBIDDEN, width=2.5)))
    fig.add_trace(go.Scatter(x=ms, y=[_log10(r["states"]) for r in rows], mode="lines+markers", name="Zustände 2ᵐ·m (log₁₀)", line=dict(color=C.COLOR_VALID, width=2.5)))
    fig.add_trace(go.Scatter(x=ms, y=[max(r["t_dp"], 1e-7) for r in rows], mode="lines+markers", name="Rekursion, Sekunden (rechte Achse)", yaxis="y2",
                             line=dict(color=C.COLOR_LINE, width=2, dash="dot")))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", type="log", title="Sekunden", fixedrange=True))
    fig.update_xaxes(title_text="Symbole m")
    fig.update_yaxes(title_text="Anzahl (log₁₀)")
    return _base(fig, 400)

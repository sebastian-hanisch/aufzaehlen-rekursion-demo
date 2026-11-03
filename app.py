"""Aufzählen und Rekursion – was man sich merken muss - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Wurzel der Reihe „Abzählen und erzeugende Funktionen“: Am Beispiel von Schichtfolgen mit verbotenen Teilfolgen zeigt die Demo, dass Aufzählen jede Folge einzeln
anfasst und früh aufgibt, während die Rekursion nur das Gedächtnis der Regeln (den Zustand) mitführt und riesige Zahlen exakt zählt. Bei Regeln, die sich alles
merken müssen (jedes Symbol genau einmal), wächst der Zustand selbst: die zweite Wand. Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import azr_algorithm as A
import azr_constants as C
from azr_evaluation import (
    Settings,
    analyse,
    big_text,
    count_text,
    de,
    enum_experiment,
    float_experiment,
    guess_experiment,
    large_experiment,
    time_text,
    verdict_count,
    verdict_enum,
    verdict_float,
    verdict_guess,
    verdict_large,
    verdict_play,
    verdict_wall,
    wall_experiment,
)
from azr_layout import dunkles_design, kopf_css
from azr_pdf_export import build_pdf
from azr_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from azr_scenario import make_rules
from azr_visualization import build_automaton, build_counts, build_timing, build_wall

st.set_page_config(page_title="Aufzählen und Rekursion – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _large(alphabet, patterns):
    return large_experiment(A.build_automaton(make_rules(alphabet, patterns)[0]))


@st.cache_data(show_spinner=False)
def _float(alphabet, patterns):
    return float_experiment(A.build_automaton(make_rules(alphabet, patterns)[0]))


@st.cache_data(show_spinner=False)
def _guess(alphabet, patterns):
    return guess_experiment(A.build_automaton(make_rules(alphabet, patterns)[0]))


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


def state_name(z):
    return "Start (leer)" if z == "" else z


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in azr_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Aufzählen und Rekursion – was man sich merken muss")
st.markdown(
    """
**Wie viele Schichtfolgen sind erlaubt?** Wer jede Folge einzeln prüft, gibt früh auf (Experiment 1 misst, wann). Die **Rekursion** zählt dieselbe Zahl, indem sie sich nur das **Gedächtnis der Regeln**
merkt, den **Zustand**, und rechnet auch sehr lange Folgen exakt aus (Experiment 2). Dies ist die Wurzel der Reihe „Abzählen und erzeugende Funktionen“; die Demo zeigt, wo dieses Gedächtnis klein bleibt
(Verbote zusammenhängender Teilfolgen) und wo es selbst explodiert (jedes Symbol genau einmal).

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/aufzaehlen-rekursion-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Gezählt wird, wie viele Folgen aus Schichten (hier Früh, Spät, Nacht) erlaubt sind, wenn bestimmte Schichten nicht direkt aufeinander folgen dürfen. **Jede Folge einzeln zu prüfen** gibt früh auf. Die **Rekursion** merkt sich stattdessen nur, **wie die Folge gerade endet** (das Gedächtnis der Regeln, der Zustand), und rechnet Tag für Tag weiter. Folgen, die gleich enden, haben dieselben erlaubten Fortsetzungen; man braucht nur ihre Anzahl.

**Wie groß muss dieses Gedächtnis sein?** Bei Verboten zusammenhängender Teilfolgen bleibt es klein. Bei „jedes Symbol genau einmal“ muss man sich merken, welche Symbole schon benutzt sind, und es wächst selbst sehr schnell (die zweite Wand). Alles ist gerechnet, nichts stammt aus echten Dienstplänen; Zeiten sind Messungen dieses Rechners.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/aufzaehlen-rekursion-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert die Rekursion", expanded=True):
    st.markdown(
        """
1. **Regeln:** Ein Alphabet (hier Schichten) und **verbotene Teilfolgen**, etwa „Nacht, dann Früh“. Eine Folge ist gültig, wenn kein Verbot als zusammenhängende Teilfolge vorkommt.
2. **Gedächtnis:** Ob das nächste Zeichen ein Verbot vollendet, hängt nur vom **längsten Ende der Folge ab, das ein Anfang eines Verbots ist**. Das ist der Zustand.
3. **Rekursion:** Für jeden Zustand steht, wie viele gültige Folgen dort enden. Ein Schritt verteilt diese Zahlen auf die Folgezustände; verbotene Übergänge entfallen.
4. **Warum das zählt:** Folgen, die im selben Zustand enden, haben dieselben Fortsetzungen. Man muss sie nicht einzeln kennen, nur ihre Anzahl.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Regeln**")
    alphabet = st.selectbox("Alphabet", list(C.ALPHABETS), key="alphabet_select", help="Die Zeichen, aus denen die Folgen bestehen.")
    patterns = st.text_input("Verbotene Teilfolgen", key="patterns_input", max_chars=C.PATTERN_TEXT_MAX,
                             help=f"Durch Komma getrennt, nur Zeichen des Alphabets, höchstens {C.PATTERN_MAX_COUNT} Muster mit je höchstens {C.PATTERN_MAX_LEN} Zeichen. "
                                  "Beispiel „NF, NNN“: nie Früh direkt nach Nacht, nie drei Nächte hintereinander.")
    n = st.slider("Länge n", *bounds("n_slider"), key="n_slider", help="Wie viele Zeichen (Tage) die Folge hat.")

sync_query_params({"alphabet_select": alphabet, "patterns_input": patterns, "n_slider": int(n)})

settings = Settings(alphabet, patterns, int(n))
a = _analysis(settings)
for message in a.parse_problems:
    st.warning(message)
if a.problems:   # unabhängiger Prüfer, nicht nur im Test: lieber eine Fehlermeldung als eine stille falsche Zahl
    st.error("Die Zählung besteht den Prüfer nicht: " + "; ".join(a.problems))

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Gültige Folgen a(n)", big_text(a.count), help="Anzahl der Folgen der Länge n, die kein Verbot enthalten; exakt gerechnet.")
m2.metric("Alle Folgen", big_text(a.total), help="Anzahl aller Folgen der Länge n ohne Regeln: Zeichenzahl hoch n.")
m3.metric("Zustände", f"{a.auto.size}", help=f"So viele Dinge muss sich die Rekursion merken. Höchstens {a.state_bound} (1 plus die Summe der Verbotslängen minus 1).")
ratio = A.growth_ratio(a.seq)
m4.metric("Wachstum a(n)/a(n−1)", "–" if ratio is None else de(ratio, 4), help="Faktor, um den die Anzahl pro zusätzlichem Tag wächst. Er pendelt sich schnell ein (Stück 2 erklärt auf welchen Wert).")
if len(a.seq) > 1:
    st.plotly_chart(build_counts(a.seq, a.rules.k), width="stretch", key="main_chart")
    st.caption("Grau gestrichelt: alle Folgen. Grün: die gültigen. Der Abstand der beiden Linien ist der Anteil, den die Regeln wegnehmen (logarithmische Achse).")

if st.button("📄 PDF der aktuellen Regeln erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="gueltige-folgen.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Folgen sind erlaubt, ohne sie aufzuzählen?")
verdict(verdict_count(a))

st.markdown("### Das Gedächtnis der Regeln")
st.caption("Jede Zeile ist ein Zustand: das längste Ende der bisherigen Folge, das ein Anfang eines Verbots ist. Die Spalten sagen, in welchen Zustand das nächste Zeichen führt; ✗ heißt verboten.")
st.dataframe(
    [{"Zustand": state_name(z), **{c: ("✗ verboten" if a.auto.trans[(z, c)] is None else state_name(a.auto.trans[(z, c)])) for c in a.rules.alphabet}} for z in a.auto.states],
    hide_index=True, width="stretch",
)
if 2 <= a.auto.size <= 8:
    st.plotly_chart(build_automaton(a.auto), width="stretch", key="automaton_chart")
    st.caption("Pfeile: Übergänge mit dem gelesenen Zeichen. Verbotene Übergänge sind nicht gezeichnet (siehe Tabelle).")
elif a.auto.size > 8:
    st.info(f"Mit {a.auto.size} Zuständen ist ein Bild nicht mehr lesbar; die Tabelle zeigt alle Übergänge.")

with st.expander("Die gültigen Folgen von Hand ansehen"):
    n_show = st.slider("Länge", 1, 6, 3, key="show_n", help="Bis Länge 6 lassen sich alle Folgen noch auflisten.")
    words = A.enumerate_valid(a.rules, n_show)
    st.markdown(f"**{len(words)} von {a.rules.k ** n_show}** Folgen der Länge {n_show} sind gültig (Rekursion: {big_text(a.seq[n_show] if n_show < len(a.seq) else A.count_dp(a.auto, n_show))}).")
    st.code(", ".join(words[:300]) + (" …" if len(words) > 300 else "") if words else "(keine)")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Wo gibt das Aufzählen auf?")
st.caption("Drei Wege zur selben Zahl: jedes Wort prüfen, nur gültige Anfänge erweitern, Rekursion. Gemessen wird auf dem Rechner, der diese App ausführt (Python); "
           f"jede Spalte hört auf, wenn eine Zeile länger als {de(C.ENUM_BUDGET, 0)} Sekunde gebraucht hat. Rechnet einige Sekunden.")
if st.button("🔬 Zeiten messen", key="enum_run"):
    st.session_state["enum_res"] = enum_experiment(a.rules)
enum_res = st.session_state.get("enum_res")
if enum_res and enum_res["rules"] == a.rules:
    for problem in enum_res["problems"]:
        st.error(problem)
    st.plotly_chart(build_timing(enum_res["rows"], enum_res["extrapolation"]), width="stretch", key="timing_chart")
    st.dataframe(
        [{"n": r["n"], "alle Folgen": big_text(r["all"]), "gültig": big_text(r["valid"]),
          "alle prüfen": "–" if r["t_brute"] is None else time_text(r["t_brute"]),
          "mit Abschneiden": "–" if r["t_dfs"] is None else time_text(r["t_dfs"]), "Rekursion": time_text(r["t_rec"])} for r in enum_res["rows"]],
        hide_index=True, width="stretch",
    )
    st.markdown("**Hochrechnung** (nicht gemessen): Zeit je Wort der letzten Messzeile mal Zahl der Wörter. Nur die Rekursion ist am Ziel gemessen.")
    st.dataframe(
        [{"n": e["n"], "gültige Folgen": big_text(e["valid"]), "alle prüfen (hochgerechnet)": "–" if e["t_brute"] is None else time_text(e["t_brute"]),
          "mit Abschneiden (hochgerechnet)": "–" if e["t_dfs"] is None else time_text(e["t_dfs"]), "Rekursion (gemessen)": time_text(e["t_rec"])} for e in enum_res["extrapolation"]],
        hide_index=True, width="stretch",
    )
    verdict(verdict_enum(enum_res))
else:
    st.info("Noch nicht gemessen für diese Regeln.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Wie groß darf n werden?")
st.caption("Die Rekursion mit exakten ganzen Zahlen, ohne Zeitgrenze für die einzelne Länge, aber mit einem gemeinsamen Zeitbudget; übersprungene Längen sind markiert.")
alphabet_rules, patterns_rules = a.settings.alphabet, ", ".join(a.rules.patterns)
large_rows = _large(alphabet_rules, patterns_rules)
st.dataframe(
    [{"n": r["n"], "Stellen der Anzahl": "übersprungen" if r["skipped"] else str(r["digits"]), "Zeit": "–" if r["skipped"] else time_text(r["seconds"])} for r in large_rows],
    hide_index=True, width="stretch",
)
verdict(verdict_large(large_rows))

st.markdown("---")

st.subheader("🔬 Experiment 3: Und mit Gleitkommazahlen?")
st.caption(f"Dieselbe Rekursion mit Python-`float` statt ganzen Zahlen, bis n = {C.FLOAT_N_MAX}. Verglichen wird der ganzzahlige Teil des Ergebnisses mit dem exakten Wert.")
verdict(verdict_float(_float(alphabet_rules, patterns_rules)))

st.markdown("---")

st.subheader("🔬 Experiment 4: Die Rekursion raten statt herleiten")
st.caption(f"Aus den ersten 2r Gliedern die Rekursion der Ordnung r bestimmen (exakte Brüche) und prüfen, bis wohin sie die ersten {C.GUESS_TERMS} Glieder trifft. "
           f"Nur bei höchstens {C.GUESS_MAX_STATES} Zuständen und bis Ordnung {C.GUESS_RMAX}.")
guess = _guess(alphabet_rules, patterns_rules)
if guess is not None:
    st.dataframe(
        [{"Ordnung r": r["r"], "Gleichungssystem": "singulär" if r["singular"] else "lösbar",
          "trifft die Folge bis n =": "–" if r["fits_until"] is None else str(r["fits_until"]),
          "trifft alle Glieder": "ja" if r["ok"] else "nein"} for r in guess["rows"]],
        hide_index=True, width="stretch",
    )
    if guess["coeffs"] is not None:
        terms = " + ".join(f"({c})·a(n−{j + 1})" for j, c in enumerate(guess["coeffs"]) if c != 0)
        st.markdown(f"**Gefundene Rekursion** (Ordnung {guess['r_min']}): a(n) = {terms}")
verdict(verdict_guess(guess))

st.markdown("---")

st.subheader("🔬 Experiment 5: Die zweite Wand – wenn der Zustand selbst wächst")
st.caption("Jedes von m Symbolen kommt genau einmal vor, bestimmte Nachbarpaare sind verboten. Dafür muss sich die Rekursion merken, **welche Symbole schon benutzt sind** und welches zuletzt kam: "
           "2ᵐ · m Zustände. Die Aufzählung prüft m! Reihenfolgen.")
w1, w2, w3 = st.columns(3)
wall_m = w1.slider("Symbole m (bis)", C.WALL_M_MIN, C.WALL_M_MAX, C.WALL_DEFAULT_M, key="wall_m", help="Die Rekursion läuft für alle m von 4 bis zu diesem Wert; je größer, desto länger.")
wall_density = w2.slider("Verbotene Paare in %", C.WALL_DENSITY_MIN, C.WALL_DENSITY_MAX, C.WALL_DEFAULT_DENSITY, 5, key="wall_density",
                         help="Anteil der geordneten Nachbarpaare, die verboten sind. 0 heißt: alle m! Reihenfolgen sind gültig.")
wall_seed = w3.number_input("Zufalls-Seed der Verbote", 0, C.SEED_MAX, C.DEFAULT_SEED, step=1, key="wall_seed")
wall_key = (int(wall_m), int(wall_density), int(wall_seed))
if st.button("🔬 Zweite Wand messen", key="wall_run"):
    st.session_state["wall_res"] = (wall_key, wall_experiment(*wall_key))
wall_res = st.session_state.get("wall_res")
if wall_res and wall_res[0] == wall_key:
    res = wall_res[1]
    for problem in res["problems"]:
        st.error(problem)
    st.plotly_chart(build_wall(res["rows"], res["extrapolation"]), width="stretch", key="wall_chart")
    st.dataframe(
        [{"m": r["m"], "Reihenfolgen m!": big_text(r["fact"]), "Zustände 2ᵐ·m": big_text(r["states"]), "gültige Reihenfolgen": big_text(r["count"]),
          "Aufzählen": "–" if r["t_brute"] is None else time_text(r["t_brute"]), "Rekursion": time_text(r["t_dp"])} for r in res["rows"]],
        hide_index=True, width="stretch",
    )
    st.markdown(f"**Hochrechnung** (nicht gemessen): Zeit der letzten Zeile mal 2^(Ziel − m) mal (Ziel/m)². Aufzählen ist nur bis m = {C.WALL_BRUTE_MAX} live nachgerechnet.")
    st.dataframe([{"m": e["m"], "Zustände": big_text(e["states"]), "Reihenfolgen m!": big_text(e["fact"]), "Rekursion (hochgerechnet)": time_text(e["t_dp"])} for e in res["extrapolation"]],
                 hide_index=True, width="stretch")
    verdict(verdict_wall(res))
else:
    st.info("Noch nicht gemessen für diese Einstellungen.")

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Der Automat liest ein Wort")
st.caption("Tippen Sie eine Folge ein. Die Tabelle zeigt, in welchem Zustand der Automat nach jedem Zeichen ist, und an welchem Zeichen ein Verbot vollendet wird.")
word = st.text_input("Folge", value="".join(a.rules.alphabet[:1]) * 3, key="play_word", max_chars=40, help="Nur Zeichen des Alphabets; Kleinbuchstaben werden in Großbuchstaben umgesetzt.").upper().strip()
if set(word) - set(a.rules.alphabet):
    st.warning(f"Nur Zeichen des Alphabets ({' '.join(a.rules.alphabet)}) sind erlaubt.")
else:
    states, bad = A.trace_word(a.auto, word)
    rows = [{"Zeichen": "–", "Gelesen": "", "Zustand danach": state_name(states[0])}]
    rows += [{"Zeichen": str(i + 1), "Gelesen": word[i], "Zustand danach": ("✗ Verbot vollendet" if (bad is not None and i == bad) else state_name(states[i + 1]))}
             for i in range(min(len(word), bad + 1 if bad is not None else len(word)))]
    st.dataframe(rows, hide_index=True, width="stretch")
    verdict(verdict_play(a.auto, word, states, bad))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Verbote zusammenhängender Teilfolgen** | Der kleine Automat ist für diese Art Verbot gezeigt. Andere Regeln können einen kleinen Automaten haben oder mehr Gedächtnis brauchen, etwa „jedes Symbol höchstens einmal“: Dort wächst der Zustand selbst (Experiment 5). | Stück 4 und 7 der Reihe: Zustandsmengen, Siebformel |
| **Der Zustand bleibt klein** | Für Verbote hat der Automat höchstens 1 plus die Summe der Verbotslängen minus 1 Zustände ({C.PATTERN_MAX_COUNT} Muster bis Länge {C.PATTERN_MAX_LEN} geben höchstens {1 + C.PATTERN_MAX_COUNT * (C.PATTERN_MAX_LEN - 1)}). Das gilt nur für Verbote dieser Art. | – |
| **Zeiten gelten für diesen Rechner und Python** | Die Messungen hängen von Rechner, Last und Sprache ab, zwei Läufe unterscheiden sich spürbar. Hochrechnungen sind keine Messungen. | – |
| **Raten findet die kleinste Ordnung ohne Anlauf** | Kleinere Ordnungen passen oft zu den ersten Gliedern und scheitern später (Experiment 4); bei einem Anlauf ist die wirksame Ordnung kleiner (Anlauf-Preset: 4 statt 5) und die Rekursion gilt erst ab einem späteren n. | Stück 2: Herleitung statt Raten |
| **Schichtfolgen sind nur der Rahmen** | Echte Dienstplanung ist ein Optimierungsproblem mit Kosten und Besetzung; hier wird nur gezählt. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/aufzaehlen-rekursion-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind ein Alphabet $\Sigma$ mit $k$ Zeichen und verbotene Teilfolgen $P$. Gesucht ist die Zahl $a(n)$ der Folgen der Länge $n$, die kein Verbot enthalten.

| Symbol | Bedeutung |
|---|---|
| $\Sigma,\ k$ | das Alphabet (hier die Schichten) und die Zahl seiner Zeichen |
| $P,\ p_j$ | die Verbote (verbotene Teilfolgen) und ein einzelnes Verbot |
| $a(n)$ | Zahl der gültigen Folgen der Länge $n$, höchstens $k^n$ |
| $z,\ Z$ | ein Zustand (längstes Ende der Folge, das ein Anfang eines Verbots ist) und die Menge der Zustände |
| $v_n(z)$ | Zahl der gültigen Folgen der Länge $n$, die im Zustand $z$ enden |
| $\delta(z, c)$ | Zustand nach dem Zeichen $c$, oder verboten |
| $m$ | Zahl der Symbole in der zweiten Wand (jedes genau einmal) |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/aufzaehlen-rekursion-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Problem.** Gegeben ein Alphabet $\Sigma$ mit $k$ Zeichen und Verbote $P = \{p_1, \dots, p_s\}$ (Wörter über $\Sigma$). Gesucht ist $a(n)$, die Zahl der Wörter der Länge $n$, die kein $p_j$ als zusammenhängende Teilfolge enthalten. Es gilt $a(n) \le k^n$.

**Zustand.** Für ein gelesenes Wort $w$ sei $\sigma(w)$ das längste Ende von $w$, das ein echter Anfang eines Verbots ist (das leere Wort zählt). Dann hängt es nur von $\sigma(w)$ und dem nächsten Zeichen $c$ ab, ob $wc$ ein Verbot beendet, und $\sigma(wc)$ ist ebenfalls durch $\sigma(w)$ und $c$ bestimmt. Die Zahl der Zustände ist höchstens $1 + \sum_j (|p_j| - 1)$.

**Rekursion.** Sei $v_n(z)$ die Zahl der gültigen Wörter der Länge $n$ im Zustand $z$ und $\delta(z, c) \in Z \cup \{\bot\}$ die Übergangsfunktion ($\bot$ = verboten). Dann ist $v_0 = e_{\text{Start}}$ und
$v_{n+1}(t) = \sum_{(z, c):\, \delta(z, c) = t} v_n(z)$, also $a(n) = \sum_z v_n(z) = e_{\text{Start}}^{\top} M^n \mathbf{1}$ mit der Übergangsmatrix $M$ ($M_{zt}$ = Zahl der Zeichen, die $z$ nach $t$ führen).

**Lineare Rekursion.** Nach Cayley–Hamilton erfüllt $M$ sein charakteristisches Polynom vom Grad $|Z|$; deshalb erfüllt $a(n)$ eine lineare Rekursion mit konstanten Koeffizienten, deren Ordnung höchstens $|Z|$ ist und die ab $n = |Z|$ gilt (Experiment 4 zeigt, dass der Anlauf auch später enden kann, wenn die Koeffizienten kleinere wirksame Ordnung ergeben).

**Zweite Wand.** Für „jedes von $m$ Symbolen genau einmal, Paare $B$ verboten“ ist der Zustand $(S, \ell)$ mit der Menge $S \subseteq \{1, \dots, m\}$ der benutzten Symbole und dem letzten Symbol $\ell \in S$: $2^m \cdot m$ Zustände (höchstens), je $m$ Übergänge, also $O(2^m m^2)$ Schritte; die Aufzählung prüft $m!$ Reihenfolgen (Held und Karp 1962 für die Rundreise, dieselbe Zustandsidee).

**Gleitkomma.** Eine Python-`float` hat 53 Bit Mantisse; ganze Zahlen über $2^{53}$ sind nicht mehr alle darstellbar, ab etwa $1{,}8 \cdot 10^{308}$ gibt die Rechnung `inf`.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
A. V. Aho und M. J. Corasick: *Efficient string matching: an aid to bibliographic search*, Communications of the ACM 18 (6), 1975, S. 333–340 (der Automat aus den Anfängen der Muster).
M. Held und R. M. Karp: *A dynamic programming approach to sequencing problems*, Journal of the Society for Industrial and Applied Mathematics 10 (1), 1962, S. 196–210.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html)."
)

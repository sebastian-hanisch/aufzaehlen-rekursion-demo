# Aufzählen und Rekursion – was man sich merken muss – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-aufzaehlen-rekursion-demo.streamlit.app/)** -->

Wurzel der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (Stück 1 von 16; die Linie wird erst vollständig veröffentlicht). Die Demo zählt **Folgen mit verbotenen Teilfolgen** (Standard: Schichtfolgen aus Früh, Spät, Nacht ohne „Früh direkt nach Nacht“ und ohne drei Nächte in Folge) auf drei Wegen: jede Folge prüfen, nur gültige Anfänge erweitern, und die **Rekursion über einen Zustand**. Es ist die erste Demo der Reihe; ein Nachfolger (Stück 2) leitet aus derselben Rekursion die erzeugende Funktion her. Schichtfolgen sind nur der Rahmen: Dienstplanung ist ein Optimierungsproblem, hier wird nur gezählt.

## Warum dieses Problem

Wie viele Folgen sind erlaubt, ohne sie einzeln anzufassen? Aufzählen gibt früh auf. Die Rekursion führt nur das **Gedächtnis der Regeln** mit, den **Zustand**: das längste Ende der bisherigen Folge, das ein Anfang eines Verbots ist. Das zählt auch sehr lange Folgen exakt. Der Kern der Demo ist die Frage, **wie groß dieses Gedächtnis sein muss**: bei Verboten zusammenhängender Teilfolgen bleibt es klein, bei „jedes Symbol genau einmal“ wächst es selbst exponentiell (die zweite Wand).

## Befunde und Korrekturen gegenüber dem Plan

- **Hook widerlegt.** Der Plan vermutete „Aufzählung bis n ≈ 20“. Gemessen (Phase 0, Python): Aufzählen mit Abschneiden trägt bis n ≈ 16 bis 17 in etwa zehn Sekunden, alle Wörter prüfen bis n ≈ 14 bis 15; zwei Läufe unterschieden sich um bis zu Faktor 2. Die App nennt deshalb **keine feste Wandzahl**, sondern misst auf dem Rechner, der sie ausführt, und rechnet hoch.
- **Fehler gefunden beim ersten AppTest-Lauf.** Python verweigert die Umwandlung ganzer Zahlen mit mehr als 4300 Stellen in Text (`ValueError`). 3¹⁰⁰⁰⁰ hat 4772 Stellen, also stürzte Experiment 2 bei Regeln ohne Einschränkung ab; mit den Standardregeln hat a(10 000) „nur“ 4061 Stellen und fiel nicht auf. Behoben mit `digit_count` und `leading_digits` ohne Stringumwandlung; Regressionstest in `tests/test_bigint.py`.
- **Konsolenfehler im Browser.** Pfeile als Annotationen mit leerem Text gaben `<text> attribute y: Expected length, "-Infinity"`. Ersetzt durch Linien mit Pfeil-Markern; im frischen Tab keine Konsoleneinträge.
- **Schranke der Zustandszahl.** Die Vormessung nannte „höchstens die Summe der Verbotslängen“; die genaue Schranke ist 1 + Σ(Länge − 1) (leeres Wort plus echte Anfänge) und wird so getestet.

## Modell

Alphabet mit k Zeichen und bis zu sechs Verbote von je höchstens sechs Zeichen; gezählt werden Wörter der Länge n, die kein Verbot als zusammenhängende Teilfolge enthalten. Der Automat (`azr_algorithm.build_automaton`) hat als Zustände die echten Anfänge der Verbote (inklusive leerem Wort), erreichbare nur; ein Schritt verteilt die Zahlen der Wörter je Zustand auf die Folgezustände, verbotene Übergänge entfallen. Die Formeln stehen im 📐-Expander der App. Die zweite Wand (Experiment 5): m Symbole, jedes genau einmal, bestimmte geordnete Nachbarpaare verboten; Zustand = (Menge der benutzten Symbole, letztes Symbol), also 2ᵐ · m Zustände.

## Methodik

- **Alle Wörter prüfen** (`brute_count`): k ⁿ Wörter erzeugen und einzeln prüfen.
- **Aufzählen mit Abschneiden** (`dfs_count`): nur gültige Anfänge erweitern.
- **Rekursion** (`sequence`, `count_dp`): Vektor über die Zustände, ein Schritt je Länge, exakte Python-Ganzzahlen.
- **Unabhängiger Prüfer in der App** (`check_count`): Matrixpotenz der Übergangsmatrix statt Vektorschritten, bis n = 8 zusätzlich Aufzählen; bei Abweichung zeigt die App einen Fehler statt einer Zahl.
- **Rekursion raten** (`solve_recurrence`, `smallest_recurrence`): aus den ersten 2r Gliedern die Rekursion der Ordnung r mit exakten Brüchen bestimmen und gegen die ersten 60 Glieder prüfen.
- **Hochrechnung** (nicht gemessen): Zeit je Wort der letzten Messzeile mal Zahl der Wörter beim Ziel; die Rekursion wird am Ziel gemessen.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_verdicts.py` oder `tests/test_oracle_aufzaehlen_rekursion.py`. **Zeiten** sind Messungen des Entwicklungsrechners (Windows, Python 3.14, Phase 0 und Browser-Durchlauf) und stehen **nicht** in Tests; getestet ist nur die Rangfolge mit großem Abstand.

| Frage | Befund |
|---|---|
| Standardfall, a(0) bis a(10) | 1, 3, 8, 20, 51, 130, 331, 843, 2147, 5468, 13926; a(12) = 90 328 von 3¹² = 531 441 Folgen (17,0 %) |
| Rekursion der Standardfolge | a(n) = 2a(n−1) + a(n−2) + a(n−3); a(n)/a(n−1) → 2,5468182769 (positive Wurzel von x³ = 2x² + x + 1), bei n = 10 schon 2,5468 |
| Fibonacci-Preset | {A, B} ohne AA: 1, 2, 3, 5, 8, 13, 21, 34, 55, zwei Zustände |
| Zustandszahlen der Presets | 3 (Standard), 2 (Fibonacci), 5 (Anlauf), 11 (viele Verbote), 3 (n = 40) |
| Zustandsschranke | vier zufällige Verbote der Länge 8 über F, S, N: naiv 3⁷ = 2187 Zustände, der Automat hat nie mehr als 1 + 4·7 = 29 (60 Zufallssätze, größter 28) |
| Rekursion im Großen (Standardregeln) | Stellen von a(n): n = 20: 9; 100: 41; 1000: 407; 3000: 1219; 10 000: 4061 |
| Rekursion gegen Aufzählen | Phase 0 (nicht getestet): n = 10 000 in 0,05 bis 0,11 s; Aufzählen mit Abschneiden bei n = 16 in 6,9 bis 14,5 s; Hochrechnung n = 30 etwa einen Monat |
| Gleitkomma statt Ganzzahl | Summe weicht ab **n = 41** vom exakten Wert ab (a(40) liegt schon über 2⁵³ ≈ 9,0·10¹⁵, ist aber zufällig noch darstellbar), Überlauf auf `inf` bei **n = 760** (Test: Bänder 38 bis 44 und 740 bis 780) |
| Rekursion raten | kleinste passende Ordnung 2, 3, 5 bei Zustandszahl 2, 3, 5 (Fibonacci, Standard, Anlauf-Preset); kleinere Ordnungen treffen nur den Anfang: Standard Ordnung 1 bis n = 1, Ordnung 2 bis n = 3; Anlauf-Preset Ordnung 1, 2, 3 bis n = 1, 3, 6 |
| Anlauf | Anlauf-Preset: Koeffizienten 2, −1, 1, 1, 0; die wirksame Ordnung 4 gilt erst ab **n = 5**, nicht ab n = 4 |
| Zweite Wand | 2ᵐ·m Zustände: m = 12: 49 152; m = 19: 9 961 472 (gegen 19! = 121 645 100 408 832 000 Reihenfolgen). Phase 0: m = 19 braucht 23 s, Aufzählen ist ab m = 11 (54 s) zu langsam; die App zählt live nur bis m = 8 nach |
| Gegenprobe der zweiten Wand | Permutationen von m Symbolen ohne „i direkt vor i+1“: 1, 1, 3, 11, 53, 309, 2119, 16 687, … (OEIS A000255, verschoben um 1) für m = 1 bis 10 |

## Ehrliche Grenzen

- **Zeiten und Hochrechnungen hängen vom Rechner ab.** Phase 0 maß Aufzählen bei n = 15 in 14,6 und 25,6 s an zwei Läufen desselben Rechners (Last). Die App misst bei jedem Klick neu; die Hochrechnung ist keine Messung und nimmt an, dass die Zeit je Wort gleich bleibt.
- **Python, nicht kompiliert.** In C wären alle Wände weiter hinten; die Aussage „der Zustand ist die Wand“ gilt davon unabhängig, die Zahl der Tage nicht.
- **Nur Verbote zusammenhängender Teilfolgen** haben einen kleinen Automaten. Regeln wie „genau fünf Nachtschichten insgesamt“ brauchen mehr Gedächtnis (Stück 8, Zählen nach Parameter).
- **Raten findet nicht immer die kleinste richtige Rekursion.** „Ordnung gleich Zustandszahl“ gilt in zwei von drei geprüften Regelsätzen; in der dritten ist die wirksame Ordnung kleiner (Koeffizient 0, Anlauf). Die Zustandszahl ist nur eine obere Schranke (Cayley–Hamilton).
- **Experiment 4 nur bis 12 Zustände und Ordnung 12.** Darüber ist die Bruchrechnung für die App zu teuer; die App sagt es.
- **Zweite Wand mit einer Verbotsdichte je Messung**; die Anzahlen gültiger Reihenfolgen wachsen mit zufälligen Verboten nicht gleichmäßig (die Paare für m + 1 Symbole sind nicht die Paare für m Symbole plus eine neue), Trends daraus sind nicht abzulesen; gezeigt werden nur Zustandszahl und Zeit.
- **Mit Plotly-Klick nicht getestet:** die Diagramme haben keine Auswahl; alle Achsen sind gesperrt.
- Alles simuliert, keine echten Dienstpläne.

## Verifikation

- **Kern:** Rekursion gegen Handrechnung (Fibonacci n = 4 mit allen acht Wörtern, Standardfall n = 1 bis 3 aus der Zählung von Hand), gegen Aufzählen aller Wörter und gegen die Matrixpotenz auf 40 festen Zufallsregelsätzen, gegen die Literaturfolgen (Fibonacci, Tribonacci, n + 1 für „kein AB“, A000255).
- **Eigenschaften:** Anzahl zwischen 0 und kⁿ, ein Verbot mehr verkleinert nie, Umbenennen der Zeichen, Reihenfolge, Duplikate und Obermuster ändern nichts, Zustandsschranke, Rekursion der Ordnung ≤ Zustandszahl gilt ab n = Zustandszahl, gleiches Ergebnis in zwei Prozessen mit verschiedenem `PYTHONHASHSEED`.
- **Randfälle:** n = 0, keine Verbote, alle Zeichen verboten, Verbot länger als die Folge, Verbot genau so lang wie die Folge, überlappende Verbote, negatives n, Zeichen außerhalb des Alphabets, Obergrenzen des Eingabeparsers inklusive.
- **Große Zahlen:** `tests/test_bigint.py` (Zahlen über der 4300-Stellen-Grenze; Regressionstest für den Fehler oben).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Experimente, Permalink mit Müll und Grenzwerten, ungültige Muster, alle Zeichen verboten, Spielwiese mit Verstoß und Fremdzeichen, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Browser:** frischer Tab ohne Konsoleneinträge (Standard, 11 Zustände, Experiment 1 und 5 per Klick), Handy-Breite 375 px ohne horizontales Scrollen der Seite.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

361 Tests (`pytest tests`), zuletzt in etwa einer Minute auf dem Entwicklungsrechner (Messung, nicht getestet).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, Automat, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `azr_algorithm.py` | Kern: Aufzählen, Automat, Rekursion, Matrixpotenz, Raten, zweite Wand, große Zahlen ohne Stringumwandlung |
| `azr_constants.py` | Regler-Grenzen, Budgets, Farben, Presets |
| `azr_evaluation.py` | Kennzahlen, Experimente, Hochrechnungen, Verdikte, Formatierung |
| `azr_layout.py` | Fester Kopf (Stylesheet) |
| `azr_pdf_export.py` | PDF der aktuellen Regeln (fpdf2) |
| `azr_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `azr_scenario.py` | Regeln, Parser der Verbotsmuster, verbotene Paare der zweiten Wand |
| `azr_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, große Zahlen, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Erzeugende Funktion, Nenner, Eigenwert:** Stück 2. Hier ist die Folge der Quotienten a(n+1)/a(n) sichtbar, ohne die Wurzel zu benennen.
- **Zählen nach Parameter** (genau j Nachtschichten): Stück 8.
- **Teilmengen-Zustand sinnvoll nutzen** (Held-Karp als Semiring, Siebformel, Hamiltonkreise): Stück 4 und 7; hier zeigt die zweite Wand nur, dass der Zustand dort die Grenze ist.
- **Verwandte Zählstücke:** DAG-Plan Stück 7 (lineare Erweiterungen, DP über Ideale), Komplexität-Plan Stück 9 (Permanente, #P), `random-spanning-tree-demo` (Kirchhoff), Kasteleyn-Plan (perfekte Paarungen planarer Graphen): Nachbarn mit anderem Ziel; die Demo verweist nur.
- **Eine kompilierte Messung** (C, Rust): nicht gebaut; die App sagt, dass alle Zeiten Python-Zeiten sind.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).

"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

ALPHABETS = {
    "F, S, N (Früh, Spät, Nacht)": "FSN",
    "A, B": "AB",
    "A, B, C": "ABC",
}
DEFAULT_ALPHABET = "F, S, N (Früh, Spät, Nacht)"
DEFAULT_PATTERNS = "NF, NNN"                 # keine Früh direkt nach Nacht, höchstens zwei Nächte in Folge
N_MIN, N_MAX, DEFAULT_N = 1, 60, 12          # Länge der Folgen; die Rekursion kostet O(n · Zustände)
PATTERN_MAX_COUNT, PATTERN_MAX_LEN = 6, 6    # höchstens 6 Verbote mit je höchstens 6 Zeichen: der Automat hat dann höchstens 31 Zustände
PATTERN_TEXT_MAX = 60                        # längere Eingaben aus der Adresszeile werden abgeschnitten
CHECK_BRUTE_MAX_N = 8                        # bis hierher prüft der App-Prüfer zusätzlich durch Aufzählen (höchstens 3^8 = 6561 Wörter)

ENUM_N_MIN, ENUM_N_MAX = 4, 16               # Folgenlängen der Zeitmessung im Experiment 1
ENUM_BUDGET = 1.0                            # Sekunden je Messzeile; danach hört das Verfahren in dieser Spalte auf
ENUM_TARGETS = (20, 25, 30, 40)              # Längen, für die hochgerechnet wird
LARGE_SIZES = (20, 100, 1000, 3000, 10000)   # Folgenlängen im Experiment 2 (exakte Ganzzahlen)
LARGE_BUDGET = 3.0                           # Sekunden für alle Zeilen zusammen
FLOAT_N_MAX = 1100                           # so weit rechnet Experiment 3 mit Gleitkommazahlen
GUESS_RMAX = 12                              # größte Ordnung, die Experiment 4 versucht
GUESS_MAX_STATES = 12                        # darüber ist die Bruchrechnung zu teuer für die App
GUESS_TERMS = 60                             # so viele Folgenglieder prüft Experiment 4 gegen die geratene Rekursion
WALL_M_MIN, WALL_M_MAX, WALL_DEFAULT_M = 4, 15, 12
WALL_DENSITY_MIN, WALL_DENSITY_MAX, WALL_DEFAULT_DENSITY = 0, 60, 30   # Prozent der Nachbarpaare, die verboten sind
WALL_BRUTE_MAX = 8                           # so viele Symbole zählt die Aufzählung (n! Reihenfolgen) noch live nach
WALL_TARGETS = (20, 25, 30)
SEED_MAX, DEFAULT_SEED = 999999, 35

COLOR_VALID = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_FORBIDDEN = "#c0504d"
COLOR_LINE = "#4c78a8"
COLOR_NODE = "#e8e8e8"

PRESETS = {
    "Standardfall: Schichtfolgen": {"alphabet": DEFAULT_ALPHABET, "patterns": "NF, NNN", "n": 12},
    "Fibonacci: A, B ohne AA": {"alphabet": "A, B", "patterns": "AA", "n": 12},
    "Rekursion mit Anlauf": {"alphabet": "A, B, C", "patterns": "AB, BC, CA, AAA", "n": 12},
    "Viele Verbote, mehr Zustände": {"alphabet": DEFAULT_ALPHABET, "patterns": "NF, NNN, FFFF, SFS, SSSS, NSN", "n": 12},
    "Zu lang zum Aufzählen (n = 40)": {"alphabet": DEFAULT_ALPHABET, "patterns": "NF, NNN", "n": 40},
}
PRESET_HELP = {
    "Standardfall: Schichtfolgen": "Früh, Spät, Nacht; keine Früh direkt nach Nacht, höchstens zwei Nächte in Folge. Der Automat hat drei Zustände.",
    "Fibonacci: A, B ohne AA": "Folgen aus A und B ohne zwei A hintereinander: die Fibonacci-Zahlen. Der kleinste Fall, den man von Hand aufzählen kann.",
    "Rekursion mit Anlauf": "Drei Symbole, vier Verbote. Die Rekursion der Zahlenfolge hat einen Anlauf: sie gilt erst ab n = 5. Gut für Experiment 4 (Raten statt Herleiten).",
    "Viele Verbote, mehr Zustände": "Sechs Verbote bis Länge 4: der Automat braucht deutlich mehr Zustände, die Rekursion bleibt billig.",
    "Zu lang zum Aufzählen (n = 40)": "Standardregeln mit n = 40: Aufzählen ist hier unbezahlbar, die Rekursion zählt es in Bruchteilen einer Millisekunde.",
}

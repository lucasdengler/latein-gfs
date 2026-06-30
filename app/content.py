"""
Fester Inhalt der GFS: C. Plinius Caecilius Secundus, epistula 6,16,4-5
(Brief an Tacitus über den Vesuvausbruch).

>>> HIER kannst du Text, Musterübersetzung, Vokabeln und Grammatik anpassen. <<<

Es werden die Sätze 1-4 als spielbare Übersetzungs-Aufgaben umgesetzt.
Die Anzahl der spielbaren Sätze ergibt sich automatisch aus dieser Liste
(SENTENCES) -> die Anzeige "Satz X/N" passt sich also an, wenn du Sätze
hinzufügst oder entfernst.

Der didaktische Schluss (Pinien-Metapher) wird als Text auf dem
Endbildschirm angezeigt (FINAL_NOTE), ist aber keine spielbare Aufgabe.
"""

# Jeder Satz:
#   latin     -> der lateinische Satz (wird dem Spieler gezeigt)
#   solution  -> Musterübersetzung (NUR serverseitig, nie an den Spieler gesendet!)
#   vocab     -> Liste von Vokabel-Hinweisen (Hilfestufe 1)
#   grammar   -> Liste von Grammatik-Hinweisen (Hilfestufe 1)
#   free_tip  -> optionaler Gratis-Tipp, der beim Erreichen des Satzes
#                automatisch und OHNE Punktabzug eingeblendet wird (oder None)

SENTENCES = [
    # --------------------------------------------------------------- Satz 1
    {
        "latin": "Erat Miseni classemque imperio praesens regebat.",
        "solution": "Er war in Misenum und befehligte als persönlich Anwesender die Flotte mit Befehlsgewalt.",
        "vocab": [
            "erat Miseni → er war in Misenum (Lokativ: Miseni) – Flottenstützpunkt am Golf von Neapel",
            "Misenum, -i n. → Misenum (Hafenstadt am Golf von Neapel)",
            "classis, -is f. → Flotte (Akk. Sg.: classem)",
            "imperio (Abl.) → mit der Befehlsgewalt",
        ],
        "grammar": [
            "„classemque imperio praesens regebat“: „praesens“ = prädikatives Partizip im Nom. – beschreibt den Zustand des Subjekts während der Handlung: „als persönlich Anwesender befehligte er die Flotte mit Befehlsgewalt“. Betont das persönliche Kommando vor Ort.",
            "Tempus: „Erat Miseni … regebat“ = Imperfekt als Rahmen – dauernder Hintergrund-Zustand, in den die Handlung eingebettet ist.",
        ],
        "free_tip": None,
    },
    # --------------------------------------------------------------- Satz 2
    {
        "latin": (
            "Nonum kal. Septembres hora fere septima mater mea indicat ei "
            "apparere nubem inusitata et magnitudine et specie. [...] Poscit "
            "soleas, ascendit locum, ex quo maxime miraculum illud conspici poterat."
        ),
        "solution": (
            "Am neunten Tag vor den Kalenden des September (= 24. August), etwa zur "
            "siebten Stunde, zeigt ihm meine Mutter an, dass eine Wolke von "
            "ungewöhnlicher Größe und Gestalt erscheine. [...] Er verlangt die "
            "Sandalen, steigt zu einer Stelle hinauf, von der aus jenes Wunder am "
            "besten betrachtet werden konnte."
        ),
        "vocab": [
            "nonum kal. Septembres → am neunten Tag vor den Kalenden des September = 24. August (Datum nach röm. Zählung)",
            "hora fere septima → ungefähr in der siebten Stunde (etwa 13 Uhr; hora 1 = Sonnenaufgang)",
            "indicat … apparere nubem → AcI: meldet, dass eine Wolke erscheint",
            "soleae, -arum f. Pl. → Sandalen, Schuhe",
            "locum (Akk.) → Ort, Platz (hier: eine Anhöhe)",
            "ex quo (Abl.) → von dem aus (relativischer Anschluss)",
            "conspici (Inf. Pass.) → gesehen/betrachtet werden",
        ],
        "grammar": [
            "AcI nach „indicat“: „mater mea indicat ei apparere nubem“ (nubem = Akk.-Subjekt, apparere = Infinitiv) = „meine Mutter zeigt ihm an, dass eine Wolke erscheine“ – knappe, indirekte Wiedergabe der Beobachtung.",
            "„locum, ex quo maxime miraculum illud conspici poterat“ = Relativsatz mit Infinitiv Präsens Passiv: „conspici“ (Inf. Präs. Passiv) hängt von „poterat“ ab – „eine Stelle, von der aus jenes Wunder am besten betrachtet werden konnte“.",
            "Tempus: historisches Präsens (indicat / Poscit / ascendit) – holt die entscheidenden Handlungsmomente in die Gegenwart und macht sie lebendig.",
        ],
        # GRATIS-TIPP fuer Satz 2: automatisch, OHNE Punktabzug.
        "free_tip": (
            "Gratis-Tipp: Der Punkt in „kal.“ ist kein Satzpunkt, sondern ein "
            "Abkürzungspunkt! „kal.“ steht für „Kalendas“ (Akk. Pl. von "
            "Kalendae = die Kalenden, der 1. Tag eines Monats). Ausgeschrieben "
            "lautet die Wendung „ante diem nonum Kalendas Septembres“ "
            "(a. d. IX Kal. Sept.). Übersetze sie wörtlich mit „am neunten Tag vor "
            "den Kalenden des September“ und gib die moderne Entsprechung dazu "
            "(= 24. August). Die Römer zählten von festen Tagen rückwärts und immer "
            "einschließlich (inklusiv): Die Kalenden des September = der 1. September; "
            "vom 1. September aus den 9. Tag zurückgezählt (inklusiv) ergibt den "
            "24. August – das überlieferte Datum des Vesuvausbruchs 79 n. Chr."
        ),
    },
    # --------------------------------------------------------------- Satz 3
    {
        "latin": (
            "Nubes — incertum procul intuentibus, ex quo monte (Vesuvium fuisse "
            "postea cognitum est) — oriebatur, cuius similitudinem et formam non "
            "alia magis arbor quam pinus expresserit."
        ),
        "solution": (
            "Eine Wolke – für die aus der Ferne Betrachtenden unsicher, von "
            "welchem Berg (dass es der Vesuv gewesen war, wurde später erkannt) – "
            "stieg auf, deren Ähnlichkeit und Gestalt kein anderer Baum besser "
            "wiedergeben könnte als eine Pinie."
        ),
        "vocab": [
            "intueri (Dep.) → anschauen, betrachten (intuentibus: Dat. Pl. Part. Präs.: „für die, die … schauten“)",
            "ex quo monte → von welchem Berg aus (indirekter Fragesatz)",
            "cuius (Gen. f.) → deren (auf nubes bezogen, rel. Anschluss)",
            "non alia magis … quam → keine andere mehr als – Vergleichskonstruktion",
            "pinus, -i (od. -us) f. → Pinie, Kiefer (Mittelmeer-Schirmpinie!)",
            "exprimere, -o → ausdrücken, treffend wiedergeben (expresserit: Konj. Pf. – potentialer Konjunktiv)",
        ],
        "grammar": [
            "„(Vesuvium fuisse postea cognitum est)“ = Parenthese mit AcI im Passiv: der AcI „Vesuvium … fuisse“ hängt von „cognitum est“ ab; „fuisse“ (Inf. Perfekt) drückt Vorzeitigkeit aus – „dass es der Vesuv gewesen war, wurde später erkannt“. Trennt den damaligen Eindruck vom späteren Wissen.",
            "„non alia magis arbor quam pinus expresserit“ = Potentialis (Konj. Perfekt) im Vergleich „magis … quam“: „kein anderer Baum dürfte sie besser wiedergegeben haben als eine Pinie“ – vorsichtiges Abwägen statt Behauptung, trägt die Pinien-Metapher.",
            "Tempus: „oriebatur“ = Imperfekt für Verlauf/Dauer (schildert den langsam ablaufenden Naturvorgang); „fuisse“ = Vorzeitigkeit (die Erkenntnis liegt nach der Beobachtung).",
        ],
        "free_tip": None,
    },
    # --------------------------------------------------------------- Satz 4
    {
        "latin": (
            "Nam longissimo velut trunco elata in altum quibusdam ramis "
            "diffundebatur, credo, quia recenti spiritu evecta, dein senescente "
            "eo destituta aut etiam pondere suo victa in latitudinem vanescebat."
        ),
        "solution": (
            "Denn gleichsam auf einem sehr langen Stamm in die Höhe gehoben, "
            "breitete sie sich in einige Äste aus, ich glaube, weil sie, durch den "
            "frischen Luftstoß emporgetragen, dann bei dessen Nachlassen im Stich "
            "gelassen oder auch durch ihr eigenes Gewicht besiegt, sich in die "
            "Breite verlor."
        ),
        "vocab": [
            "longissimus, a, um → sehr lang (Sup. zu longus); longissimo … trunco: mit einem sehr langen Stamm (Abl. instr./modi)",
            "elatus, a, um (PPP) → emporgehoben, in die Höhe getrieben (zu efferre); elata: f. Sg. – auf nubes bezogen",
            "quibusdam ramis (Abl. Pl.) → in gewisse Zweige (Abl. von quidam: ein gewisser)",
            "diffundi (Pass.) → sich ausbreiten (diffundebatur: Impf. Pass.)",
            "credo (Parenthese) → ich glaube (eingeschobene Bemerkung des Plinius)",
            "quia (Konj.) → weil",
            "recens, -ntis → frisch, neu (recenti spiritu: Abl.: durch einen frischen Lufthauch)",
            "spiritus, -us m. → Atem, Hauch, Luftströmung",
            "evehere, evectus, a, um → hinausführen, emportragen (PPP evecta: emporgetragen)",
            "dein (= deinde) → dann",
            "senescere, -o → alt werden, nachlassen (senescente eo: Abl. abs.: als dieser nachließ)",
            "destituere, destitutus, a, um → im Stich lassen, verlassen (PPP: verlassen, ohne Stütze)",
            "aut etiam → oder auch",
            "suo (Abl.) → ihr eigenes (zu pondere)",
        ],
        "grammar": [
            "Kausalsatz „quia recenti spiritu evecta … vanescebat“: „senescente eo“ = Ablativus absolutus („als dieser [Luftstoß] nachließ“); „recenti spiritu“ und „pondere suo“ = Ablative der Ursache („durch den frischen Stoß“, „durch ihr eigenes Gewicht“); „evecta, destituta, victa“ = Partizipienhäufung. Die dichte Häufung bildet die Phasen von Aufstieg und Zerfall der Wolke sprachlich nach.",
            "Tempus: „diffundebatur, vanescebat“ = Imperfekt für Verlauf/Dauer – der andauernde Vorgang des Ausbreitens und Zerfließens.",
        ],
        "free_tip": None,
    },
]

# Anzahl spielbarer Sätze (für "Satz X/N").
SENTENCE_COUNT = len(SENTENCES)

# Didaktischer Schluss / Pinien-Metapher -> wird auf dem Endbildschirm gezeigt.
FINAL_NOTE = (
    "Diese Beschreibung machte Plinius zum Namensgeber des "
    "„Plinianischen Vulkanausbruchs“. Die Schirmpinie hat einen schlanken "
    "hohen Stamm und eine breit ausladende Krone – genau die Form einer großen "
    "Eruptionswolke. „non alia magis … quam“ gehört zusammen, "
    "„expresserit“ ist ein potentialer Konjunktiv."
)


def public_sentence(index: int) -> dict:
    """
    Liefert die für den Spieler sichtbaren Daten eines Satzes
    (OHNE Musterübersetzung!).
    """
    s = SENTENCES[index]
    return {
        "index": index,
        "number": index + 1,
        "total": SENTENCE_COUNT,
        "latin": s["latin"],
        "free_tip": s.get("free_tip"),
    }


def help1_content(index: int) -> dict:
    """Vokabel- und Grammatik-Hinweise (Hilfestufe 1) für einen Satz."""
    s = SENTENCES[index]
    return {"vocab": s["vocab"], "grammar": s["grammar"]}

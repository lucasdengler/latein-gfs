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
        "solution": "Er war in Misenum und befehligte dort persönlich die Flotte.",
        "vocab": [
            "erat Miseni → er war in Misenum (Lokativ: Miseni) – Flottenstützpunkt am Golf von Neapel",
            "Misenum, -i n. → Misenum (Hafenstadt am Golf von Neapel)",
            "classis, -is f. → Flotte (Akk. Sg.: classem)",
            "imperio (Abl.) → mit der Befehlsgewalt",
        ],
        "grammar": [
            "„Miseni“ = Lokativ (Ortsangabe ohne Präposition bei Städtenamen der o-/a-Deklination Sg.): „in Misenum“.",
            "„classem-que“: angehängtes -que = „und“; „classem“ = Akk. Sg., Objekt zu „regebat“.",
            "„praesens“ = prädikatives Adjektiv im Nom. (auf das Subjekt „er“ bezogen): „persönlich/anwesend“.",
            "„imperio“ = Ablativus instrumenti/modi; „regebat“ = Imperfekt.",
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
            "Am 24. August, etwa gegen ein Uhr mittags, wies meine Mutter ihn "
            "darauf hin, dass eine Wolke von ungewöhnlicher Größe und Gestalt "
            "auftauchte. [...] Er verlangte seine Sandalen und stieg zu einem "
            "erhöhten Punkt hinauf, von dem aus man dieses Naturwunder am besten "
            "beobachten konnte."
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
            "AcI nach „indicat“: „nubem … apparere“ = „dass eine Wolke erscheint“ (nubem = Subjektsakkusativ, apparere = Infinitiv).",
            "„hora fere septima“ = Ablativus temporis („in der ungefähr 7. Stunde“).",
            "„inusitata et magnitudine et specie“ = Ablativus qualitatis; „et … et“ = „sowohl … als auch“; „inusitata“ (Abl. f. Sg.) bezieht sich auf magnitudine/specie.",
            "„Poscit, ascendit“ = historisches Präsens; „ex quo“ = relativischer Anschluss; „conspici“ = Inf. Präs. Passiv, abhängig von „poterat“.",
        ],
        # GRATIS-TIPP fuer Satz 2: automatisch, OHNE Punktabzug.
        "free_tip": (
            "Gratis-Tipp: Der Punkt in „kal.“ ist kein Satzpunkt, sondern ein "
            "Abkürzungspunkt! „kal.“ steht für „Kalendas“ (Akk. Pl. von "
            "Kalendae = die Kalenden, der 1. Tag eines Monats). Ausgeschrieben "
            "lautet die Wendung „ante diem nonum Kalendas Septembres“ "
            "(a. d. IX Kal. Sept.). Die Römer zählten von festen Tagen rückwärts "
            "und immer einschließlich (inklusiv). Die Kalenden des September = der "
            "1. September. Vom 1. September aus den 9. Tag zurückgezählt (inklusiv) "
            "ergibt den 24. August – das überlieferte Datum des Vesuvausbruchs 79 n. Chr."
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
            "Die Wolke stieg empor – für die Beobachter aus der Ferne war unklar, "
            "von welchem Berg sie ausging (erst später erfuhr man, dass es der "
            "Vesuv war) –, und kein anderer Baum hätte ihre Form und Gestalt "
            "besser nachgebildet als eine Pinie."
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
            "Hauptsatz: „Nubes … oriebatur“ = „die Wolke stieg empor/entstand“.",
            "Einschub „incertum (erat) procul intuentibus …“: „incertum“ = Prädikatsnomen („[es war] unklar“); „intuentibus“ = Dat. Pl. PPA von „intueri“ (Deponens) = „für die aus der Ferne Betrachtenden“.",
            "„ex quo monte … oriebatur“ = indirekter Fragesatz (abhängig von „incertum“): „von welchem Berg sie aufstieg“.",
            "„(Vesuvium fuisse postea cognitum est)“ = Parenthese mit AcI („Vesuvium fuisse“ = „dass es der Vesuv war“); „cognitum est“ = Passiv („man erkannte später“).",
            "„cuius“ = relativischer Anschluss, Gen. Sg. f. (auf „nubes“): „deren“.",
            "„non alia magis arbor quam pinus expresserit“ = Vergleich („non alia magis … quam“ gehört zusammen); „expresserit“ = Konj. Perfekt, potentialer Konjunktiv („dürfte … wiedergegeben haben / hätte … wiedergeben können“).",
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
            "Denn wie auf einem enorm langen Stamm schoss sie in die Höhe und "
            "verzweigte sich dann in verschiedene Äste; ich glaube, weil sie durch "
            "den frischen Druck der Eruption emporgetrieben, dann aber, als dieser "
            "nachließ, sich selbst überlassen oder gar von ihrer eigenen Last "
            "bezwungen, in die Breite zerfloss."
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
            "„longissimo velut trunco“ = Ablativ (instr./modi); „velut“ = „gleichsam wie“: „wie auf einem sehr langen Stamm“.",
            "„elata, evecta, destituta, victa“ = vier PPP im Nom. f. Sg., alle auf „nubes“ bezogen (Partizipien-Reihe).",
            "„senescente eo“ = Ablativus absolutus: „als dieser (= der Hauch/spiritus) nachließ“.",
            "„credo“ = Parenthese: „ich glaube“.",
            "„in altum“ = „in die Höhe“, „in latitudinem“ = „in die Breite“; „diffundebatur, vanescebat“ = Imperfekt; „recenti spiritu“, „pondere suo“ = Ablative (instr./causae).",
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

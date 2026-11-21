# analisis.py - Motor de análisis emocional y de comunicación (sin modelos de IA; solo texto)
#
# Sigue el documento "Sistema de análisis emocional, comportamiento humano y generación de
# respuestas". Principios que se aplican en el código:
#   - Varias emociones a la vez (principal + secundarias), cada una con intensidad 1-5 y evidencias.
#   - Una palabra suelta NO basta: una frase completa pesa 2, una palabra sola pesa 1 y, si no hay
#     nada que la respalde, la emoción se marca como "posible".
#   - MAYÚSCULAS, signos de exclamación y letras alargadas solo suben la intensidad de una emoción
#     que ya fue detectada; no crean enojo por sí solos.
#   - Negaciones ("no estoy triste"), sarcasmo y humor se tienen en cuenta.
#   - El riesgo es cualitativo (bajo / moderado / alto), con indicadores y su incertidumbre.
#   - Si no hay información suficiente, lo dice en vez de inventar.
import re
import unicodedata

# ─── Normalización y búsqueda ─────────────────────────

_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def normalizar(texto):
    """Minúsculas y sin tildes."""
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def limpiar(texto, leet=False):
    """Normaliza y colapsa letras repetidas ('holaaaa' -> 'hola'). Con leet, '1d10ta' -> 'idiota'."""
    t = normalizar(texto)
    if leet:
        t = t.translate(_LEET)
    return re.sub(r"(.)\1{2,}", r"\1", t)


class Patron:
    """Busca frases como palabra(s) completa(s) y devuelve la frase original (con tildes) y su posición."""

    def __init__(self, frases):
        self.mapa = {}
        for f in frases:
            self.mapa.setdefault(normalizar(f), f)
        orden = sorted(self.mapa, key=len, reverse=True)
        self.re = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(f) for f in orden) + r")(?!\w)") if orden else None

    def buscar(self, texto):
        if not self.re:
            return []
        vistos, res = set(), []
        for m in self.re.finditer(texto):
            original = self.mapa[m.group(0)]
            if original not in vistos:
                vistos.add(original)
                res.append((original, m.start()))
        return res

    def hay(self, texto):
        return bool(self.re and self.re.search(texto))


_NEGACION = re.compile(r"(?:^|\s)(?:no|nunca|jamas|tampoco|ni)\s+(?:\w+\s+){0,2}$")


def _negado(texto, inicio):
    return bool(_NEGACION.search(texto[max(0, inicio - 25):inicio]))


# ─── Léxico de emociones ──────────────────────────────
# (nombre, familia, frases completas [peso 2], palabras sueltas [peso 1])

EMOCIONES = [
    # ALEGRÍA
    ("Felicidad", "alegría",
     ["estoy muy feliz", "estoy feliz", "me siento muy bien", "hoy ha sido un día increíble", "no puedo creer lo bien que salió"],
     ["feliz", "contento", "contenta", "alegre", "genial"]),
    ("Entusiasmo", "alegría",
     ["no puedo esperar", "tengo muchísimas ganas", "tengo muchas ganas", "estoy deseando", "esto va a ser increíble"],
     ["emocionado", "emocionada", "entusiasmado", "entusiasmada"]),
    ("Orgullo", "alegría",
     ["finalmente lo conseguí", "valió la pena", "estoy orgulloso", "estoy orgullosa", "lo logré"],
     ["orgulloso", "orgullosa"]),
    ("Alivio", "alegría",
     ["menos mal", "por fin puedo", "pensé que iba a salir mal", "por fin terminó"],
     ["aliviado", "aliviada", "alivio"]),
    # AFECTO
    ("Afecto", "afecto",
     ["te quiero", "te amo", "te extraño", "te adoro", "me importas", "me haces falta", "te aprecio"],
     ["cariño"]),
    # TRISTEZA
    ("Pena", "tristeza",
     ["me siento muy mal", "me duele demasiado", "esto me duele", "no esperaba que terminara así", "me cuesta aceptar"],
     ["triste", "tristeza", "llorar", "llorando", "dolor"]),
    ("Soledad", "tristeza",
     ["no tengo a nadie", "nadie me entiende", "siempre estoy solo", "siempre estoy sola", "a nadie le importo",
      "me siento solo", "me siento sola"],
     ["soledad"]),
    ("Desilusión", "tristeza",
     ["esperaba más de ti", "me decepcionaste", "pensé que sería diferente", "confiaba en que"],
     ["decepcionado", "decepcionada", "decepción", "desilusión"]),
    ("Desesperanza", "tristeza",
     ["nada va a cambiar", "ya no tiene sentido", "cansado de luchar", "cansada de luchar", "no veo ninguna salida",
      "no veo salida", "no hay salida", "ya nada importa"],
     []),
    # ENOJO
    ("Irritación", "enojo",
     ["qué fastidio", "siempre haces lo mismo", "ya me tienes cansado", "ya me tienes cansada",
      "no entiendo por qué haces eso"],
     ["fastidio", "fastidiado", "molesto", "molesta", "incómodo", "incómoda"]),
    ("Frustración", "enojo",
     ["estoy cansado de intentarlo", "estoy cansada de intentarlo", "nada me sale bien", "hago todo lo posible",
      "siempre termino en el mismo lugar", "otra vez lo mismo", "que esto se repita", "no puedo seguir soportando",
      "ya no puedo seguir soportando"],
     ["frustrado", "frustrada", "frustración"]),
    ("Rabia", "enojo",
     ["no soporto más", "no soporto esto", "estoy harto", "estoy harta", "me tienes hasta aquí", "me tienes harto",
      "me tienes harta", "no quiero volver a saber nada", "no te soporto"],
     ["rabia", "furioso", "furiosa", "enojado", "enojada", "harto", "harta"]),
    ("Indignación", "enojo",
     ["es una injusticia", "no merecía que me trataran", "es increíble que permitan", "no pienso aceptar"],
     ["injusto", "injusticia", "indignado", "indignada", "indignante"]),
    ("Resentimiento", "enojo",
     ["nunca voy a olvidar", "después de todo lo que hice por ti", "siempre termino perdonándote",
      "llevo mucho tiempo guardándome", "llevo tiempo guardándome", "llevo días guardándomelo",
      "llevo mucho tiempo guardándomelo", "llevo tiempo guardándomelo"],
     ["resentimiento", "resentido", "resentida", "rencor"]),
    # MIEDO
    ("Ansiedad anticipatoria", "miedo",
     ["y si todo sale mal", "no dejo de pensar en lo que podría pasar", "tengo miedo de equivocarme",
      "no sé qué va a ocurrir"],
     ["ansiedad", "ansioso", "ansiosa", "nervioso", "nerviosa", "preocupado", "preocupada"]),
    ("Inseguridad", "miedo",
     ["no creo ser suficiente", "no soy suficiente", "seguro hay alguien mejor", "no sé si estoy haciendo lo correcto",
      "tengo miedo de que me rechacen"],
     ["inseguro", "insegura", "inseguridad"]),
    ("Temor al abandono", "miedo",
     ["no quiero que te vayas", "siento que me vas a dejar", "me vas a dejar", "tengo miedo de perderte",
      "cada vez te siento más distante"],
     []),
    ("Vergüenza", "miedo",
     ["qué vergüenza", "no quiero que nadie se entere", "me siento ridículo", "me siento ridícula"],
     ["vergüenza", "avergonzado", "avergonzada"]),
    ("Miedo", "miedo",
     ["tengo miedo", "me da miedo", "me da susto"],
     ["miedo", "asustado", "asustada", "terror", "pánico"]),
    # ASCO Y RECHAZO
    ("Asco y rechazo", "asco y rechazo",
     ["me da asco", "qué asco", "no quiero tener nada que ver contigo", "me parece repugnante",
      "no puedo creer que alguien sea así"],
     ["asco", "repugnante", "asqueroso", "asquerosa", "repulsivo"]),
    # SORPRESA
    ("Sorpresa", "sorpresa",
     ["no me lo esperaba", "no puedo creer que", "me dejaste sin palabras", "cómo pudiste hacer eso",
      "no esperaba semejante"],
     ["sorpresa", "sorprendido", "sorprendida", "increíble", "wow"]),
    # COMPLEJAS
    ("Nostalgia", "compleja",
     ["extraño esos tiempos", "como antes", "cuando todo era más fácil", "recuerdo cuando"], ["nostalgia", "añoro"]),
    ("Culpa", "compleja",
     ["fue mi culpa", "me siento culpable", "no debí hacerlo", "soy el culpable", "soy la culpable"], ["culpable"]),
    ("Remordimiento", "compleja",
     ["me arrepiento", "no me lo perdono", "nunca me lo voy a perdonar"], ["remordimiento", "arrepentido", "arrepentida"]),
    ("Celos", "compleja",
     ["con quién estabas", "con quién hablas", "quién es esa", "quién es ese", "te vi con", "andabas con",
      "quién te escribió"],
     ["celos", "celoso", "celosa"]),
    ("Envidia", "compleja",
     ["quisiera tener lo que tiene", "siempre le sale todo bien", "por qué a él sí y a mí no",
      "por qué a ella sí y a mí no"], ["envidia", "envidioso", "envidiosa"]),
    ("Amargura", "compleja",
     ["todo me sale mal siempre", "la vida es injusta conmigo", "ya no creo en nadie"],
     ["amargura", "amargado", "amargada"]),
    ("Desesperación", "compleja",
     ["no aguanto más", "no aguanto un segundo más", "ya no aguanto", "no puedo más", "ya no puedo más",
      "no sé qué hacer", "todo se está derrumbando", "todo se derrumba", "no puedo seguir así"],
     ["desesperado", "desesperada", "desesperación"]),
    ("Agotamiento emocional", "compleja",
     ["estoy agotado", "estoy agotada", "estoy cansado de todo", "estoy cansada de todo", "ya no tengo fuerzas",
      "no tengo energía para esto", "estoy exhausto", "estoy exhausta", "estoy cansado de esta situación",
      "no puedo seguir soportando", "ya no puedo seguir soportando"],
     ["agotado", "agotada", "agotamiento", "exhausto", "exhausta", "saturado", "saturada"]),
    ("Impotencia", "compleja",
     ["no puedo hacer nada", "no hay nada que pueda hacer", "no depende de mí", "me siento impotente",
      "no puedo cambiarlo"], ["impotencia", "impotente"]),
    ("Vacío emocional", "compleja",
     ["me siento vacío", "me siento vacía", "no siento nada", "nada me motiva", "nada me llena",
      "no tengo ganas de nada", "sin ganas de nada"], ["vacío", "vacía"]),
    ("Confusión emocional", "compleja",
     ["no sé qué siento", "no sé qué pensar", "estoy confundido", "estoy confundida", "no sé qué hacer con esto"],
     ["confundido", "confundida", "confusión"]),
]

_EMO = [(n, f, Patron(fr), Patron(pa)) for n, f, fr, pa in EMOCIONES]

FAMILIAS_NEGATIVAS = ("tristeza", "enojo", "miedo", "asco y rechazo", "compleja")

# Frases que fijan un piso de intensidad (4 = alta, 5 = muy alta)
_FUERTES = {normalizar(x) for x in [
    "no aguanto más", "ya no aguanto", "no puedo más", "ya no puedo más", "no soporto más", "estoy harto", "estoy harta",
    "me tienes hasta aquí", "no quiero volver a saber nada", "cansado de luchar", "cansada de luchar", "no veo salida",
    "no hay salida", "ya no tiene sentido", "ya no tengo fuerzas", "nada va a cambiar", "ya nada importa",
    "me siento vacío", "me siento vacía", "no siento nada", "no tengo ganas de nada", "no puedo seguir así",
    "no puedo seguir soportando", "ya no puedo seguir soportando"]}
_EXTREMAS = {normalizar(x) for x in [
    "no aguanto un segundo más", "todo se está derrumbando", "todo se derrumba", "no veo ninguna salida"]}

_INTENSIFICADORES = Patron(["muy", "muchísimo", "muchísima", "demasiado", "demasiada", "súper", "extremadamente",
                            "completamente", "totalmente", "realmente", "bastante", "mucho", "tan"])
_ABSOLUTOS = Patron(["siempre", "nunca", "jamás", "nadie", "todo", "todos", "nada", "en la vida", "todo el tiempo"])
_ACUMULACION = Patron(["llevo mucho tiempo", "llevo días", "llevo meses", "llevo semanas", "llevo tiempo", "una y otra vez",
                       "otra vez", "cada vez", "desde hace", "hoy fue el límite", "la última gota", "se repita",
                       "se repite", "ya van", "de nuevo", "guardándomelo", "guardándome", "acumulado", "siempre"])
_SARCASMO = Patron(["ah claro", "claro, como no", "claro como no", "qué gracioso", "gracias por nada", "muy bien, felicidades",
                    "qué bien, otra vez", "buenísimo, ahora", "genial, ahora", "sí claro", "qué lindo, otra vez",
                    "qué amable", "qué considerado", "qué detalle"])
_HUMOR = Patron(["jaja", "jajaja", "jeje", "jejeje", "xd", "lol", "😂", "🤣"])

NIVELES = {1: "muy baja", 2: "baja", 3: "moderada", 4: "alta", 5: "muy alta"}

# etiqueta del modelo de IA -> (nombre, familia)
_MODELO = {
    "joy": ("Felicidad", "alegría"), "sadness": ("Pena", "tristeza"), "anger": ("Irritación", "enojo"),
    "fear": ("Miedo", "miedo"), "disgust": ("Asco y rechazo", "asco y rechazo"), "surprise": ("Sorpresa", "sorpresa"),
}


def _enfasis(texto):
    senales = []
    letras = [c for c in texto if c.isalpha()]
    if len(letras) >= 8 and sum(c.isupper() for c in letras) / len(letras) >= 0.7:
        senales.append("mayúsculas")
    if texto.count("!") >= 2:
        senales.append("signos de exclamación")
    if re.search(r"(.)\1{2,}", texto.lower()):
        senales.append("letras alargadas")
    if re.search(r"\?{2,}", texto):
        senales.append("preguntas repetidas")
    return senales


def detectar_emociones(texto, limpio, modelo_emocion=None, sarcasmo=False):
    enfasis = _enfasis(texto)
    hay_intensificador = _INTENSIFICADORES.hay(limpio)
    encontradas = []

    for nombre, familia, p_frases, p_palabras in _EMO:
        evidencias, peso, piso = [], 0, 1
        for original, pos in p_frases.buscar(limpio):
            if _negado(limpio, pos):
                continue
            evidencias.append(original)
            peso += 2
            clave = normalizar(original)
            piso = max(piso, 5 if clave in _EXTREMAS else 4 if clave in _FUERTES else 1)
        for original, pos in p_palabras.buscar(limpio):
            if _negado(limpio, pos) or original in evidencias:
                continue
            evidencias.append(original)
            peso += 1
        if not evidencias:
            continue
        # Con sarcasmo, las palabras positivas sueltas no se toman literalmente
        if sarcasmo and familia in ("alegría", "afecto") and peso < 2:
            continue
        encontradas.append({"nombre": nombre, "familia": familia, "evidencias": evidencias, "peso": peso,
                            "piso": piso, "modelo": False})

    # El modelo de IA corrobora una emoción (o aporta una débil si el texto no la muestra)
    if modelo_emocion:
        etiqueta, prob = modelo_emocion
        if etiqueta in _MODELO and prob >= 0.5:
            nombre_m, familia_m = _MODELO[etiqueta]
            misma = [e for e in encontradas if e["familia"] == familia_m]
            if misma:
                misma[0]["modelo"] = True
            elif not (sarcasmo and familia_m == "alegría"):
                encontradas.append({"nombre": nombre_m, "familia": familia_m, "evidencias": ["(lo indica el modelo de IA)"],
                                    "peso": 1, "piso": 2 if prob >= 0.7 else 1, "modelo": True})

    for e in encontradas:
        intensidad = 1 + (1 if e["peso"] >= 2 else 0)
        if hay_intensificador:
            intensidad += 1
        if len([x for x in e["evidencias"] if not x.startswith("(")]) >= 2:
            intensidad += 1
        if enfasis:
            intensidad += 1  # solo cuenta porque la emoción ya fue detectada por su contenido
        e["intensidad"] = max(1, min(5, max(intensidad, e["piso"])))
        corroborada = e["peso"] >= 2 or e["modelo"] or sum(1 for x in encontradas if x["familia"] == e["familia"]) > 1
        e["certeza"] = "probable" if corroborada else "posible"

    # Ambivalencia: cariño y malestar a la vez ("te quiero, pero...")
    afecto = [e for e in encontradas if e["familia"] in ("afecto",)]
    negativas = [e for e in encontradas if e["familia"] in FAMILIAS_NEGATIVAS]
    if afecto and negativas and re.search(r"(?<!\w)pero(?!\w)", limpio):
        encontradas.append({"nombre": "Ambivalencia", "familia": "compleja",
                            "evidencias": ["cariño y malestar unidos por «pero»"], "peso": 2, "piso": 1, "modelo": False,
                            "intensidad": max(e["intensidad"] for e in afecto + negativas), "certeza": "probable"})

    encontradas.sort(key=lambda e: (-e["intensidad"], -e["peso"]))
    return encontradas, enfasis


# ─── Intención comunicativa ───────────────────────────

INTENCIONES = {
    "Desahogo": ["necesitaba sacar", "necesito desahogarme", "llevo días guardándomelo", "tenía que decirlo",
                 "llevo mucho tiempo guardándomelo", "solo quería decirlo", "solo quiero desahogarme", "quiero sacar esto", "llevo mucho tiempo callando",
                 "ya no me lo puedo guardar"],
    "Búsqueda de apoyo": ["no sé con quién hablar", "necesito hablar con alguien", "necesito apoyo", "necesito ayuda",
                          "necesito que me escuches", "puedes escucharme", "me puedes escuchar", "no tengo a nadie"],
    "Búsqueda de soluciones": ["cómo puedo", "cómo solucionar", "cómo soluciono", "qué hago", "qué debo hacer",
                               "no sé cómo", "cómo arreglo", "qué me recomiendas", "qué puedo hacer", "ayúdame a"],
    "Reclamo": ["siempre haces lo mismo", "nunca reconoces", "no me escribes", "por qué no me respondes",
                "por qué no respondes", "no me respondes", "me ignoras", "no contestas", "por qué tardas",
                "no me haces caso", "no me tomas en cuenta", "no me escuchas", "lo que haces"],
    "Establecimiento de límites": ["no voy a permitir", "no voy a tolerar", "no pienso aceptar", "no acepto que",
                                   "no permito que", "ya no voy a aguantar", "necesito espacio", "no me hables así",
                                   "no me trates así", "hasta aquí", "este es mi límite", "hoy fue el límite",
                                   "no vuelvas a", "ya no puedo seguir soportando"],
    "Reconciliación": ["no quiero que terminemos así", "quiero arreglar las cosas", "podemos hablar", "hablemos",
                       "perdóname", "lo siento", "quiero que lo solucionemos", "empecemos de nuevo",
                       "dame otra oportunidad", "quiero arreglarlo", "lamento lo que"],
    "Búsqueda de validación": ["estoy exagerando", "soy yo el problema", "tengo razón o no", "es normal que",
                               "estoy loco por sentirme", "estoy loca por sentirme", "me estoy volviendo loco",
                               "verdad que tengo razón"],
    "Provocación": ["vamos, dime algo", "dime algo", "a ver si te atreves", "sé que te molesta", "qué vas a hacer",
                    "te molesta, verdad", "atrévete"],
    "Manipulación emocional": ["si realmente me quisieras", "si me quisieras", "si de verdad me quisieras",
                               "después de todo lo que hice por ti", "si me dejas", "por tu culpa me",
                               "nadie más te va a querer", "sin mí no eres nada", "harías lo que te pido"],
    "Posible distanciamiento": ["quiero terminar", "terminemos esto", "terminemos la relación", "ya no quiero estar contigo", "necesito distancia",
                                "se acabó", "hasta aquí llegamos", "no quiero verte", "no quiero hablar contigo",
                                "vamos a terminar", "démonos un tiempo", "damos un tiempo"],
}
_INTENC = {k: Patron(v) for k, v in INTENCIONES.items()}

# ─── Riesgo ───────────────────────────────────────────

_AUTOLESION = Patron(["quiero morirme", "me quiero morir", "quiero morir", "no quiero vivir", "ya no quiero vivir",
                      "no quiero seguir viviendo", "quitarme la vida", "acabar con mi vida", "suicidarme", "suicidio",
                      "hacerme daño", "me voy a matar", "no vale la pena vivir", "ya no quiero estar aquí",
                      "desaparecer para siempre", "mejor si no estuviera", "voy a acabar con todo"])
_AUTOLESION_RE = re.compile(r"(?<!\w)me voy a (hacer|lastimar)(\s+\w+)?\s+dano(?!\w)")
_DISTRES = Patron(["no aguanto más", "no aguanto un segundo más", "ya no aguanto", "no puedo más", "ya no puedo más",
                   "hoy fue el límite", "todo se está derrumbando", "todo se derrumba", "no veo ninguna salida",
                   "no veo salida", "no hay salida", "ya no tiene sentido", "cansado de luchar", "cansada de luchar",
                   "estoy cansado de todo", "estoy cansada de todo", "no puedo seguir así", "no tiene sentido seguir"])
_AMENAZA_VIOLENTA = Patron(["te voy a pegar", "te voy a matar", "te voy a golpear", "te voy a hacer daño",
                            "voy a hacerte daño", "te voy a lastimar", "voy a lastimarte", "te voy a romper",
                            "te voy a acabar", "te mato", "te voy a destruir"])
_AMENAZA_RE = re.compile(r"(?<!\w)voy a hacerte (dano|algo)(?!\w)")
_AMENAZA_VAGA = Patron(["me las vas a pagar", "te vas a arrepentir", "te vas a acordar de mí", "esto no se va a quedar así",
                        "te arrepentirás"])
_DANO_OTROS = Patron(["lo voy a matar", "la voy a matar", "los voy a matar", "voy a hacerle daño", "voy a vengarme",
                      "me voy a vengar", "voy a acabar con él", "voy a acabar con ella"])
_VIOLENCIA_SUFRIDA = Patron(["me pega", "me golpea", "me golpeó", "me pegó", "me agrede", "me agredió",
                             "me amenazó de muerte", "me amenaza de muerte", "me tiene encerrada", "me tiene encerrado",
                             "me empujó", "me ahorcó", "me va a matar", "me quiere matar"])

# ─── Comportamiento comunicativo ──────────────────────

_INSULTOS = Patron(["estúpido", "estúpida", "idiota", "imbécil", "pendejo", "pendeja", "cabrón", "cabrona", "maldito",
                    "maldita", "desgraciado", "desgraciada", "hdp", "hijo de puta", "hija de puta", "malparido",
                    "malparida", "hijueputa", "gonorrea"])
_DESCALIF = Patron(["no sirves", "no vales nada", "eres un inútil", "eres inútil", "eres una inútil",
                    "nunca haces nada bien", "no sabes hacer nada", "eres un desastre", "eres un fracaso", "eres torpe",
                    "tonto", "tonta", "burro", "burra", "patético", "patética", "eres basura", "eres una basura"])
_DESPRECIO = Patron(["me das asco", "das asco", "eres un asco", "eres lo peor", "no mereces", "ni te molestes",
                     "qué asco de persona", "no vales nada", "nadie te quiere"])
_CULPABILIZACION = Patron(["por tu culpa", "todo es tu culpa", "tú tienes la culpa", "eres el culpable", "eres la culpable",
                           "todo lo arruinas", "lo arruinaste todo", "es tu culpa", "eres el problema"])
_VICTIMIZACION = Patron(["siempre soy yo", "todos me hacen daño", "siempre me pasa a mí", "nadie sufre como yo",
                         "pobre de mí", "soy la víctima", "siempre me toca a mí", "todos están contra mí"])
_CHANTAJE = Patron(["si realmente me quisieras", "si me quisieras", "si de verdad me quisieras",
                    "después de todo lo que hice por ti", "si me dejas", "nadie más te va a querer",
                    "sin mí no eres nada", "harías lo que te pido", "por tu culpa me"])
_GASLIGHTING = Patron(["eso nunca pasó", "estás inventando", "estás loco", "estás loca", "te lo imaginas",
                       "estás exagerando", "exageras", "eso no fue así", "nunca dije eso", "te lo estás inventando",
                       "estás imaginando cosas", "siempre te inventas"])
_AGRESION = Patron(["cuidado conmigo", "cállate", "cierra la boca", "lárgate", "vete a la mierda", "te vas a arrepentir",
                    "me las vas a pagar"])
_PASIVO_AG = Patron(["como quieras", "haz lo que quieras", "no pasa nada, en serio", "claro, lo que digas",
                     "lo que digas", "ya veo", "qué bien por ti", "nada, olvídalo", "olvídalo", "no importa",
                     "como digas", "como sea", "da igual"])
_EVASION_FRASES = Patron(["no quiero hablar de eso", "luego hablamos", "ahora no", "dejemos eso", "mejor no hablamos",
                          "no tengo ganas de hablar", "después hablamos", "hablamos luego"])
_EVASION_CORTAS = {"ok", "oka", "vale", "ya", "ah", "bueno", "mmm", "hmm", "k"}


def _buscar(patron, limpio):
    return [o for o, pos in patron.buscar(limpio)]


def detectar_comportamientos(texto, limpio, limpio_leet, sarcasmo, humor):
    c = {}

    def agregar(nombre, evidencias, nota=None):
        if evidencias:
            c[nombre] = {"evidencias": evidencias[:3], "nota": nota}

    agregar("Insultos", _buscar(_INSULTOS, limpio_leet))
    agregar("Descalificación", _buscar(_DESCALIF, limpio_leet))
    agregar("Desprecio", _buscar(_DESPRECIO, limpio))
    agregar("Culpabilización", _buscar(_CULPABILIZACION, limpio))
    agregar("Victimización", _buscar(_VICTIMIZACION, limpio),
            "Se detecta con cautela: expresar dolor no es victimizarse.")
    agregar("Chantaje emocional", _buscar(_CHANTAJE, limpio),
            "Una frase aislada no basta para afirmar que hay mala intención.")
    gl = _buscar(_GASLIGHTING, limpio)
    if len(gl) >= 2:
        agregar("Posible manipulación de la percepción (gaslighting)", gl, "Es un patrón repetido; aquí hay varias frases.")
    elif gl:
        agregar("Frase que podría invalidar la percepción del otro", gl,
                "Una sola frase no permite concluir gaslighting.")
    agresion = _buscar(_AGRESION, limpio) + _buscar(_AMENAZA_VIOLENTA, limpio) + _buscar(_AMENAZA_VAGA, limpio)
    if _AMENAZA_RE.search(limpio):
        agresion.append("voy a hacerte daño")
    agregar("Agresión verbal", agresion + [x for x in c.get("Insultos", {}).get("evidencias", [])][:0])
    pa = _buscar(_PASIVO_AG, limpio) + (["tono sarcástico"] if sarcasmo else [])
    agregar("Pasivo-agresividad", pa, "Puede ser cansancio o evitar el conflicto; falta contexto.")

    palabras = limpio.split()
    ev = _buscar(_EVASION_FRASES, limpio)
    if len(palabras) <= 3 and any(p.strip(".,!?¿¡") in _EVASION_CORTAS for p in palabras):
        ev.append("respuesta muy corta")
    agregar("Evasión", ev, "Puede ser protección o necesidad de espacio, no necesariamente una intención negativa.")

    abs_ = _buscar(_ABSOLUTOS, limpio)
    hostil = any(k in c for k in ("Insultos", "Descalificación", "Desprecio", "Culpabilización", "Agresión verbal"))
    if len(abs_) >= 2 or (abs_ and hostil):
        agregar("Generalización", abs_)

    if humor and ("Insultos" in c or "Descalificación" in c):
        c["Insultos"]["nota"] = "Hay señales de humor (jaja, xd); podría ser una broma entre conocidos."
    return c


def clasificar_estilo(comp, intenciones):
    agresivo = [k for k in ("Insultos", "Descalificación", "Desprecio", "Agresión verbal") if k in comp]
    pasivo_ag = "Pasivo-agresividad" in comp
    evasion = "Evasión" in comp
    asertivo = any(i in ("Establecimiento de límites", "Reclamo", "Búsqueda de soluciones", "Reconciliación", "Desahogo",
                         "Búsqueda de apoyo") for i in intenciones)
    estilos = []
    if agresivo:
        estilos.append("agresiva")
    if pasivo_ag:
        estilos.append("pasivo-agresiva")
    if evasion:
        estilos.append("pasiva/evasiva")
    if asertivo and not agresivo:
        estilos.append("asertiva")
    if not estilos:
        return "No se puede determinar con este mensaje"
    if len(estilos) == 1:
        return estilos[0].capitalize()
    return "Mixta (" + " + ".join(estilos) + ")"


def evaluar_riesgo(limpio, emociones, comp, intenciones):
    """Riesgo cualitativo con indicadores. No usa porcentajes: no hay un modelo validado que los respalde."""
    ind, flags = [], {"autolesion": False, "ambiguo": False, "violencia": False, "amenaza": False,
                      "violencia_sufrida": False, "dano_otros": False}
    alto, moderado = [], []

    a = _buscar(_AUTOLESION, limpio)
    frases = list(a)
    if a or _AUTOLESION_RE.search(limpio):
        flags["autolesion"] = True
        alto.append("Referencia explícita a morir o hacerse daño: " + (f"«{a[0]}»" if a else "«hacerse daño»"))
    av = _buscar(_AMENAZA_VIOLENTA, limpio)
    if av or _AMENAZA_RE.search(limpio):
        flags["violencia"] = flags["amenaza"] = True
        alto.append("Amenaza de violencia hacia otra persona: " + (f"«{av[0]}»" if av else "«voy a hacerte daño»"))
    do = _buscar(_DANO_OTROS, limpio)
    if do:
        flags["violencia"] = flags["dano_otros"] = True
        alto.append(f"Plan o intención de dañar a otras personas: «{do[0]}»")
    vs = _buscar(_VIOLENCIA_SUFRIDA, limpio)
    if vs:
        flags["violencia_sufrida"] = True
        alto.append(f"Posible situación de violencia o peligro: «{vs[0]}»")

    d = _buscar(_DISTRES, limpio)
    frases += d
    if d and not flags["autolesion"]:
        flags["ambiguo"] = True
        moderado.append(f"Expresión de agotamiento o desesperación («{d[0]}») sin mención explícita de hacerse daño; "
                        "merece una pregunta directa sobre su seguridad")
    av2 = _buscar(_AMENAZA_VAGA, limpio)
    if av2 and not flags["amenaza"]:
        flags["amenaza"] = True
        moderado.append(f"Advertencia o amenaza poco clara: «{av2[0]}» (no se sabe si implica violencia)")
    for k in ("Insultos", "Agresión verbal", "Desprecio"):
        if k in comp:
            moderado.append(f"{k.capitalize()}: «{comp[k]['evidencias'][0]}»")
    if any(e["familia"] == "enojo" and e["intensidad"] >= 4 for e in emociones):
        moderado.append("Enojo de intensidad alta (la intensidad no equivale a peligro)")
    if any(e["nombre"] in ("Desesperanza", "Desesperación") for e in emociones) and not flags["autolesion"]:
        if not any("desesperación" in m for m in moderado):
            moderado.append("Desesperanza o desesperación expresadas en el texto")

    if alto:
        nivel, ind = "alto", alto + moderado
    elif moderado:
        nivel, ind = "moderado", moderado
    else:
        nivel = "bajo"
        ind = ["No se encuentran amenazas, referencias a hacerse daño ni hostilidad marcada en el texto."]

    if flags["autolesion"]:
        inc = "Nunca debe tratarse como una simple estrategia de manipulación; se prioriza la seguridad."
    elif flags["ambiguo"]:
        inc = ("Estas frases pueden referirse a cansancio de una situación y no a hacerse daño, pero un solo mensaje "
               "no permite saberlo: lo más seguro es preguntar directamente.")
    elif nivel == "bajo":
        inc = "Es una lectura basada solo en este mensaje; el riesgo puede cambiar con más contexto."
    else:
        inc = "Es una estimación cualitativa a partir del texto; no es una medición clínica."
    return {"nivel": nivel, "indicadores": ind[:5], "incertidumbre": inc, "flags": flags, "frases": frases}


# ─── Análisis completo ────────────────────────────────

def analizar(texto, modelo_emocion=None, modelo_agresivo=False):
    limpio = limpiar(texto)
    limpio_leet = limpiar(texto, leet=True)
    sarcasmo = _SARCASMO.hay(limpio)
    humor = _HUMOR.hay(limpio)

    emociones, enfasis = detectar_emociones(texto, limpio, modelo_emocion, sarcasmo)
    comp = detectar_comportamientos(texto, limpio, limpio_leet, sarcasmo, humor)
    hostiles = [k for k in ("Insultos", "Descalificación", "Desprecio", "Agresión verbal") if k in comp]
    if hostiles and not any(e["familia"] == "enojo" for e in emociones):
        ev = [x for k in hostiles for x in comp[k]["evidencias"] if not x.startswith("(")][:3]
        emociones.append({"nombre": "Irritación", "familia": "enojo", "evidencias": ev, "peso": 1, "piso": 1, "modelo": False,
                          "intensidad": 4 if len(hostiles) >= 2 else 3, "certeza": "posible"})
        emociones.sort(key=lambda e: (-e["intensidad"], -e["peso"]))
    if modelo_agresivo and "Agresión verbal" not in comp:
        comp["Agresión verbal"] = {"evidencias": ["(lo indica el modelo de IA)"], "nota": None}

    # Intenciones: (nombre, justificación)
    intenciones = []
    for nombre, patron in _INTENC.items():
        ev = [o for o, pos in patron.buscar(limpio) if not _negado(limpio, pos)]
        if ev:
            intenciones.append((nombre, "Aparece " + ", ".join(f"«{x}»" for x in ev[:2]) + "."))
    nombres = [n for n, _ in intenciones]
    riesgo = evaluar_riesgo(limpio, emociones, comp, nombres)
    if riesgo["flags"]["amenaza"] and "Amenaza" not in nombres:
        ev = _buscar(_AMENAZA_VIOLENTA, limpio) + _buscar(_AMENAZA_VAGA, limpio)
        intenciones.insert(0, ("Amenaza", "Comunica una posible consecuencia dañina: «" + (ev[0] if ev else "voy a hacerte daño") + "»."))
    if not intenciones and sum(1 for e in emociones if e["intensidad"] >= 3) >= 2 and "?" not in texto:
        intenciones.append(("Desahogo", "Expresa varias emociones intensas sin hacer una petición concreta."))
    if not intenciones and any(e["nombre"] == "Soledad" for e in emociones):
        intenciones.append(("Búsqueda de apoyo", "Habla de sentirse solo/a."))
    if "?" in texto and not any(n == "Búsqueda de soluciones" for n, _ in intenciones) and emociones \
            and re.search(r"(?<!\w)(que hago|que puedo|como)(?!\w)", limpio):
        intenciones.append(("Búsqueda de soluciones", "Hace una pregunta sobre qué hacer o cómo resolver."))
    nombres = [n for n, _ in intenciones]
    estilo = clasificar_estilo(comp, nombres)

    # Estado emocional
    acumulado = [o for o, _ in _ACUMULACION.buscar(limpio)][:3]
    simultaneas = []
    fams = {e["familia"] for e in emociones}
    nombres_e = {e["nombre"] for e in emociones}
    if "Ambivalencia" in nombres_e:
        simultaneas.append("Hay cariño y malestar al mismo tiempo; no se contradicen necesariamente.")
    if "enojo" in fams and (fams & {"tristeza", "miedo"} or nombres_e & {"Desilusión", "Vergüenza", "Impotencia"}):
        simultaneas.append("El enojo podría estar acompañando tristeza, miedo o decepción; a veces es la parte más visible.")
    if "alegría" in fams and "miedo" in fams:
        simultaneas.append("La alegría convive con inseguridad o preocupación.")

    # Mensajes cotidianos
    cotidiano = None
    if not emociones and not intenciones and not comp:
        if re.search(r"(?<!\w)(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|saludos)(?!\w)", limpio):
            cotidiano = "saludo"
        elif re.search(r"(?<!\w)(gracias|muchas gracias|mil gracias|te agradezco)(?!\w)", limpio):
            cotidiano = "agradecimiento"

    suficiente = bool(emociones or intenciones or comp or cotidiano or riesgo["nivel"] != "bajo")

    notas = []
    if sarcasmo:
        notas.append("Hay expresiones que podrían ser sarcasmo o ironía; las palabras positivas no se leen de forma literal.")
    if humor:
        notas.append("Hay señales de humor (jaja, xd…); el tono podría no ser literal.")
    if enfasis and emociones:
        notas.append("Énfasis en la escritura (" + ", ".join(enfasis) + "): se tomó solo como refuerzo de lo que el texto ya expresa.")
    elif "mayúsculas" in enfasis:
        notas.append("Está escrito en mayúsculas, pero eso por sí solo no indica enojo.")

    return {
        "texto": texto,
        "emociones": emociones, "principal": emociones[0] if emociones else None,
        "secundarias": emociones[1:5], "acumulado": acumulado, "simultaneas": simultaneas,
        "intenciones": intenciones, "comportamientos": comp, "estilo": estilo, "riesgo": riesgo,
        "notas": notas, "suficiente": suficiente, "cotidiano": cotidiano, "sarcasmo": sarcasmo,
        "palabras": len(limpio.split()),
    }

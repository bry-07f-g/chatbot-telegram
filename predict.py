# predict.py - Motor de análisis: modelos de IA + léxico + memoria que aprende
#
# Capas (de la más general a la más específica):
#   1. Modelos preentrenados (pysentimiento): emoción y discurso de odio/agresividad.
#   2. Léxico en español (insultos, amenazas, vulgaridades, emociones) con normalización
#      de tildes, letras repetidas ("idiotaaa") y escritura tipo "1d10ta".
#   3. Reglas de intención por frases.
#   4. Memoria (aprendizaje.py): lo que el usuario corrigió tiene prioridad.
import re
import unicodedata

from pysentimiento import create_analyzer

import aprendizaje

print("🔄 Cargando modelos de pysentimiento...")
emotion_analyzer = create_analyzer(task="emotion", lang="es")
hate_analyzer = create_analyzer(task="hate_speech", lang="es")
print("✅ Modelos cargados correctamente")

# ─── Normalización ────────────────────────────────────

_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def _normalizar(texto):
    """Minúsculas y sin tildes."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _limpiar(texto):
    """Normaliza, des-ofusca ('1d10ta' -> 'idiota') y colapsa letras repetidas ('holaaaa' -> 'hola')."""
    t = _normalizar(texto).translate(_LEET)
    return re.sub(r"(.)\1{2,}", r"\1", t)


def _compilar(frases):
    """Un solo patrón que busca cualquiera de las frases como palabra(s) completa(s)."""
    ordenadas = sorted({_normalizar(f) for f in frases}, key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(f) for f in ordenadas) + r")(?!\w)")


def _hits(patron, texto_limpio):
    return len(set(patron.findall(texto_limpio)))


# ─── Léxico ───────────────────────────────────────────

INSULTOS = [
    "estúpido", "estúpida", "idiota", "imbécil", "pendejo", "pendeja", "cabrón", "cabrona",
    "maldito", "maldita", "desgraciado", "desgraciada", "hdp", "hijo de puta", "hija de puta",
    "eres basura", "eres una basura", "eres un inútil", "eres inútil", "eres una inútil",
    "eres un fracaso", "eres un fracasado", "eres una fracasada", "eres un asco", "eres lo peor",
]
VULGAR = [
    "mierda", "carajo", "joder", "puta", "puto", "gonorrea", "hijueputa", "malparido", "malparida",
]
DESCALIFICACION = [
    "tonto", "tonta", "burro", "burra", "ridículo", "ridícula", "patético", "patética", "necio", "necia",
]
DESPRECIO = [
    "te odio", "no te soporto", "no sirves", "me das asco", "das asco", "qué asco", "cállate",
    "cierra la boca", "lárgate", "vete a la mierda", "no vales nada", "nadie te quiere",
    "ojalá te mueras", "me tienes harto", "me tienes harta", "estoy harto de ti", "estoy harta de ti",
    "me tienes mamado", "me tienes mamada", "me arrepiento de haberte conocido",
]
AMENAZAS = [
    "te voy a pegar", "te voy a matar", "te voy a golpear", "te voy a buscar", "te voy a acabar",
    "me las vas a pagar", "te vas a arrepentir", "te vas a acordar de mí", "te arrepentirás",
]
CRISIS = [
    "quiero morirme", "me quiero morir", "quiero morir", "no quiero vivir", "ya no quiero vivir",
    "quitarme la vida", "acabar con mi vida", "suicidarme", "suicidio", "hacerme daño",
    "me voy a matar", "no vale la pena vivir", "ya no quiero estar aquí", "desaparecer para siempre",
]

# etiqueta de pysentimiento -> palabras que la delatan en el texto
LEXICO_EMOCION = {
    "anger": ["harto", "harta", "furioso", "furiosa", "rabia", "molesto", "molesta", "enojado", "enojada",
              "enfurecido", "indignado", "indignada", "me tienes harto", "me tienes harta"],
    "sadness": ["triste", "tristeza", "llorar", "llorando", "deprimido", "deprimida", "vacío", "sin ganas",
                "me duele", "decepcionado", "decepcionada", "desanimado", "desanimada"],
    "fear": ["miedo", "asustado", "asustada", "terror", "pánico", "me da susto", "me da miedo",
             "preocupado", "preocupada", "ansiedad", "angustia"],
    "disgust": ["asco", "repugnante", "asqueroso", "asquerosa", "me da asco", "qué asco"],
    "surprise": ["wow", "no puedo creer", "increíble", "sorprendido", "sorprendida", "sorpresa", "no lo esperaba"],
    "joy": ["feliz", "alegre", "contento", "contenta", "te quiero", "te amo", "te adoro", "me encanta",
            "genial", "excelente", "emocionado", "emocionada", "gracias"],
}

P_INSULTOS = _compilar(INSULTOS)
P_VULGAR = _compilar(VULGAR)
P_DESCALIF = _compilar(DESCALIFICACION)
P_DESPRECIO = _compilar(DESPRECIO)
P_AMENAZAS = _compilar(AMENAZAS)
P_AMENAZA_RE = re.compile(r"(?<!\w)te voy a (pegar|matar|golpear|buscar|acabar|romper)(?!\w)")
P_CRISIS = _compilar(CRISIS)
P_EMOCION = {k: _compilar(v) for k, v in LEXICO_EMOCION.items()}


def analizar_lexico(texto):
    """Busca señales de toxicidad, amenaza, crisis y emoción en el propio texto."""
    limpio = _limpiar(texto)
    senales, nivel = [], 0

    n = _hits(P_INSULTOS, limpio)
    if n:
        nivel += 40 + 10 * (n - 1)
        senales.append("insultos")
    if _hits(P_DESPRECIO, limpio):
        nivel += 35
        senales.append("frases hirientes")
    amenaza = bool(_hits(P_AMENAZAS, limpio) or P_AMENAZA_RE.search(limpio))
    if amenaza:
        nivel += 60
        senales.append("amenaza")
    if _hits(P_VULGAR, limpio):
        nivel += 25
        senales.append("lenguaje vulgar")
    if _hits(P_DESCALIF, limpio):
        nivel += 20
        senales.append("descalificación")

    letras = [c for c in texto if c.isalpha()]
    if len(letras) >= 8 and sum(c.isupper() for c in letras) / len(letras) >= 0.7:
        senales.append("mayúsculas (gritos)")
        if nivel:
            nivel += 15
    if texto.count("!") >= 3:
        senales.append("muchos signos de exclamación")
        if nivel:
            nivel += 10

    crisis = bool(_hits(P_CRISIS, limpio))
    if crisis:
        senales.append("mención de hacerse daño")

    conteo = {k: _hits(p, limpio) for k, p in P_EMOCION.items()}
    emocion = max(conteo, key=conteo.get) if any(conteo.values()) else None

    return {"nivel": min(nivel, 100), "senales": senales, "amenaza": amenaza, "crisis": crisis, "emocion": emocion}


# ─── Intención (reglas por frases) ────────────────────

# Orden = prioridad. La primera categoría que coincida gana.
REGLAS_INTENCION = [
    ("afecto", ["te quiero", "te amo", "me gustas", "te extraño", "te necesito", "te adoro"]),
    ("reclamo", ["por qué no respondes", "por qué no me respondes", "no me respondes", "me ignoras",
                 "no contestas", "por qué tardas", "por qué demoras", "no me escribes"]),
    ("celos", ["con quién", "quién es", "te veo con", "andabas con", "quién te escribió", "quién te habla"]),
    ("agresion", ["odio", "mierda", "qué asco"] + INSULTOS + DESPRECIO + AMENAZAS),
    ("ruptura", ["terminar", "dejar", "no quiero seguir", "acabó", "se acabó", "hasta aquí", "se terminó"]),
    ("manipulacion", ["si me quisieras", "deberías", "nunca haces", "siempre igual", "como siempre",
                      "si realmente me quisieras"]),
    ("control", ["dónde estás", "con quién hablas", "dime la verdad", "ubicación", "envía ubicación"]),
    ("desinteres", ["ok", "vale", "ah", "ya", "como digas", "da igual", "me da igual", "jaja", "jeje", "ok ok"]),
    ("curiosidad", ["qué tal", "cómo estás", "qué haces", "cómo te va", "en qué andas", "qué cuentas"]),
    ("tristeza", ["triste", "deprimido", "deprimida", "mal", "me siento solo", "me siento sola",
                  "estoy solo", "estoy sola", "soledad", "llorar", "llorando", "me siento mal"]),
    ("agradecimiento", ["gracias", "muchas gracias", "te agradezco", "mil gracias"]),
    ("saludo", ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches", "hey", "saludos"]),
]
_REGLAS = [(nombre, _compilar(frases)) for nombre, frases in REGLAS_INTENCION]


def detectar_intencion(texto):
    limpio = _limpiar(texto)
    for intencion, patron in _REGLAS:
        if patron.search(limpio):
            return intencion
    return "normal"


# ─── Ghosting ─────────────────────────────────────────

_P_DESINTERES = _compilar(["ok", "vale", "ah", "ya", "luego", "ocupado", "ahora no", "después", "mañana",
                           "ahora no puedo"])


def calcular_ghosting(texto, intencion, emocion):
    # Saludos y agradecimientos son cortos pero no indican ghosting
    if intencion in ("saludo", "agradecimiento", "crisis"):
        return 0

    score = 0
    texto = texto.lower()

    if len(texto) <= 5:
        score += 35
    if len(texto.split()) == 1:
        score += 25
    if _P_DESINTERES.search(_limpiar(texto)):
        score += 30

    if intencion == "desinteres":
        score += 35
    elif intencion == "reclamo":
        score += 15
    elif intencion == "afecto":
        score -= 25

    if emocion in ["sadness", "anger", "fear", "disgust"]:
        score += 10
    elif emocion in ["joy", "surprise"]:
        score -= 15

    return max(0, min(score, 95))


# ─── Riesgo ───────────────────────────────────────────

INTENCIONES_CONFLICTO = ["celos", "reclamo", "ruptura", "manipulacion", "agresion", "control"]


def calcular_riesgo(nivel_toxico, intencion, emocion, crisis=False, amenaza=False):
    if crisis or amenaza or nivel_toxico >= 70:
        return "🔴 Alto"
    if nivel_toxico >= 40 or intencion in INTENCIONES_CONFLICTO or emocion in ["anger", "disgust"]:
        return "🟡 Medio"
    return "🟢 Bajo"


# ─── Emociones ────────────────────────────────────────

EMOCION_MAP = {
    "joy": "positivo", "sadness": "tristeza", "anger": "enojo", "surprise": "sorpresa",
    "disgust": "disgusto", "fear": "miedo", "others": "neutral", "neutral": "neutral",
}


def mapear_emocion(emocion_raw):
    return EMOCION_MAP.get(emocion_raw, "neutral")


# pysentimiento devuelve la salida de hate_speech como LISTA de etiquetas (multietiqueta):
# p. ej. ['hateful', 'aggressive']. Se acepta también un texto suelto por si cambia la versión.
ETIQUETAS_TOXICAS = ("hateful", "targeted", "aggressive")


def _nivel_modelo_odio(pred):
    salida = pred.output
    etiquetas = [salida] if isinstance(salida, str) else list(salida or [])
    probas = getattr(pred, "probas", None) or {}
    nivel = max([int(probas.get(k, 0) * 100) for k in ETIQUETAS_TOXICAS] + [0])
    if any(e in ETIQUETAS_TOXICAS for e in etiquetas):
        nivel = max(nivel, 50)
    return nivel


# ─── Función principal ────────────────────────────────

def analizar_texto(texto):
    lex = analizar_lexico(texto)

    # 1) Emoción (modelo)
    emo_raw, emo_conf, emo_top = "others", 0.0, []
    try:
        pred = emotion_analyzer.predict(texto)
        emo_raw = pred.output
        emo_conf = float(pred.probas.get(emo_raw, 0.0))
        emo_top = sorted(((k, v) for k, v in pred.probas.items() if k != "others"), key=lambda x: -x[1])
    except Exception as e:
        print(f"Error en modelo de emociones: {e}")

    # 2) Toxicidad (modelo + léxico)
    odio = 0
    try:
        odio = _nivel_modelo_odio(hate_analyzer.predict(texto))
    except Exception as e:
        print(f"Error en modelo de toxicidad: {e}")
    nivel_toxico = max(lex["nivel"], odio)
    if odio >= 50 and "lenguaje agresivo (IA)" not in lex["senales"]:
        lex["senales"].append("lenguaje agresivo (IA)")

    # 3) Emoción final: si el modelo no ve nada claro, usa lo que dice el texto
    emocion_raw = emo_raw
    if lex["emocion"] and (emo_raw == "others" or emo_conf < 0.45):
        emocion_raw = lex["emocion"]
    if nivel_toxico >= 40 and emocion_raw not in ("anger", "disgust", "fear", "sadness"):
        emocion_raw = "anger"
    usa_modelo = emocion_raw == emo_raw
    emociones_top = [(mapear_emocion(k), int(v * 100)) for k, v in emo_top[:3] if v >= 0.15] if usa_modelo else []

    # 4) Intención: crisis > memoria > reglas
    origen = "reglas"
    intencion = detectar_intencion(texto)
    if lex["crisis"]:
        intencion = "crisis"
    else:
        if intencion == "normal":
            if nivel_toxico >= 40:
                intencion = "agresion"
            elif emocion_raw == "sadness" and emo_conf >= 0.6:
                intencion = "tristeza"
        aprendido = aprendizaje.predecir(texto)
        if aprendido:
            intencion, origen = aprendido[0], "aprendido"
    if intencion == "agresion":
        nivel_toxico = max(nivel_toxico, 40)

    ghosting = calcular_ghosting(texto, intencion, emocion_raw)
    riesgo = calcular_riesgo(nivel_toxico, intencion, emocion_raw, lex["crisis"], lex["amenaza"])

    return {
        "emocion": mapear_emocion(emocion_raw),
        "emocion_confianza": int(emo_conf * 100) if usa_modelo and emo_raw != "others" else None,
        "emociones_top": emociones_top,
        "toxicidad": "si" if nivel_toxico >= 40 else "no",
        "toxicidad_nivel": nivel_toxico,
        "ghosting": ghosting,
        "riesgo": riesgo,
        "intencion": intencion,
        "origen": origen,
        "senales": lex["senales"],
    }

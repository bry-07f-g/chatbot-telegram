# predict.py - Versión para pysentimiento 0.7.3
from pysentimiento import create_analyzer

# ─── Modelos preentrenados ─────────────────────────

print("🔄 Cargando modelos de pysentimiento...")
emotion_analyzer = create_analyzer(task="emotion", lang="es")
hate_analyzer = create_analyzer(task="hate_speech", lang="es")
print("✅ Modelos cargados correctamente")

# ─── Intención (reglas mejoradas) ─────────────────────

import re
import unicodedata

def _normalizar(texto):
    """Minúsculas y sin tildes, para que 'por qué' y 'por que' coincidan."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

def _contiene(texto, frases):
    """True si alguna frase aparece como palabra completa (no dentro de otra palabra)."""
    for frase in frases:
        patron = r"(?<!\w)" + re.escape(_normalizar(frase)) + r"(?!\w)"
        if re.search(patron, texto):
            return True
    return False

# Orden = prioridad. La primera categoría que coincida gana.
REGLAS_INTENCION = [
    ("afecto", ["te quiero", "te amo", "me gustas", "te extraño", "te necesito", "te adoro"]),
    ("reclamo", ["por qué no respondes", "por qué no me respondes", "no me respondes", "me ignoras", "no contestas", "por qué tardas", "por qué demoras", "no me escribes"]),
    ("celos", ["con quién", "quién es", "te veo con", "andabas con", "quién te escribió", "quién te habla"]),
    ("agresion", ["odio", "estúpido", "idiota", "imbécil", "estúpida", "mierda", "qué asco"]),
    ("ruptura", ["terminar", "dejar", "no quiero seguir", "acabó", "se acabó", "hasta aquí", "se terminó"]),
    ("manipulacion", ["si me quisieras", "deberías", "nunca haces", "siempre igual", "como siempre", "si realmente me quisieras"]),
    ("control", ["dónde estás", "con quién hablas", "dime la verdad", "ubicación", "envía ubicación"]),
    ("desinteres", ["ok", "vale", "ah", "ya", "como digas", "da igual", "me da igual", "jaja", "jeje", "ok ok"]),
    ("curiosidad", ["qué tal", "cómo estás", "qué haces", "cómo te va", "en qué andas", "qué cuentas"]),
    ("tristeza", ["triste", "deprimido", "mal", "solo", "soledad", "llorar", "me siento mal"]),
]

def detectar_intencion(texto):
    texto = _normalizar(texto)
    for intencion, frases in REGLAS_INTENCION:
        if _contiene(texto, frases):
            return intencion
    return "normal"

# ─── Ghosting ─────────────────────────────────────────

def calcular_ghosting(texto, intencion, emocion):
    score = 0
    texto = texto.lower()
    
    # Mensajes muy cortos
    if len(texto) <= 5:
        score += 35
    
    # Respuesta de una palabra
    if len(texto.split()) == 1:
        score += 25
    
    # Palabras que indican desinterés
    if any(palabra in texto for palabra in ["ok", "vale", "ah", "ya", "luego", "ocupado", "ahora no", "después", "mañana", "ahora no puedo"]):
        score += 30
    
    # Intención relacionada
    if intencion == "desinteres":
        score += 35
    elif intencion == "reclamo":
        score += 15
    elif intencion == "afecto":
        score -= 25
    
    # Emoción negativa
    if emocion in ["sadness", "anger", "fear", "disgust"]:
        score += 10
    elif emocion in ["joy", "surprise"]:
        score -= 15
    
    return max(0, min(score, 95))

# ─── Calcular riesgo ───────────────────────────────────

def calcular_riesgo(hate_result, intencion, emocion):
    # Verificar si hay hate_speech
    if hate_result.output == "hateful" or hate_result.output == "targeted":
        return "🔴 Alto"
    elif intencion in ["celos", "reclamo", "ruptura", "manipulacion", "agresion"]:
        return "🟡 Medio"
    elif emocion in ["anger", "disgust"]:
        return "🟡 Medio"
    else:
        return "🟢 Bajo"

# ─── Mapear emociones ───────────────────────────────────

def mapear_emocion(emocion_raw):
    emocion_map = {
        'joy': 'positivo',
        'sadness': 'tristeza',
        'anger': 'enojo',
        'surprise': 'sorpresa',
        'disgust': 'disgusto',
        'fear': 'miedo',
        'neutral': 'neutral'
    }
    return emocion_map.get(emocion_raw, 'neutral')

# ─── Función principal ─────────────────────────────────

def analizar_texto(texto):
    try:
        # 🔥 MODELOS IA con pysentimiento
        emocion_pred = emotion_analyzer.predict(texto)
        hate_pred = hate_analyzer.predict(texto)
        
        # Obtener emoción principal
        emocion_raw = emocion_pred.output
        emocion = mapear_emocion(emocion_raw)
        
        # Toxicidad (basada en hate_speech)
        toxicidad = "si" if hate_pred.output in ["hateful", "targeted"] else "no"
        
        # Intención (reglas)
        intencion = detectar_intencion(texto)
        
        # Ghosting
        ghosting = calcular_ghosting(texto, intencion, emocion_raw)
        
        # Riesgo
        riesgo = calcular_riesgo(hate_pred, intencion, emocion_raw)
        
        # Confianza
        confianza = max(emocion_pred.probas.values())
        
        return emocion, toxicidad, ghosting, riesgo, intencion, int(confianza * 100)
    
    except Exception as e:
        print(f"Error en analizar_texto: {e}")
        return "neutral", "no", 0, "🟢 Bajo", "normal", 50
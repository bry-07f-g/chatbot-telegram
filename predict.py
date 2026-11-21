# predict.py - Une los modelos de IA (pysentimiento) con el análisis por texto de analisis.py
from pysentimiento import create_analyzer

import analisis

print("🔄 Cargando modelos de pysentimiento...")
emotion_analyzer = create_analyzer(task="emotion", lang="es")
hate_analyzer = create_analyzer(task="hate_speech", lang="es")
print("✅ Modelos cargados correctamente")

# pysentimiento devuelve la salida de hate_speech como LISTA de etiquetas (multietiqueta),
# p. ej. ['hateful', 'aggressive']; por eso se acepta lista o texto.
ETIQUETAS_AGRESIVAS = ("hateful", "targeted", "aggressive")


def _es_agresivo(pred):
    salida = pred.output
    etiquetas = [salida] if isinstance(salida, str) else list(salida or [])
    probas = getattr(pred, "probas", None) or {}
    return any(e in ETIQUETAS_AGRESIVAS for e in etiquetas) or \
        max([probas.get(k, 0) for k in ETIQUETAS_AGRESIVAS] + [0]) >= 0.5


def analizar_texto(texto):
    """Devuelve el análisis completo (ver analisis.analizar). Los modelos de IA solo corroboran o complementan."""
    modelo_emocion, agresivo = None, False
    try:
        pred = emotion_analyzer.predict(texto)
        modelo_emocion = (pred.output, float(pred.probas.get(pred.output, 0.0)))
    except Exception as e:
        print(f"Error en modelo de emociones: {e}")
    try:
        agresivo = _es_agresivo(hate_analyzer.predict(texto))
    except Exception as e:
        print(f"Error en modelo de agresividad: {e}")
    return analisis.analizar(texto, modelo_emocion, agresivo)

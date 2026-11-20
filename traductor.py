# traductor.py - Comando /traducir: traduce un texto y genera el audio de pronunciación
import html
from io import BytesIO

from deep_translator import GoogleTranslator
from gtts import gTTS

# nombre en español -> (código, nombre para mostrar)
IDIOMAS = {
    "ingles": ("en", "Inglés"),
    "español": ("es", "Español"),
    "espanol": ("es", "Español"),
    "frances": ("fr", "Francés"),
    "aleman": ("de", "Alemán"),
    "italiano": ("it", "Italiano"),
    "portugues": ("pt", "Portugués"),
    "japones": ("ja", "Japonés"),
    "coreano": ("ko", "Coreano"),
    "chino": ("zh-CN", "Chino"),
}

USO = (
    "ℹ️ Uso: /traducir <idioma> <texto>\n"
    "Ejemplo: /traducir japonés hola como estas\n"
    "Idiomas: inglés, francés, alemán, italiano, portugués, japonés, coreano, chino, español"
)


def _sin_tildes(s: str) -> str:
    return s.lower().translate(str.maketrans("áéíóúü", "aeiouu"))


def parsear_comando(args):
    """Devuelve (codigo, nombre, texto) o None si los argumentos no son válidos."""
    if len(args) < 2:
        return None
    clave = _sin_tildes(args[0])
    if clave not in IDIOMAS:
        return None
    codigo, nombre = IDIOMAS[clave]
    return codigo, nombre, " ".join(args[1:])


def traducir(texto: str, codigo: str) -> str:
    return GoogleTranslator(source="auto", target=codigo).translate(texto)


def generar_audio(texto: str, codigo: str) -> BytesIO:
    # gTTS usa 'zh-CN' como 'zh-CN' y el resto igual que los códigos de arriba
    audio = BytesIO()
    gTTS(text=texto, lang=codigo).write_to_fp(audio)
    audio.seek(0)
    audio.name = "pronunciacion.mp3"
    return audio


def formatear(original: str, resultado: str, codigo: str) -> str:
    return (
        f"🌐 <b>Traducción ({codigo.split('-')[0].upper()})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Original:</b>\n{html.escape(original)}\n\n"
        f"✅ <b>Resultado:</b>\n{html.escape(resultado)}"
    )

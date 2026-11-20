import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from predict import analizar_texto

# ─── Configuración ──────────────────────────────────────

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ERROR: Variable TELEGRAM_TOKEN no configurada")
    print("📌 Configuración:")
    print("   En PowerShell: $env:TELEGRAM_TOKEN='tu_token_aqui'")
    exit(1)

# ─── Datos ──────────────────────────────────────────────

# INTERPRETACIONES: Qué significa el mensaje que te enviaron
INTERPRETACIONES = {
    "reclamo": [
        "📢 La persona se siente ignorada y reclama tu atención.",
        "😤 Hay frustración porque esperaba una respuesta y no llegó.",
        "💢 Percibe que la estás descuidando o ignorando.",
    ],
    "celos": [
        "😒 Siente inseguridad y teme que haya un tercero.",
        "🔍 Necesita confirmar que sigue siendo importante para ti.",
        "🤨 Desconfía de tus acciones o amistades.",
    ],
    "agresion": [
        "⚠️ Está muy enojado y busca herir o provocar.",
        "🔥 El conflicto puede escalar si respondes de forma similar.",
        "💥 Hay agresividad que debes manejar con cuidado.",
    ],
    "tristeza": [
        "😢 Está pasando por un momento difícil o de dolor.",
        "🫂 Necesita apoyo emocional y contención.",
        "💔 Hay vulnerabilidad, no lo ignores.",
    ],
    "manipulacion": [
        "🎭 Está usando culpa o condiciones para obtener lo que quiere.",
        "⛓️ Quiere presionarte emocionalmente para que actúes.",
        "⚠️ Ten cuidado con responder desde la culpa.",
    ],
    "control": [
        "🔒 Quiere saber todo lo que haces y con quién.",
        "👁️ Hay una necesidad excesiva de controlarte.",
        "📱 No confía plenamente en ti.",
    ],
    "ruptura": [
        "💔 Está considerando seriamente terminar la relación.",
        "😩 Hay agotamiento emocional acumulado.",
        "🚪 Quiere distancia o poner un punto final.",
    ],
    "desinteres": [
        "😐 No muestra interés en seguir la conversación.",
        "❄️ Hay distancia emocional o está ocupado.",
        "📉 Probablemente no quiere profundizar.",
    ],
    "inseguridad": [
        "😟 Tiene dudas sobre la relación o sobre sí mismo.",
        "🤔 Necesita reafirmación y seguridad.",
        "🌀 Busca calmar su ansiedad con respuestas claras.",
    ],
    "afecto": [
        "💕 Está expresando cariño y buenos sentimientos.",
        "🤗 Quiere acercarse y fortalecer el vínculo.",
        "🌸 Hay conexión emocional positiva.",
    ],
    "curiosidad": [
        "🤔 Tiene interés genuino en ti y tu vida.",
        "💬 Quiere iniciar o mantener una conversación.",
        "🔍 Busca conocer más sobre ti.",
    ],
    "normal": [
        "💬 Es una conversación cotidiana sin carga emocional.",
        "✅ No hay señales de conflicto ni urgencia.",
        "📝 Todo fluye con normalidad.",
    ],
}

# SUGERENCIAS: Cómo responder al mensaje (para TI)
SUGERENCIAS = {
    "reclamo": [
        "🗣️ Responde: 'Entiendo que te sientes ignorado, no fue mi intención. Hablemos.'",
        "⏸️ Reconoce su molestia antes de dar explicaciones: 'Tienes razón, no respondí rápido.'",
        "🤝 Pregunta: '¿Qué puedo hacer para que no te sientas así?'",
    ],
    "celos": [
        "🧠 Responde con calma: 'No hay nadie más, pero entiendo tu inseguridad.'",
        "💬 Valida su emoción: 'Veo que esto te preocupa, hablemos sin pelear.'",
        "🔐 Reafirma: 'Eres importante para mí. ¿Podemos hablar de esto tranquilos?'",
    ],
    "agresion": [
        "🌬️ No respondas con agresión. Di: 'Esto se está poniendo feo, hablemos más tarde.'",
        "🚫 Establece límite: 'No voy a responder si me hablas así.'",
        "⏰ Tómate un tiempo: 'Mejor hablamos cuando estemos más calmados.'",
    ],
    "tristeza": [
        "👥 Responde: 'Estoy aquí para ti. ¿Quieres hablar de lo que pasa?'",
        "💬 Muestra apoyo: 'Lamento que te sientas así, cuentas conmigo.'",
        "🤗 Ofrece compañía: '¿Necesitas desahogarte o prefieres distraerte?'",
    ],
    "manipulacion": [
        "🚩 No cedas por culpa. Di: 'No me gusta que me condiciones así.'",
        "🗣️ Marca límite: 'Si me quieres pedir algo, hazlo sin chantajes.'",
        "⚖️ Responde neutro: 'Te escucho, pero no voy a reaccionar desde la culpa.'",
    ],
    "control": [
        "🤝 Responde: 'Confío en ti y espero que tú confíes en mí.'",
        "📱 Marca espacio: 'Está bien que quieras saber, pero también necesito mi espacio.'",
        "🧘 Tranquiliza: 'No pasa nada, pero no puedo responder todo el tiempo.'",
    ],
    "ruptura": [
        "💬 Responde: 'Hablemos esto en persona, es importante.'",
        "🤔 Pide tiempo: 'No tomemos decisiones en caliente. Hablemos mañana.'",
        "🕊️ Si es firme: 'Lo respeto si es tu decisión, pero me duele.'",
    ],
    "desinteres": [
        "🧐 Pregunta: '¿Estás bien? Parece que no tienes ganas de hablar.'",
        "💬 Dale espacio: 'Cuando quieras hablar, aquí estoy.'",
        "⏸️ No insistas: 'Ok, hablamos cuando tengas tiempo.'",
    ],
    "inseguridad": [
        "🔍 Responde: 'Estoy contigo, no tienes nada que temer.'",
        "💬 Tranquiliza: 'Si algo te preocupa, pregúntame sin miedo.'",
        "📖 Reafirma: 'Me importas y no tengo nada que ocultar.'",
    ],
    "afecto": [
        "🌸 Corresponde: 'Yo también te quiero mucho ❤️'",
        "💌 Agradece: 'Qué bonito mensaje, gracias por tus palabras.'",
        "🎁 Sorprende: 'Me hiciste el día, te quiero igual.'",
    ],
    "curiosidad": [
        "🔍 Responde con entusiasmo: 'Todo bien, ¿y tú? Cuéntame.'",
        "💬 Aprovecha: 'Justo pensaba en ti. ¿Qué has hecho?'",
        "🌟 Sigue la conversación: 'Me alegra que preguntes, te cuento...'",
    ],
    "normal": [
        "👍 Responde con naturalidad: 'Todo bien, ¿y tú?'",
        "💬 Sigue la conversación: 'Qué bueno, seguimos hablando.'",
        "🌟 Mantén el tono: 'Genial, cualquier cosa me dices.'",
    ],
}

EMOJIS = {
    "reclamo": "😔",
    "celos": "😒",
    "agresion": "⚠️",
    "tristeza": "😢",
    "manipulacion": "🚩",
    "control": "🔒",
    "ruptura": "💔",
    "desinteres": "😶",
    "inseguridad": "😟",
    "afecto": "💕",
    "curiosidad": "🤔",
    "normal": "💬",
}

EMOJIS_EMOCION = {
    "positivo": "😊",
    "tristeza": "😢",
    "enojo": "😠",
    "sorpresa": "😲",
    "disgusto": "😖",
    "miedo": "😨",
    "neutral": "😐",
}

# ─── Funciones auxiliares ───────────────────────────────

def construir_barra(valor: int) -> str:
    bloques = valor // 10
    return "█" * bloques + "░" * (10 - bloques)

def obtener_texto(diccionario, clave, default="normal"):
    return random.choice(diccionario.get(clave, diccionario[default]))

def formatear_respuesta(datos: dict) -> str:
    return (
        f"{datos['emoji_principal']} *Análisis del mensaje que te enviaron*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{datos['emoji_emocion']} *Emoción detectada:* {datos['emocion']}\n"
        f"🚩 *Toxicidad:* {datos['toxicidad']}\n"
        f"🧠 *Intención:* {datos['intencion']}\n"
        f"💔 *Ghosting:* {datos['ghosting_bar']} {datos['ghosting']}%\n"
        f"🔥 *Riesgo:* {datos['riesgo']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Qué significa:*\n{datos['interpretacion']}\n\n"
        f"💬 *Cómo responder:*\n{datos['sugerencia']}"
    )

# ─── Comandos ───────────────────────────────────────────

MENSAJE_AYUDA = (
    "🤖 *Chat Analyzer Bot*\n"
    "Pégame un mensaje que te hayan enviado y te digo qué significa y cómo responderlo.\n\n"
    "*Comandos:*\n"
    "/start - Saludo e introducción\n"
    "/ayuda - Muestra esta ayuda\n\n"
    "*Ejemplo:* escribe `por qué no me respondes` y recibirás el análisis."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "amigo"
    await update.message.reply_text(f"👋 ¡Hola, {nombre}!\n\n" + MENSAJE_AYUDA, parse_mode="Markdown")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENSAJE_AYUDA, parse_mode="Markdown")

# ─── Handler principal ──────────────────────────────────

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        
        emocion, toxicidad, ghosting, riesgo, intencion, confianza = analizar_texto(texto)
        
        datos = {
            "emoji_principal": EMOJIS.get(intencion, "💬"),
            "emoji_emocion": EMOJIS_EMOCION.get(emocion, "😐"),
            "emocion": emocion.capitalize(),
            "toxicidad": "🔴 Alta" if toxicidad == "si" else "🟢 Baja",
            "intencion": intencion.capitalize(),
            "ghosting": ghosting,
            "ghosting_bar": construir_barra(ghosting),
            "riesgo": riesgo,
            "interpretacion": obtener_texto(INTERPRETACIONES, intencion),
            "sugerencia": obtener_texto(SUGERENCIAS, intencion),
        }
        
        respuesta = formatear_respuesta(datos)
        await update.message.reply_text(respuesta, parse_mode="Markdown")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar el mensaje.")

# ─── Inicialización ─────────────────────────────────────

def main():
    print("🤖 Bot de análisis de mensajes activo...")
    print("📌 Analizo los mensajes que TE ENVÍAN y te digo cómo responder")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()

if __name__ == "__main__":
    main()
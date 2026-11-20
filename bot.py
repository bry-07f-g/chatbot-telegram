import asyncio
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from predict import analizar_texto
import traductor

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
    "saludo": [
        "👋 Está iniciando la conversación de forma amable.",
        "💬 Quiere abrir el diálogo o saber cómo estás.",
        "🙂 No hay señales de conflicto; es un saludo.",
    ],
    "agradecimiento": [
        "🙏 Está agradeciendo algo que hiciste o dijiste.",
        "😊 Hay buena disposición y reconocimiento hacia ti.",
        "🤝 La conversación va en un tono positivo.",
    ],
    "normal": [
        "💬 Es una conversación cotidiana sin carga emocional.",
        "✅ No hay señales de conflicto ni urgencia.",
        "📝 Todo fluye con normalidad.",
    ],
}

# SUGERENCIAS: respuestas listas para enviar + un consejo (para TI)
SUGERENCIAS = {
    "reclamo": {
        "respuestas": [
            "Tienes razón, me demoré en responderte y lo siento. Ya estoy aquí, cuéntame.",
            "Perdón por dejarte esperando, no fue mi intención ignorarte. ¿Hablamos ahora?",
            "Entiendo que te molestó que no respondiera. Estaba ocupado, pero me importas. ¿Qué necesitas?",
            "Gracias por decírmelo. Voy a tratar de avisarte cuando no pueda responder.",
        ],
        "consejo": "Primero reconoce su molestia y después explica. Si empiezas con excusas, se siente peor.",
    },
    "celos": {
        "respuestas": [
            "Estaba con un amigo, no pasa nada raro. Si algo te preocupa, dímelo con calma.",
            "Entiendo que te genere duda. Te cuento con gusto cómo estuvo mi día.",
            "Eres importante para mí y no tengo nada que ocultar. ¿Qué es lo que te inquieta?",
            "No hay nadie más. Prefiero que hablemos de esto tranquilos y no peleando.",
        ],
        "consejo": "No te pongas a la defensiva. Responde con calma y con datos simples; eso baja la tensión.",
    },
    "agresion": {
        "respuestas": [
            "Así no me gusta hablar. Cuando estemos más tranquilos lo conversamos.",
            "Entiendo que estás molesto, pero no voy a seguir si me tratas así.",
            "Prefiero parar aquí para no decir algo de lo que me arrepienta. Hablamos más tarde.",
            "Veo que estás muy enojado. Dime qué pasó y lo resolvemos con respeto.",
        ],
        "consejo": "No respondas con insultos ni en caliente. Poner un límite claro y pausar la conversación suele funcionar mejor.",
    },
    "tristeza": {
        "respuestas": [
            "Lamento mucho que estés así. Estoy aquí para escucharte, ¿qué pasó?",
            "Cuenta conmigo para lo que necesites. ¿Quieres hablar o prefieres que te acompañe un rato?",
            "No estás solo en esto. Si quieres desahogarte, te leo con calma.",
            "Gracias por contármelo. ¿Hay algo que pueda hacer para ayudarte hoy?",
        ],
        "consejo": "No minimices lo que siente con frases como 'no es para tanto'. Escuchar primero ayuda más que dar soluciones.",
    },
    "manipulacion": {
        "respuestas": [
            "Quiero ayudarte, pero no me gusta que me pidas las cosas con culpa. Dímelo directo.",
            "Te escucho, pero voy a decidir con calma y no por presión.",
            "Entiendo lo que sientes. Hablemos de lo que necesitas sin condiciones.",
            "Si te molestó algo, podemos hablarlo. Los chantajes no me ayudan a entenderte.",
        ],
        "consejo": "No cedas solo por sentirte culpable. Puedes ser amable y aun así mantener tu decisión.",
    },
    "control": {
        "respuestas": [
            "Estoy bien, no te preocupes. Te cuento más tarde cómo me fue.",
            "Confío en ti y espero que confíes en mí. Necesito también mi espacio.",
            "Está bien que quieras saber de mí, pero no puedo avisar cada cosa que hago.",
            "Hablemos de cómo podemos sentirnos tranquilos los dos sin tener que vigilarnos.",
        ],
        "consejo": "Si pasa seguido, conversa sobre acuerdos de confianza. Compartir todo por presión no es sano.",
    },
    "ruptura": {
        "respuestas": [
            "Esto es importante y no quiero hablarlo por mensaje. ¿Podemos vernos o llamarnos?",
            "No tomemos una decisión tan grande en caliente. Hablemos mañana con calma.",
            "Me duele leer eso. ¿Qué es lo que más te ha pesado últimamente?",
            "Si de verdad lo sientes así, lo voy a respetar, pero quiero entender por qué.",
        ],
        "consejo": "Evita rogar o contestar con rabia. Pide hablar en persona o por llamada.",
    },
    "desinteres": {
        "respuestas": [
            "Te noto distante. ¿Estás bien o prefieres que hablemos más tarde?",
            "Cuando tengas tiempo me escribes, aquí estaré.",
            "Si no es buen momento, no hay problema. Hablamos luego.",
            "¿Pasó algo? Sé que a veces uno no tiene ganas de hablar, y está bien.",
        ],
        "consejo": "No insistas con muchos mensajes seguidos. Deja una puerta abierta y dale espacio.",
    },
    "inseguridad": {
        "respuestas": [
            "Estoy contigo, puedes preguntarme lo que quieras sin miedo.",
            "Me importas y no tengo nada que ocultarte. ¿Qué te preocupa?",
            "Es normal tener dudas a veces. Hablemos de ellas con calma.",
            "Gracias por ser sincero conmigo. Cuenta con mi apoyo.",
        ],
        "consejo": "Responde con claridad y sin ironía. Una respuesta concreta tranquiliza más que una larga.",
    },
    "afecto": {
        "respuestas": [
            "Yo también te quiero mucho ❤️",
            "Qué lindo mensaje, me alegraste el día. Gracias por decírmelo.",
            "Me haces muy feliz, yo también te extraño.",
            "Gracias por tus palabras. Me encanta tenerte en mi vida.",
        ],
        "consejo": "Responde con sinceridad; no hace falta algo largo. Un detalle personal hace que se sienta más real.",
    },
    "curiosidad": {
        "respuestas": [
            "¡Todo bien por aquí! ¿Y tú, cómo vas? Cuéntame.",
            "Bien, gracias por preguntar. Hoy estuve muy ocupado, ¿y tú qué hiciste?",
            "Aquí andamos, con ganas de saber de ti. ¿Cómo te fue hoy?",
            "Todo tranquilo. Me alegra que me escribas, ¿qué cuentas?",
        ],
        "consejo": "Devuelve la pregunta para que la conversación siga fluyendo.",
    },
    "saludo": {
        "respuestas": [
            "¡Hola! ¿Cómo estás?",
            "¡Hola! Qué gusto saludarte, ¿cómo va todo?",
            "¡Buenas! ¿Qué tal tu día?",
            "¡Hola! Aquí estoy, cuéntame.",
        ],
        "consejo": "Un saludo amable y una pregunta corta abren bien la conversación.",
    },
    "agradecimiento": {
        "respuestas": [
            "¡De nada! Para eso estamos.",
            "Con gusto, me alegra haber ayudado.",
            "No hay de qué, cuando necesites algo me dices.",
            "A ti por confiar en mí. ¡Siempre a la orden!",
        ],
        "consejo": "Responde breve y cálido. No hace falta explicar más.",
    },
    "normal": {
        "respuestas": [
            "Todo bien, ¿y tú? Cuéntame un poco más.",
            "Entiendo. ¿Y cómo te fue con eso?",
            "Qué bueno, sigamos hablando.",
            "Perfecto, cualquier cosa me avisas.",
        ],
        "consejo": "El mensaje no tiene carga emocional fuerte. Responde con naturalidad y con una pregunta abierta.",
    },
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
    "saludo": "👋",
    "agradecimiento": "🙏",
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

def obtener_sugerencia(intencion: str):
    """Devuelve (respuesta lista para enviar, consejo) según la intención."""
    datos = SUGERENCIAS.get(intencion, SUGERENCIAS["normal"])
    return random.choice(datos["respuestas"]), datos["consejo"]

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
        f"💬 *Puedes responder:*\n\"{datos['sugerencia']}\"\n\n"
        f"💡 *Consejo:* {datos['consejo']}"
    )

# ─── Comandos ───────────────────────────────────────────

MENSAJE_AYUDA = (
    "🤖 *Chat Analyzer Bot*\n"
    "Pégame un mensaje que te hayan enviado y te digo qué significa y cómo responderlo.\n\n"
    "*Comandos:*\n"
    "/start - Saludo e introducción\n"
    "/ayuda - Muestra esta ayuda\n"
    "/traducir <idioma> <texto> - Traduce y envía el audio de pronunciación\n\n"
    "*Ejemplo:* escribe `por qué no me respondes` y recibirás el análisis."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name or "amigo"
    await update.message.reply_text(f"👋 ¡Hola, {nombre}!\n\n" + MENSAJE_AYUDA, parse_mode="Markdown")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENSAJE_AYUDA, parse_mode="Markdown")

async def traducir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = traductor.parsear_comando(context.args)
    if datos is None:
        await update.message.reply_text(traductor.USO)
        return
    codigo, nombre, texto = datos
    espera = await update.message.reply_text("⏳ Traduciendo y generando audio...")
    try:
        # Las librerías son bloqueantes: se ejecutan en un hilo para no congelar el bot
        resultado = await asyncio.to_thread(traductor.traducir, texto, codigo)
        await espera.edit_text(traductor.formatear(texto, resultado, codigo), parse_mode="HTML")
        audio = await asyncio.to_thread(traductor.generar_audio, resultado, codigo)
        await update.message.reply_voice(audio, caption=f"🔊 Pronunciación en {nombre}")
    except Exception as e:
        print(f"❌ Error en /traducir: {e}")
        await espera.edit_text("⚠️ No pude traducir ese texto. Intenta de nuevo.")

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
        }
        datos["sugerencia"], datos["consejo"] = obtener_sugerencia(intencion)
        
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
    app.add_handler(CommandHandler("traducir", traducir))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()

if __name__ == "__main__":
    main()
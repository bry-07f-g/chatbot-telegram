import asyncio
import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters,
)

import aprendizaje
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
    "crisis": [
        "🚨 Habla de sentirse sin salida o de hacerse daño.",
        "💔 Hay un dolor muy fuerte que necesita atención.",
        "🫂 Lo más importante es que no esté solo.",
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
    "crisis": {
        "respuestas": [
            "Gracias por contármelo, me importa lo que sientes. ¿Estás a salvo en este momento?",
            "No estás solo, estoy aquí contigo. ¿Quieres que hablemos ahora?",
            "Lo que me dices es importante. ¿Hay alguien cerca que pueda acompañarte?",
            "Quiero ayudarte. ¿Buscamos juntos apoyo de alguien de confianza o de un profesional?",
        ],
        "consejo": "Responde con calma y sin juzgar. Si hay riesgo inmediato, llama al 123 o busca ayuda cercana.",
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

# SOLUCIONES: ideas concretas para resolver la situación (para TI)
SOLUCIONES = {
    "reclamo": [
        "Acordar un tiempo razonable de respuesta y cumplirlo.",
        "Avisar cuando no puedas responder, aunque sea con un mensaje corto.",
        "Fijar un momento para hablar con calma y sin interrupciones.",
    ],
    "celos": [
        "Hablar de lo que le preocupa sin acusaciones ni interrogatorios.",
        "Compartir tus planes con anticipación para generar confianza.",
        "Acordar entre los dos qué necesitan saber del otro y qué es espacio personal.",
    ],
    "agresion": [
        "Pausar la conversación al menos 30 minutos antes de responder.",
        "Retomar el tema por llamada o en persona, donde hay menos malentendidos.",
        "Si se repite, poner un límite claro sobre cómo quieres que te hablen y apoyarte en alguien de confianza.",
    ],
    "tristeza": [
        "Escuchar sin interrumpir ni dar consejos de inmediato.",
        "Ofrecer compañía concreta: una llamada, una caminata o verse.",
        "Si la tristeza dura semanas, sugerir hablar con un profesional.",
    ],
    "manipulacion": [
        "Pedirle que diga directamente lo que necesita.",
        "Tomarte un tiempo antes de decidir, sin sentirte culpable.",
        "Mantener tu decisión con amabilidad; si es constante, conversar sobre los límites.",
    ],
    "control": [
        "Conversar sobre qué le genera inseguridad.",
        "Acordar un nivel de contacto cómodo para los dos.",
        "Si hay presión constante, hablar con alguien de confianza o un orientador.",
    ],
    "ruptura": [
        "Pedir hablar en persona o por llamada, no por chat.",
        "Preguntar qué cambios concretos haría falta.",
        "Si deciden terminar, hacerlo con respeto y darse tiempo para procesarlo.",
    ],
    "desinteres": [
        "Preguntar de forma abierta si pasa algo, sin presionar.",
        "Dar unas horas de espacio y escribir de nuevo con un mensaje ligero.",
        "Proponer un plan concreto en lugar de mensajes largos.",
    ],
    "inseguridad": [
        "Responder con claridad y ejemplos concretos.",
        "Reforzar con acciones, no solo con palabras.",
        "Animarle a expresar sus dudas apenas aparezcan.",
    ],
    "afecto": [
        "Corresponder con un detalle personal.",
        "Proponer un plan para verse o hacer algo juntos.",
        "Mantener la comunicación constante y sincera.",
    ],
    "curiosidad": [
        "Responder con algo concreto de tu día.",
        "Devolver una pregunta para que la charla fluya.",
        "Si hay mucho que contar, proponer una llamada o nota de voz.",
    ],
    "saludo": [
        "Responder el saludo y hacer una pregunta corta.",
        "Si hace tiempo que no hablan, mencionar algo en común.",
        "Aprovechar para proponer un tema o un plan.",
    ],
    "agradecimiento": [
        "Responder con calidez y brevedad.",
        "Ofrecer ayuda para lo que siga.",
        "Mantener el buen ánimo de la conversación.",
    ],
    "normal": [
        "Mantener la conversación con preguntas abiertas.",
        "Compartir algo propio para que fluya.",
        "Si necesitas algo concreto, plantearlo de forma directa.",
    ],
    "crisis": [
        "Tomar en serio lo que dice y no minimizarlo.",
        "Preguntar con calma si está a salvo ahora mismo y no dejarle solo si hay peligro.",
        "Animarle a hablar con una persona de confianza o un profesional; si hay peligro inmediato, llamar al 123.",
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
    "crisis": "🚨",
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

NOMBRES_EMOCION = {"neutral": "Sin emoción clara"}


def formatear_respuesta(d: dict) -> str:
    lineas = [
        f"{d['emoji_principal']} *Análisis del mensaje que te enviaron*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"{d['emoji_emocion']} *Emoción detectada:* {d['emocion']}",
    ]
    if d["otras_emociones"]:
        lineas.append(f"   ↳ También: {d['otras_emociones']}")
    lineas += [
        f"🚩 *Toxicidad:* {d['toxicidad']} ({d['toxicidad_nivel']}%)",
        f"🧠 *Intención:* {d['intencion']}{d['origen']}",
        f"💔 *Ghosting:* {d['ghosting_bar']} {d['ghosting']}%",
        f"🔥 *Riesgo:* {d['riesgo']}",
    ]
    if d["senales"]:
        lineas.append(f"🔎 *Señales:* {d['senales']}")
    lineas += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"💡 *Qué significa:*\n{d['interpretacion']}",
        "",
        f"💬 *Puedes responder:*\n\"{d['sugerencia']}\"",
        "",
        f"🛠️ *Ideas para resolverlo:*\n{d['soluciones']}",
        "",
        f"📌 *Consejo:* {d['consejo']}",
        "",
        "¿Acerté con la intención? Tu respuesta me ayuda a aprender 👇",
    ]
    return "\n".join(lineas)

# ─── Comandos ───────────────────────────────────────────

MENSAJE_AYUDA = (
    "🤖 *Chat Analyzer Bot*\n"
    "Pégame un mensaje que te hayan enviado y te digo qué significa y cómo responderlo.\n\n"
    "*Comandos:*\n"
    "/start - Saludo e introducción\n"
    "/ayuda - Muestra esta ayuda\n"
    "/aprendizaje - Cuántos mensajes he aprendido de tus correcciones\n"
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

PENDIENTES_MAX = 500


def _guardar_pendiente(context, chat_id, msg_id, texto, intencion):
    pendientes = context.bot_data.setdefault("pendientes", {})
    pendientes[(chat_id, msg_id)] = {"texto": texto, "intencion": intencion}
    while len(pendientes) > PENDIENTES_MAX:
        pendientes.pop(next(iter(pendientes)))


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        r = analizar_texto(texto)
        intencion = r["intencion"]

        sugerencia, consejo = obtener_sugerencia(intencion)
        principal = r["emocion"]
        porcentaje = f" ({r['emocion_confianza']}%)" if r["emocion_confianza"] else ""
        otras = " · ".join(
            f"{NOMBRES_EMOCION.get(n, n.capitalize())} {p}%" for n, p in r["emociones_top"][1:]
        )
        datos = {
            "emoji_principal": EMOJIS.get(intencion, "💬"),
            "emoji_emocion": EMOJIS_EMOCION.get(principal, "😐"),
            "emocion": NOMBRES_EMOCION.get(principal, principal.capitalize()) + porcentaje,
            "otras_emociones": otras,
            "toxicidad": "🔴 Alta" if r["toxicidad"] == "si" else "🟢 Baja",
            "toxicidad_nivel": r["toxicidad_nivel"],
            "intencion": intencion.capitalize(),
            "origen": " 🧠 (aprendido de tus correcciones)" if r["origen"] == "aprendido" else "",
            "ghosting": r["ghosting"],
            "ghosting_bar": construir_barra(r["ghosting"]),
            "riesgo": r["riesgo"],
            "senales": ", ".join(r["senales"]),
            "interpretacion": obtener_texto(INTERPRETACIONES, intencion),
            "sugerencia": sugerencia,
            "consejo": consejo,
            "soluciones": "\n".join("• " + s for s in SOLUCIONES.get(intencion, SOLUCIONES["normal"])),
        }

        msg_id = update.message.message_id
        _guardar_pendiente(context, update.effective_chat.id, msg_id, texto, intencion)
        teclado = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Acertó", callback_data=f"ok|{msg_id}"),
            InlineKeyboardButton("✏️ Corregir", callback_data=f"fix|{msg_id}"),
        ]])
        await update.message.reply_text(
            formatear_respuesta(datos), parse_mode="Markdown", reply_markup=teclado
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar el mensaje.")


async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botones de retroalimentación: así el bot aprende mientras se usa."""
    q = update.callback_query
    await q.answer()
    try:
        partes = q.data.split("|")
        accion = partes[0]
        clave = (q.message.chat_id, int(partes[1]))
        pendiente = context.bot_data.get("pendientes", {}).get(clave)

        if pendiente is None:
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text("⌛ Ya no tengo ese mensaje guardado. Envíalo otra vez para corregirlo.")
            return

        if accion == "ok":
            total = aprendizaje.aprender(pendiente["texto"], pendiente["intencion"])
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"✅ ¡Gracias! Guardé este ejemplo. Ya he aprendido {total} mensajes.")

        elif accion == "fix":
            botones = [
                InlineKeyboardButton(f"{EMOJIS.get(n, '💬')} {n.capitalize()}", callback_data=f"set|{partes[1]}|{n}")
                for n in INTERPRETACIONES
            ]
            filas = [botones[i:i + 2] for i in range(0, len(botones), 2)]
            await q.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(filas))

        elif accion == "set" and partes[2] in INTERPRETACIONES:
            nueva = partes[2]
            total = aprendizaje.aprender(pendiente["texto"], nueva)
            pendiente["intencion"] = nueva
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(
                f"🧠 Aprendido. Los mensajes parecidos a ese ahora los clasifico como {nueva.capitalize()}. "
                f"Ya he aprendido {total} mensajes."
            )
    except Exception as e:
        print(f"❌ Error en botón: {e}")


async def estado_aprendizaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🧠 Mensajes aprendidos de tus correcciones: {aprendizaje.total()}")

# ─── Inicialización ─────────────────────────────────────

def main():
    print("🤖 Bot de análisis de mensajes activo...")
    print("📌 Analizo los mensajes que TE ENVÍAN y te digo cómo responder")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("traducir", traducir))
    app.add_handler(CommandHandler("aprendizaje", estado_aprendizaje))
    app.add_handler(CallbackQueryHandler(boton))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()

if __name__ == "__main__":
    main()
import asyncio
import html
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters,
)

import traductor
from analisis import NIVELES
from predict import analizar_texto
from respuestas import recomendar

# ─── Configuración ──────────────────────────────────────

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ERROR: Variable TELEGRAM_TOKEN no configurada")
    print("📌 Configuración:")
    print("   En PowerShell: $env:TELEGRAM_TOKEN='tu_token_aqui'")
    exit(1)

MAX_TELEGRAM = 4000  # el límite real de Telegram es 4096 caracteres por mensaje

# ─── Formato del análisis (HTML: todo texto dinámico se escapa) ──

esc = html.escape
EMOJI_RIESGO = {"bajo": "🟢", "moderado": "🟡", "alto": "🔴"}
EMOJI_FAMILIA = {"alegría": "😊", "afecto": "💕", "tristeza": "😢", "enojo": "😠", "miedo": "😨",
                 "asco y rechazo": "😖", "sorpresa": "😲", "compleja": "🌀"}


def _evidencias(e):
    ev = [x for x in e["evidencias"] if not x.startswith("(")]
    if ev:
        return ", ".join(f"«{esc(x)}»" for x in ev[:3])
    return "<i>lo indica el modelo de IA</i>" if e["modelo"] else ""


def _linea_emocion(e):
    emoji = EMOJI_FAMILIA.get(e["familia"], "•")
    texto = f"{emoji} <b>{esc(e['nombre'])}</b> — intensidad {e['intensidad']}/5 ({NIVELES[e['intensidad']]}), {e['certeza']}"
    ev = _evidencias(e)
    return texto + (f"\n    Evidencia: {ev}" if ev else "")


def _corto(texto, n=110):
    texto = texto.split(";")[0].strip()
    return texto if len(texto) <= n else texto[:n].rsplit(" ", 1)[0] + "…"


def elegir_respuestas(rec):
    """Muestra 2 respuestas (la principal y la más útil de las otras); el resto va en el botón «Más respuestas»."""
    todas = rec["responder"]
    if len(todas) <= 2:
        return todas, []
    segunda = next((v for v in todas[1:] if v[0].startswith("Según")), None) \
        or next((v for v in todas[1:] if v[0] in ("Firme", "Conciliadora")), todas[1])
    return [todas[0], segunda], [v for v in todas if v not in (todas[0], segunda)]


def _respuestas_html(variantes):
    return "\n".join(f"<b>{esc(e)}:</b> “{esc(t)}”" for e, t in variantes)


def formatear_compacto(a, rec, mostrar):
    """Un solo mensaje corto con lo esencial. Siempre dice algo útil, incluso si el mensaje es neutro."""
    p = a["principal"]
    if p:
        L = [f"{EMOJI_FAMILIA.get(p['familia'], '•')} <b>{esc(p['nombre'])}</b> · intensidad {p['intensidad']}/5 ({NIVELES[p['intensidad']]})"]
        otras = [e["nombre"].lower() for e in a["secundarias"][:3]]
        if otras:
            L.append("También: " + esc(", ".join(otras)))
    else:
        L = ["😐 <b>Tono neutro</b> · sin carga emocional fuerte"]

    intenciones = [n for n, _ in a["intenciones"][:2]]
    if not intenciones:
        hostil = any(k in a["comportamientos"] for k in ("Insultos", "Descalificación", "Desprecio", "Agresión verbal"))
        intenciones = ["Expresar enojo" if hostil else
                       {"saludo": "Saludo", "agradecimiento": "Agradecimiento"}.get(a["cotidiano"], "Seguir la conversación")]
    L.append("🎯 <b>Intención:</b> " + esc(" · ".join(intenciones)))

    r = a["riesgo"]
    riesgo = f"{EMOJI_RIESGO[r['nivel']]} <b>Riesgo:</b> {r['nivel'].capitalize()}"
    if r["nivel"] != "bajo" and r["indicadores"]:
        riesgo += " — " + esc(_corto(r["indicadores"][0]))
    L.append(riesgo)
    if a["comportamientos"]:
        L.append(f"🗣️ <b>Estilo:</b> {esc(a['estilo'])} ({esc(', '.join(list(a['comportamientos'])[:3]).lower())})")

    L += ["", "💡 " + esc(rec["significado"]), "", "🧭 <b>Cómo actuar</b>"]
    L += [f"• {esc(x)}" for x in rec["hacer"][:2]]
    L.append(f"⏱️ {esc(rec['cuando'])}")
    if rec["limites"]:
        L.append(f"🚧 {esc(rec['limites'])}")
    if rec["seguridad"]:
        L.append(f"🛟 {esc(_corto(rec['seguridad'], 200))}")

    L += ["", "💬 <b>Puedes responder</b>", _respuestas_html(mostrar)]
    if rec["esperar"]:
        L.append("💤 También puedes esperar o no responder.")
    L += ["", "🚫 <b>Evita:</b> " + esc(" · ".join(rec["evitar"][:2])), "", "<i>Lectura orientativa, no es un diagnóstico.</i>"]
    return "\n".join(L)


def partir(texto, limite=MAX_TELEGRAM):
    """Parte un texto largo en trozos de hasta `limite` caracteres, cortando en saltos de línea."""
    trozos, actual = [], ""
    for linea in texto.split("\n"):
        if len(actual) + len(linea) + 1 > limite and actual:
            trozos.append(actual)
            actual = ""
        actual += ("\n" if actual else "") + linea
    if actual:
        trozos.append(actual)
    return trozos


# ─── Comandos ───────────────────────────────────────────

MENSAJE_AYUDA = (
    "🤖 <b>Chat Analyzer Bot</b>\n"
    "Pégame un mensaje que te hayan enviado y analizo qué emociones expresa, qué intención parece tener, "
    "cómo se comunica y qué riesgo hay. Después te digo qué significa, cómo actuar y qué podrías responder.\n\n"
    "<b>Comandos:</b>\n"
    "/start - Saludo e introducción\n"
    "/ayuda - Muestra esta ayuda\n"
    "/traducir &lt;idioma&gt; &lt;texto&gt; - Traduce y envía el audio de pronunciación\n\n"
    "<b>Ejemplo:</b> escribe <code>Te quiero, pero ya no puedo seguir soportando lo que haces</code>."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = esc(update.effective_user.first_name or "amigo")
    await update.message.reply_text(f"👋 ¡Hola, {nombre}!\n\n" + MENSAJE_AYUDA, parse_mode=ParseMode.HTML)


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENSAJE_AYUDA, parse_mode=ParseMode.HTML)


async def traducir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = traductor.parsear_comando(context.args)
    if datos is None:
        await update.message.reply_text(traductor.USO)
        return
    codigo, nombre, texto = datos
    espera = await update.message.reply_text("⏳ Traduciendo y generando audio...")
    try:
        resultado = await asyncio.to_thread(traductor.traducir, texto, codigo)
        await espera.edit_text(traductor.formatear(texto, resultado, codigo), parse_mode="HTML")
        audio = await asyncio.to_thread(traductor.generar_audio, resultado, codigo)
        await update.message.reply_voice(audio, caption=f"🔊 Pronunciación en {nombre}")
    except Exception as e:
        print(f"❌ Error en /traducir: {e}")
        await espera.edit_text("⚠️ No pude traducir ese texto. Intenta de nuevo.")


# ─── Handler principal ──────────────────────────────────

MAS_MAX = 200


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    try:
        analisis = await asyncio.to_thread(analizar_texto, texto)
        rec = recomendar(analisis)
        mostrar, resto = elegir_respuestas(rec)
        mensaje = formatear_compacto(analisis, rec, mostrar)
        teclado = None
        if resto:
            guardadas = context.bot_data.setdefault("mas_respuestas", {})
            guardadas[(update.effective_chat.id, update.message.message_id)] = resto
            while len(guardadas) > MAS_MAX:
                guardadas.pop(next(iter(guardadas)))
            teclado = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Más respuestas", callback_data=f"mas|{update.message.message_id}")]])
        await update.message.reply_text(mensaje[:MAX_TELEGRAM], parse_mode=ParseMode.HTML, reply_markup=teclado)
    except Exception as e:
        # Aunque algo falle, siempre se responde con algo útil
        print(f"❌ Error: {e}")
        await update.message.reply_text(
            "😐 Tono neutro · sin carga emocional fuerte\n\n💬 Puedes responder: “Claro, cuéntame más, te escucho.”")


async def mas_respuestas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        clave = (q.message.chat_id, int(q.data.split("|")[1]))
        resto = context.bot_data.get("mas_respuestas", {}).get(clave)
        await q.edit_message_reply_markup(reply_markup=None)
        if resto:
            await q.message.reply_text("💬 <b>Más respuestas</b>\n" + _respuestas_html(resto), parse_mode=ParseMode.HTML)
        else:
            await q.message.reply_text("Envíame el mensaje otra vez y te doy más respuestas.")
    except Exception as e:
        print(f"❌ Error en botón: {e}")


# ─── Inicialización ─────────────────────────────────────

def main():
    print("🤖 Bot de análisis emocional activo...")
    print("📌 Analizo los mensajes que TE ENVÍAN y te digo cómo actuar y responder")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("traducir", traducir))
    app.add_handler(CallbackQueryHandler(mas_respuestas, pattern="^mas"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()


if __name__ == "__main__":
    main()

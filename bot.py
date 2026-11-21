import asyncio
import html
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

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


def formatear_analisis(a):
    L = ["🔎 <b>ANÁLISIS DEL MENSAJE</b>", "━━━━━━━━━━━━━━━━━━━━", "", "<b>1. EMOCIONES DETECTADAS</b>"]
    if a["principal"]:
        L.append("<u>Principal</u>")
        L.append(_linea_emocion(a["principal"]))
        if a["secundarias"]:
            L.append("<u>Secundarias</u>")
            L += [_linea_emocion(e) for e in a["secundarias"]]
    else:
        L.append("No se detectan emociones con claridad en este mensaje.")
    for n in a["notas"]:
        L.append(f"⚠️ <i>{esc(n)}</i>")

    L += ["", "<b>2. ESTADO EMOCIONAL</b>"]
    if a["principal"]:
        nombres = [e["nombre"].lower() for e in a["emociones"][:4]]
        L.append("Posible estado: " + esc(", ".join(nombres)) + ".")
    else:
        L.append("No hay información suficiente para describirlo.")
    L.append("Sentimientos acumulados: " + (
        "sí, hay señales (" + ", ".join(f"«{esc(x)}»" for x in a["acumulado"][:2]) + ")." if a["acumulado"]
        else "no se observan señales claras."))
    L.append("Emociones simultáneas o contradicciones: " + (esc(" ".join(a["simultaneas"])) if a["simultaneas"] else "no se observan."))

    L += ["", "<b>3. INTENCIÓN COMUNICATIVA</b>"]
    if a["intenciones"]:
        L += [f"• <b>{esc(n)}</b> — {esc(j)}" for n, j in a["intenciones"][:4]]
    else:
        L.append("No se identifica una intención clara con la información disponible.")

    L += ["", "<b>4. COMPORTAMIENTO COMUNICATIVO</b>", f"Estilo: <b>{esc(a['estilo'])}</b>"]
    if a["comportamientos"]:
        for nombre, d in a["comportamientos"].items():
            ev = ", ".join(f"«{esc(x)}»" if not x.startswith("(") else esc(x) for x in d["evidencias"])
            L.append(f"• {esc(nombre)}: {ev}" + (f"\n    <i>{esc(d['nota'])}</i>" if d["nota"] else ""))
    else:
        L.append("No se observan insultos, amenazas, culpabilización ni presión emocional.")

    r = a["riesgo"]
    L += ["", "<b>5. NIVEL DE RIESGO</b>", f"{EMOJI_RIESGO[r['nivel']]} <b>{r['nivel'].capitalize()}</b>"]
    L += [f"• {esc(i)}" for i in r["indicadores"]]
    L.append(f"<i>Incertidumbre: {esc(r['incertidumbre'])}</i>")
    return "\n".join(L)


def formatear_recomendaciones(rec):
    L = ["🧭 <b>6. ¿QUÉ SIGNIFICA?</b>", esc(rec["significado"]), "", "<b>7. ¿CÓMO DEBES ACTUAR?</b>"]
    L += [f"• {esc(x)}" for x in rec["hacer"]]
    L.append(f"⏱️ <b>Cuándo responder:</b> {esc(rec['cuando'])}")
    if rec["limites"]:
        L.append(f"🚧 <b>Límites:</b> {esc(rec['limites'])}")
    if rec["espacio"]:
        L.append(f"🌿 <b>Dar espacio:</b> {esc(rec['espacio'])}")
    if rec["seguridad"]:
        L.append(f"🛟 <b>Seguridad:</b> {esc(rec['seguridad'])}")

    L += ["", "<b>8. ¿QUÉ PUEDES RESPONDER?</b>"]
    for etiqueta, texto in rec["responder"]:
        L.append(f"💬 <b>{esc(etiqueta)}:</b>\n“{esc(texto)}”")
    if rec["esperar"]:
        L.append(f"💤 {esc(rec['esperar'])}")

    L += ["", "<b>9. ¿QUÉ DEBES EVITAR?</b>"]
    L += [f"• {esc(x)}" for x in rec["evitar"]]
    L += ["", "ℹ️ <i>Análisis orientativo basado solo en el texto del mensaje. No es un diagnóstico ni una medición clínica.</i>"]
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

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        analisis = await asyncio.to_thread(analizar_texto, texto)
        rec = recomendar(analisis)
        for bloque in (formatear_analisis(analisis), formatear_recomendaciones(rec)):
            for trozo in partir(bloque):
                await update.message.reply_text(trozo, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar el mensaje.")


# ─── Inicialización ─────────────────────────────────────

def main():
    print("🤖 Bot de análisis emocional activo...")
    print("📌 Analizo los mensajes que TE ENVÍAN y te digo cómo actuar y responder")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("traducir", traducir))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()


if __name__ == "__main__":
    main()

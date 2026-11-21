# redactor.py - Redacta las respuestas sugeridas combinando lo que dijo la persona con el análisis
#
# En vez de una frase fija por emoción, cada respuesta se arma con piezas:
#   reconocer lo que siente (citando sus propias palabras cuando se puede) + validar + una pregunta o
#   un paso concreto según la intención. Cada pieza tiene varias formas de decirse y se elige una al azar,
#   así el bot no repite siempre las mismas frases.
import random

from analisis import normalizar


def citar(texto, frase):
    """Devuelve la frase tal como la escribió la persona (con sus mayúsculas), entre « »."""
    n_texto, n_frase = normalizar(texto), normalizar(frase)
    if len(n_texto) == len(texto):
        i = n_texto.find(n_frase)
        if i >= 0:
            return "«" + texto[i:i + len(n_frase)].strip(" .,;") + "»"
    return "«" + frase + "»"


def _cita_principal(a):
    p = a["principal"]
    if not p:
        return None
    for ev in p["evidencias"]:
        if not ev.startswith("(") and len(ev.split()) >= 2:
            return citar(a["texto"], ev)
    return None


# ─── Piezas para reconocer lo que siente ──────────────

ABRE = {
    "tristeza": ["Siento que estés pasando por esto.", "Gracias por contarme cómo te sientes.", "Debe ser duro sentirte así.",
                 "Me importa lo que te está pasando."],
    "enojo": ["Veo que esto te molestó bastante.", "Entiendo que estés molesto.", "Noto que esto te afectó mucho.",
              "Gracias por decirme lo que te molesta."],
    "miedo": ["Entiendo que esto te preocupe.", "Es normal sentir inquietud con algo así.", "Se nota que esto te tiene inquieto."],
    "alegría": ["¡Qué bueno leer eso!", "Me alegra mucho saberlo.", "Qué gusto que estés así."],
    "afecto": ["Gracias por decírmelo.", "Qué lindo mensaje.", "Me alegra leer eso."],
    "asco y rechazo": ["Veo que lo ocurrido te generó mucho rechazo.", "Entiendo que eso te pareciera inaceptable."],
    "sorpresa": ["Parece que esto te tomó por sorpresa.", "Vaya, se nota que no lo esperabas."],
    "compleja": ["Se nota que estás sintiendo muchas cosas a la vez.", "Gracias por ser tan sincero conmigo."],
}
ABRE_CITA_NEGATIVA = {
    "enojo": ["Cuando dices {c}, se nota que esto te ha molestado bastante.", "Leí {c} y entiendo que estés molesto.",
              "{c}: se nota que esto viene afectándote."],
    "tristeza": ["Cuando escribes {c}, entiendo que lo estás pasando mal.", "Leí {c} y no quiero pasarlo por alto.",
                 "{c}: se nota que esto te pesa."],
    "miedo": ["Cuando dices {c}, entiendo que esto te preocupe.", "Leí {c} y se nota la inquietud."],
    "asco y rechazo": ["Cuando dices {c}, veo que esto te generó mucho rechazo."],
    "compleja": ["Cuando escribes {c}, se nota que estás cargando con mucho.", "Leí {c} y no quiero pasarlo por alto."],
}
ABRE_CITA_POSITIVA = ["Me encantó leer {c}.", "{c}: qué bueno escucharlo."]
FAMILIAS_NEGATIVAS = ("tristeza", "enojo", "miedo", "asco y rechazo", "compleja")

IRONIA = ("Me dio la impresión de que había algo de ironía en el mensaje; si te molestó algo, prefiero que me lo digas "
          "directamente.")

# ─── Preguntas o pasos siguientes por emoción ─────────

PREGUNTAS = {
    "Felicidad": ["¿Qué fue lo que más te hizo feliz?", "Cuéntame cómo pasó."],
    "Entusiasmo": ["¿Qué es lo que más esperas de ese día?", "Ojalá salga incluso mejor de lo que esperas."],
    "Orgullo": ["Te lo mereces, has trabajado para eso. ¿Qué fue lo más difícil de conseguirlo?",
                "Es bueno que reconozcas tu propio esfuerzo."],
    "Alivio": ["Me alegra que por fin puedas respirar tranquilo.", "¿Qué fue lo que más te preocupaba?"],
    "Afecto": ["¿Cómo estás tú?", "Yo también te aprecio."],
    "Pena": ["No tienes que fingir que estás bien. Si quieres hablar, te escucho.", "¿Quieres contarme qué pasó?"],
    "Soledad": ["¿Quieres contarme qué te hace sentir tan solo?", "¿Te gustaría que hablemos un rato o que nos veamos?"],
    "Desilusión": ["¿Qué fue lo que más te decepcionó?", "Me gustaría entender qué esperabas que pasara."],
    "Desesperanza": ["No quiero minimizar lo que sientes. ¿Estás a salvo ahora mismo? ¿Has pensado en hacerte daño o en no seguir viviendo?"],
    "Irritación": ["¿Podemos hablar de lo que ocurrió para entendernos mejor?", "¿Qué fue lo que más te molestó?"],
    "Frustración": ["¿Quieres que pensemos en una alternativa o prefieres desahogarte primero?",
                    "¿Qué ha sido lo más difícil de intentar solucionarlo?"],
    "Rabia": ["Prefiero que hablemos cuando los dos podamos hacerlo sin lastimarnos.", "Te escucho, pero sin gritos ni insultos."],
    "Indignación": ["¿Qué parte de la situación te afectó más?", "Tiene sentido que lo veas como injusto."],
    "Resentimiento": ["Siento que esto viene de hace tiempo. ¿Qué es lo que más te ha afectado?",
                      "No quiero quedarme solo con lo de hoy; ¿qué más se ha ido acumulando?"],
    "Ansiedad anticipatoria": ["¿Qué es exactamente lo que más miedo te da de esa situación?", "Separemos lo que ya pasó de lo que tememos que pase."],
    "Inseguridad": ["Tener dudas no significa que no seas suficiente. ¿Qué pasó para que empezaras a sentirte así?"],
    "Temor al abandono": ["Me gustaría hablar de lo que está generando esa inseguridad.", "¿Qué te hace sentir que nos estamos alejando?"],
    "Vergüenza": ["Todos cometemos errores o pasamos situaciones incómodas, y eso no define quién eres."],
    "Miedo": ["¿Qué es lo que más te inquieta en este momento?", "No tienes que enfrentarlo solo."],
    "Asco y rechazo": ["¿Qué fue lo que te pareció inaceptable?", "Respeto lo que sientes; cuéntame qué fue lo que más te chocó."],
    "Sorpresa": ["¿Fue una sorpresa agradable o te tomó desprevenido de forma desagradable?"],
    "Nostalgia": ["¿Qué es lo que más extrañas de ese momento?"],
    "Culpa": ["Reconocerlo es importante. Podemos pensar cómo repararlo sin que te castigues."],
    "Remordimiento": ["Sentirlo dice que te importa. ¿Hay algo que podamos hacer para repararlo?"],
    "Celos": ["Cuéntame qué fue lo que te preocupó y lo hablamos con calma."],
    "Envidia": ["¿Qué es lo que a ti te gustaría lograr?"],
    "Amargura": ["¿Qué ha sido lo más difícil de todo esto?"],
    "Desesperación": ["No quiero minimizarlo. ¿Estás a salvo ahora mismo? ¿Has pensado en hacerte daño?"],
    "Agotamiento emocional": ["No tienes que resolverlo todo hoy. ¿Quieres hablar o prefieres descansar primero?"],
    "Impotencia": ["¿Qué parte de la situación es la que más te pesa?"],
    "Vacío emocional": ["¿Desde cuándo lo sientes así?"],
    "Confusión emocional": ["No tienes que tenerlo claro ahora. ¿Quieres que lo ordenemos juntos?"],
}
PREGUNTA_FAMILIA = {
    "tristeza": ["¿Quieres contarme más?"], "enojo": ["¿Qué fue lo que más te molestó?"], "miedo": ["¿Qué es lo que más te inquieta?"],
    "alegría": ["Cuéntame más."], "afecto": ["¿Cómo estás tú?"], "asco y rechazo": ["¿Qué te pareció inaceptable?"],
    "sorpresa": ["¿Qué fue lo que pasó exactamente?"], "compleja": ["¿Qué es lo que más necesitas ahora?"],
}

# Mensajes con cariño y malestar a la vez (ambivalencia)
AMBIVALENCIA = [
    "Gracias por decírmelo con sinceridad. Sé que me quieres y que aun así esto te está desgastando. Me gustaría entender "
    "qué es lo que más te pesa y qué podemos cambiar.",
    "Puedo ver que hay cariño y también cansancio. Las dos cosas pueden ser ciertas. ¿Qué es lo que más necesitas que cambie?",
    "Te agradezco que lo digas con honestidad, sin dejar de decir que me quieres. No quiero ponerme a la defensiva; cuéntame "
    "qué es lo que más te ha afectado.",
]

# ─── Según la intención (a veces citando) ─────────────

POR_INTENCION = {
    "Desahogo": ["Te leo. No tienes que resolverlo ahora mismo; sigo aquí.", "Puedes desahogarte todo lo que necesites, te escucho sin interrumpir.",
                 "Gracias por sacarlo. No hace falta que busquemos una solución hoy."],
    "Búsqueda de apoyo": ["Gracias por confiarme cómo te sientes. ¿Quieres contarme qué está pasando?", "Cuenta conmigo. ¿Prefieres hablar ahora o más tarde?"],
    "Búsqueda de soluciones": ["Podemos analizar lo que está pasando y pensar en algunas alternativas. ¿Por dónde quieres empezar?",
                               "Vamos paso a paso: cuéntame qué has intentado y qué fue lo que no funcionó."],
    "Reclamo": ["Cuando dices {c}, entiendo que algo te ha molestado. Quiero escucharte sin ponerme a la defensiva: ¿qué situación concreta fue la que más te afectó?",
                "Tomo en serio lo que dices. ¿Me ayudas con un ejemplo de lo que te molestó para entenderlo bien?",
                "Entiendo que tengas una inconformidad. Me gustaría saber qué comportamiento te ha afectado."],
    "Establecimiento de límites": ["Entiendo lo que me dices y lo voy a tener en cuenta. ¿Qué necesitas que cambie?",
                                   "Es válido que pongas ese límite. Dime cómo podemos hacerlo para que los dos estemos cómodos."],
    "Reconciliación": ["Valoro que quieras arreglarlo. Podemos hablar con calma cuando los dos estemos listos.",
                       "Si ambos nos escuchamos y reconocemos nuestros errores, podemos intentar resolverlo."],
    "Búsqueda de validación": ["Lo que sientes merece ser escuchado. Podemos revisar juntos qué pasó para entenderlo mejor.",
                               "No creo que debas minimizar lo que sientes. Cuéntame más para entender la situación."],
    "Provocación": ["No quiero convertir esto en una discusión. Si tienes algo que resolver, hablémoslo con respeto.",
                    "Prefiero no seguir por este camino. Si quieres hablar de verdad, aquí estoy."],
    "Manipulación emocional": ["Quiero ayudarte, pero no desde la presión. Dime directamente qué necesitas y lo hablamos.",
                               "El cariño no debería usarse para obligar a nadie. Podemos hablar de lo que necesitas sin condiciones."],
    "Posible distanciamiento": ["Entiendo que necesites distancia. Si quieres, hablamos con calma cuando estés listo. ¿Cuánto tiempo necesitas?",
                                "Respeto que quieras tomarte un tiempo. ¿Prefieres que te escriba o esperar a que tú lo hagas?"],
}

# ─── Tonos por familia ────────────────────────────────

NEUTRAL = {
    "tristeza": ["Te leo. Si quieres contarme más, aquí estoy.", "Aquí estoy por si quieres hablar.", "Gracias por contármelo."],
    "enojo": ["Entiendo que estás molesto. Podemos hablar cuando estemos más tranquilos.", "Leí tu mensaje. Hablemos con calma cuando puedas.",
              "Veo que estás molesto; retomamos cuando baje la tensión."],
    "miedo": ["Entiendo la preocupación. ¿Qué es lo que más te inquieta?", "Miremos qué hechos tenemos antes de suponer lo peor."],
    "alegría": ["Qué bueno saberlo. Cuéntame más.", "Me alegra leerlo."],
    "afecto": ["Gracias por decírmelo.", "Te leo, gracias por escribirme."],
    "asco y rechazo": ["Entiendo que eso te generó rechazo.", "Veo que no estás de acuerdo con lo que pasó."],
    "sorpresa": ["¿Qué pasó exactamente?", "Cuéntame con calma qué fue lo que pasó."],
    "compleja": ["Te entiendo; no es fácil sentir tantas cosas a la vez.", "Gracias por contármelo. Vamos con calma."],
}
FIRME = {
    "tristeza": ["Quiero apoyarte; ayúdame a entender qué necesitas ahora mismo.", "Me importa cómo estás. Dime qué te serviría en este momento."],
    "enojo": ["Quiero escucharte, pero necesito que hablemos con calma y concretando qué pasó.",
              "Estoy dispuesto a hablarlo, pero no a que se convierta en una pelea."],
    "miedo": ["Antes de suponer lo peor, miremos qué hechos tenemos.", "Entiendo el miedo, pero decidamos con datos y no con suposiciones."],
    "alegría": ["Me alegra, y me gustaría que sigamos compartiendo cosas así."],
    "afecto": ["Esto también me importa; hablemos de lo que cada uno necesita."],
    "asco y rechazo": ["Respeto tus límites; dime qué es lo que no quieres que se repita."],
    "sorpresa": ["Necesito más contexto para entender cómo te sientes con eso."],
    "compleja": ["Quiero ayudarte, pero necesito que me digas qué es lo que más necesitas ahora."],
}
FIRME_HOSTIL = [
    "Quiero hablar de esto, pero no con insultos. Cuando estés más tranquilo, seguimos.",
    "No voy a seguir la conversación si me hablas así. Hablamos cuando podamos hacerlo con respeto.",
    "Prefiero parar aquí para no decir algo de lo que me arrepienta. Retomamos más tarde.",
]
EMPATICA_HOSTIL = [
    "Veo que estás muy molesto, y quiero entender por qué. Pero prefiero que lo hablemos sin insultos.",
    "Noto que algo te hirió mucho. Cuéntame qué pasó, pero sin agredirnos.",
]
NEUTRAL_HOSTIL = [
    "Veo que estás muy molesto. Voy a esperar a que se calme la conversación.",
    "Leí tu mensaje. Hablemos cuando los dos estemos más tranquilos.",
]
CONCILIADORA = {
    "tristeza": ["Estoy contigo. Vamos paso a paso, sin presión.", "No tienes que explicarlo todo hoy; acompáñame un rato y lo vamos viendo."],
    "enojo": ["Quiero entender qué pasó para que no se repita. ¿Podemos hablarlo con calma?",
              "Quiero que lo arreglemos. ¿Hablamos esta noche, cuando los dos estemos más tranquilos?"],
    "miedo": ["Estoy contigo. Vamos a mirar esto juntos con calma."],
    "alegría": ["Me alegra de verdad. Gracias por compartirlo conmigo."],
    "afecto": ["Qué lindo leerte. Yo también quiero cuidar esto."],
    "asco y rechazo": ["Quiero entender qué te pareció inaceptable."],
    "sorpresa": ["Cuéntame con calma, aquí te escucho."],
    "compleja": ["Podemos ir despacio y ordenar esto juntos."],
}

# ─── Respuestas de seguridad (con cita) ───────────────

PREGUNTA_SEGURIDAD = [
    "Veo que estás pasando por un momento muy difícil y que llevas tiempo cargando con esto. No quiero discutir ni minimizar lo que "
    "sientes. Pero antes quiero preguntarte algo importante: cuando dices {c}, ¿te refieres a terminar esta situación o has pensado "
    "en hacerte daño?",
    "Me preocupa cómo te sientes. Cuando escribes {c}, quiero asegurarme de que estás bien: ¿hablas de poner fin a lo que está pasando "
    "o has pensado en hacerte daño?",
]
SEGURIDAD_EXPLICITA = [
    "Gracias por decírmelo, me importa lo que sientes y quiero tomarlo en serio. Cuando dices {c}, necesito preguntarte: ¿estás a salvo "
    "ahora mismo? ¿Estás pensando en quitarte la vida? Estoy aquí contigo.",
    "Lo que escribes ({c}) es importante y no quiero dejarlo pasar. ¿Estás a salvo en este momento? Si piensas en hacerte daño, "
    "dímelo con confianza; no estás solo.",
]


def frase_riesgo(a):
    frases = a["riesgo"].get("frases") or []
    return citar(a["texto"], frases[0]) if frases else "«eso»"


def componer(a, rng=None):
    """Devuelve una lista de (etiqueta, texto) con respuestas adaptadas al análisis."""
    rng = rng or random
    p = a["principal"]
    comp = a["comportamientos"]
    hostil = any(k in comp for k in ("Insultos", "Descalificación", "Desprecio", "Agresión verbal"))
    intents = [n for n, _ in a["intenciones"]]
    fam = p["familia"] if p else ("enojo" if hostil else "compleja")
    nombre = p["nombre"] if p else ""
    cita = _cita_principal(a)
    salida = []

    # Empática
    if hostil:
        texto = rng.choice(EMPATICA_HOSTIL)
    elif any(e["nombre"] == "Ambivalencia" for e in a["emociones"]):
        texto = rng.choice(AMBIVALENCIA)
    elif p:
        if cita and fam in FAMILIAS_NEGATIVAS and rng.random() < 0.6:
            abre = rng.choice(ABRE_CITA_NEGATIVA[fam]).format(c=cita)
        elif cita and fam in ("alegría", "afecto") and rng.random() < 0.6:
            abre = rng.choice(ABRE_CITA_POSITIVA).format(c=cita)
        else:
            abre = rng.choice(ABRE[fam])
        texto = abre + " " + rng.choice(PREGUNTAS.get(nombre, PREGUNTA_FAMILIA[fam]))
    else:
        texto = None
    if texto:
        if a["sarcasmo"]:
            texto += " " + IRONIA
        salida.append(("Empática", texto))

    # Según la intención
    for n in intents:
        if n in POR_INTENCION and n != "Amenaza":
            t = rng.choice(POR_INTENCION[n])
            if "{c}" in t:
                t = t.format(c=cita) if cita else rng.choice([x for x in POR_INTENCION[n] if "{c}" not in x])
            salida.append((f"Según su intención ({n.lower()})", t))
            break

    # Neutral, firme y conciliadora
    salida.append(("Neutral", rng.choice(NEUTRAL_HOSTIL if hostil else NEUTRAL[fam])))
    salida.append(("Firme", rng.choice(FIRME_HOSTIL if hostil else FIRME[fam])))
    if not hostil:
        salida.append(("Conciliadora", rng.choice(CONCILIADORA[fam])))

    # Sin repetir el mismo texto
    vistos, unicas = set(), []
    for etiqueta, t in salida:
        if t not in vistos:
            vistos.add(t)
            unicas.append((etiqueta, t))
    return unicas[:5]

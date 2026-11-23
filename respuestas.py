# respuestas.py - Recomendaciones: qué significa, cómo actuar, qué responder y qué evitar
#
# Las respuestas sugeridas son plantillas escritas a mano (no las inventa un modelo), elegidas
# según la emoción principal, la intención, el comportamiento y el riesgo del análisis.
import random

import redactor
from analisis import NIVELES

# ─── Respuesta empática por emoción ───────────────────

EMPATICA = {
    "Felicidad": "Me alegra mucho que estés pasando por un momento así. ¿Qué fue lo que más te hizo feliz?",
    "Entusiasmo": "Se nota que tienes muchas ganas de hacerlo. Ojalá salga incluso mejor de lo que esperas.",
    "Orgullo": "Te lo mereces. Has trabajado para conseguirlo y es bueno que puedas reconocer tu propio esfuerzo.",
    "Alivio": "Me imagino lo difícil que debió ser. Me alegra que finalmente puedas respirar tranquilo.",
    "Afecto": "Gracias por decírmelo, significa mucho para mí. Yo también te aprecio.",
    "Pena": "Siento que estés pasando por esto. No tienes que fingir que estás bien. Si quieres hablar, puedo escucharte.",
    "Soledad": "Debe ser muy difícil sentirte así. ¿Quieres contarme qué te está haciendo sentir tan solo?",
    "Desilusión": "Entiendo que esperabas algo diferente. Me gustaría comprender qué fue lo que más te decepcionó.",
    "Desesperanza": "Parece que estás atravesando algo realmente difícil. No quiero minimizar lo que sientes. "
                    "¿Estás a salvo ahora mismo? ¿Has pensado en hacerte daño o en no seguir viviendo?",
    "Irritación": "Veo que esto te está molestando. ¿Podemos hablar de lo que ocurrió para entendernos mejor?",
    "Frustración": "Entiendo que estés frustrado, especialmente si sientes que llevas mucho tiempo intentando solucionar "
                   "lo mismo. ¿Quieres que pensemos en alguna alternativa?",
    "Rabia": "Entiendo que estés muy molesto. Prefiero que hablemos cuando podamos hacerlo sin lastimarnos.",
    "Indignación": "Entiendo por qué consideras que lo sucedido fue injusto. ¿Qué parte de la situación te afectó más?",
    "Resentimiento": "Parece que esto no viene solamente de lo que pasó hoy. Siento que llevas tiempo acumulando "
                     "molestias. ¿Qué es lo que más te ha afectado?",
    "Ansiedad anticipatoria": "Entiendo que te preocupe lo que pueda pasar. ¿Qué es exactamente lo que más miedo te da de esa situación?",
    "Inseguridad": "Es normal tener dudas en determinadas situaciones, pero eso no significa que no seas suficiente. "
                   "¿Qué ocurrió para que empezaras a sentirte así?",
    "Temor al abandono": "Entiendo que te preocupe perder esta relación. Creo que sería bueno hablar de lo que está "
                         "generando esa inseguridad.",
    "Vergüenza": "Todos podemos cometer errores o pasar por situaciones incómodas. Eso no define quién eres.",
    "Miedo": "Entiendo que tengas miedo. ¿Qué es lo que más te inquieta en este momento?",
    "Asco y rechazo": "Veo que lo sucedido te generó un rechazo muy fuerte. ¿Quieres explicar qué fue lo que consideraste inaceptable?",
    "Sorpresa": "Vaya, parece que no esperabas que sucediera algo así. ¿Fue una sorpresa positiva o te tomó desprevenido "
                "de una manera desagradable?",
    "Nostalgia": "Se nota que esos recuerdos te importan. ¿Qué es lo que más extrañas de ese momento?",
    "Culpa": "Se nota que te preocupa lo que pasó. Reconocerlo es importante, y podemos pensar cómo repararlo sin que te castigues.",
    "Remordimiento": "Parece que esto te pesa mucho. Sentirlo dice que te importa; ¿hay algo que podamos hacer para repararlo?",
    "Celos": "Entiendo que algo te generó inseguridad. Prefiero que lo hablemos con calma; cuéntame qué fue lo que te preocupó.",
    "Envidia": "A veces ver lo que otros consiguen duele. ¿Qué es lo que a ti te gustaría lograr?",
    "Amargura": "Parece que has acumulado muchas malas experiencias. ¿Quieres contarme qué ha sido lo más difícil?",
    "Desesperación": "Parece que estás al límite y no quiero minimizarlo. ¿Estás a salvo ahora mismo? ¿Has pensado en hacerte daño?",
    "Agotamiento emocional": "Se nota que llevas mucho tiempo cargando con esto. No tienes que resolverlo todo hoy; ¿quieres hablar o "
                             "prefieres descansar un poco primero?",
    "Impotencia": "Debe ser frustrante sentir que no puedes cambiar esto. ¿Qué parte de la situación es la que más te pesa?",
    "Vacío emocional": "Gracias por contarme cómo te sientes, eso que describes es importante. ¿Desde cuándo lo sientes así?",
    "Confusión emocional": "Es normal sentirse confundido. No tienes que tenerlo claro ahora; ¿quieres que lo vayamos ordenando juntos?",
    "Ambivalencia": "Puedes querer a alguien y aun así estar agotado por lo que pasa; las dos cosas pueden ser ciertas. "
                    "¿Qué es lo que más necesitas ahora?",
}

# ─── Guía por familia emocional ───────────────────────

FAMILIA = {
    "alegría": {
        "hacer": ["Reconocer el sentimiento positivo.", "Mostrar interés por lo sucedido.", "Compartir el entusiasmo sin exagerar."],
        "evitar": ["Minimizar sus logros.", "Cambiar de tema hacia tus propios asuntos.", "Responder con indiferencia."],
        "neutral": "Qué bueno saberlo. Cuéntame más.",
        "firme": "Me alegra, y me gustaría que sigamos compartiendo cosas así.",
        "conciliadora": "Me alegra de verdad. Gracias por compartirlo conmigo.",
    },
    "afecto": {
        "hacer": ["Responder con sinceridad.", "Un detalle personal vale más que una frase larga."],
        "evitar": ["Responder con frialdad sin explicar por qué.", "Burlarte del mensaje."],
        "neutral": "Gracias por decírmelo.",
        "firme": "Esto también me importa; hablemos de lo que cada uno necesita.",
        "conciliadora": "Qué lindo leerte. Yo también quiero cuidar esto.",
    },
    "tristeza": {
        "hacer": ["Escuchar sin interrumpir.", "Validar lo que siente.", "Ofrecer acompañamiento concreto (una llamada, verse)."],
        "evitar": ["Minimizar con frases como «no es para tanto».", "Dar soluciones de inmediato.", "Frases vacías como «todo pasa por algo»."],
        "neutral": "Te leo. Si quieres contarme más, aquí estoy.",
        "firme": "Quiero apoyarte; ayúdame a entender qué necesitas ahora mismo.",
        "conciliadora": "Estoy contigo. Vamos paso a paso, sin presión.",
    },
    "enojo": {
        "hacer": ["Mantener la calma y un tono tranquilo.", "Reconocer la molestia antes de explicarte.", "Preguntar qué la provocó."],
        "evitar": ["Responder con provocaciones o en caliente.", "Ponerte a la defensiva de inmediato.", "Seguir discutiendo por chat si sube la tensión."],
        "neutral": "Entiendo que estás molesto. Podemos hablar cuando estemos más tranquilos.",
        "firme": "Quiero escucharte, pero no voy a seguir la conversación si hay insultos o gritos.",
        "conciliadora": "Quiero entender qué pasó para que no se repita. ¿Podemos hablarlo con calma?",
    },
    "miedo": {
        "hacer": ["Transmitir tranquilidad sin invalidar la preocupación.", "Separar hechos de suposiciones.", "Ayudar a ver qué sí puede controlar."],
        "evitar": ["Alimentar escenarios catastróficos.", "Burlarte de sus dudas.", "Decir «no es nada» sin escucharle."],
        "neutral": "Entiendo la preocupación. ¿Qué es lo que más te inquieta?",
        "firme": "Antes de suponer lo peor, miremos qué hechos tenemos.",
        "conciliadora": "Estoy contigo. Vamos a mirar esto juntos con calma.",
    },
    "asco y rechazo": {
        "hacer": ["No confundir rechazo con odio o agresividad.", "Identificar el comportamiento que lo causó.", "Respetar sus límites."],
        "evitar": ["Justificar insultos o humillaciones.", "Insistir en que no debería sentirse así."],
        "neutral": "Entiendo que eso te generó rechazo.",
        "firme": "Respeto tus límites; dime qué es lo que no quieres que se repita.",
        "conciliadora": "Quiero entender qué te pareció inaceptable.",
    },
    "sorpresa": {
        "hacer": ["Averiguar si la sorpresa fue agradable o desagradable.", "No asumir alegría ni enojo.", "Pedir contexto."],
        "evitar": ["Suponer cómo se siente.", "Reaccionar con burla."],
        "neutral": "¿Qué pasó exactamente?",
        "firme": "Necesito más contexto para entender cómo te sientes con eso.",
        "conciliadora": "Cuéntame con calma, aquí te escucho.",
    },
    "compleja": {
        "hacer": ["Reconocer que puede sentir varias cosas a la vez.", "No exigirle que lo tenga claro.", "Preguntar qué necesita ahora."],
        "evitar": ["Decirle qué debería sentir.", "Reducir todo a una sola emoción."],
        "neutral": "Te entiendo; no es fácil sentir tantas cosas a la vez.",
        "firme": "Quiero ayudarte, pero necesito que me digas qué es lo que más necesitas ahora.",
        "conciliadora": "Podemos ir despacio y ordenar esto juntos.",
    },
}

# Ajustes más específicos que la familia
ESPECIFICO = {
    "Frustración": {"hacer": ["Reconocer el esfuerzo.", "Identificar el obstáculo concreto.", "Preguntar si quiere desahogarse o buscar alternativas."],
                    "evitar": ["Ofrecer soluciones precipitadas."]},
    "Rabia": {"hacer": ["No entrar en discusiones impulsivas.", "Dar espacio cuando haga falta.", "Poner límites ante insultos o amenazas."]},
    "Resentimiento": {"hacer": ["Reconocer que puede haber dolor acumulado.", "No centrarse solo en el último conflicto.", "Identificar situaciones anteriores relacionadas."],
                      "evitar": ["Forzar una reconciliación."]},
    "Vergüenza": {"hacer": ["No juzgar ni ridiculizar.", "Transmitir comprensión.", "Diferenciar cometer un error de ser mala persona."],
                  "evitar": ["Exponerle innecesariamente."]},
    "Culpa": {"hacer": ["Diferenciar responsabilidad de autocastigo.", "Ayudar a reconocer el error.", "Promover reparación cuando corresponda."]},
    "Desesperanza": {"hacer": ["Escuchar con especial atención.", "Preguntar por su seguridad si hay señales preocupantes.", "Recomendar apoyo humano y profesional."],
                     "evitar": ["Frases vacías como «todo pasa por algo»."]},
    "Inseguridad": {"hacer": ["Reconocer sus capacidades.", "Ayudar a diferenciar hechos de interpretaciones."],
                    "evitar": ["Burlarte de sus dudas.", "Reforzar comparaciones negativas."]},
    "Temor al abandono": {"hacer": ["Hablar de lo que genera la inseguridad.", "Ser claro sobre lo que sí está pasando."]},
    "Soledad": {"hacer": ["Mostrar disponibilidad.", "Preguntar si necesita compañía."],
                "evitar": ["Asumir que estar acompañado elimina la soledad."]},
    "Desesperación": {"hacer": ["Reconocer que existe un malestar acumulado.", "No invalidar lo que siente ni intentar solucionarlo todo de inmediato.", "No responder con insultos ni a la defensiva."],
                      "evitar": ["Minimizar con frases como «todo pasa» o «no es para tanto».", "Pedir explicaciones o discutir en este momento."]},
    "Agotamiento emocional": {"hacer": ["Reconocer que lleva tiempo cargando con esto.", "No intentar solucionarlo todo de inmediato.", "Ofrecer escucha o descanso, según lo que prefiera."],
                              "evitar": ["Exigirle que lo resuelva ya.", "Minimizar lo que siente."]},
    "Desilusión": {"hacer": ["Reconocer la expectativa incumplida.", "No ponerte a la defensiva.", "Identificar qué fue lo que decepcionó."]},
}

# ─── Respuesta según la intención (documento, sección 5) ──

POR_INTENCION = {
    "Desahogo": "Puedes expresarte. No tienes que resolverlo todo ahora mismo. Estoy dispuesto a escucharte.",
    "Búsqueda de apoyo": "Gracias por confiarme cómo te sientes. ¿Quieres contarme qué está pasando?",
    "Búsqueda de soluciones": "Podemos analizar lo que está pasando y pensar en algunas alternativas.",
    "Reclamo": "Entiendo que tengas una inconformidad. Me gustaría saber qué comportamiento te ha afectado.",
    "Establecimiento de límites": "Es válido establecer límites. Puedes expresar lo que no estás dispuesto a aceptar sin necesidad de entrar en una discusión.",
    "Reconciliación": "Si ambos estamos dispuestos a escucharnos y reconocer nuestros errores, podemos intentar resolverlo.",
    "Búsqueda de validación": "Lo que sientes merece ser escuchado. Podemos analizar la situación para entender qué ocurrió.",
    "Provocación": "No quiero convertir esto en una discusión. Si tienes algo que resolver, podemos hablarlo con respeto.",
    "Amenaza": "No voy a continuar una conversación con amenazas. Si existe un peligro inmediato, lo prioritario es mantener la seguridad y buscar ayuda.",
    "Manipulación emocional": "El cariño no debería utilizarse para obligar a alguien a hacer algo. Podemos hablar de lo que necesitas sin imponer condiciones.",
    "Posible distanciamiento": "Entiendo que necesites distancia. Si quieres, hablamos con calma cuando estés listo. ¿Cuánto tiempo necesitas?",
}

EVITAR_INTENCION = {
    "Desahogo": "Dar soluciones o consejos antes de escuchar.",
    "Reclamo": "Defenderte de inmediato o contraatacar con otro reclamo.",
    "Establecimiento de límites": "Tomar el límite como un ataque o intentar negociarlo en caliente.",
    "Búsqueda de validación": "Burlarte o decir «estás exagerando».",
    "Provocación": "Caer en la provocación o responder con sarcasmo.",
    "Amenaza": "Provocar, desafiar o escalar el conflicto.",
    "Manipulación emocional": "Ceder solo por culpa o presión, y tampoco manipular de vuelta.",
    "Posible distanciamiento": "Asumir que quiere terminar la relación; pregúntaselo antes.",
    "Búsqueda de soluciones": "Dar una solución sin entender primero el problema completo.",
}

HOSTILES = ("Insultos", "Descalificación", "Desprecio", "Agresión verbal")


def _lista(items):
    return ", ".join(items)


def _significado(a):
    """Explicación corta (1-3 frases). Siempre dice algo útil, incluso si el mensaje es neutro."""
    comp = a["comportamientos"]
    if a["cotidiano"] == "saludo":
        return "Es un saludo amable; solo busca iniciar o retomar la conversación."
    if a["cotidiano"] == "agradecimiento":
        return "Es un agradecimiento; transmite buena disposición y no hay conflicto."
    p = a["principal"]
    if not p:
        if "Evasión" in comp:
            return ("Respuesta breve: puede ser acuerdo, cansancio o necesidad de espacio. "
                    "No le des más peso del que tiene.")
        return "Mensaje de tono neutro, sin carga emocional fuerte. Lo más probable es que solo busque seguir la conversación."
    ev = [x for x in p["evidencias"] if not x.startswith("(")]
    txt = f"Parece expresar {p['nombre'].lower()} ({NIVELES[p['intensidad']]})"
    if ev:
        txt += f" por «{ev[0]}»"
    txt += "."
    if a["acumulado"]:
        txt += " Hay señales de malestar acumulado."
    if a["simultaneas"]:
        txt += " " + a["simultaneas"][0]
    elif a["secundarias"]:
        txt += " También aparece " + a["secundarias"][0]["nombre"].lower() + "."
    if a["intenciones"]:
        txt += " Parece buscar: " + a["intenciones"][0][0].lower() + "."
    return txt


def recomendar(a):
    f = a["riesgo"]["flags"]
    comp = a["comportamientos"]
    intents = [n for n, _ in a["intenciones"]]
    p = a["principal"]
    hostil = [k for k in HOSTILES if k in comp]
    fam = p["familia"] if p else None

    rec = {"significado": _significado(a), "hacer": [], "cuando": "", "limites": None, "espacio": None,
           "seguridad": None, "responder": [], "esperar": None, "evitar": []}

    # 1) Seguridad primero ───────────────────────────
    if f["autolesion"]:
        rec["hacer"] = ["Tomarlo con total seriedad y no minimizarlo.",
                        "Preguntar directamente si está a salvo ahora mismo y si piensa en hacerse daño.",
                        "No dejarle solo si hay peligro; acompañarle o avisar a alguien de confianza cerca de él o ella.",
                        "Recomendar ayuda inmediata: servicios de emergencia (123 en Colombia) o un profesional."]
        rec["cuando"] = "Ahora, sin esperar: la seguridad va primero."
        rec["seguridad"] = "Sí, es la prioridad. Si hay riesgo inmediato, llama al 123 o a los servicios de emergencia de tu zona."
        rec["responder"] = [("Directa y cercana", random.choice(redactor.SEGURIDAD_EXPLICITA).format(c=redactor.frase_riesgo(a))),
                            ("Si hay peligro inmediato",
                             "Me preocupa tu seguridad. Por favor llama al 123 o dile a alguien que esté cerca de ti ahora mismo. "
                             "Yo me quedo contigo mientras tanto.")]
        rec["evitar"] = ["Tratarlo como una simple estrategia de manipulación.", "Frases vacías como «todo pasa por algo».",
                         "Prometer guardar el secreto si hay riesgo.", "Dejar la conversación sin comprobar que está a salvo."]
        return rec

    if f["violencia"] or f["violencia_sufrida"]:
        if f["violencia_sufrida"] and not f["amenaza"] and not f["dano_otros"]:
            rec["hacer"] = ["Creerle y no minimizar lo que cuenta.", "Preguntar si está a salvo ahora mismo.",
                            "Animarle a buscar ayuda: servicios de emergencia (123 en Colombia) y personas de confianza."]
            rec["cuando"] = "Pronto; no esperes si piensas que está en peligro."
            rec["seguridad"] = "Sí. Si hay peligro inmediato, llama al 123."
            rec["responder"] = [("Cercana y directa", "Gracias por contármelo, te creo y no estás solo. ¿Estás a salvo ahora mismo? "
                                                       "Si hay peligro, llama al 123; puedo ayudarte a pensar con quién hablar.")]
            rec["evitar"] = ["Culparle por lo que le pasa.", "Presionarle a decidir algo de inmediato.",
                             "Confrontar tú mismo al agresor sin pensar en la seguridad."]
        else:
            rec["hacer"] = ["No provocar ni escalar el conflicto.", "Poner tu seguridad primero.",
                            "Guardar el mensaje como evidencia.", "Pedir ayuda si hay peligro (123 en Colombia) o a alguien de confianza."]
            rec["cuando"] = "No tienes que responder de inmediato. Primero asegúrate de estar a salvo."
            rec["limites"] = "Sí: puedes decir con claridad que no continuarás una conversación con amenazas."
            rec["espacio"] = "Sí: tomar distancia es válido y recomendable."
            rec["seguridad"] = "Sí. Si sientes que hay peligro real, llama al 123 y avisa a alguien de confianza."
            rec["responder"] = [("Firme y breve", POR_INTENCION["Amenaza"])]
            rec["esperar"] = "No continuar la conversación o no responder también es una opción válida."
            rec["evitar"] = ["Provocar, desafiar o responder con otra amenaza.", "Ir a confrontarle en persona.",
                             "Ignorar el mensaje si sientes miedo real."]
        return rec

    # 2) Mensajes sin información suficiente o cotidianos ───
    if a["cotidiano"]:
        rec["hacer"] = ["Responder con naturalidad y una pregunta corta."]
        rec["cuando"] = "Cuando puedas, sin prisa."
        rec["responder"] = [("Natural", "¡Hola! ¿Cómo estás?" if a["cotidiano"] == "saludo" else "¡De nada! Con gusto.")]
        rec["evitar"] = ["Buscarle un significado oculto: es un mensaje cotidiano."]
        return rec

    if not p and not intents and not hostil:
        pregunta = "?" in a["texto"]
        rec["hacer"] = (["Responder directamente a lo que pregunta, con calma."] if pregunta else
                        ["Responder con naturalidad, sin darle más peso del necesario."]) + \
                       ["Si te queda la duda, pregunta con calma qué quiso decir."]
        rec["cuando"] = "Cuando puedas; no hay urgencia."
        rec["responder"] = [("Natural", random.choice(["Claro, cuéntame más.", "Entiendo. ¿Y tú cómo vas?", "Aquí estoy, dime."])),
                            ("Para aclarar", random.choice(["¿Todo bien? Cuéntame si quieres.", "¿Quieres que hablemos de eso con calma?"]))]
        rec["evitar"] = ["Interpretarlo como indiferencia sin contexto.", "Atribuirle intenciones que el texto no muestra."]
        return rec

    # 3) Caso general ────────────────────────────────
    if p is None:  # hay intención o comportamiento, pero ninguna emoción clara
        fam = "enojo" if hostil or set(intents) & {"Reclamo", "Provocación", "Amenaza", "Establecimiento de límites"} else "compleja"
        p = {"nombre": "", "familia": fam, "intensidad": 3, "evidencias": [], "certeza": "posible"}
    guia = FAMILIA[fam]
    esp = ESPECIFICO.get(p["nombre"], {})
    rec["hacer"] = list(esp.get("hacer", guia["hacer"]))
    if f["ambiguo"]:
        rec["hacer"].insert(0, "Comprobar con una pregunta directa si está a salvo.")
    evitar = list(esp.get("evitar", [])) + [x for x in guia["evitar"] if x not in esp.get("evitar", [])]

    # Cuándo responder
    if f["ambiguo"]:
        rec["cuando"] = "Pronto, y con una pregunta directa sobre su seguridad."
    elif hostil or "Provocación" in intents or (fam == "enojo" and p["intensidad"] >= 4):
        rec["cuando"] = "No tienes que responder enseguida: espera a que baje la tensión (por ejemplo, 30 minutos o más)."
    elif fam == "tristeza" or "Búsqueda de apoyo" in intents:
        rec["cuando"] = "Cuanto antes, sin presionar."
    elif fam in ("alegría", "afecto"):
        rec["cuando"] = "Cuando quieras; es un buen momento para compartirlo."
    else:
        rec["cuando"] = "Cuando puedas y sin prisa; responde con calma."

    # Límites (el límite del otro no es agresión: regla 9)
    if hostil or "Provocación" in intents or "Manipulación emocional" in intents or "Amenaza" in intents:
        rec["limites"] = "Sí. Un límite claro y tranquilo, por ejemplo: «Quiero hablarlo, pero no con insultos»."
    elif "Establecimiento de límites" in intents:
        rec["limites"] = "El mensaje marca un límite: respetarlo no significa que te esté atacando."

    # Espacio
    if hostil or (fam == "enojo" and p["intensidad"] >= 4) or "Posible distanciamiento" in intents:
        rec["espacio"] = "Sí: dar espacio ayuda a bajar la tensión. Puedes avisar que retomarán la conversación más tarde."

    # Seguridad
    if f["ambiguo"]:
        rec["seguridad"] = ("Sí. Frases como estas merecen una pregunta directa («¿estás a salvo? ¿has pensado en hacerte daño?»), "
                            "aunque por sí solas no demuestran esa intención. Si dice que sí, busca ayuda (123 en Colombia).")

    # Respuestas redactadas con lo que dijo la persona (ver redactor.py)
    variantes = redactor.componer(a)
    if f["ambiguo"]:
        pregunta = random.choice(redactor.PREGUNTA_SEGURIDAD).format(c=redactor.frase_riesgo(a))
        variantes = [("Con pregunta de seguridad", pregunta)] + [v for v in variantes if v[0] not in ("Empática", "Firme")]
    rec["responder"] = variantes[:5]
    if hostil or "Provocación" in intents or (fam == "enojo" and p["intensidad"] >= 4):
        rec["esperar"] = "No siempre hace falta responder: esperar, tomar distancia o no seguir la discusión también es una buena opción."

    # Evitar
    if hostil:
        evitar.insert(0, "Responder con insultos o amenazas.")
    if "Manipulación emocional" in intents or "Chantaje emocional" in comp:
        evitar.append("Ceder solo por culpa o presión, y tampoco manipular de vuelta.")
    if a["sarcasmo"]:
        evitar.append("Tomar al pie de la letra una frase que puede ser sarcástica sin preguntar.")
    for n in intents:
        if n in EVITAR_INTENCION and EVITAR_INTENCION[n] not in evitar:
            evitar.append(EVITAR_INTENCION[n])
    evitar.append("Atribuirle intenciones que el texto no muestra.")
    rec["evitar"] = evitar[:6]
    return rec

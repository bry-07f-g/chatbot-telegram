# 🤖 Chat Analyzer Bot

**Chat Analyzer Bot** es un bot de Telegram que utiliza Inteligencia Artificial y Procesamiento de Lenguaje Natural (NLP) para analizar mensajes de texto en español. El bot detecta emociones (principales y secundarias, con intensidad), intención comunicativa, comportamiento y nivel de riesgo, y **explica qué significa el mensaje, cómo actuar y qué responder**.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Ejemplos de Mensajes](#-ejemplos-de-mensajes)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Posibles Mejoras](#-posibles-mejoras)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 🎭 **Emociones múltiples** | Más de 30 emociones y estados (alegría, tristeza, enojo, miedo, asco, sorpresa y complejas como culpa, celos, agotamiento o ambivalencia), con intensidad 1-5 y evidencias |
| 🧠 **Intención comunicativa** | Desahogo, apoyo, soluciones, reclamo, límites, reconciliación, validación, provocación, amenaza, manipulación |
| 🗣️ **Comportamiento** | Insultos, descalificación, culpabilización, chantaje emocional, pasivo-agresividad, evasión y más |
| 🛟 **Riesgo cualitativo** | Bajo, moderado o alto, con indicadores; prioriza la seguridad ante autolesión o violencia |
| 💬 **Respuestas sugeridas** | Empática, neutral, firme y conciliadora, más qué hacer y qué evitar |
| 🌐 **Traductor** | `/traducir <idioma> <texto>` con audio de pronunciación |

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Lenguaje principal |
| **pysentimiento** | 0.7.3 | NLP para español (emociones y hate speech) |
| **Transformers** | 4.6.1+ | Modelos BERT para análisis de texto |
| **PyTorch** | 2.0+ | Deep learning |
| **python-telegram-bot** | 20.7 | Framework del bot |

---



## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/bry-07f-g/chatbot-telegram.git
cd chatbot-telegram
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```txt
python-telegram-bot>=22.0
pysentimiento>=0.7.3
transformers>=4.6.1
torch>=2.0.0
deep-translator
gTTS
```

---

## ⚙️ Configuración

### 1. Crear un bot en Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía el comando: `/newbot`
3. Elige un nombre para tu bot (ej: `Chat Analyzer Bot`)
4. Elige un username (ej: `chat_analyzer_bot`)
5. **Guarda el token** que te entregue BotFather

### 2. Configurar variable de entorno

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_TOKEN="tu_token_aqui"
```

**Windows (CMD):**
```cmd
set TELEGRAM_TOKEN=tu_token_aqui
```

**Linux/Mac:**
```bash
export TELEGRAM_TOKEN="tu_token_aqui"
```

### 3. Ejecutar el bot

```bash
python bot.py
```

Verás algo como:
```
🔄 Cargando modelos de pysentimiento...
✅ Modelos cargados correctamente
🤖 Bot de análisis de mensajes activo...
📝 Token configurado: ✅ Sí
🟢 Bot corriendo... Esperando mensajes
```

---

## 🎯 Uso

1. Abre Telegram y busca tu bot por su username
2. Envía cualquier mensaje de texto al bot
3. El bot te responderá con un análisis completo del mensaje
4. **El análisis incluye sugerencias de cómo responder**

### Comandos

| Comando | Qué hace |
|---------|----------|
| `/start` | Saludo e introducción |
| `/ayuda` | Lista de comandos |
| `/traducir <idioma> <texto>` | Traduce el texto y envía un audio con la pronunciación. Ej: `/traducir japonés hola como estas` |

---

## 📝 Ejemplos de Mensajes

| Mensaje que te envían | Qué detecta |
|-----------------------|-------------|
| `Te quiero, pero ya no puedo seguir soportando lo que haces` | Afecto + agotamiento + frustración, con ambivalencia |
| `Hoy fue el límite, no aguanto un segundo más` | Desesperación muy alta, intención de límites, riesgo moderado y pregunta directa de seguridad |
| `Siempre haces lo mismo y nunca reconoces tus errores` | Reclamo con generalizaciones, riesgo bajo |
| `Si realmente me quisieras, harías lo que te pido` | Posible manipulación emocional (con cautela) |
| `Si vuelves a hacerlo, voy a hacerte daño` | Amenaza, riesgo alto, recomienda no provocar y buscar ayuda |
| `ok` | Sin información suficiente; no se asume indiferencia |

---

## 🧠 Cómo analiza los mensajes

El bot sigue un modelo de análisis emocional y de comunicación y responde con **un solo mensaje corto**: emoción principal (con intensidad y emociones secundarias), intención, riesgo, qué significa, cómo actuar, qué responder y qué evitar. El botón **💬 Más respuestas** muestra las demás opciones (empática, neutral, firme y conciliadora). Si el mensaje no tiene carga emocional, lo lee como tono neutro y sugiere igualmente cómo responder. El análisis completo tiene estas partes:

1. **Emociones detectadas**: principal y secundarias, con intensidad de 1 a 5 y la evidencia (frases del texto) que las respalda.
2. **Estado emocional**: malestar acumulado y emociones simultáneas (por ejemplo, cariño y agotamiento a la vez).
3. **Intención comunicativa**: desahogo, apoyo, soluciones, reclamo, límites, reconciliación, validación, provocación, amenaza, manipulación emocional.
4. **Comportamiento comunicativo**: estilo (asertivo, agresivo, pasivo-agresivo, mixto) y señales como insultos, culpabilización o chantaje emocional.
5. **Nivel de riesgo**: bajo, moderado o alto, con indicadores y su incertidumbre. No usa porcentajes porque no hay un modelo validado que los respalde.
6. **¿Qué significa?**
7. **¿Cómo debes actuar?**: qué hacer, cuándo responder, límites, espacio y seguridad.
8. **¿Qué puedes responder?**: respuestas empática, neutral, firme y conciliadora.
9. **¿Qué debes evitar?**

**Reglas para no equivocarse:** una palabra suelta no basta (se marca como "posible"); las MAYÚSCULAS no equivalen a enojo; se tienen en cuenta negaciones, sarcasmo y humor; una respuesta corta ("ok") no se interpreta como indiferencia; el límite de otra persona no se confunde con agresión; un mensaje sin carga emocional se trata como tono neutro y siempre recibe una respuesta sugerida.

**Seguridad:** ante referencias a hacerse daño, amenazas de violencia o violencia sufrida, el riesgo es alto, el bot prioriza la seguridad, sugiere preguntar directamente si la persona está a salvo y recomienda ayuda (123 en Colombia). Una amenaza de autolesión nunca se trata como simple manipulación.

**Capas técnicas:** modelos de IA de `pysentimiento` (emoción y agresividad) que corroboran el análisis, más un léxico en español (con normalización de tildes y letras repetidas) y reglas de contexto en `analisis.py`. Las respuestas sugeridas se arman en `respuestas.py` y `redactor.py` con piezas escritas a mano: citan las palabras de la persona, combinan emoción e intención y tienen varias formas de decir lo mismo para no repetirse.

> El análisis es orientativo, basado solo en el texto. No es un diagnóstico psicológico.

---

## 📁 Estructura del Proyecto

```
chatbot-telegram/
│
├── bot.py                 # Código principal del bot de Telegram
├── predict.py             # Carga los modelos de IA y lanza el análisis
├── analisis.py            # Emociones, intención, comportamiento y riesgo
├── respuestas.py          # Qué significa, cómo actuar y qué evitar
├── redactor.py            # Redacta las respuestas sugeridas según el análisis
├── traductor.py           # Comando /traducir
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Documentación
```

---

## 🔮 Posibles Mejoras

- [ ] **Modelo personalizado**: Entrenar con dataset propio para mayor precisión
- [ ] **Soporte multimedia**: Análisis de imágenes, audios y documentos
- [ ] **Dashboard web**: Visualización de métricas y estadísticas
- [ ] **API REST**: Exponer funcionalidades como servicio web
- [ ] **Base de datos**: Almacenamiento anonimizado para análisis longitudinal
- [ ] **Dockerización**: Contenedor para despliegue en la nube
- [ ] **Soporte multi-idioma**: Ampliar a inglés, portugués, etc.
- [ ] **Historial de conversaciones**: Analizar evolución de emociones en el tiempo

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu rama de features (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 📧 Contacto

- **Autor**: Bryan Franco Gomez
- **Email**: francobryan524@gmail.com
- **GitHub**: [github.com/bry-07f-g](https://github.com/bry-07f-g)

---

## ⚠️ Notas de Seguridad

- **Nunca** compartas tu token de Telegram públicamente
- **No subas** el token a repositorios públicos
- Usa siempre variables de entorno para información sensible
- Si tu token se expone, revócalo inmediatamente con [@BotFather](https://t.me/BotFather)

---

## 🙏 Agradecimientos

- [pysentimiento](https://github.com/pysentimiento/pysentimiento) - Librería de NLP para español
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Framework del bot
- [Hugging Face](https://huggingface.co/) - Modelos preentrenados

---

## 📊 Estado del Proyecto

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-green)

---

**¡Disfruta analizando y mejorando tus conversaciones! 🚀**

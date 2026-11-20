# aprendizaje.py - Memoria que aprende de las correcciones del usuario mientras el bot corre
#
# Cada vez que el usuario confirma o corrige la intención de un mensaje, se guarda el par
# (texto, intención) en aprendizaje.json. Al analizar un mensaje nuevo, si se parece lo
# suficiente a uno aprendido (similitud de coseno sobre n-gramas de caracteres con TF-IDF),
# se usa la intención aprendida en vez de las reglas. Se guarda en disco, así que el bot
# conserva lo aprendido aunque se reinicie.
import json
import os
import re
import threading
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ARCHIVO = os.getenv(
    "APRENDIZAJE_ARCHIVO",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "aprendizaje.json"),
)
UMBRAL = 0.6          # similitud mínima para fiarse de un ejemplo aprendido
MAX_EJEMPLOS = 2000   # tope para que el archivo no crezca sin control


def _clave(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"(.)\1{2,}", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


class Memoria:
    def __init__(self, archivo: str = ARCHIVO):
        self.archivo = archivo
        self.ejemplos = []   # [{"texto": ..., "intencion": ...}]
        self._lock = threading.Lock()
        self._vec = None
        self._matriz = None
        self._cargar()
        self._reentrenar()

    def _cargar(self):
        try:
            with open(self.archivo, encoding="utf-8") as f:
                datos = json.load(f)
            self.ejemplos = [e for e in datos if "texto" in e and "intencion" in e]
        except (FileNotFoundError, json.JSONDecodeError):
            self.ejemplos = []

    def _guardar(self):
        tmp = self.archivo + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.ejemplos, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.archivo)

    def _reentrenar(self):
        claves = [_clave(e["texto"]) for e in self.ejemplos]
        if not claves or not any(claves):
            self._vec = self._matriz = None
            return
        self._vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self._matriz = self._vec.fit_transform(claves)

    def total(self) -> int:
        return len(self.ejemplos)

    def aprender(self, texto: str, intencion: str) -> int:
        """Guarda (o actualiza) un ejemplo y reentrena. Devuelve cuántos ejemplos hay."""
        clave = _clave(texto)
        if not clave:
            return self.total()
        with self._lock:
            for e in self.ejemplos:
                if _clave(e["texto"]) == clave:
                    e["intencion"] = intencion
                    break
            else:
                self.ejemplos.append({"texto": texto, "intencion": intencion})
                if len(self.ejemplos) > MAX_EJEMPLOS:
                    self.ejemplos.pop(0)
            self._guardar()
            self._reentrenar()
            return self.total()

    def predecir(self, texto: str, umbral: float = UMBRAL):
        """Devuelve (intencion, similitud) del ejemplo más parecido, o None."""
        if self._vec is None:
            return None
        clave = _clave(texto)
        if not clave:
            return None
        sims = cosine_similarity(self._vec.transform([clave]), self._matriz)[0]
        mejor = int(sims.argmax())
        if sims[mejor] >= umbral:
            return self.ejemplos[mejor]["intencion"], float(sims[mejor])
        return None


memoria = Memoria()


def predecir(texto, umbral=UMBRAL):
    return memoria.predecir(texto, umbral)


def aprender(texto, intencion):
    return memoria.aprender(texto, intencion)


def total():
    return memoria.total()

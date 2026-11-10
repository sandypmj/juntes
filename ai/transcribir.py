"""Transcripción de audio, en este orden:

1. faster-whisper en esta computadora, si está instalado: el audio no sale del equipo.
2. Google Gemini, si hay GEMINI_API_KEY: el audio se envía a Google. Es lo que usa la
   versión publicada, por eso el demo público trabaja solo con datos sintéticos.
3. Si no hay ninguno, la persona pega el texto del relato.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Literal

import streamlit as st

from ai.estructurar import MODELO_GEMINI, obtener_clave
from ai.estructurar import _cliente_gemini as cliente_gemini

MODELO_WHISPER = "base"

Metodo = Literal["whisper", "gemini", "manual"]
NOMBRES_METODO: dict[str, str] = {
    "whisper": "Whisper, en esta computadora (el audio no sale del equipo)",
    "gemini": "Google Gemini (el audio se envía a Google)",
    "manual": "texto pegado a mano",
}
TIPOS_AUDIO = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".m4a": "audio/aac",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
}
INSTRUCCION_GEMINI = (
    "Transcribe este audio en español, palabra por palabra. Devuelve solo la transcripción, "
    "sin comentarios, títulos ni marcas de tiempo. Si no se entiende nada, devuelve un texto vacío."
)


def whisper_disponible() -> bool:
    return importlib.util.find_spec("faster_whisper") is not None


def metodo_disponible() -> Metodo:
    if whisper_disponible():
        return "whisper"
    if obtener_clave("GEMINI_API_KEY"):
        return "gemini"
    return "manual"


@lru_cache(maxsize=1)
def _modelo():
    from faster_whisper import WhisperModel

    return WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8")


def transcribir_whisper(audio: bytes, extension: str = ".wav", idioma: str = "es") -> str:
    """Transcribe en local; el archivo temporal se borra al terminar."""
    descriptor, ruta = tempfile.mkstemp(suffix=extension)
    try:
        with os.fdopen(descriptor, "wb") as archivo:
            archivo.write(audio)
        segmentos, _ = _modelo().transcribe(ruta, language=idioma)
        return " ".join(s.text.strip() for s in segmentos).strip()
    finally:
        os.remove(ruta)


@st.cache_data(ttl=24 * 60 * 60, max_entries=200, show_spinner=False)
def transcribir_gemini(audio: bytes, extension: str = ".wav") -> str:
    """Envía el audio a Gemini. En caché: el mismo audio no vuelve a gastar cuota."""
    from google.genai import types

    tipo = TIPOS_AUDIO.get(extension.lower(), "audio/wav")
    cliente = cliente_gemini()  # se guarda en una variable: si no, Python lo cierra antes de usarlo
    respuesta = cliente.models.generate_content(
        model=MODELO_GEMINI,
        contents=[types.Part.from_bytes(data=audio, mime_type=tipo), INSTRUCCION_GEMINI],
    )
    return (respuesta.text or "").strip()


def transcribir(audio: bytes, nombre: str = "grabacion.wav") -> tuple[str, Metodo]:
    """Devuelve (texto, método usado). Lanza RuntimeError con un mensaje legible si no puede."""
    extension = Path(nombre).suffix or ".wav"
    fallo_whisper = False
    if whisper_disponible():
        try:
            return transcribir_whisper(audio, extension), "whisper"
        except Exception:  # modelo sin descargar o audio que Whisper no lee: se intenta con Gemini
            fallo_whisper = True
    if obtener_clave("GEMINI_API_KEY"):
        try:
            return transcribir_gemini(audio, extension), "gemini"
        except Exception as error:
            limite = "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error)
            motivo = "Gemini alcanzó su límite de uso por ahora." if limite else "Gemini no pudo transcribir el audio."
            raise RuntimeError(motivo) from error
    if fallo_whisper:
        raise RuntimeError("Whisper no pudo transcribir este audio.")
    raise RuntimeError("No hay un método de transcripción disponible.")

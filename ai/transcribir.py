"""Transcripción local de audio con faster-whisper, si está instalado.

El audio se procesa en esta computadora y el archivo temporal se borra al terminar.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
from functools import lru_cache

MODELO_WHISPER = "small"


def disponible() -> bool:
    return importlib.util.find_spec("faster_whisper") is not None


@lru_cache(maxsize=1)
def _modelo():
    from faster_whisper import WhisperModel

    return WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8")


def transcribir(audio: bytes, extension: str = ".wav", idioma: str = "es") -> str:
    """Devuelve el texto del audio. Lanza RuntimeError si faster-whisper no está instalado."""
    if not disponible():
        raise RuntimeError("faster-whisper no está instalado.")

    descriptor, ruta = tempfile.mkstemp(suffix=extension)
    try:
        with os.fdopen(descriptor, "wb") as archivo:
            archivo.write(audio)
        segmentos, _ = _modelo().transcribe(ruta, language=idioma)
        return " ".join(s.text.strip() for s in segmentos).strip()
    finally:
        os.remove(ruta)

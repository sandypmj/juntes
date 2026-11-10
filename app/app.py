"""Juntes nos cuidamos y construimos: asistente de rutas, voces y observatorio."""

from __future__ import annotations

import csv
import hashlib
import html
import os
import sys
import uuid
from datetime import date
from pathlib import Path

import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai import transcribir as transcripcion  # noqa: E402
from ai.estructurar import (  # noqa: E402
    ETIQUETAS_NECESIDAD,
    NOMBRES_MODO,
    ConsultaEstructurada,
    Resultado,
    estructurar_consulta,
    estructurar_relato,
    normalizar,
    proveedor_activo,
)

DATA = Path(os.environ.get("JUNTES_DATA_DIR", ROOT / "data"))
RUTA_RECURSOS = DATA / "recursos.csv"

# Los CSV de data/ solo traen ejemplos sintéticos. Lo real va a data/privado/, ignorado por Git.
DATOS_PRIVADOS = DATA / "privado"
EJEMPLO_BARRERAS = DATA / "barreras.csv"
EJEMPLO_RELATOS = DATA / "relatos.csv"
RUTA_BARRERAS = DATOS_PRIVADOS / "barreras.csv"
RUTA_RELATOS = DATOS_PRIVADOS / "relatos.csv"

COLUMNAS_BARRERAS = ["fecha_mes", "distrito", "ambito", "dimension", "tipo_necesidad", "motivo", "origen", "busqueda_id"]
COLUMNAS_RELATOS = [
    "id", "fecha_mes", "distrito", "texto", "lugares", "ambito", "capa",
    "emociones", "memoria", "lat", "lon", "ubicacion", "origen",
]

NOMBRE_APP = "Juntes nos cuidamos y construimos"
AVISO_DEMO = (
    "Esta es una versión de demostración con datos sintéticos. No escribas datos personales "
    "ni relatos reales de violencia. Si estás en riesgo, llama a la Línea 100 o al 105."
)
DISTRITOS = ["Villa El Salvador", "Ventanilla"]
CENTROS = {"Villa El Salvador": (-12.2130, -76.9350), "Ventanilla": (-11.8770, -77.1300)}
VISTA_MAPA = {
    "Todos": ((-12.045, -77.030), 10),
    "Villa El Salvador": ((-12.2130, -76.9350), 13),
    "Ventanilla": ((-11.8700, -77.1350), 12),
}
# Recuadro aproximado de cada distrito (sur-oeste, nor-este), para que el mapa lo muestre completo.
LIMITES_DISTRITO = {
    "Villa El Salvador": ((-12.245, -76.965), (-12.185, -76.905)),
    "Ventanilla": ((-11.905, -77.160), (-11.835, -77.100)),
}
ZOOM_MAXIMO = 14

DIMENSIONES = {
    "economica": ("Económica", "¿Puede pagar el servicio y llegar hasta él?"),
    "fisica": ("Física", "¿Puede ingresar y desplazarse en el espacio?"),
    "comunicacional": ("Comunicacional", "¿Puede comprender y utilizar la información?"),
    "institucional": ("Institucional", "¿Conoce los requisitos y puede completar el procedimiento?"),
    "seguridad": ("Seguridad y no discriminación", "¿Puede acceder sin exponerse a violencia o trato discriminatorio?"),
    "territorial": ("Disponibilidad territorial", "¿Hay una alternativa razonablemente próxima y operativa?"),
    "cultural": ("Pertinencia cultural", "¿La atención considera idioma, contexto y particularidades culturales?"),
}
ETIQUETAS_DIMENSION = {k: v[0] for k, v in DIMENSIONES.items()}
# Nombre corto para el semáforo; el nombre completo y la pregunta van en el texto de ayuda.
NOMBRE_CORTO = {
    "economica": "Económica",
    "fisica": "Física",
    "comunicacional": "Comunicación",
    "institucional": "Trámites",
    "seguridad": "Seguridad",
    "territorial": "Cercanía",
    "cultural": "Cultura",
}
# Cada estado lleva símbolo además de color, para quien no distingue colores.
SEMAFORO = {
    "si": ("✓", "Sí", "circulo-si"),
    "parcial": ("½", "Parcial", "circulo-parcial"),
    "no": ("✕", "No", "circulo-no"),
    "por_verificar": ("?", "Por verificar", "circulo-verificar"),
}
PESOS = {"si": 2.0, "parcial": 1.0, "por_verificar": 0.5, "no": 0.0}

ETIQUETAS_AMBITO = {
    "derechos_proteccion": "Derechos y protección",
    "movilidad_seguridad": "Movilidad y seguridad",
    "accesibilidad_inclusion": "Accesibilidad e inclusión",
    "cultura_recreacion": "Cultura, educación y recreación",
    "redes_cuidados": "Redes comunitarias y cuidados",
    "memoria": "Memoria y representación",
    "sin_clasificar": "Sin clasificar",
}
COLOR_AMBITO = {
    "derechos_proteccion": "#7B3FA0",
    "movilidad_seguridad": "#2F6DB5",
    "accesibilidad_inclusion": "#0E9AA7",
    "cultura_recreacion": "#2E8B57",
    "redes_cuidados": "#D1603D",
    "memoria": "#8A5A12",
}
ICONOS_AMBITO = {
    "derechos_proteccion": "🛡️",
    "movilidad_seguridad": "🚌",
    "accesibilidad_inclusion": "♿",
    "cultura_recreacion": "🎭",
    "redes_cuidados": "🤝",
    "memoria": "🕯️",
}
# Fondos suaves para las tarjetas: el texto oscuro del tema (#3B2A20) mantiene contraste alto.
FONDO_AMBITO = {
    "derechos_proteccion": "#F4EDF8",
    "movilidad_seguridad": "#EBF2FA",
    "accesibilidad_inclusion": "#E7F6F7",
    "cultura_recreacion": "#EAF6EE",
    "redes_cuidados": "#FCEEE8",
    "memoria": "#F7EFE2",
}
CAPAS = {
    "miedo": ("Miedo", "#7B3FA0"),
    "seguridad": ("Seguridad", "#C2185B"),
    "cuidado": ("Cuidado", "#D1603D"),
    "cultura": ("Cultura", "#2F6DB5"),
    "memoria": ("Memoria", "#8A5A12"),
    "verde": ("Verde", "#2E8B57"),
    "accesibilidad": ("Accesibilidad", "#0E9AA7"),
}
ETIQUETAS_MOTIVO = {
    "sin_recurso": "No hay un recurso registrado",
    "condicion_no_cumplida": "El recurso no cumple la condición",
    "dato_por_verificar": "La condición no está confirmada",
    "no_clasificada": "Consulta no clasificada",
}
MOTIVOS_SIN_ALTERNATIVA = {"sin_recurso", "condicion_no_cumplida", "no_clasificada"}
TIPOS_COMUNITARIOS = {"organizacion_mujeres", "olla_comun", "comedor_adulto_mayor", "organizacion_adultos_mayores"}
TIPOS_PERSONAS_MAYORES = {"adulto_mayor", "comedor_adulto_mayor", "organizacion_adultos_mayores"}
# Recursos con sede en Lima que atienden a personas de cualquier distrito de Lima y Callao.
ALCANCE_LIMA = "Lima"
SIN_DATO = {"", "por verificar", "dato sintetico", "no aplica (atencion telefonica)"}
TERMINOS_ESPERA = ["lista de espera", "listas de espera", "en espera", "sin cupos", "cupos limitados"]
EJEMPLOS_BUSQUEDA = [
    ("🎨", "Taller de arte para mi hijo"),
    ("🤝", "Cuidado para mi mamá adulta mayor"),
    ("🚌", "Paradero seguro de noche"),
    ("⚖️", "Orientación legal gratuita"),
]
CAPAS_SEGURIDAD = {"miedo", "seguridad"}
SERENAZGO = {
    "Villa El Salvador": "Serenazgo de Villa El Salvador: (01) 510-0200",
    "Ventanilla": "Central de emergencias Alerta Ventanilla: (01) 904-0388",
}

# Qué recursos responden a cada tipo de necesidad: por tipo de recurso o por texto.
# "movilidad" y "accesibilidad" no tienen recursos propios todavía.
NECESIDADES = {
    "violencia": {"tipos": {"organizacion_mujeres"}, "texto": ["violencia"]},
    "orientacion_legal": {"tipos": set(), "texto": ["legal", "orientacion", "defensoria"]},
    "salud": {"tipos": {"salud"}, "texto": []},
    "alimentacion": {"tipos": {"olla_comun", "comedor_adulto_mayor"}, "texto": []},
    "cuidado_infantil": {"tipos": {"cuidado_infantil"}, "texto": []},
    "personas_mayores": {"tipos": TIPOS_PERSONAS_MAYORES, "texto": ["adultas mayores", "adultos mayores"]},
    "ninez": {"tipos": set(), "texto": ["nina", "nino"]},
    "tramites": {"tipos": set(), "texto": ["tramites"]},
    "cultura_educacion": {"tipos": {"espacio_verde", "espacio_cultural", "educacion"}, "texto": []},
    "apoyo_comunitario": {"tipos": {"organizacion_mujeres", "olla_comun"}, "texto": []},
    "memoria": {"tipos": {"lugar_memoria", "organizacion_mujeres"}, "texto": []},
    "movilidad": {"tipos": set(), "texto": []},
    "accesibilidad": {"tipos": set(), "texto": []},
}
# Desde esta pertinencia un recurso es alternativa directa; por debajo, solo complementaria.
PERTINENCIA_DIRECTA = 2.0
# Palabras como "hijo" o "cuidado" suelen nombrar a quién se cuida, no lo que se busca:
# solo cuentan cuando son la necesidad principal.
TEMAS_SOLO_PRINCIPALES = {"ninez", "apoyo_comunitario", "otro"}
TIPOS_POR_POBLACION = {
    "cuidado_infantil": {"cuidado_infantil"},
    "personas_mayores": TIPOS_PERSONAS_MAYORES,
}

ESTILOS = """
<style>
  h1, h2, h3 { color: #7A3322; }
  .bloque-inicio { background: #F6E9DA; border-radius: 16px; padding: 1.1rem 1.4rem; margin-bottom: .8rem; }
  .bloque-inicio h1 { margin: 0; padding: 0; font-size: 2rem; }
  .bloque-inicio p { margin: .3rem 0 0; }
  .semaforo { display: flex; flex-wrap: wrap; gap: .5rem .3rem; margin: .5rem 0 .3rem; padding: 0; list-style: none; }
  .dimension { display: flex; flex-direction: column; align-items: center; width: 5.4rem;
               text-align: center; font-size: .78rem; font-weight: 600; line-height: 1.15; }
  .circulo { width: 2.5rem; height: 2.5rem; border-radius: 50%; display: flex; align-items: center;
             justify-content: center; font-size: 1.15rem; font-weight: 800; margin-bottom: .3rem;
             border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(59, 42, 32, .3); }
  .circulo-si { background: #2A6F48; color: #fff; }
  .circulo-parcial { background: #F2C14E; color: #3B2A20; }
  .circulo-no { background: #B3261E; color: #fff; }
  .circulo-verificar { background: #6F6A64; color: #fff; }
  .leyenda { font-size: .8rem; color: #5A4636; margin: 0 0 .6rem; }
  .icono-ambito { font-size: 1.5rem; margin-right: .35rem; }
  .relato-vecina { background: #fff; border-radius: 12px; padding: .7rem 1rem; margin: .45rem 0;
                   border-left: 5px solid #7B3FA0; }
  .relato-vecina.seguro { border-left-color: #C2185B; }
  .relato-vecina p { margin: .2rem 0; }
  .contactos-utiles { background: #FFFFFF; border: 1px solid #E3CDB8; border-radius: 12px; padding: .8rem 1.1rem; }
  .contactos-utiles a { color: #7A3322; font-weight: 700; }
  .ayuda-urgente { background: #B3261E; color: #fff; border-radius: 14px; padding: 1rem 1.3rem; margin-bottom: 1rem; }
  .ayuda-urgente a { color: #fff; font-weight: 700; }
  .ayuda-urgente p { margin: .25rem 0; font-size: 1.05rem; }
  .sintetico { background: #3B2A20; color: #fff; border-radius: 6px; padding: .05rem .4rem; font-size: .75rem; }
</style>
"""


def estilos_tarjetas() -> str:
    """Fondo suave y borde izquierdo del color de cada ámbito en las tarjetas del asistente."""
    reglas = [
        f'div[class*="st-key-tarjeta-{ambito.replace("_", "-")}-"] {{ background: {FONDO_AMBITO[ambito]}; '
        f"border-left: 6px solid {COLOR_AMBITO[ambito]} !important; border-radius: 14px; }}"
        for ambito in FONDO_AMBITO
    ]
    return "<style>\n" + "\n".join(reglas) + "\n</style>"


@st.cache_data
def cargar_recursos(ruta: Path, version: float) -> pd.DataFrame:
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df


def leer_csv(ruta: Path, columnas: list[str]) -> pd.DataFrame:
    try:
        return pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except (OSError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=columnas, dtype=str)


def leer_datos(ejemplo: Path, real: Path, columnas: list[str]) -> pd.DataFrame:
    """Une los ejemplos publicados con lo real; cualquiera de los dos archivos puede faltar."""
    partes = [df for df in (leer_csv(ejemplo, columnas), leer_csv(real, columnas)) if not df.empty]
    if not partes:
        return pd.DataFrame(columns=columnas, dtype=str)
    return pd.concat(partes, ignore_index=True).reindex(columns=columnas).fillna("")


def agregar_fila(ruta: Path, columnas: list[str], fila: dict) -> bool:
    """Agrega una fila creando carpeta y archivo si hace falta. Devuelve False si no pudo."""
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        nuevo = not ruta.exists() or ruta.stat().st_size == 0
        with open(ruta, "a", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas, lineterminator="\n")
            if nuevo:
                escritor.writeheader()
            escritor.writerow(fila)
    except OSError:
        return False
    return True


def mes_actual() -> str:
    return date.today().strftime("%Y-%m")


def es_nacional(recurso) -> bool:
    return recurso["distrito"] != ALCANCE_LIMA and "nacional" in normalizar(recurso["nombre"])


def disponible_en(recurso, distrito: str) -> bool:
    return recurso["distrito"] in (distrito, ALCANCE_LIMA) or es_nacional(recurso)


def zona(recurso) -> str:
    if recurso["distrito"] == ALCANCE_LIMA:
        return "Lima Metropolitana y Callao"
    return "Nacional" if es_nacional(recurso) else recurso["distrito"]


def es_relevante(recurso, consulta: ConsultaEstructurada) -> bool:
    regla = NECESIDADES.get(consulta.tipo_necesidad)
    if regla is None:
        return recurso["ambito"] == consulta.ambito
    texto = normalizar(f"{recurso['nombre']} {recurso['descripcion']}")
    return recurso["tipo"] in regla["tipos"] or any(t in texto for t in regla["texto"])


def coincidencia(recurso, tipo_necesidad: str) -> float:
    """3 si el tipo o el nombre del recurso responde a la necesidad; 2 si solo la descripción."""
    regla = NECESIDADES.get(tipo_necesidad)
    if regla is None:
        return 0.0
    nombre = normalizar(recurso["nombre"])
    if recurso["tipo"] in regla["tipos"] or any(t in nombre for t in regla["texto"]):
        return 3.0
    descripcion = normalizar(recurso["descripcion"])
    return 2.0 if any(t in descripcion for t in regla["texto"]) else 0.0


def pertinencia(recurso, consulta: ConsultaEstructurada, temas: list[str]) -> float:
    """Cuánto responde el recurso a lo que se pidió, sin mirar el semáforo.

    Cuenta la necesidad principal y, a mitad de peso, otras necesidades específicas que las
    palabras clave reconocen en el texto (por si la IA eligió una categoría demasiado general).
    """
    if consulta.tipo_necesidad in NECESIDADES:
        total = coincidencia(recurso, consulta.tipo_necesidad)
    else:
        total = 2.0 if consulta.ambito != "sin_clasificar" and recurso["ambito"] == consulta.ambito else 0.0
    for tema in dict.fromkeys(temas):
        if tema != consulta.tipo_necesidad and tema not in TEMAS_SOLO_PRINCIPALES:
            total += 0.5 * coincidencia(recurso, tema)
    return total


def es_de_otra_poblacion(recurso, consulta: ConsultaEstructurada) -> bool:
    """Un servicio para personas mayores no es complemento de una guardería, ni al revés."""
    return any(
        recurso["tipo"] in tipos and necesidad != consulta.tipo_necesidad
        for necesidad, tipos in TIPOS_POR_POBLACION.items()
    )


def puntaje(recurso, restricciones: dict[str, str]) -> float:
    total = 0.5 if recurso["estado_verificacion"] == "si" else 0.0
    for dimension in DIMENSIONES:
        valor = recurso[dimension]
        pedida = dimension in restricciones
        total += PESOS.get(valor, 0.0) * (3 if pedida else 1)
        if pedida and valor == "no":
            total -= 6
    return total


def buscar_alternativas(
    recursos: pd.DataFrame, consulta: ConsultaEstructurada, distrito: str, temas: list[str] | None = None
) -> list[dict]:
    """Ordena por pertinencia; luego reales antes que sintéticos; recién después, el semáforo.

    Así, un recurso pertinente con datos "por verificar" no queda detrás de un ejemplo
    sintético que tiene todas las dimensiones en "sí".
    """
    temas = temas or []
    restricciones = consulta.restricciones.activas()
    candidatos = []
    for recurso in recursos.to_dict("records"):
        if disponible_en(recurso, distrito):
            candidatos.append({**recurso, "pertinencia": pertinencia(recurso, consulta, temas)})
    candidatos.sort(key=lambda r: (
        -r["pertinencia"],
        r["estado_verificacion"] == "sintetico",
        -puntaje(r, restricciones),
        r["distrito"] != distrito,
        r["id"],
    ))

    directas = [{**r, "complementaria": False} for r in candidatos if r["pertinencia"] >= PERTINENCIA_DIRECTA][:3]
    if not directas:
        return []
    ids = {r["id"] for r in directas}
    # Complementarias: primero las algo pertinentes; después, otras del mismo ámbito y la misma población.
    complementarias = [
        {**r, "complementaria": True}
        for r in candidatos
        if r["id"] not in ids
        and (r["pertinencia"] > 0 or (r["ambito"] == consulta.ambito and not es_de_otra_poblacion(r, consulta)))
    ]
    return directas + complementarias[: 3 - len(directas)]


def tiene_lista_espera(recurso: dict) -> bool:
    texto = normalizar(" ".join(recurso[c] for c in ("descripcion", "horario", "requisitos", "canales", "costo")))
    return any(t in texto for t in TERMINOS_ESPERA)


def tiene_dato_por_verificar(recurso: dict) -> bool:
    texto = normalizar(" ".join(recurso[c] for c in ("costo", "horario", "requisitos", "canales")))
    return (
        recurso["estado_verificacion"] == "por_verificar"
        or any(recurso[d] == "por_verificar" for d in DIMENSIONES)
        or "verificar" in texto
    )


def es_comunitaria(recurso: dict) -> bool:
    return recurso["tipo"] in TIPOS_COMUNITARIOS or "comunitari" in normalizar(recurso["nombre"])


def sugerir_comunitaria(
    recursos: pd.DataFrame, consulta: ConsultaEstructurada, distrito: str, alternativas: list[dict]
) -> dict | None:
    """Busca una red comunitaria del distrito cuando alguna alternativa tiene espera o dudas."""
    if not any(tiene_lista_espera(a) or tiene_dato_por_verificar(a) for a in alternativas):
        return None
    usados = {a["id"] for a in alternativas}
    restricciones = consulta.restricciones.activas()
    opciones = [
        r for r in recursos.to_dict("records")
        if r["distrito"] == distrito
        and es_comunitaria(r)
        and (es_relevante(r, consulta) or r["ambito"] == consulta.ambito)
        and (es_relevante(r, consulta) or not es_de_otra_poblacion(r, consulta))
        and r["id"] not in usados
        and not tiene_lista_espera(r)
        and not any(r[d] == "no" for d in restricciones)
        and (consulta.tipo_necesidad != "violencia" or r["tipo"] == "organizacion_mujeres")
    ]
    if not opciones:
        return None
    opciones.sort(key=lambda r: (
        not es_relevante(r, consulta),
        r["estado_verificacion"] == "sintetico",
        -puntaje(r, restricciones),
        r["id"],
    ))
    return {**opciones[0], "complementaria": False}


def es_movilidad(consulta: ConsultaEstructurada) -> bool:
    return consulta.tipo_necesidad == "movilidad" or consulta.ambito == "movilidad_seguridad"


def detectar_barreras(alternativas: list[dict], consulta: ConsultaEstructurada) -> list[tuple[str, str]]:
    """Devuelve (dimensión, motivo) por cada necesidad que quedó sin solución."""
    restricciones = list(consulta.restricciones.activas())
    alternativas = [a for a in alternativas if not a["complementaria"]]
    if not alternativas:
        por_defecto = "seguridad" if es_movilidad(consulta) else "territorial"
        return [(d, "sin_recurso") for d in (restricciones or [por_defecto])]

    barreras = []
    for dimension in restricciones:
        valores = [a[dimension] for a in alternativas]
        if any(v in ("si", "parcial") for v in valores):
            continue
        motivo = "dato_por_verificar" if "por_verificar" in valores else "condicion_no_cumplida"
        barreras.append((dimension, motivo))
    return barreras


def registrar_barreras(barreras: list[tuple[str, str]], consulta: ConsultaEstructurada, distrito: str) -> bool:
    """Guarda solo categorías: nunca el texto de la consulta ni datos de la persona.

    busqueda_id es aleatorio y solo sirve para contar una búsqueda con varias barreras una vez.
    """
    busqueda_id = uuid.uuid4().hex[:12]
    resultados = [
        agregar_fila(RUTA_BARRERAS, COLUMNAS_BARRERAS, {
            "fecha_mes": mes_actual(),
            "distrito": distrito,
            "ambito": "movilidad_seguridad" if es_movilidad(consulta) else consulta.ambito,
            "dimension": dimension,
            "tipo_necesidad": consulta.tipo_necesidad,
            "motivo": motivo,
            "origen": "real",
            "busqueda_id": busqueda_id,
        })
        for dimension, motivo in barreras
    ]
    return all(resultados)


def mostrar_ayuda_urgente() -> None:
    st.markdown(
        """<div class="ayuda-urgente" role="alert">
        <p><strong>Si estás en peligro ahora, llama al <a href="tel:105">105</a></strong> (Policía Nacional).</p>
        <p><strong>Línea <a href="tel:100">100</a></strong>: gratuita, las 24 horas. Orientación y soporte emocional frente a la violencia.</p>
        </div>""",
        unsafe_allow_html=True,
    )


def mostrar_fuente(resultado: Resultado) -> None:
    if resultado.fuente != "respaldo":
        st.caption(f"Analizado con {NOMBRES_MODO[resultado.fuente]}.")
    elif resultado.aviso:
        st.caption(f"{resultado.aviso} Analizado por palabras clave.")
    else:
        st.caption("Analizado por palabras clave.")


def html_semaforo(recurso: dict) -> str:
    items = []
    for dimension, (etiqueta, pregunta) in DIMENSIONES.items():
        simbolo, texto, clase = SEMAFORO.get(recurso[dimension], SEMAFORO["por_verificar"])
        descripcion = html.escape(f"{etiqueta}: {texto}. {pregunta}")
        items.append(
            f'<li class="dimension" title="{descripcion}" aria-label="{descripcion}">'
            f'<span class="circulo {clase}" aria-hidden="true">{simbolo}</span>'
            f"{html.escape(NOMBRE_CORTO[dimension])}</li>"
        )
    leyenda = " · ".join(f"{s} {t}" for s, t, _ in SEMAFORO.values())
    return f'<ul class="semaforo">{"".join(items)}</ul><p class="leyenda">{leyenda}</p>'


def detalle_dimension(dimension: str, recurso: dict) -> str:
    campos = {
        "economica": ("Costo", "costo"),
        "institucional": ("Requisitos", "requisitos"),
        "territorial": ("Horario", "horario"),
        "comunicacional": ("Canales", "canales"),
    }
    if dimension not in campos:
        return ""
    etiqueta, campo = campos[dimension]
    return f" {etiqueta}: {recurso[campo]}."


def mostrar_barreras_recurso(recurso: dict, restricciones: dict[str, str]) -> None:
    sin_confirmar = []
    for dimension, (etiqueta, pregunta) in DIMENSIONES.items():
        valor = recurso[dimension]
        if valor == "por_verificar":
            sin_confirmar.append(dimension)
        elif valor in ("no", "parcial"):
            estado = "Barrera" if valor == "no" else "Se cumple solo en parte"
            aclaracion = " Mencionaste esta condición." if dimension in restricciones else ""
            st.markdown(f"**{etiqueta} · {estado}.** {pregunta}{detalle_dimension(dimension, recurso)}{aclaracion}")

    pedidas = [ETIQUETAS_DIMENSION[d] for d in sin_confirmar if d in restricciones]
    if pedidas:
        st.markdown(f"**Sin confirmar lo que mencionaste:** {', '.join(pedidas)}. Pregunta antes de ir.")
    if sin_confirmar:
        st.caption("Sin confirmar: " + ", ".join(ETIQUETAS_DIMENSION[d] for d in sin_confirmar) + ".")


def aviso_verificacion(recurso: dict) -> None:
    estado = recurso["estado_verificacion"]
    partes = []
    if estado == "sintetico":
        partes.append("Ejemplo sintético del demo: no es un servicio real.")
    elif estado == "por_verificar":
        partes.append("Estos datos aún no están verificados.")
    elif estado == "parcial":
        partes.append("Estos datos están verificados solo en parte.")
    if partes:
        st.warning(" ".join(partes) + " Confirma antes de ir.", icon="⚠️")


def tiene_dato(valor: str) -> bool:
    return normalizar(valor.strip()) not in SIN_DATO


def enlace_telefono(telefono: str) -> str:
    """Convierte '(01) 319-2530 anexo 601' en un enlace tel: con solo el número."""
    numero = "".join(c for c in normalizar(telefono).split("anexo")[0].split("(c")[0] if c.isdigit())
    texto = html.escape(telefono)
    return f'<a href="tel:{numero}">{texto}</a>' if numero else texto


def mostrar_contacto(recurso: dict) -> None:
    lineas = []
    if tiene_dato(recurso["direccion"]):
        lineas.append(f"**Dirección:** {html.escape(recurso['direccion'])}")
    if tiene_dato(recurso["telefono"]):
        lineas.append(f"**Teléfono:** {enlace_telefono(recurso['telefono'])}")
    if tiene_dato(recurso["redes"]):
        redes = recurso["redes"].strip()
        enlace = f'<a href="{html.escape(redes)}" target="_blank">{html.escape(redes)}</a>' if redes.startswith("http") else html.escape(redes)
        lineas.append(f"**Web o redes:** {enlace}")
    if lineas:
        st.markdown("  \n".join(lineas), unsafe_allow_html=True)
    else:
        st.caption("Dirección, teléfono y redes: por verificar.")

    if recurso["estado_verificacion"] == "sintetico" or pd.isna(recurso["lat"]) or pd.isna(recurso["lon"]):
        return
    destino = f"{recurso['lat']},{recurso['lon']}"
    st.link_button("📍 Cómo llegar", f"https://www.google.com/maps/search/?api=1&query={destino}")
    if recurso["coord_verificadas"] != "si":
        st.caption("La ubicación en el mapa es aproximada: confirma la dirección antes de ir.")


def mostrar_alternativa(titulo: str, recurso: dict, restricciones: dict[str, str]) -> None:
    ambito = recurso["ambito"]
    clave = f"tarjeta-{ambito.replace('_', '-')}-{recurso['id']}"
    with st.container(border=True, key=clave):
        icono = ICONOS_AMBITO.get(ambito, "📍")
        st.markdown(
            f'<h3><span class="icono-ambito" aria-hidden="true">{icono}</span>{html.escape(titulo)}</h3>',
            unsafe_allow_html=True,
        )
        st.caption(f"{icono} {ETIQUETAS_AMBITO.get(ambito, ambito)} · {zona(recurso)}")
        if recurso["complementaria"]:
            st.info("Alternativa complementaria: es del mismo ámbito, pero puede no resolver lo que necesitas.")
        st.write(recurso["descripcion"])
        st.markdown(html_semaforo(recurso), unsafe_allow_html=True)
        st.markdown(
            f"**Costo:** {recurso['costo']}  \n**Horario:** {recurso['horario']}  \n"
            f"**Requisitos:** {recurso['requisitos']}  \n**Canales de atención:** {recurso['canales']}"
        )
        mostrar_contacto(recurso)
        mostrar_barreras_recurso(recurso, restricciones)
        aviso_verificacion(recurso)


def relatos_de_seguridad(distrito: str) -> pd.DataFrame:
    relatos = leer_datos(EJEMPLO_RELATOS, RUTA_RELATOS, COLUMNAS_RELATOS)
    return relatos[
        (relatos["distrito"] == distrito)
        & (relatos["capa"].isin(CAPAS_SEGURIDAD) | (relatos["ambito"] == "movilidad_seguridad"))
    ]


def mostrar_movilidad(distrito: str) -> None:
    """Para paraderos, transporte y calles: voces del barrio, contactos útiles e invitación a contar."""
    st.markdown(
        f'<h3><span class="icono-ambito" aria-hidden="true">🚌</span>Moverte con seguridad en {html.escape(distrito)}</h3>',
        unsafe_allow_html=True,
    )
    st.write(
        "Todavía no tenemos un servicio que garantice un paradero o un camino seguro. "
        "Esto es lo que sabemos por ahora."
    )

    st.markdown("**Lo que cuentan las vecinas**")
    relatos = relatos_de_seguridad(distrito)
    if relatos.empty:
        st.caption("Aún no hay relatos sobre seguridad en este distrito.")
    for _, relato in relatos.iterrows():
        seguro = relato["capa"] == "seguridad"
        icono, etiqueta = ("💡", "Se siente seguro") if seguro else ("🌙", "Da miedo")
        marca = ' <span class="sintetico">EJEMPLO SINTÉTICO</span>' if relato["origen"] == "sintetico" else ""
        lugar = html.escape(relato["lugares"] or relato["ubicacion"])
        st.markdown(
            f'<div class="relato-vecina{" seguro" if seguro else ""}">'
            f"<p><strong>{icono} {etiqueta} · {lugar}</strong>{marca}</p>"
            f"<p>{html.escape(relato['texto'][:400])}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("**Contactos útiles**")
    st.markdown(
        f"""<div class="contactos-utiles">
        <p>🚓 <a href="tel:105">105</a>: Policía Nacional, si estás en peligro ahora.</p>
        <p>💜 <a href="tel:100">Línea 100</a>: gratuita, las 24 horas, frente al acoso y la violencia.</p>
        <p>🦺 {html.escape(SERENAZGO[distrito])} (dato de gob.pe, por verificar).</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.info(
        "¿Conoces un paradero o una calle que da miedo, o uno donde te sientes segura? "
        "Cuéntalo en la pestaña **Voces**: cada relato mejora el mapa del barrio.",
        icon="🗣️",
    )


def usar_ejemplo(texto: str) -> None:
    st.session_state["asistente_texto"] = texto


def pestana_asistente(recursos: pd.DataFrame) -> None:
    st.header("Cuéntanos qué necesitas")
    st.write("Buscamos alternativas en tu distrito y te mostramos qué tan accesible es cada una.")
    st.caption("Prueba con un ejemplo:")
    for columna, (icono, ejemplo) in zip(st.columns(len(EJEMPLOS_BUSQUEDA)), EJEMPLOS_BUSQUEDA):
        columna.button(f"{icono} {ejemplo}", on_click=usar_ejemplo, args=(ejemplo,), width="stretch")
    with st.form("form_asistente"):
        texto = st.text_area(
            "¿Qué necesitas?",
            key="asistente_texto",
            placeholder="Ejemplo: necesito un lugar para almorzar barato y uso silla de ruedas",
            help="No escribas tu nombre, DNI, teléfono ni dirección.",
        )
        distrito = st.selectbox("Distrito", DISTRITOS)
        enviado = st.form_submit_button("Buscar alternativas", type="primary")

    if enviado:
        if not texto.strip():
            st.session_state.pop("asistente", None)
            st.info("Escribe tu necesidad para poder buscar.")
        else:
            with st.spinner("Buscando alternativas..."):
                resultado = estructurar_consulta(texto.strip(), distrito)
            alternativas = buscar_alternativas(recursos, resultado.datos, distrito, resultado.temas)
            barreras = detectar_barreras(alternativas, resultado.datos)
            guardadas = registrar_barreras(barreras, resultado.datos, distrito)
            comunitaria = sugerir_comunitaria(recursos, resultado.datos, distrito, alternativas)
            st.session_state["asistente"] = (resultado, alternativas, barreras, distrito, guardadas, comunitaria)

    if "asistente" not in st.session_state:
        return

    resultado, alternativas, barreras, distrito, guardadas, comunitaria = st.session_state["asistente"]
    consulta = resultado.datos
    if consulta.riesgo:
        mostrar_ayuda_urgente()

    st.markdown(f"**Entendimos:** {html.escape(consulta.necesidad)} · {distrito}")
    restricciones = consulta.restricciones.activas()
    if restricciones:
        st.markdown("**Condiciones a cuidar:** " + ", ".join(ETIQUETAS_DIMENSION[d] for d in restricciones))
    mostrar_fuente(resultado)

    if alternativas:
        for numero, recurso in enumerate(alternativas, start=1):
            mostrar_alternativa(f"{numero}. {recurso['nombre']}", recurso, restricciones)
        if len(alternativas) < 3:
            st.caption(f"Solo encontramos {len(alternativas)} alternativa(s) compatible(s) en la base actual.")
        if comunitaria:
            motivo = (
                "Alguna opción tiene lista de espera."
                if any(tiene_lista_espera(a) for a in alternativas)
                else "Algunos datos de estas opciones están por verificar."
            )
            st.markdown(f"**También puedes buscar apoyo comunitario.** {motivo}")
            mostrar_alternativa(f"Alternativa comunitaria: {comunitaria['nombre']}", comunitaria, restricciones)
    elif not es_movilidad(consulta):
        st.info(
            f"Todavía no tenemos este servicio en el directorio de {distrito}. "
            "No queremos mostrarte algo que no responde a lo que buscas: registramos este vacío "
            "para que el Observatorio lo haga visible."
        )
    if es_movilidad(consulta):
        mostrar_movilidad(distrito)

    if barreras and guardadas:
        st.success("Registramos esta barrera de forma anónima para el Observatorio. No guardamos lo que escribiste.")
    elif barreras:
        st.warning("No pudimos registrar esta barrera en el Observatorio.", icon="⚠️")
    st.caption("El asistente orienta; no reemplaza la atención ni da asesoría legal.")


def ubicar_relato(lugares: list[str], distrito: str, recursos: pd.DataFrame, semilla: str) -> tuple[float, float, str]:
    """Da un punto aproximado cerca de un lugar público conocido; nunca una vivienda."""
    lat, lon = CENTROS[distrito]
    ubicacion = "Zona aproximada del distrito"
    candidatos = recursos[
        (recursos["distrito"] == distrito)
        & recursos["lat"].notna()
        & (recursos["estado_verificacion"] != "sintetico")
    ]
    terminos = [normalizar(l) for l in lugares if len(l.strip()) >= 5]
    encontrado = False
    for _, recurso in candidatos.iterrows():
        nombre = normalizar(recurso["nombre"])
        for termino in terminos:
            palabras = [p for p in termino.split() if len(p) >= 6]
            if termino in nombre or nombre in termino or any(p in nombre for p in palabras):
                lat, lon = recurso["lat"], recurso["lon"]
                ubicacion = f"Cerca de {recurso['nombre']}"
                encontrado = True
                break
        if encontrado:
            break

    huella = hashlib.sha256(semilla.encode()).digest()
    lat += (huella[0] - 127.5) / 127.5 * 0.003
    lon += (huella[1] - 127.5) / 127.5 * 0.003
    return round(float(lat), 4), round(float(lon), 4), ubicacion


def guardar_relato(recursos: pd.DataFrame) -> None:
    pendiente = st.session_state.get("voces_resultado")
    texto = st.session_state.get("voces_revision", "").strip()
    if not pendiente or not texto or not st.session_state.get("voces_consentimiento"):
        return
    resultado, distrito = pendiente
    relato = resultado.datos
    identificador = uuid.uuid4().hex[:8]
    lat, lon, ubicacion = ubicar_relato(relato.lugares, distrito, recursos, identificador)
    guardado = agregar_fila(RUTA_RELATOS, COLUMNAS_RELATOS, {
        "id": identificador,
        "fecha_mes": mes_actual(),
        "distrito": distrito,
        "texto": texto,
        "lugares": "; ".join(relato.lugares),
        "ambito": relato.ambito,
        "capa": relato.capa,
        "emociones": "; ".join(relato.emociones),
        "memoria": "; ".join(relato.memoria),
        "lat": lat,
        "lon": lon,
        "ubicacion": ubicacion,
        "origen": "real",
    })
    if not guardado:
        st.session_state["voces_error"] = True
        return
    for clave in ("voces_resultado", "voces_revision", "voces_consentimiento", "voces_texto", "voces_metodo"):
        st.session_state.pop(clave, None)
    st.session_state["voces_guardado"] = True


def base_mapa(filtro: str, puntos: pd.DataFrame) -> folium.Map:
    """Encuadra los puntos visibles y el distrito completo, sin acercarse más que ZOOM_MAXIMO."""
    centro, zoom = VISTA_MAPA[filtro]
    mapa = folium.Map(location=centro, zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)
    distritos = DISTRITOS if filtro == "Todos" else [filtro]
    lats = [p[0] for d in distritos for p in LIMITES_DISTRITO[d]]
    lons = [p[1] for d in distritos for p in LIMITES_DISTRITO[d]]
    coordenadas = puntos[["lat", "lon"]].apply(pd.to_numeric, errors="coerce").dropna()
    lats += coordenadas["lat"].tolist()
    lons += coordenadas["lon"].tolist()
    mapa.fit_bounds([(min(lats), min(lons)), (max(lats), max(lons))], padding=(16, 16), max_zoom=ZOOM_MAXIMO)
    return mapa


def punto(lat: float, lon: float, color: str, popup: str, titulo: str) -> folium.CircleMarker:
    return folium.CircleMarker(
        location=(lat, lon),
        radius=9,
        color="#FFFFFF",
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.92,
        popup=folium.Popup(popup, max_width=320),
        tooltip=html.escape(titulo),
    )


def nombre_capa(etiqueta: str, color: str, cantidad: int) -> str:
    return f'<span style="color:{color}">●</span> {html.escape(etiqueta)} ({cantidad})'


def mapa_relatos(relatos: pd.DataFrame, filtro: str) -> folium.Map:
    mapa = base_mapa(filtro, relatos)
    for capa, (etiqueta, color) in CAPAS.items():
        filas = relatos[relatos["capa"] == capa]
        grupo = folium.FeatureGroup(name=nombre_capa(etiqueta, color, len(filas)))
        for _, fila in filas.iterrows():
            marca = "<b>EJEMPLO SINTÉTICO</b><br>" if fila["origen"] == "sintetico" else ""
            memoria = f"<br><b>Memoria:</b> {html.escape(fila['memoria'])}" if fila["memoria"] else ""
            emociones = f"<br><b>Emociones:</b> {html.escape(fila['emociones'])}" if fila["emociones"] else ""
            texto = html.escape(fila["texto"][:400])
            popup = (
                f"{marca}<b>{html.escape(etiqueta)}</b><br>{texto}{emociones}{memoria}"
                f"<br><i>{html.escape(fila['ubicacion'])}</i>"
            )
            punto(float(fila["lat"]), float(fila["lon"]), color, popup, f"{etiqueta}: {fila['distrito']}").add_to(grupo)
        grupo.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    return mapa


def pestana_voces(recursos: pd.DataFrame) -> None:
    st.header("Voces que conectan y construyen")
    st.write(
        "Cuenta algo sobre tu barrio: un lugar que da miedo, una red de cuidado, una memoria que no debe perderse. "
        "No hace falta relatar hechos de violencia en detalle."
    )
    if st.session_state.pop("voces_guardado", False):
        st.success("Relato guardado y agregado al mapa. Gracias por compartirlo.")
    if st.session_state.pop("voces_error", False):
        st.error("No pudimos guardar el relato. Inténtalo de nuevo.")

    metodo = transcripcion.metodo_disponible()
    if metodo == "manual":
        st.info("La transcripción de audio no está disponible en este equipo. Puedes pegar aquí el texto del relato.")
    else:
        st.caption(f"🎙️ El audio se transcribe con {transcripcion.NOMBRES_METODO[metodo]}.")
        if metodo == "gemini":
            st.caption("En esta versión de demostración, graba solo relatos de ejemplo, sin datos reales.")
        grabacion = st.audio_input("Graba tu relato con el micrófono", key="voces_grabacion")
        archivo = st.file_uploader("O sube un audio", type=["mp3", "wav", "m4a", "ogg", "flac"], key="voces_archivo")
        audio = grabacion or archivo
        if audio and st.button("Transcribir audio"):
            with st.spinner("Transcribiendo el audio..."):
                try:
                    texto_audio, usado = transcripcion.transcribir(audio.getvalue(), audio.name or "grabacion.wav")
                except RuntimeError as error:
                    st.warning(f"{error} Puedes pegar aquí el texto del relato.")
                else:
                    if texto_audio:
                        st.session_state["voces_texto"] = texto_audio
                        st.session_state["voces_metodo"] = usado
                    else:
                        st.warning("No se entendió el audio. Prueba grabar de nuevo o pega el texto.")
        if st.session_state.get("voces_metodo"):
            st.caption(f"Transcrito con {transcripcion.NOMBRES_METODO[st.session_state['voces_metodo']]}. Revisa el texto.")

    texto = st.text_area("Texto del relato", key="voces_texto", height=130)
    distrito = st.selectbox("Distrito del relato", DISTRITOS, key="voces_distrito")
    if st.button("Estructurar relato", type="primary"):
        if texto.strip():
            with st.spinner("Organizando el relato..."):
                resultado = estructurar_relato(texto.strip())
            st.session_state["voces_resultado"] = (resultado, distrito)
            st.session_state["voces_revision"] = resultado.datos.texto_anonimizado
            st.session_state["voces_consentimiento"] = False
        else:
            st.info("Pega o transcribe un relato para continuar.")

    if "voces_resultado" in st.session_state:
        resultado, distrito_relato = st.session_state["voces_resultado"]
        relato = resultado.datos
        if relato.riesgo:
            mostrar_ayuda_urgente()
        with st.container(border=True):
            st.subheader("Revisa antes de guardar")
            mostrar_fuente(resultado)
            etiqueta_capa = CAPAS[relato.capa][0]
            st.markdown(
                f"**Capa:** {etiqueta_capa} · **Ámbito:** {ETIQUETAS_AMBITO[relato.ambito]} · **Distrito:** {distrito_relato}"
            )
            st.markdown(f"**Lugares:** {html.escape(', '.join(relato.lugares)) or 'Ninguno identificado'}")
            st.markdown(f"**Emociones:** {html.escape(', '.join(relato.emociones)) or 'Ninguna identificada'}")
            st.markdown(f"**Mujeres o hechos de memoria:** {html.escape(', '.join(relato.memoria)) or 'Ninguno identificado'}")
            st.text_area(
                "Texto que se guardará. Quita nombres de personas vivas y direcciones de viviendas.",
                key="voces_revision",
                height=130,
            )
            st.checkbox(
                "La persona que cuenta este relato dio su consentimiento para guardarlo y mostrarlo en el mapa.",
                key="voces_consentimiento",
            )
            st.button(
                "Guardar relato",
                disabled=not st.session_state.get("voces_consentimiento"),
                on_click=guardar_relato,
                args=(recursos,),
            )

    st.subheader("Mapa de voces")
    st.caption("Los puntos son aproximados y nunca señalan viviendas. Activa o desactiva capas en el recuadro del mapa.")
    relatos = leer_datos(EJEMPLO_RELATOS, RUTA_RELATOS, COLUMNAS_RELATOS)
    filtro = st.selectbox("Ver distrito", list(VISTA_MAPA), key="voces_filtro")
    visibles = relatos if filtro == "Todos" else relatos[relatos["distrito"] == filtro]
    st_folium(
        mapa_relatos(visibles, filtro),
        height=460,
        use_container_width=True,
        returned_objects=[],
        key=f"mapa_voces_{filtro}_{len(relatos)}",
    )
    sinteticos = int((visibles["origen"] == "sintetico").sum())
    if sinteticos:
        st.caption(f"{sinteticos} de {len(visibles)} relatos son ejemplos sintéticos.")


def grafico_barras(datos: pd.DataFrame, columna: str, etiquetas: dict[str, str]) -> alt.Chart:
    conteo = (
        datos[columna].map(lambda v: etiquetas.get(v, v)).value_counts().rename_axis("categoria").reset_index(name="barreras")
    )
    base = alt.Chart(conteo).encode(
        y=alt.Y("categoria:N", sort="-x", title=None, axis=alt.Axis(labelLimit=240, ticks=False, domain=False)),
        x=alt.X("barreras:Q", title=None, axis=None, scale=alt.Scale(nice=False, domainMin=0)),
        tooltip=[alt.Tooltip("categoria:N", title="Categoría"), alt.Tooltip("barreras:Q", title="Barreras")],
    )
    barras = base.mark_bar(color="#A8452E", size=18, cornerRadiusEnd=4)
    numeros = base.mark_text(align="left", dx=5, color="#3B2A20", fontWeight=600).encode(text="barreras:Q")
    return (barras + numeros).properties(height=36 * len(conteo) + 12)


def mostrar_grafico(titulo: str, datos: pd.DataFrame, columna: str, etiquetas: dict[str, str]) -> None:
    st.subheader(titulo)
    st.altair_chart(grafico_barras(datos, columna, etiquetas), width="stretch")


def mapa_recursos(recursos: pd.DataFrame, filtro: str) -> folium.Map:
    mapa = base_mapa(filtro, recursos)
    for ambito in sorted(recursos["ambito"].unique()):
        filas = recursos[recursos["ambito"] == ambito]
        etiqueta = ETIQUETAS_AMBITO.get(ambito, ambito)
        color = COLOR_AMBITO.get(ambito, "#6F6A64")
        grupo = folium.FeatureGroup(name=nombre_capa(etiqueta, color, len(filas)))
        for _, fila in filas.iterrows():
            marca = "<b>EJEMPLO SINTÉTICO</b><br>" if fila["estado_verificacion"] == "sintetico" else ""
            popup = (
                f"{marca}<b>{html.escape(fila['nombre'])}</b><br>{html.escape(fila['descripcion'])}"
                f"<br><b>Verificación:</b> {html.escape(fila['estado_verificacion'])}"
                "<br><i>Ubicación aproximada</i>"
            )
            punto(fila["lat"], fila["lon"], color, popup, fila["nombre"]).add_to(grupo)
        grupo.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    return mapa


def pestana_observatorio(recursos: pd.DataFrame) -> None:
    st.header("Observatorio de barreras")
    st.write("Lo que no tuvo solución se convierte en evidencia por ámbito, dimensión y distrito.")
    barreras = leer_datos(EJEMPLO_BARRERAS, RUTA_BARRERAS, COLUMNAS_BARRERAS)

    filtro_columna, incluir_columna = st.columns([1, 1])
    filtro = filtro_columna.selectbox("Distrito", list(VISTA_MAPA), key="observatorio_distrito")
    incluir = incluir_columna.checkbox("Incluir datos sintéticos", value=True, key="observatorio_sinteticos")

    datos = barreras if filtro == "Todos" else barreras[barreras["distrito"] == filtro]
    if not incluir:
        datos = datos[datos["origen"] != "sintetico"]

    sinteticas = int((datos["origen"] == "sintetico").sum())
    sin_alternativa = datos.loc[datos["motivo"].isin(MOTIVOS_SIN_ALTERNATIVA), "busqueda_id"].nunique()
    total, sin_opcion, reales, ejemplo = st.columns(4)
    total.metric("Barreras registradas", len(datos))
    sin_opcion.metric(
        "Búsquedas sin alternativa viable",
        sin_alternativa,
        help="Búsquedas sin recurso registrado o en las que ninguna opción cumple lo que la persona necesita.",
    )
    reales.metric("Registros reales", len(datos) - sinteticas)
    ejemplo.metric("Registros sintéticos", sinteticas)
    if sinteticas:
        st.warning(f"{sinteticas} de {len(datos)} registros son sintéticos: sirven para mostrar el tablero, no son evidencia.", icon="⚠️")

    if datos.empty:
        st.info("Todavía no hay barreras registradas con estos filtros.")
    else:
        izquierda, derecha = st.columns(2)
        with izquierda:
            mostrar_grafico("Por ámbito", datos, "ambito", ETIQUETAS_AMBITO)
        with derecha:
            mostrar_grafico("Por dimensión", datos, "dimension", ETIQUETAS_DIMENSION)
        mostrar_grafico("Por distrito", datos, "distrito", {})
        with st.expander("Ver los datos en tabla"):
            tabla = datos.drop(columns="busqueda_id").assign(
                ambito=datos["ambito"].map(lambda v: ETIQUETAS_AMBITO.get(v, v)),
                dimension=datos["dimension"].map(lambda v: ETIQUETAS_DIMENSION.get(v, v)),
                tipo_necesidad=datos["tipo_necesidad"].map(lambda v: ETIQUETAS_NECESIDAD.get(v, v)),
                motivo=datos["motivo"].map(lambda v: ETIQUETAS_MOTIVO.get(v, v)),
            )
            st.dataframe(tabla, hide_index=True, width="stretch")

    st.subheader("Mapa de recursos")
    con_coordenadas = recursos[recursos["lat"].notna() & recursos["lon"].notna()]
    visibles = con_coordenadas if filtro == "Todos" else con_coordenadas[con_coordenadas["distrito"] == filtro]
    st.caption(
        "Las coordenadas son aproximadas y aún no están verificadas. "
        f"{len(recursos) - len(con_coordenadas)} recurso(s) telefónico(s) o con sede fuera del distrito no aparecen en el mapa."
    )
    st_folium(
        mapa_recursos(visibles, filtro),
        height=460,
        use_container_width=True,
        returned_objects=[],
        key=f"mapa_recursos_{filtro}",
    )


def main() -> None:
    st.set_page_config(page_title=NOMBRE_APP, page_icon="🤝", layout="wide")
    st.markdown(ESTILOS + estilos_tarjetas(), unsafe_allow_html=True)
    st.markdown(
        f"""<div class="bloque-inicio"><h1>{NOMBRE_APP}</h1>
        <p>Tecnología para ciudades más justas, accesibles y cuidadoras.</p></div>""",
        unsafe_allow_html=True,
    )

    st.warning(AVISO_DEMO, icon="⚠️")

    if not RUTA_RECURSOS.exists():
        st.error("No se encontró data/recursos.csv.")
        st.stop()
    recursos = cargar_recursos(RUTA_RECURSOS, RUTA_RECURSOS.stat().st_mtime)

    st.caption(f"Modo activo: {NOMBRES_MODO[proveedor_activo()]}.")

    asistente, voces, observatorio = st.tabs(["Asistente", "Voces", "Observatorio"])
    with asistente:
        pestana_asistente(recursos)
    with voces:
        pestana_voces(recursos)
    with observatorio:
        pestana_observatorio(recursos)


if __name__ == "__main__":
    main()

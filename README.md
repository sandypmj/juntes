# Juntes nos cuidamos y construimos

**Tecnología para ciudades más justas, accesibles y cuidadoras.**

> Juntes escucha las voces del barrio, conecta a las personas con servicios y redes que realmente pueden usar, y convierte cada barrera en evidencia para construir ciudades cuidadoras.

**Demo:** _[URL pública — pendiente]_ · **Video de respaldo:** _[link — pendiente]_

---

## 1. One-liner

Conectamos a vecinas, jóvenes y personas mayores con rutas reales de acceso a derechos, servicios, cultura y redes de apoyo, mediante un asistente que evalúa siete dimensiones de accesibilidad y un mapa construido con las voces del barrio.

## 2. Founder

**Sandy Patricia Martínez Jara** — socióloga, docente e investigadora

<img src="docs/founder.jpg" alt="Sandy Patricia Martínez Jara" width="280">

> Más de 14 años conectando políticas públicas, territorio y evidencia para que los derechos lleguen a las personas en su diversidad.

**Por qué soy la persona indicada.** He trabajado en el Estado, la sociedad civil y la cooperación internacional en América Latina, diseñando y fortaleciendo políticas e intervenciones, generando evidencia y articulando gobiernos, instituciones y organizaciones comunitarias, desde una perspectiva de género, interseccionalidad, derechos humanos y diversidad. Conozco desde adentro cómo se formulan los planes que Juntes alimenta y cómo se viven las barreras en los barrios. Hoy sumo la ciencia de datos para transformar información en evidencia útil y visibilizar desigualdades.

**Capacidades que traigo**

- **Estado y políticas públicas:** diseño, implementación y evaluación.
- **Derechos humanos y diversidad:** género e interseccionalidad.
- **Territorio y articulación:** gobiernos, instituciones y organizaciones comunitarias.
- **Conocimiento y formación:** investigación aplicada, gestión del conocimiento y desarrollo de capacidades.
- **Ciencia de datos:** transformación de información en evidencia para la acción.

**Cómo cubro cada rol con agentes de IA**

| Rol | Cómo lo cubro |
| --- | --- |
| Producto | Mi experiencia en políticas públicas y territorio, y las conversaciones con usuarias |
| Ingeniería | Claude Code como co-founder técnico; yo defino la lógica de las siete dimensiones y reviso cada parte del código |
| Diseño | Iteración rápida con Claude Code y pruebas con personas usuarias |
| Ventas | Mi red en gobiernos locales, sociedad civil y consultoría social |

*Juntes es mi apuesta por conectar conocimiento, tecnología y acción para construir ciudades más justas, accesibles y cuidadoras.*

## 3. Problema

**Quién lo sufre.** Mujeres, niñas, jóvenes, personas mayores, personas con discapacidad, migrantes y personas LGTBIQ+ de barrios populares de Lima que necesitan acceder a servicios de protección, salud, cultura o cuidado. Y los equipos municipales que deben diagnosticar esas barreras para sus planes.

**El problema.** No basta con que un servicio exista. Muchas veces falla en una condición concreta: cuesta, queda lejos, no tiene rampa, pide un requisito imposible, no atiende en quechua o el camino es inseguro de noche. Nadie mide cuál de esas condiciones falla.

**Cómo se resuelve hoy.** Directorios en PDF desactualizados, preguntar por WhatsApp a conocidas, talleres participativos en papelógrafos que nadie sistematiza, diagnósticos que tardan meses.

**Cuánto cuesta.** Tiempo perdido buscando en sitios oficiales incompletos o desactualizados, derivaciones a líneas con listas de espera y, muchas veces, el abandono de la búsqueda: el derecho existe, pero no se ejerce.

**Evidencia.** Notas de 3 conversaciones con usuarias potenciales en [`docs/research/`](docs/research/):

1. Profesional con experiencia de trabajo en Villa El Salvador: "Al tener conocimiento de los derechos y los servicios disponibles de manera clara puede abrir un gran abanico de oportunidades". [Entrevista 1](docs/research/entrevista_01.md)
2. Profesional tester en Argentina: "no sabía a dónde acudir". [Entrevista 2](docs/research/entrevista_02.md)
3. [Pendiente: tercera conversación]

## 4. Solución e insight

**Qué construí.** Una plataforma con dos puertas de entrada y una base territorial común:

- **Asistente de rutas:** la persona cuenta su necesidad y recibe dos o tres alternativas viables, con un semáforo de siete dimensiones de accesibilidad y la explicación de cada barrera.
- **Voces que conectan y construyen:** relatos de voz sobre el barrio (miedo, cuidado, cultura, memoria, verde, accesibilidad) que se transcriben en local y se convierten en un mapa con capas y en una ruta sonora con la historia de las mujeres del barrio.
- **Observatorio de barreras:** junta lo que no tuvo solución y lo convierte en evidencia por zona, ámbito y dimensión.

**Las siete dimensiones de accesibilidad**

| Dimensión | Pregunta |
| --- | --- |
| Económica | ¿Puede pagar el servicio y llegar hasta él? |
| Física | ¿Puede ingresar y desplazarse en el espacio? |
| Comunicacional | ¿Puede comprender y utilizar la información? |
| Institucional | ¿Conoce los requisitos y puede completar el procedimiento? |
| Seguridad y no discriminación | ¿Puede acceder sin exponerse a violencia o trato discriminatorio? |
| Disponibilidad territorial | ¿Hay una alternativa razonablemente próxima y operativa? |
| Pertinencia cultural | ¿La atención considera idioma, contexto y particularidades culturales? |

**Cinco ámbitos + memoria:** acceso a derechos y protección · movilidad y seguridad · accesibilidad e inclusión · cultura, educación y recreación · redes comunitarias y cuidados · memoria y representación (transversal).

**El insight.** Una barrera es un desajuste entre lo que una persona necesita y las condiciones reales de su entorno. Los servicios existen pero no llegan, y la memoria de quienes sostienen el barrio no aparece en ningún mapa. Inspirada en el urbanismo feminista del Col·lectiu Punt 6, Juntes lleva la auditoría de la ciudad cuidadora a escala: con voz, de forma continua y con una alternativa para cada persona.

## 5. Why now

Hace tres años, transcribir y codificar cientos de relatos costaba meses. Hoy Whisper transcribe el audio en local, sin que la grabación salga de la computadora, y un LLM estructura cada relato o consulta en segundos y por centavos. Cuando hay clave de API, el texto de consultas y relatos se envía a la API de Anthropic; sin clave, ese texto no sale de la computadora.

## 6. Demo

**URL:** _[pendiente]_

**Cómo correrlo en local**

Después de crear el archivo `.env` con `copy`, agrega tu clave de API en ese archivo antes de ejecutar `streamlit run`.

```bash
git clone https://github.com/sandypmj/juntes.git
cd juntes
pip install -r requirements.txt
copy .env.example .env
streamlit run app/app.py
```

**Capturas del flujo principal** (en `docs/`):

1. _[Voces: relato en el mapa]_
2. _[Asistente: alternativas con semáforo]_
3. _[Observatorio de barreras]_

**Arquitectura:** _[diagrama en `docs/arquitectura.png`]_

```
Audio / texto ─► Whisper (local) ─► LLM con salida estructurada ─► Base territorial
                                                                    (recursos.csv + relatos)
                                                                          │
                     ┌────────────────────────────┬────────────────────────┤
                     ▼                            ▼                        ▼
            Alternativas viables         Mapa de voces y memoria     Observatorio de barreras
              (semáforo 7D)              (Folium, ruta sonora)          (dashboard)
```

**Modelos y APIs, y por qué**

- **Whisper en local:** el audio es sensible, por eso se transcribe en la computadora y no se envía a ningún servicio.
- **LLM con salidas estructuradas:** clasifica relatos y consultas en ámbito, dimensión, lugar y barrera con un esquema fijo, para poder agregarlos. Cuando hay clave de API, el texto de consultas y relatos se envía a la API de Anthropic; sin clave, la app usa un respaldo por palabras clave y ese texto no sale de la computadora.
- **Folium:** mapa con capas, liviano y sin costo.
- **Texto a voz (opcional):** ruta sonora con voz sintética cuando la persona prefiere no ser reconocida.

## 7. Modelo de negocio

Gratis para la comunidad. Pagan quienes obtienen valor institucional. La cooperación es un complemento, nunca la base.

| Plan | Para quién | Qué recibe | Precio (hipótesis) |
| --- | --- | --- | --- |
| Comunidad | Personas, ollas comunes, colectivos | Asistente, mapa, relatos, rutas sonoras | Gratis |
| Organizaciones | ONG, colegios, centros culturales, universidades | Panel de su territorio, reportes, ruta sonora a medida | S/ 100 al mes o S/ 1,500 por ruta |
| Institucional | Consultoras, empresas, inmobiliarias, municipalidades | Diagnóstico participativo con enfoque de género, observatorio, informe anexable | Desde S/ 12,000 por proyecto |

**Fuentes de ingreso, de mayor a menor peso:** consultoras y empresas (líneas base sociales y participación ciudadana) · organizaciones · pilotos municipales · cooperación y fondos concursables como complemento (máximo un tercio del ingreso).

**Costo por usuario:** transcripción local (casi cero), LLM a centavos por relato o consulta, hosting gratuito al inicio. El costo principal es la facilitación en campo. _[Completar con el cálculo de tokens real.]_

## 8. Herramientas del curso

| Herramienta | Sesión | Dónde está en el repo |
| --- | --- | --- |
| Whisper (voz a texto) | 13 | `ai/transcribir.py` |
| LLM con salidas estructuradas | 08 | `ai/estructurar.py` |
| Mapas con Folium | 06 | `app/app.py` (pestañas Voces y Observatorio) |
| Dashboard | 05 | `app/app.py` (pestaña Observatorio) |
| Texto a voz (opcional) | 15 | Aún no implementado |

## 9. Qué hizo el agente

_[Completar al final: qué archivos generó Claude Code, qué partes ajusté yo y qué decisiones tomé.]_

## Ética y cuidados

- Consentimiento grabado al inicio de cada relato.
- Anonimización de personas vivas; nunca se ubican viviendas.
- No se piden relatos de violencia en detalle.
- Si una consulta sugiere riesgo, la Línea 100 y el 105 aparecen primero.
- El asistente orienta; no reemplaza la atención ni da asesoría legal.
- Cada dato indica si está verificado, reportado por la comunidad o sin verificar.
- Los datos del demo son públicos, propios o sintéticos (marcados como tales).
- El audio se transcribe en local. Cuando hay clave de API, el texto de consultas y relatos se envía a la API de Anthropic; sin clave, ese texto no sale de la computadora.
- Los relatos y barreras reales no se suben al repositorio público; solo se publican los ejemplos sintéticos.

## Licencia

MIT

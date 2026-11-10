# Pruebas con usuarias de la app publicada

- **Fecha:** 10 de noviembre de 2026
- **Versión probada:** https://juntes-cuidamos.streamlit.app (con Google Gemini)
- **Modalidad:** a distancia, por WhatsApp. Cada persona usó la app por su cuenta y envió sus comentarios por escrito.
- **Privacidad:** no registramos nombres; solo el rol de cada persona.

## Prueba 1

**Perfil.** Especialista en género y gestión pública, con años de experiencia en Villa El Salvador. Hoy es consultora y acompaña una buena práctica de articulación entre el CEM y las comisarías en Ventanilla.

**Respuestas textuales**

> "Se entiende, aunque la falta de datos limita la búsqueda. Habría que ampliar las referencias sobre las necesidades; por ejemplo, escribí guardería y no me apareció información sobre los Wawa Wasi."

> "Puse cuidado de ancianos y no me brindó información, por ejemplo, de las organizaciones de adultos mayores o el servicio de adultos mayores que existe en Villa El Salvador, que es representativo."

> "Además existen comedores de adultos mayores."

> "También incluir lo de INABIF."

## Prueba 2

**Perfil.** Gestora cultural con perspectiva de género y madre de dos niños en edad escolar. Evaluó la app desde su experiencia en el sector cultural y en servicios para infancias.

**Qué hizo.** Buscó "biblioteca", "talleres" y "teatro" en Villa El Salvador. Las tres búsquedas dieron alternativas.

**Respuestas textuales**

> "La herramienta sirve para encontrar lugares dentro de tu distrito (aunque ahora solo estén activados los de Villa El Salvador y Ventanilla), un guía para sentirte seguros e informados."

> "En cuanto a las alternativas, me aparecen útiles. Podrían agregar: fotos del lugar, el número de teléfono y el link que te lleve a la página de Facebook o Instagram, así como la dirección y el mapa."

> "Creo que esta herramienta les sería útil a las familias, a las cuidadoras y a cualquier persona que necesita información específica de su distrito o de otros."

> "Usé las palabras biblioteca, talleres y teatro; todas tuvieron alternativas bajo el distrito requerido."

## Hallazgos

**Lo que funcionó**

- **Comprensión del propósito.** Las dos usuarias entendieron para qué sirve la app sin explicación previa: encontrar servicios del propio distrito y sentirse "seguros e informados".
- **Búsquedas culturales con resultados.** Biblioteca, talleres y teatro devolvieron alternativas en el distrito elegido.

**Lo que faltó**

- **Cuidados para la primera infancia.** "Guardería" no llevó a Cuna Más (antes Wawa Wasi), que es el servicio que la gente conoce por ese nombre.
- **Cuidados para personas adultas mayores.** "Cuidado de ancianos" no llevó al CIAM, a los comedores ni a las organizaciones de personas adultas mayores. En Villa El Salvador el CIAM es un servicio representativo.
- **Programas nacionales con presencia en Lima.** Faltaba el INABIF.
- **Datos de contacto.** Las alternativas no mostraban dirección, teléfono, redes sociales ni cómo llegar.

**A quién le sirve**

- Familias.
- Cuidadoras.
- Personas de otros distritos que necesitan información específica de su zona.

## Qué cambiamos

Implementado el mismo día, 10 de noviembre de 2026:

1. **Nuevos recursos** en `data/recursos.csv`: Cuna Más (cuidado diurno) y el CIAM en Villa El Salvador y Ventanilla, el INABIF como recurso de Lima, y un comedor de personas adultas mayores en cada distrito, marcado como ejemplo sintético. Las coordenadas son aproximadas y las dimensiones que no pudimos confirmar quedaron por verificar.
2. **Datos de contacto:** nuevas columnas `direccion`, `telefono` y `redes`, llenadas solo con datos de fuentes oficiales (gob.pe y webs institucionales). Lo demás dice "por verificar".
3. **Mejor comprensión de las consultas**, tanto por palabras clave como en las instrucciones a Gemini. Guardería, wawa wasi, cuna, nido, cuidado infantil y niños pequeños llevan a Cuna Más. Anciano, adulto mayor, tercera edad, abuelos y persona mayor llevan al CIAM, a los comedores y a las organizaciones de personas adultas mayores. Si la IA deja una de estas consultas como genérica, las palabras clave deciden.
4. **En el asistente:**
   - Cada alternativa muestra dirección, teléfono (con enlace para llamar) y web o redes cuando existen, y un botón "Cómo llegar" que abre Google Maps. Si la ubicación no está verificada, la app avisa que es aproximada.
   - Cuando no hay un recurso adecuado, la app lo dice ("Todavía no tenemos este servicio en el directorio") y lo registra en el Observatorio como barrera sin recurso.

## Próximos pasos

- **Fotos de los lugares:** antes de publicarlas pediremos permiso a las organizaciones y servicios.
- **Ampliar a otros distritos,** como pidió la segunda usuaria.
- **Verificar en campo** las sedes de Cuna Más y del CIAM en cada distrito, y sumar organizaciones reales de personas adultas mayores.

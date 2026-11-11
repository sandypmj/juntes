# Pruebas con personas usuarias de la app publicada

- **Fecha:** 10 de noviembre de 2026 (las tres pruebas)
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

Después envió dos comentarios más:

> "También usé la palabra paraderos seguros, pero no hubo opciones."

> "No sentí confusión al usar la herramienta como tal, sino que todo era muy plano (eso es un tema de diagramación); las imágenes ayudan más a socializar la información."

## Prueba 3

**Perfil.** Sociólogo con perspectiva de género que ha trabajado en Lima y en Buenos Aires.

**Respuestas textuales**

> "Es práctica y útil."

> "Se entiende muy bien, son opciones útiles. Imagino que se ampliarán las opciones de distrito."

> "Sí he necesitado encontrar servicios públicos, pero me han sido muy accesibles, principalmente por el dominio de las herramientas digitales. Comprendo que un obstáculo para muchas personas puede ser que las aplicaciones o las plataformas no sean muy accesibles."

## Hallazgos

**Lo que funcionó**

- **Comprensión del propósito.** Las dos usuarias entendieron para qué sirve la app sin explicación previa: encontrar servicios del propio distrito y sentirse "seguros e informados". La segunda dijo que no sintió confusión al usarla.
- **Búsquedas culturales con resultados.** Biblioteca, talleres y teatro devolvieron alternativas en el distrito elegido.

**Lo que faltó**

- **Cuidados para la primera infancia.** "Guardería" no llevó a Cuna Más (antes Wawa Wasi), que es el servicio que la gente conoce por ese nombre.
- **Cuidados para personas adultas mayores.** "Cuidado de ancianos" no llevó al CIAM, a los comedores ni a las organizaciones de personas adultas mayores. En Villa El Salvador el CIAM es un servicio representativo.
- **Programas nacionales con presencia en Lima.** Faltaba el INABIF.
- **Datos de contacto.** Las alternativas no mostraban dirección, teléfono, redes sociales ni cómo llegar.
- **Movilidad y seguridad.** "Paraderos seguros" no dio opciones. No hay un servicio que garantice un paradero seguro, pero la app tampoco mostraba lo que sí tiene: los relatos de las vecinas, los contactos de emergencia y la posibilidad de contar la propia experiencia.
- **Diseño plano.** La información se entendía, pero todo se veía igual. Las imágenes ayudan a socializar la información.

**Lo que confirmó la tercera prueba**

- **Comprensión y utilidad confirmadas.** La app "se entiende muy bien" y las opciones son útiles.
- **Ampliar distritos.** Varias pruebas piden más distritos, además de Villa El Salvador y Ventanilla.
- **La brecha digital es una barrera real.** Corresponde a la dimensión comunicacional: quien no domina las herramientas digitales tiene más difícil encontrar servicios, incluso usando Juntes.

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

Implementado después de los dos comentarios adicionales:

5. **Movilidad y seguridad.** Las consultas sobre paraderos, transporte, caminos, iluminación o sentirse segura en la calle ahora muestran:
   - "Lo que cuentan las vecinas": los relatos de la pestaña Voces del distrito en las capas miedo y seguridad.
   - Contactos útiles: 105, Línea 100 y el serenazgo o la central de emergencias municipal (por verificar).
   - Una invitación a contar la propia experiencia en Voces.

   Cada una de estas búsquedas queda registrada en el Observatorio como barrera de movilidad y seguridad. Sumamos la capa "seguridad" al mapa de Voces y dos relatos sintéticos sobre paraderos: uno inseguro por falta de luz y otro seguro por la presencia de comercio.
6. **Diseño más visual, sin fotos reales:**
   - Un ícono por ámbito: 🛡️ derechos y protección, 🚌 movilidad y seguridad, ♿ accesibilidad e inclusión, 🎭 cultura y recreación, 🤝 redes y cuidados, 🕯️ memoria.
   - Cada alternativa es una tarjeta con fondo suave y borde del color de su ámbito.
   - El semáforo de las siete dimensiones ahora tiene círculos de color, con símbolo (✓, ½, ✕, ?) y nombre corto. El símbolo permite leerlo sin distinguir colores.
   - Cuatro botones de ejemplo de búsqueda llenan el cuadro de texto.
   - Los colores mantienen buen contraste con el texto.

## Próximos pasos

- **Fotos de los lugares:** antes de publicarlas pediremos permiso a las organizaciones y servicios.
- **Ampliar a otros distritos,** como pidieron la segunda y la tercera prueba.
- **Lenguaje simple y relatos por voz,** para que escribir no sea una condición para usar la app.
- **Acompañamiento de facilitadoras y organizaciones comunitarias** para quienes no usan apps, como pidió la tercera prueba al señalar la brecha digital.
- **Verificar en campo** las sedes de Cuna Más y del CIAM en cada distrito, y sumar organizaciones reales de personas adultas mayores.

---
name: senda-reels
description: Reglas obligatorias para crear reels o vídeos de Senda Natural con La Investigadora (voz en off, escenas que ilustran el guion, subtítulos llamativos). Úsala SIEMPRE que se vaya a producir, rehacer o revisar un reel/vídeo, antes de generar nada.
---

# Reels y vídeos de Senda Natural

Reglas de la usuaria. No negociables. Aplican a todo reel o vídeo, cada día.

## 0. Look cinematográfico, como una serie de Netflix (obligatorio)
- Todo plano debe verse de cine: lentes anamórficas, poca profundidad de campo, iluminación de contraste suave y dirigida, grading cálido con negros ricos, grano de película sutil, cámara con movimiento motivado (dolly, push-in, travelling, handheld suave). Nunca aspecto de vídeo corporativo, stock ni "IA plana".
- Incluir siempre en los prompts: "cinematic, Netflix series look, anamorphic lens, shallow depth of field, film grain, rich color grading, motivated camera movement".
- Escenarios con carácter (no laboratorio genérico blanco): luz de ventana, texturas, atrezo con sentido.

## 1. La Investigadora siempre en movimiento
- Nunca fija, nunca solo mirando a cámara todo el rato. Variar plano y acción: de pie, caminando, gesticulando con las manos, señalando, mirando un objeto, acercándose a cámara, cambiando de plano medio a primer plano.
- Un mismo plano de ella no dura más de unos 5-6 s seguidos; alternar con las escenas del punto 2.
- NUNCA va de blanco ni con bata de laboratorio. Tiene su outfit propio, el del Element/imagen de referencia: no describirlo en el prompt de otra forma, escribir "keep the exact outfit, hair and face of the start image; no white lab coat".
- Mantener su identidad con el Element de Higgsfield "La Investigadora" (1ca4f2da-725e-48a2-b996-fa83898574cb) y el Soul 411e8819-11a2-447f-b8dc-305e70b7c679.

## 2. Alternar lo que dice con lo que se ve, con la lógica del guion
- Dividir el guion por secciones (HOOK, METÁFORA, PIVOTE, HERIDA, CTA). Lo que se ve en cada tramo debe ilustrar literalmente lo que se dice en ese tramo.
- Ella aparece hablando en el gancho, el pivote y el cierre. La metáfora y la herida se ilustran con escenas (coche en el taller, hucha, espejo...) mientras suena la voz en off.
- Nunca poner imágenes que no tengan relación con la frase (error de los días 2 y 4 originales).

## 3. Voz siempre de La Investigadora diciendo el guion
- Voz ElevenLabs `iuCOanGou5VLdjsVzuSj`, modelo `eleven_multilingual_v2`, flow `weime5DY6BKajeZdTu6M`. Siempre la misma voz, el guion completo, sin recortar.
- Cuando ella aparece hablando, sus labios van sincronizados con la voz: Seedance 2.5 con `start_image` (Element) + `audio_references` (tramo de voz de 2-30 s).
- Escribir como se pronuncia: siglas desarrolladas ("ultravioleta", no "UV"), números en letra ("veinticinco"), CTA en imperativo ("Guarda este vídeo y compártelo").
- Verificar la locución con `video_analyze` (Magnific) antes de proponer: transcripción por tramos, titubeos, voz coherente entre tramos, final no cortado.

## 4. Subtítulos llamativos (no planos)
- Todo reel lleva subtítulos grabados en el vídeo: palabra a palabra o frase corta, grandes, tipografía gruesa, con contorno o sombra, palabra clave resaltada en dorado #D4AF7F sobre texto crema #FAF6F0, zona segura (no tapar cara ni los botones de Instagram).
- NO usar subtítulos grises ni blancos simples de una sola línea.
- La generación de subtítulos es un paso OBLIGATORIO de todo reel y se hace con OpusClip (sección 10): se aplican a la versión final montada, con voz, antes de importar a CloudFront y de pedir el visto bueno. Nunca pasar un reel a `aprobado` sin ellos. Si OpusClip fallara, avisar a la usuaria y usar CapCut como plan B.

## 5. Proceso (resumen)
1. Dividir guion en tramos y decidir cuáles son "ella habla" y cuáles "ilustración + voz en off".
2. Generar voz por tramos (ElevenLabs), importar a Higgsfield (`media_import_url`).
3. Generar tomas con Seedance 2.5 9:16 720p: habladas (con audio de referencia) e ilustrativas (`generate_audio:false`).
4. Copiar cada mp4 a Supabase bucket `reels` (función `copyvid`), subir a Magnific (`creations_request_upload` + función `relay` + `creations_finalize_upload`), mezclar la voz en las ilustrativas (`video_audio_mix`, `muteVideo:true`), unir con `video_concatenate`.
5. Añadir subtítulos llamativos (punto 4).
6. Verificar con `video_analyze`, importar a Higgsfield y enseñar a la usuaria. NUNCA guardar en `content_calendar` ni dejar en `aprobado` sin su visto bueno.
7. Guion, caption y notas del día deben coincidir con lo que dice la locución.

## 6. Publicación (n8n "Diaria-IG")
- Aprobar antes de las 18:00 UTC (19:00 España en invierno, 20:00 en verano) o no sale ese día.
- El caption nunca usa `tema` ni hashtags con "rutina".

## 7. Copy (caption) correcto: siempre el del guion hablado
- El copy de Instagram (`carousel_caption` en `content_calendar`) debe salir del guion que dice la voz del vídeo final: el gancho, la idea central y el CTA tal como se oyen. Nunca un copy antiguo, genérico ni de otro día.
- Si la voz se ha suavizado o cambiado (p. ej. sin cifras ni plazos), el copy se cambia igual.
- Estructura: gancho + idea central en frases cortas, CTA en imperativo y firma "Tu asesora de piel · Senda Natural". Sin `tema`, sin hashtags de "rutina", sin "Ringana", sin promesas de resultado.
- Antes de pasar un reel a `listo` o `aprobado`, comprobar con SQL que `carousel_caption` no está vacío y coincide con la locución. Sin copy correcto, no se aprueba.
- Si un reel ya publicado sale con copy erróneo, avisar a la usuaria y darle el texto correcto para editarlo en Instagram.

## 8. Comprobar de dónde coge el copy el workflow (lección del día 4)
- Tener `carousel_caption` bien escrito no basta: el nodo "IG – Crear Reel" de n8n debe leerlo. Su campo `caption` ha de ser `{{ $('Supabase – Buscar Aprobados').item.json.carousel_caption }}` (o el equivalente que llegue desde "Set – Datos Publicación"), nunca `guion`, `tema` ni un texto fijo.
- Antes de aprobar un reel: (1) comparar el copy de `carousel_caption` con la locución, (2) pedir a la usuaria captura del nodo o confirmar la expresión si no está verificada, (3) tras publicar, comprobar el copy real del post.
- Si sale mal: NO eliminar el reel; se corrige con "Editar" en Instagram y se arregla el nodo antes de la siguiente publicación.
- El JSON `n8n/senda-natural-produccion.json` del repositorio está desactualizado respecto al workflow real; no fiarse de él para esto.

## 9. La Investigadora no tiene que salir siempre
- No todos los reels llevan a La Investigadora en pantalla. Se pueden hacer reels enteros sin ella, solo con su voz en off diciendo el guion (regla 3 sigue vigente: la voz es siempre suya).
- Alternar entre reels con ella y reels sin ella para dar variedad al perfil; no repetir el mismo formato dos días seguidos.
- En los reels sin ella, subir el misterio y la atmósfera: planos cerrados de objetos y manos, sombras, niebla, luz dirigida, texturas, contraluces, movimientos de cámara lentos, detalles simbólicos que ilustren la metáfora del guion. Mantener el look cinematográfico de serie de Netflix (regla 0) y las imágenes alineadas con lo que dice la voz (regla 2).
- Sin ella no hay sincronía labial: toda la narración va como voz en off sobre las escenas (`generate_audio:false` + `video_audio_mix`), con subtítulos llamativos (regla 4) y copy correcto (regla 7).
- Cuidar manos y cuerpos si aparecen personas: anatomía correcta, sin deformaciones.

## 10. Subtítulos con OpusClip (conector "AI Producer by OpusClip", validado el 31-oct)
- Los subtítulos los grabo yo con OpusClip; la usuaria ya lo conectó. CapCut queda solo como plan B manual.
- Dominios que deben estar permitidos en la red del entorno: `producer.opus.pro`, `*.opuslab.ai`, `storage.googleapis.com`, `upload.higgsfield.ai`, `ak-data.magnific.com`.
- Flujo: (1) `start_project_from_attachment` con la URL de CloudFront del reel; (2) `get_task` hasta `done`; (3) `build_captions` con `accent:#D4AF7F`, `font:heavy-hitter`, `position:68`, `placement:fixed`, `user_request:"subtitulos llamativos, no planos"`; (4) añadir el `host_div` devuelto al `index.html` del proyecto (quitar el `<link>` a `styles/slots.css`, que no existe) y `commit_workspace` con `expected_files` (index.html con `content` + los ficheros devueltos con sha256), `authoring:false` o `finish_project`; (5) `start_export`, `get_task`, `get_export_url`; (6) descargar con curl usando cookie jar (`-L -c jar -b jar`; el enlace es de un solo uso y redirige a `opus-lab.cdn.opuslab.ai`); (7) subir a Higgsfield (`media_upload` + PUT + `media_confirm`) para obtener la URL de CloudFront y a Magnific para `video_analyze`; (8) guardar en `video_url` y `carousel_caption`, y esperar el visto bueno de la usuaria antes de `aprobado`.
- Resultado aceptado por la usuaria ("ha salido perfecto"): texto blanco semibold con palabra clave más grande en beige dorado, a la altura del torso, sin tapar boca ni ojos.
- No pasar a `aprobado` un reel sin subtítulos.

## 11. Enlace de la bio
- Cuando un copy, guion, subtítulo o locución mencione el enlace de la bio, escribir siempre **www.sendanatural.net** (nunca app.sendanatural.lat). Vale para reels, carruseles, TikTok y YouTube.
- Los reels con CTA "link en bio" dicen solo "Link en bio" en voz y subtítulo; el dominio completo va en el copy de Instagram.

## 12. Portada del reel (decisión de la usuaria, 8-nov)
- Todo reel lleva una portada propia para el feed. NO usar el primer fotograma (casi siempre La Investigadora, que llama poco la atención).
- Formato 9:16 (1080x1920) con el contenido clave en la zona central (el grid del perfil recorta a 3:4). Imagen cinematográfica y simbólica de la metáfora del guion (objetos, manos, luz dorada, sin rostro fijo mirando a cámara) + el gancho en tipografía serif cursiva, crema #EFE3CF y dorado #D4AF7F. Sin otros textos.
- Cómo se hace: imagen con `generate_image` (gpt_image_2_6, 9:16) y una segunda pasada con la imagen de referencia pidiendo el texto exacto (funciona bien con acentos). Canva no sirve: `resize-design` agotó la cuota gratuita.
- Se guarda importando a Higgsfield (`media_import_url`) y la URL de CloudFront `.png` va en `content_calendar.portada_url`. n8n debe mandarla en `cover_url` del nodo "IG – Crear Reel".
- Comprobar siempre el texto de la portada letra por letra antes de guardarla.


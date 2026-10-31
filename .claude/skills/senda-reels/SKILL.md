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
- Si no hay herramienta para grabarlos, decirlo claramente a la usuaria antes de dar el vídeo por terminado y no pasarlo a `aprobado` sin ellos.

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

# Senda Natural: reglas de contenido y patron de assets

Memoria del proyecto. Aplica a todo el contenido de RRSS (carruseles, reels, stories, foto quote).

## Compliance (no negociable)
- NUNCA mencionar "Ringana" en material de cara al publico.
- NUNCA usar nombres oficiales de producto en copy publico (captions, slides, `tema`, `carousel_tema`). Usar descripcion generica ("tu crema ideal", "la crema ligera"). El nombre oficial solo en `notas` (uso interno).
- NUNCA testimonios inventados (nombre + edad + frase). Sin testimonio real y autorizado, reformular como criterio o necesidad sin atribucion. Ejemplo valido: "Lo que casi todas buscamos: una crema que no pese y que hidrate de verdad."
- Firma siempre "Senda Natural". Nunca el nombre personal de Esther.
- CTAs segun el documento de cada dia: A = Conversion (reels: diagnostico en app.sendanatural.lat), B = Engagement (carruseles: comentarios/guardados/shares), C = Follow (stories: seguir + DM automatico que lleva a la app). Nunca checkout ni venta automatica.
- Nunca la palabra "rutina" ni lenguaje de red de ventas. Cada escena lleva etiqueta de veracidad (real / compuesta / ilustrativa); una escena ilustrativa nunca se presenta como testimonio.

## FUENTE DE VERDAD DE LOS GUIONES (leer antes de tocar contenido)
- Google Drive, carpeta "OFERTAS IRRESISTIBLES · Premisa Emocional" (id 1gdFGwK-gr7Dxz0-tpbHJTT-28aSFeBiT), con las instrucciones "premisa emocional" y los avatares.
- Guiones: carpeta "Guiones · Nueva Premisa Emocional" (id 1e2mREy4X0NewguInNay79mbWDLvJN3qz): un documento por dia ("Dia 0N · Avatar · Formato · Nueva Premisa") y "Guiones Semana 1".
- NO usar `Guiones_365_SendaNatural.xlsx`: es el plan antiguo y no coincide.
- IGNORAR por completo la carpeta de Drive "Bebes y Ninos · Avatares 77-81" (id 17GhRS9hagfJgrKIUYMbsHkig0VqyX_u1): no se usa por el momento. No leerla, no usarla en guiones ni en el calendario.
- Trabajar sin pedir permiso para crear contenido: el usuario ya delego la creacion. Solo preguntar si la decision es suya (formato, publicar o no).
- Estructura de cada documento: Avatar, Grupo, Problema, Pilar, Tipo CTA, Producto, Presentadora, Formato; secciones del guion, CAPTION y NOTAS DE PRODUCCION/DISENO.
- Carrusel segun el documento: 6 slides, 1:1 (1080x1080), Cormorant Garamond titulos + DM Sans cuerpo, fondo #0E0D0A, texto #D4AF7F, firma "Tu asesora de piel · Senda Natural".
- Todos los guiones de `content_calendar` empiezan con cabecera numerada `DÍA 0N · PERSONAJE · Formato` (dias 1-14 ya ajustados a la Nueva Premisa). Cada dia nuevo debe seguir ese formato: HOOK/ESCENA/... o STORY/QUOTE segun formato, `tema` = `PERSONAJE · herida: ...`, `notas` con producto interno + veracidad + CTA + viralidad.
- Semana 2 (avatares): 8 Isabella (carrusel), 9 Valentina (reel), 10 Paula (carrusel), 11 Andrea (reel), 12 Mercedes (stories), 13 Amparo (foto quote), 14 Teresa (reel). Semana 3 en adelante: seguir con los avatares de las carpetas Set Light / Medium / Rich, nunca Bebes y Ninos.
- Avatares Light/Medium/Rich son solo internos.
- Claims de producto sujetos a las GC Rules (por ejemplo "sin silicones" hay que confirmarlo antes de publicar).

## Formato y marca
- Carrusel y foto quote: 1080x1080 (1:1, segun los documentos de Drive). Stories: 1080x1920. Reels: 9:16 video. NUNCA 16:9 apaisado (Instagram lo muestra diminuto).
- Exportar siempre a JPG (calidad 90).
- Icono de la hoja en TODAS las piezas: abajo a la izquierda, 80 px, 75 % de opacidad. En la ultima pagina: icono grande a la derecha + firma "Senda Natural". Asset en Canva: `MAHZYEEVm_I` (SVG vectorial servido por la edge function `brand-icon`).
- Estilo: fondo oscuro #0E0D0A, serif cursiva dorada (#ad844a / #c2985c), cuerpo crema (#d1c0a9).
- Canva: la cuota de IA esta agotada, `create-design` falla. Partir de una copia (`copy-design` de `DAHZYAM2x3c`) y editar con `edit-design` reutilizando los elementos de texto (conservan la tipografia de marca). `add_text` usa fuente por defecto y no es de marca.

## Patron unico para subir assets a Supabase (proyecto jrovkkjxvzuzcpexdydy)
Carruseles, stories y fotos:
1. Exportar de Canva a JPG.
2. Guardar con la edge function `ingest` (descarga el JPG de Canva y lo sube bien, sin corromper bytes). Se llama desde SQL con `net.http_post` (extension `pg_net`) y la anon key en `Authorization`. Body: `{"dia": N, "urls": [...]}`; opcional `"start": k` para sustituir una sola slide.
3. Queda en bucket `carousel-images`, ruta `dia{N}/slide-000{i}.jpg`.
4. IMPORTANTE: Instagram RECHAZA las URLs de Supabase (storage directo y function `img`: error 2207083, aunque el archivo sea un JPEG valido). Solo acepta CloudFront. Por eso, tras `ingest`, importar cada slide a Higgsfield con `media_import_url` (url = `https://jrovkkjxvzuzcpexdydy.supabase.co/storage/v1/object/public/carousel-images/dia{N}/slide-000{i}.jpg`). Devuelve un `media_id`; la URL definitiva es `https://d2ol7oe51mr4n9.cloudfront.net/user_3C5cQxE1oi1XbZDKdjou8cwMYeD/<media_id>.png` (mismo CloudFront que los reels). Verificado en produccion con el dia 1: `via` = cloudfront en las 6 slides.
5. En `content_calendar` guardar esas URLs de CloudFront, en orden, en `carousel_slide_urls` (jsonb). Foto quote: la URL en `imagen_url`. Supabase queda como copia de seguridad.
6. Rellenar tambien `carousel_tema` (titulo publico sin producto), `carousel_canva_design_id` y `carousel_status = 'listo'`. `status` queda en `listo` para el flujo de aprobacion por Telegram.
Reels: `video_url` = URL de CloudFront (Higgsfield), `audio_url` = `elevenlabs:<voice_id>`.
- Los enlaces de export de Canva caducan en menos de 24 h: NUNCA guardarlos como URL definitiva.
- NUNCA subir binarios desde un nodo Code de n8n: el Buffer viaja como JSON y el archivo queda corrupto. Para URLs de Canva aun sin guardar, el nodo "Code – Subir Imagenes a Supabase" las envuelve con la function `canva-img` (solo hosts `export-download.canva.com`).
- La function `img` solo sirve rutas `dia{N}/slide-000{i}.jpg` del bucket (no usar para Instagram).
- Caption de carruseles: el nodo "Code – Crear Carrusel IG" lee `carousel_caption` de Supabase por `dia`. `tema` es un descriptor interno y NUNCA se publica.

## Instagram (workflow n8n "Diaria-IG")
- Token de Instagram Login (empieza por `IGAA`), variable n8n `INSTAGRAM_TOKEN` = `Bearer IGAA...` (con espacio). Dura 60 dias: renovar antes. Nunca pegarlo duplicado.
- Endpoint `https://graph.instagram.com/v21.0/me/...`. En el nodo de publicar, URL `{{ $json.api_base }}/media_publish` y `access_token` sin el prefijo `Bearer`.
- Los nodos Code de n8n abortan a los 60 s: crear las slides en paralelo con `Promise.all`.
- Instagram acepta JPEG y PNG, pero el archivo debe ser una imagen real servida por URL publica.

## Estado del calendario (actualizado 2-nov-2026)
- Publicados: 1 (carrusel), 2 (reel), 3 (carrusel), 4 (reel), 5 (carrusel de imagenes, 1-nov, lanzado a mano con Execute workflow), 6 (foto quote, 2-nov, salio bien con su copy).
- Aprobados: reel 7 (3-nov, GPS, sin La Investigadora), carrusel 8 (4-nov), reel 9 (5-nov, con ella) y reel 11 (7-nov, sin ella; acepto con el subtitulo "Link envio" y billetes/reloj dorado en la maleta, regenerable si ella lo pide).
- Listos: foto quote 13 (9-nov, `imagen_url`), carrusel 10.
- Pendientes: reel 14 (10-nov, con ella; guion y copy hechos, falta producir) y dia 12 (8-nov), que pasa de stories a CARRUSEL DE VIDEO (rama nueva en n8n + clips).
- Los copies (`carousel_caption`) de todos los dias 5-14 estan escritos desde la locucion/guion. Comprobar siempre que no esten vacios antes de aprobar.
- La consulta "Supabase – Buscar Aprobados" NO filtra por fecha: coge el `aprobado` con el `dia` mas bajo (`status=eq.aprobado&order=dia.asc&limit=1`). Para que una pieza salga hoy, ninguna `aprobado` con numero menor debe quedar sin publicar. Una pieza que no deba salir se deja en `listo`.

## Decisiones de formato (1-nov)
- STORIES RETIRADAS del calendario: el workflow no las soporta (caen en la rama de imagen, que publica una foto de feed y busca `imagen_url`) y las pegatinas de encuesta/SEGUIR no se pueden anadir por la API. Mezcla de formatos acordada: reel, carrusel de imagenes y carrusel de video.
- Carrusel de imagenes: base Canva `DAHZYAM2x3c` (9 paginas, 1080x1350 = 4:5, NO 1:1 como dice el doc de Drive; es el formato de los carruseles ya publicados). Copiar, editar pagina a pagina (replace_text/delete_element), exportar solo las paginas usadas (p. ej. 1-5 y 9), JPG 90. Dia 5 usa el diseno `DAHZssiMfd0`.
- Cuidado al copiar URLs firmadas de Canva a mano: un caracter distinto (p. ej. la hora en `response-expires`) da `download 403` en `ingest`; repetir solo esa slide con `"start": k`.
- Carrusel de video: Instagram lo permite (hijos VIDEO), pero n8n solo tiene rama de imagenes; hay que anadirla antes de planificarlo.

## Produccion de reels: lecciones de la semana 1-nov
- Siempre leer `.claude/skills/senda-reels/SKILL.md` primero (look cinematografico, outfit propio de La Investigadora sin bata blanca, voz suya, imagenes alineadas con el guion, copy correcto, subtitulos con OpusClip).
- Subtitulos: conector "AI Producer by OpusClip" (ya conectado). Flujo en la skill (seccion 10). Dominios de red permitidos en el entorno: `producer.opus.pro`, `*.opuslab.ai`, `storage.googleapis.com`, `upload.higgsfield.ai`, `ak-data.magnific.com`. El patron `scribble-subtitle` con acento #D4AF7F gusto a la usuaria. Revisar siempre que el texto grabado coincida con la locucion (el dia 11 salio "envio").
- `copyvid` solo acepta paths planos (`d9_s1.mp4`, sin `/`). La URL firmada de ElevenLabs caduca en 2 h: pedir una nueva con `creative_get_flow_run_status` antes de copiar.
- Seedance: pedir labios en movimiento de forma explicita; si el clip hablado sale sin labios o con la mano deformada, regenerar solo ese plano. No recortar el ultimo clip por debajo de la duracion de la voz (se corto "bio").
- El filtro de contenido de Higgsfield puede dar falsos positivos (`nsfw`) con primeros planos de piel/cara; reformular sin personas.
- Costes: un reel completo gasta mucho. Higgsfield: 2.800 creditos al inicio de la sesion, 215 tras producir reels 7, 9 y 11. Avisar a la usuaria antes de producir otro.
- Los enlaces de descarga de OpusClip son de un solo uso y redirigen a otro host: usar cookie jar (`curl -L -c jar -b jar`).

## n8n: lecciones nuevas (1-nov)
- El programador lanza a las 18:00 hora de ESPANA (17:00 UTC en invierno), aunque el nodo diga "18:00 UTC". Si se pierde esa hora, se lanza a mano con Execute workflow en el Editor (solo recoge `aprobado` con fecha de hoy).
- ARREGLADO el 1-nov y verificado el 2-nov (dia 6 publicado bien): `IG – Crear Imagen` / `IG – Publicar Imagen` mandan `access_token` SIN "Bearer" con `{{ $('Set – Datos Publicación').item.json._token.replace(/^Bearer\s*/i, '') }}`.
- `caption` de IG – Crear Imagen e IG – Crear Reel ya NO es texto fijo: lee `{{ $('Supabase – Buscar Aprobados').item.json.carousel_caption }}`. Antes la imagen usaba `{{ $json.tema }}` (descriptor interno) y el reel un texto fijo ("interes compuesto") que salio en el reel del dia 7 y hubo que borrar. Para que funcione, el `select` de la URL de "Supabase – Buscar Aprobados" incluye `carousel_caption`.
- "Execute workflow" publica DE VERDAD; para probar un nodo usar solo "Execute step" dentro del nodo. Si el nodo muestra el aviso de salida desactualizada, es normal tras cambiar parametros. Comprobar que "Pin data" no este activado.
- Despues de tocar un nodo, comprobar siempre en Instagram el copy de la primera publicacion que pase por el.
- La rama de carrusel funciona (dias 1, 3 y 5 publicados por ahi).
- El JSON de `n8n/` en el repositorio esta desactualizado respecto al workflow real: no fiarse de el.
- Confirmacion de Telegram: pendientes parse mode HTML, saltos de linea reales, hora real de publicacion "18:00 Espana / 12:00 Colombia / 11:00 Mexico" (invierno; desde el 28-mar-2027 cambia la hora de Espana). El mensaje decia 20:00 por error. El guion trae `\n` literales: convertir con `.replace(/\\n/g, '\n')` y cortar a ~900 caracteres y responder al boton (Answer Query Callback) para evitar duplicados.

## Agentes y otras plataformas
- Agentes de proyecto creados (rama `claude/senda-natural-cinematografico-xpmnqr`, PR #17): `senda-tiktok` y `senda-youtube` en `.claude/agents/`, con skills `senda-tiktok` y `senda-youtube`. Reutilizan el reel aprobado; no publican sin "aprueba". TikTok publica con las herramientas `tiktok_*` de Higgsfield (cuenta aun sin conectar). YouTube no tiene herramienta de subida conectada.
- Sesiones creadas para ellos: "Agente TikTok · Senda Natural" y "Agente YouTube · Senda Natural".
- Reglas de la usuaria vigentes: no mencionar Ringana, nada de "rutina", sin cifras/plazos inventados ("casi siempre" en vez de "cuatro de cada cinco"), firma "Tu asesora de piel · Senda Natural", guardar en `content_calendar` solo tras su visto bueno.

## Reels: proceso validado con el dia 2 (publicado 2026-10-29)
- El video de Higgsfield sale SIN audio y dura 15 s. Un reel de ~45 s se monta por ESCENAS que sigan el guion (gancho, metafora, pivote, herida, cierre) y la voz en off de ElevenLabs encima. Nunca repetir el mismo clip en bucle ni usar escenas que no encajen con lo que dice la voz.
- Seedance 2.5 (Higgsfield) genera clips de hasta 30 s; sin audio (`generate_audio:false`) para escenas, con `start_image` del Element "La Investigadora" (1ca4f2da-725e-48a2-b996-fa83898574cb) para los planos de ella. La referencia de audio de Seedance admite 2-30 s.
- Voz: ElevenLabs `eleven_multilingual_v2`, voice_id `iuCOanGou5VLdjsVzuSj`, flow `weime5DY6BKajeZdTu6M`. Escribir en el guion de voz las siglas y numeros como se pronuncian ("ultravioleta", no "UV"; "veinticinco", no "25") y el CTA en imperativo ("Guarda este vídeo y compártelo"). Despues transcribir el video con `video_analyze` de Magnific y comprobar titubeos, siglas y final no cortado ANTES de proponerlo.
- Montaje gratis con Magnific: subir clips con `creations_request_upload` + funcion edge `relay` + `creations_finalize_upload`; `video_cut`, `video_concatenate`, `video_audio_mix` (muteVideo:true). Magnific NO acepta URLs de CloudFront: copiar antes a Supabase bucket `reels` con la funcion `copyvid`. Despues importar a Higgsfield con `media_import_url` y guardar la URL `https://d2ol7oe51mr4n9.cloudfront.net/user_3C5cQxE1oi1XbZDKdjou8cwMYeD/<media_id>.mp4` en `video_url`.
- Guardar en `content_calendar` solo tras el visto bueno de la usuaria. Actualizar tambien guion y caption para que coincidan con la locucion.
- El lipsync de Magnific gasta creditos y se agotaron; usar solo herramientas gratuitas.

## n8n "Diaria-IG": lecciones
- Publicacion programada: nodo "Schedule – Publicación 18:00 UTC". Solo coge lo que este en `aprobado` con `fecha_publicacion` de HOY; aprobar ANTES de las 18:00 UTC o el dia se queda sin salir (al dia siguiente busca la fecha siguiente).
- Los nodos "IG – Crear Reel" e "IG – Publicar Reel" deben llevar `access_token` = `{{ $json._token.replace(/^Bearer\s*/i, '') }}` (Publicar Reel: `{{ $('Set – Datos Publicación').item.json._token.replace(/^Bearer\s*/i, '') }}`). Sin eso: error 400 "Cannot parse access token".
- El caption del reel NUNCA debe usar `{{ $json.tema }}` (es descriptor interno) ni `#RutinaDeRostro` ("rutina" prohibida). Usar el texto limpio de `carousel_caption`. Revisar tambien "IG – Crear Imagen" (dias de foto quote) por la misma plantilla.
- Si n8n avisa "Workflow was changed by someone else / Autosave failed": hay otra pestaña con el flujo abierto; cerrar todas, recargar y rehacer los cambios guardando con una sola pestaña.

## Skill obligatoria para reels/vídeos
Antes de producir o revisar cualquier reel o vídeo, leer `.claude/skills/senda-reels/SKILL.md` (La Investigadora en movimiento, escenas que ilustran el guion, voz siempre suya, subtítulos llamativos).

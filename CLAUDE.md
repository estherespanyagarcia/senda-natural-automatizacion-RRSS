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
- Los guiones de `content_calendar` de los dias 1, 3, 5 y 6 NO corresponden a la Nueva Premisa (son anteriores); los dias 2, 4 y 7 (reels) si coinciden.
- Avatares Light/Medium/Rich son solo internos.
- Claims de producto sujetos a las GC Rules (por ejemplo "sin silicones" hay que confirmarlo antes de publicar).

## Formato y marca
- Carrusel y foto quote: 1080x1350 (4:5). Stories: 1080x1920. Reels: 9:16 video. NUNCA 16:9 apaisado (Instagram lo muestra diminuto).
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

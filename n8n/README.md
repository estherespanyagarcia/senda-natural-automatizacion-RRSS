# Automatización n8n – Senda Natural

## Arquitectura

```
Claude Code Remote (09:00 diario)
  └─ ElevenLabs MCP → 4 vídeos (IG x2 + TikTok x2)
       └─ POST /api/automation/save-results
            ├─ Supabase: guarda URLs + estado
            └─ n8n Webhook → Telegram (botones aprobación)
```

La API de ElevenLabs Flows no tiene endpoints REST públicos todavía (previsto para 2026).
El pipeline de vídeo se ejecuta mediante una **rutina diaria de Claude Code Remote** que usa el MCP de ElevenLabs.

---

## Variables de entorno necesarias

### Vercel (ya configuradas o añadir en dashboard)
| Variable | Descripción |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | URL de Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key |
| `CRON_SECRET` | Secreto para proteger los endpoints de cron |
| `N8N_WEBHOOK_URL` | URL del webhook de n8n (ver paso 3) |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | Chat ID de Esther |

### n8n (Environment Variables en n8n Cloud o self-hosted)
| Variable | Descripción |
|---|---|
| `TELEGRAM_CHAT_ID` | Chat ID de Esther |
| `VERCEL_APP_URL` | https://senda-natural-automatizacion-rrss.vercel.app |
| `CRON_SECRET` | El mismo CRON_SECRET de Vercel |

---

## Paso 1: Importar el workflow en n8n

1. Abrir n8n → **Workflows → Import from file**
2. Seleccionar `n8n/senda-natural-produccion.json`
3. En el nodo **"Telegram – Notificar Vídeos"**: conectar las credenciales de Telegram
4. Activar el workflow

### URL del Webhook
Una vez activado, n8n genera la URL del webhook. Es algo como:
```
https://[tu-n8n].app.n8n.cloud/webhook/senda-natural-videos
```
→ Copiar esta URL y pegarla como `N8N_WEBHOOK_URL` en Vercel.

---

## Paso 2: Supabase – añadir columnas (si no existen)

Ejecutar en Supabase SQL Editor:
```sql
ALTER TABLE content_calendar
  ADD COLUMN IF NOT EXISTS elevenlabs_ig1_url TEXT,
  ADD COLUMN IF NOT EXISTS elevenlabs_ig2_url TEXT,
  ADD COLUMN IF NOT EXISTS elevenlabs_tiktok1_url TEXT,
  ADD COLUMN IF NOT EXISTS elevenlabs_tiktok2_url TEXT;
```

---

## Paso 3: Rutina diaria de Claude Code Remote

La rutina **ya está creada** (ID: `trig_01MqphnfDoS72nxDVdnNGZQF`) y se ejecuta automáticamente a las **09:00 hora de Madrid** todos los días.

> **IMPORTANTE sobre variables de entorno:**
> La rutina necesita leer `$CRON_SECRET` del entorno. Asegúrate de que esta variable esté configurada en el entorno de Claude Code Remote donde se ejecuta la rutina (Environment → Secrets en claude.ai/code).

> **IMPORTANTE sobre MCP de ElevenLabs:**
> Si la sesión disparada no tiene acceso a los tools de ElevenLabs MCP, necesitarás recrear la rutina desde la interfaz web de claude.ai (Routines) donde podrás seleccionar los conectores manualmente.

La rutina:
1. Llama a `/api/automation/daily-scripts` para obtener los 4 guiones del día
2. Para cada vídeo, ejecuta el pipeline completo de ElevenLabs via MCP:
   - TTS con eleven_v4 + voz de Esther
   - Generación de 3 clips de imagen (gpt-image-2)
   - Animación a vídeo (bytedance-seedance-v2.5)
   - Título de cierre estático (SÍGUEME. / ESTO ES SOLO EL PRINCIPIO.)
   - Composición final (eleven_composition)
3. Llama a `/api/automation/save-results` con las 4 URLs

---

## Paso 4: Flujo de aprobación (Telegram)

Cuando los 4 vídeos están listos, Esther recibe en Telegram:
```
🎬 4 vídeos listos — [tema del día]

📱 IG Reel A → [link ElevenLabs]
📱 IG Reel B → [link ElevenLabs]
🎵 TikTok A  → [link ElevenLabs]
🎵 TikTok B  → [link ElevenLabs]

[✅ Publicar hoy] [🔄 Regenerar] [❌ Descartar]
```

---

## Tiempos estimados por ejecución
- TTS + imagen (paralelo): ~2 min
- Animación a vídeo × 4 vídeos × 3 clips: ~8 min
- Composición × 4: ~4 min
- **Total: 15-20 minutos** desde trigger hasta notificación Telegram

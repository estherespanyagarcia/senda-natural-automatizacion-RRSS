import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

interface VideoResult {
  slot: string;        // "ig-1" | "ig-2" | "tiktok-1" | "tiktok-2"
  label: string;       // "IG Reel A", etc.
  platform: string;
  generation_id: string;
  video_url: string;   // ElevenLabs history link (permanent, mobile-accessible)
  duration_secs?: number;
}

interface Payload {
  entry_id: string;
  dia: number;
  tema: string;
  videos: VideoResult[];
  error?: string;
}

function auth(req: NextRequest): boolean {
  const secret =
    req.headers.get("x-cron-secret") ??
    req.headers.get("authorization")?.replace("Bearer ", "");
  return secret === process.env.CRON_SECRET;
}

async function notifyN8n(payload: Payload, urls: Record<string, string>) {
  const webhookUrl = process.env.N8N_WEBHOOK_URL;
  if (!webhookUrl) return;
  await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dia: payload.dia,
      tema: payload.tema,
      ig1_url: urls["ig-1"] ?? null,
      ig2_url: urls["ig-2"] ?? null,
      tiktok1_url: urls["tiktok-1"] ?? null,
      tiktok2_url: urls["tiktok-2"] ?? null,
      all_videos: payload.videos,
    }),
  }).catch(() => {/* best-effort */});
}

export async function POST(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const payload: Payload = await req.json();
  const today = new Date().toISOString().split("T")[0];

  if (payload.error) {
    // Pipeline failed — log and notify
    await supabase
      .from("content_calendar")
      .update({ status: "pendiente", notas: `Error pipeline ElevenLabs: ${payload.error}` })
      .eq("id", payload.entry_id);
    await supabase.from("cron_log").insert({
      fecha: today,
      dia_seleccionado: payload.dia,
      status: "error",
      motivo_cambio: payload.error,
    });
    return NextResponse.json({ ok: false });
  }

  // Build URL map and serialized video list
  const urlMap: Record<string, string> = {};
  for (const v of payload.videos) {
    urlMap[v.slot] = v.video_url;
  }

  // Update calendar entry with all video URLs
  await supabase
    .from("content_calendar")
    .update({
      status: "listo",
      video_url: urlMap["ig-1"] ?? urlMap["tiktok-1"] ?? null,
      notas: JSON.stringify(payload.videos.map((v) => ({ slot: v.slot, url: v.video_url, gen: v.generation_id }))),
    })
    .eq("id", payload.entry_id);

  // Log to content_history
  await supabase.from("content_history").upsert({
    dia: payload.dia,
    tema: payload.tema,
    formato: "elevenlabs-4pack",
    rrss: "instagram,tiktok",
    status_final: "listo",
    fecha_generacion: new Date().toISOString(),
  });

  await supabase.from("cron_log").insert({
    fecha: today,
    dia_seleccionado: payload.dia,
    status: "completado",
    motivo_cambio: `${payload.videos.length} vídeos ElevenLabs generados.`,
  });

  // Fire n8n webhook (best-effort, doesn't block response)
  notifyN8n(payload, urlMap);

  return NextResponse.json({ ok: true, saved: payload.videos.length });
}

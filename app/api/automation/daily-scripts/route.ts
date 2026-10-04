import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

// Visual style and media direction for each video slot
const VIDEO_SLOTS = [
  {
    slot: "ig-1",
    platform: "instagram",
    label: "IG Reel A",
    aspect: "9:16",
    duration: "20-25",
    tono: "editorial-producto",
    visual_angle: "Primer plano de piel o producto con iluminación cinematográfica. Textura macro. Estética de revista de lujo. Fondo oscuro.",
    script_angle: "Gancho principal — presenta el problema directamente al espectador",
  },
  {
    slot: "ig-2",
    platform: "instagram",
    label: "IG Reel B",
    aspect: "9:16",
    duration: "20-25",
    tono: "dramático-investigativo",
    visual_angle: "Planos de archivo de expresiones faciales de preocupación o revelación. Atmósfera dramática. Luz lateral dura.",
    script_angle: "Giro revelador — el dato oculto o la causa que nadie explica",
  },
  {
    slot: "tiktok-1",
    platform: "tiktok",
    label: "TikTok A",
    aspect: "9:16",
    duration: "15-20",
    tono: "provocador-revelador",
    visual_angle: "Motion graphics con texto en pantalla. Ritmo rápido. Planos de personas aplicando productos del día a día.",
    script_angle: "Hook impactante en las primeras 2 palabras — máxima energía",
  },
  {
    slot: "tiktok-2",
    platform: "tiktok",
    label: "TikTok B",
    aspect: "9:16",
    duration: "15-20",
    tono: "educativo-directo",
    visual_angle: "Infografía limpia, diagrama de ingredientes INCI, planos del protocolo. Estilo editorial B&W con acento dorado.",
    script_angle: "La solución — qué hacer exactamente, paso a paso",
  },
];

// Generates 4 distinct variant scripts from the main guion
function buildVariantScripts(
  guion: string,
  tema: string,
  slots: typeof VIDEO_SLOTS
): Array<{ slot: string; platform: string; label: string; aspect: string; duration: string; script: string; visual_prompt: string; image_prompts: string[] }> {
  const normalized = guion.trim();

  return slots.map((s) => {
    const script = `${normalized}\n\n[Ángulo: ${s.script_angle}]`;

    const imagePrompts = Array.from({ length: 3 }, (_, i) => {
      const beats = [
        `Problema: ${tema}. ${s.visual_angle} Iluminación dramática. Plano de apertura.`,
        `Desarrollo: ${tema}. ${s.visual_angle} Plano detalle, macro, texturas.`,
        `Resolución: ${tema}. ${s.visual_angle} Plano final con sensación de alivio o transformación.`,
      ];
      return (
        `Cinematic 9:16 portrait video frame. ${beats[i]} ` +
        `Brand palette: deep warm black #0E0D0A background, gold #D4AF7F accent, cream #FAF6F0 text. ` +
        `Style: ${s.tono}. Ultra-high quality, no text overlays, no logos, no brand names on packaging.`
      );
    });

    return {
      slot: s.slot,
      platform: s.platform,
      label: s.label,
      aspect: s.aspect,
      duration: s.duration,
      script,
      visual_prompt: s.visual_angle,
      image_prompts: imagePrompts,
    };
  });
}

function auth(req: NextRequest): boolean {
  const secret =
    req.headers.get("x-cron-secret") ??
    req.headers.get("authorization")?.replace("Bearer ", "");
  return secret === process.env.CRON_SECRET;
}

export async function GET(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const today = new Date().toISOString().split("T")[0];

  // Try today's scheduled entry first
  const { data: primary } = await supabase
    .from("content_calendar")
    .select("*")
    .eq("fecha_publicacion", today)
    .eq("status", "pendiente")
    .single();

  // Fallback: oldest unused pending entry
  let entry = primary;
  let motivo: string | null = null;
  if (!entry) {
    const { data: fallback } = await supabase
      .from("content_calendar")
      .select("*")
      .eq("status", "pendiente")
      .order("dia", { ascending: true })
      .limit(1)
      .single();
    entry = fallback ?? null;
    if (entry)
      motivo = `Sin entrada programada para hoy. Usando día ${entry.dia} como fallback.`;
  }

  if (!entry) {
    return NextResponse.json({ ok: false, message: "No hay entradas pendientes." }, { status: 404 });
  }

  const videos = buildVariantScripts(entry.guion ?? entry.tema, entry.tema, VIDEO_SLOTS);

  return NextResponse.json({
    ok: true,
    dia: entry.dia,
    entry_id: entry.id,
    tema: entry.tema,
    pilar: entry.pilar,
    motivo,
    videos,
    voice_id: "iuCOanGou5VLdjsVzuSj",  // Esther's cloned voice in ElevenLabs
    oobCode: "78ef7dd03f2d4240b8d9b18595bf36c5",  // for mobile-accessible history links
  });
}

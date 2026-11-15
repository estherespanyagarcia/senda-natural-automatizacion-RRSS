import json, uuid
nodes=[]; conns={}
def nid(): return str(uuid.uuid4())
def add(name,type_,tv,x,y,params,**kw):
    n={"id":nid(),"name":name,"type":type_,"typeVersion":tv,"position":[x,y],"parameters":params}
    n.update(kw); nodes.append(n); return name
def link(a,b,out=0):
    conns.setdefault(a,{"main":[]})
    m=conns[a]["main"]
    while len(m)<=out: m.append([])
    m[out].append({"node":b,"type":"main","index":0})

SB='={{ $json.supabase_url }}'
def cfg(name,x,y):
    return add(name,"n8n-nodes-base.set",3.4,x,y,{"assignments":{"assignments":[
      {"id":nid(),"name":"supabase_url","value":"https://jrovkkjxvzuzcpexdydy.supabase.co","type":"string"},
      {"id":nid(),"name":"supabase_key","value":"={{ $vars.SUPABASE_ANON_KEY }}","type":"string"},
      {"id":nid(),"name":"bot_token","value":"={{ $vars.TELEGRAM_BOT_TOKEN_GANCHOS }}","type":"string"},
      {"id":nid(),"name":"chat_id","value":"={{ $vars.TELEGRAM_CHAT_ID }}","type":"string"},
      {"id":nid(),"name":"ig_token","value":"={{ $vars.INSTAGRAM_TOKEN }}","type":"string"},
      {"id":nid(),"name":"api_base","value":"https://graph.instagram.com/v21.0/me","type":"string"}]},
      "includeOtherFields":True,"options":{}})
def sbheaders(ref):
    return {"parameters":[{"name":"apikey","value":"={{ %s.supabase_key }}"%ref},
                          {"name":"Authorization","value":"={{ 'Bearer ' + %s.supabase_key }}"%ref},
                          {"name":"Content-Type","value":"application/json"},
                          {"name":"Prefer","value":"return=minimal"}]}
def sb_get(name,x,y,cfgnode,filt):
    ref="$('%s').first().json"%cfgnode
    return add(name,"n8n-nodes-base.httpRequest",4.2,x,y,{"method":"GET",
      "url":"={{ %s.supabase_url }}/rest/v1/hook_tests?%s&select=*&limit=1"%(ref,filt),
      "sendHeaders":True,"headerParameters":sbheaders(ref),"options":{}})
def sb_patch(name,x,y,cfgnode,idea_expr,body_expr):
    ref="$('%s').first().json"%cfgnode
    return add(name,"n8n-nodes-base.httpRequest",4.2,x,y,{"method":"PATCH",
      "url":"={{ %s.supabase_url }}/rest/v1/hook_tests?idea=eq.{{ %s }}"%(ref,idea_expr),
      "sendHeaders":True,"headerParameters":sbheaders(ref),
      "sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify(%s) }}"%body_expr,"options":{}})
def tg(name,x,y,cfgnode,method,body_expr):
    ref="$('%s').first().json"%cfgnode
    return add(name,"n8n-nodes-base.httpRequest",4.2,x,y,{"method":"POST",
      "url":"=https://api.telegram.org/bot{{ %s.bot_token }}/%s"%(ref,method),
      "sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify(%s) }}"%body_expr,"options":{}})
KB="{inline_keyboard:[[{text:'✅ Aprobar',callback_data:'hook_approve_'+%s},{text:'❌ Rechazar',callback_data:'hook_reject_'+%s}]]}"

PRE = r"""
const esc = s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const prohibidas = /(ringana|rutina|desintox|cierra(r)? (los )?poros|\bcura\b|oportunidad de negocio|únete|red de|multinivel)/i;
function revisar(r){
  const cap=r.caption||''; const p=[];
  if(prohibidas.test(cap)) p.push('palabra prohibida');
  if(cap.split('\n').length>2) p.push('más de 2 renglones');
  if(/#\w+/.test(cap)) p.push('hashtags');
  if(!cap.includes('www.sendanatural.net')) p.push('falta la CTA');
  if(!/Senda Natural\s*$/.test(cap.trim())) p.push('falta la firma');
  if(!r.video_url) p.push('sin vídeo');
  return p;
}
"""
# ---------- CADENA A: 12:00 aviso ----------
add("Schedule – Aviso 12:00","n8n-nodes-base.scheduleTrigger",1.2,0,0,{"rule":{"interval":[{"field":"cronExpression","expression":"0 12 16-22 11 *"}]}})
cfg("Config 12h",220,0)
today="$now.setZone('Europe/Madrid').toFormat('yyyy-MM-dd')"
sb_get("Supabase – Buscar reel de hoy",440,0,"Config 12h","fecha_publicacion=eq.{{ %s }}&status=in.(borrador,en_revision)"%today)
add("Code – Revisar reglas y preparar mensaje","n8n-nodes-base.code",2,660,0,{"jsCode":PRE+r"""
const cfg=$('Config 12h').first().json;
const rows=$input.all().map(i=>i.json).filter(r=>r&&r.idea);
if(!rows.length) return [{json:{...cfg,idea:0,bloqueado:true,mensaje:'<b>REEL DE GANCHO PRUEBA</b>\nHoy no hay reel en borrador para esta fecha. No se envía a aprobar.'}}];
const r=rows[0]; const p=revisar(r);
if(p.length) return [{json:{...cfg,idea:r.idea,bloqueado:true,motivo:p.join(', '),mensaje:`<b>REEL DE GANCHO PRUEBA · BLOQUEADO</b>\nIdea ${r.idea}: ${esc(p.join(', '))}.\nNo se envía a aprobar.`}}];
const mensaje=`<b>REEL DE GANCHO PRUEBA</b>\nIdea ${r.idea} · publicación prevista 13:00 (Europe/Madrid)\n\n<b>Gancho:</b> ${esc(r.gancho)}\n\n<b>Leyenda:</b>\n${esc(r.caption)}\n\n<a href="${r.video_url}">Ver vídeo</a>`;
return [{json:{...cfg,idea:r.idea,bloqueado:false,mensaje}}];
"""})
add("IF – ¿Bloqueado?","n8n-nodes-base.if",2,880,0,{"conditions":{"options":{"caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":nid(),"leftValue":"={{ $json.bloqueado }}","rightValue":True,"operator":{"type":"boolean","operation":"equals"}}]},"options":{}})
tg("Telegram – Aviso bloqueado",1100,-80,"Code – Revisar reglas y preparar mensaje","sendMessage","{chat_id:$('Code – Revisar reglas y preparar mensaje').first().json.chat_id,text:$('Code – Revisar reglas y preparar mensaje').first().json.mensaje,parse_mode:'HTML'}")
sb_patch("Supabase – Marcar bloqueado",1320,-80,"Code – Revisar reglas y preparar mensaje","$('Code – Revisar reglas y preparar mensaje').first().json.idea","{status:'bloqueado_reglas',cumple_reglas:false,motivo_bloqueo:$('Code – Revisar reglas y preparar mensaje').first().json.motivo||'sin fila'}")
C="$('Code – Revisar reglas y preparar mensaje').first().json"
tg("Telegram – Pedir aprobación",1100,100,"Code – Revisar reglas y preparar mensaje","sendMessage","{chat_id:%s.chat_id,text:%s.mensaje,parse_mode:'HTML',reply_markup:%s}"%(C,C,KB%(C+".idea",C+".idea")))
sb_patch("Supabase – Marcar en revisión",1320,100,"Code – Revisar reglas y preparar mensaje",C+".idea","{status:'en_revision',cumple_reglas:true,aviso_enviado_at:new Date().toISOString()}")
link("Schedule – Aviso 12:00","Config 12h"); link("Config 12h","Supabase – Buscar reel de hoy"); link("Supabase – Buscar reel de hoy","Code – Revisar reglas y preparar mensaje"); link("Code – Revisar reglas y preparar mensaje","IF – ¿Bloqueado?")
link("IF – ¿Bloqueado?","Telegram – Aviso bloqueado",0); link("IF – ¿Bloqueado?","Telegram – Pedir aprobación",1)
link("Telegram – Aviso bloqueado","Supabase – Marcar bloqueado"); link("Telegram – Pedir aprobación","Supabase – Marcar en revisión")

# ---------- CADENA B: botones ----------
add("Telegram Trigger – Ganchos","n8n-nodes-base.telegramTrigger",1.2,0,400,{"updates":["callback_query"],"additionalFields":{}},webhookId=nid())
add("Code – Extraer acción","n8n-nodes-base.code",2,220,400,{"jsCode":r"""
const cq=$json.callback_query; const d=(cq&&cq.data)||'';
const m=d.match(/^hook_(approve|reject)_(\d+)$/);
if(!m) return [];
return [{json:{callback_id:cq.id,action:m[1],idea:Number(m[2])}}];
"""})
cfg("Config botones",440,400)
add("IF – ¿Aprobado?","n8n-nodes-base.if",2,660,400,{"conditions":{"options":{"caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":nid(),"leftValue":"={{ $json.action }}","rightValue":"approve","operator":{"type":"string","operation":"equals"}}]},"options":{}})
J="$('Config botones').first().json"
sb_patch("Supabase – Marcar aprobado por Esther",880,320,"Config botones",J+".idea","{status:'aprobado_por_esther',aprobado_at:new Date().toISOString()}")
tg("Telegram – Responder botón (ok)",1100,320,"Config botones","answerCallbackQuery","{callback_query_id:%s.callback_id,text:'Aprobado'}"%J)
tg("Telegram – Confirmación aprobado",1320,320,"Config botones","sendMessage","{chat_id:%s.chat_id,text:'REEL DE GANCHO PRUEBA aprobado (idea '+%s.idea+'). Se publicará a las 13:00 (Europe/Madrid).'}"%(J,J))
sb_patch("Supabase – Volver a borrador",880,500,"Config botones",J+".idea","{status:'borrador'}")
tg("Telegram – Responder botón (no)",1100,500,"Config botones","answerCallbackQuery","{callback_query_id:%s.callback_id,text:'Rechazado'}"%J)
tg("Telegram – Confirmación rechazo",1320,500,"Config botones","sendMessage","{chat_id:%s.chat_id,text:'REEL DE GANCHO PRUEBA rechazado (idea '+%s.idea+'). No se publica.'}"%(J,J))
link("Telegram Trigger – Ganchos","Code – Extraer acción"); link("Code – Extraer acción","Config botones"); link("Config botones","IF – ¿Aprobado?")
link("IF – ¿Aprobado?","Supabase – Marcar aprobado por Esther",0); link("IF – ¿Aprobado?","Supabase – Volver a borrador",1)
link("Supabase – Marcar aprobado por Esther","Telegram – Responder botón (ok)"); link("Telegram – Responder botón (ok)","Telegram – Confirmación aprobado")
link("Supabase – Volver a borrador","Telegram – Responder botón (no)"); link("Telegram – Responder botón (no)","Telegram – Confirmación rechazo")

# ---------- CADENA C: 13:00 publicar ----------
add("Schedule – Publicación 13:00","n8n-nodes-base.scheduleTrigger",1.2,0,800,{"rule":{"interval":[{"field":"cronExpression","expression":"0 13 16-22 11 *"}]}})
cfg("Config 13h",220,800)
sb_get("Supabase – Buscar aprobado de hoy",440,800,"Config 13h","fecha_publicacion=eq.{{ %s }}&status=eq.aprobado_por_esther"%today)
add("Code – ¿Hay aprobado?","n8n-nodes-base.code",2,660,800,{"jsCode":r"""
const cfg=$('Config 13h').first().json;
const rows=$input.all().map(i=>i.json).filter(r=>r&&r.idea);
if(!rows.length) return [{json:{...cfg,hay:false}}];
return [{json:{...cfg,hay:true,...rows[0]}}];
"""})
add("IF – ¿Hay aprobado?","n8n-nodes-base.if",2,880,800,{"conditions":{"options":{"caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":nid(),"leftValue":"={{ $json.hay }}","rightValue":True,"operator":{"type":"boolean","operation":"equals"}}]},"options":{}})
P="$('Code – ¿Hay aprobado?').first().json"
tok=P+".ig_token.replace(/^Bearer\\s*/i,'')"
add("IG – Crear Reel","n8n-nodes-base.httpRequest",4.2,1100,720,{"method":"POST",
  "url":"={{ %s.api_base }}/media"%P,"sendBody":True,"specifyBody":"json",
  "jsonBody":"={{ JSON.stringify({media_type:'REELS',video_url:%s.video_url,caption:%s.caption,share_to_feed:true,access_token:%s,...(%s.portada_url?{cover_url:%s.portada_url}:{})}) }}"%(P,P,tok,P,P),"options":{}})
add("Esperar 90s","n8n-nodes-base.wait",1.1,1320,720,{"amount":90,"unit":"seconds"},webhookId=nid())
add("IG – Publicar Reel","n8n-nodes-base.httpRequest",4.2,1540,720,{"method":"POST","url":"={{ %s.api_base }}/media_publish"%P,"sendBody":True,"specifyBody":"json",
  "jsonBody":"={{ JSON.stringify({creation_id:$('IG – Crear Reel').first().json.id,access_token:%s}) }}"%tok,"options":{}})
sb_patch("Supabase – Marcar publicado",1760,720,"Config 13h",P+".idea","{status:'publicado',publicado_at:new Date().toISOString()}")
tg("Telegram – Confirmación publicado",1980,720,"Config 13h","sendMessage","{chat_id:%s.chat_id,text:'REEL DE GANCHO PRUEBA publicado (idea '+%s.idea+'). Anota las visitas a las 48 h en el CSV.'}"%(P,P))
# sin aprobación
sb_get("Supabase – Buscar pendiente de hoy",1100,900,"Config 13h","fecha_publicacion=eq.{{ %s }}&status=in.(borrador,en_revision,bloqueado_reglas)"%today)
add("Code – Mensaje sin aprobación","n8n-nodes-base.code",2,1320,900,{"jsCode":PRE+r"""
const cfg=$('Config 13h').first().json;
const rows=$input.all().map(i=>i.json).filter(r=>r&&r.idea);
if(!rows.length) return [{json:{...cfg,idea:0,mensaje:'<b>REEL DE GANCHO PRUEBA</b>\nA las 13:00 no hay reel preparado para hoy. No se publica nada.'}}];
const r=rows[0];
const mensaje=`<b>REEL DE GANCHO PRUEBA</b>\nA las 13:00 NO hay aprobación de la idea ${r.idea}. <b>No se publica.</b>\n\n<b>Gancho:</b> ${esc(r.gancho)}\n\n<b>Leyenda:</b>\n${esc(r.caption||'')}\n\n<a href="${r.video_url||''}">Ver vídeo</a>`;
return [{json:{...cfg,idea:r.idea,mensaje,aprobable:!!r.video_url&&r.status!=='bloqueado_reglas'}}];
"""})
D="$('Code – Mensaje sin aprobación').first().json"
tg("Telegram – Repetir aviso sin aprobación",1540,900,"Config 13h","sendMessage","{chat_id:%s.chat_id,text:%s.mensaje,parse_mode:'HTML',...(%s.aprobable?{reply_markup:%s}:{})}"%(D,D,D,KB%(D+".idea",D+".idea")))
link("Schedule – Publicación 13:00","Config 13h"); link("Config 13h","Supabase – Buscar aprobado de hoy"); link("Supabase – Buscar aprobado de hoy","Code – ¿Hay aprobado?"); link("Code – ¿Hay aprobado?","IF – ¿Hay aprobado?")
link("IF – ¿Hay aprobado?","IG – Crear Reel",0); link("IF – ¿Hay aprobado?","Supabase – Buscar pendiente de hoy",1)
link("IG – Crear Reel","Esperar 90s"); link("Esperar 90s","IG – Publicar Reel"); link("IG – Publicar Reel","Supabase – Marcar publicado"); link("Supabase – Marcar publicado","Telegram – Confirmación publicado")
link("Supabase – Buscar pendiente de hoy","Code – Mensaje sin aprobación"); link("Code – Mensaje sin aprobación","Telegram – Repetir aviso sin aprobación")

wf={"name":"Ganchos Prueba · aviso 12:00 + aprobación + publicación 13:00","nodes":nodes,"connections":conns,"settings":{"executionOrder":"v1","timezone":"Europe/Madrid"}}
json.dump(wf,open("ganchos_prueba_workflow.json","w"),ensure_ascii=False,indent=2)
print(len(nodes),"nodos")

import { resolve, normalize, dirname, isAbsolute, join, relative, parse } from "node:path";
import { existsSync, readFileSync, realpathSync, mkdirSync, appendFileSync, promises as fs } from "node:fs";
import { verify } from "node:crypto";

const IG_HOOK_DIAG_20261117 = "I:/Projetos/Instagram-RobsonAlencar/03-agendamentos/logs/hook-firing.log";
try { mkdirSync(dirname(IG_HOOK_DIAG_20261117), {recursive:true}); appendFileSync(IG_HOOK_DIAG_20261117, JSON.stringify({at:new Date().toISOString(),event:"PLUGIN_LOADED"})+"\n"); } catch {}
const DEFAULT_ROOT = "I:/Projetos/Instagram-RobsonAlencar";
const TOOLS_READ = new Set(["read","glob","grep","list","skill","webfetch","websearch","question","todoread","list_mcp_resources","instagram_auditar_perfil","mesh-gama_gama_status","mesh-gama_gama_opencode_config","mesh-gama_gama_list_configs","mesh-gama_gama_read_config"]);
const TOOLS_WRITE = new Set(["write","edit","multiedit"]);
const normalizePath = p => normalize(resolve(p)).replaceAll(String.fromCharCode(92),"/").toLowerCase();
const under = (p,d) => p===d || p.startsWith(d+"/");
const safeName = s => typeof s==="string" && /^[a-z0-9][a-z0-9_-]{0,63}$/i.test(s);
const canonical = a => [a.nivel,a.session_id,a.task,a.expires_at,a.nonce,JSON.stringify(a.pastas)].join("\n");
function physical(p) {
  // Resolve existing file or deepest existing ancestor, then append missing path.
  let cursor=p; const missing=[];
  while(!existsSync(cursor)) {
    const parent=dirname(cursor);
    if(parent===cursor) return null;
    missing.unshift(p.split(/[\\/]/).filter(Boolean).at(-1)); 
    // use basename rather than splitting remaining string
    missing[0]=cursor.slice(parent.length).replace(/^[\\/]+/,"");
    cursor=parent;
  }
  try {
    let x=realpathSync.native(cursor);
    for(const part of missing) x=join(x,part);
    return normalizePath(x);
  }catch{return null;}
}
export function createInstagramGuard({root=DEFAULT_ROOT,publicKeyFile}={}){
 const ROOT=resolve(root), R=normalizePath(ROOT), RPHYSICAL=physical(ROOT);
 const path=(s)=>join(ROOT,s);
 const LOCK=path("03-agendamentos/publicador/BLOQUEIO-PUBLICACAO-ATIVO");
 const AUTH=path("00-regras/AUTORIZACAO-MANUAL-DE-ESCRITA.json");
 const LOG=path("03-agendamentos/logs/write-guard.log");
 const KEY=publicKeyFile || path("00-regras/write-guard-public-key.pem");
 const protectedList=[".opencode",".git","02-scripts","06-referencias","03-agendamentos/publicador/perfil-instagram"];
 const hardBlocked=p=>p===normalizePath(LOCK)||p===normalizePath(AUTH)||protectedList.some(s=>under(p,normalizePath(path(s))));
 function dest(raw,cwd) {
   if(typeof raw!=="string"||!raw.trim()||raw.includes("\0"))return null;
   const lexical=normalizePath(isAbsolute(raw)?raw:resolve(cwd,raw));
   if(!under(lexical,R)||hardBlocked(lexical))return null;
   const real=physical(isAbsolute(raw)?raw:resolve(cwd,raw));
   if(!real||!RPHYSICAL||!under(real,RPHYSICAL)||hardBlocked(real))return null;
   return {lexical,real};
 }
 function permitted(dst,a){
   if(!dst)return false;
   const allowed=a.nivel==="PRODUZIR" ?
     ["01-conteudo/rascunhos","debug",...a.pastas.map(n=>"01-conteudo/"+n)] :
     ["03-agendamentos/publicador/fila","03-agendamentos/publicador/processados"];
   return allowed.some(n=>{
     const base=normalizePath(path(n));
     const physicalBase=physical(path(n));
     return under(dst.lexical,base) && physicalBase && under(dst.real,physicalBase) && under(physicalBase,RPHYSICAL);
   });
 }
 async function logDecision(level,target,decision,reason){
  const event={timestamp:new Date().toISOString(),nivel:level,path:target||null,decisao:decision,motivo:reason};
  try {
   await fs.mkdir(dirname(LOG),{recursive:true});
   await fs.appendFile(LOG,JSON.stringify(event)+"\n","utf8");
  }catch(e){throw new Error("[IG AUDITORIA INDISPONIVEL] "+e.message);}
 }

 // Queries limited to the project: diagnostics may not write, delete or publish.
 const projectPath=raw=>isAbsolute(raw)?raw:resolve(ROOT,raw);
 function safeReadPath(raw){
   if(typeof raw!=="string"||raw.includes("\0")||raw.includes("'")||raw.includes('"')||raw.includes(String.fromCharCode(96)))return false;
   const p=projectPath(raw);
   const lex=normalizePath(p),real=physical(p);
   return !!(real && RPHYSICAL && under(lex,R) && under(real,RPHYSICAL));
 }
 function safeDiagnosticBash(command){
   if(typeof command!=="string" || command.length>1400)return null;
   const cmd=command.trim();
   if(/^(?:node(?:\.exe)?\s+(?:--version|-v)|python(?:\.exe)?\s+(?:--version|-V)|node(?:\.exe)?\s+(?:--version|-v)\s*;\s*python(?:\.exe)?\s+(?:--version|-V))$/i.test(cmd))
     return cmd;
   const parts=cmd.split(/\s*&&\s*/);
   if(parts.length===1 || (parts.length>=3&&parts.length<=9&&parts.length%2===1)){
     const commands=[];
     let valid=true;
     for(let i=0;i<parts.length;i++){
       if(i%2===1){
         if(parts[i]!=="echo ---"){valid=false;break}
         commands.push("Write-Output '---'");
         continue;
       }
       const m=/^(?:ls|dir|Get-ChildItem)\s+(?:"([^"]+)"|'([^']+)'|(\S+))(?:\s+2>\/dev\/null)?$/i.exec(parts[i].trim());
       const target=m&&(m[1]||m[2]||m[3]);
       if(!target || !safeReadPath(target)){valid=false;break}
       commands.push("Get-ChildItem -LiteralPath '"+projectPath(target).replace(/'/g,"''")+"' | Select-Object Name,Length,Mode");
     }
     if(valid&&commands.length){
       const powershell=commands.join("; ");
       const encoded=Buffer.from(powershell,"utf16le").toString("base64");
       return "powershell.exe -NoProfile -EncodedCommand "+encoded;
     }
   }
   if(/[;&\r\n\x60><$]/.test(cmd))return null;
   const m=/^(?:Get-ChildItem|Test-Path|ls|dir)\s+(?:-LiteralPath\s+)?(?:"([^"]+)"|'([^']+)'|(\S+))$/i.exec(cmd);
   if(m){
     const target=m[1]||m[2]||m[3];
     if(!safeReadPath(target))return null;
     const type=/^Test-Path/i.test(cmd)?"Test-Path":"Get-ChildItem";
     const command=type+" -LiteralPath '"+projectPath(target).replace(/'/g,"''")+"'";
     return "powershell.exe -NoProfile -EncodedCommand "+Buffer.from(command,"utf16le").toString("base64");
   }
   return null;
 }

 function safeAnalysisBash(command){
   if(typeof command!=="string" || command.length>1200) return false;
   const cmd=command.trim();
   if(/[;\r\n\x60><$]/.test(cmd))return false;
   const inside=(p,scope)=>{
     if(!p||typeof p!=="string")return false;
     const lexical=normalizePath(projectPath(p)),real=physical(projectPath(p)),base=normalizePath(path(scope)),realBase=physical(path(scope));
     return !!(real&&realBase&&under(lexical,base)&&under(real,realBase)&&under(realBase,RPHYSICAL));
   };
   const columns=new Set(["name","length","lastwritetime","mode"]);
   const listing=/^(Get-ChildItem|Test-Path)\s+(?:-LiteralPath\s+)?(["'])([^"']+)\2(?:\s*\|\s*Select-Object\s+([a-zA-Z,\s]+))?$/i.exec(cmd);
   if(listing){
     const fields=listing[4]?listing[4].split(",").map(x=>x.trim().toLowerCase()):[];
     return fields.every(x=>columns.has(x)) && inside(listing[3],"01-conteudo");
   }
   const token='(?:"([^"]+)"|\\x27([^\\x27]+)\\x27|(\\S+))';
   const py='^python(?:\\.exe)?(?:\\s+-X\\s+utf8)?\\s+';
   const one=new RegExp(py+token+"$","i").exec(cmd);
   if(one){
     const script=one[1]||one[2]||one[3];
     return normalizePath(projectPath(script))===normalizePath(path("02-scripts/validar_layout_fixo.py"));
   }
   // QA da geometria oficial: leitura somente, nunca autoriza escrita ou publicacao.
   const geom=/^python(?:\.exe)?(?:\s+-X\s+utf8)?\s+("[^"]+"|'[^']+'|\S+)\s+--pasta\s+("[^"]+"|'[^']+'|\S+)\s+--expected\s+([1-9]|10)$/i.exec(cmd);
   if(geom){
     const source=geom[1].replace(/^['"]|['"]$/g,""),target=geom[2].replace(/^['"]|['"]$/g,"");
     return normalizePath(projectPath(source))===normalizePath(path("02-scripts/validar_padrao_carrossel.py")) && inside(target,"01-conteudo");
   }
   const two=new RegExp(py+token+"\\s+"+token+"\\s+--expected\\s+(?:[1-9]|10)\\s+--exigir-cenas$","i").exec(cmd);
   if(two){
     const script=two[1]||two[2]||two[3],target=two[4]||two[5]||two[6];
     return normalizePath(projectPath(script))===normalizePath(path("02-scripts/qa_carrossel.py")) && inside(target,"01-conteudo");
   }
   return false;
 }


 // Scoped QA scripts: limited to the current authorized carousel, no arbitrary Python
 // commands, eval, pipes, redirects or writes outside the draft.
 function safeTextAndImageQABash(command,grant){
   if(!grant || typeof command!=="string" || command.length>1500)return false;
   const cmd=command.trim();
   if(/[;&\r\n\x60><$|]/.test(cmd))return false;
   const tok='(?:"([^"]+)"|\\x27([^\\x27]+)\\x27|([^\\s"\\x27]+))';
   const prefix='^python(?:\\.exe)?(?:\\s+-X\\s+utf8)?\\s+';
   const parse=new RegExp(prefix+tok+'(.*)$','i').exec(cmd);
   if(!parse)return false;
   const script=parse[1]||parse[2]||parse[3],rest=parse[4]||"";
   const file=normalizePath(projectPath(script));
   const scope=normalizePath(path("01-conteudo/"+grant.folder));
   const realScope=physical(path("01-conteudo/"+grant.folder));
   if(!realScope)return false;
   const insideDraft=(candidate,extension)=>{
     if(typeof candidate!=="string"||!candidate)return false;
     const filePath=projectPath(candidate),lex=normalizePath(filePath),phys=physical(filePath);
     return (!extension || lex.endsWith(extension))
       && under(lex,scope) && phys && under(phys,realScope);
   };
   // Avoid weak, general-purpose argument parsing; these patterns are exact.
   const textQA=new RegExp('^\\s+--html\\s+'+tok+'\\s+--legenda\\s+'+tok+'(?:\\s+--saida\\s+'+tok+')?$','i').exec(rest);
   if(file===normalizePath(path("02-scripts/qa_texto_taxonomia.py"))&&textQA){
     const args=[textQA[1]||textQA[2]||textQA[3],textQA[4]||textQA[5]||textQA[6],textQA[7]||textQA[8]||textQA[9]];
     return insideDraft(args[0],".html") && insideDraft(args[1],".txt")
       && (!args[2]||insideDraft(args[2],".json"))
       && normalizePath(projectPath(args[0]))===normalizePath(path("01-conteudo/"+grant.folder+"/carrossel.html"))
       && normalizePath(projectPath(args[1]))===normalizePath(path("01-conteudo/"+grant.folder+"/legenda.txt"));
   }
   const editorial = new RegExp('^\\s+--legenda\\s+' + tok +
     '(?:\\s+--registrar\\s+--revisor\\s+"?humanizer\\+ig-caption"?)?$','i').exec(rest);
   if (file === normalizePath(path("02-scripts/validar_legenda_editorial.py")) && editorial) {
     const target = editorial[1] || editorial[2] || editorial[3];
     return insideDraft(target, ".txt")
       && normalizePath(projectPath(target)) === normalizePath(path("01-conteudo/" + grant.folder + "/legenda.txt"))
       && insideDraft(target + ".editorial.json", ".json");
   }
   const captions=new RegExp('^\\s+'+tok+'$','i').exec(rest);
   if(file===normalizePath(path("04-skills/ig-caption/caption.py"))&&captions){
     const target=captions[1]||captions[2]||captions[3];
     return insideDraft(target,".txt")
       && normalizePath(projectPath(target))===normalizePath(path("01-conteudo/"+grant.folder+"/legenda.txt"));
   }
   const pngQA=new RegExp('^\\s+'+tok+'\\s+--expected\\s+([1-9]|10)(?:\\s+--exigir-cenas)?$','i').exec(rest);
   if(file===normalizePath(path("02-scripts/qa_carrossel.py"))&&pngQA){
     const target=pngQA[1]||pngQA[2]||pngQA[3];
     return normalizePath(projectPath(target))===normalizePath(path("01-conteudo/"+grant.folder+"/out"))
       && insideDraft(target);
   }
   return false;
 }

 // Scoped drafting is based on a real user message. It cannot authorize publication.
 const SCOPE_DIR=path("03-agendamentos/logs/producao-sessoes");
 const allowedDraftExt=new Set([".html",".css",".json",".txt",".md",".png",".jpg",".jpeg",".webp"]);
 function scopedDraftTarget(dst){
   if(!dst)return null;
   const base=normalizePath(path("01-conteudo"));
   const pbase=physical(path("01-conteudo"));
   if(!pbase || !under(dst.lexical,base)||!under(dst.real,pbase))return null;
   const rel=relative(base,dst.lexical).replaceAll("\\","/");
   const parts=rel.split("/");
   if(parts.length<2 || parts.length>4 || !/^carrossel-[a-z0-9-]{5,80}$/i.test(parts[0]))return null;
   if(parts.some(s=>s==="."||s===".."||!s||!/^[-a-z0-9_. ]+$/i.test(s)))return null;
   const name=parts.at(-1);
   const dot=name.lastIndexOf(".");
   if(dot<0 || !allowedDraftExt.has(name.slice(dot).toLowerCase()))return null;
   return {folder:parts[0],folderPath:join(ROOT,"01-conteudo",parts[0])};
 }

 const SCOPED_TTL_MS=8*60*60*1000;
 const SCOPED_ACTIVITY_WINDOW_MS=24*60*60*1000;
 const normalizeUserText=s=>String(s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
 async function loadActiveGrant(sessionId,client){
   if(!/^ses_[A-Za-z0-9]+$/.test(sessionId||""))return null;
   const file=join(SCOPE_DIR,sessionId+".json");
   let grant;
   try{grant=JSON.parse(await fs.readFile(file,"utf8"))}catch{return null}
   if(grant?.session!==sessionId || !/^carrossel-[a-z0-9-]{5,80}$/i.test(grant.folder||""))return null;
   const now=Date.now();
   if(Number(grant.expires_at)>now)return grant;
   // Renew only when a REAL user has recently asked to create, continue, edit or render the SAME project.
   if(!client?.session?.messages)return null;
   try{
     const response=await client.session.messages({path:{id:sessionId},query:{directory:ROOT,limit:80}});
     const messages=response.data;
     if(!Array.isArray(messages))return null;
     const latest=[...messages].reverse().find(m=>m.info?.role==="user");
     if(!latest)return null;
     const at=Number(latest.info?.time?.created||latest.info?.time?.updated||0);
     if(!at || at>now+60000 || now-at>SCOPED_ACTIVITY_WINDOW_MS)return null;
     const text=normalizeUserText((latest.parts||[]).filter(x=>x.type==="text").map(x=>x.text||"").join(" "));
     if(/^\s*(cancele|cancelar|pare|stop|nao faca|nao crie)\b/.test(text))return null;
     if(!/\b(carrossel|continue|continuar|escuro|claro|edite|editar|corrija|corrigir|finalize|finalizar|renderizar|teste)\b/.test(text))return null;
     grant={...grant,expires_at:now+SCOPED_TTL_MS,renewed_at:now};
     await fs.writeFile(file,JSON.stringify(grant),"utf8");
     return grant;
   }catch{return null}
 }
 async function parentGrant(input,client){
   if(!client?.session?.get)return null;
   try{
     const response=await client.session.get({path:{id:input.sessionID},query:{directory:ROOT}});
     const sub=response.data||response;
     if(!["executor-codigo","executor-visual","auditor-deus","general"].includes(sub.agent))return null;
     const parent=String(sub.parentID||"");
     if(!/^ses_[A-Za-z0-9]+$/.test(parent))return null;
     return await loadActiveGrant(parent,client);
   }catch{return null}
 }
 async function resumeDraft(input, client, expectedFolder) {
   const sid = input.sessionID;
   if (!client?.session?.messages || !/^ses_[A-Za-z0-9]+$/.test(sid || "")) return null;
   try {
     const registry = JSON.parse(await fs.readFile(path("00-regras/RASCUNHOS-RETOMAVEIS.json"), "utf8"));
     const result = await client.session.messages({path:{id:sid},query:{directory:ROOT,limit:50}});
     const latest = (result.data || []).filter(m => m.info?.role === "user")
       .sort((a,b) => (b.info.time?.created || 0) - (a.info.time?.created || 0))[0];
     const command = normalizeUserText((latest?.parts || [])
       .filter(p => p.type === "text" && !p.synthetic && !p.ignored).map(p => p.text).join(" ")).trim();
     const folder = /^retomar rascunho (carrossel-[a-z0-9-]{5,80})$/.exec(command)?.[1];
     const now = Date.now();
     const created = Number(latest?.info?.time?.created || 0);
     if (!folder || (expectedFolder && folder !== expectedFolder) || !Array.isArray(registry)
         || !registry.includes(folder) || created > now || now - created >= SCOPED_TTL_MS
         || !existsSync(path("01-conteudo/" + folder + "/carrossel.html"))) return null;
     return {session:sid, folder, expires_at:created + SCOPED_TTL_MS};
   } catch { return null; }
 }

 async function scopedProduction(input,dst,client){
   const target=scopedDraftTarget(dst);
   if(!target||!client||!/^ses_[A-Za-z0-9]+$/.test(input?.sessionID||""))return false;
   const existing=await loadActiveGrant(input.sessionID,client);
   if(existing)return existing.folder===target.folder;
   const parent=await parentGrant(input,client);
   if(parent)return parent.folder===target.folder;
   // A new session must start in a NEW directory, never overwrite a published or historical package.
   if(existsSync(target.folderPath))return Boolean(await resumeDraft(input, client, target.folder));
   let messages;
   try{
     const result=await client.session.messages({path:{id:input.sessionID},query:{directory:ROOT,limit:50}});
     messages=result.data;
   }catch{return false}
   if(!Array.isArray(messages))return false;
   const users=messages.filter(m=>m.info?.role==="user")
       .map(m=>normalizeUserText((m.parts||[]).filter(p=>p.type==="text"&&!p.synthetic&&!p.ignored).map(p=>p.text||"").join(" ")));
   if(!users.some(t=>/\b(crie|criar|produza|produzir|faca|monte|gere|gerar)\b.{0,150}\b(novo\s+)?carrossel\b/.test(t)))return false;
   const last=users.at(-1)||"";
   if(/^\s*(cancele|cancelar|pare|stop|nao faca|nao crie)/.test(last))return false;
   const now=Date.now();
   const grantFile=join(SCOPE_DIR,input.sessionID+".json");
   const payload={session:input.sessionID,folder:target.folder,created_at:now,expires_at:now+SCOPED_TTL_MS};
   try{
     await fs.mkdir(SCOPE_DIR,{recursive:true});
     await fs.writeFile(grantFile,JSON.stringify(payload),{encoding:"utf8",flag:"wx"});
   }catch{return false}
   return true;
 }
 async function draftGrantForSession(input,client){
   if(!/^ses_[A-Za-z0-9]+$/.test(input?.sessionID||""))return null;
   return (await loadActiveGrant(input.sessionID,client)) || (await parentGrant(input,client)) || (await resumeDraft(input,client));
 }

 // Local Playwright previews are restricted to the HTML in the user's current draft.
 // No clicks, evaluate, arbitrary websites, uploads or Instagram automation via MCP.
 const PREVIEW_SCOPE_BY_SESSION=new Map();
 function safeLocalPreview(urlText,grant){
   if(!grant||typeof urlText!=="string")return null;
   try{
     const uri=new URL(urlText);
     if(uri.protocol!=="file:" || (uri.hostname && uri.hostname!=="localhost") || uri.search || uri.hash)return null;
     const local=decodeURIComponent(uri.pathname.replace(/^\/(?=[a-z]:)/i,""));
     if(!isAbsolute(local) || !/\.html$/i.test(local))return null;
     const dst=dest(local,ROOT),draft=scopedDraftTarget(dst);
     if(!draft || draft.folder!==grant.folder || !existsSync(local))return null;
     return local;
   }catch{return null}
 }

 function safeRenderBash(command,grant){
   if(!grant || typeof command!=="string" || command.length>1400)return false;
   const cmd=command.trim();
   if(/[;&\r\n\x60><$]/.test(cmd))return false;
   const tok='(?:"([^"]+)"|(\\S+))';
   const re=new RegExp('^node(?:\\.exe)?\\s+'+tok+'\\s+'+tok+'\\s+'+tok+'(?:\\s+--exigir-cenas)?$','i');
   const m=re.exec(cmd);
   if(!m)return false;
   const script=m[1]||m[2],html=m[3]||m[4],out=m[5]||m[6];
   const base=normalizePath(path("01-conteudo/"+grant.folder));
   const realBase=physical(path("01-conteudo/"+grant.folder));
   return !!realBase && normalizePath(projectPath(script))===normalizePath(path("04-skills/carrossel/scripts/exportar.mjs"))
      && under(normalizePath(projectPath(html)),base) && html.toLowerCase().endsWith(".html")
      && under(normalizePath(projectPath(out)),base)
      && physical(projectPath(out)) && under(physical(projectPath(out)),realBase);
 }


 // Refuse speculative/no-op edits before OpenCode's native exact-match tool runs.
 // This does not bypass file scope restrictions or modify any file.
 const EDIT_FAILS=new Map();
 function ensureExactEdit(args,requested,sid){
   if(typeof args.oldString!=="string"||typeof args.newString!=="string")return;
   const key=String(sid||"")+":"+String(requested||"");
   const failures=EDIT_FAILS.get(key)||0;
   if(args.oldString===args.newString){
     EDIT_FAILS.set(key,failures+1);
     throw new Error("[IG EDITAR] Edicao sem efeito: oldString e newString sao identicos. NAO repetir edit. Leia o HTML atual e corrija apenas o que realmente existe.");
   }
   const pathToFile=args.filePath||args.file_path||args.path||"";
   if(!pathToFile)return;
   const src=isAbsolute(pathToFile)?pathToFile:resolve(ROOT,pathToFile);
   if(!existsSync(src))return;
   let actual;
   try{actual=readFileSync(src,"utf8")}catch{return}
   if(!actual.includes(args.oldString)){
     EDIT_FAILS.set(key,failures+1);
     const repeated=failures+1>=2 ? " SEGUNDA FALHA: nao tente uma terceira edicao especulativa; releia o arquivo e, se necessario, use write com o conteudo integral verificado.":"";
     throw new Error("[IG EDITAR] oldString NAO aparece no arquivo atual. Chame read NO ARQUIVO EXATO, copie o trecho literal, confira acentos, espacos e caixa; depois edite. Nao invente um trecho."+repeated);
   }
   EDIT_FAILS.delete(key);
 }

 function authorize(input){
   let a;
   try{a=JSON.parse(readFileSync(AUTH,"utf8"));}catch{return {reason:"ausente-ou-malformada"};}
   if(!a || !["PRODUZIR","PUBLICAR"].includes(a.nivel)||!Array.isArray(a.pastas)||!a.pastas.every(safeName))return {reason:"escopo-invalido"};
   if(typeof a.session_id!=="string" || a.session_id!==input?.sessionID)return {reason:"sessao-divergente"};
   if(typeof a.task!=="string" || !safeName(a.task)||!(a.nivel==="PRODUZIR"?a.task.startsWith("producao-"):a.task.startsWith("publicar-")))return {reason:"tarefa-invalida"};
   if(typeof a.nonce!=="string"||a.nonce.length<16||typeof a.assinatura!=="string"||!/^base64:/.test(a.assinatura))return {reason:"assinatura-invalida"};
   const deadline=Date.parse(a.expires_at);
   if(!Number.isFinite(deadline)||deadline<=Date.now()||deadline-Date.now()>(a.nivel==="PUBLICAR"?600000:1800000))return {reason:"ttl-invalido-ou-expirado"};
   try{
     const ok=verify(null,Buffer.from(canonical(a)),readFileSync(KEY,"utf8"),Buffer.from(a.assinatura.slice(7),"base64"));
     if(!ok)return {reason:"assinatura-nao-verificada"};
   }catch{return {reason:"chave-ou-assinatura-invalidas"};}
   if(a.nivel==="PUBLICAR" && existsSync(LOCK))return {reason:"bloqueio-publicacao-ativo"};
   return {grant:a};
 }
 return async ({directory,client})=>({
  "tool.execute.before":async(input,output)=>{
    const cwd=directory||ROOT;
    try { appendFileSync(IG_HOOK_DIAG_20261117, JSON.stringify({at:new Date().toISOString(),event:"HOOK_CALLED",tool:String(input?.tool||""),session:input?.sessionID||null})+"\n"); } catch {}
    if(!under(normalizePath(cwd),R))return;
    const tool=String(input?.tool||"").toLowerCase(),args=output?.args||{};
    const raw=args.filePath||args.file_path||args.path||args.destination||args.output_path||"";
    const requested=String(raw||args.command||tool);
    // Read tools are not given write privileges; unknown tools fail-closed.
    if(TOOLS_READ.has(tool)){
      await logDecision("ANALISAR",requested,"PERMITIDO","leitura");
      return;
    }
    if(tool==="instagram_gpu")return;
    if(tool==="task" && ["executor-codigo","executor-visual","auditor-deus","general"].includes(args.subagent_type))return;
    if(tool==="instagram_publicador")return;
    // Navigation is limited to the current local HTML. This does not authorize
    // Playwright clicks, evaluate, interactive browser access or publication.
    if(tool.startsWith("playwright_browser_")){
      const grant=await draftGrantForSession(input,client);
      const sid=input?.sessionID;
      if(tool==="playwright_browser_resize" && grant && args.width===1080 && args.height===1350){
        await logDecision("ANALISAR",requested,"PERMITIDO","preview-redimensionamento-1080x1350");
        return;
      }
      if(tool==="playwright_browser_navigate"){
        const local=safeLocalPreview(args.url,grant);
        if(local){
          PREVIEW_SCOPE_BY_SESSION.set(sid,local);
          await logDecision("ANALISAR",requested,"PERMITIDO","preview-html-local-da-pasta-autorizada");
          return;
        }
      }
      if(grant && PREVIEW_SCOPE_BY_SESSION.has(sid)){
        const local=PREVIEW_SCOPE_BY_SESSION.get(sid);
        const prefix=normalizePath(path("01-conteudo/"+grant.folder));
        if(under(normalizePath(local),prefix)){
          if(tool==="playwright_browser_snapshot"){
            await logDecision("ANALISAR",requested,"PERMITIDO","preview-inspecao-local");
            return;
          }
          if(tool==="playwright_browser_take_screenshot"){
            const target=args.filename||args.path||args.outputPath||null;
            if(!target || (typeof target==="string" && /\.png$/i.test(target) &&
               under(normalizePath(projectPath(target)),prefix) &&
               under(physical(projectPath(target)),physical(path("01-conteudo/"+grant.folder))))){
              await logDecision("ANALISAR",requested,"PERMITIDO","preview-screenshot-pasta-autorizada");
              return;
            }
          }
        }
      }
      await logDecision("ANALISAR",requested,"NEGADO","playwright-fora-do-html-local-autorizado");
      throw new Error("[IG ANALISAR] Playwright limitado ao HTML local do carrossel autorizado; renderize pelo exportar.mjs.");
    }
    // Analise/QA nao e publicacao: so comandos literalmente reconhecidos.
    if(tool==="bash"){
      const diagnostic=safeDiagnosticBash(args.command);
      if(diagnostic){
        output.args.command=diagnostic;
        await logDecision("ANALISAR",requested,"PERMITIDO","bash-diagnostico-somente-leitura");
        return;
      }
      const grant=await draftGrantForSession(input,client);
      if(safeRenderBash(args.command,grant)){
        await logDecision("PRODUZIR",requested,"PERMITIDO","renderizacao-escopo-sessao");
        return;
      }
      if(safeTextAndImageQABash(args.command,grant) || safeAnalysisBash(args.command)){
        await logDecision("ANALISAR",requested,"PERMITIDO","bash-qa-padrao-restrito");
        return;
      }
      await logDecision("ANALISAR",requested,"NEGADO","bash-fora-da-lista-segura");
      throw new Error("[IG ANALISAR] Bash nao autorizado para este comando. Use read/glob ou QA padronizado; publicacao deve passar por instagram_publicador.");
    }
    if(TOOLS_WRITE.has(tool) && !args.patches && !args.files && !args.edits){
      const dst=dest(raw,cwd);
      if(await scopedProduction(input,dst,client)){
        if(tool==="edit")ensureExactEdit(args,raw,input.sessionID);
        await logDecision("PRODUZIR",requested,"PERMITIDO","criacao-nova-autorizada-pela-ordem");
        return;
      }
    }
    const result=authorize(input);
    if(!result.grant){
      await logDecision("ANALISAR",requested,"NEGADO",result.reason);
      throw new Error("[IG ANALISAR] "+result.reason);
    }
    const a=result.grant;
    if(TOOLS_WRITE.has(tool)){
      // Reject undocumented bulk file arrays and unrecognized patching modes.
      if(args.patches||args.files||args.edits){
        await logDecision(a.nivel,requested,"NEGADO","escrita-em-lote-nao-auditada");
        throw new Error("[IG] Escrita em lote nao auditada");
      }
      const target=dest(raw,cwd);
      if(permitted(target,a)){
        if(tool==="edit")ensureExactEdit(args,raw,input.sessionID);
        await logDecision(a.nivel,target.lexical,"PERMITIDO","destino-autorizado");
        return;
      }
      await logDecision(a.nivel,requested,"NEGADO","caminho-proibido-ou-symlink");
      throw new Error("[IG "+a.nivel+"] Caminho proibido");
    }
    await logDecision(a.nivel,requested,"NEGADO","ferramenta-nao-autorizada");
    throw new Error("[IG "+a.nivel+"] Ferramenta nao autorizada: "+tool);
  }
 });
}
export const InstagramReadOnlyGuard = createInstagramGuard();
export default InstagramReadOnlyGuard;





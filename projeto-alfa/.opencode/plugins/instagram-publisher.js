import { tool } from "@opencode-ai/plugin";
import { readFile, readdir, realpath, writeFile, rename, unlink, mkdir } from "node:fs/promises";
import { createHash, randomUUID } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";

const root = "I:/Projetos/Instagram-RobsonAlencar";
const account = "pastorrobsonalencar";
const python = "C:/Users/ROBSON ALENCAR/AppData/Local/Programs/Python/Python312/python.exe";
const run = promisify(execFile);
const normalize = value => value.normalize("NFD").replace(/\p{Diacritic}/gu, "").trim().toLowerCase();
const text = message => message.parts.filter(part => part.type === "text" && !part.synthetic && !part.ignored).map(part => part.text).join("\n");

async function fileInside(parent, target) {
  const actual = await realpath(target);
  const relative = path.relative(parent, actual);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) throw Error("Arquivo fora do pacote.");
  return actual;
}

async function packageSnapshot(folder, captionName) {
  if (!folder.split(/[\\/]/).every(part => /^[\p{L}\p{N}_ .-]+$/u.test(part) && part !== "." && part !== "..")) throw Error("Pasta invalida.");
  if (!/^[\p{L}\p{N}_ .-]+\.txt$/iu.test(captionName)) throw Error("LEGENDA_ARQUIVO_ESPERADO: passe legenda.txt, o nome do arquivo dentro da pasta. O texto integral deve estar nesse arquivo.");
  const content = await realpath(path.join(root, "01-conteudo"));
  const project = await fileInside(content, path.join(content, folder));
  const caption = await fileInside(project, path.join(project, captionName));
  // Carrosseis novos podem ter os PNGs diretamente na pasta do trabalho.
  const outCandidate=path.join(project,"out");
  const out=await realpath(outCandidate).catch(error=>{
    if(error.code!=="ENOENT")throw error;
    return project;
  });
  if(out!==project)await fileInside(project,out);
  const entries = (await readdir(out)).sort();
  const slides = entries.filter(name => /^slide-.*\.png$/.test(name));
  const files = slides.length ? slides : entries.filter(name => /\.(mp4|png|jpe?g)$/i.test(name));
  if (!files.length || files.length > 10 || (files.some(name => /\.mp4$/i.test(name)) && files.length !== 1)) throw Error("Midia invalida.");
  const captionBytes = await readFile(caption);
  const captionText = captionBytes.toString("utf8").replace(/\r\n?/g,"\n").trim();
  if (!captionText || captionText.length > 2200) throw Error("Legenda vazia ou longa demais.");
  const hash = createHash("sha256").update(JSON.stringify([folder, captionName, files])).update(captionBytes);
  for (const name of files) hash.update(createHash("sha256").update(await readFile(await fileInside(out, path.join(out, name)))).digest());
  // Universal identity contract: EVERY future multipage carousel must match the approved signature.
  if(files.length>1){
    if(files.some(name=>!/^slide-\d{2}\.png$/i.test(name)))
      throw Error("CARROSSEL_INVALIDO: nomeie os PNGs sequencialmente slide-01.png a slide-10.png.");
    const script=path.join(root,"02-scripts","validar_padrao_carrossel.py");
    let check;
    try{
      check=await run(python,["-X","utf8",script,"--pasta",project,"--expected",String(files.length)],
        {cwd:root,windowsHide:true,timeout:60000});
    }catch(error){
      const details=String(error.stdout||error.stderr||error.message);
      throw Error("ASSINATURA_OU_SETA_FORA_DO_PADRAO: "+details.slice(-1800));
    }
    const proof=JSON.parse(check.stdout);
    if(proof.aprovado_geometria!==true)
      throw Error("PADRAO_VISUAL_REPROVADO: "+JSON.stringify(proof.falhas||[]));
  }
  return { caption, captionText, files, mediaFolder:path.relative(content,out).replaceAll("\\","/"), hash: hash.digest("hex") };
}

export const InstagramPublisher = async ({ directory, client }) => {
  if (path.resolve(directory).toLowerCase() !== path.resolve(root).toLowerCase()) return {};
  const pending = new Map();
  const stateDir=path.join(root,"03-agendamentos","publicador","perguntas");
  const stateFile=sid=>{
    if(!/^ses_[A-Za-z0-9]+$/.test(sid))throw Error("Sessao invalida.");
    return path.join(stateDir,sid+".json");
  };
  const loadState=async sid=>{
    const live=pending.get(sid);if(live)return live;
    try{
      const state=JSON.parse(await readFile(stateFile(sid),"utf8"));
      if(state.sessionID!==sid||Date.now()-state.createdAt>45*60*1000)return null;
      pending.set(sid,state);return state;
    }catch(e){if(e.code==="ENOENT")return null;throw e;}
  };
  const saveState=async (sid,info)=>{
    await mkdir(stateDir,{recursive:true});
    const state={...info,sessionID:sid,createdAt:Date.now()};
    const tmp=stateFile(sid)+"."+randomUUID()+".tmp";
    try{await writeFile(tmp,JSON.stringify(state,null,2),"utf8");await rename(tmp,stateFile(sid))}
    finally{await unlink(tmp).catch(()=>{})}
    pending.set(sid,state);
  };
  const clearState=async sid=>{pending.delete(sid);await unlink(stateFile(sid)).catch(e=>{if(e.code!=="ENOENT")throw e})};
  const messages = async sessionID => {
    const result = await client.session.messages({ path: { id: sessionID }, query: { directory, limit: 12 } });
    if (!Array.isArray(result.data)) throw Error("Nao consegui verificar as mensagens da sessao.");
    return result.data;
  };
  return { tool: {
    instagram_publicador: tool({
      description: "Revisa material, consulta agendamentos ou publica/agende somente com aprovacao e confirmacao real do Windows.",
      args: {
        etapa: tool.schema.enum(["consultar_pacote", "revisar", "decidir", "publicar", "consultar_bio", "aplicar_bio", "consultar_agendamentos"]),
        pasta: tool.schema.string().optional(),
        legenda: tool.schema.string().describe("Nome do arquivo TXT dentro da pasta, por exemplo legenda.txt. Nunca passe o texto integral.").optional(), bio: tool.schema.string().optional(),
        quando: tool.schema.string().optional(),
        acao: tool.schema.enum(["publicar","agendar","corrigir","refinar","refazer","rascunho","cancelar"]).optional()
      },
      async execute(args, context) {
        if (path.resolve(context.directory).toLowerCase() !== path.resolve(root).toLowerCase()) throw Error("Sessao fora do projeto.");
        const history = await messages(context.sessionID);
        const lastUser = history.findLast(item => item.info.role === "user");
        if (!lastUser) throw Error("Mensagem do usuario ausente.");
        if (args.etapa === "consultar_bio" || args.etapa === "aplicar_bio") {
          const argv = [path.join(root,"02-scripts/editar-bio.cjs")];
          if (args.etapa === "aplicar_bio") {
            if (!args.bio || text(lastUser).trim() !== "Aplicar bio:\n" + args.bio) throw Error("Para aprovar, envie Aplicar bio: e, na linha seguinte, o texto exato.");
            argv.push(Buffer.from(args.bio,"utf8").toString("base64"));
          }
          const result = await run("node",argv,{cwd:root,windowsHide:true,timeout:95000});
          return result.stdout.trim();
        }
        if (args.etapa === "consultar_agendamentos") {
          // Read-only status. No publication, scheduling or access to credentials.
          const result = await run(python, ["02-scripts/status-agendamento.py", "--json"], { cwd: root, timeout: 25000, windowsHide: true });
          return result.stdout.trim();
        }
        if (!args.pasta) throw Error("Informe a pasta do carrossel relativa a 01-conteudo.");
        if (!args.legenda) args = {...args, legenda:"legenda.txt"};
        const pack = await packageSnapshot(args.pasta, args.legenda);
        if (args.quando && (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d-03:00$/.test(args.quando) || !(Date.parse(args.quando) > Date.now()))) throw Error("Horario futuro invalido.");
        if (args.etapa === "publicar") throw Error("ETAPA_ANTIGA_DESATIVADA: faca revisar -> pergunta -> decidir.");
        if (args.etapa === "revisar" || args.etapa === "consultar_pacote") {
          // Generate the UUID BEFORE the QA audit, allowing hashes and approval
          // to reference the exact same future job. Never invent approval receipts.
          const prior = await loadState(context.sessionID);
          let auditJobId = null;
          if (args.etapa === "consultar_pacote" || args.etapa === "revisar") {
            try {
              const auditPath = path.join(root,"01-conteudo",pack.mediaFolder,"aprovacao-visual.json");
              const audit = JSON.parse((await readFile(auditPath,"utf8")).replace(/^\uFEFF/,""));
              if (typeof audit.job_id === "string" && /^[a-z0-9_-]{8,80}$/i.test(audit.job_id)) auditJobId = audit.job_id;
            } catch (error) {
              if (error.code !== "ENOENT" && !(error instanceof SyntaxError)) throw error;
            }
          }
          const jobId = auditJobId || (prior && prior.hash === pack.hash && (prior.quando||null) === (args.quando||null)
            ? prior.jobId : randomUUID());
          if (auditJobId) {
            const receipt = path.join("03-agendamentos","publicador","processados",auditJobId+".json");
            let done;
            try { done = JSON.parse((await readFile(path.join(root,receipt),"utf8")).replace(/^\uFEFF/,"")); }
            catch (err) { if (err.code !== "ENOENT") throw err; }
            if (done?.id === auditJobId && done.account === account && done.status === "publicado") {
              return JSON.stringify({status:"JA_PUBLICADO",job_id:auditJobId,conta:account,
                comprovante:receipt,publicado_em:done.attempt_finished_at,
                proximo_passo:"Informe o recibo da publicacao anterior e encerre.",publicacao_executada:false});
            }
          }
          const q={id:jobId,status:"aprovado",approved_by:"PREFLIGHT_NAO_AUTORIZADO",
            account,scheduled_at:args.quando||new Date(Date.now()-5000).toISOString(),
            files:pack.files.map(n=>path.join(root,"01-conteudo",pack.mediaFolder,n)),caption:pack.captionText};
          const encoded=Buffer.from(JSON.stringify(q),"utf8").toString("base64");
          const check=await run(python,["02-scripts/avaliar_decisao_carrossel.py","--payload",encoded],
            {cwd:root,timeout:35000,windowsHide:true});
          const qa=JSON.parse(check.stdout);
          if (args.etapa === "consultar_pacote") {
            const failures = qa.falhas || [];
            const editorial = failures.filter(code => /LEGENDA|EDITORIAL/.test(code));
            const visual = failures.filter(code => /VISUAL|AUDITOR|SLIDES_MUDARAM|APROVACAO_DE_OUTRA_TAREFA/.test(code));
            return JSON.stringify({pasta:args.pasta, arquivo_legenda:args.legenda,
              midias:pack.files, qa_aprovado:qa.qa_concluido, falhas:failures,
              falhas_editoriais:editorial, falhas_visuais:visual,
              proximo_passo:qa.qa_concluido ? "Use revisar para apresentar o pacote e confirmar a ordem."
                : "Trate somente as falhas atuais. Se a lista editorial estiver vazia, preserve a legenda e o recibo.",
              agendamento_criado:false, publicacao_executada:false});
          }
          await saveState(context.sessionID,{user:lastUser.info.id,hash:pack.hash,
            quando:args.quando||null,jobId,pasta:args.pasta,legenda:args.legenda,qa});
          const options=qa.qa_concluido?["Publicar agora","Agendar","Refinar","Refazer","Cancelar"]:
            ["Corrigir verificacoes","Refinar","Refazer","Manter rascunho","Cancelar"];
          return JSON.stringify({conta:account,pasta:args.pasta,midias:pack.files,
            legenda_integral:pack.captionText,job_id:jobId,quando:args.quando||"agora",
            qa_aprovado:qa.qa_concluido,falhas:qa.falhas,
            pergunta_question:{header:"Decisao Instagram",
              question:"Carrossel "+jobId+". "+(qa.qa_concluido?
                "QA concluido. Qual acao autoriza?":"QA pendente. O que devemos corrigir?"),
              options:options.map(label=>({label,description:label==="Refinar"?
                "Editar material e revalidar":label==="Refazer"?"Nova versao e novo QA":
                label==="Cancelar"?"Nenhuma publicacao":label==="Manter rascunho"?
                "Manter bloqueado":label==="Corrigir verificacoes"?
                "Corrigir erros identificados, sem publicar":label==="Agendar"?
                "Exige horario futuro em -03:00":"Publicar so com QA aprovado"})),
              multiple:false},
            instrucao:"Copie pergunta_question literalmente na ferramenta separada question. Preserve o identificador e os rotulos. Depois da resposta chame decidir uma vez, sem repetir revisar. Para publicar agora omita quando. Mostrar os PNGs e a legenda integral. Usar a ferramenta question; aguardar resposta real do usuario. Somente depois chamar decidir com a acao exata. Nao autorizar por conta propria."
          });
        }
        if(args.etapa!=="decidir")throw Error("Etapa desconhecida.");
        const approval=await loadState(context.sessionID);
        if(!approval)throw Error("SEM_REVISAO_PENDENTE: Chame consultar_pacote com a mesma pasta e legenda.txt. Se houver falha, trate a falha retornada. Se o QA passar, chame revisar com o horario futuro autorizado (ou sem horario para publicar agora), apresente o pacote e obtenha nova decisao. Nao repita decidir nesta revisao.");
        if(Date.now()-approval.createdAt>45*60*1000)throw Error("REVISAO_EXPIRADA: Chame consultar_pacote com a mesma pasta e legenda.txt. Se houver falha, trate a falha retornada. Se o QA passar, chame revisar com o horario futuro autorizado (ou sem horario para publicar agora), apresente o pacote e obtenha nova decisao. Nao repita decidir nesta revisao.");
        if(args.pasta!==approval.pasta || args.legenda!==approval.legenda ||
           (args.quando||null)!==approval.quando || pack.hash!==approval.hash)
          throw Error("ARQUIVOS_HORARIO_OU_LEGENDA_MUDARAM: nova revisao obrigatoria.");
        const aliases=new Map([
          ["publicar agora","publicar"],["publicar","publicar"],
          ["pode publicar","publicar"],["publique agora","publicar"],
          ["agendar","agendar"],["pode agendar","agendar"],
          ["corrigir verificacoes","corrigir"],["corrigir","corrigir"],
          ["refinar","refinar"],["refazer","refazer"],
          ["manter rascunho","rascunho"],["rascunho","rascunho"],
          ["cancelar","cancelar"]
        ]);
        const choice=value=>{
          const normalized=normalize(String(value||"")).replace(/[.!?]+$/,"").replace(/ \(recomendado\)$/,"");
          const direct=aliases.get(normalized);
          if(direct)return direct;
          // Aceitar apenas uma ordem curta, afirmativa e inequívoca.
          // Horarios misturados com "agora" nao sao inferidos.
          if(/^(?:por favor )?(?:publique|poste|publicar|postar)(?: o carrossel| este carrossel| esse post)? agora$/.test(normalized))return "publicar";
          if(/^(?:por favor )?(?:agende|agendar)(?: o carrossel| esse post)?$/.test(normalized))return "agendar";
          return null;
        };
        let decision=null,receipt=null;
        // Uma ordem explicita na mensagem original ja e autorizacao: nao exija
        // segunda pergunta apenas por formalidade. Ainda confira QA, conta,
        // hashes, legenda integral e autorizacao no verificador Python.
        // O verificador confere o ID real da mensagem na sessao OpenCode.
        const directChoice = choice(text(lastUser));
        if (directChoice && (lastUser.info.id !== approval.user ||
            (directChoice === "publicar" && !approval.quando) ||
            (directChoice === "agendar" && Boolean(approval.quando)))) {
          decision = directChoice;
          receipt = {message:lastUser.info.id,channel:"chat"};
        }
        if(!decision){
          for(const msg of history.slice().reverse()){
            for(const part of (msg.parts||[]).slice().reverse()){
              if(part.type!=="tool"||part.tool!=="question"||part.state?.status!=="completed")continue;
              const question = part.state.input?.questions?.[0]?.question || "";
              const slug = path.basename(approval.pasta).replace(/^carrossel-/, "");
              const words = question.toLowerCase().split(/[^\p{L}\p{N}_-]+/u);
              if (!question.includes(approval.jobId) && !(args.acao === "publicar" &&
                  !approval.quando && words.some(word => word.replace(/^carrossel-/, "") === slug.toLowerCase()))) continue;
              let output=part.state.output;
              if(typeof output==="string"){
                try{output=JSON.parse(output)}catch{output={answers:[[output]]}}
              }
              const answerTime = part.state.time?.end;
              if (!Number.isFinite(answerTime) || answerTime < approval.createdAt) continue;
              const arr = part.state.metadata?.answers ?? output?.answers ?? output?.answer;
              const response=Array.isArray(arr)?arr.flat(Infinity).filter(x=>typeof x==="string"):[];
              if(response.length!==1)continue;
              const option=choice(response[0]);
              if(!option)continue;
              decision=option;
              receipt={message:lastUser.info.id,channel:"question",partID:part.id};
              break;
            }
            if(decision)break;
          }
        }
        if(!decision)throw Error("RESPOSTA_NAO_ENCONTRADA: apresente question e espere escolha real do usuario.");
        if(!args.acao || args.acao!==decision)throw Error("ACAO_DIVERGENTE: a escolha real foi "+decision);
        if(["corrigir","refinar","refazer","rascunho","cancelar"].includes(decision)){
          await clearState(context.sessionID);
          return JSON.stringify({id:approval.jobId,acao:decision,
            status:decision==="cancelar"?"CANCELADO":decision==="rascunho"?"RASCUNHO":"VOLTAR_A_EDICAO",
            publicar:false,agendar:false,
            proximo:"Se modificar os arquivos, refaca o QA e apresente nova pergunta antes de qualquer postagem."});
        }
        if(!approval.qa?.qa_concluido)throw Error("QA_REPROVADO: corrija os erros antes de publicar ou agendar.");
        if(decision==="agendar"&&!approval.quando)
          return JSON.stringify({id:approval.jobId,status:"HORARIO_NECESSARIO",
            pergunta:"Qual data e hora futuras para agendar? Refa?a a revisao com esse horario antes de confirmar."});
        if(decision==="publicar"&&approval.quando)throw Error("HORARIO_ANTERIOR: revise sem agendamento para publicar agora.");
        if(decision==="agendar"&&!(Date.parse(approval.quando)>Date.now()))throw Error("HORARIO_VENCIDO: revise data futura.");
        const prior=history.some(msg=>msg.info.role==="assistant" &&
          text(msg).replace(/\s+/g," ").includes(pack.captionText.replace(/\s+/g," ")));
        if(!prior)throw Error("LEGENDA_NAO_EXIBIDA: apresente legenda completa e imagens antes da escolha.");
        // New QA run prevents approval of files changed after the question.
        const q={id:approval.jobId,status:"aprovado",approved_by:"PREFLIGHT_NAO_AUTORIZADO",
          account,scheduled_at:approval.quando||new Date(Date.now()-5000).toISOString(),
          files:pack.files.map(name=>path.join(root,"01-conteudo",pack.mediaFolder,name)),caption:pack.captionText};
        const encoded=Buffer.from(JSON.stringify(q),"utf8").toString("base64");
        const check=await run(python,["02-scripts/avaliar_decisao_carrossel.py","--payload",encoded],
          {cwd:root,windowsHide:true,timeout:35000});
        const qa=JSON.parse(check.stdout);
        if(!qa.qa_concluido)throw Error("QA_REPROVADO_AGORA: "+qa.falhas.join(", "));
        await clearState(context.sessionID);
        const argv=["02-scripts/postar-agora.py","--pasta",approval.pasta,
          "--legenda",pack.caption,"--conta",account,"--id",approval.jobId,
          "--sessao",context.sessionID,"--resposta",receipt.message,"--autorizado-pelo-usuario"];
        if(receipt.channel==="question"){
          if(!/^prt_[A-Za-z0-9]+$/.test(receipt.partID||""))
            throw Error("PROVENIENCIA_DA_PERGUNTA_INVALIDA");
          argv.push("--pergunta",receipt.partID);
        }
        if(approval.quando)argv.push("--quando",approval.quando);
        try{
          const result=await run(python,argv,{cwd:root,timeout:290000,windowsHide:true});
          return JSON.stringify({id:approval.jobId,acao:decision,
            status:"EXECUCAO_RETORNOU_CONFERIR_COMPROVANTE",resultado:result.stdout.trim(),
            sem_confirmacao:"Se o Instagram nao retornar prova real, nao classifique como publicado."});
        }catch(error){
          throw Error("ACAO_NAO_CONFIRMADA: "+String(error.stderr||error.message).slice(-1500)+
            " Nao tente novamente automaticamente.");
        }
      }
    })
  } };
};

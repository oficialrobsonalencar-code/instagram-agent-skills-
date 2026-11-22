// OpenCode 1.x project-scoped continuity and quality guidance.
// Does not execute commands, mutate permissions, or touch credentials.
import { resolve, normalize } from "node:path";

const RULES = [
  "[INSTAGRAM ROBSON ALENCAR - CONTROLE DE QUALIDADE]",
  "PESQUISA INSTAGRAM: quando o usuario pedir temas atuais, tendencias ou repercussao, consultar 00-regras/LAST30DAYS-USO-INSTAGRAM.md e carregar .opencode/skills/instagram-last30days/SKILL.md. Apenas investigar e citar fontes; nunca tomar a existencia de imagem, pasta, corpus ou referencia como licenca de uso. Proibido ler cookies, coletar credenciais, instalar componentes, pagar por APIs, agendar ou publicar sem autorizacao especifica.",
  "REGRA ZERO: localizar uma foto, documento, arquivo no mapa, pasta 00-usuario, referencia, sessao antiga ou output NAO concede autorizacao para usar seu conteudo. Exija que o usuario indique o arquivo expressamente NA TAREFA ATUAL; se nao indicou, produza material ORIGINAL, sem copiar historico. Leia 00-regras/CONTROLE-DE-FONTES-E-APROVACAO.md.",
  "PUBLICACAO: no fluxo de envio, a aprovacao da midia e da legenda autoriza a tentativa imediata pelo publicador oficial. Respeite horario futuro ou pedido de so revisao. Confira processados antes do envio e informe apenas o resultado confirmado.",
  "Leia AGENTS.md. Consulte o protocolo de entrada somente quando precisar localizar o trabalho ou entender um fluxo desconhecido.",
  "Consulte o mapa apenas se o caminho do material ou a arquitetura forem desconhecidos. Se o pacote ja estiver identificado, trabalhe nele e evite reconstruir o mapa durante a tarefa.",
  "Leia 00-regras/PERFIL-4X5-GRADE-1X1.md: arte 1080x1350, preview central 1080x1080, conteudo essencial em y=135..1215 e x=80..1000. Nunca selecione referencia antiga pelo nome do arquivo; somente use estilo de imagem expressamente escolhida pelo usuario no pedido atual.",
  "Nao escolher o caminho mais facil: se uma arte exige cenas diferentes e arquivos reais, nao entregar placeholders, fundos vazios ou templates com texto trocado; falha do motor = BLOQUEADO, nao CONCLUIDO.",
  "Criar, adaptar, editar e corrigir sao tarefas distintas. Nao recomece o trabalho aprovado; preserve os arquivos originais.",
  "Em carrosseis artisticos, use somente 04-skills/carrossel/scripts/exportar.mjs com --exigir-cenas. NAO reutilize entregas reprovadas ou caminhos isolados na quarentena.",
  "Entrega so e concluida com arquivos efetivos, PNG 1080x1350, preview da grade em previews-grade-1x1 (1080x1080), QA com retorno zero, imagens validas e revisao visual. Nao chame tentativa de sucesso.",
  "Se o QA reprovar, corrija e rode novamente; nao contorne nem desative a auditoria. Se o motor falhar, informe o bloqueio real.",
  "Nao reutilize monograma, paleta, slogan ou fonte das propostas reprovadas como marca oficial.",
  "Verifique a tipografia em tamanho de celular, areas seguras, pagina, arte especifica por ideia e fidelidade biblica.",
  "Criar ou revisar isoladamente nao publica. No fluxo de envio, siga as aprovacoes da midia e legenda e exija comprovante do resultado.",
  "Se uma decisao criativa essencial continuar ambigua depois de recuperar os materiais, pergunte UMA vez, sem inventar preferencias."
].join("\n");

export const QualityDirectorPlugin = async ({ directory }) => {
  // Local plugin applies only inside this specific project.
  const project = normalize(resolve("I:/Projetos/Instagram-RobsonAlencar")).toLowerCase();
  if (!directory || normalize(resolve(directory)).toLowerCase() !== project) return {};
  return {
    "experimental.chat.system.transform": async (_input, output) => {
      if (Array.isArray(output?.system) && !output.system.includes(RULES)) output.system.push(RULES);
    },
    "experimental.session.compacting": async (_input, output) => {
      if (Array.isArray(output?.context)) {
        output.context.push(
          "Preserve a tarefa Instagram atual, referencia visual, caminho do arquivo, estado do QA e bloqueios concretos. "+
          "Preserve a versao da midia, legenda, aprovacoes, conta e resultado. Siga a regra prioritaria de publicacao em AGENTS.md."
        );
      }
    }
  };
};

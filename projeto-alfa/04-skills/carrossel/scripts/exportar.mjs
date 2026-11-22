#!/usr/bin/env node
// Exporta cada slide de um carrossel HTML como PNG 1080x1350 (formato de feed do Instagram).
//
// Uso:
//   node exportar.mjs carrossel.html [pasta-de-saida] [--seletor ".slide"] [--escala 1]
//
// Cada elemento que casar com o seletor (padrão: .slide) vira um arquivo slide-01.png, slide-02.png...
// Requer o pacote "playwright" instalado na pasta de trabalho (npm i playwright).
// Usa o Chromium do Playwright; se ele não estiver baixado, tenta o Google Chrome instalado no computador.

import { resolve, join, dirname } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { mkdirSync, existsSync, renameSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const LARGURA = 1080;
const ALTURA = 1350;

function lerArgumentos(argv) {
  const posicionais = [];
  const opcoes = { seletor: '.slide', escala: 1, exigirCenas: false, exigirFidelidade: false, manifesto: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--seletor') opcoes.seletor = argv[++i];
    else if (argv[i] === '--escala') opcoes.escala = Number(argv[++i]) || 1;
    else if (argv[i] === '--exigir-cenas') opcoes.exigirCenas = true;
    else if (argv[i] === '--exigir-fidelidade') opcoes.exigirFidelidade = true;
    else if (argv[i] === '--manifest') { opcoes.manifesto = argv[++i]; opcoes.exigirFidelidade = true; }
    else posicionais.push(argv[i]);
  }
  return { arquivo: posicionais[0], saida: posicionais[1] || 'out', ...opcoes };
}

const { arquivo, saida, seletor, escala, exigirCenas, exigirFidelidade, manifesto } = lerArgumentos(process.argv.slice(2));

if (!arquivo) {
  console.error('Uso: node exportar.mjs carrossel.html [pasta-de-saida] [--seletor ".slide"] [--escala 1]');
  process.exit(1);
}
if (!existsSync(arquivo)) {
  console.error(`Arquivo não encontrado: ${arquivo}`);
  process.exit(1);
}

// PORTAO DE LEGENDA OBRIGATORIA para TODOS os novos carrosseis.
const legendaObrigatoria=resolve(dirname(resolve(arquivo)),'legenda.txt');
if(!existsSync(legendaObrigatoria)){
  console.error('LEGENDA_OBRIGATORIA_AUSENTE: crie legenda.txt ao lado de carrossel.html antes de renderizar.');
  process.exit(9);
}
const legendaLinter=resolve(dirname(fileURLToPath(import.meta.url)),'../../ig-caption/caption.py');
for(const [etapa,script,args] of [
  ['SKILL_IG_CAPTION',legendaLinter,[legendaObrigatoria]],
]){
  const status=spawnSync('python',['-X','utf8',script,...args],{stdio:'inherit',windowsHide:true});
  if(status.error||status.status!==0){
    console.error('BLOQUEADO_'+etapa+': sem legenda valida NAO renderizar nem entregar.');
    process.exit(status.status||9);
  }
}
console.log('LEGENDA_FORMATO_VALIDADO: CTA e hashtags; recibo editorial continua obrigatorio para publicar.');
// PORTAO EDITORIAL ANTES DA RENDERIZACAO: ortografia pt-BR + taxonomia + erros contextuais conhecidos.
// Nao confundir com revisao semantica humana ou validacao teologica completa.
const qaTexto=resolve(dirname(fileURLToPath(import.meta.url)),'../../../02-scripts/qa_texto_taxonomia.py');
const qaTextoReport=resolve(dirname(resolve(arquivo)),'qa-texto-taxonomia.json');
const qaTextoCheck=spawnSync('python',['-X','utf8',qaTexto,'--html',resolve(arquivo),'--legenda',legendaObrigatoria,'--saida',qaTextoReport],{stdio:'inherit',windowsHide:true});
if(qaTextoCheck.error || qaTextoCheck.status!==0){
  console.error('TEXTO_OU_TAXONOMIA_REPROVADO: corrigir ortografia, contexto biblico e vocabulario no HTML/legenda; NAO renderizar/entregar.');
  process.exit(qaTextoCheck.status || 11);
}
console.log('QA_TEXTO_TAXONOMIA_PASSOU: dicionario pt-BR e regras contextuais verificadas; revisao editorial humana ainda necessaria.');

// Gate de fidelidade: NAO substitui comparacao visual humana.
const manifestoCandidato = manifesto ? resolve(manifesto) : resolve(dirname(resolve(arquivo)), 'manifesto-fidelidade.json');
const validarManifesto = exigirFidelidade || existsSync(manifestoCandidato);
if (validarManifesto) {
  if (!existsSync(manifestoCandidato)) {
    console.error('FIDELIDADE BLOQUEADA: manifesto de referencia ausente: '+manifestoCandidato);
    process.exit(7);
  }
  const validador = resolve(dirname(fileURLToPath(import.meta.url)), '../../../02-scripts/validar_fidelidade.py');
  const validation = spawnSync('python', [validador, '--manifest', manifestoCandidato], {stdio:'inherit',windowsHide:true});
  if (validation.error || validation.status !== 0) {
    console.error('FIDELIDADE BLOQUEADA: manifesto ausente, nao autorizado ou nao verificado. Nao aprovar a arte.');
    process.exit(validation.status || 7);
  }
  console.log('FIDELIDADE: manifesto valido; exportacao permanecera RASCUNHO ate comparacao visual.');
}

// O Playwright é procurado primeiro na pasta de onde você roda o comando (onde você fez npm i playwright),
// e só depois ao lado deste script.
let chromium;
try {
  let alvo = 'playwright';
  try {
    alvo = pathToFileURL(createRequire(join(process.cwd(), 'x.js')).resolve('playwright')).href;
  } catch { /* cai no import padrão */ }
  const modulo = await import(alvo);
  chromium = modulo.chromium ?? modulo.default.chromium;
} catch {
  console.error('O pacote "playwright" não está instalado aqui.');
  console.error('Rode na pasta de trabalho:  npm i playwright && npx playwright install chromium');
  process.exit(1);
}

async function abrirNavegador() {
  try {
    return await chromium.launch();
  } catch {
    // Chromium do Playwright não baixado: tenta o Chrome do sistema.
    try {
      return await chromium.launch({ channel: 'chrome' });
    } catch (erro) {
      console.error('Não consegui abrir um navegador.');
      console.error(String(erro.message).split('\n')[0]);
      console.error('Rode:  npx playwright install chromium   (ou instale o Google Chrome)');
      process.exit(1);
    }
  }
}

const navegador = await abrirNavegador();
const pagina = await navegador.newPage({
  viewport: { width: LARGURA, height: ALTURA },
  deviceScaleFactor: escala,
});

await pagina.goto(pathToFileURL(resolve(arquivo)).href, { waitUntil: 'networkidle' });
await pagina.evaluate(() => document.fonts.ready);

const slides = await pagina.locator(seletor).all();
if (slides.length === 0) {
  console.error(`Nenhum elemento encontrado com o seletor "${seletor}".`);
  await navegador.close();
  process.exit(1);
}

// Quality gate: fail closed on missing visual assets and inconsistent pagination.
const qualityIssues = await pagina.evaluate(selector => {
  const issues = [];
  const cards = [...document.querySelectorAll(selector)];
  const visualAssets = new Map();
  const PLACEHOLDER = /placeholder|dummyimage|via\.placeholder|picsum\.photos\/id\/0\b|example\.com\/|loremflickr/i;
  const pageMarks = [];
  cards.forEach((slide, index) => {
    const num = index + 1;
    const styles = [slide, ...slide.querySelectorAll('*')];
    const unique = new Set();
    for (const el of styles) {
      const style = getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') continue;
      if (el.tagName === 'IMG') {
        const src = el.getAttribute('src') || '';
        if (PLACEHOLDER.test(src)) issues.push({slide:num, issue:'imagem_placeholder',src:src.slice(0,140)});
        if (!el.complete || el.naturalWidth === 0) issues.push({slide:num,issue:'imagem_quebrada',src:src.slice(0,140)});
        if (src) unique.add(src);
      }
      const bg = style.backgroundImage || '';
      if (PLACEHOLDER.test(bg)) issues.push({slide:num,issue:'fundo_placeholder',background:bg.slice(0,160)});
      // Track only explicit content images, not intentional shared slide backgrounds.
      if (bg !== 'none' && (el.matches('.visual,.visual-content,.visual-bg,.hero,.artwork') || el.tagName === 'IMG')) unique.add(bg);
      if (el.children.length === 0 && /^\s*\d{1,2}\s*\/\s*\d{1,2}\s*$/.test(el.textContent || '')) {
        const [current,total] = el.textContent.trim().split('/').map(s => Number(s.trim()));
        pageMarks.push({slide:num,current,total});
      }
    }
    for (const asset of unique) {
      if (!visualAssets.has(asset)) visualAssets.set(asset, []);
      visualAssets.get(asset).push(num);
    }
  });
  if (pageMarks.length) {
    if (pageMarks.length !== cards.length) issues.push({issue:'paginacao_incompleta',encontrados:pageMarks.length,slides:cards.length});
    for (const mark of pageMarks) if (mark.current !== mark.slide || mark.total !== cards.length)
      issues.push({issue:'paginacao_incorreta',...mark,esperado:mark.slide+'/'+cards.length});
  }
  for (const [asset, places] of visualAssets) {
    if (cards.length >= 4 && places.length >= Math.ceil(cards.length * .75))
      issues.push({issue:'arte_principal_repetida',slides:places,asset:asset.slice(0,120)});
  }
  return issues;
}, seletor);
if (qualityIssues.length) {
  console.error('ERRO QUALIDADE VISUAL: '+JSON.stringify(qualityIssues));
  await navegador.close();
  process.exit(3);
}

// Exigir dimensoes e area central segura antes de gravar PNGs.
const safeIssues = await pagina.evaluate(selector => {
  const issues = [];
  const nodes = '.copy,.copy .eyebrow,.copy h1,.copy h1 strong,.copy p,.topline,.bottomline,.brand,.eyebrow,h1,h2,p,.hgroup h1,.hgroup h2,.hgroup .sub,.foot,.topo,.rodape,.corpo,.lista li,.card .text,.cartao,.numero,.botao';
  const allSlides = [...document.querySelectorAll(selector)];
  const repeatedHand = allSlides.filter(s => s.querySelector('.hand')).length;
  if (allSlides.length >= 5 && repeatedHand >= Math.ceil(allSlides.length * 0.6)) {
    issues.push({ issue:'visual_repetido',reason:'Mao ou emoji em quase todos os slides; usar imagem especifica por ideia' });
  }
  for (const [i,slide] of allSlides.entries()) {
    const bounds = slide.getBoundingClientRect();
    if (Math.abs(bounds.width-1080)>1 || Math.abs(bounds.height-1350)>1) {
      issues.push({slide:i+1,issue:'resolucao',width:bounds.width,height:bounds.height});
      continue;
    }
    // Verificar TODO texto visivel, independente da classe CSS usada pelo agente.
    // Range identifica a posicao real de cada trecho, inclusive spans em headings.
    const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
    let textNode;
    let checked = 0;
    while ((textNode = walker.nextNode()) && checked < 500) {
      if (!textNode.textContent.trim() || textNode.textContent.trim() === '↻') continue;
      const el = textNode.parentElement;
      if (!el) continue;
      const style = getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') continue;
      const range = document.createRange();
      range.selectNodeContents(textNode);
      for (const rect of range.getClientRects()) {
        if (rect.width <= 0 || rect.height <= 0) continue;
        checked++;
        const x = rect.left - bounds.left;
        const y = rect.top - bounds.top;
        if (x < 79 || rect.right-bounds.left > 1001 || y < 135 || rect.bottom-bounds.top > 1215) {
          issues.push({slide:i+1,issue:'texto_fora_area_segura',element:el.className||el.tagName,text:textNode.textContent.trim().slice(0,28),x:Math.round(x),y:Math.round(y)});
        }
        let ancestor = el;
        while (ancestor && ancestor !== slide) {
          const a = getComputedStyle(ancestor);
          if (['hidden','clip'].includes(a.overflowX) || ['hidden','clip'].includes(a.overflowY)) {
            const ar=ancestor.getBoundingClientRect();
            if (rect.left < ar.left-1 || rect.right > ar.right+1 || rect.top < ar.top-1 || rect.bottom > ar.bottom+1) {
              issues.push({slide:i+1,issue:'texto_cortado_pelo_container',element:ancestor.className||ancestor.tagName,text:textNode.textContent.trim().slice(0,28)});
            }
          }
          ancestor=ancestor.parentElement;
        }
      }
    }
    for (const el of slide.querySelectorAll(nodes)) {
      const r=el.getBoundingClientRect(),css=getComputedStyle(el);
      if(css.display==='none'||css.visibility==='hidden'||r.width===0||r.height===0)continue;
      const x=r.left-bounds.left,y=r.top-bounds.top;
      if(x<79||x+r.width>1001||y<135||y+r.height>1215) {
        issues.push({slide:i+1,issue:'fora_area_segura',element:el.className||el.tagName,x:Math.round(x),y:Math.round(y)});
      }
      if(['hidden','clip','auto','scroll'].includes(css.overflowY) && (el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2)){
        issues.push({slide:i+1,issue:'texto_cortado',element:el.className||el.tagName});
      }
    }
  }
  return issues;
}, seletor);
if (safeIssues.length) {
  console.error('ERRO AREA SEGURA: '+JSON.stringify(safeIssues));
  await navegador.close();
  process.exit(2);
}
const pastaSaida = resolve(saida);
mkdirSync(dirname(pastaSaida), {recursive:true});
// Nunca sobrescrever arquivo aprovado antes do QA: gerar em pasta de staging.
const pastaTemporaria = `${pastaSaida}.validando-${process.pid}`;
if (existsSync(pastaTemporaria)) throw new Error('Pasta temporaria ocupada: '+pastaTemporaria);
mkdirSync(pastaTemporaria, {recursive:true});

for (let i = 0; i < slides.length; i++) {
  const nome = `slide-${String(i + 1).padStart(2, '0')}.png`;
  await slides[i].screenshot({ path: join(pastaTemporaria, nome) });
  console.log(`ok  ${nome}`);
}

await navegador.close();
// Auditoria dos arquivos finais. Em identidade visual, exigir cenas reais por padrão.
const qaScript = resolve(dirname(fileURLToPath(import.meta.url)), '../../../02-scripts/qa_carrossel.py');
const strict = exigirCenas; // Exigir cenas pelo argumento --exigir-cenas; nao depender de pasta antiga removida.
const qaArgs = [qaScript, pastaTemporaria, '--expected', String(slides.length), ...(strict ? ['--exigir-cenas'] : [])];
const qaResult = spawnSync('python', qaArgs, {stdio:'inherit',windowsHide:true});
if (qaResult.error || qaResult.status !== 0) {
  console.error(`ERRO QA DOS PNGS: ${qaResult.error?.message || 'auditoria reprovou a entrega'}. Não publicar. Versao anterior preservada; diagnostico em ${pastaTemporaria}`);
  process.exit(qaResult.status || 4);
}
// QA ASSINATURA OFICIAL: obrigatorio em TODOS os novos carrosseis, antes da entrega.
const oficialScript=resolve(dirname(fileURLToPath(import.meta.url)), '../../../02-scripts/validar_padrao_carrossel.py');
const oficialArgs=['-X','utf8',oficialScript,'--pasta',pastaTemporaria,'--expected',String(slides.length),'--html',resolve(arquivo)];
const oficialQA=spawnSync('python',oficialArgs,{stdio:'inherit',windowsHide:true});
if(oficialQA.error || oficialQA.status!==0){
  console.error('BLOQUEADO: seta ou assinatura fora do padrao oficial. A versao antiga nao sera substituida. Corrija fonte e PNGs.');
  process.exit(oficialQA.status||8);
}
console.log('QA ASSINATURA OFICIAL: todos os slides aprovados.');

let backup = null;
try {
  if (existsSync(pastaSaida)) {
    backup = `${pastaSaida}.backup-${new Date().toISOString().replace(/[:.]/g,'-')}`;
    renameSync(pastaSaida, backup);
  }
  renameSync(pastaTemporaria, pastaSaida);
} catch (error) {
  if (backup && !existsSync(pastaSaida) && existsSync(backup)) renameSync(backup, pastaSaida);
  console.error('ERRO NA ENTREGA ATOMICA: '+error.message+'; versao anterior restaurada ou preservada');
  process.exit(5);
}
if (backup) console.log('Versao anterior preservada em '+backup);
console.log(`\n${slides.length} slide(s) exportado(s) e auditados em ${pastaSaida}`);

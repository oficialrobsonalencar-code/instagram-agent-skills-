// Publicador seguro: fila aprovada, perfil dedicado, verificacao e sem tentativas cegas.
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
(async()=>{
 const filename=process.argv[2];
 if(!filename||!fs.existsSync(filename))throw Error('Arquivo de trabalho inexistente');
 const q=JSON.parse(fs.readFileSync(filename,'utf8').replace(/^\uFEFF/,''));
 const preflightUpload=process.argv.includes('--preflight-upload');
 const preflight=process.argv.includes('--preflight') || preflightUpload;
 // Toda publicacao real precisa de liberacao por pacote, mesmo que o bloqueio global exista.
 // A verificacao e independente da fila e ocorre ANTES de abrir o navegador.
 if(!preflight){
  const {spawnSync}=require('child_process');
  const proof=spawnSync('python',[path.join(__dirname,'verificar_execucao_autorizada.py'),filename],
    {encoding:'utf8',timeout:15000,windowsHide:true});
  if(proof.status!==0)throw Error('PUBLICACAO_BLOQUEADA_POR_PACOTE: '+String(proof.stderr||proof.stdout||'sem prova').trim().slice(-500));
  console.log('PACOTE_INDIVIDUAL_VERIFICADO',q.id);
 }
 if((q.status!=='tentativa_iniciada' && !(preflight && q.status==='revisao_necessaria'))||!q.id||!q.approved_by)throw Error('Aprovacao ausente');
 const items=q.files||[];
 if(items.length<1||items.length>10||!items.every(x=>fs.existsSync(x)))throw Error('Midias invalidas');
 if(!q.caption?.trim())throw Error('Legenda vazia');
 const root=path.resolve(__dirname,'../03-agendamentos/publicador');
 const profile=path.join(root,'perfil-instagram');
 const proof=path.join(root,'evidencias');
 fs.mkdirSync(profile,{recursive:true});fs.mkdirSync(proof,{recursive:true});
 const capture=path.join(proof,String(q.id).replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,60));
 const browser=await chromium.launchPersistentContext(profile,{headless:true,viewport:{width:1280,height:900},args:['--disable-blink-features=AutomationControlled']});
 try{
  const page=browser.pages()[0]||await browser.newPage();
  await page.goto('https://www.instagram.com/',{waitUntil:'domcontentloaded',timeout:35000});
  await page.waitForTimeout(3000);
  if(await page.locator('input[name="username"], input[type="password"]').count() || /accounts\/emailsignup|accounts\/login|signup|register/i.test(page.url()))throw Error('PERFIL_NAO_LOGADO: autenticacao dedicada ausente ou redirecionada; entrar manualmente antes de publicar');
  // Conta precisa ser explicitamente configurada, sem confiar em usuario logado errado.
  const expected=String(q.account||'').replace(/^@/,'').toLowerCase();
  if(!expected)throw Error('CONTA_NAO_ESPECIFICADA');
  // Algumas versões exibem a identidade no painel lateral, sem link clicável.
  const profileLink=page.locator('a[href="/'+expected+'/"],a[href="https://www.instagram.com/'+expected+'/"]').first();
  let matched=await profileLink.count()>0;
  if(!matched){
   const accountText=page.getByText(expected,{exact:true}).first();
   matched=await accountText.isVisible().catch(()=>false) &&
     await page.getByText(/Switch|Alternar|Mudar/i).first().isVisible().catch(()=>false);
  }
  if(!matched){
   const links=await page.locator('a[href*="'+expected+'"]').count();
   const visible=await page.getByText(expected,{exact:true}).count();
   console.log('ACCOUNT_DIAG',JSON.stringify({url:page.url(),accountText:visible,accountLinks:links}));
   throw Error('CONTA_NAO_CONFIRMADA: identidade da sessao nao provada para '+expected);
  }
  // Exigir o comando de criacao do menu lateral, nao links "Create account"/cadastro.
  let create=page.locator('svg[aria-label="New post"], svg[aria-label="Nova publicação"], svg[aria-label="Criar"]').first().locator('xpath=ancestor::a[1]');
  if(!(await create.count()))create=page.getByRole('link',{name:/^Criar$|^Create$|^Novo post$|^New post$/i}).first();
  if(!(await create.count()))throw Error('BOTAO_CRIAR_NAO_ENCONTRADO: menu lateral do Instagram indisponivel');
  await create.click();
  await page.waitForTimeout(500);
  // Instagram inclui entradas Post invisíveis no DOM. Escolher só a VISÍVEL.
  // Evita coordenadas fixas que quebram com idioma, zoom e mudanças na janela.
  const postName=/^Postar$|^Post$/i;
  const options=await page.getByText(postName).all();
  let activePost=null;
  for (const item of options) {
   if(await item.isVisible().catch(()=>false)) { activePost=item; break; }
  }
  if(!activePost)throw Error('OPCAO_POST_VISIVEL_NAO_ENCONTRADA');
  await activePost.click();
  await page.getByText(/Create new post|Criar nova publicação|Criar novo post/i).first().waitFor({state:'visible',timeout:10000});
  if(preflight && !preflightUpload){
   const n=await page.locator('input[type="file"]').count();
   const button=await page.getByRole('button',{name:/Selecionar do computador|Select from computer|Selecionar arquivos|Select files/i}).count();
   await page.screenshot({path:capture+'-diagnostico.png'}).catch(()=>{});
   console.log('PREFLIGHT_OK',JSON.stringify({account:expected,fileInputs:n,selectButtons:button}));
   return;
  }
  // O Instagram frequentemente mantém um input de arquivo oculto e não emite
  // filechooser em certas versões da interface. Priorizar o input nativo.
  let fileInput=page.locator('input[type="file"]').first();
  if(!(await fileInput.count())) {
   const select=page.getByRole('button',{name:/Selecionar do computador|Select from computer|Selecionar arquivos|Select files/i}).first();
   if(!(await select.count()))throw Error('SELETOR_ARQUIVO_NAO_LOCALIZADO');
   const chooserPromise=page.waitForEvent('filechooser',{timeout:8000}).catch(()=>null);
   await select.click();
   fileInput=page.locator('input[type="file"]').first();
   if(await fileInput.count())await fileInput.setInputFiles(items);
   else { const chooser=await chooserPromise; if(!chooser)throw Error('INPUT_ARQUIVO_AUSENTE: interface de upload mudou'); await chooser.setFiles(items); }
  } else {
   await fileInput.setInputFiles(items);
  }
  await page.waitForTimeout(3000);
  for(let i=0;i<4;i++){
   const next=page.getByRole('button',{name:/^Avançar$|^Next$/i}).first();
   if(!(await next.isVisible().catch(()=>false)))break;
   await next.click();await page.waitForTimeout(1300);
  }
  const caption=page.getByRole('textbox',{name:/legenda|caption/i}).first();
  if(!(await caption.isVisible().catch(()=>false)))throw Error('CAMPO_LEGENDA_NAO_LOCALIZADO');
  await caption.fill(q.caption);
  await page.screenshot({path:capture+'-antes.png'}).catch(()=>{});
  const share=page.getByRole('button',{name:/^Compartilhar$|^Share$/i}).first();
  if(!(await share.isVisible().catch(()=>false)))throw Error('BOTAO_COMPARTILHAR_NAO_LOCALIZADO');
  if(preflightUpload){
   const inputs=await page.locator('input[type="file"]').count();
   console.log('PREFLIGHT_UPLOAD_OK',JSON.stringify({account:expected,mediaCount:items.length,captionLength:q.caption.length,fileInputs:inputs,shareButtonReady:true,published:false}));
   return;
  }
  await share.click();
  // Resultado incerto nunca autoriza nova tentativa automatica.
  let confirmed=false;
  try{
   await page.getByText(/Seu post foi compartilhado|Your post has been shared|Post compartilhado|Post shared/i).first().waitFor({state:'visible',timeout:45000});
   confirmed=true;
  }catch{}
  await page.screenshot({path:capture+'-depois.png'}).catch(()=>{});
  if(!confirmed)throw Error('RESULTADO_INCERTO: verificar manualmente, nao reenviar automaticamente');
  console.log('PUBLICACAO_CONFIRMADA',q.id);
 }finally{await browser.close();}
})().catch(err=>{console.error('PUBLICADOR_ERRO',err.message);process.exitCode=1;});

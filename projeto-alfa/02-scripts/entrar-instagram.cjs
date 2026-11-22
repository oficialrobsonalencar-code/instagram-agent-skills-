const path=require('path'),fs=require('fs');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'../03-agendamentos/publicador/perfil-instagram');
 fs.mkdirSync(root,{recursive:true});
 console.log('Navegador dedicado do publicador. Entre na conta correta e feche a janela quando terminar.');
 const browser=await chromium.launchPersistentContext(root,{headless:false,viewport:{width:1280,height:900}});
 const page=browser.pages()[0]||await browser.newPage();
 await page.goto('https://www.instagram.com/accounts/login/',{waitUntil:'domcontentloaded',timeout:40000});
 await new Promise(resolve=>browser.on('close',resolve));
})().catch(e=>{console.error('ERRO',e.message);process.exitCode=1});

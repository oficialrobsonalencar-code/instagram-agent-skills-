const path = require('node:path');
const { chromium } = require(path.join(process.env.APPDATA,'npm/node_modules/@playwright/mcp/node_modules/playwright-core'));
const profile = path.resolve(__dirname,'../03-agendamentos/publicador/perfil-instagram');
const exe = path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium-1248/chrome-win64/chrome.exe');
async function main() {
  const requested = process.argv[2];
  const value = requested === undefined ? undefined : Buffer.from(requested,'base64').toString('utf8');
  if (value !== undefined && (!value.trim() || [...value].length > 150)) throw Error('Bio vazia ou maior que 150 caracteres.');
  const browser = await chromium.launchPersistentContext(profile,{executablePath:exe,headless:true});
  try {
    const page = await browser.newPage();
    await page.goto('https://www.instagram.com/pastorrobsonalencar/',{waitUntil:'domcontentloaded'});
    const edit = page.locator('a[href="/accounts/edit/"]').first();
    await edit.waitFor({timeout:18000});
    if (new URL(page.url()).pathname !== '/pastorrobsonalencar/') throw Error('Perfil divergente.');
    await edit.click();
    await page.waitForURL('https://www.instagram.com/accounts/edit/**');
    const field = page.locator('textarea:visible');
    await field.first().waitFor();
    if (await field.count() !== 1 || !/bio/i.test(await field.evaluate(e=>[e.placeholder,e.ariaLabel,...Array.from(e.labels||[],l=>l.textContent),e.parentElement.parentElement.innerText].join(' ')))) throw Error('Campo de biografia ambiguo.');
    if (value === undefined) { console.log(JSON.stringify({conta:'pastorrobsonalencar',bio:await field.inputValue()})); return; }
    if (await field.inputValue() !== value) {
      await field.fill(value);
      const saved = page.waitForResponse(r=>r.request().method()==='POST' && /instagram\.com$/.test(new URL(r.url()).hostname) && /edit_profile|graphql/.test(r.url()) && r.ok());
      await Promise.all([saved,page.getByRole('button',{name:/^(enviar|submit|salvar|save)$/i}).click()]);
    }
    await page.reload({waitUntil:'domcontentloaded'});
    if (await field.inputValue() !== value) throw Error('Gravacao nao confirmada.');
    console.log('Bio confirmada em @pastorrobsonalencar.');
  } finally { await browser.close(); }
}
main().catch(e=>{ console.error(e.message.split('\n')[0]); process.exitCode=1; });
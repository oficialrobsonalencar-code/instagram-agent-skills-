const PW = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Roaming\\npm\\node_modules\\@playwright\\mcp\\node_modules\\playwright-core';
const EXE = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Local\\ms-playwright\\chromium-1248\\chrome-win64\\chrome.exe';
const PROFILE = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Local\\OpenCode\\BrowserProfile';
const { chromium } = require(PW);
(async () => {
  const browser = await chromium.launchPersistentContext(PROFILE, { executablePath: EXE, headless: true, viewport: { width: 1280, height: 900 } });
  const page = browser.pages()[0] || await browser.newPage();
  await page.goto('https://www.instagram.com/p/DfW4AO7EXqv/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const caption = await page.locator('article span, article div[dir="auto"]').allTextContents();
  const txt = caption.join(' ').replace(/\s+/g, ' ').slice(0, 400);
  // indicador de carrossel (ex: "1/6") ou botão próximo
  const carrossel = await page.locator('button[aria-label*="próximo"], button[aria-label*="Next"], span:has-text("/6")').count();
  console.log('indicadores carrossel:', carrossel);
  console.log('texto:', txt);
  await browser.close();
})().catch(e => { console.error('ERRO', e.message); process.exit(1); });

const path = require('path');
const PW = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Roaming\\npm\\node_modules\\@playwright\\mcp\\node_modules\\playwright-core';
const EXE = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Local\\ms-playwright\\chromium-1248\\chrome-win64\\chrome.exe';
const PROFILE = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Local\\OpenCode\\BrowserProfile';
const { chromium } = require(PW);
(async () => {
  const browser = await chromium.launchPersistentContext(PROFILE, { executablePath: EXE, headless: true, viewport: { width: 1280, height: 900 } });
  const page = browser.pages()[0] || await browser.newPage();
  await page.goto('https://www.instagram.com/pastorrobsonalencar/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(5000);
  const links = await page.locator('a[href*="/p/"]').evaluateAll(els => els.slice(0, 6).map(e => ({ href: e.getAttribute('href'), txt: (e.innerText || '').slice(0, 120) })));
  console.log(JSON.stringify(links, null, 1));
  await browser.close();
})().catch(e => { console.error('ERRO', e.message); process.exit(1); });

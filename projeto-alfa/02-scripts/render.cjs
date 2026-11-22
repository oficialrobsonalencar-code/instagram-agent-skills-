const path = require('path');
const fs = require('fs');
const PW = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Roaming\\npm\\node_modules\\@playwright\\mcp\\node_modules\\playwright-core';
const EXE = 'C:\\Users\\ROBSON ALENCAR\\AppData\\Local\\ms-playwright\\chromium-1248\\chrome-win64\\chrome.exe';
const { chromium } = require(PW);

(async () => {
  const html = fs.readFileSync(path.join(__dirname, 'carrossel-8h.html'), 'utf-8');
  const outDir = path.join(__dirname, 'out-8h');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: EXE, headless: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  const n = await page.locator('.slide').count();
  for (let i = 0; i < n; i++) {
    const name = path.join(outDir, 'slide-' + String(i + 1).padStart(2, '0') + '.png');
    await page.locator('.slide').nth(i).screenshot({ path: name, type: 'png' });
    console.log('ok', path.basename(name));
  }
  await browser.close();
  console.log(n + ' slides em ' + outDir);
})().catch(e => { console.error(e); process.exit(1); });

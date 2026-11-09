// Rendu PDF du livre : node src/render.cjs src/livre.html build/livre.pdf
const { chromium } = require('playwright');
const path = require('node:path');
(async () => {
  const [,, input, output] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load', timeout: 0 });
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.pdf({ path: output, format: 'A4', printBackground: true, preferCSSPageSize: true, outline: true, tagged: true, timeout: 0 });
  await browser.close();
  console.log('pdf', output);
})();

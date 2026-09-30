/**
 * End-to-end journey in a real browser (Chromium), desktop and mobile, with two accounts.
 * Test data is fictional and marked as such. Usage: npm run build && npm run e2e
 */
import { chromium, type Page, type BrowserContext } from 'playwright';
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { buildApp } from '../server/app.ts';
import { tmpDir, makePdf } from '../server/test/helpers.ts';
import { createHash, randomBytes } from 'node:crypto';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import type { JsonCaller } from '../server/generation.ts';

// TEST DOUBLE: deterministic stand-in for a real AI provider (no network, no cost).
const fakeAi: JsonCaller = async (_cfg, _prompt, _schema, name) => name === 'explanation'
  ? { title: 'T', explanation: 'La purification (tahara) est une condition pour que la prière soit valide.', points_to_check: ['Vérifier les exceptions citées par le cours.'] }
  : { flashcards: [{ question: 'Quelle eau permet les ablutions ?', answer: "L'eau pure et purifiante", skill: 'definition', pages: [3], excerpt: "L'eau pure et purifiante permet les ablutions." }],
      mcq: [{ question: "Selon l'avis retenu, l'eau changée par une chose pure…", choices: [{ text: 'reste purifiante tant que son nom demeure', correct: true, why: 'Avis retenu.' }, { text: 'devient impure', correct: false, why: 'Non dit par le cours.' }], explanation: '', skill: 'distinction', pages: [3], excerpt: '' }],
      open: [] };

const here = path.dirname(fileURLToPath(import.meta.url));
const shots = path.join(here, 'screenshots');
mkdirSync(shots, { recursive: true });
const dist = path.join(here, '..', 'dist');
if (!existsSync(path.join(dist, 'index.html'))) throw new Error('Lancer `npm run build` avant `npm run e2e`.');

const dataDir = tmpDir();
const { app } = await buildApp({ dataDir, staticDir: dist, secretKey: 'e2e-secret-'.padEnd(40, 'x'), callJson: fakeAi });
await app.listen({ port: 0, host: '127.0.0.1' });
const addr = app.server.address() as { port: number };
const BASE = `http://127.0.0.1:${addr.port}`;
const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium'].find(existsSync);
const browser = await chromium.launch({ executablePath: exe });
const results: string[] = [];
const step = (s: string) => { results.push(s); console.log('✓', s); };

const fixtures = tmpDir();
const pdfPath = path.join(fixtures, 'purification-demo.pdf');
writeFileSync(pdfPath, await makePdf([
  'DONNEES FICTIVES DE DEMONSTRATION\nChapitre : la purification (tahara).\nLa purification est une condition de validite de la priere.',
  '',
  "L'eau pure et purifiante permet les ablutions.\nSelon l'avis retenu dans ce cours, l'eau changee par une chose pure reste purifiante\ntant que son nom d'eau demeure, avec divergence entre les ecoles.",
]));
const csvPath = path.join(fixtures, 'flashcards.csv');
writeFileSync(csvPath, '﻿Question;Réponse;Page\n"ما هي الطهارة؟\n(définition)";"رفع الحدث وإزالة النجس";1\n"Condition de validité de la prière ?";"La purification";1\n"Quelle eau permet les ablutions ?";"L\'eau pure et purifiante; selon l\'avis retenu";3\n');
const jsonPath = path.join(fixtures, 'supports.json');
writeFileSync(jsonPath, JSON.stringify({
  format: 'muraja.v1',
  mcq: [{ question: "L'eau changée par une chose pure reste-t-elle purifiante selon l'avis retenu ?",
    choices: [{ text: 'Oui, tant que son nom d’eau demeure', correct: true, why: 'Avis retenu dans le cours, avec divergence.' },
      { text: 'Non, jamais', correct: false, why: 'Le cours mentionne une condition, pas une interdiction générale.' },
      { text: 'Seulement pour la prière du vendredi', correct: false, why: 'Aucune restriction de ce type dans le cours.' }],
    source: { pages: [3], excerpt: "l'eau changee par une chose pure reste purifiante" } }],
  open: [{ question: 'Expliquez avec vos mots pourquoi la purification précède la prière.', answer: 'Parce qu’elle est une condition de validité de la prière.', skill: 'application' }],
  mindmap: { title: 'La purification', nodes: [
    { id: 'r', label: 'الطهارة — La purification' }, { id: 'e', label: 'L’eau', parent: 'r', note: 'Eau pure et purifiante.' },
    { id: 'c', label: 'Condition de la prière', parent: 'r' }, { id: 'd', label: 'Divergence des écoles', parent: 'e' }] },
  glossary: [{ term: 'Tahara', arabic: 'الطَّهَارَة', definition: 'Purification rituelle.' }],
}));

async function register(ctx: BrowserContext, name: string, email: string): Promise<Page> {
  const page = await ctx.newPage();
  page.on('pageerror', (e) => { throw e; });
  await page.goto(BASE);
  await page.getByRole('button', { name: 'Pas encore de compte ? Créer un compte' }).click();
  await page.getByLabel('Prénom').fill(name);
  await page.getByLabel('Adresse e-mail').fill(email);
  await page.getByLabel('Mot de passe').fill('motdepasse-demo');
  await page.getByRole('button', { name: 'Créer mon compte' }).click();
  await page.getByRole('heading', { name: `Bonjour ${name}` }).waitFor();
  return page;
}

async function answerCurrent(page: Page) {
  const badge = await page.locator('.review-card .badge').first().innerText();
  if (badge === 'Flashcard') {
    await page.getByRole('button', { name: 'Afficher la réponse' }).click();
    await page.getByRole('button', { name: /^Bien/ }).click();
  } else if (badge === 'QCM') {
    await page.locator('.choice').filter({ hasText: 'tant que son nom' }).click();
    await page.getByRole('button', { name: 'Valider' }).click();
    await page.getByText('Bonne réponse.').waitFor();
    await page.getByRole('button', { name: 'Continuer' }).click();
  } else {
    await page.getByLabel('Votre réponse, sans regarder le cours').fill('Car elle conditionne sa validité.');
    await page.getByRole('button', { name: 'Comparer avec la réponse attendue' }).click();
    await page.getByRole('button', { name: /^Difficile/ }).click();
  }
}

try {
  // ------------------------------------------------ account A, desktop
  const desk = await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'fr-FR', timezoneId: 'Indian/Reunion', acceptDownloads: true });
  const a = await register(desk, 'Hakim', 'hakim@example.org');
  await a.getByText('Commencez par ajouter un cours.').waitFor();
  await a.screenshot({ path: path.join(shots, 'desktop-01-accueil-vide.png') });
  step('Compte A créé ; accueil vide avec action claire');

  await a.getByRole('button', { name: '＋ Ajouter un cours' }).click();
  await a.getByLabel('Nom de la nouvelle matière').fill('Fiqh (démo)');
  await a.getByLabel('Nom du nouveau chapitre').fill('La purification');
  await a.getByLabel('Fichier', { exact: true }).setInputFiles(pdfPath);
  await a.getByRole('button', { name: 'Ajouter', exact: true }).click();
  await a.getByRole('heading', { name: 'Cours ajouté' }).waitFor();
  await a.getByText('3 page(s) lue(s).').waitFor();
  await a.getByText(/Pages sans texte lisible : 2/).waitFor();
  await a.screenshot({ path: path.join(shots, 'desktop-02-pdf-importe.png') });
  step('PDF de 3 pages importé ; page 2 sans texte signalée');

  await a.getByRole('link', { name: 'Lire le cours' }).click();
  await a.getByRole('heading', { name: 'Page 3' }).waitFor();
  const docUrl = a.url();
  // Select an exact sentence of page 3, then create a question from it.
  await a.evaluate(() => {
    const el = [...document.querySelectorAll('section.page .text div')].find((e) => e.textContent?.includes('eau pure'))!;
    const node = el.firstChild!;
    const start = node.textContent!.indexOf("L'eau pure");
    const r = document.createRange();
    r.setStart(node, start);
    r.setEnd(node, start + "L'eau pure et purifiante permet les ablutions.".length);
    getSelection()!.removeAllRanges();
    getSelection()!.addRange(r);
  });
  await a.locator('section[aria-label="Page 3"]').getByRole('button', { name: 'Créer une question' }).click();
  await a.getByLabel(/^Question/).fill('Quelle eau permet les ablutions ?');
  await a.getByLabel('Réponse (cachée pendant la révision)').fill("L'eau pure et purifiante.");
  await a.getByRole('button', { name: 'Ajouter', exact: true }).click();
  await a.getByText('1 question(s) créée(s) depuis ce document.').waitFor();
  step('Question créée depuis une sélection du PDF (page 3 + extrait)');

  await a.getByRole('link', { name: '← Retour au chapitre' }).click();
  await a.getByRole('link', { name: 'Importer' }).click();
  await a.getByLabel('Fichier', { exact: true }).setInputFiles(csvPath);
  await a.getByText('Aperçu — flashcards.csv : 3 ligne(s)').waitFor();
  assert.equal(await a.getByLabel('Page(s) (facultatif)').inputValue(), '2');
  await a.getByLabel('Document source (facultatif)').selectOption({ label: 'purification-demo' });
  await a.getByText('ما هي الطهارة؟').first().waitFor();
  await a.screenshot({ path: path.join(shots, 'desktop-03-apercu-csv.png'), fullPage: true });
  await a.getByRole('button', { name: 'Importer 3 carte(s)' }).click();
  await a.getByText('3 flashcard(s) importées.').waitFor();
  step('CSV (arabe, retour à la ligne, « ; », BOM) prévisualisé puis importé');

  await a.locator('#json-file').setInputFiles(jsonPath);
  await a.getByLabel('Document source (pour vérifier les extraits cités)').selectOption({ label: 'purification-demo' });
  await a.getByRole('button', { name: 'Prévisualiser' }).click();
  await a.getByText(/1 QCM, 1 question\(s\) ouverte\(s\), une carte mentale de 4 nœuds/).waitFor();
  await a.getByRole('button', { name: 'Importer', exact: true }).click();
  await a.getByText(/Import terminé\. 1 élément\(s\) avec source vérifiée/).waitFor();
  step('JSON muraja.v1 importé ; l’extrait réellement présent est « vérifié »');

  await a.getByRole('link', { name: /Questions/ }).click();
  await a.getByText('Source vérifiée · p. 3').first().waitFor();
  await a.getByText('Source à vérifier').first().waitFor();
  await a.screenshot({ path: path.join(shots, 'desktop-04-questions.png'), fullPage: true });
  const dirs = await a.locator('.text', { hasText: 'ما هي الطهارة' }).first().locator('div').evaluateAll((els) => els.map((e) => getComputedStyle(e).direction));
  assert.deepEqual(dirs, ['rtl', 'ltr']);
  step('Texte mixte arabe/français : direction calculée ligne par ligne');

  // ------------------------------------------------ review session with interruption
  await a.getByRole('link', { name: 'Accueil' }).first().click();
  await a.getByRole('button', { name: "Réviser aujourd'hui" }).click();
  await a.locator('.review-card').waitFor();
  await a.screenshot({ path: path.join(shots, 'desktop-05-revision.png') });
  await answerCurrent(a);
  await answerCurrent(a);
  await a.getByText('3 / ').waitFor();
  // Interruption: close the tab, reopen the site.
  await a.close();
  const a2 = await desk.newPage();
  await a2.goto(BASE);
  await a2.getByText('Séance en cours : 2 /').waitFor();
  await a2.getByRole('button', { name: 'Reprendre ma révision' }).click();
  await a2.getByText('3 / ').waitFor();
  step('Séance interrompue puis reprise à la même position');

  // Double click on a grade must record a single review.
  const before = await (await a2.request.get(`${BASE}/api/progress`)).json();
  const kind = await a2.locator('.review-card .badge').first().innerText();
  if (kind === 'Flashcard') {
    await a2.getByRole('button', { name: 'Afficher la réponse' }).click();
    await a2.getByRole('button', { name: /^Bien/ }).dblclick();
  } else {
    await answerCurrent(a2);
  }
  await a2.getByText('4 / ').waitFor();
  const after = await (await a2.request.get(`${BASE}/api/progress`)).json();
  assert.equal(after.activities.reviews_total, before.activities.reviews_total + 1);
  step('Double clic sur une évaluation : une seule réponse enregistrée');

  for (let i = 0; i < 20; i++) {
    if (await a2.getByRole('heading', { name: 'Séance terminée' }).isVisible()) break;
    await answerCurrent(a2);
    await a2.waitForTimeout(150);
  }
  await a2.getByRole('heading', { name: 'Séance terminée' }).waitFor();
  step('Séance terminée (flashcards, QCM, question ouverte)');

  // ------------------------------------------------ mind map
  await a2.goto(`${BASE}/#/library`);
  await a2.getByRole('link', { name: 'La purification' }).click();
  await a2.getByRole('link', { name: 'Carte mentale' }).click();
  await a2.getByRole('link', { name: 'La purification' }).click();
  await a2.locator('.mm-node', { hasText: 'L’eau' }).click();
  await a2.getByRole('button', { name: '＋ Idée secondaire' }).click();
  await a2.getByLabel('Idée', { exact: true }).fill('Eau changée par une chose pure');
  await a2.getByLabel('Explication').fill('Reste purifiante tant que son nom d’eau demeure (avis retenu).');
  await a2.getByLabel('Lier une question').selectOption({ index: 1 });
  await a2.getByRole('button', { name: 'Enregistrer' }).click();
  await a2.getByText('Carte enregistrée.').waitFor();
  await a2.screenshot({ path: path.join(shots, 'desktop-06-carte-mentale.png'), fullPage: true });
  await a2.getByLabel("S'entraîner : masquer les branches").check();
  await a2.locator('.mm-node.hidden-label').first().waitFor();
  await a2.getByRole('button', { name: 'Liste' }).click();
  await a2.getByRole('tree').waitFor();
  await a2.reload();
  await a2.locator('.mm-node', { hasText: 'Eau changée par une chose pure' }).waitFor();
  step('Carte mentale éditée, liée à une question, persistée ; mode exercice et vue liste');

  await a2.goto(`${BASE}/#/progress`);
  await a2.getByRole('heading', { name: 'Mes progrès' }).waitFor();
  await a2.screenshot({ path: path.join(shots, 'desktop-07-progres.png'), fullPage: true });
  const exp = await (await a2.request.get(`${BASE}/api/export`)).json();
  assert.equal(exp.items.length, 6); // before AI steps
  assert.ok(exp.review_logs.length >= 6);
  step(`Export JSON : ${exp.items.length} éléments, ${exp.review_logs.length} réponses`);

  // Honest "explain simply" without provider.
  await a2.goto(`${BASE}/#/library`);
  await a2.getByRole('link', { name: 'La purification' }).click();
  await a2.getByRole('link', { name: /Fiches/ }).click();
  await a2.getByRole('button', { name: '＋ Nouvelle fiche' }).click();
  await a2.getByLabel('Contenu').fill('الطهارة شرط لصحة الصلاة.\nLa purification est une condition de validité.');
  await a2.getByRole('button', { name: 'Enregistrer' }).click();
  await a2.getByRole('button', { name: 'Expliquer simplement' }).click();
  await a2.getByText("Aucune IA n'est connectée à votre compte").waitFor();
  step('« Expliquer simplement » sans IA connectée : message honnête, rien de simulé');

  // ------------------------------------------------ AI: personal key (test double provider) + generation from pages
  await a2.goto(`${BASE}/#/settings`);
  await a2.getByLabel(/^Clé API/).fill('sk-ant-demo-key-0000');
  await a2.getByRole('button', { name: 'Enregistrer', exact: true }).last().click();
  await a2.getByText(/Connectée : Anthropic \(Claude\) · claude-opus-5-5 · clé …0000/).waitFor();
  await a2.screenshot({ path: path.join(shots, 'desktop-08-reglages-ia.png'), fullPage: true });
  await a2.goto(docUrl.replace(/^.*#/, `${BASE}/#`));
  await a2.getByText("Générer des questions avec l'IA").click();
  await a2.getByLabel('Pages').fill('1');
  await a2.getByLabel('à', { exact: true }).fill('3');
  await a2.getByRole('button', { name: 'Générer', exact: true }).click();
  await a2.getByText('Pages ignorées (sans texte lisible) : 2.').waitFor();
  await a2.screenshot({ path: path.join(shots, 'desktop-09-generation.png'), fullPage: true });
  await a2.getByRole('button', { name: 'Enregistrer la sélection' }).click();
  await a2.getByText(/2 question\(s\) ajoutée\(s\), dont 1 avec une source retrouvée/).waitFor();
  step('IA intégrée (fournisseur simulé) : brouillon relu puis enregistré, page scannée ignorée, source vérifiée');
  await a2.getByRole('link', { name: '← Retour au chapitre' }).click();
  await a2.getByRole('link', { name: /Fiches/ }).click();
  await a2.getByRole('button', { name: 'Expliquer simplement' }).first().click();
  await a2.getByRole('heading', { name: /Explication simple — / }).waitFor();
  await a2.getByText('Généré par IA').first().waitFor();
  step('« Expliquer simplement » avec IA : explication enregistrée comme fiche marquée « Généré par IA »');

  // ------------------------------------------------ connect "Claude" (OAuth consent in the browser, then MCP)
  const reg = await (await a2.request.post(`${BASE}/oauth/register`, { data: { client_name: 'Claude', redirect_uris: ['https://claude.ai/api/mcp/auth_callback'] } })).json();
  const verifier = randomBytes(32).toString('base64url');
  const q = new URLSearchParams({ response_type: 'code', client_id: reg.client_id, redirect_uri: 'https://claude.ai/api/mcp/auth_callback', state: 'st',
    code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256', scope: 'muraja' });
  let callback = '';
  await a2.route(/^https:\/\/claude\.ai\//, (route) => { callback = route.request().url(); return route.fulfill({ status: 200, body: 'ok' }); });
  await a2.goto(`${BASE}/oauth/authorize?${q}`);
  await a2.getByRole('heading', { name: 'Autoriser « Claude » ?' }).waitFor();
  await a2.screenshot({ path: path.join(shots, 'desktop-10-autorisation.png') });
  await a2.getByRole('button', { name: 'Autoriser' }).click();
  await a2.waitForURL(/^https:\/\/claude\.ai\//);
  const back = new URL(callback || a2.url());
  assert.equal(back.searchParams.get('state'), 'st');
  const code = back.searchParams.get('code')!;
  const tok = await (await a2.request.post(`${BASE}/oauth/token`, { form: { grant_type: 'authorization_code', code, code_verifier: verifier, client_id: reg.client_id, redirect_uri: 'https://claude.ai/api/mcp/auth_callback' } })).json();
  const mcp = new McpClient({ name: 'e2e', version: '1' });
  await mcp.connect(new StreamableHTTPClientTransport(new URL(`${BASE}/mcp`), { requestInit: { headers: { Authorization: `Bearer ${tok.access_token}` } } }));
  const courses = JSON.parse(((await mcp.callTool({ name: 'list_courses', arguments: {} })) as any).content[0].text);
  const chId = courses.subjects[0].chapters[0].id;
  const docId2 = courses.subjects[0].chapters[0].documents[0].id;
  const pagesRead = JSON.parse(((await mcp.callTool({ name: 'read_course_pages', arguments: { document_id: docId2, from_page: 3, to_page: 3 } })) as any).content[0].text);
  assert.match(pagesRead.pages[0].text, /eau pure/);
  await mcp.callTool({ name: 'add_flashcards', arguments: { chapter_id: chId, document_id: docId2, cards: [{ question: 'Quand l’eau changée reste-t-elle purifiante ?', answer: 'Tant que son nom d’eau demeure (avis retenu, divergence)', pages: [3], excerpt: 'reste purifiante' }] } });
  await mcp.close();
  await a2.unroute(/^https:\/\/claude\.ai\//);
  await a2.goto(`${BASE}/#/chapter/${chId}?tab=questions`);
  await a2.getByText('Ajouté par Claude').first().waitFor();
  await a2.goto(`${BASE}/#/settings`);
  await a2.getByText('Applications connectées').waitFor();
  await a2.getByRole('button', { name: 'Déconnecter', exact: true }).waitFor();
  step('Connexion « Claude » : autorisation dans le navigateur, lecture du cours et ajout de flashcards via MCP, visibles dans le chapitre');

  // ------------------------------------------------ account B: isolation through the UI and the API
  const other = await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'fr-FR' });
  const b = await register(other, 'Maryam', 'maryam@example.org');
  await b.goto(docUrl.replace(/^.*#/, `${BASE}/#`));
  await b.getByText('Introuvable.').waitFor();
  const docId = docUrl.split('/').pop()!;
  assert.equal((await b.request.get(`${BASE}/api/documents/${docId}/file`)).status(), 404);
  assert.equal((await (await b.request.get(`${BASE}/api/library`)).json()).subjects.length, 0);
  step('Compte B : document, fichier et bibliothèque de A inaccessibles');

  // ------------------------------------------------ mobile (Android-size) screenshots for account A
  const mob = await browser.newContext({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'fr-FR', timezoneId: 'Indian/Reunion' });
  await mob.addCookies((await desk.cookies()).map((c) => ({ ...c })));
  const m = await mob.newPage();
  await m.goto(BASE);
  await m.getByRole('heading', { name: 'Bonjour Hakim' }).waitFor();
  await m.screenshot({ path: path.join(shots, 'mobile-01-accueil.png') });
  await m.goto(`${BASE}/#/library`);
  await m.getByRole('link', { name: 'La purification' }).click();
  await m.getByRole('link', { name: /Questions/ }).click();
  await m.screenshot({ path: path.join(shots, 'mobile-02-questions.png') });
  await m.getByRole('button', { name: 'Réviser ce chapitre' }).click();
  await m.getByText("Rien à réviser aujourd'hui dans ce chapitre.").or(m.locator('.review-card')).first().waitFor();
  await m.goto(`${BASE}/#/glossary`);
  await m.getByText('الطَّهَارَة').waitFor();
  await m.screenshot({ path: path.join(shots, 'mobile-03-glossaire.png') });
  const docLink = docUrl.replace(/^.*#/, `${BASE}/#`);
  await m.goto(docLink);
  await m.getByRole('heading', { name: 'Page 1' }).waitFor();
  await m.screenshot({ path: path.join(shots, 'mobile-04-document.png') });
  const overflow = await m.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(overflow <= 0, `débordement horizontal ${overflow}px`);
  step('Écrans mobiles (412 px) sans débordement horizontal');

  await browser.close();
  console.log(`\nE2E OK — ${results.length} étapes. Captures : ${path.relative(process.cwd(), shots)}`);
} catch (e) {
  console.error('E2E ÉCHEC après :', results);
  const pages = browser.contexts().flatMap((c) => c.pages());
  for (const [i, p] of pages.entries()) await p.screenshot({ path: path.join(shots, `echec-${i}.png`) }).catch(() => {});
  await browser.close();
  throw e;
} finally {
  await app.close();
}

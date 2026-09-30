import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { readdirSync } from 'node:fs';
import path from 'node:path';
import { makeApp, signup, chapter, makePdf, Client } from './helpers.ts';

const LOREM = 'La purification est une condition de validite de la priere selon les quatre ecoles.';

test('two accounts are isolated on every resource, including stored files', async () => {
  const { app, dataDir } = await makeApp();
  const alice = await signup(app, 'alice@example.org');
  const bob = await signup(app, 'bob@example.org');
  const ch = await chapter(alice);
  const up = await alice.upload(`/api/chapters/${ch}/documents/upload`, 'cours.pdf', await makePdf([LOREM, LOREM]), 'application/pdf');
  assert.equal(up.status, 200, up.body);
  const docId = up.json.id;
  const item = await alice.post(`/api/chapters/${ch}/items`, { type: 'flashcard', prompt: 'Q ?', answer: 'R' });
  const map = await alice.post(`/api/chapters/${ch}/mindmaps`, {});
  const note = await alice.post(`/api/chapters/${ch}/notes`, { title: 'Fiche', body: 'x' });

  for (const url of [`/api/chapters/${ch}`, `/api/documents/${docId}`, `/api/documents/${docId}/file`, `/api/mindmaps/${map.json.id}`]) {
    assert.equal((await bob.get(url)).status, 404, url);
  }
  assert.equal((await bob.del(`/api/documents/${docId}`)).status, 404);
  assert.equal((await bob.patch(`/api/items/${item.json.id}`, { prompt: 'volé' })).status, 404);
  assert.equal((await bob.patch(`/api/notes/${note.json.id}`, { body: 'volé' })).status, 404);
  assert.equal((await bob.post(`/api/chapters/${ch}/items`, { type: 'flashcard', prompt: 'a', answer: 'b' })).status, 404);
  assert.equal((await bob.post('/api/review/answer', { item_id: item.json.id, review_id: randomUUID(), expected_version: 0, rating: 3 })).status, 404);
  // Bob cannot cite Alice's document as a source nor link her items in his mind map.
  const bobCh = await chapter(bob);
  const stolen = await bob.post(`/api/chapters/${bobCh}/items`, { type: 'flashcard', prompt: 'a', answer: 'b', source: { document_id: docId, pages: [1], excerpt: LOREM } });
  assert.equal(stolen.json.source_document_id, null);
  assert.notEqual(stolen.json.source_status, 'verified');
  const bobMap = await bob.post(`/api/chapters/${bobCh}/mindmaps`, {});
  const put = await bob.put(`/api/mindmaps/${bobMap.json.id}`, { title: 'm', nodes: [{ id: 'root', label: 'r', parentId: null, itemIds: [item.json.id] }] });
  assert.deepEqual(put.json.nodes[0].itemIds, []);
  // Library, progress and export only contain the caller's data.
  assert.equal((await bob.get('/api/library')).json.subjects.length, 1);
  const exp = (await bob.get('/api/export')).json;
  assert.equal(exp.items.length, 1);
  assert.equal(exp.documents.length, 0);
  assert.ok(!JSON.stringify(exp).includes('password'));
  // Files are stored per user directory.
  const aliceUser = (await alice.get('/api/me')).json.user.id;
  assert.deepEqual(readdirSync(path.join(dataDir, 'files', aliceUser)), [`${docId}.pdf`]);
  // Unauthenticated access is refused.
  assert.equal((await new Client(app).get(`/api/documents/${docId}/file`)).status, 401);
  await app.close();
});

test('mutating requests without the custom header are refused (CSRF)', async () => {
  const { app } = await makeApp();
  const res = await app.inject({ method: 'POST', url: '/api/auth/register', headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ email: 'x@example.org', name: 'x', password: 'motdepasse-solide' }) });
  assert.equal(res.statusCode, 403);
  await app.close();
});

test('invite code is enforced when configured', async () => {
  const { app } = await makeApp({ inviteCode: 'famille-2026' });
  const c = new Client(app);
  assert.equal((await c.post('/api/auth/register', { email: 'a@example.org', name: 'a', password: 'motdepasse-solide' })).status, 403);
  assert.equal((await c.post('/api/auth/register', { email: 'a@example.org', name: 'a', password: 'motdepasse-solide', invite: 'famille-2026' })).status, 200);
  await app.close();
});

test('multi-page PDF keeps page numbers; scanned pages are detected', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const ok = await c.upload(`/api/chapters/${ch}/documents/upload`, 'c.pdf', await makePdf(['Page un. ' + LOREM, 'Page deux. ' + LOREM, 'Page trois. ' + LOREM]), 'application/pdf');
  assert.equal(ok.json.extraction_status, 'ok');
  const doc = (await c.get(`/api/documents/${ok.json.id}`)).json;
  assert.deepEqual(doc.pages.map((p: any) => p.page_number), [1, 2, 3]);
  assert.match(doc.pages[1].text, /^Page deux/);

  const partial = await c.upload(`/api/chapters/${ch}/documents/upload`, 'p.pdf', await makePdf([LOREM, '', LOREM, LOREM]), 'application/pdf');
  assert.equal(partial.json.extraction_status, 'partial');
  assert.match(partial.json.extraction_note, /Pages sans texte lisible : 2/);

  const scan = await c.upload(`/api/chapters/${ch}/documents/upload`, 's.pdf', await makePdf(['', '', 'p3']), 'application/pdf');
  assert.equal(scan.json.extraction_status, 'insufficient');
  assert.match(scan.json.extraction_note, /OCR/);

  const bad = await c.upload(`/api/chapters/${ch}/documents/upload`, 'x.pdf', Buffer.from('<script>alert(1)</script>'), 'application/pdf');
  assert.equal(bad.status, 400);
  const broken = await c.upload(`/api/chapters/${ch}/documents/upload`, 'b.pdf', Buffer.from('%PDF-1.7 garbage'), 'application/pdf');
  assert.equal(broken.status, 400);
  assert.match(broken.json.error, /pas pu être ouvert/);
  await app.close();
});

test('JSON import validates, and only verifies sources really present in the document', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const up = await c.upload(`/api/chapters/${ch}/documents/upload`, 'cours.pdf', await makePdf([LOREM, 'Autre page sans rapport avec la priere ni le reste.']), 'application/pdf');
  const data = {
    format: 'muraja.v1',
    flashcards: [
      { question: 'Statut de la purification ?', answer: 'Condition de validité', source: { pages: [1], excerpt: 'condition de validite de la priere' } },
      { question: 'Inventée ?', answer: 'x', source: { pages: [2], excerpt: 'condition de validite de la priere' } },
      { question: 'Sans source ?', answer: 'y' },
    ],
    mcq: [{ question: 'Q', choices: [{ text: 'a', correct: true }, { text: 'b', correct: false, why: 'non' }] }],
    notes: [{ title: 'الطهارة', body: 'شرط لصحة الصلاة' }],
    mindmap: { title: 'Carte', nodes: [{ id: 'r', label: 'Purification' }, { id: 'a', label: 'Eau', parent: 'r' }] },
    glossary: [{ term: 'Tahara', arabic: 'الطهارة', definition: 'purification' }],
  };
  const invalid = await c.post(`/api/chapters/${ch}/import/json`, { data: { ...data, mcq: [{ question: 'Q', choices: [{ text: 'a', correct: true }, { text: 'b', correct: true }] }] } });
  assert.equal(invalid.json.ok, false);
  const cyclic = await c.post(`/api/chapters/${ch}/import/json`, { data: { ...data, mindmap: { title: 't', nodes: [{ id: 'a', label: 'a', parent: 'b' }, { id: 'b', label: 'b', parent: 'a' }] } } });
  assert.equal(cyclic.json.ok, false);
  const preview = await c.post(`/api/chapters/${ch}/import/json`, { data, document_id: up.json.id });
  assert.equal(preview.json.dry_run, true);
  assert.equal((await c.get(`/api/chapters/${ch}`)).json.items.length, 0, 'dry run writes nothing');
  const done = await c.post(`/api/chapters/${ch}/import/json`, { data, document_id: up.json.id, dry_run: false });
  assert.equal(done.json.ok, true, JSON.stringify(done.json));
  const view = (await c.get(`/api/chapters/${ch}`)).json;
  const byPrompt = Object.fromEntries(view.items.map((i: any) => [i.prompt, i]));
  assert.equal(byPrompt['Statut de la purification ?'].source_status, 'verified');
  assert.equal(byPrompt['Inventée ?'].source_status, 'to_verify');
  assert.equal(byPrompt['Sans source ?'].source_status, 'to_verify');
  assert.equal(view.notes[0].title, 'الطهارة');
  assert.equal(view.mindmaps.length, 1);
  await app.close();
});

test('JSON content is stored as inert text', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const payload = '<img src=x onerror=alert(1)>';
  await c.post(`/api/chapters/${ch}/import/json`, { data: { format: 'muraja.v1', flashcards: [{ question: payload, answer: payload }] }, dry_run: false });
  const it = (await c.get(`/api/chapters/${ch}`)).json.items[0];
  assert.equal(it.prompt, payload);
  const page = await app.inject({ method: 'GET', url: '/api/health' });
  assert.match(String(page.headers['content-security-policy']), /script-src 'self'/);
  await app.close();
});

test('CSV import: preview, rejection of incomplete rows, commit', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const rows = [{ question: 'ما هي الطهارة؟\nDeux lignes', answer: 'رفع الحدث' }, { question: '', answer: '' }, { question: 'Q2', answer: '' }];
  const pre = await c.post(`/api/chapters/${ch}/import/csv`, { rows });
  assert.equal(pre.json.count, 1);
  assert.equal(pre.json.errors.length, 1);
  const bad = await c.post(`/api/chapters/${ch}/import/csv`, { rows, dry_run: false });
  assert.equal(bad.json.ok, false);
  const ok = await c.post(`/api/chapters/${ch}/import/csv`, { rows: rows.slice(0, 2), dry_run: false });
  assert.equal(ok.json.count, 1);
  const it = (await c.get(`/api/chapters/${ch}`)).json.items[0];
  assert.equal(it.prompt, 'ما هي الطهارة؟\nDeux lignes');
  assert.equal(it.source_status, 'to_verify');
  await app.close();
});

test('editing one field (suspend) keeps the rest of the item; suspended items leave today', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const mcq = await c.post(`/api/chapters/${ch}/items`, { type: 'mcq', prompt: 'Q', explanation: 'Explication gardée',
    choices: [{ text: 'a', correct: true, why: 'w' }, { text: 'b', correct: false }] });
  const fc = await c.post(`/api/chapters/${ch}/items`, { type: 'flashcard', prompt: 'Q2', answer: 'R2', explanation: 'E2' });
  assert.equal((await c.get('/api/review/today')).json.new, 2);
  const s1 = await c.patch(`/api/items/${mcq.json.id}`, { suspended: true });
  const s2 = await c.patch(`/api/items/${fc.json.id}`, { suspended: true });
  assert.equal(s1.status, 200, s1.body);
  assert.equal(s2.status, 200, s2.body);
  assert.equal(s1.json.explanation, 'Explication gardée');
  assert.equal(s1.json.choices.length, 2);
  assert.deepEqual([s2.json.answer, s2.json.explanation], ['R2', 'E2']);
  assert.equal((await c.get('/api/review/today')).json.new, 0);
  const edited = await c.patch(`/api/items/${fc.json.id}`, { answer: 'R3' });
  assert.deepEqual([edited.json.prompt, edited.json.answer, edited.json.suspended], ['Q2', 'R3', true]);
  await app.close();
});

test('changing one scheduler setting keeps the others; bad timezone refused', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  await c.put('/api/me/settings', { scheduler: { new_per_day: 7, request_retention: 0.85 } });
  const r = await c.put('/api/me/settings', { scheduler: { enable_fuzz: false } });
  assert.deepEqual(r.json.user.settings, { request_retention: 0.85, maximum_interval: 36500, enable_fuzz: false, new_per_day: 7 });
  assert.equal((await c.put('/api/me/settings', { timezone: 'Mars/Olympus' })).status, 400);
  await app.close();
});

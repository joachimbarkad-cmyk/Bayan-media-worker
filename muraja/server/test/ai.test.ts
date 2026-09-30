import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { makeApp, signup, chapter, makePdf } from './helpers.ts';
import type { JsonCaller } from '../generation.ts';

const SECRET = 'x'.repeat(40);
const LOREM = 'La purification est une condition de validite de la priere selon les quatre ecoles.';

test('without a personal key, generation says so honestly and nothing is simulated', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  const n = (await c.post(`/api/chapters/${ch}/notes`, { title: 'F', body: 'texte' })).json;
  const r = await c.post(`/api/notes/${n.id}/explain`, {});
  assert.equal(r.status, 409);
  assert.match(r.json.error, /pas activée sur ce site/);
  assert.equal((await c.put('/api/ai/key', { provider: 'anthropic', api_key: 'sk-ant-test-123456' })).status, 409);
  await app.close();
});

test('personal key is encrypted at rest; explain and question generation are validated, stored once, sources checked', async () => {
  const calls: string[] = [];
  const fake: JsonCaller = async (cfg, prompt, _schema, name) => {
    calls.push(`${cfg.provider}:${cfg.model}:${cfg.apiKey}:${name}`);
    assert.match(prompt, /<cours>/);
    if (name === 'explanation') return { title: 'T', explanation: 'Explication simple.', points_to_check: ['exception éventuelle'] };
    return {
      flashcards: [
        { question: 'Statut ?', answer: 'Condition de validité', skill: 'definition', pages: [1], excerpt: 'condition de validite de la priere' },
        { question: 'Hors cours ?', answer: 'x', skill: 'application', pages: [9], excerpt: 'inventé' },
      ],
      mcq: [
        { question: 'Q', choices: [{ text: 'a', correct: true, why: 'w' }, { text: 'b', correct: false, why: 'w' }], explanation: '', skill: 'distinction', pages: [1], excerpt: '' },
        { question: 'Deux bonnes', choices: [{ text: 'a', correct: true, why: '' }, { text: 'b', correct: true, why: '' }], explanation: '', skill: 'definition', pages: [], excerpt: '' },
      ],
      open: [],
    };
  };
  const { app, dataDir } = await makeApp({ secretKey: SECRET, callJson: fake });
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  assert.equal((await c.put('/api/ai/key', { provider: 'anthropic', api_key: 'sk-ant-SECRETKEY-9876' })).json.model, 'claude-opus-5-5');
  const st = (await c.get('/api/ai/status')).json;
  assert.equal(st.configured.key_hint, '…9876');
  assert.ok(!JSON.stringify(st).includes('SECRETKEY'));
  const dbBytes = readFileSync(path.join(dataDir, 'muraja.sqlite')).toString('latin1') + (() => { try { return readFileSync(path.join(dataDir, 'muraja.sqlite-wal')).toString('latin1'); } catch { return ''; } })();
  assert.ok(!dbBytes.includes('SECRETKEY'), 'key must not be stored in clear');

  const n = (await c.post(`/api/chapters/${ch}/notes`, { title: 'Fiche', body: 'La purification précède la prière.' })).json;
  const e1 = await c.post(`/api/notes/${n.id}/explain`, {});
  assert.equal(e1.status, 200, e1.body);
  const e2 = await c.post(`/api/notes/${n.id}/explain`, {});
  assert.equal(e2.json.stored, true, 'generated once, then reused');
  assert.equal(calls.length, 1);
  assert.equal(calls[0], 'anthropic:claude-opus-5-5:sk-ant-SECRETKEY-9876:explanation');

  const doc = (await c.upload(`/api/chapters/${ch}/documents/upload`, 'c.pdf', await makePdf([LOREM, '']), 'application/pdf')).json;
  const noText = await c.post(`/api/documents/${doc.id}/generate`, { from_page: 2, to_page: 2 });
  assert.equal(noText.status, 400);
  assert.match(noText.json.error, /pas de texte lisible/);
  const prev = (await c.post(`/api/documents/${doc.id}/generate`, { from_page: 1, to_page: 2 })).json;
  assert.deepEqual(prev.skipped_pages, [2]);
  assert.equal(prev.mcq.length, 1, 'MCQ with two correct answers dropped');
  assert.deepEqual(prev.flashcards[1].pages, [], 'page outside the selection dropped');
  assert.equal((await c.get(`/api/chapters/${ch}`)).json.items.length, 0, 'preview writes nothing');
  const saved = (await c.post(`/api/documents/${doc.id}/generated`, { flashcards: prev.flashcards, mcq: prev.mcq, open: [] })).json;
  assert.deepEqual([saved.count, saved.verified], [3, 1]);
  const items = (await c.get(`/api/chapters/${ch}`)).json.items;
  assert.ok(items.every((i: any) => i.origin === 'ai:anthropic'));
  await app.close();
});

test('daily generation limit protects the learner budget', async () => {
  const fake: JsonCaller = async () => ({ title: 'T', explanation: 'E', points_to_check: [] });
  const { app } = await makeApp({ secretKey: SECRET, callJson: fake });
  const c = await signup(app, 'a@example.org');
  const ch = await chapter(c);
  await c.put('/api/ai/key', { provider: 'anthropic', api_key: 'sk-ant-abcdefgh' });
  let last = 0;
  for (let i = 0; i < 41; i++) {
    const n = (await c.post(`/api/chapters/${ch}/notes`, { title: `F${i}`, body: 'b' })).json;
    last = (await c.post(`/api/notes/${n.id}/explain`, {})).status;
  }
  assert.equal(last, 429);
  await app.close();
});

test('a bad key gets an honest error from the real provider API (no cost: request is rejected)', async (t) => {
  const { app } = await makeApp({ secretKey: SECRET });
  const c = await signup(app, 'a@example.org');
  const r = await c.post('/api/ai/test', { provider: 'anthropic', api_key: 'sk-ant-invalid-key-for-test' });
  if (r.status === 502 && /injoignable/.test(r.json.error)) { t.skip('api.anthropic.com injoignable depuis cet environnement'); await app.close(); return; }
  assert.equal(r.status, 400, r.body);
  assert.match(r.json.error, /Clé API refusée/);
  await app.close();
});

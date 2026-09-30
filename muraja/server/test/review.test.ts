import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { makeApp, signup, chapter, tmpDir, Client } from './helpers.ts';

const DAY = 86400_000;

async function seed(c: Client, n: number, type: 'flashcard' | 'mcq' = 'flashcard') {
  const ch = await chapter(c);
  for (let i = 0; i < n; i++) {
    const body = type === 'mcq'
      ? { type, prompt: `QCM ${i}`, choices: [{ text: 'bonne', correct: true }, { text: 'b', correct: false }, { text: 'c', correct: false }, { text: 'd', correct: false }] }
      : { type, prompt: `Question ${i}`, answer: `Réponse ${i}` };
    const r = await c.post(`/api/chapters/${ch}/items`, body);
    assert.equal(r.status, 200, r.body);
  }
  return ch;
}

async function answer(c: Client, sessionId: string, extra: Record<string, unknown> = {}) {
  const cur = (await c.get(`/api/review/sessions/${sessionId}`)).json;
  const body = { session_id: sessionId, item_id: cur.item.id, review_id: randomUUID(), expected_version: cur.item.version, rating: 3, ...extra };
  return { cur, body, res: await c.post('/api/review/answer', body) };
}

test('double click: same review id is idempotent, a second different click is refused', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  await seed(c, 2);
  const s = (await c.post('/api/review/sessions', {})).json;
  const { body, res } = await answer(c, s.id);
  assert.equal(res.status, 200);
  const again = await c.post('/api/review/answer', body);
  assert.equal(again.status, 200);
  assert.equal(again.json.duplicate, true);
  const other = await c.post('/api/review/answer', { ...body, review_id: randomUUID() });
  assert.equal(other.status, 409);
  const prog = (await c.get('/api/progress')).json;
  assert.equal(prog.activities.reviews_total, 1, 'only one review recorded');
  assert.equal(again.json.session.position, 1, 'session advanced exactly once');
  await app.close();
});

test('reviews and session position persist across a restart (interrupted session)', async () => {
  const dataDir = tmpDir();
  let t = Date.UTC(2026, 8, 30, 6, 0);
  const now = () => t;
  let { app } = await makeApp({ dataDir, now });
  const c = await signup(app, 'a@example.org');
  await seed(c, 5);
  const s = (await c.post('/api/review/sessions', {})).json;
  await answer(c, s.id, { rating: 3 });
  await answer(c, s.id, { rating: 4 });
  const cookie = c.cookie;
  await app.close(); // interruption

  ({ app } = await makeApp({ dataDir, now }));
  const c2 = new Client(app);
  c2.cookie = cookie;
  const today = (await c2.get('/api/review/today')).json;
  assert.equal(today.session.id, s.id);
  assert.equal(today.session.position, 2);
  const resumed = (await c2.post('/api/review/sessions', {})).json;
  assert.equal(resumed.resumed, true);
  const cur = (await c2.get(`/api/review/sessions/${s.id}`)).json;
  assert.equal(cur.item.prompt, 'Question 2');
  const exp = (await c2.get('/api/export')).json;
  assert.equal(exp.review_logs.length, 2);
  const reviewed = exp.review_state.filter((r: any) => r.reps > 0);
  assert.equal(reviewed.length, 2);
  assert.ok(reviewed.every((r: any) => r.due > t), 'FSRS scheduled into the future');
  await app.close();
});

test('FSRS schedule: Easy goes further than Hard, Again comes back in the same session', async () => {
  let t = Date.UTC(2026, 8, 30, 6, 0);
  const { app } = await makeApp({ now: () => t });
  const c = await signup(app, 'a@example.org');
  await c.put('/api/me/settings', { scheduler: { enable_fuzz: false } });
  await seed(c, 3);
  const s = (await c.post('/api/review/sessions', {})).json;
  const a = (await answer(c, s.id, { rating: 1 })).res.json;
  const h = (await answer(c, s.id, { rating: 2 })).res.json;
  const e = (await answer(c, s.id, { rating: 4 })).res.json;
  assert.ok(e.next_due > h.next_due && h.next_due > a.next_due);
  assert.equal(a.session.total, 4, 'Again re-queued the card');
  const cur = (await c.get(`/api/review/sessions/${s.id}`)).json;
  assert.equal(cur.item.prompt, 'Question 0');
  await app.close();
});

test('today uses the user local day in Indian/Reunion (UTC+4)', async () => {
  // 19:30 UTC on 30/09 = 23:30 in Réunion; the local day ends at 20:00 UTC.
  let t = Date.UTC(2026, 8, 30, 10, 0);
  const { app } = await makeApp({ now: () => t });
  const c = await signup(app, 'a@example.org');
  assert.equal((await c.get('/api/me')).json.user.timezone, 'Indian/Reunion');
  await c.put('/api/me/settings', { scheduler: { enable_fuzz: false, new_per_day: 10 } });
  await seed(c, 1);
  // Graduate the card: Easy on a new card schedules it days ahead.
  const s = (await c.post('/api/review/sessions', {})).json;
  const r = (await answer(c, s.id, { rating: 4 })).res.json;
  const dueDate = r.next_due as number;
  // Just before local midnight of the due day's previous day: not due. Just after local midnight of the due day: due.
  const dueLocalMidnight = Math.floor((dueDate + 4 * 3600_000) / DAY) * DAY - 4 * 3600_000;
  t = dueLocalMidnight - 60_000;
  assert.equal((await c.get('/api/review/today')).json.due, 0);
  t = dueLocalMidnight + 60_000;
  const today = (await c.get('/api/review/today')).json;
  assert.equal(today.due, 1);
  assert.equal(today.date, new Date(dueLocalMidnight + 4 * 3600_000).toISOString().slice(0, 10));
  // Same instant seen from UTC would still be the previous day.
  assert.notEqual(today.date, new Date(t).toISOString().slice(0, 10));
  await app.close();
});

test('new cards per day quota is respected in the local day', async () => {
  let t = Date.UTC(2026, 8, 30, 6, 0);
  const { app } = await makeApp({ now: () => t });
  const c = await signup(app, 'a@example.org');
  await c.put('/api/me/settings', { scheduler: { new_per_day: 3 } });
  await seed(c, 10);
  assert.equal((await c.get('/api/review/today')).json.new, 3);
  const s = (await c.post('/api/review/sessions', {})).json;
  for (let i = 0; i < 3; i++) await answer(c, s.id, { rating: 4 });
  assert.equal((await c.get('/api/review/today')).json.new, 0);
  t += DAY;
  assert.equal((await c.get('/api/review/today')).json.new, 3);
  await app.close();
});

test('MCQ: server grades, reveals explanations, shuffles positions; wrong answer = Again', async () => {
  const { app } = await makeApp();
  const c = await signup(app, 'a@example.org');
  await seed(c, 1, 'mcq');
  const s = (await c.post('/api/review/sessions', {})).json;
  const positions = new Set<number>();
  for (let i = 0; i < 40; i++) {
    const cur = (await c.get(`/api/review/sessions/${s.id}`)).json;
    assert.equal(cur.item.choices[0].correct, undefined, 'correctness not sent before answering');
    positions.add(cur.item.choices.findIndex((ch: any) => ch.text === 'bonne'));
  }
  assert.ok(positions.size >= 3, `correct answer should move: ${[...positions]}`);
  const cur = (await c.get(`/api/review/sessions/${s.id}`)).json;
  const wrong = cur.item.choices.find((ch: any) => ch.text !== 'bonne').index;
  const r = await c.post('/api/review/answer', { session_id: s.id, item_id: cur.item.id, review_id: randomUUID(), expected_version: cur.item.version, choice_index: wrong });
  assert.equal(r.json.correct, false);
  assert.equal(r.json.rating, 1);
  assert.equal(r.json.choices.filter((ch: any) => ch.correct).length, 1);
  await app.close();
});

test('progress separates activities from mastery; MCQ success counts as recognition only', async () => {
  let t = Date.UTC(2026, 8, 1, 6, 0);
  const { app } = await makeApp({ now: () => t });
  const c = await signup(app, 'a@example.org');
  await c.put('/api/me/settings', { scheduler: { enable_fuzz: false } });
  await seed(c, 1);
  await seed(c, 1, 'mcq');
  for (let round = 0; round < 12; round++) {
    const s = (await c.post('/api/review/sessions', { resume: false })).json;
    if (!s.id) { t += 5 * DAY; continue; }
    for (;;) {
      const cur = (await c.get(`/api/review/sessions/${s.id}`)).json;
      if (!cur.item) break;
      const extra = cur.item.type === 'mcq' ? { choice_index: 0, rating: undefined } : { rating: 4 };
      await c.post('/api/review/answer', { session_id: s.id, item_id: cur.item.id, review_id: randomUUID(), expected_version: cur.item.version, ...extra });
    }
    t += 25 * DAY;
  }
  const p = (await c.get('/api/progress')).json;
  assert.ok(p.activities.reviews_total >= 4);
  assert.equal(p.items.mastered, 1, 'the flashcard is mastered');
  assert.equal(p.items.recognized, 1, 'the MCQ is only recognised');
  await app.close();
});

test('learning cards are due only once their step has elapsed; review cards by local day', async () => {
  let t = Date.UTC(2026, 8, 30, 6, 0);
  const { app } = await makeApp({ now: () => t });
  const c = await signup(app, 'a@example.org');
  await c.put('/api/me/settings', { scheduler: { enable_fuzz: false } });
  await seed(c, 1);
  const s = (await c.post('/api/review/sessions', {})).json;
  const r = (await answer(c, s.id, { rating: 3 })).res.json; // new → learning step (minutes)
  assert.ok(r.next_due - t < 3600_000);
  let today = (await c.get('/api/review/today')).json;
  assert.deepEqual([today.due, today.later_today], [0, 1]);
  t = r.next_due + 1000;
  today = (await c.get('/api/review/today')).json;
  assert.deepEqual([today.due, today.later_today], [1, 0]);
  await app.close();
});

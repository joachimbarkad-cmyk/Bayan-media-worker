import type { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { tx } from './db.ts';
import { Sealer } from './crypto.ts';
import { UserError } from './pdf.ts';
import {
  PROVIDERS, MAX_INPUT_CHARS, DAILY_LIMIT, ExplainOut, QuestionsOut, EXPLAIN_SCHEMA, QUESTIONS_SCHEMA,
  explainPrompt, questionsPrompt, callJson as realCallJson, listModels, type ProviderName, type ProviderConfig,
} from './generation.ts';
import { ImportV1 } from './importSchema.ts';
import type { Ctx } from './ctx.ts';

const Provider = z.enum(['anthropic', 'openai', 'gemini']);

export function registerAi(app: FastifyInstance, ctx: Ctx) {
  const { db, auth, owned, now } = ctx;
  const sealer = ctx.secret && ctx.secret.length >= 32 ? new Sealer(ctx.secret) : null;
  const callJson = ctx.callJson ?? realCallJson;

  function config(userId: string): ProviderConfig | null {
    const row = db.prepare('SELECT provider, model, key_enc FROM ai_settings WHERE user_id = ?').get(userId) as any;
    if (!row || !sealer) return null;
    try {
      return { provider: row.provider, model: row.model, apiKey: sealer.open(row.key_enc) };
    } catch {
      return null; // secret changed: key unreadable, must be re-entered
    }
  }

  function requireConfig(userId: string): ProviderConfig {
    const c = config(userId);
    if (!c) {
      throw new UserError(sealer
        ? "Aucune IA n'est connectée à votre compte. Ajoutez votre clé dans Réglages › Assistant IA, ou utilisez Claude/ChatGPT connecté à Murāja'a."
        : "La génération intégrée n'est pas activée sur ce site (clé de chiffrement serveur absente). Vous pouvez connecter Claude ou ChatGPT à Murāja'a, ou importer des supports préparés.", 409);
    }
    return c;
  }

  /** Counts one generation against the per-user daily limit (local day). */
  function consume(u: { id: string; timezone: string }) {
    const day = ctx.dayBounds(u.timezone, now()).date;
    const row = db.prepare('SELECT count FROM ai_usage WHERE user_id = ? AND day = ?').get(u.id, day) as any;
    if ((row?.count ?? 0) >= DAILY_LIMIT) throw new UserError(`Limite de ${DAILY_LIMIT} générations par jour atteinte. Elle protège votre budget ; réessayez demain.`, 429);
    db.prepare('INSERT INTO ai_usage (user_id, day, count) VALUES (?,?,1) ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1').run(u.id, day);
  }

  function glossary(userId: string): string[] {
    return (db.prepare('SELECT term, arabic, definition FROM glossary WHERE user_id = ? ORDER BY term LIMIT 100').all(userId) as any[])
      .map((g) => `${g.term}${g.arabic ? ` (${g.arabic})` : ''} : ${g.definition}`);
  }

  app.get('/api/ai/status', async (req) => {
    const u = auth(req);
    const row = db.prepare('SELECT provider, model, key_hint, updated_at FROM ai_settings WHERE user_id = ?').get(u.id) as any;
    const used = (db.prepare('SELECT count FROM ai_usage WHERE user_id = ? AND day = ?').get(u.id, ctx.dayBounds(u.timezone, now()).date) as any)?.count ?? 0;
    return {
      key_storage: !!sealer,
      configured: row ? { ...row, readable: !!config(u.id) } : null,
      providers: PROVIDERS,
      daily_limit: DAILY_LIMIT, used_today: used,
    };
  });

  app.post('/api/ai/test', async (req) => {
    const u = auth(req);
    const body = z.object({ provider: Provider, api_key: z.string().trim().min(8).max(500).optional() }).parse(req.body);
    const key = body.api_key ?? (config(u.id)?.provider === body.provider ? config(u.id)!.apiKey : null);
    if (!key) throw new UserError('Entrez une clé à tester.');
    const models = await listModels(body.provider, key);
    return { ok: true, models: models.slice(0, 200) };
  });

  app.put('/api/ai/key', async (req) => {
    const u = auth(req);
    if (!sealer) throw new UserError("L'enregistrement de clés personnelles n'est pas activé sur ce site (MURAJA_SECRET_KEY absente).", 409);
    const body = z.object({
      provider: Provider,
      model: z.string().trim().max(100).optional(),
      api_key: z.string().trim().min(8).max(500).optional(),
    }).parse(req.body);
    const existing = db.prepare('SELECT provider, key_enc FROM ai_settings WHERE user_id = ?').get(u.id) as any;
    const model = body.model || PROVIDERS[body.provider].defaultModel;
    if (!model) throw new UserError('Choisissez un modèle (bouton « Tester la clé » pour voir ceux disponibles).');
    let keyEnc: string, hint: string;
    if (body.api_key) {
      keyEnc = sealer.seal(body.api_key);
      hint = `…${body.api_key.slice(-4)}`;
    } else if (existing && existing.provider === body.provider) {
      keyEnc = existing.key_enc;
      hint = (db.prepare('SELECT key_hint FROM ai_settings WHERE user_id = ?').get(u.id) as any).key_hint;
    } else {
      throw new UserError('Entrez votre clé API.');
    }
    db.prepare(`INSERT INTO ai_settings (user_id, provider, model, key_enc, key_hint, updated_at) VALUES (?,?,?,?,?,?)
      ON CONFLICT(user_id) DO UPDATE SET provider = excluded.provider, model = excluded.model, key_enc = excluded.key_enc,
      key_hint = excluded.key_hint, updated_at = excluded.updated_at`).run(u.id, body.provider, model, keyEnc, hint, now());
    return { ok: true, provider: body.provider, model, key_hint: hint };
  });

  app.delete('/api/ai/key', async (req) => {
    const u = auth(req);
    db.prepare('DELETE FROM ai_settings WHERE user_id = ?').run(u.id);
    return { ok: true };
  });

  // Status used by the older UI button; kept for compatibility.
  app.get('/api/generation/status', async (req) => {
    const u = auth(req);
    const c = config(u.id);
    return c
      ? { available: true, provider: c.provider, message: `IA connectée : ${PROVIDERS[c.provider].label} (${c.model}).` }
      : { available: false, provider: 'aucun', message: "Aucune IA n'est connectée à votre compte. Réglages › Assistant IA." };
  });

  // ---------------------------------------------------------------- explain a note
  app.post('/api/notes/:id/explain', async (req) => {
    const u = auth(req);
    const note = owned('notes', (req.params as any).id, u.id);
    const { regenerate } = z.object({ regenerate: z.boolean().default(false) }).parse(req.body ?? {});
    const title = `Explication simple — ${note.title}`.slice(0, 200);
    if (!regenerate) {
      const prior = db.prepare("SELECT * FROM notes WHERE user_id = ? AND chapter_id = ? AND title = ? AND origin LIKE 'ai:%'").get(u.id, note.chapter_id, title) as any;
      if (prior) return { available: true, stored: true, note_id: prior.id, message: 'Explication déjà générée : elle est enregistrée dans les fiches.' };
    }
    const cfg = requireConfig(u.id);
    // Course material: the cited document pages when the note has them, else the note itself.
    let pages: Array<{ page: number | null; text: string }> = [];
    if (note.source_document_id && note.source_pages) {
      const nums: number[] = JSON.parse(note.source_pages);
      pages = (db.prepare(`SELECT page_number, text FROM document_pages WHERE document_id = ? AND user_id = ? AND readable = 1
        AND page_number IN (${nums.map(() => '?').join(',')})`).all(note.source_document_id, u.id, ...nums) as any[])
        .map((p) => ({ page: p.page_number, text: p.text }));
    }
    if (note.body.trim()) pages.push({ page: null, text: note.body });
    if (!pages.length) throw new UserError('La fiche est vide : écrivez-la ou reliez-la à des pages du cours.');
    const text = pages.map((p) => p.text).join('\n');
    if (text.length > MAX_INPUT_CHARS) throw new UserError('Texte trop long pour une seule explication : découpez la fiche.');
    consume(u);
    const out = ExplainOut.safeParse(await callJson(cfg, explainPrompt(note.title, pages, glossary(u.id)), EXPLAIN_SCHEMA, 'explanation'));
    if (!out.success) throw new UserError("La réponse de l'IA ne respecte pas le format attendu. Réessayez.", 502);
    const body = out.data.explanation + (out.data.points_to_check.length ? `\n\nÀ vérifier dans le cours :\n${out.data.points_to_check.map((p) => `• ${p}`).join('\n')}` : '');
    const data = ImportV1.parse({ format: 'muraja.v1', notes: [{ title, body }] });
    const saved = tx(db, () => ctx.saveContent(u.id, note.chapter_id, data, null, null, `ai:${cfg.provider}`));
    return { available: true, stored: false, note_id: saved.notes[0], message: 'Explication générée et enregistrée dans les fiches (à vérifier).' };
  });

  // ---------------------------------------------------------------- questions from pages (preview, then save)
  app.post('/api/documents/:id/generate', async (req) => {
    const u = auth(req);
    const doc = owned('documents', (req.params as any).id, u.id);
    const body = z.object({
      from_page: z.number().int().min(1).default(1), to_page: z.number().int().min(1).optional(),
      flashcards: z.number().int().min(0).max(30).default(8), mcq: z.number().int().min(0).max(20).default(4), open: z.number().int().min(0).max(10).default(2),
    }).parse(req.body ?? {});
    const to = body.to_page ?? body.from_page;
    if (to < body.from_page || to - body.from_page > 60) throw new UserError('Choisissez au plus 60 pages à la fois.');
    const rows = db.prepare(`SELECT page_number, text, readable FROM document_pages WHERE document_id = ? AND user_id = ?
      AND page_number BETWEEN ? AND ? ORDER BY page_number`).all(doc.id, u.id, body.from_page, to) as any[];
    const readable = rows.filter((r) => r.readable);
    if (!readable.length) throw new UserError("Ces pages n'ont pas de texte lisible (document scanné ?) : aucune question fiable ne peut en être tirée.");
    const pages = readable.map((r) => ({ page: doc.kind === 'pdf' ? r.page_number : null, text: r.text }));
    if (pages.reduce((n, p) => n + p.text.length, 0) > MAX_INPUT_CHARS) throw new UserError('Trop de texte en une fois : réduisez le nombre de pages.');
    const cfg = requireConfig(u.id);
    consume(u);
    const raw = await callJson(cfg, questionsPrompt(pages, glossary(u.id), body), QUESTIONS_SCHEMA, 'questions');
    const out = QuestionsOut.safeParse(raw);
    if (!out.success) throw new UserError("La réponse de l'IA ne respecte pas le format attendu. Réessayez.", 502);
    // Keep only MCQs with exactly one correct choice; drop pages outside the selected range.
    const inRange = (ps: number[]) => ps.filter((p) => p >= body.from_page && p <= to);
    const g = out.data;
    return {
      provider: cfg.provider, model: cfg.model,
      skipped_pages: rows.filter((r) => !r.readable).map((r) => r.page_number),
      flashcards: g.flashcards.map((f) => ({ ...f, pages: inRange(f.pages) })),
      mcq: g.mcq.filter((q) => q.choices.filter((c) => c.correct).length === 1).map((q) => ({ ...q, pages: inRange(q.pages) })),
      open: g.open.map((o) => ({ ...o, pages: inRange(o.pages) })),
    };
  });

  app.post('/api/documents/:id/generated', async (req) => {
    const u = auth(req);
    const doc = owned('documents', (req.params as any).id, u.id);
    const cfg = config(u.id);
    const b = QuestionsOut.parse(req.body);
    const src = (x: { pages: number[]; excerpt: string }) => (x.pages.length || x.excerpt ? { pages: x.pages, excerpt: x.excerpt || undefined } : undefined);
    const data = ImportV1.parse({
      format: 'muraja.v1',
      flashcards: b.flashcards.map((f) => ({ question: f.question, answer: f.answer, skill: f.skill, source: src(f) })),
      mcq: b.mcq.map((q) => ({ question: q.question, choices: q.choices.map((c) => ({ text: c.text, correct: c.correct, why: c.why || undefined })), explanation: q.explanation || undefined, skill: q.skill, source: src(q) })),
      open: b.open.map((o) => ({ question: o.question, answer: o.answer, source: src(o) })),
    });
    const saved = tx(db, () => ctx.saveContent(u.id, doc.chapter_id, data, null, doc.id, `ai:${cfg?.provider ?? 'inconnu'}`));
    return { ok: true, count: saved.items.length, verified: saved.verified };
  });
}

export type { ProviderName };

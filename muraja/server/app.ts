import Fastify, { type FastifyInstance, type FastifyReply, type FastifyRequest } from 'fastify';
import cookie from '@fastify/cookie';
import multipart from '@fastify/multipart';
import fastifyStatic from '@fastify/static';
import { randomUUID, randomInt } from 'node:crypto';
import { mkdirSync, existsSync, createReadStream, rmSync, writeFileSync, unlinkSync } from 'node:fs';
import path from 'node:path';
import { z, ZodError } from 'zod';
import { openDb, tx, type DB } from './db.ts';
import { hashPassword, verifyPassword, newSessionToken, hashToken, AttemptLimiter, SESSION_MS } from './auth.ts';
import { extractPdf, normalizeText, UserError } from './pdf.ts';
import { resolveSource } from './sources.ts';
import { SchedulerSettings, SchedulerPatch, emptyState, applyRating, Rating, State, type StateRow, type Grade } from './fsrs.ts';
import { dayBounds, isValidTimeZone } from './time.ts';
import { registerAi } from './ai.ts';
import { registerOAuth } from './oauth.ts';
import { registerMcp } from './mcp.ts';
import type { JsonCaller } from './generation.ts';
import { ImportV1, treeError, type MindNode } from './importSchema.ts';

export interface AppOptions {
  dataDir: string;
  staticDir?: string;
  inviteCode?: string;
  secureCookies?: boolean;
  now?: () => number;
  env?: NodeJS.ProcessEnv;
  /** Public HTTPS base URL (e.g. https://muraja.example.org), used by OAuth/MCP metadata. */
  publicUrl?: string;
  /** Secret used to encrypt personal API keys (else MURAJA_SECRET_KEY). */
  secretKey?: string;
  /** Test hook replacing real provider calls. */
  callJson?: JsonCaller;
}

const COOKIE = 'muraja_session';
const MAX_PDF_BYTES = 30 * 1024 * 1024;
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;
const MAX_TEXT_CHARS = 400_000;
const SESSION_MAX_ITEMS = 60;
const MAX_REQUEUES = 3;

interface User { id: string; email: string; name: string; timezone: string; settings: string }
declare module 'fastify' {
  interface FastifyRequest { user?: User }
}

const Id = z.string().uuid();
const Name = z.string().trim().min(1).max(200);
const SourceIn = z.object({
  document_id: z.string().uuid().nullable().optional(),
  pages: z.array(z.number().int().min(1).max(10000)).max(50).nullable().optional(),
  excerpt: z.string().trim().max(2000).nullable().optional(),
}).nullable().optional();
const Choice = z.object({ text: z.string().trim().min(1).max(1000), correct: z.boolean(), why: z.string().trim().max(2000).default('') });
const ItemIn = z.object({
  type: z.enum(['flashcard', 'mcq', 'open']),
  prompt: z.string().trim().min(1).max(2000),
  answer: z.string().trim().max(5000).default(''),
  explanation: z.string().trim().max(5000).default(''),
  choices: z.array(Choice).min(2).max(8).nullable().optional(),
  skill: z.enum(['definition', 'distinction', 'application']).nullable().optional(),
  source: SourceIn,
});

// PATCH schema without defaults: an absent field must keep its stored value (Zod 4 applies defaults inside .partial()).
const ItemPatch = z.object({
  prompt: z.string().trim().min(1).max(2000).optional(),
  answer: z.string().trim().max(5000).optional(),
  explanation: z.string().trim().max(5000).optional(),
  choices: z.array(Choice).min(2).max(8).nullable().optional(),
  skill: z.enum(['definition', 'distinction', 'application']).nullable().optional(),
  source: SourceIn,
  suspended: z.boolean().optional(),
});

function parse<T extends z.ZodTypeAny>(schema: T, data: unknown): z.infer<T> {
  return schema.parse(data);
}

function checkItemShape(it: { type: string; answer: string; choices?: Array<{ correct: boolean }> | null }) {
  if (it.type === 'mcq') {
    if (!it.choices || it.choices.filter((c) => c.correct).length !== 1) {
      throw new UserError('Un QCM doit avoir au moins deux propositions, dont exactement une correcte.');
    }
  } else if (!it.answer) {
    throw new UserError('La réponse est obligatoire.');
  }
}

export function userSettings(u: Pick<User, 'settings'>): SchedulerSettings {
  let raw: unknown = {};
  try { raw = JSON.parse(u.settings); } catch { /* defaults */ }
  const r = SchedulerSettings.safeParse(raw);
  return r.success ? r.data : SchedulerSettings.parse({});
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = randomInt(i + 1);
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function itemOut(row: any) {
  return {
    ...row,
    choices: row.choices ? JSON.parse(row.choices) : null,
    source_pages: row.source_pages ? JSON.parse(row.source_pages) : null,
    suspended: !!row.suspended,
  };
}

export async function buildApp(opts: AppOptions): Promise<{ app: FastifyInstance; db: DB }> {
  const now = opts.now ?? Date.now;
  const env = opts.env ?? process.env;
  const db = openDb(opts.dataDir);
  const filesDir = path.join(opts.dataDir, 'files');
  mkdirSync(filesDir, { recursive: true });
  const limiter = new AttemptLimiter();
  const app = Fastify({ logger: false, bodyLimit: 8 * 1024 * 1024, trustProxy: true });

  await app.register(cookie);
  await app.register(multipart, { limits: { fileSize: MAX_PDF_BYTES, files: 1, fields: 5 } });

  // ------------------------------------------------------------------ hooks
  app.addHook('onSend', async (req, reply, payload) => {
    reply.header('X-Content-Type-Options', 'nosniff');
    reply.header('Referrer-Policy', 'same-origin');
    reply.header('X-Frame-Options', 'SAMEORIGIN');
    if (!reply.getHeader('Content-Security-Policy')) {
      reply.header('Content-Security-Policy',
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; " +
        "font-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'self'; form-action 'self'");
    }
    if (req.url.startsWith('/api/')) reply.header('Cache-Control', 'no-store');
    return payload;
  });

  // Mutating API calls must carry a custom header: cross-site forms cannot set it (CSRF defence).
  app.addHook('onRequest', async (req, reply) => {
    if (req.url.startsWith('/api/') && !['GET', 'HEAD', 'OPTIONS'].includes(req.method) && req.headers['x-muraja'] !== '1') {
      return reply.code(403).send({ error: 'Requête refusée.' });
    }
  });

  app.setErrorHandler((err: any, _req, reply) => {
    if (err instanceof UserError) return reply.code(err.status).send({ error: err.message });
    if (err instanceof ZodError) {
      return reply.code(400).send({ error: 'Données invalides.', details: err.issues.map((i) => `${i.path.join('.') || '—'} : ${i.message}`) });
    }
    if (err.code === 'FST_REQ_FILE_TOO_LARGE') return reply.code(413).send({ error: 'Fichier trop volumineux.' });
    if (err.statusCode && err.statusCode < 500) return reply.code(err.statusCode).send({ error: 'Requête invalide.' });
    console.error(err);
    return reply.code(500).send({ error: 'Erreur interne. Réessayez ; vos données enregistrées ne sont pas perdues.' });
  });

  function currentUser(req: FastifyRequest): User | null {
    const token = req.cookies[COOKIE];
    if (!token) return null;
    const th = hashToken(token);
    const row = db.prepare(
      `SELECT u.id, u.email, u.name, u.timezone, u.settings, s.expires_at FROM sessions s JOIN users u ON u.id = s.user_id
       WHERE s.token_hash = ? AND s.expires_at > ?`,
    ).get(th, now()) as (User & { expires_at: number }) | undefined;
    if (!row) return null;
    // Sliding expiry: an account in regular use stays signed in.
    if (row.expires_at - now() < SESSION_MS / 2) db.prepare('UPDATE sessions SET expires_at = ? WHERE token_hash = ?').run(now() + SESSION_MS, th);
    const { expires_at: _e, ...user } = row;
    return user;
  }

  function auth(req: FastifyRequest): User {
    const u = currentUser(req);
    if (!u) throw new UserError('Connexion requise.', 401);
    return u;
  }

  /** Fetch a row owned by the user or fail with 404 (never reveals other users' rows). */
  function owned<T = any>(table: string, id: string, userId: string): T {
    if (!Id.safeParse(id).success) throw new UserError('Introuvable.', 404);
    const row = db.prepare(`SELECT * FROM ${table} WHERE id = ? AND user_id = ?`).get(id, userId);
    if (!row) throw new UserError('Introuvable.', 404);
    return row as T;
  }

  function startSession(reply: FastifyReply, userId: string) {
    const s = newSessionToken(now());
    db.prepare('INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?,?,?,?)').run(s.tokenHash, userId, now(), s.expiresAt);
    reply.setCookie(COOKIE, s.token, {
      path: '/', httpOnly: true, sameSite: 'lax', secure: !!opts.secureCookies, maxAge: 400 * 86400, // real expiry is enforced server-side (sliding)
    });
  }

  function publicUser(u: User) {
    return { id: u.id, email: u.email, name: u.name, timezone: u.timezone, settings: userSettings(u) };
  }

  // ------------------------------------------------------------------ auth
  app.get('/api/health', async () => ({ ok: true }));

  app.post('/api/auth/register', async (req, reply) => {
    const body = parse(z.object({
      email: z.string().trim().toLowerCase().email().max(200), name: Name,
      password: z.string().min(8, 'au moins 8 caractères').max(200), invite: z.string().optional(),
    }), req.body);
    if (opts.inviteCode && body.invite !== opts.inviteCode) throw new UserError("Code d'invitation incorrect.", 403);
    if (db.prepare('SELECT 1 FROM users WHERE email = ?').get(body.email)) throw new UserError('Un compte existe déjà avec cette adresse.', 409);
    const id = randomUUID();
    db.prepare('INSERT INTO users (id, email, name, password_hash, created_at) VALUES (?,?,?,?,?)')
      .run(id, body.email, body.name, hashPassword(body.password), now());
    startSession(reply, id);
    return { user: publicUser(db.prepare('SELECT * FROM users WHERE id = ?').get(id) as unknown as User) };
  });

  app.post('/api/auth/login', async (req, reply) => {
    const body = parse(z.object({ email: z.string().trim().toLowerCase().max(200), password: z.string().max(200) }), req.body);
    const key = `${body.email}|${req.ip}`;
    if (limiter.blocked(key)) throw new UserError('Trop de tentatives. Réessayez dans quelques minutes.', 429);
    const u = db.prepare('SELECT * FROM users WHERE email = ?').get(body.email) as any;
    if (!u || !verifyPassword(body.password, u.password_hash)) {
      limiter.record(key);
      throw new UserError('Adresse ou mot de passe incorrect.', 401);
    }
    limiter.reset(key);
    startSession(reply, u.id);
    return { user: publicUser(u) };
  });

  app.post('/api/auth/logout', async (req, reply) => {
    const token = req.cookies[COOKIE];
    if (token) db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(hashToken(token));
    reply.clearCookie(COOKIE, { path: '/' });
    return { ok: true };
  });

  app.get('/api/me', async (req) => ({ user: publicUser(auth(req)) }));

  app.put('/api/me/settings', async (req) => {
    const u = auth(req);
    const body = parse(z.object({
      timezone: z.string().max(100).optional(),
      scheduler: SchedulerPatch.optional(),
      name: Name.optional(),
    }), req.body);
    if (body.timezone && !isValidTimeZone(body.timezone)) throw new UserError('Fuseau horaire inconnu.');
    const patch = Object.fromEntries(Object.entries(body.scheduler ?? {}).filter(([, v]) => v !== undefined));
    const merged = SchedulerSettings.parse({ ...userSettings(u), ...patch });
    db.prepare('UPDATE users SET timezone = ?, settings = ?, name = ? WHERE id = ?')
      .run(body.timezone ?? u.timezone, JSON.stringify(merged), body.name ?? u.name, u.id);
    return { user: publicUser(db.prepare('SELECT * FROM users WHERE id = ?').get(u.id) as unknown as User) };
  });


  // ------------------------------------------------------------------ library
  app.get('/api/library', async (req) => {
    const u = auth(req);
    const { end } = dayBounds(u.timezone, now());
    const subjects = db.prepare('SELECT id, name, created_at FROM subjects WHERE user_id = ? ORDER BY name COLLATE NOCASE').all(u.id) as any[];
    const chapters = db.prepare(
      `SELECT c.id, c.subject_id, c.name, c.created_at,
        (SELECT COUNT(*) FROM documents d WHERE d.chapter_id = c.id) AS documents,
        (SELECT COUNT(*) FROM items i WHERE i.chapter_id = c.id) AS items,
        (SELECT COUNT(*) FROM items i JOIN review_state r ON r.item_id = i.id
          WHERE i.chapter_id = c.id AND i.suspended = 0 AND ((r.state = 2 AND r.due < ?) OR (r.state IN (1,3) AND r.due <= ?))) AS due
       FROM chapters c WHERE c.user_id = ? ORDER BY c.created_at`,
    ).all(end, now(), u.id) as any[];
    return { subjects: subjects.map((s) => ({ ...s, chapters: chapters.filter((c) => c.subject_id === s.id) })) };
  });

  app.post('/api/subjects', async (req) => {
    const u = auth(req);
    const { name } = parse(z.object({ name: Name }), req.body);
    const id = randomUUID();
    db.prepare('INSERT INTO subjects (id, user_id, name, created_at) VALUES (?,?,?,?)').run(id, u.id, name, now());
    return { id, name };
  });
  app.patch('/api/subjects/:id', async (req) => {
    const u = auth(req);
    const s = owned('subjects', (req.params as any).id, u.id);
    const { name } = parse(z.object({ name: Name }), req.body);
    db.prepare('UPDATE subjects SET name = ? WHERE id = ?').run(name, s.id);
    return { ok: true };
  });
  app.delete('/api/subjects/:id', async (req) => {
    const u = auth(req);
    const s = owned('subjects', (req.params as any).id, u.id);
    const docs = db.prepare('SELECT d.storage_name FROM documents d JOIN chapters c ON c.id = d.chapter_id WHERE c.subject_id = ?').all(s.id) as any[];
    db.prepare('DELETE FROM subjects WHERE id = ?').run(s.id);
    docs.forEach((d) => removeFile(u.id, d.storage_name));
    return { ok: true };
  });

  app.post('/api/chapters', async (req) => {
    const u = auth(req);
    const body = parse(z.object({ subject_id: z.string(), name: Name }), req.body);
    owned('subjects', body.subject_id, u.id);
    const id = randomUUID();
    db.prepare('INSERT INTO chapters (id, user_id, subject_id, name, created_at) VALUES (?,?,?,?,?)').run(id, u.id, body.subject_id, body.name, now());
    return { id, name: body.name };
  });
  app.patch('/api/chapters/:id', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const { name } = parse(z.object({ name: Name }), req.body);
    db.prepare('UPDATE chapters SET name = ? WHERE id = ?').run(name, c.id);
    return { ok: true };
  });
  app.delete('/api/chapters/:id', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const docs = db.prepare('SELECT storage_name FROM documents WHERE chapter_id = ?').all(c.id) as any[];
    db.prepare('DELETE FROM chapters WHERE id = ?').run(c.id);
    docs.forEach((d) => removeFile(u.id, d.storage_name));
    return { ok: true };
  });

  app.get('/api/chapters/:id', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const subject = db.prepare('SELECT id, name FROM subjects WHERE id = ?').get(c.subject_id);
    const documents = db.prepare(
      'SELECT id, title, kind, mime, size, page_count, extraction_status, extraction_note, created_at FROM documents WHERE chapter_id = ? ORDER BY created_at',
    ).all(c.id);
    const notes = db.prepare('SELECT * FROM notes WHERE chapter_id = ? ORDER BY created_at').all(c.id).map(itemOut);
    const items = db.prepare(
      `SELECT i.*, r.due, r.state, r.reps, r.lapses, r.stability, r.last_rating FROM items i
       LEFT JOIN review_state r ON r.item_id = i.id WHERE i.chapter_id = ? ORDER BY i.created_at`,
    ).all(c.id).map(itemOut);
    const mindmaps = db.prepare('SELECT id, title, origin, source_status, updated_at FROM mindmaps WHERE chapter_id = ? ORDER BY created_at').all(c.id);
    return { chapter: { id: c.id, name: c.name, subject }, documents, notes, items, mindmaps };
  });

  // ------------------------------------------------------------------ documents
  function userDir(userId: string) {
    const d = path.join(filesDir, userId);
    mkdirSync(d, { recursive: true });
    return d;
  }
  function removeFile(userId: string, storageName: string | null) {
    if (!storageName) return;
    try { unlinkSync(path.join(filesDir, userId, storageName)); } catch { /* already gone */ }
  }

  app.post('/api/chapters/:id/documents/upload', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const file = await req.file();
    if (!file) throw new UserError('Aucun fichier reçu.');
    const buf = await file.toBuffer();
    if (file.file.truncated) throw new UserError('Fichier trop volumineux (30 Mo maximum).', 413);
    const head = buf.subarray(0, 12);
    const isPdf = head.subarray(0, 5).toString('latin1') === '%PDF-';
    const imageMime = head[0] === 0x89 && head.subarray(1, 4).toString('latin1') === 'PNG' ? 'image/png'
      : head[0] === 0xff && head[1] === 0xd8 ? 'image/jpeg'
      : head.subarray(0, 4).toString('latin1') === 'RIFF' && head.subarray(8, 12).toString('latin1') === 'WEBP' ? 'image/webp' : null;
    if (!isPdf && !imageMime) throw new UserError('Format non pris en charge. Envoyez un PDF, ou une image PNG/JPEG/WebP (par exemple une carte mentale).');
    if (imageMime && buf.length > MAX_IMAGE_BYTES) throw new UserError('Image trop volumineuse (10 Mo maximum).', 413);
    const rawTitle = (file.fields as any)?.title?.value ?? file.filename ?? 'Document';
    const title = String(rawTitle).replace(/\.(pdf|png|jpe?g|webp)$/i, '').trim().slice(0, 200) || 'Document';
    const id = randomUUID();
    const storageName = `${id}.${isPdf ? 'pdf' : imageMime!.split('/')[1]}`;
    if (isPdf) {
      let extraction;
      try {
        extraction = await extractPdf(new Uint8Array(buf));
      } catch (e) {
        if (e instanceof UserError) throw e;
        throw new UserError("Ce PDF n'a pas pu être ouvert (fichier endommagé ou protégé par mot de passe).");
      }
      writeFileSync(path.join(userDir(u.id), storageName), buf);
      tx(db, () => {
        db.prepare(`INSERT INTO documents (id, user_id, chapter_id, title, kind, mime, size, storage_name, page_count, extraction_status, extraction_note, created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, u.id, c.id, title, 'pdf', 'application/pdf', buf.length, storageName,
          extraction.pages.length, extraction.status, extraction.note, now());
        const ins = db.prepare('INSERT INTO document_pages (document_id, user_id, page_number, text, readable) VALUES (?,?,?,?,?)');
        for (const p of extraction.pages) ins.run(id, u.id, p.page_number, p.text, p.readable ? 1 : 0);
      });
      return { id, title, kind: 'pdf', page_count: extraction.pages.length, extraction_status: extraction.status, extraction_note: extraction.note };
    }
    writeFileSync(path.join(userDir(u.id), storageName), buf);
    const note = "Image consultable. Elle n'est pas transformée en carte interactive : pour cela, importez une structure de nœuds (JSON) ou construisez la carte dans l'éditeur.";
    db.prepare(`INSERT INTO documents (id, user_id, chapter_id, title, kind, mime, size, storage_name, page_count, extraction_status, extraction_note, created_at)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, u.id, c.id, title, 'image', imageMime, buf.length, storageName, 0, 'not_applicable', note, now());
    return { id, title, kind: 'image', extraction_status: 'not_applicable', extraction_note: note };
  });

  app.post('/api/chapters/:id/documents/text', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const body = parse(z.object({ title: Name, text: z.string().min(1).max(MAX_TEXT_CHARS) }), req.body);
    const text = normalizeText(body.text);
    if (!text) throw new UserError('Le texte est vide.');
    const id = randomUUID();
    tx(db, () => {
      db.prepare(`INSERT INTO documents (id, user_id, chapter_id, title, kind, mime, size, storage_name, page_count, extraction_status, extraction_note, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, u.id, c.id, body.title, 'text', 'text/plain', text.length, null, 1, 'ok', '', now());
      db.prepare('INSERT INTO document_pages (document_id, user_id, page_number, text, readable) VALUES (?,?,?,?,1)').run(id, u.id, 1, text);
    });
    return { id, title: body.title, kind: 'text' };
  });

  app.get('/api/documents/:id', async (req) => {
    const u = auth(req);
    const d = owned('documents', (req.params as any).id, u.id);
    const pages = db.prepare('SELECT page_number, text, readable FROM document_pages WHERE document_id = ? AND user_id = ? ORDER BY page_number').all(d.id, u.id);
    const { storage_name: _s, ...doc } = d;
    return { document: doc, pages: pages.map((p: any) => ({ ...p, readable: !!p.readable })) };
  });

  app.get('/api/documents/:id/file', async (req, reply) => {
    const u = auth(req);
    const d = owned('documents', (req.params as any).id, u.id);
    if (!d.storage_name) throw new UserError('Ce document ne contient pas de fichier.', 404);
    const p = path.join(filesDir, u.id, d.storage_name);
    if (!existsSync(p)) throw new UserError('Fichier introuvable.', 404);
    reply.header('Content-Type', d.mime);
    reply.header('Content-Disposition', `inline; filename="${encodeURIComponent(d.title)}.${d.storage_name.split('.').pop()}"`);
    reply.header('Content-Security-Policy', "sandbox; default-src 'none'; img-src 'self'; style-src 'unsafe-inline'");
    reply.header('Cache-Control', 'private, no-store');
    return reply.send(createReadStream(p));
  });

  app.delete('/api/documents/:id', async (req) => {
    const u = auth(req);
    const d = owned('documents', (req.params as any).id, u.id);
    db.prepare('DELETE FROM documents WHERE id = ?').run(d.id);
    removeFile(u.id, d.storage_name);
    return { ok: true };
  });

  // ------------------------------------------------------------------ notes (fiches)
  app.post('/api/chapters/:id/notes', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const body = parse(z.object({ title: Name, body: z.string().max(50000).default(''), source: SourceIn }), req.body);
    const id = randomUUID();
    const src = resolveSource(db, u.id, body.source, 'manual');
    db.prepare(`INSERT INTO notes (id, user_id, chapter_id, title, body, origin, source_document_id, source_pages, source_excerpt, source_status, created_at, updated_at)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, u.id, c.id, body.title, body.body, 'manual', src.source_document_id, src.source_pages, src.source_excerpt, src.source_status, now(), now());
    return itemOut(db.prepare('SELECT * FROM notes WHERE id = ?').get(id));
  });
  app.patch('/api/notes/:id', async (req) => {
    const u = auth(req);
    const n = owned('notes', (req.params as any).id, u.id);
    const body = parse(z.object({ title: Name.optional(), body: z.string().max(50000).optional(), source: SourceIn }), req.body);
    const src = body.source !== undefined ? resolveSource(db, u.id, body.source, n.origin === 'manual' ? 'manual' : 'import') : null;
    db.prepare(`UPDATE notes SET title = ?, body = ?, source_document_id = ?, source_pages = ?, source_excerpt = ?, source_status = ?, updated_at = ? WHERE id = ?`)
      .run(body.title ?? n.title, body.body ?? n.body, src ? src.source_document_id : n.source_document_id, src ? src.source_pages : n.source_pages,
        src ? src.source_excerpt : n.source_excerpt, src ? src.source_status : n.source_status, now(), n.id);
    return itemOut(db.prepare('SELECT * FROM notes WHERE id = ?').get(n.id));
  });
  app.delete('/api/notes/:id', async (req) => {
    const u = auth(req);
    const n = owned('notes', (req.params as any).id, u.id);
    db.prepare('DELETE FROM notes WHERE id = ?').run(n.id);
    return { ok: true };
  });

  // ------------------------------------------------------------------ items
  function insertItem(userId: string, chapterId: string, it: z.infer<typeof ItemIn>, origin: string) {
    checkItemShape(it);
    const id = randomUUID();
    const src = resolveSource(db, userId, it.source, origin === 'manual' ? 'manual' : 'import');
    const t = now();
    db.prepare(`INSERT INTO items (id, user_id, chapter_id, type, prompt, answer, explanation, choices, skill, origin,
      source_document_id, source_pages, source_excerpt, source_status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`)
      .run(id, userId, chapterId, it.type, it.prompt, it.type === 'mcq' ? '' : it.answer, it.explanation,
        it.type === 'mcq' ? JSON.stringify(it.choices) : null, it.skill ?? null, origin,
        src.source_document_id, src.source_pages, src.source_excerpt, src.source_status, t, t);
    const s = emptyState(id, userId, t);
    db.prepare(`INSERT INTO review_state (item_id, user_id, due, stability, difficulty, elapsed_days, scheduled_days, learning_steps, reps, lapses, state, last_review, last_rating, version)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(s.item_id, s.user_id, s.due, s.stability, s.difficulty, s.elapsed_days, s.scheduled_days,
      s.learning_steps, s.reps, s.lapses, s.state, s.last_review, s.last_rating, s.version);
    return id;
  }

  app.post('/api/chapters/:id/items', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const it = parse(ItemIn, req.body);
    const id = tx(db, () => insertItem(u.id, c.id, it, 'manual'));
    return itemOut(db.prepare('SELECT * FROM items WHERE id = ?').get(id));
  });
  app.patch('/api/items/:id', async (req) => {
    const u = auth(req);
    const cur = itemOut(owned('items', (req.params as any).id, u.id));
    const body = parse(ItemPatch, req.body);
    const defined = Object.fromEntries(Object.entries(body).filter(([, v]) => v !== undefined));
    const merged = { ...cur, ...defined, type: cur.type };
    checkItemShape(merged);
    const src = body.source !== undefined ? resolveSource(db, u.id, body.source, cur.origin === 'manual' ? 'manual' : 'import') : null;
    db.prepare(`UPDATE items SET prompt = ?, answer = ?, explanation = ?, choices = ?, skill = ?, suspended = ?,
      source_document_id = ?, source_pages = ?, source_excerpt = ?, source_status = ?, updated_at = ? WHERE id = ?`)
      .run(merged.prompt, merged.type === 'mcq' ? '' : merged.answer, merged.explanation,
        merged.type === 'mcq' ? JSON.stringify(merged.choices) : null, merged.skill ?? null, merged.suspended ? 1 : 0,
        src ? src.source_document_id : cur.source_document_id, src ? src.source_pages : (cur.source_pages ? JSON.stringify(cur.source_pages) : null),
        src ? src.source_excerpt : cur.source_excerpt, src ? src.source_status : cur.source_status, now(), cur.id);
    return itemOut(db.prepare('SELECT * FROM items WHERE id = ?').get(cur.id));
  });
  // The answer is only fetched once the learner chose to reveal it.
  app.get('/api/items/:id/answer', async (req) => {
    const u = auth(req);
    const it = itemOut(owned('items', (req.params as any).id, u.id));
    const { answer, explanation, source_document_id, source_pages, source_excerpt, source_status } = it;
    return { item: { answer, explanation, source_document_id, source_pages, source_excerpt, source_status } };
  });
  app.delete('/api/items/:id', async (req) => {
    const u = auth(req);
    const it = owned('items', (req.params as any).id, u.id);
    db.prepare('DELETE FROM items WHERE id = ?').run(it.id);
    return { ok: true };
  });

  // ------------------------------------------------------------------ imports
  function docForImport(userId: string, chapterId: string, documentId?: string | null, title?: string) {
    if (documentId) return owned('documents', documentId, userId).id as string;
    if (title) {
      const d = db.prepare('SELECT id FROM documents WHERE chapter_id = ? AND user_id = ? AND title = ?').get(chapterId, userId, title) as any;
      return d?.id ?? null;
    }
    return null;
  }

  /**
   * Stores validated structured content (import JSON, in-app AI, assistant connector) in one chapter.
   * Every source goes through resolveSource: "verified" only when the excerpt is found in the course.
   * Must be called inside a transaction.
   */
  function saveContent(userId: string, chapterId: string, data: ImportV1, mapNodes: MindNode[] | null, docId: string | null, origin: string) {
    const src = (s?: { pages?: number[]; excerpt?: string }) => (s ? { document_id: docId, pages: s.pages ?? null, excerpt: s.excerpt ?? null } : null);
    let verified = 0;
    const out = { notes: [] as string[], items: [] as Array<{ id: string; type: string; source_status: string }>, mindmap: null as string | null };
    const t = now();
    for (const n of data.notes) {
      const s = resolveSource(db, userId, src(n.source), origin === 'manual' ? 'manual' : 'import');
      if (s.source_status === 'verified') verified++;
      const id = randomUUID();
      db.prepare(`INSERT INTO notes (id, user_id, chapter_id, title, body, origin, source_document_id, source_pages, source_excerpt, source_status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, userId, chapterId, n.title, n.body, origin, s.source_document_id, s.source_pages, s.source_excerpt, s.source_status, t, t);
      out.notes.push(id);
    }
    const all: Array<z.infer<typeof ItemIn>> = [
      ...data.flashcards.map((f) => ({ type: 'flashcard' as const, prompt: f.question, answer: f.answer, explanation: f.explanation ?? '', skill: f.skill, source: src(f.source) })),
      ...data.mcq.map((q) => ({ type: 'mcq' as const, prompt: q.question, answer: '', explanation: q.explanation ?? '',
        choices: q.choices.map((ch) => ({ text: ch.text, correct: ch.correct, why: ch.why ?? '' })), skill: q.skill, source: src(q.source) })),
      ...data.open.map((o) => ({ type: 'open' as const, prompt: o.question, answer: o.answer, explanation: o.explanation ?? '', skill: o.skill, source: src(o.source) })),
    ];
    for (const it of all) {
      const id = insertItem(userId, chapterId, it, origin);
      const st = (db.prepare('SELECT source_status FROM items WHERE id = ?').get(id) as any).source_status as string;
      if (st === 'verified') verified++;
      out.items.push({ id, type: it.type, source_status: st });
    }
    if (data.mindmap && mapNodes) {
      out.mindmap = randomUUID();
      db.prepare(`INSERT INTO mindmaps (id, user_id, chapter_id, title, data, origin, source_status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)`)
        .run(out.mindmap, userId, chapterId, data.mindmap.title, JSON.stringify({ nodes: mapNodes }), origin, 'to_verify', t, t);
    }
    for (const g of data.glossary) {
      db.prepare('INSERT INTO glossary (id, user_id, term, arabic, definition, created_at) VALUES (?,?,?,?,?,?)')
        .run(randomUUID(), userId, g.term, g.arabic ?? '', g.definition ?? '', t);
    }
    return { verified, ...out };
  }

  app.post('/api/chapters/:id/import/json', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const body = parse(z.object({ data: z.unknown(), document_id: z.string().nullable().optional(), dry_run: z.boolean().default(true) }), req.body);
    const r = ImportV1.safeParse(body.data);
    if (!r.success) {
      return { ok: false, errors: r.error.issues.slice(0, 30).map((i) => `${i.path.join('.') || '—'} : ${i.message}`) };
    }
    const data = r.data;
    const mapNodes: MindNode[] | null = data.mindmap
      ? data.mindmap.nodes.map((n) => ({ id: n.id, label: n.label, parentId: n.parent ?? null, note: n.note ?? '', itemIds: [] }))
      : null;
    if (mapNodes) {
      const err = treeError(mapNodes);
      if (err) return { ok: false, errors: [`mindmap : ${err}`] };
    }
    const docId = docForImport(u.id, c.id, body.document_id, data.document_title);
    const summary = {
      notes: data.notes.length, flashcards: data.flashcards.length, mcq: data.mcq.length, open: data.open.length,
      mindmap: mapNodes ? mapNodes.length : 0, glossary: data.glossary.length,
      linked_document: docId,
      without_source: [...data.notes, ...data.flashcards, ...data.mcq, ...data.open].filter((x) => !x.source || (!x.source.excerpt && !x.source.pages)).length,
    };
    if (body.dry_run) return { ok: true, dry_run: true, summary };
    const { verified } = tx(db, () => saveContent(u.id, c.id, data, mapNodes, docId, 'import'));
    return { ok: true, dry_run: false, summary: { ...summary, verified_sources: verified } };
  });

  app.post('/api/chapters/:id/import/csv', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const body = parse(z.object({
      rows: z.array(z.object({
        question: z.string().max(2000), answer: z.string().max(5000), explanation: z.string().max(5000).optional(),
        pages: z.string().max(200).optional(), excerpt: z.string().max(2000).optional(),
      })).max(5000),
      document_id: z.string().nullable().optional(),
      dry_run: z.boolean().default(true),
    }), req.body);
    const docId = docForImport(u.id, c.id, body.document_id);
    const errors: string[] = [];
    const valid: Array<z.infer<typeof ItemIn>> = [];
    body.rows.forEach((r, i) => {
      const q = r.question.trim(), a = r.answer.trim();
      if (!q && !a) return; // blank line
      if (!q || !a) { errors.push(`ligne ${i + 1} : question ou réponse vide`); return; }
      const pages = (r.pages ?? '').split(/[^0-9]+/).filter(Boolean).map(Number).filter((n) => n >= 1 && n <= 10000);
      const hasSrc = pages.length > 0 || !!r.excerpt?.trim();
      valid.push({ type: 'flashcard', prompt: q, answer: a, explanation: r.explanation?.trim() ?? '', skill: null,
        source: hasSrc || docId ? { document_id: docId, pages, excerpt: r.excerpt?.trim() || null } : null });
    });
    if (body.dry_run) return { ok: errors.length === 0, dry_run: true, count: valid.length, errors: errors.slice(0, 50) };
    if (errors.length) return { ok: false, dry_run: false, count: 0, errors: errors.slice(0, 50) };
    tx(db, () => valid.forEach((it) => insertItem(u.id, c.id, it, 'import')));
    return { ok: true, dry_run: false, count: valid.length, errors: [] };
  });

  // ------------------------------------------------------------------ review
  function loadState(itemId: string, userId: string): StateRow {
    return db.prepare('SELECT * FROM review_state WHERE item_id = ? AND user_id = ?').get(itemId, userId) as unknown as StateRow;
  }

  function dueQueue(u: User, chapterId: string | null) {
    const t = now();
    const { start, end } = dayBounds(u.timezone, t);
    const s = userSettings(u);
    const scope = chapterId ? 'AND i.chapter_id = ?' : '';
    const args = chapterId ? [chapterId] : [];
    // Review cards are due by local day; learning/relearning steps (minutes) only once their time has come.
    const due = db.prepare(`SELECT i.id FROM items i JOIN review_state r ON r.item_id = i.id
      WHERE i.user_id = ? AND i.suspended = 0 AND ((r.state = 2 AND r.due < ?) OR (r.state IN (1,3) AND r.due <= ?)) ${scope}
      ORDER BY r.due`).all(u.id, end, t, ...args) as any[];
    const laterToday = (db.prepare(`SELECT COUNT(*) AS n FROM items i JOIN review_state r ON r.item_id = i.id
      WHERE i.user_id = ? AND i.suspended = 0 AND r.state IN (1,3) AND r.due > ? AND r.due < ? ${scope}`).get(u.id, t, end, ...args) as any).n as number;
    const introducedToday = (db.prepare(`SELECT COUNT(DISTINCT item_id) AS n FROM review_logs WHERE user_id = ? AND state_before = 0 AND reviewed_at >= ?`)
      .get(u.id, start) as any).n as number;
    const newQuota = Math.max(0, s.new_per_day - introducedToday);
    const fresh = db.prepare(`SELECT i.id FROM items i JOIN review_state r ON r.item_id = i.id
      WHERE i.user_id = ? AND i.suspended = 0 AND r.state = 0 ${scope} ORDER BY i.created_at LIMIT ?`).all(u.id, ...args, newQuota) as any[];
    return { due: due.map((r) => r.id as string), fresh: fresh.map((r) => r.id as string), laterToday };
  }

  function activeSession(userId: string) {
    return db.prepare('SELECT * FROM study_sessions WHERE user_id = ? AND finished_at IS NULL ORDER BY created_at DESC LIMIT 1').get(userId) as any;
  }

  app.get('/api/review/today', async (req) => {
    const u = auth(req);
    const q = dueQueue(u, null);
    const s = activeSession(u.id);
    return {
      due: q.due.length, new: q.fresh.length, later_today: q.laterToday, date: dayBounds(u.timezone, now()).date, timezone: u.timezone,
      session: s ? { id: s.id, position: s.position, total: JSON.parse(s.item_ids).length } : null,
    };
  });

  app.post('/api/review/sessions', async (req) => {
    const u = auth(req);
    const body = parse(z.object({ chapter_id: z.string().nullable().optional(), resume: z.boolean().default(true) }), req.body ?? {});
    if (body.chapter_id) owned('chapters', body.chapter_id, u.id);
    const existing = activeSession(u.id);
    if (existing && body.resume && !body.chapter_id) return { id: existing.id, resumed: true };
    const q = dueQueue(u, body.chapter_id ?? null);
    const ids = [...q.due, ...q.fresh].slice(0, SESSION_MAX_ITEMS);
    if (!ids.length) return { id: null, resumed: false };
    const id = randomUUID();
    tx(db, () => {
      db.prepare('UPDATE study_sessions SET finished_at = ? WHERE user_id = ? AND finished_at IS NULL').run(now(), u.id);
      db.prepare('INSERT INTO study_sessions (id, user_id, item_ids, position, created_at, updated_at) VALUES (?,?,?,?,?,?)')
        .run(id, u.id, JSON.stringify(ids), 0, now(), now());
    });
    return { id, resumed: false };
  });

  function presentItem(itemId: string, userId: string) {
    const it = itemOut(db.prepare('SELECT * FROM items WHERE id = ? AND user_id = ?').get(itemId, userId));
    const st = loadState(itemId, userId);
    const base = {
      id: it.id, type: it.type, prompt: it.prompt, skill: it.skill, chapter_id: it.chapter_id,
      source_status: it.source_status, version: st.version, state: st.state,
    };
    if (it.type === 'mcq') {
      // Positions are shuffled at each presentation; correctness is only revealed after answering.
      const order: number[] = shuffle((it.choices as unknown[]).map((_, i) => i));
      return { ...base, choices: order.map((i) => ({ index: i, text: it.choices[i].text as string })) };
    }
    return base;
  }

  app.get('/api/review/sessions/:id', async (req) => {
    const u = auth(req);
    const s = owned('study_sessions', (req.params as any).id, u.id);
    let ids: string[] = JSON.parse(s.item_ids);
    let pos = s.position;
    // Skip items deleted or suspended since the session started.
    while (pos < ids.length) {
      const ok = db.prepare('SELECT 1 FROM items WHERE id = ? AND user_id = ? AND suspended = 0').get(ids[pos], u.id);
      if (ok) break;
      pos++;
    }
    if (pos !== s.position) db.prepare('UPDATE study_sessions SET position = ?, updated_at = ? WHERE id = ?').run(pos, now(), s.id);
    if (pos >= ids.length) {
      if (!s.finished_at) db.prepare('UPDATE study_sessions SET finished_at = ? WHERE id = ?').run(now(), s.id);
      return { session: { id: s.id, position: pos, total: ids.length, finished: true }, item: null };
    }
    return { session: { id: s.id, position: pos, total: ids.length, finished: false }, item: presentItem(ids[pos], u.id) };
  });

  const AnswerIn = z.object({
    session_id: z.string().nullable().optional(),
    item_id: z.string(),
    review_id: z.string().uuid(),
    expected_version: z.number().int().min(0),
    rating: z.number().int().min(1).max(4).optional(),
    choice_index: z.number().int().min(0).max(7).optional(),
    hesitated: z.boolean().optional(),
    response: z.string().max(5000).optional(),
  });

  function answerFeedback(it: any, logRow: any, st: StateRow) {
    return {
      review_id: logRow.id, rating: logRow.rating, correct: logRow.correct == null ? null : !!logRow.correct,
      answer: it.answer, explanation: it.explanation,
      choices: it.type === 'mcq' ? it.choices.map((c: any, i: number) => ({ index: i, text: c.text, correct: c.correct, why: c.why })) : null,
      source: { document_id: it.source_document_id, pages: it.source_pages, excerpt: it.source_excerpt, status: it.source_status },
      next_due: st.due, version: st.version,
    };
  }

  app.post('/api/review/answer', async (req) => {
    const u = auth(req);
    const body = parse(AnswerIn, req.body);
    const it = itemOut(owned('items', body.item_id, u.id));
    return tx(db, () => {
      // Idempotency: the same review_id (double click, network retry) returns the stored outcome.
      const prior = db.prepare('SELECT * FROM review_logs WHERE id = ?').get(body.review_id) as any;
      if (prior) {
        if (prior.user_id !== u.id || prior.item_id !== it.id) throw new UserError('Évaluation refusée.', 409);
        return { ...answerFeedback(it, prior, loadState(it.id, u.id)), duplicate: true, session: sessionInfo(body.session_id, u.id) };
      }
      const st = loadState(it.id, u.id);
      if (st.version !== body.expected_version) throw new UserError('Cette carte vient déjà d’être évaluée.', 409);
      let grade: Grade;
      let correct: number | null = null;
      if (it.type === 'mcq') {
        if (body.choice_index == null || body.choice_index >= it.choices.length) throw new UserError('Choisissez une proposition.');
        correct = it.choices[body.choice_index].correct ? 1 : 0;
        // Explicit QCM → FSRS mapping (docs/SPEC.md): wrong = Again, right with hesitation = Hard, right = Good.
        grade = (correct ? (body.hesitated ? Rating.Hard : Rating.Good) : Rating.Again) as Grade;
      } else {
        if (!body.rating) throw new UserError('Indiquez comment vous vous êtes souvenu.');
        grade = body.rating as Grade;
      }
      const t = now();
      const next = applyRating(st, grade, t, userSettings(u));
      db.prepare(`UPDATE review_state SET due = ?, stability = ?, difficulty = ?, elapsed_days = ?, scheduled_days = ?, learning_steps = ?,
        reps = ?, lapses = ?, state = ?, last_review = ?, last_rating = ?, version = ? WHERE item_id = ? AND version = ?`)
        .run(next.due, next.stability, next.difficulty, next.elapsed_days, next.scheduled_days, next.learning_steps, next.reps,
          next.lapses, next.state, next.last_review, next.last_rating, next.version, it.id, st.version);
      db.prepare('INSERT INTO review_logs (id, user_id, item_id, rating, correct, response, state_before, due_after, reviewed_at) VALUES (?,?,?,?,?,?,?,?,?)')
        .run(body.review_id, u.id, it.id, grade, correct, body.response ?? null, st.state, next.due, t);
      // Advance the session only if this item is the one expected at the current position.
      if (body.session_id) {
        const s = owned('study_sessions', body.session_id, u.id);
        const ids: string[] = JSON.parse(s.item_ids);
        if (!s.finished_at && ids[s.position] === it.id) {
          const { end } = dayBounds(u.timezone, t);
          const occurrences = ids.filter((x) => x === it.id).length;
          if (grade === Rating.Again && next.due < end && occurrences <= MAX_REQUEUES && ids.length < SESSION_MAX_ITEMS * 2) ids.push(it.id);
          db.prepare('UPDATE study_sessions SET item_ids = ?, position = ?, updated_at = ? WHERE id = ?').run(JSON.stringify(ids), s.position + 1, t, s.id);
        }
      }
      const logRow = db.prepare('SELECT * FROM review_logs WHERE id = ?').get(body.review_id);
      return { ...answerFeedback(it, logRow, next), duplicate: false, session: sessionInfo(body.session_id, u.id) };
    });
  });

  function sessionInfo(sessionId: string | null | undefined, userId: string) {
    if (!sessionId) return null;
    const s = db.prepare('SELECT * FROM study_sessions WHERE id = ? AND user_id = ?').get(sessionId, userId) as any;
    return s ? { id: s.id, position: s.position, total: JSON.parse(s.item_ids).length } : null;
  }

  app.post('/api/review/sessions/:id/finish', async (req) => {
    const u = auth(req);
    const s = owned('study_sessions', (req.params as any).id, u.id);
    db.prepare('UPDATE study_sessions SET finished_at = COALESCE(finished_at, ?) WHERE id = ?').run(now(), s.id);
    return { ok: true };
  });

  // ------------------------------------------------------------------ progress
  app.get('/api/progress', async (req) => {
    const u = auth(req);
    const { start } = dayBounds(u.timezone, now());
    const one = (sql: string, ...a: any[]) => (db.prepare(sql).get(u.id, ...a) as any).n as number;
    return {
      activities: {
        reviews_today: one('SELECT COUNT(*) AS n FROM review_logs WHERE user_id = ? AND reviewed_at >= ?', start),
        reviews_total: one('SELECT COUNT(*) AS n FROM review_logs WHERE user_id = ?'),
      },
      items: {
        total: one('SELECT COUNT(*) AS n FROM items WHERE user_id = ?'),
        new: one('SELECT COUNT(*) AS n FROM review_state WHERE user_id = ? AND state = 0'),
        learning: one('SELECT COUNT(*) AS n FROM review_state WHERE user_id = ? AND state IN (1,3)'),
        // Mastery = free recall (flashcard/open), in review state, stability ≥ 21 days, last answer ≥ Good.
        mastered: one(`SELECT COUNT(*) AS n FROM review_state r JOIN items i ON i.id = r.item_id WHERE r.user_id = ? AND i.type != 'mcq'
          AND r.state = 2 AND r.stability >= 21 AND r.last_rating >= 3`),
        // QCM success only proves recognition.
        recognized: one(`SELECT COUNT(*) AS n FROM review_state r JOIN items i ON i.id = r.item_id WHERE r.user_id = ? AND i.type = 'mcq'
          AND r.state = 2 AND r.last_rating >= 3`),
        to_rework: one('SELECT COUNT(*) AS n FROM review_state WHERE user_id = ? AND last_rating = 1'),
      },
      difficult: db.prepare(`SELECT i.id, i.prompt, i.type, i.chapter_id, r.lapses FROM items i JOIN review_state r ON r.item_id = i.id
        WHERE i.user_id = ? AND (r.last_rating = 1 OR r.lapses >= 2) ORDER BY r.lapses DESC, r.last_review DESC LIMIT 10`).all(u.id),
    };
  });

  // ------------------------------------------------------------------ mind maps
  const NodeIn = z.object({
    id: z.string().min(1).max(100), label: z.string().trim().min(1).max(500), parentId: z.string().max(100).nullable(),
    note: z.string().max(5000).default(''), itemIds: z.array(z.string()).max(50).default([]),
  });
  function cleanNodes(userId: string, nodes: z.infer<typeof NodeIn>[]): MindNode[] {
    const err = treeError(nodes);
    if (err) throw new UserError(`Carte invalide : ${err}.`);
    const ownedItem = db.prepare('SELECT 1 FROM items WHERE id = ? AND user_id = ?');
    return nodes.map((n) => ({ ...n, itemIds: [...new Set(n.itemIds)].filter((id) => Id.safeParse(id).success && ownedItem.get(id, userId)) }));
  }

  app.post('/api/chapters/:id/mindmaps', async (req) => {
    const u = auth(req);
    const c = owned('chapters', (req.params as any).id, u.id);
    const body = parse(z.object({ title: Name.optional() }), req.body ?? {});
    const id = randomUUID();
    const nodes: MindNode[] = [{ id: 'root', label: c.name, parentId: null, note: '', itemIds: [] }];
    db.prepare(`INSERT INTO mindmaps (id, user_id, chapter_id, title, data, origin, source_status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)`)
      .run(id, u.id, c.id, body.title ?? c.name, JSON.stringify({ nodes }), 'manual', 'personal', now(), now());
    return { id };
  });
  app.get('/api/mindmaps/:id', async (req) => {
    const u = auth(req);
    const m = owned('mindmaps', (req.params as any).id, u.id);
    const data = JSON.parse(m.data);
    const itemIds = [...new Set((data.nodes as MindNode[]).flatMap((n) => n.itemIds))];
    const items = itemIds.length
      ? db.prepare(`SELECT id, type, prompt, answer FROM items WHERE user_id = ? AND id IN (${itemIds.map(() => '?').join(',')})`).all(u.id, ...itemIds)
      : [];
    return { mindmap: { id: m.id, chapter_id: m.chapter_id, title: m.title, origin: m.origin, source_status: m.source_status, nodes: data.nodes, updated_at: m.updated_at }, items };
  });
  app.put('/api/mindmaps/:id', async (req) => {
    const u = auth(req);
    const m = owned('mindmaps', (req.params as any).id, u.id);
    const body = parse(z.object({ title: Name, nodes: z.array(NodeIn).min(1).max(1000) }), req.body);
    const nodes = cleanNodes(u.id, body.nodes);
    db.prepare('UPDATE mindmaps SET title = ?, data = ?, updated_at = ? WHERE id = ?').run(body.title, JSON.stringify({ nodes }), now(), m.id);
    return { ok: true, nodes };
  });
  app.delete('/api/mindmaps/:id', async (req) => {
    const u = auth(req);
    const m = owned('mindmaps', (req.params as any).id, u.id);
    db.prepare('DELETE FROM mindmaps WHERE id = ?').run(m.id);
    return { ok: true };
  });

  // ------------------------------------------------------------------ glossary
  const GlossIn = z.object({ term: Name, arabic: z.string().trim().max(300).default(''), definition: z.string().trim().max(3000).default('') });
  app.get('/api/glossary', async (req) => {
    const u = auth(req);
    return { entries: db.prepare('SELECT id, term, arabic, definition FROM glossary WHERE user_id = ? ORDER BY term COLLATE NOCASE').all(u.id) };
  });
  app.post('/api/glossary', async (req) => {
    const u = auth(req);
    const g = parse(GlossIn, req.body);
    const id = randomUUID();
    db.prepare('INSERT INTO glossary (id, user_id, term, arabic, definition, created_at) VALUES (?,?,?,?,?,?)').run(id, u.id, g.term, g.arabic, g.definition, now());
    return { id, ...g };
  });
  app.patch('/api/glossary/:id', async (req) => {
    const u = auth(req);
    const e = owned('glossary', (req.params as any).id, u.id);
    const g = parse(GlossIn, req.body);
    db.prepare('UPDATE glossary SET term = ?, arabic = ?, definition = ? WHERE id = ?').run(g.term, g.arabic, g.definition, e.id);
    return { id: e.id, ...g };
  });
  app.delete('/api/glossary/:id', async (req) => {
    const u = auth(req);
    const e = owned('glossary', (req.params as any).id, u.id);
    db.prepare('DELETE FROM glossary WHERE id = ?').run(e.id);
    return { ok: true };
  });

  // ------------------------------------------------------------------ export
  app.get('/api/export', async (req, reply) => {
    const u = auth(req);
    const all = (sql: string) => db.prepare(sql).all(u.id);
    const out = {
      format: 'muraja.export.v1',
      exported_at: new Date(now()).toISOString(),
      user: publicUser(u),
      subjects: all('SELECT * FROM subjects WHERE user_id = ?'),
      chapters: all('SELECT * FROM chapters WHERE user_id = ?'),
      documents: all('SELECT id, chapter_id, title, kind, mime, size, page_count, extraction_status, extraction_note, created_at FROM documents WHERE user_id = ?'),
      document_pages: all('SELECT document_id, page_number, text, readable FROM document_pages WHERE user_id = ?'),
      notes: all('SELECT * FROM notes WHERE user_id = ?'),
      items: all('SELECT * FROM items WHERE user_id = ?').map(itemOut),
      review_state: all('SELECT * FROM review_state WHERE user_id = ?'),
      review_logs: all('SELECT * FROM review_logs WHERE user_id = ?'),
      mindmaps: all('SELECT * FROM mindmaps WHERE user_id = ?').map((m: any) => ({ ...m, data: JSON.parse(m.data) })),
      glossary: all('SELECT * FROM glossary WHERE user_id = ?'),
      note: 'Les fichiers PDF et images se téléchargent séparément depuis chaque document.',
    };
    reply.header('Content-Disposition', `attachment; filename="muraja-export-${dayBounds(u.timezone, now()).date}.json"`);
    return out;
  });

  // ------------------------------------------------------------------ AI: personal key, OAuth, MCP connector
  const ctx = { db, env, now, auth, currentUser, owned, saveContent, docForImport, userSettings, dayBounds, publicUrl: opts.publicUrl, callJson: opts.callJson, secret: opts.secretKey ?? env.MURAJA_SECRET_KEY };
  registerAi(app, ctx);
  registerOAuth(app, ctx);
  await registerMcp(app, ctx);

  // ------------------------------------------------------------------ static web app
  if (opts.staticDir && existsSync(opts.staticDir)) {
    await app.register(fastifyStatic, { root: opts.staticDir, wildcard: false });
    app.setNotFoundHandler((req, reply) => {
      if (req.url.startsWith('/api/')) return reply.code(404).send({ error: 'Introuvable.' });
      return reply.sendFile('index.html');
    });
  }

  app.addHook('onClose', async () => db.close());
  return { app, db };
}

export function resetDataDir(dir: string) {
  rmSync(dir, { recursive: true, force: true });
}

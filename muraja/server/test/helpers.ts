import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { PDFDocument, StandardFonts } from 'pdf-lib';
import { buildApp, type AppOptions } from '../app.ts';

export function tmpDir() {
  return mkdtempSync(path.join(tmpdir(), 'muraja-test-'));
}

export async function makeApp(o: Partial<AppOptions> = {}) {
  const dataDir = o.dataDir ?? tmpDir();
  const { app, db } = await buildApp({ dataDir, ...o });
  return { app, db, dataDir };
}

/** Minimal client with a cookie jar over fastify.inject. */
export class Client {
  cookie = '';
  app: any;
  constructor(app: any) { this.app = app; }
  async req(method: string, url: string, body?: unknown, extra: Record<string, string> = {}) {
    const headers: Record<string, string> = { 'x-muraja': '1', ...extra };
    if (this.cookie) headers.cookie = this.cookie;
    const payload = body === undefined ? undefined : typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body);
    if (body !== undefined && !Buffer.isBuffer(body) && !extra['content-type']) headers['content-type'] = 'application/json';
    const res = await this.app.inject({ method, url, headers, payload });
    const set = res.headers['set-cookie'];
    if (set) {
      const first = (Array.isArray(set) ? set[0] : set).split(';')[0];
      this.cookie = first;
    }
    let json: any = null;
    try { json = res.json(); } catch { /* not json */ }
    return { status: res.statusCode, json, body: res.body, headers: res.headers };
  }
  get(u: string) { return this.req('GET', u); }
  post(u: string, b: unknown = {}) { return this.req('POST', u, b); }
  put(u: string, b: unknown) { return this.req('PUT', u, b); }
  patch(u: string, b: unknown) { return this.req('PATCH', u, b); }
  del(u: string) { return this.req('DELETE', u); }
  async upload(url: string, filename: string, data: Buffer, mime: string) {
    const boundary = '----muraja' + Math.random().toString(16).slice(2);
    const body = Buffer.concat([
      Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${filename}"\r\nContent-Type: ${mime}\r\n\r\n`),
      data, Buffer.from(`\r\n--${boundary}--\r\n`),
    ]);
    return this.req('POST', url, body, { 'content-type': `multipart/form-data; boundary=${boundary}` });
  }
}

export async function signup(app: any, email: string, extra: Record<string, unknown> = {}) {
  const c = new Client(app);
  const r = await c.post('/api/auth/register', { email, name: email.split('@')[0], password: 'motdepasse-solide', ...extra });
  if (r.status !== 200) throw new Error(`signup failed ${r.status} ${r.body}`);
  return c;
}

export async function chapter(c: Client, subject = 'Fiqh', name = 'La purification') {
  const s = await c.post('/api/subjects', { name: subject });
  const ch = await c.post('/api/chapters', { subject_id: s.json.id, name });
  return ch.json.id as string;
}

/** Build a PDF whose pages contain the given texts; an empty string produces a page without text (like a scan). */
export async function makePdf(pages: string[]): Promise<Buffer> {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  for (const t of pages) {
    const p = doc.addPage();
    t.split('\n').forEach((line, i) => p.drawText(line, { x: 50, y: 740 - i * 18, font, size: 12 }));
  }
  return Buffer.from(await doc.save());
}

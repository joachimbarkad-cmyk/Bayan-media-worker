/**
 * OAuth 2.1 authorization server so that a learner can connect THEIR Claude or ChatGPT account
 * to Murāja'a (custom connector / MCP app). Implements what Claude's connector client requires:
 * RFC 9728 protected resource metadata, RFC 8414 server metadata, RFC 7591 dynamic client
 * registration, PKCE S256 only, public clients, refresh-token rotation with reuse detection,
 * form-urlencoded token endpoint, port-agnostic loopback redirects.
 */
import type { FastifyInstance, FastifyRequest } from 'fastify';
import { createHash, randomBytes, randomUUID } from 'node:crypto';
import { z } from 'zod';
import { tx } from './db.ts';
import { hashToken, AttemptLimiter } from './auth.ts';
import { UserError } from './pdf.ts';
import type { Ctx } from './ctx.ts';

export const SCOPE = 'muraja';
const ACCESS_TTL = 3600_000;
const REFRESH_TTL = 90 * 86400_000;
const CODE_TTL = 5 * 60_000;

export function baseUrl(ctx: Ctx, req: FastifyRequest): string {
  const configured = ctx.publicUrl ?? ctx.env.MURAJA_PUBLIC_URL;
  return (configured ?? `${req.protocol}://${req.host}`).replace(/\/+$/, '');
}

export function resourceMetadataUrl(ctx: Ctx, req: FastifyRequest) {
  return `${baseUrl(ctx, req)}/.well-known/oauth-protected-resource/mcp`;
}

function isLoopback(u: URL) {
  return u.protocol === 'http:' && (u.hostname === 'localhost' || u.hostname === '127.0.0.1' || u.hostname === '[::1]');
}

function validRedirect(raw: string): boolean {
  try {
    const u = new URL(raw);
    if (u.hash) return false;
    return u.protocol === 'https:' || isLoopback(u);
  } catch {
    return false;
  }
}

/** Exact match, except loopback redirects which match whatever the port (RFC 8252 §7.3). */
export function redirectMatches(registered: string[], candidate: string): boolean {
  if (registered.includes(candidate)) return true;
  let c: URL;
  try { c = new URL(candidate); } catch { return false; }
  if (!isLoopback(c)) return false;
  return registered.some((r) => {
    try {
      const u = new URL(r);
      return isLoopback(u) && u.hostname === c.hostname && u.pathname === c.pathname && u.search === c.search;
    } catch { return false; }
  });
}

const b64url = (buf: Buffer) => buf.toString('base64url');
const newSecret = () => b64url(randomBytes(32));

export interface AccessInfo { userId: string; clientId: string; clientName: string; scope: string }

export function registerOAuth(app: FastifyInstance, ctx: Ctx) {
  const { db, now, auth } = ctx;
  const regLimiter = new AttemptLimiter(30, 3600_000);

  app.addContentTypeParser('application/x-www-form-urlencoded', { parseAs: 'string' }, (_req, body, done) => {
    done(null, Object.fromEntries(new URLSearchParams(body as string)));
  });

  // ---------------------------------------------------------------- discovery
  const prm = async (req: FastifyRequest) => ({
    resource: `${baseUrl(ctx, req)}/mcp`,
    authorization_servers: [baseUrl(ctx, req)],
    scopes_supported: [SCOPE],
    bearer_methods_supported: ['header'],
    resource_name: "Murāja'a",
  });
  app.get('/.well-known/oauth-protected-resource', prm);
  app.get('/.well-known/oauth-protected-resource/mcp', prm);
  const asMeta = async (req: FastifyRequest) => {
    const b = baseUrl(ctx, req);
    return {
      issuer: b,
      authorization_endpoint: `${b}/oauth/authorize`,
      token_endpoint: `${b}/oauth/token`,
      registration_endpoint: `${b}/oauth/register`,
      revocation_endpoint: `${b}/oauth/revoke`,
      response_types_supported: ['code'],
      grant_types_supported: ['authorization_code', 'refresh_token'],
      code_challenge_methods_supported: ['S256'],
      token_endpoint_auth_methods_supported: ['none'],
      revocation_endpoint_auth_methods_supported: ['none'],
      scopes_supported: [SCOPE, 'offline_access'],
    };
  };
  app.get('/.well-known/oauth-authorization-server', asMeta);
  app.get('/.well-known/oauth-authorization-server/*', asMeta);

  // ---------------------------------------------------------------- dynamic client registration
  app.post('/oauth/register', async (req, reply) => {
    if (regLimiter.blocked(req.ip)) return reply.code(429).send({ error: 'slow_down', error_description: 'Trop d’enregistrements.' });
    regLimiter.record(req.ip);
    const r = z.object({
      client_name: z.string().trim().max(100).optional(),
      redirect_uris: z.array(z.string().max(500)).min(1).max(10),
      token_endpoint_auth_method: z.string().optional(),
      grant_types: z.array(z.string()).optional(),
      response_types: z.array(z.string()).optional(),
    }).passthrough().safeParse(req.body);
    if (!r.success) return reply.code(400).send({ error: 'invalid_client_metadata', error_description: 'Métadonnées invalides.' });
    if (!r.data.redirect_uris.every(validRedirect)) {
      return reply.code(400).send({ error: 'invalid_redirect_uri', error_description: 'Adresse de retour HTTPS (ou boucle locale) exigée.' });
    }
    if (r.data.token_endpoint_auth_method && r.data.token_endpoint_auth_method !== 'none') {
      return reply.code(400).send({ error: 'invalid_client_metadata', error_description: 'Seuls les clients publics (PKCE) sont acceptés.' });
    }
    const clientId = `mc_${newSecret()}`;
    const name = r.data.client_name || new URL(r.data.redirect_uris[0]).hostname;
    db.prepare('INSERT INTO oauth_clients (client_id, client_name, redirect_uris, created_at) VALUES (?,?,?,?)')
      .run(clientId, name, JSON.stringify(r.data.redirect_uris), now());
    return reply.code(201).send({
      client_id: clientId, client_name: name, redirect_uris: r.data.redirect_uris, client_id_issued_at: Math.floor(now() / 1000),
      token_endpoint_auth_method: 'none', grant_types: ['authorization_code', 'refresh_token'], response_types: ['code'],
    });
  });

  // ---------------------------------------------------------------- authorization (consent in the web app)
  const AuthParams = z.object({
    response_type: z.literal('code'),
    client_id: z.string().max(200),
    redirect_uri: z.string().max(500),
    code_challenge: z.string().min(43).max(128),
    code_challenge_method: z.literal('S256'),
    state: z.string().max(1000).optional(),
    scope: z.string().max(200).optional(),
    resource: z.string().max(500).optional(),
  });

  function checkAuthRequest(q: unknown) {
    const p = AuthParams.safeParse(q);
    if (!p.success) throw new UserError('Demande de connexion invalide (paramètres OAuth manquants ou PKCE S256 absent).');
    const client = db.prepare('SELECT * FROM oauth_clients WHERE client_id = ?').get(p.data.client_id) as any;
    if (!client) throw new UserError('Application inconnue : recommencez la connexion depuis Claude ou ChatGPT.');
    if (!redirectMatches(JSON.parse(client.redirect_uris), p.data.redirect_uri)) throw new UserError('Adresse de retour non enregistrée pour cette application.');
    return { params: p.data, client };
  }

  app.get('/oauth/authorize', async (req, reply) => {
    try {
      checkAuthRequest(req.query);
    } catch (e) {
      // Never redirect to an unverified redirect_uri.
      reply.type('text/html; charset=utf-8').code(400);
      return `<!doctype html><meta charset="utf-8"><title>Connexion refusée</title><p style="font:18px system-ui;padding:24px">${escapeHtml((e as Error).message)}</p>`;
    }
    const qs = new URLSearchParams(req.query as Record<string, string>).toString();
    return reply.redirect(`/#/connect?${qs}`);
  });

  app.get('/api/oauth/request', async (req) => {
    auth(req);
    const { params, client } = checkAuthRequest(req.query);
    return { client_name: client.client_name, redirect_host: new URL(params.redirect_uri).host, loopback: isLoopback(new URL(params.redirect_uri)) };
  });

  app.post('/api/oauth/approve', async (req) => {
    const u = auth(req);
    const body = z.object({ approve: z.boolean(), params: z.record(z.string(), z.string()) }).parse(req.body);
    const { params } = checkAuthRequest(body.params);
    const target = new URL(params.redirect_uri);
    if (params.state) target.searchParams.set('state', params.state);
    target.searchParams.set('iss', baseUrl(ctx, req));
    if (!body.approve) {
      target.searchParams.set('error', 'access_denied');
      return { redirect: target.toString() };
    }
    const code = newSecret();
    db.prepare('INSERT INTO oauth_codes (code_hash, client_id, user_id, redirect_uri, code_challenge, scope, expires_at) VALUES (?,?,?,?,?,?,?)')
      .run(hashToken(code), params.client_id, u.id, params.redirect_uri, params.code_challenge, SCOPE, now() + CODE_TTL);
    target.searchParams.set('code', code);
    return { redirect: target.toString() };
  });

  // ---------------------------------------------------------------- tokens
  function issue(clientId: string, userId: string, familyId: string) {
    const access = newSecret(), refresh = newSecret(), t = now();
    // Housekeeping: drop expired codes and tokens (a revoked family stays until expiry for reuse detection).
    db.prepare('DELETE FROM oauth_codes WHERE expires_at < ?').run(t);
    db.prepare('DELETE FROM oauth_tokens WHERE expires_at < ?').run(t);
    const ins = db.prepare('INSERT INTO oauth_tokens (token_hash, kind, family_id, client_id, user_id, scope, created_at, expires_at) VALUES (?,?,?,?,?,?,?,?)');
    ins.run(hashToken(access), 'access', familyId, clientId, userId, SCOPE, t, t + ACCESS_TTL);
    ins.run(hashToken(refresh), 'refresh', familyId, clientId, userId, SCOPE, t, t + REFRESH_TTL);
    return { access_token: access, token_type: 'Bearer', expires_in: ACCESS_TTL / 1000, refresh_token: refresh, scope: SCOPE };
  }

  app.post('/oauth/token', async (req, reply) => {
    reply.header('Cache-Control', 'no-store').header('Pragma', 'no-cache');
    const b = (req.body ?? {}) as Record<string, string>;
    const fail = (error: string, description: string, status = 400) => reply.code(status).send({ error, error_description: description });
    if (b.grant_type === 'authorization_code') {
      if (!b.code || !b.code_verifier || !b.client_id || !b.redirect_uri) return fail('invalid_request', 'Paramètres manquants.');
      return tx(db, () => {
        const row = db.prepare('SELECT * FROM oauth_codes WHERE code_hash = ?').get(hashToken(b.code)) as any;
        if (row) db.prepare('DELETE FROM oauth_codes WHERE code_hash = ?').run(row.code_hash); // single use
        if (!row || row.expires_at < now()) return fail('invalid_grant', 'Code invalide ou expiré.');
        if (row.client_id !== b.client_id || row.redirect_uri !== b.redirect_uri) return fail('invalid_grant', 'Code émis pour une autre application.');
        const challenge = b64url(createHash('sha256').update(b.code_verifier).digest());
        if (challenge !== row.code_challenge) return fail('invalid_grant', 'Vérification PKCE échouée.');
        return issue(row.client_id, row.user_id, randomUUID());
      });
    }
    if (b.grant_type === 'refresh_token') {
      if (!b.refresh_token) return fail('invalid_request', 'refresh_token manquant.');
      return tx(db, () => {
        const row = db.prepare("SELECT * FROM oauth_tokens WHERE token_hash = ? AND kind = 'refresh'").get(hashToken(b.refresh_token)) as any;
        if (!row) return fail('invalid_grant', 'Jeton inconnu.');
        if (b.client_id && b.client_id !== row.client_id) return fail('invalid_grant', 'Jeton émis pour une autre application.');
        if (row.revoked) {
          // Reuse of a rotated refresh token: assume theft, revoke the whole family.
          db.prepare('UPDATE oauth_tokens SET revoked = 1 WHERE family_id = ?').run(row.family_id);
          return fail('invalid_grant', 'Jeton déjà utilisé : connexion révoquée par sécurité.');
        }
        if (row.expires_at < now()) return fail('invalid_grant', 'Jeton expiré.');
        db.prepare('UPDATE oauth_tokens SET revoked = 1 WHERE family_id = ?').run(row.family_id);
        return issue(row.client_id, row.user_id, row.family_id);
      });
    }
    return fail('unsupported_grant_type', 'Type de demande non pris en charge.');
  });

  app.post('/oauth/revoke', async (req, reply) => {
    const token = ((req.body ?? {}) as Record<string, string>).token;
    if (token) {
      const row = db.prepare('SELECT family_id FROM oauth_tokens WHERE token_hash = ?').get(hashToken(token)) as any;
      if (row) db.prepare('UPDATE oauth_tokens SET revoked = 1 WHERE family_id = ?').run(row.family_id);
    }
    return reply.code(200).send({});
  });

  // ---------------------------------------------------------------- the learner's connected apps
  app.get('/api/connections', async (req) => {
    const u = auth(req);
    const rows = db.prepare(`SELECT c.client_id, c.client_name, MIN(t.created_at) AS since, MAX(t.created_at) AS last_used
      FROM oauth_tokens t JOIN oauth_clients c ON c.client_id = t.client_id
      WHERE t.user_id = ? AND t.revoked = 0 AND t.expires_at > ? GROUP BY c.client_id ORDER BY last_used DESC`).all(u.id, now());
    return { connections: rows, mcp_url: `${baseUrl(ctx, req)}/mcp` };
  });

  app.delete('/api/connections/:clientId', async (req) => {
    const u = auth(req);
    db.prepare('UPDATE oauth_tokens SET revoked = 1 WHERE user_id = ? AND client_id = ?').run(u.id, (req.params as any).clientId);
    return { ok: true };
  });
}

/** Resolves a bearer access token; null if missing, unknown, expired or revoked. */
export function verifyAccess(ctx: Ctx, token: string): AccessInfo | null {
  const row = ctx.db.prepare(`SELECT t.user_id, t.client_id, t.scope, c.client_name FROM oauth_tokens t JOIN oauth_clients c ON c.client_id = t.client_id
    WHERE t.token_hash = ? AND t.kind = 'access' AND t.revoked = 0 AND t.expires_at > ?`).get(hashToken(token), ctx.now()) as any;
  return row ? { userId: row.user_id, clientId: row.client_id, clientName: row.client_name, scope: row.scope } : null;
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
}

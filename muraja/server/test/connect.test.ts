import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash, randomBytes } from 'node:crypto';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { makeApp, signup, chapter, makePdf, Client } from './helpers.ts';

const LOREM = 'La purification est une condition de validite de la priere selon les quatre ecoles.';
const REDIRECT = 'https://claude.ai/api/mcp/auth_callback';

function form(o: Record<string, string>) { return new URLSearchParams(o).toString(); }

/** Runs DCR → authorize → consent (as the logged-in user) → token exchange. */
async function connect(app: any, user: Client, redirect = REDIRECT) {
  const reg = await app.inject({ method: 'POST', url: '/oauth/register', headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ client_name: 'Claude', redirect_uris: [redirect], token_endpoint_auth_method: 'none' }) });
  assert.equal(reg.statusCode, 201, reg.body);
  const clientId = reg.json().client_id;
  const verifier = randomBytes(32).toString('base64url');
  const params = { response_type: 'code', client_id: clientId, redirect_uri: redirect, state: 'xyz',
    code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256', scope: 'muraja' };
  const auth = await app.inject({ method: 'GET', url: `/oauth/authorize?${form(params)}` });
  assert.equal(auth.statusCode, 302);
  assert.match(auth.headers.location, /^\/#\/connect\?/);
  const info = await user.get(`/api/oauth/request?${form(params)}`);
  assert.equal(info.json.client_name, 'Claude');
  const ok = await user.post('/api/oauth/approve', { approve: true, params });
  const back = new URL(ok.json.redirect);
  assert.equal(back.searchParams.get('state'), 'xyz');
  const code = back.searchParams.get('code')!;
  const tok = await app.inject({ method: 'POST', url: '/oauth/token', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    payload: form({ grant_type: 'authorization_code', code, code_verifier: verifier, client_id: clientId, redirect_uri: redirect }) });
  assert.equal(tok.statusCode, 200, tok.body);
  return { clientId, verifier, code, params, ...tok.json() };
}

test('discovery metadata and 401 challenge follow the connector requirements', async () => {
  const { app } = await makeApp({ publicUrl: 'https://muraja.example.org' });
  const r = await app.inject({ method: 'POST', url: '/mcp', headers: { 'content-type': 'application/json' }, payload: '{}' });
  assert.equal(r.statusCode, 401);
  assert.match(String(r.headers['www-authenticate']), /resource_metadata="https:\/\/muraja\.example\.org\/\.well-known\/oauth-protected-resource\/mcp"/);
  const prm = (await app.inject({ method: 'GET', url: '/.well-known/oauth-protected-resource/mcp' })).json();
  assert.equal(prm.resource, 'https://muraja.example.org/mcp');
  assert.deepEqual(prm.authorization_servers, ['https://muraja.example.org']);
  const as = (await app.inject({ method: 'GET', url: '/.well-known/oauth-authorization-server' })).json();
  assert.deepEqual(as.code_challenge_methods_supported, ['S256']);
  assert.ok(as.registration_endpoint && as.token_endpoint_auth_methods_supported.includes('none'));
  await app.close();
});

test('OAuth: PKCE enforced, code single-use, refresh rotation with reuse detection, revocation', async () => {
  const { app } = await makeApp();
  const u = await signup(app, 'a@example.org');
  const c = await connect(app, u);
  const tokenReq = (o: Record<string, string>) => app.inject({ method: 'POST', url: '/oauth/token', headers: { 'content-type': 'application/x-www-form-urlencoded' }, payload: form(o) });
  // Code reuse refused.
  const again = await tokenReq({ grant_type: 'authorization_code', code: c.code, code_verifier: c.verifier, client_id: c.clientId, redirect_uri: REDIRECT });
  assert.equal(again.json().error, 'invalid_grant');
  // A second, independent connection (e.g. ChatGPT) coexists.
  await connect(app, u);
  // Refresh rotation.
  const r1 = await tokenReq({ grant_type: 'refresh_token', refresh_token: c.refresh_token, client_id: c.clientId });
  assert.equal(r1.statusCode, 200);
  assert.notEqual(r1.json().refresh_token, c.refresh_token);
  // Old access token no longer works after rotation; new one does.
  const mcpCall = (tok: string) => app.inject({ method: 'POST', url: '/mcp', headers: { authorization: `Bearer ${tok}`, 'content-type': 'application/json', accept: 'application/json, text/event-stream' },
    payload: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/list', params: {} }) });
  assert.equal((await mcpCall(c.access_token)).statusCode, 401);
  assert.equal((await mcpCall(r1.json().access_token)).statusCode, 200);
  // Reusing the old refresh token revokes the whole family.
  assert.equal((await tokenReq({ grant_type: 'refresh_token', refresh_token: c.refresh_token })).json().error, 'invalid_grant');
  assert.equal((await mcpCall(r1.json().access_token)).statusCode, 401);
  // Unknown redirect never redirects.
  const bad = await app.inject({ method: 'GET', url: `/oauth/authorize?${form({ ...c.params, redirect_uri: 'https://evil.example/cb' })}` });
  assert.equal(bad.statusCode, 400);
  // Denial returns access_denied to the client.
  const denied = await u.post('/api/oauth/approve', { approve: false, params: c.params });
  assert.equal(new URL(denied.json.redirect).searchParams.get('error'), 'access_denied');
  // The learner sees and revokes the connection.
  const c3 = await connect(app, u);
  assert.equal((await u.get('/api/connections')).json.connections.length, 2);
  await u.del(`/api/connections/${c3.clientId}`);
  assert.equal((await mcpCall(c3.access_token)).statusCode, 401);
  await app.close();
});

test('PKCE mismatch and non-HTTPS redirect registration are refused; loopback matches any port', async () => {
  const { app } = await makeApp();
  const u = await signup(app, 'a@example.org');
  const http = await app.inject({ method: 'POST', url: '/oauth/register', headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ redirect_uris: ['http://evil.example/cb'] }) });
  assert.equal(http.statusCode, 400);
  const reg = await app.inject({ method: 'POST', url: '/oauth/register', headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ client_name: 'Claude Code', redirect_uris: ['http://localhost/callback'] }) });
  const params = { response_type: 'code', client_id: reg.json().client_id, redirect_uri: 'http://localhost:3118/callback', state: 's',
    code_challenge: createHash('sha256').update('a'.repeat(43)).digest('base64url'), code_challenge_method: 'S256' };
  assert.equal((await app.inject({ method: 'GET', url: `/oauth/authorize?${form(params)}` })).statusCode, 302);
  const code = new URL((await u.post('/api/oauth/approve', { approve: true, params })).json.redirect).searchParams.get('code')!;
  const tok = await app.inject({ method: 'POST', url: '/oauth/token', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    payload: form({ grant_type: 'authorization_code', code, code_verifier: 'b'.repeat(43), client_id: params.client_id, redirect_uri: params.redirect_uri }) });
  assert.equal(tok.json().error, 'invalid_grant');
  await app.close();
});

test('MCP with the official client: read my course, save verified flashcards; other accounts stay private', async () => {
  const { app } = await makeApp();
  await app.listen({ port: 0, host: '127.0.0.1' });
  const base = `http://127.0.0.1:${(app.server.address() as any).port}`;
  const alice = await signup(app, 'alice@example.org');
  const bob = await signup(app, 'bob@example.org');
  const ch = await chapter(alice);
  const doc = (await alice.upload(`/api/chapters/${ch}/documents/upload`, 'c.pdf', await makePdf([LOREM, 'Deuxieme page du cours sur les eaux.']), 'application/pdf')).json;
  const bobDoc = (await bob.upload(`/api/chapters/${await chapter(bob)}/documents/upload`, 'b.pdf', await makePdf(['Cours prive de Bob sur un autre sujet tres different.']), 'application/pdf')).json;
  const tok = await connect(app, alice);

  const client = new McpClient({ name: 'test', version: '1.0.0' });
  await client.connect(new StreamableHTTPClientTransport(new URL(`${base}/mcp`), { requestInit: { headers: { Authorization: `Bearer ${tok.access_token}` } } }));
  const tools = (await client.listTools()).tools.map((t) => t.name).sort();
  assert.deepEqual(tools, ['add_course_text', 'add_flashcards', 'add_quiz_questions', 'create_chapter', 'get_chapter', 'get_my_progress', 'list_courses', 'read_course_pages', 'save_mindmap', 'save_note']);

  const list = JSON.parse((await client.callTool({ name: 'list_courses', arguments: {} }) as any).content[0].text);
  assert.equal(list.subjects[0].chapters[0].documents[0].id, doc.id);
  assert.ok(!JSON.stringify(list).includes(bobDoc.id));

  const read = JSON.parse((await client.callTool({ name: 'read_course_pages', arguments: { document_id: doc.id } }) as any).content[0].text);
  assert.equal(read.pages[0].page, 1);
  assert.match(read.pages[0].text, /condition de validite/);
  const stolen = await client.callTool({ name: 'read_course_pages', arguments: { document_id: bobDoc.id } }) as any;
  assert.equal(stolen.isError, true);

  const saved = JSON.parse((await client.callTool({ name: 'add_flashcards', arguments: { chapter_id: ch, document_id: doc.id, cards: [
    { question: 'Statut de la purification ?', answer: 'Condition de validité de la prière', skill: 'definition', pages: [1], excerpt: 'condition de validite de la priere' },
    { question: 'Citation inventée ?', answer: 'x', pages: [2], excerpt: 'phrase qui n existe pas dans le cours' },
  ] } }) as any).content[0].text);
  assert.deepEqual([saved.saved.items, saved.verified_sources, saved.to_verify], [2, 1, 1]);
  const into = await client.callTool({ name: 'add_flashcards', arguments: { chapter_id: (await bob.get('/api/library')).json.subjects[0].chapters[0].id, cards: [{ question: 'q', answer: 'a' }] } }) as any;
  assert.equal(into.isError, true, 'cannot write into another account');

  const mm = await client.callTool({ name: 'save_mindmap', arguments: { chapter_id: ch, title: 'Carte', nodes: [{ id: 'r', label: 'Racine' }, { id: 'a', label: 'A', parent: 'r' }] } }) as any;
  assert.ok(!mm.isError);
  const view = (await alice.get(`/api/chapters/${ch}`)).json;
  assert.equal(view.items.length, 2);
  assert.equal(view.items[0].origin, 'assistant:Claude');
  assert.equal(view.mindmaps.length, 1);
  assert.equal((await bob.get(`/api/chapters/${(await bob.get('/api/library')).json.subjects[0].chapters[0].id}`)).json.items.length, 0);
  await client.close();
  await app.close();
});

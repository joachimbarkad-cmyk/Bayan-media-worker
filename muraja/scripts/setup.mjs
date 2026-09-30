// Creates or updates muraja/.env for self-hosting. Usage: npm run setup -- https://mon-pc.mon-reseau.ts.net
// Existing secrets are kept; only the public URL is updated when given. Never commit .env.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '.env');
const env = new Map();
if (existsSync(file)) {
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) env.set(m[1], m[2]);
  }
}
const url = process.argv[2];
if (url) {
  let u;
  try { u = new URL(url); } catch { console.error(`Adresse invalide : ${url}`); process.exit(1); }
  if (u.protocol !== 'https:') { console.error("L'adresse publique doit commencer par https://"); process.exit(1); }
  env.set('MURAJA_PUBLIC_URL', u.origin);
  env.set('MURAJA_SECURE_COOKIES', '1');
}
if (!env.get('MURAJA_SECRET_KEY')) env.set('MURAJA_SECRET_KEY', randomBytes(32).toString('base64url'));
if (!env.get('MURAJA_INVITE_CODE')) env.set('MURAJA_INVITE_CODE', randomBytes(6).toString('base64url'));
if (!env.get('HOST')) env.set('HOST', '127.0.0.1');
if (!env.get('PORT')) env.set('PORT', '8787');
writeFileSync(file, [...env].map(([k, v]) => `${k}=${v}`).join('\n') + '\n', { mode: 0o600 });
console.log(`Configuration écrite dans ${file}`);
console.log(`Adresse publique : ${env.get('MURAJA_PUBLIC_URL') ?? '(aucune : site local seulement)'}`);
console.log(`Code d'invitation à donner aux personnes qui créent un compte : ${env.get('MURAJA_INVITE_CODE')}`);

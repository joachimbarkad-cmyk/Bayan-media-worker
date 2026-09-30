import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildApp } from './app.ts';

const here = path.dirname(fileURLToPath(import.meta.url));
const env = process.env;
if (env.MURAJA_PUBLIC_URL && !env.MURAJA_INVITE_CODE) {
  console.error("MURAJA_PUBLIC_URL est défini mais pas MURAJA_INVITE_CODE : n'importe qui pourrait créer un compte. Lancez `npm run setup`.");
  process.exit(1);
}
const { app } = await buildApp({
  dataDir: env.MURAJA_DATA ?? path.join(here, '..', 'data'),
  staticDir: path.join(here, '..', 'dist'),
  inviteCode: env.MURAJA_INVITE_CODE || undefined,
  secureCookies: env.MURAJA_SECURE_COOKIES === '1',
  publicUrl: env.MURAJA_PUBLIC_URL || undefined,
});
const port = Number(env.PORT ?? 8787);
const host = env.HOST ?? '127.0.0.1';
await app.listen({ port, host });
console.log(`Murāja'a : http://${host}:${port}${env.MURAJA_PUBLIC_URL ? ` — public : ${env.MURAJA_PUBLIC_URL}` : ''}`);

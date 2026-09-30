import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildApp } from './app.ts';

const here = path.dirname(fileURLToPath(import.meta.url));
const env = process.env;
const { app } = await buildApp({
  dataDir: env.MURAJA_DATA ?? path.join(here, '..', 'data'),
  staticDir: path.join(here, '..', 'dist'),
  inviteCode: env.MURAJA_INVITE_CODE || undefined,
  secureCookies: env.MURAJA_SECURE_COOKIES === '1',
});
const port = Number(env.PORT ?? 8787);
const host = env.HOST ?? '127.0.0.1';
await app.listen({ port, host });
console.log(`Murāja'a : http://${host}:${port}`);

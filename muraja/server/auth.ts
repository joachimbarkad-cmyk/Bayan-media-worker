import { randomBytes, scryptSync, timingSafeEqual, createHash } from 'node:crypto';

export const SESSION_MS = 60 * 86400_000;

export function hashPassword(password: string): string {
  const salt = randomBytes(16);
  const hash = scryptSync(password.normalize('NFKC'), salt, 64, { N: 16384, r: 8, p: 1 });
  return `scrypt$${salt.toString('base64')}$${hash.toString('base64')}`;
}

export function verifyPassword(password: string, stored: string): boolean {
  const [scheme, saltB64, hashB64] = stored.split('$');
  if (scheme !== 'scrypt' || !saltB64 || !hashB64) return false;
  const expected = Buffer.from(hashB64, 'base64');
  const actual = scryptSync(password.normalize('NFKC'), Buffer.from(saltB64, 'base64'), expected.length, { N: 16384, r: 8, p: 1 });
  return timingSafeEqual(actual, expected);
}

export function newSessionToken(now: number): { token: string; tokenHash: string; expiresAt: number } {
  const token = randomBytes(32).toString('base64url');
  return { token, tokenHash: hashToken(token), expiresAt: now + SESSION_MS };
}

export function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('hex');
}

/** Small in-memory limiter for login attempts (per key, sliding window). */
export class AttemptLimiter {
  private hits = new Map<string, number[]>();
  private max: number;
  private windowMs: number;
  constructor(max = 10, windowMs = 15 * 60_000) {
    this.max = max;
    this.windowMs = windowMs;
  }
  blocked(key: string, now = Date.now()): boolean {
    const list = (this.hits.get(key) ?? []).filter((t) => now - t < this.windowMs);
    this.hits.set(key, list);
    return list.length >= this.max;
  }
  record(key: string, now = Date.now()) {
    const list = this.hits.get(key) ?? [];
    list.push(now);
    this.hits.set(key, list);
  }
  reset(key: string) { this.hits.delete(key); }
}

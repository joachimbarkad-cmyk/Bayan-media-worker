import { createCipheriv, createDecipheriv, createHash, randomBytes } from 'node:crypto';

/**
 * Encrypts users' personal API keys at rest (AES-256-GCM). The server key comes from
 * MURAJA_SECRET_KEY (at least 32 characters) and never reaches the browser or the database.
 */
export class Sealer {
  private key: Buffer;
  constructor(secret: string) {
    if (secret.length < 32) throw new Error('MURAJA_SECRET_KEY doit contenir au moins 32 caractères.');
    this.key = createHash('sha256').update(secret).digest();
  }
  seal(plain: string): string {
    const iv = randomBytes(12);
    const c = createCipheriv('aes-256-gcm', this.key, iv);
    const body = Buffer.concat([c.update(plain, 'utf8'), c.final()]);
    return ['v1', iv.toString('base64'), c.getAuthTag().toString('base64'), body.toString('base64')].join('.');
  }
  open(sealed: string): string {
    const [v, iv, tag, body] = sealed.split('.');
    if (v !== 'v1') throw new Error('format inconnu');
    const d = createDecipheriv('aes-256-gcm', this.key, Buffer.from(iv, 'base64'));
    d.setAuthTag(Buffer.from(tag, 'base64'));
    return Buffer.concat([d.update(Buffer.from(body, 'base64')), d.final()]).toString('utf8');
  }
}

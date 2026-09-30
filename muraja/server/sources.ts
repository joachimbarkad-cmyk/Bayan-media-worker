import type { DB } from './db.ts';
import { normalizeText } from './pdf.ts';

export type SourceStatus = 'verified' | 'to_verify' | 'personal';

export interface SourceInput { document_id?: string | null; pages?: number[] | null; excerpt?: string | null }

function squash(s: string): string {
  return normalizeText(s).toLowerCase()
    .replace(/[ً-ْٰـ]/g, '') // Arabic harakat & tatweel: compare letters only
    .replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

/**
 * Decide the source status of an item. A reference is "verified" only when the excerpt
 * really appears in the cited readable pages of a document owned by the same user.
 * Nothing is inferred or invented: missing data stays missing and is marked "to_verify".
 */
export function resolveSource(db: DB, userId: string, src: SourceInput | null | undefined, origin: 'manual' | 'import') {
  const empty = { source_document_id: null as string | null, source_pages: null as string | null, source_excerpt: null as string | null };
  if (!src || (!src.document_id && !src.excerpt && !(src.pages && src.pages.length))) {
    return { ...empty, source_status: (origin === 'manual' ? 'personal' : 'to_verify') as SourceStatus };
  }
  const out = {
    source_document_id: null as string | null,
    source_pages: src.pages && src.pages.length ? JSON.stringify([...new Set(src.pages)].sort((a, b) => a - b)) : null,
    source_excerpt: src.excerpt ? src.excerpt.slice(0, 2000) : null,
    source_status: 'to_verify' as SourceStatus,
  };
  if (src.document_id) {
    const doc = db.prepare('SELECT id FROM documents WHERE id = ? AND user_id = ?').get(src.document_id, userId);
    if (doc) out.source_document_id = src.document_id;
  }
  if (out.source_document_id && out.source_excerpt && src.pages && src.pages.length) {
    const needle = squash(out.source_excerpt);
    const rows = db.prepare(
      `SELECT page_number, text FROM document_pages WHERE document_id = ? AND user_id = ? AND readable = 1
       AND page_number IN (${src.pages.map(() => '?').join(',')})`,
    ).all(out.source_document_id, userId, ...src.pages) as Array<{ text: string }>;
    if (needle.length >= 8 && rows.some((r) => squash(r.text).includes(needle))) out.source_status = 'verified';
  }
  return out;
}

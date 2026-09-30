import path from 'node:path';
import { createRequire } from 'node:module';
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';

const require = createRequire(import.meta.url);
const STANDARD_FONTS = path.join(path.dirname(require.resolve('pdfjs-dist/package.json')), 'standard_fonts') + path.sep;

export const MAX_PDF_PAGES = 600;
/** Fewer meaningful characters than this on a page = page not readable (scan, image, empty). */
const MIN_PAGE_CHARS = 25;

export interface ExtractedPage { page_number: number; text: string; readable: boolean }
export interface Extraction {
  pages: ExtractedPage[];
  status: 'ok' | 'partial' | 'insufficient';
  note: string;
}

/** Normalise text: NFKC maps Arabic presentation forms (U+FB50–U+FEFF) back to base letters. */
export function normalizeText(s: string): string {
  return s.normalize('NFKC').replace(/\u0000/g, '').replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
}

function meaningfulChars(s: string): number {
  return (s.match(/[\p{L}\p{N}]/gu) ?? []).length;
}

/** Share of characters that look like broken font mapping (replacement / private-use chars). */
function garbledRatio(s: string): number {
  if (!s) return 0;
  const bad = (s.match(/[�-]/g) ?? []).length;
  return bad / s.length;
}

function describePages(nums: number[]): string {
  return nums.length > 12 ? `${nums.slice(0, 12).join(', ')}…` : nums.join(', ');
}

export async function extractPdf(data: Uint8Array): Promise<Extraction> {
  const task = pdfjs.getDocument({ data, useSystemFonts: false, standardFontDataUrl: STANDARD_FONTS, verbosity: 0 });
  const doc = await task.promise;
  try {
    if (doc.numPages > MAX_PDF_PAGES) {
      throw new UserError(`Ce PDF compte ${doc.numPages} pages ; la limite est ${MAX_PDF_PAGES}. Découpez-le en plusieurs chapitres.`);
    }
    const pages: ExtractedPage[] = [];
    for (let i = 1; i <= doc.numPages; i++) {
      const page = await doc.getPage(i);
      const content = await page.getTextContent();
      let text = '';
      for (const item of content.items as Array<{ str?: string; hasEOL?: boolean }>) {
        if (typeof item.str !== 'string') continue;
        text += item.str + (item.hasEOL ? '\n' : ' ');
      }
      text = normalizeText(text);
      const readable = meaningfulChars(text) >= MIN_PAGE_CHARS && garbledRatio(text) < 0.2;
      pages.push({ page_number: i, text, readable });
      page.cleanup();
    }
    const unreadable = pages.filter((p) => !p.readable).map((p) => p.page_number);
    let status: Extraction['status'] = 'ok';
    let note = '';
    if (pages.length === 0 || unreadable.length / pages.length > 0.5) {
      status = 'insufficient';
      note = `Le texte de ce PDF n'a pas pu être lu correctement (${unreadable.length} page(s) sur ${pages.length}). ` +
        `Il s'agit probablement d'un document scanné ou d'une police mal encodée. La reconnaissance de texte (OCR) ` +
        `n'est pas encore disponible : le PDF reste consultable, mais aucune question ne sera présentée comme fiable ` +
        `à partir de ce texte. Vous pouvez coller le texte du cours ou importer des supports préparés ailleurs.`;
    } else if (unreadable.length > 0) {
      status = 'partial';
      note = `Pages sans texte lisible : ${describePages(unreadable)} (image, schéma ou page scannée). Les autres pages sont exploitables.`;
    }
    return { pages, status, note };
  } finally {
    await task.destroy();
  }
}

/** An error whose message can be shown to the user as-is. */
export class UserError extends Error {
  status: number;
  constructor(message: string, status = 400) {
    super(message);
    this.status = status;
  }
}

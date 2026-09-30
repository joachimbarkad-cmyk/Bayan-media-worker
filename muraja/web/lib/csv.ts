import Papa from 'papaparse';

export interface CsvTable { headers: string[]; rows: string[][]; delimiter: string; warnings: string[] }

/** Decode bytes: UTF-8 (BOM stripped) by default; fall back suggestion when invalid sequences appear. */
export function decodeBytes(bytes: Uint8Array, encoding: 'utf-8' | 'windows-1256' | 'windows-1252' = 'utf-8'): { text: string; suspicious: boolean } {
  const text = new TextDecoder(encoding).decode(bytes).replace(/^﻿/, '');
  return { text, suspicious: encoding === 'utf-8' && text.includes('�') };
}

/**
 * Parse CSV/TSV text. Handles quoted fields, embedded newlines and delimiters, Unicode (Arabic),
 * and auto-detects , ; tab or | unless a delimiter is forced.
 */
export function parseCsv(text: string, opts: { delimiter?: string; hasHeader: boolean }): CsvTable {
  const res = Papa.parse<string[]>(text, {
    delimiter: opts.delimiter || '',
    delimitersToGuess: [',', ';', '\t', '|'],
    skipEmptyLines: 'greedy',
  });
  const warnings = res.errors.slice(0, 5).map((e) => `ligne ${(e.row ?? 0) + 1} : ${e.message}`);
  const data = res.data.map((r) => r.map((c) => (c ?? '').trim()));
  const width = Math.max(0, ...data.map((r) => r.length));
  const norm = data.map((r) => [...r, ...Array(width - r.length).fill('')]);
  const headers = opts.hasHeader && norm.length
    ? norm[0].map((h, i) => h || `Colonne ${i + 1}`)
    : Array.from({ length: width }, (_, i) => `Colonne ${i + 1}`);
  return { headers, rows: opts.hasHeader ? norm.slice(1) : norm, delimiter: res.meta.delimiter, warnings };
}

export type Mapping = { question: number; answer: number; explanation: number; pages: number; excerpt: number };

/** Guess a column mapping from header names (French/English/Arabic); -1 means unused. */
export function guessMapping(headers: string[]): Mapping {
  const find = (re: RegExp, fallback: number) => {
    const i = headers.findIndex((h) => re.test(h.toLowerCase()));
    return i >= 0 ? i : fallback;
  };
  const question = find(/question|recto|front|term|terme|سؤال/, 0);
  const answer = find(/r[ée]ponse|verso|back|answer|définition|definition|جواب|إجابة/, headers.length > 1 ? (question === 0 ? 1 : 0) : -1);
  return {
    question, answer,
    explanation: find(/explication|explanation|note|شرح/, -1),
    pages: find(/page/, -1),
    excerpt: find(/extrait|excerpt|citation|source|quote/, -1),
  };
}

export function applyMapping(rows: string[][], m: Mapping) {
  const col = (r: string[], i: number) => (i >= 0 ? r[i] ?? '' : '');
  return rows.map((r) => ({
    question: col(r, m.question), answer: col(r, m.answer),
    explanation: col(r, m.explanation) || undefined, pages: col(r, m.pages) || undefined, excerpt: col(r, m.excerpt) || undefined,
  }));
}

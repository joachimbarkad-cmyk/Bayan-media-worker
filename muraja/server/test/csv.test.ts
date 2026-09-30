import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseCsv, decodeBytes, guessMapping, applyMapping } from '../../web/lib/csv.ts';

test('CSV with Arabic, quoted fields, embedded newlines and commas', () => {
  const text = '﻿Question,Réponse\n"ما هي الطهارة؟\nsur deux lignes","رفع الحدث، وإزالة النجس"\n"Définition, avec virgule","Réponse ""citée"""\n';
  const { text: decoded } = decodeBytes(new TextEncoder().encode(text));
  const t = parseCsv(decoded, { hasHeader: true });
  assert.equal(t.delimiter, ',');
  assert.deepEqual(t.headers, ['Question', 'Réponse']);
  assert.equal(t.rows.length, 2);
  assert.equal(t.rows[0][0], 'ما هي الطهارة؟\nsur deux lignes');
  assert.equal(t.rows[0][1], 'رفع الحدث، وإزالة النجس');
  assert.equal(t.rows[1][1], 'Réponse "citée"');
  const m = guessMapping(t.headers);
  assert.deepEqual([m.question, m.answer], [0, 1]);
  assert.equal(applyMapping(t.rows, m)[0].answer, 'رفع الحدث، وإزالة النجس');
});

test('semicolon and tab separators are detected; header can be disabled', () => {
  assert.equal(parseCsv('a;b\nc;d\n', { hasHeader: false }).delimiter, ';');
  const tsv = parseCsv('recto\tverso\nq\tr\n', { hasHeader: true });
  assert.equal(tsv.delimiter, '\t');
  assert.deepEqual(guessMapping(tsv.headers), { question: 0, answer: 1, explanation: -1, pages: -1, excerpt: -1 });
  const noHeader = parseCsv('q1,r1\nq2,r2\n', { hasHeader: false });
  assert.equal(noHeader.rows.length, 2);
  assert.deepEqual(noHeader.headers, ['Colonne 1', 'Colonne 2']);
});

test('forced delimiter and ragged rows', () => {
  const t = parseCsv('q|r|x\nq2|r2\n', { hasHeader: false, delimiter: '|' });
  assert.deepEqual(t.rows[1], ['q2', 'r2', '']);
});

test('Windows-1256 Arabic bytes are flagged when read as UTF-8 and decoded when chosen', () => {
  const bytes = new Uint8Array([0xC7, 0xE1, 0xD8, 0xE5, 0xC7, 0xD1, 0xC9]); // "الطهارة" in windows-1256
  assert.equal(decodeBytes(bytes).suspicious, true);
  assert.equal(decodeBytes(bytes, 'windows-1256').text, 'الطهارة');
});

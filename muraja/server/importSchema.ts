import { z } from 'zod';

/** Documented JSON import format (see docs/IMPORT_FORMAT.md). All strings are stored as plain text. */
const text = (max: number) => z.string().trim().min(1).max(max);
const Source = z.object({
  pages: z.array(z.number().int().min(1).max(10000)).max(50).optional(),
  excerpt: z.string().trim().max(2000).optional(),
}).strict().optional();
const Skill = z.enum(['definition', 'distinction', 'application']).optional();

export const ImportV1 = z.object({
  format: z.literal('muraja.v1'),
  document_title: z.string().trim().max(300).optional(),
  notes: z.array(z.object({ title: text(300), body: text(50000), source: Source }).strict()).max(500).default([]),
  flashcards: z.array(z.object({
    question: text(2000), answer: text(5000), explanation: z.string().trim().max(5000).optional(), skill: Skill, source: Source,
  }).strict()).max(3000).default([]),
  mcq: z.array(z.object({
    question: text(2000),
    choices: z.array(z.object({ text: text(1000), correct: z.boolean(), why: z.string().trim().max(2000).optional() }).strict())
      .min(2).max(8)
      .refine((cs) => cs.filter((c) => c.correct).length === 1, 'exactement une proposition doit être correcte'),
    explanation: z.string().trim().max(5000).optional(), skill: Skill, source: Source,
  }).strict()).max(3000).default([]),
  open: z.array(z.object({
    question: text(2000), answer: text(5000), explanation: z.string().trim().max(5000).optional(), skill: Skill, source: Source,
  }).strict()).max(1000).default([]),
  mindmap: z.object({
    title: text(300),
    nodes: z.array(z.object({
      id: text(100), label: text(500), parent: z.string().max(100).nullable().optional(), note: z.string().max(5000).optional(),
    }).strict()).min(1).max(1000),
  }).strict().optional(),
  glossary: z.array(z.object({ term: text(300), arabic: z.string().trim().max(300).optional(), definition: z.string().trim().max(3000).optional() }).strict()).max(2000).default([]),
}).strict();
export type ImportV1 = z.infer<typeof ImportV1>;

export interface MindNode { id: string; label: string; parentId: string | null; note: string; itemIds: string[] }

/** Checks a node list forms a single tree (one root, known parents, no cycle). Returns an error or null. */
export function treeError(nodes: Array<{ id: string; parentId: string | null }>): string | null {
  const ids = new Set<string>();
  for (const n of nodes) {
    if (ids.has(n.id)) return `identifiant de nœud en double : ${n.id}`;
    ids.add(n.id);
  }
  const roots = nodes.filter((n) => !n.parentId);
  if (roots.length !== 1) return `la carte doit avoir exactement une racine (trouvé : ${roots.length})`;
  const parent = new Map(nodes.map((n) => [n.id, n.parentId]));
  for (const n of nodes) {
    if (n.parentId && !ids.has(n.parentId)) return `parent inconnu pour ${n.id} : ${n.parentId}`;
    let cur: string | null | undefined = n.parentId, steps = 0;
    while (cur) {
      if (cur === n.id || ++steps > nodes.length) return `cycle détecté autour de ${n.id}`;
      cur = parent.get(cur);
    }
  }
  return null;
}

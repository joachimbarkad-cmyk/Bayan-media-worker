import type { FastifyRequest } from 'fastify';
import type { DB } from './db.ts';
import type { ImportV1, MindNode } from './importSchema.ts';
import type { JsonCaller } from './generation.ts';

export interface User { id: string; email: string; name: string; timezone: string; settings: string }

/** Helpers shared by the route modules (built in app.ts). */
export interface Ctx {
  db: DB;
  env: NodeJS.ProcessEnv;
  now: () => number;
  auth: (req: FastifyRequest) => User;
  currentUser: (req: FastifyRequest) => User | null;
  owned: <T = any>(table: string, id: string, userId: string) => T;
  saveContent: (userId: string, chapterId: string, data: ImportV1, mapNodes: MindNode[] | null, docId: string | null, origin: string) =>
    { verified: number; notes: string[]; items: Array<{ id: string; type: string; source_status: string }>; mindmap: string | null };
  docForImport: (userId: string, chapterId: string, documentId?: string | null, title?: string) => string | null;
  dayBounds: (tz: string, now: number) => { start: number; end: number; date: string };
  publicUrl?: string;
  callJson?: JsonCaller;
  secret?: string;
}

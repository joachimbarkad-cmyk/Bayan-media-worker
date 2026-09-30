export class ApiError extends Error {
  status: number;
  details: string[];
  constructor(status: number, message: string, details: string[] = []) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function request<T>(method: string, url: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { 'x-muraja': '1' };
  let payload: BodyInit | undefined;
  if (body instanceof FormData) payload = body;
  else if (body !== undefined) {
    headers['content-type'] = 'application/json';
    payload = JSON.stringify(body);
  }
  let res: Response;
  try {
    res = await fetch(url, { method, headers, body: payload, credentials: 'same-origin' });
  } catch {
    throw new ApiError(0, 'Connexion impossible. Vérifiez votre réseau puis réessayez.');
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && url !== '/api/me') window.dispatchEvent(new Event('muraja:logout'));
    throw new ApiError(res.status, data?.error ?? `Erreur ${res.status}`, data?.details ?? []);
  }
  return data as T;
}

export const api = {
  get: <T,>(u: string) => request<T>('GET', u),
  post: <T,>(u: string, b: unknown = {}) => request<T>('POST', u, b),
  put: <T,>(u: string, b: unknown) => request<T>('PUT', u, b),
  patch: <T,>(u: string, b: unknown) => request<T>('PATCH', u, b),
  del: <T,>(u: string) => request<T>('DELETE', u),
};

export type SourceStatus = 'verified' | 'to_verify' | 'personal';
export interface Choice { text: string; correct: boolean; why: string }
export interface Item {
  id: string; chapter_id: string; type: 'flashcard' | 'mcq' | 'open'; prompt: string; answer: string; explanation: string;
  choices: Choice[] | null; skill: string | null; origin: string; source_document_id: string | null; source_pages: number[] | null;
  source_excerpt: string | null; source_status: SourceStatus; suspended: boolean; due?: number; state?: number; reps?: number; lapses?: number;
}
export interface Note {
  id: string; title: string; body: string; origin: string; source_document_id: string | null; source_pages: number[] | null;
  source_excerpt: string | null; source_status: SourceStatus; updated_at: number;
}
export interface DocumentInfo {
  id: string; title: string; kind: 'pdf' | 'text' | 'image'; size: number; page_count: number;
  extraction_status: 'ok' | 'partial' | 'insufficient' | 'not_applicable'; extraction_note: string; created_at: number;
}
export interface User {
  id: string; email: string; name: string; timezone: string;
  settings: { request_retention: number; maximum_interval: number; enable_fuzz: boolean; new_per_day: number };
}
export interface ChapterView {
  chapter: { id: string; name: string; subject: { id: string; name: string } };
  documents: DocumentInfo[]; notes: Note[]; items: Item[];
  mindmaps: Array<{ id: string; title: string; origin: string; source_status: SourceStatus }>;
}
export interface MindNode { id: string; label: string; parentId: string | null; note: string; itemIds: string[] }

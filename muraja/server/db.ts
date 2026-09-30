import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import path from 'node:path';

export type DB = DatabaseSync;

const MIGRATIONS: string[] = [
  `
  CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Indian/Reunion',
    settings TEXT NOT NULL DEFAULT '{}',
    created_at INTEGER NOT NULL
  );
  CREATE TABLE sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
  );
  CREATE TABLE subjects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL
  );
  CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL
  );
  CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('pdf','text','image')),
    mime TEXT,
    size INTEGER NOT NULL DEFAULT 0,
    storage_name TEXT,
    page_count INTEGER NOT NULL DEFAULT 0,
    extraction_status TEXT NOT NULL CHECK (extraction_status IN ('ok','partial','insufficient','not_applicable')),
    extraction_note TEXT NOT NULL DEFAULT '',
    created_at INTEGER NOT NULL
  );
  CREATE TABLE document_pages (
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    readable INTEGER NOT NULL,
    PRIMARY KEY (document_id, page_number)
  );
  CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    origin TEXT NOT NULL,
    source_document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    source_pages TEXT,
    source_excerpt TEXT,
    source_status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );
  CREATE TABLE items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('flashcard','mcq','open')),
    prompt TEXT NOT NULL,
    answer TEXT NOT NULL DEFAULT '',
    explanation TEXT NOT NULL DEFAULT '',
    choices TEXT,
    skill TEXT,
    origin TEXT NOT NULL,
    source_document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    source_pages TEXT,
    source_excerpt TEXT,
    source_status TEXT NOT NULL,
    suspended INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );
  CREATE TABLE review_state (
    item_id TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    due INTEGER NOT NULL,
    stability REAL NOT NULL,
    difficulty REAL NOT NULL,
    elapsed_days REAL NOT NULL,
    scheduled_days REAL NOT NULL,
    learning_steps INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    lapses INTEGER NOT NULL,
    state INTEGER NOT NULL,
    last_review INTEGER,
    last_rating INTEGER,
    version INTEGER NOT NULL DEFAULT 0
  );
  CREATE TABLE review_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    correct INTEGER,
    response TEXT,
    state_before INTEGER NOT NULL,
    due_after INTEGER NOT NULL,
    reviewed_at INTEGER NOT NULL
  );
  CREATE TABLE study_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_ids TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    finished_at INTEGER
  );
  CREATE TABLE mindmaps (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    data TEXT NOT NULL,
    origin TEXT NOT NULL,
    source_status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );
  CREATE TABLE glossary (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    arabic TEXT NOT NULL DEFAULT '',
    definition TEXT NOT NULL DEFAULT '',
    created_at INTEGER NOT NULL
  );
  CREATE INDEX idx_items_user ON items(user_id, chapter_id);
  CREATE INDEX idx_state_due ON review_state(user_id, due);
  CREATE INDEX idx_logs_user ON review_logs(user_id, reviewed_at);
  CREATE INDEX idx_docs_user ON documents(user_id, chapter_id);
  `,
];

export function openDb(dataDir: string): DB {
  mkdirSync(dataDir, { recursive: true });
  const db = new DatabaseSync(path.join(dataDir, 'muraja.sqlite'));
  db.exec('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;');
  const version = (db.prepare('PRAGMA user_version').get() as { user_version: number }).user_version;
  for (let v = version; v < MIGRATIONS.length; v++) {
    tx(db, () => {
      db.exec(MIGRATIONS[v]);
      db.exec(`PRAGMA user_version = ${v + 1}`);
    });
  }
  return db;
}

/** Run fn inside a transaction; rolls back on error. */
export function tx<T>(db: DB, fn: () => T): T {
  db.exec('BEGIN IMMEDIATE');
  try {
    const out = fn();
    db.exec('COMMIT');
    return out;
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }
}

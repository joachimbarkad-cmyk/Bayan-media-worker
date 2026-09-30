import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { ApiError, type SourceStatus } from '../api.ts';

export function useLoad<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(fn, deps);
  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await run());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [run]);
  useEffect(() => { reload(); }, [reload]);
  return { data, error, loading, reload, setData };
}

export function errorText(e: unknown): string {
  if (e instanceof ApiError) return e.details.length ? `${e.message} ${e.details.slice(0, 4).join(' · ')}` : e.message;
  return e instanceof Error ? e.message : String(e);
}

export function Loading({ label = 'Chargement…' }: { label?: string }) {
  return <div className="loading" role="status" aria-live="polite">{label}</div>;
}

export function ErrorBox({ error, onRetry }: { error: string | null; onRetry?: () => void }) {
  if (!error) return null;
  return (
    <div className="notice bad" role="alert">
      <div>{error}</div>
      {onRetry && <button className="small" onClick={onRetry} style={{ marginTop: 8 }}>Réessayer</button>}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty">{children}</div>;
}

/**
 * User-provided text: plain text only (never HTML). Each line gets its own direction so a
 * French line after an Arabic one (or the reverse) is laid out correctly.
 */
export function Txt({ children, className = '', as: As = 'div' }: { children: string; className?: string; as?: 'div' | 'span' | 'p' }) {
  const lines = children.split('\n');
  if (As === 'span' || lines.length === 1) return <As className={`text ${className}`} dir="auto">{children}</As>;
  return (
    <As className={`text ${className}`}>
      {lines.map((l, i) => (l.trim() ? <div key={i} dir="auto">{l}</div> : <br key={i} />))}
    </As>
  );
}

const SOURCE_LABEL: Record<SourceStatus, [string, string]> = {
  verified: ['Source vérifiée', 'ok'],
  to_verify: ['Source à vérifier', 'warn'],
  personal: ['Note personnelle', ''],
};
export function SourceBadge({ status, pages }: { status: SourceStatus; pages?: number[] | null }) {
  const [label, cls] = SOURCE_LABEL[status];
  return (
    <span className={`badge ${cls}`} title={status === 'verified' ? "L'extrait cité a été retrouvé dans le document." : status === 'to_verify' ? "Aucun extrait retrouvé dans le document : à contrôler." : 'Contenu rédigé par vous.'}>
      {label}{pages && pages.length ? ` · p. ${pages.join(', ')}` : ''}
    </span>
  );
}

export const TYPE_LABEL = { flashcard: 'Flashcard', mcq: 'QCM', open: 'Question ouverte' } as const;
export const SKILL_LABEL: Record<string, string> = { definition: 'Définition', distinction: 'Distinction', application: 'Application' };

export function formatDue(ms?: number, state?: number) {
  if (state === 0 || ms == null) return 'Nouvelle';
  const d = new Date(ms);
  const diff = ms - Date.now();
  if (diff <= 0) return 'À revoir';
  if (diff < 86400_000) return `Aujourd'hui ${d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
  return `Le ${d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}`;
}

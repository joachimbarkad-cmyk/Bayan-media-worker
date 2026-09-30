import { api, type User } from '../api.ts';
import { go } from '../router.ts';
import { useLoad, Loading, ErrorBox, Empty, errorText } from '../components/ui.tsx';
import { useState } from 'react';

interface Today { due: number; new: number; later_today: number; date: string; session: { id: string; position: number; total: number } | null }
interface Lib { subjects: Array<{ id: string; name: string; chapters: Array<{ id: string; name: string; items: number; due: number }> }> }

export function Home({ user }: { user: User }) {
  const today = useLoad(() => api.get<Today>('/api/review/today'), []);
  const lib = useLoad(() => api.get<Lib>('/api/library'), []);
  const [err, setErr] = useState<string | null>(null);

  async function start(resume: boolean) {
    try {
      const s = await api.post<{ id: string | null }>('/api/review/sessions', { resume });
      if (s.id) go(`/review?session=${s.id}`);
      else today.reload();
    } catch (e) { setErr(errorText(e)); }
  }

  const t = today.data;
  const total = t ? t.due + t.new : 0;
  const hasContent = !!lib.data?.subjects.some((s) => s.chapters.some((c) => c.items > 0));
  return (
    <div className="stack">
      <h1>Bonjour {user.name}</h1>
      <ErrorBox error={today.error ?? err} onRetry={today.reload} />
      {today.loading && !t ? <Loading /> : t && (
        <section className="card hero" aria-labelledby="today-title">
          <h2 id="today-title" className="sr-only">Révision du jour</h2>
          {t.session && t.session.position < t.session.total ? (
            <>
              <p>Séance en cours : {t.session.position} / {t.session.total}</p>
              <button className="primary big" onClick={() => go(`/review?session=${t.session!.id}`)}>Reprendre ma révision</button>
            </>
          ) : total > 0 ? (
            <>
              <div className="count">{total}</div>
              <p>{t.due > 0 && `${t.due} à revoir`}{t.due > 0 && t.new > 0 && ' · '}{t.new > 0 && `${t.new} nouvelle${t.new > 1 ? 's' : ''}`}</p>
              <button className="primary big" onClick={() => start(false)}>Réviser aujourd'hui</button>
            </>
          ) : hasContent ? (
            <>
              <p style={{ fontSize: '1.2rem' }}>✓ Rien à réviser pour le moment.</p>
              <p className="muted">{t.later_today > 0
                ? `${t.later_today} carte${t.later_today > 1 ? 's' : ''} en cours d'apprentissage reviendr${t.later_today > 1 ? 'ont' : 'a'} plus tard aujourd'hui.`
                : 'Revenez demain : vos cartes réapparaîtront au bon moment.'}</p>
            </>
          ) : (
            <>
              <p style={{ fontSize: '1.1rem' }}>Commencez par ajouter un cours.</p>
              <p className="muted">Un PDF, un texte, ou des flashcards préparées ailleurs (par exemple NotebookLM).</p>
            </>
          )}
        </section>
      )}
      <button className="big" onClick={() => go('/add')}>＋ Ajouter un cours</button>
      <section aria-labelledby="mine">
        <h2 id="mine" style={{ marginTop: 20 }}>Mes matières</h2>
        <ErrorBox error={lib.error} onRetry={lib.reload} />
        {lib.loading && !lib.data ? <Loading /> : lib.data && (lib.data.subjects.length === 0
          ? <Empty>Aucune matière pour l'instant.</Empty>
          : (
            <div className="card"><ul className="list">
              {lib.data.subjects.flatMap((s) => s.chapters.map((c) => (
                <li key={c.id} className="spread">
                  <a href={`#/chapter/${c.id}`} dir="auto"><b>{s.name}</b> — {c.name}</a>
                  <span className="muted">{c.items} élément{c.items > 1 ? 's' : ''}{c.due > 0 ? ` · ${c.due} à revoir` : ''}</span>
                </li>
              )))}
              {lib.data.subjects.every((s) => s.chapters.length === 0) && <li>Aucun chapitre. <a href="#/library">Organiser la bibliothèque</a></li>}
            </ul></div>
          ))}
      </section>
    </div>
  );
}

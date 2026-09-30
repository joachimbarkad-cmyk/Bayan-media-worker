import { useState } from 'react';
import { api } from '../api.ts';
import { useLoad, Loading, ErrorBox, Empty, errorText } from '../components/ui.tsx';

interface Lib { subjects: Array<{ id: string; name: string; chapters: Array<{ id: string; name: string; items: number; documents: number; due: number }> }> }

export function Library() {
  const lib = useLoad(() => api.get<Lib>('/api/library'), []);
  const [newSubject, setNewSubject] = useState('');
  const [newChapter, setNewChapter] = useState<Record<string, string>>({});
  const [err, setErr] = useState<string | null>(null);

  async function act(fn: () => Promise<unknown>) {
    setErr(null);
    try { await fn(); await lib.reload(); } catch (e) { setErr(errorText(e)); }
  }

  return (
    <div className="stack">
      <div className="spread"><h1>Bibliothèque</h1><a className="btn" href="#/glossary">Glossaire</a></div>
      <ErrorBox error={lib.error ?? err} onRetry={lib.reload} />
      <form className="card row" onSubmit={(e) => { e.preventDefault(); if (newSubject.trim()) act(async () => { await api.post('/api/subjects', { name: newSubject }); setNewSubject(''); }); }}>
        <label htmlFor="ns" className="sr-only">Nouvelle matière</label>
        <input id="ns" type="text" placeholder="Nouvelle matière (ex. Fiqh, Tajwid…)" value={newSubject} onChange={(e) => setNewSubject(e.target.value)} style={{ flex: 1, minWidth: 200 }} dir="auto" />
        <button className="primary">Ajouter</button>
      </form>
      {lib.loading && !lib.data ? <Loading /> : lib.data && lib.data.subjects.length === 0 && <Empty>Créez une première matière, puis ses chapitres.</Empty>}
      {lib.data?.subjects.map((s) => (
        <section key={s.id} className="card" aria-label={s.name}>
          <div className="spread">
            <h2 dir="auto">{s.name}</h2>
            <div className="row">
              <button className="small" onClick={() => { const n = prompt('Nouveau nom de la matière', s.name); if (n?.trim()) act(() => api.patch(`/api/subjects/${s.id}`, { name: n })); }}>Renommer</button>
              <button className="small danger" onClick={() => { if (confirm(`Supprimer « ${s.name} » et tout son contenu ?`)) act(() => api.del(`/api/subjects/${s.id}`)); }}>Supprimer</button>
            </div>
          </div>
          <ul className="list">
            {s.chapters.map((c) => (
              <li key={c.id} className="spread">
                <a href={`#/chapter/${c.id}`} dir="auto" style={{ fontWeight: 600 }}>{c.name}</a>
                <span className="muted">{c.documents} support{c.documents > 1 ? 's' : ''} · {c.items} élément{c.items > 1 ? 's' : ''}{c.due ? ` · ${c.due} à revoir` : ''}</span>
              </li>
            ))}
          </ul>
          <form className="row" style={{ marginTop: 10 }} onSubmit={(e) => { e.preventDefault(); const n = newChapter[s.id]; if (n?.trim()) act(async () => { await api.post('/api/chapters', { subject_id: s.id, name: n }); setNewChapter({ ...newChapter, [s.id]: '' }); }); }}>
            <label htmlFor={`nc-${s.id}`} className="sr-only">Nouveau chapitre</label>
            <input id={`nc-${s.id}`} type="text" placeholder="Nouveau chapitre" value={newChapter[s.id] ?? ''} onChange={(e) => setNewChapter({ ...newChapter, [s.id]: e.target.value })} style={{ flex: 1, minWidth: 180 }} dir="auto" />
            <button>Ajouter le chapitre</button>
          </form>
        </section>
      ))}
    </div>
  );
}

import { useState } from 'react';
import { api } from '../api.ts';
import { useLoad, Loading, ErrorBox, Empty, errorText } from '../components/ui.tsx';

interface Entry { id: string; term: string; arabic: string; definition: string }

export function Glossary() {
  const g = useLoad(() => api.get<{ entries: Entry[] }>('/api/glossary'), []);
  const [draft, setDraft] = useState({ term: '', arabic: '', definition: '' });
  const [editing, setEditing] = useState<Entry | null>(null);
  const [q, setQ] = useState('');
  const [err, setErr] = useState<string | null>(null);

  async function act(fn: () => Promise<unknown>) {
    setErr(null);
    try { await fn(); await g.reload(); } catch (e) { setErr(errorText(e)); }
  }
  const list = (g.data?.entries ?? []).filter((e) => !q || `${e.term} ${e.arabic} ${e.definition}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="stack">
      <p className="muted" style={{ marginBottom: 0 }}><a href="#/library">← Bibliothèque</a></p>
      <h1>Glossaire</h1>
      <p className="muted">Vos termes de référence (translittération, arabe vocalisé, sens retenu dans votre cours).</p>
      <ErrorBox error={g.error ?? err} onRetry={g.reload} />
      <form className="card stack" onSubmit={(e) => { e.preventDefault(); if (draft.term.trim()) act(async () => { await api.post('/api/glossary', draft); setDraft({ term: '', arabic: '', definition: '' }); }); }}>
        <div className="grid2">
          <div><label htmlFor="gt">Terme</label><input id="gt" type="text" value={draft.term} onChange={(e) => setDraft({ ...draft, term: e.target.value })} dir="auto" /></div>
          <div><label htmlFor="ga">En arabe</label><input id="ga" type="text" lang="ar" dir="rtl" value={draft.arabic} onChange={(e) => setDraft({ ...draft, arabic: e.target.value })} /></div>
        </div>
        <div><label htmlFor="gd">Définition</label><textarea id="gd" rows={2} value={draft.definition} onChange={(e) => setDraft({ ...draft, definition: e.target.value })} dir="auto" /></div>
        <div className="row end"><button className="primary">Ajouter</button></div>
      </form>
      <label htmlFor="gq" className="sr-only">Rechercher</label>
      <input id="gq" type="text" placeholder="Rechercher un terme" value={q} onChange={(e) => setQ(e.target.value)} dir="auto" />
      {g.loading && !g.data ? <Loading /> : list.length === 0 ? <Empty>Aucun terme.</Empty> : (
        <div className="card"><ul className="list">
          {list.map((e) => editing?.id === e.id ? (
            <li key={e.id} className="stack">
              <input type="text" aria-label="Terme" value={editing.term} onChange={(x) => setEditing({ ...editing, term: x.target.value })} dir="auto" />
              <input type="text" aria-label="En arabe" lang="ar" dir="rtl" value={editing.arabic} onChange={(x) => setEditing({ ...editing, arabic: x.target.value })} />
              <textarea aria-label="Définition" rows={2} value={editing.definition} onChange={(x) => setEditing({ ...editing, definition: x.target.value })} dir="auto" />
              <div className="row end">
                <button onClick={() => setEditing(null)}>Annuler</button>
                <button className="primary" onClick={() => act(async () => { await api.patch(`/api/glossary/${e.id}`, editing); setEditing(null); })}>Enregistrer</button>
              </div>
            </li>
          ) : (
            <li key={e.id}>
              <div className="spread">
                <b dir="auto">{e.term}</b>
                {e.arabic && <span lang="ar" dir="rtl" style={{ fontSize: '1.3rem' }}>{e.arabic}</span>}
              </div>
              {e.definition && <div className="text" dir="auto">{e.definition}</div>}
              <div className="row end">
                <button className="small" onClick={() => setEditing(e)}>Modifier</button>
                <button className="small danger" onClick={() => { if (confirm(`Supprimer « ${e.term} » ?`)) act(() => api.del(`/api/glossary/${e.id}`)); }}>Supprimer</button>
              </div>
            </li>
          ))}
        </ul></div>
      )}
    </div>
  );
}

import { useState } from 'react';
import { api, type ChapterView, type Note, type Item, type DocumentInfo } from '../api.ts';
import { go } from '../router.ts';
import { useLoad, Loading, ErrorBox, Empty, Txt, SourceBadge, OriginBadge, TYPE_LABEL, SKILL_LABEL, formatDue, errorText } from '../components/ui.tsx';
import { ItemForm, SourceFields, sourceDraft, sourcePayload, type SourceDraft } from '../components/ItemForm.tsx';
import { ImportCsv, ImportJson } from '../components/Importers.tsx';

const TABS = [['supports', 'Supports'], ['fiches', 'Fiches'], ['questions', 'Questions'], ['carte', 'Carte mentale'], ['import', 'Importer']] as const;
const STATUS_BADGE: Record<DocumentInfo['extraction_status'], [string, string]> = {
  ok: ['Texte lu', 'ok'], partial: ['Lecture partielle', 'warn'], insufficient: ['Texte illisible', 'bad'], not_applicable: ['Image', ''],
};

export function Chapter({ id, tab }: { id: string; tab: string }) {
  const view = useLoad(() => api.get<ChapterView>(`/api/chapters/${id}`), [id]);
  const [err, setErr] = useState<string | null>(null);

  if (view.loading && !view.data) return <Loading />;
  if (!view.data) return <ErrorBox error={view.error} onRetry={view.reload} />;
  const v = view.data;

  async function act(fn: () => Promise<unknown>) {
    setErr(null);
    try { await fn(); await view.reload(); } catch (e) { setErr(errorText(e)); }
  }

  return (
    <div>
      <p className="muted" style={{ marginBottom: 4 }}><a href="#/library">Bibliothèque</a> › <span dir="auto">{v.chapter.subject.name}</span></p>
      <div className="spread">
        <h1 dir="auto">{v.chapter.name}</h1>
        <div className="row">
          <button className="small" onClick={() => { const n = prompt('Nouveau nom du chapitre', v.chapter.name); if (n?.trim()) act(() => api.patch(`/api/chapters/${id}`, { name: n })); }}>Renommer</button>
          <button className="small danger" onClick={() => { if (confirm('Supprimer ce chapitre, ses supports, fiches et questions ?')) act(async () => { await api.del(`/api/chapters/${id}`); go('/library'); }); }}>Supprimer</button>
        </div>
      </div>
      {v.items.length > 0 && (
        <button className="primary" style={{ marginBottom: 14 }} onClick={() => act(async () => {
          const s = await api.post<{ id: string | null }>('/api/review/sessions', { chapter_id: id, resume: false });
          if (s.id) go(`/review?session=${s.id}`); else setErr("Rien à réviser aujourd'hui dans ce chapitre.");
        })}>Réviser ce chapitre</button>
      )}
      <nav className="tabs" aria-label="Sections du chapitre">
        {TABS.map(([k, l]) => <a key={k} href={`#/chapter/${id}?tab=${k}`} aria-current={tab === k ? 'page' : undefined}>{l}{k === 'questions' ? ` (${v.items.length})` : k === 'fiches' ? ` (${v.notes.length})` : ''}</a>)}
      </nav>
      <ErrorBox error={err ?? view.error} />
      {tab === 'supports' && <Supports v={v} act={act} />}
      {tab === 'fiches' && <Notes v={v} reload={view.reload} act={act} />}
      {tab === 'questions' && <Questions v={v} reload={view.reload} act={act} />}
      {tab === 'carte' && <Maps v={v} act={act} />}
      {tab === 'import' && (
        <div className="stack">
          <ImportCsv chapterId={id} docs={v.documents} onDone={view.reload} />
          <ImportJson chapterId={id} docs={v.documents} onDone={view.reload} />
        </div>
      )}
    </div>
  );
}

type Act = (fn: () => Promise<unknown>) => Promise<void>;

function Supports({ v, act }: { v: ChapterView; act: Act }) {
  return (
    <div className="stack">
      <a className="btn" href="#/add">＋ Ajouter un support</a>
      {v.documents.length === 0 ? <Empty>Aucun support. Ajoutez un PDF ou collez le texte du cours.</Empty> : (
        <div className="card"><ul className="list">
          {v.documents.map((d) => {
            const [label, cls] = STATUS_BADGE[d.extraction_status];
            return (
              <li key={d.id}>
                <div className="spread">
                  <a href={`#/document/${d.id}`} dir="auto" style={{ fontWeight: 600 }}>{d.title}</a>
                  <span className={`badge ${cls}`}>{label}</span>
                </div>
                <small>{d.kind === 'pdf' ? `PDF · ${d.page_count} page(s)` : d.kind === 'text' ? 'Texte' : 'Image'} · {(d.size / 1024 / 1024).toFixed(1)} Mo</small>
                {d.extraction_note && <p className="muted" style={{ fontSize: '.92rem', marginTop: 4 }}>{d.extraction_note}</p>}
                <div className="row end"><button className="small danger" onClick={() => { if (confirm('Supprimer ce support ?')) act(() => api.del(`/api/documents/${d.id}`)); }}>Supprimer</button></div>
              </li>
            );
          })}
        </ul></div>
      )}
    </div>
  );
}

function Notes({ v, reload, act }: { v: ChapterView; reload: () => void; act: Act }) {
  const [editing, setEditing] = useState<string | null>(null);
  const [explain, setExplain] = useState<Record<string, string>>({});
  return (
    <div className="stack">
      <button onClick={() => act(async () => { const n = await api.post<Note>(`/api/chapters/${v.chapter.id}/notes`, { title: 'Nouvelle fiche', body: '' }); setEditing(n.id); })}>＋ Nouvelle fiche</button>
      {v.notes.length === 0 && <Empty>Aucune fiche. Rédigez l'essentiel du chapitre avec vos mots, ou importez des fiches préparées.</Empty>}
      {v.notes.map((n) => editing === n.id
        ? <NoteEditor key={n.id} note={n} docs={v.documents} onDone={() => { setEditing(null); reload(); }} />
        : (
          <article key={n.id} className="card">
            <div className="spread"><h2 dir="auto">{n.title}</h2><span className="row" style={{ gap: 6 }}><OriginBadge origin={n.origin} /><SourceBadge status={n.source_status} pages={n.source_pages} /></span></div>
            {n.body ? <Txt>{n.body}</Txt> : <p className="muted">Fiche vide.</p>}
            {n.source_excerpt && <blockquote className="muted text" dir="auto" style={{ borderInlineStart: '3px solid var(--line)', paddingInlineStart: 10, margin: '10px 0' }}>{n.source_excerpt}</blockquote>}
            {explain[n.id] && <div className="notice" role="status">{explain[n.id]}</div>}
            <div className="row end">
              <button className="small" onClick={() => act(async () => {
                const r = await api.post<{ available: boolean; message: string }>(`/api/notes/${n.id}/explain`, {});
                setExplain({ ...explain, [n.id]: r.message });
                reload();
              })}>Expliquer simplement</button>
              <button className="small" onClick={() => setEditing(n.id)}>Modifier</button>
              <button className="small danger" onClick={() => { if (confirm('Supprimer cette fiche ?')) act(() => api.del(`/api/notes/${n.id}`)); }}>Supprimer</button>
            </div>
          </article>
        ))}
    </div>
  );
}

function NoteEditor({ note, docs, onDone }: { note: Note; docs: DocumentInfo[]; onDone: () => void }) {
  const [title, setTitle] = useState(note.title);
  const [body, setBody] = useState(note.body);
  const [source, setSource] = useState<SourceDraft>(sourceDraft(note));
  const [err, setErr] = useState<string | null>(null);
  return (
    <form className="card stack" onSubmit={async (e) => {
      e.preventDefault();
      try { await api.patch(`/api/notes/${note.id}`, { title, body, source: sourcePayload(source) }); onDone(); } catch (e2) { setErr(errorText(e2)); }
    }}>
      <div><label htmlFor={`nt-${note.id}`}>Titre</label><input id={`nt-${note.id}`} type="text" value={title} onChange={(e) => setTitle(e.target.value)} dir="auto" /></div>
      <div><label htmlFor={`nb-${note.id}`}>Contenu</label><textarea id={`nb-${note.id}`} rows={12} value={body} onChange={(e) => setBody(e.target.value)} dir="auto" />
        <small>Gardez les conditions, exceptions et divergences d'avis du cours.</small></div>
      <SourceFields docs={docs} value={source} onChange={setSource} idp={`note-${note.id}`} />
      {err && <div className="notice bad" role="alert">{err}</div>}
      <div className="row end"><button type="button" onClick={onDone}>Annuler</button><button className="primary">Enregistrer</button></div>
    </form>
  );
}

function Questions({ v, reload, act }: { v: ChapterView; reload: () => void; act: Act }) {
  const [adding, setAdding] = useState(v.items.length === 0);
  const [editing, setEditing] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | Item['type']>('all');
  const items = v.items.filter((i) => filter === 'all' || i.type === filter);
  return (
    <div className="stack">
      {adding ? (
        <div className="card"><h2>Nouvelle question</h2><ItemForm chapterId={v.chapter.id} docs={v.documents} onDone={() => reload()} onCancel={() => setAdding(false)} /></div>
      ) : <button onClick={() => setAdding(true)}>＋ Nouvelle question</button>}
      {v.items.length > 0 && (
        <div className="row" role="group" aria-label="Filtrer">
          {(['all', 'flashcard', 'mcq', 'open'] as const).map((k) => (
            <button key={k} className="small" aria-pressed={filter === k} onClick={() => setFilter(k)} style={filter === k ? { borderColor: 'var(--primary)', color: 'var(--primary)' } : undefined}>
              {k === 'all' ? 'Tout' : TYPE_LABEL[k]}
            </button>
          ))}
        </div>
      )}
      {v.items.length === 0 && !adding && <Empty>Aucune question.</Empty>}
      <div className="card" hidden={items.length === 0}><ul className="list">
        {items.map((it) => (
          <li key={it.id}>
            {editing === it.id ? (
              <ItemForm chapterId={v.chapter.id} docs={v.documents} item={it} onDone={() => { setEditing(null); reload(); }} onCancel={() => setEditing(null)} />
            ) : (
              <>
                <div className="row" style={{ gap: 6, marginBottom: 4 }}>
                  <span className="badge">{TYPE_LABEL[it.type]}</span>
                  {it.skill && <span className="badge">{SKILL_LABEL[it.skill]}</span>}
                  <OriginBadge origin={it.origin} />
                  <SourceBadge status={it.source_status} pages={it.source_pages} />
                  <span className="badge">{it.suspended ? 'Suspendue' : formatDue(it.due, it.state)}</span>
                </div>
                <Txt className="">{it.prompt}</Txt>
                <details><summary>Voir la réponse</summary>
                  {it.type === 'mcq'
                    ? <ul>{it.choices?.map((c, i) => <li key={i} dir="auto">{c.correct ? '✓ ' : ''}{c.text}</li>)}</ul>
                    : <Txt>{it.answer}</Txt>}
                  {it.explanation && <Txt className="muted">{it.explanation}</Txt>}
                </details>
                <div className="row end">
                  <button className="small" onClick={() => setEditing(it.id)}>Modifier</button>
                  <button className="small" onClick={() => act(() => api.patch(`/api/items/${it.id}`, { suspended: !it.suspended }))}>{it.suspended ? 'Réactiver' : 'Suspendre'}</button>
                  <button className="small danger" onClick={() => { if (confirm('Supprimer cette question et son historique ?')) act(() => api.del(`/api/items/${it.id}`)); }}>Supprimer</button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul></div>
    </div>
  );
}

function Maps({ v, act }: { v: ChapterView; act: Act }) {
  const images = v.documents.filter((d) => d.kind === 'image');
  return (
    <div className="stack">
      <button onClick={() => act(async () => { const m = await api.post<{ id: string }>(`/api/chapters/${v.chapter.id}/mindmaps`, {}); go(`/mindmap/${m.id}`); })}>＋ Nouvelle carte mentale</button>
      {v.mindmaps.length === 0 && <Empty>Aucune carte interactive. Créez-la ici, ou importez une structure de nœuds (JSON).</Empty>}
      {v.mindmaps.length > 0 && (
        <div className="card"><ul className="list">
          {v.mindmaps.map((m) => (
            <li key={m.id} className="spread"><a href={`#/mindmap/${m.id}`} dir="auto" style={{ fontWeight: 600 }}>{m.title}</a><SourceBadge status={m.source_status} /></li>
          ))}
        </ul></div>
      )}
      {images.length > 0 && (
        <section className="card">
          <h2>Images consultables</h2>
          <p className="muted">Ces images (par exemple une carte téléchargée depuis NotebookLM) restent des ressources à regarder ; elles ne sont pas converties en carte interactive.</p>
          <ul className="list">{images.map((d) => <li key={d.id}><a href={`#/document/${d.id}`} dir="auto">{d.title}</a></li>)}</ul>
        </section>
      )}
    </div>
  );
}

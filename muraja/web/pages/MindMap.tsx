import { useEffect, useMemo, useState } from 'react';
import { api, type ChapterView, type MindNode } from '../api.ts';
import { useLoad, Loading, ErrorBox, Txt, SourceBadge, TYPE_LABEL, errorText } from '../components/ui.tsx';
import { go } from '../router.ts';

interface MapView {
  mindmap: { id: string; chapter_id: string; title: string; origin: string; source_status: 'verified' | 'to_verify' | 'personal'; nodes: MindNode[] };
  items: Array<{ id: string; type: 'flashcard' | 'mcq' | 'open'; prompt: string; answer: string }>;
}

const W = 170, H = 64, GX = 210, GY = 78, PAD = 16;

/** Tidy tree layout: leaves on consecutive rows, parents centred on their children. */
function layout(nodes: MindNode[]) {
  const kids = new Map<string, MindNode[]>();
  nodes.forEach((n) => { if (n.parentId) kids.set(n.parentId, [...(kids.get(n.parentId) ?? []), n]); });
  const root = nodes.find((n) => !n.parentId)!;
  const pos = new Map<string, { x: number; y: number }>();
  let row = 0, maxDepth = 0;
  function place(n: MindNode, depth: number): number {
    maxDepth = Math.max(maxDepth, depth);
    const ch = kids.get(n.id) ?? [];
    const y = ch.length ? ch.map((c) => place(c, depth + 1)).reduce((a, b) => a + b, 0) / ch.length : row++ * GY;
    pos.set(n.id, { x: PAD + depth * GX, y: PAD + y });
    return y;
  }
  if (root) place(root, 0);
  return { pos, kids, width: PAD * 2 + maxDepth * GX + W, height: PAD * 2 + Math.max(0, row - 1) * GY + H };
}

let counter = 0;
const newId = () => `n${Date.now().toString(36)}${(counter++).toString(36)}`;

export function MindMapPage({ id }: { id: string }) {
  const m = useLoad(() => api.get<MapView>(`/api/mindmaps/${id}`), [id]);
  const [nodes, setNodes] = useState<MindNode[] | null>(null);
  const [title, setTitle] = useState('');
  const [sel, setSel] = useState<string>('root');
  const [dirty, setDirty] = useState(false);
  const [view, setView] = useState<'map' | 'list'>('map');
  const [quiz, setQuiz] = useState(false);
  const [shown, setShown] = useState<Set<string>>(new Set());
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad'; text: string } | null>(null);
  const [chapter, setChapter] = useState<ChapterView | null>(null);

  useEffect(() => {
    if (!m.data) return;
    setNodes(m.data.mindmap.nodes);
    setTitle(m.data.mindmap.title);
    setSel(m.data.mindmap.nodes.find((n) => !n.parentId)?.id ?? '');
    api.get<ChapterView>(`/api/chapters/${m.data.mindmap.chapter_id}`).then(setChapter, () => setChapter(null));
  }, [m.data]);

  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => { if (dirty) e.preventDefault(); };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [dirty]);

  const lay = useMemo(() => (nodes ? layout(nodes) : null), [nodes]);
  if (m.loading && !m.data) return <Loading />;
  if (!m.data || !nodes || !lay) return <ErrorBox error={m.error} onRetry={m.reload} />;
  const mm = m.data.mindmap;
  const node = nodes.find((n) => n.id === sel);
  const items = chapter?.items ?? [];

  const update = (next: MindNode[]) => { setNodes(next); setDirty(true); setMsg(null); };
  const patch = (nid: string, p: Partial<MindNode>) => update(nodes.map((n) => (n.id === nid ? { ...n, ...p } : n)));
  function addChild(parentId: string) {
    const n: MindNode = { id: newId(), label: 'Nouvelle idée', parentId, note: '', itemIds: [] };
    update([...nodes!, n]);
    setSel(n.id);
  }
  function remove(nid: string) {
    const doomed = new Set([nid]);
    let grew = true;
    while (grew) {
      grew = false;
      nodes!.forEach((n) => { if (n.parentId && doomed.has(n.parentId) && !doomed.has(n.id)) { doomed.add(n.id); grew = true; } });
    }
    const parent = nodes!.find((n) => n.id === nid)?.parentId;
    update(nodes!.filter((n) => !doomed.has(n.id)));
    setSel(parent ?? '');
  }
  async function save() {
    try {
      const r = await api.put<{ nodes: MindNode[] }>(`/api/mindmaps/${id}`, { title, nodes });
      setNodes(r.nodes);
      setDirty(false);
      setMsg({ kind: 'ok', text: 'Carte enregistrée.' });
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); }
  }
  const hidden = (n: MindNode) => quiz && n.parentId !== null && !shown.has(n.id);
  const onNode = (n: MindNode) => {
    if (hidden(n)) setShown(new Set([...shown, n.id]));
    setSel(n.id);
  };

  function ListTree({ parentId }: { parentId: string | null }) {
    const list = parentId === null ? nodes!.filter((n) => !n.parentId) : lay!.kids.get(parentId) ?? [];
    if (!list.length) return null;
    return (
      <ul className={parentId === null ? 'tree' : undefined} role={parentId === null ? 'tree' : 'group'}>
        {list.map((n) => (
          <li key={n.id} role="treeitem" aria-expanded={(lay!.kids.get(n.id) ?? []).length ? true : undefined} aria-selected={sel === n.id}>
            <button onClick={() => onNode(n)} aria-current={sel === n.id} dir="auto" style={sel === n.id ? { borderColor: 'var(--accent)' } : undefined}>
              {hidden(n) ? '… (masqué — toucher pour révéler)' : n.label}
            </button>
            <ListTree parentId={n.id} />
          </li>
        ))}
      </ul>
    );
  }

  return (
    <div className="stack">
      <p className="muted" style={{ marginBottom: 0 }}>
        <a href={`#/chapter/${mm.chapter_id}?tab=carte`} onClick={(e) => { if (dirty && !confirm('Quitter sans enregistrer ?')) e.preventDefault(); }}>← Retour au chapitre</a>
      </p>
      <div className="spread">
        <label htmlFor="mt" className="sr-only">Titre de la carte</label>
        <input id="mt" type="text" value={title} onChange={(e) => { setTitle(e.target.value); setDirty(true); }} dir="auto" style={{ fontSize: '1.3rem', fontWeight: 700, flex: 1, minWidth: 200 }} />
        <SourceBadge status={mm.source_status} />
      </div>
      <div className="row">
        <button className="small" aria-pressed={view === 'map'} onClick={() => setView('map')}>Carte</button>
        <button className="small" aria-pressed={view === 'list'} onClick={() => setView('list')}>Liste</button>
        <label className="check" style={{ marginInlineStart: 8 }}>
          <input type="checkbox" checked={quiz} onChange={(e) => { setQuiz(e.target.checked); setShown(new Set()); }} /> S'entraîner : masquer les branches
        </label>
        <span style={{ flex: 1 }} />
        {dirty && <span className="badge warn">Non enregistrée</span>}
        <button className="primary small" onClick={save} disabled={!dirty}>Enregistrer</button>
      </div>
      {quiz && <div className="notice">Rappelez-vous chaque idée avant de toucher la case pour la révéler.</div>}
      {msg && <div className={`notice ${msg.kind}`} role="status">{msg.text}</div>}

      {view === 'map' ? (
        <div className="mm-wrap">
          <div className="mm-canvas" style={{ width: lay.width, height: lay.height }}>
            <svg width={lay.width} height={lay.height} aria-hidden="true">
              {nodes.filter((n) => n.parentId).map((n) => {
                const a = lay.pos.get(n.parentId!)!, b = lay.pos.get(n.id)!;
                const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2, mx = (x1 + x2) / 2;
                return <path key={n.id} d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`} fill="none" stroke="var(--line)" strokeWidth="2" />;
              })}
            </svg>
            {nodes.map((n) => {
              const p = lay.pos.get(n.id)!;
              return (
                <button key={n.id} className={`mm-node ${n.parentId ? '' : 'root'} ${hidden(n) ? 'hidden-label' : ''}`}
                  style={{ left: p.x, top: p.y, height: H }} aria-current={sel === n.id} onClick={() => onNode(n)} dir="auto"
                  aria-label={hidden(n) ? 'Idée masquée, toucher pour révéler' : n.label}>
                  {n.label.length > 60 ? n.label.slice(0, 58) + '…' : n.label}
                  {(n.note || n.itemIds.length > 0) && !hidden(n) && <span aria-hidden="true"> •</span>}
                </button>
              );
            })}
          </div>
        </div>
      ) : <div className="card"><ListTree parentId={null} /></div>}

      {node && !hidden(node) && (
        <section className="card stack" aria-label="Idée sélectionnée">
          <div>
            <label htmlFor="nl">Idée</label>
            <input id="nl" type="text" value={node.label} onChange={(e) => patch(node.id, { label: e.target.value })} dir="auto" />
          </div>
          <div>
            <label htmlFor="nn">Explication</label>
            <textarea id="nn" rows={3} value={node.note} onChange={(e) => patch(node.id, { note: e.target.value })} dir="auto" placeholder="Expliquez cette idée simplement, avec ses conditions et exceptions." />
          </div>
          <div>
            <h3>Questions du cours liées</h3>
            {node.itemIds.length === 0 && <p className="muted">Aucune.</p>}
            <ul className="list">
              {node.itemIds.map((iid) => {
                const it = items.find((x) => x.id === iid) ?? m.data!.items.find((x) => x.id === iid);
                return it ? (
                  <li key={iid}>
                    <span className="badge">{TYPE_LABEL[it.type]}</span> <Txt as="span">{it.prompt}</Txt>
                    {it.answer && <details><summary>Réponse</summary><Txt>{it.answer}</Txt></details>}
                    <button className="small ghost" onClick={() => patch(node.id, { itemIds: node.itemIds.filter((x) => x !== iid) })}>Retirer le lien</button>
                  </li>
                ) : null;
              })}
            </ul>
            {items.length > 0 && (
              <select aria-label="Lier une question" value="" onChange={(e) => { if (e.target.value) patch(node.id, { itemIds: [...node.itemIds, e.target.value] }); }}>
                <option value="">＋ Lier une question du chapitre…</option>
                {items.filter((it) => !node.itemIds.includes(it.id)).map((it) => <option key={it.id} value={it.id}>{it.prompt.slice(0, 80)}</option>)}
              </select>
            )}
          </div>
          <div className="row end">
            <button onClick={() => addChild(node.id)}>＋ Idée secondaire</button>
            {node.parentId && <button onClick={() => addChild(node.parentId!)}>＋ Idée au même niveau</button>}
            {node.parentId && <button className="danger" onClick={() => { if (confirm('Supprimer cette idée et ses sous-idées ?')) remove(node.id); }}>Supprimer</button>}
          </div>
        </section>
      )}
      <div className="row end">
        <button className="small danger" onClick={async () => { if (confirm('Supprimer toute la carte ?')) { await api.del(`/api/mindmaps/${id}`); go(`/chapter/${mm.chapter_id}?tab=carte`); } }}>Supprimer la carte</button>
      </div>
    </div>
  );
}

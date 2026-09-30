import { useState, type FormEvent } from 'react';
import { api, type Item, type Choice, type DocumentInfo } from '../api.ts';
import { errorText } from './ui.tsx';

export interface SourceDraft { document_id: string; pages: string; excerpt: string }

export function SourceFields({ docs, value, onChange, idp }: { docs: DocumentInfo[]; value: SourceDraft; onChange: (v: SourceDraft) => void; idp: string }) {
  const readable = docs.filter((d) => d.kind !== 'image');
  return (
    <details className="field" open={!!(value.document_id || value.excerpt)}>
      <summary>Source dans le cours (facultatif)</summary>
      <div className="stack" style={{ marginTop: 8 }}>
        <div>
          <label htmlFor={`${idp}-doc`}>Document</label>
          <select id={`${idp}-doc`} value={value.document_id} onChange={(e) => onChange({ ...value, document_id: e.target.value })}>
            <option value="">Aucun</option>
            {readable.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor={`${idp}-pages`}>Page(s)</label>
          <input id={`${idp}-pages`} type="text" inputMode="numeric" placeholder="ex. 3, 4" value={value.pages} onChange={(e) => onChange({ ...value, pages: e.target.value })} />
        </div>
        <div>
          <label htmlFor={`${idp}-ex`}>Extrait exact du cours</label>
          <textarea id={`${idp}-ex`} rows={2} value={value.excerpt} onChange={(e) => onChange({ ...value, excerpt: e.target.value })} dir="auto" />
          <small>La source est marquée « vérifiée » seulement si cet extrait est retrouvé tel quel sur ces pages.</small>
        </div>
      </div>
    </details>
  );
}

export function sourcePayload(s: SourceDraft) {
  const pages = s.pages.split(/[^0-9]+/).filter(Boolean).map(Number);
  if (!s.document_id && !s.excerpt.trim() && !pages.length) return null;
  return { document_id: s.document_id || null, pages, excerpt: s.excerpt.trim() || null };
}

export function sourceDraft(x?: { source_document_id: string | null; source_pages: number[] | null; source_excerpt: string | null }): SourceDraft {
  return { document_id: x?.source_document_id ?? '', pages: x?.source_pages?.join(', ') ?? '', excerpt: x?.source_excerpt ?? '' };
}

const emptyChoices = (): Choice[] => [
  { text: '', correct: true, why: '' }, { text: '', correct: false, why: '' }, { text: '', correct: false, why: '' },
];

export function ItemForm({ chapterId, docs, item, initial, onDone, onCancel }: {
  chapterId: string; docs: DocumentInfo[]; item?: Item; initial?: Partial<{ prompt: string; source: SourceDraft }>;
  onDone: (it: Item) => void; onCancel?: () => void;
}) {
  const [type, setType] = useState<Item['type']>(item?.type ?? 'flashcard');
  const [prompt, setPrompt] = useState(item?.prompt ?? initial?.prompt ?? '');
  const [answer, setAnswer] = useState(item?.answer ?? '');
  const [explanation, setExplanation] = useState(item?.explanation ?? '');
  const [skill, setSkill] = useState(item?.skill ?? '');
  const [choices, setChoices] = useState<Choice[]>(item?.choices ?? emptyChoices());
  const [source, setSource] = useState<SourceDraft>(item ? sourceDraft(item) : initial?.source ?? { document_id: '', pages: '', excerpt: '' });
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const idp = item?.id ?? 'new';

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    const body = {
      type, prompt, answer, explanation, skill: skill || null, source: sourcePayload(source),
      choices: type === 'mcq' ? choices.filter((c) => c.text.trim()) : null,
    };
    try {
      const it = item ? await api.patch<Item>(`/api/items/${item.id}`, body) : await api.post<Item>(`/api/chapters/${chapterId}/items`, body);
      onDone(it);
      if (!item) { setPrompt(''); setAnswer(''); setExplanation(''); setChoices(emptyChoices()); }
    } catch (e2) { setErr(errorText(e2)); } finally { setBusy(false); }
  }

  return (
    <form onSubmit={submit} className="stack" aria-label={item ? 'Modifier la question' : 'Nouvelle question'}>
      {!item && (
        <div className="row" role="radiogroup" aria-label="Type">
          {([['flashcard', 'Flashcard'], ['mcq', 'QCM'], ['open', 'Question ouverte']] as const).map(([k, l]) => (
            <label key={k} className="check" style={{ marginRight: 10 }}><input type="radio" name={`type-${idp}`} checked={type === k} onChange={() => setType(k)} /> {l}</label>
          ))}
        </div>
      )}
      <div>
        <label htmlFor={`${idp}-q`}>Question <small>(une seule question précise)</small></label>
        <textarea id={`${idp}-q`} rows={2} value={prompt} onChange={(e) => setPrompt(e.target.value)} dir="auto" required />
      </div>
      {type !== 'mcq' ? (
        <div>
          <label htmlFor={`${idp}-a`}>{type === 'open' ? 'Réponse attendue' : 'Réponse (cachée pendant la révision)'}</label>
          <textarea id={`${idp}-a`} rows={2} value={answer} onChange={(e) => setAnswer(e.target.value)} dir="auto" required />
        </div>
      ) : (
        <fieldset style={{ border: 0, padding: 0 }}>
          <legend style={{ fontWeight: 600 }}>Propositions — cochez la bonne réponse</legend>
          {choices.map((c, i) => (
            <div key={i} className="card" style={{ padding: 10, marginBottom: 8 }}>
              <div className="row">
                <input type="radio" name={`ok-${idp}`} aria-label={`Proposition ${i + 1} correcte`} checked={c.correct} onChange={() => setChoices(choices.map((x, j) => ({ ...x, correct: j === i })))} style={{ width: 22, height: 22 }} />
                <input type="text" aria-label={`Proposition ${i + 1}`} value={c.text} onChange={(e) => setChoices(choices.map((x, j) => (j === i ? { ...x, text: e.target.value } : x)))} style={{ flex: 1 }} dir="auto" />
                {choices.length > 2 && <button type="button" className="small ghost" onClick={() => setChoices(choices.filter((_, j) => j !== i))} aria-label={`Retirer la proposition ${i + 1}`}>✕</button>}
              </div>
              <input type="text" aria-label={`Pourquoi (proposition ${i + 1})`} placeholder="Pourquoi est-elle juste ou fausse ?" value={c.why} onChange={(e) => setChoices(choices.map((x, j) => (j === i ? { ...x, why: e.target.value } : x)))} style={{ marginTop: 6 }} dir="auto" />
            </div>
          ))}
          {choices.length < 8 && <button type="button" className="small" onClick={() => setChoices([...choices, { text: '', correct: false, why: '' }])}>＋ Proposition</button>}
        </fieldset>
      )}
      <div>
        <label htmlFor={`${idp}-x`}>Explication / correction <small>(facultatif)</small></label>
        <textarea id={`${idp}-x`} rows={2} value={explanation} onChange={(e) => setExplanation(e.target.value)} dir="auto" />
      </div>
      <div>
        <label htmlFor={`${idp}-s`}>Compétence visée</label>
        <select id={`${idp}-s`} value={skill} onChange={(e) => setSkill(e.target.value)}>
          <option value="">—</option><option value="definition">Définition</option><option value="distinction">Distinction</option><option value="application">Application</option>
        </select>
      </div>
      <SourceFields docs={docs} value={source} onChange={setSource} idp={idp} />
      {err && <div className="notice bad" role="alert">{err}</div>}
      <div className="row end">
        {onCancel && <button type="button" onClick={onCancel}>Annuler</button>}
        <button className="primary" disabled={busy}>{item ? 'Enregistrer' : 'Ajouter'}</button>
      </div>
    </form>
  );
}

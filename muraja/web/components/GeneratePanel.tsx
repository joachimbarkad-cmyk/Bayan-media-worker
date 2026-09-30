import { useState } from 'react';
import { api } from '../api.ts';
import { errorText, Txt, SKILL_LABEL } from './ui.tsx';

type Src = { pages: number[]; excerpt: string };
interface Preview {
  provider: string; model: string; skipped_pages: number[];
  flashcards: Array<{ question: string; answer: string; skill: string } & Src>;
  mcq: Array<{ question: string; choices: Array<{ text: string; correct: boolean; why: string }>; explanation: string; skill: string } & Src>;
  open: Array<{ question: string; answer: string } & Src>;
}

/** Generates questions from selected pages with the learner's own AI key, then lets them pick what to keep. */
export function GeneratePanel({ docId, pageCount, onSaved }: { docId: string; pageCount: number; onSaved: (n: number) => void }) {
  const [from, setFrom] = useState(1);
  const [to, setTo] = useState(Math.min(pageCount, 5));
  const [preview, setPreview] = useState<Preview | null>(null);
  const [keep, setKeep] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad' | 'warn'; text: string } | null>(null);

  async function generate() {
    setBusy(true); setMsg(null); setPreview(null);
    try {
      const p = await api.post<Preview>(`/api/documents/${docId}/generate`, { from_page: from, to_page: to });
      const k: Record<string, boolean> = {};
      p.flashcards.forEach((_, i) => { k[`f${i}`] = true; });
      p.mcq.forEach((_, i) => { k[`m${i}`] = true; });
      p.open.forEach((_, i) => { k[`o${i}`] = true; });
      setKeep(k); setPreview(p);
      if (p.skipped_pages.length) setMsg({ kind: 'warn', text: `Pages ignorées (sans texte lisible) : ${p.skipped_pages.join(', ')}.` });
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); } finally { setBusy(false); }
  }

  async function save() {
    if (!preview) return;
    setBusy(true);
    try {
      const r = await api.post<{ count: number; verified: number }>(`/api/documents/${docId}/generated`, {
        flashcards: preview.flashcards.filter((_, i) => keep[`f${i}`]),
        mcq: preview.mcq.filter((_, i) => keep[`m${i}`]),
        open: preview.open.filter((_, i) => keep[`o${i}`]),
      });
      setPreview(null);
      setMsg({ kind: 'ok', text: `${r.count} question(s) ajoutée(s), dont ${r.verified} avec une source retrouvée dans le cours. Les autres sont marquées « à vérifier ».` });
      onSaved(r.count);
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); } finally { setBusy(false); }
  }

  const Row = ({ id, children, src }: { id: string; children: React.ReactNode; src: Src }) => (
    <li>
      <label className="check" style={{ alignItems: 'flex-start' }}>
        <input type="checkbox" checked={!!keep[id]} onChange={(e) => setKeep({ ...keep, [id]: e.target.checked })} />
        <div style={{ flex: 1 }}>{children}{src.pages.length > 0 && <small> · p. {src.pages.join(', ')}</small>}{src.excerpt && <Txt className="muted">{`« ${src.excerpt} »`}</Txt>}</div>
      </label>
    </li>
  );

  return (
    <details className="card">
      <summary><b>Générer des questions avec l'IA</b></summary>
      <div className="stack" style={{ marginTop: 10 }}>
        <p className="muted">Utilise l'IA connectée dans Réglages. Le résultat est un brouillon : relisez, décochez ce qui ne convient pas, puis enregistrez.</p>
        {pageCount > 1 && (
          <div className="row">
            <label htmlFor="g-from">Pages</label>
            <input id="g-from" type="number" min={1} max={pageCount} value={from} onChange={(e) => setFrom(Number(e.target.value))} style={{ width: 90 }} />
            <label htmlFor="g-to">à</label>
            <input id="g-to" type="number" min={from} max={pageCount} value={to} onChange={(e) => setTo(Number(e.target.value))} style={{ width: 90 }} />
          </div>
        )}
        <button className="primary" disabled={busy} onClick={generate}>{busy && !preview ? 'Génération…' : 'Générer'}</button>
        {msg && <div className={`notice ${msg.kind}`} role="status">{msg.text}</div>}
        {preview && (
          <>
            <small className="muted">Généré par {preview.provider} ({preview.model}) — à vérifier.</small>
            <ul className="list">
              {preview.flashcards.map((f, i) => <Row key={`f${i}`} id={`f${i}`} src={f}><span className="badge">Flashcard · {SKILL_LABEL[f.skill]}</span> <Txt>{f.question}</Txt><Txt className="muted">{`→ ${f.answer}`}</Txt></Row>)}
              {preview.mcq.map((q, i) => <Row key={`m${i}`} id={`m${i}`} src={q}><span className="badge">QCM</span> <Txt>{q.question}</Txt><ul>{q.choices.map((c, j) => <li key={j} dir="auto">{c.correct ? '✓ ' : ''}{c.text}</li>)}</ul></Row>)}
              {preview.open.map((o, i) => <Row key={`o${i}`} id={`o${i}`} src={o}><span className="badge">Question ouverte</span> <Txt>{o.question}</Txt></Row>)}
            </ul>
            <button className="primary" disabled={busy || !Object.values(keep).some(Boolean)} onClick={save}>Enregistrer la sélection</button>
          </>
        )}
      </div>
    </details>
  );
}

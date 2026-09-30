import { useEffect, useMemo, useState } from 'react';
import { api } from '../api.ts';
import { go } from '../router.ts';
import { Loading, ErrorBox, Txt, SourceBadge, errorText, TYPE_LABEL, SKILL_LABEL } from '../components/ui.tsx';

interface Presented {
  id: string; type: 'flashcard' | 'mcq' | 'open'; prompt: string; skill: string | null; version: number; state: number;
  source_status: 'verified' | 'to_verify' | 'personal'; choices?: Array<{ index: number; text: string }>;
}
interface Current { session: { id: string; position: number; total: number; finished: boolean }; item: Presented | null }
interface Feedback {
  rating: number; correct: boolean | null; answer: string; explanation: string; next_due: number;
  choices: Array<{ index: number; text: string; correct: boolean; why: string }> | null;
  source: { document_id: string | null; pages: number[] | null; excerpt: string | null; status: 'verified' | 'to_verify' | 'personal' };
  session: { position: number; total: number } | null;
}

const GRADES = [
  [1, 'Oublié', 'je ne savais pas'], [2, 'Difficile', 'avec effort'], [3, 'Bien', 'je savais'], [4, 'Facile', 'immédiat'],
] as const;

function nextLabel(ms: number) {
  const diff = ms - Date.now();
  if (diff < 3600_000) return `dans ${Math.max(1, Math.round(diff / 60_000))} min`;
  if (diff < 86400_000) return `dans ${Math.round(diff / 3600_000)} h`;
  const days = Math.round(diff / 86400_000);
  return `dans ${days} jour${days > 1 ? 's' : ''}`;
}

export function Review({ chapterId: _c }: { chapterId: string | null }) {
  const sessionId = new URLSearchParams(window.location.hash.split('?')[1] ?? '').get('session');
  const [cur, setCur] = useState<Current | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [picked, setPicked] = useState<number | null>(null);
  const [hesitated, setHesitated] = useState(false);
  const [response, setResponse] = useState('');
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(0);
  // One review id per presentation: a double click or a retry is recognised by the server.
  const reviewId = useMemo(() => crypto.randomUUID(), [cur?.item?.id, cur?.session.position]);

  async function load() {
    if (!sessionId) return;
    setError(null);
    try {
      const c = await api.get<Current>(`/api/review/sessions/${sessionId}`);
      setCur(c); setRevealed(false); setPicked(null); setHesitated(false); setResponse(''); setFeedback(null);
    } catch (e) { setError(errorText(e)); }
  }
  useEffect(() => { load(); }, [sessionId]);

  async function submit(extra: { rating?: number; choice_index?: number }) {
    if (!cur?.item || busy) return;
    setBusy(true);
    setError(null);
    try {
      const f = await api.post<Feedback>('/api/review/answer', {
        session_id: cur.session.id, item_id: cur.item.id, review_id: reviewId, expected_version: cur.item.version,
        hesitated, response: response || undefined, ...extra,
      });
      setDone((d) => d + 1);
      if (cur.item.type === 'mcq') setFeedback(f);
      else await load();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!cur?.item || (e.target as HTMLElement)?.tagName === 'TEXTAREA') return;
      if (cur.item.type === 'flashcard' && !revealed && (e.key === ' ' || e.key === 'Enter')) { e.preventDefault(); setRevealed(true); }
      else if (revealed && cur.item.type !== 'mcq' && ['1', '2', '3', '4'].includes(e.key)) submit({ rating: Number(e.key) });
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  if (!sessionId) return <p>Aucune séance. <a href="#/">Retour à l'accueil</a></p>;
  if (!cur) return error ? <ErrorBox error={error} onRetry={load} /> : <Loading />;
  const { session, item } = cur;
  const pct = session.total ? Math.round((session.position / session.total) * 100) : 100;

  if (!item) {
    return (
      <div className="card hero stack">
        <h1>Séance terminée</h1>
        <p>{done > 0 ? `${done} réponse(s) enregistrée(s).` : 'Tout est à jour.'} Les prochaines révisions sont planifiées.</p>
        <button className="primary big" onClick={() => go('/')}>Retour à l'accueil</button>
        <a href="#/progress">Voir mes progrès</a>
      </div>
    );
  }

  return (
    <div>
      <div className="spread">
        <span className="muted">{session.position + 1} / {session.total}</span>
        <button className="small ghost" onClick={() => go('/')}>Interrompre</button>
      </div>
      <div className="progressbar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Avancement de la séance"><span style={{ width: `${pct}%` }} /></div>
      <ErrorBox error={error} onRetry={load} />
      <article className="card review-card" aria-live="polite">
        <div className="row" style={{ gap: 6 }}>
          <span className="badge">{TYPE_LABEL[item.type]}</span>
          {item.skill && <span className="badge">{SKILL_LABEL[item.skill]}</span>}
          {item.state === 0 && <span className="badge">Nouvelle</span>}
          {item.source_status === 'to_verify' && <SourceBadge status="to_verify" />}
        </div>
        <Txt className="prompt">{item.prompt}</Txt>

        {item.type === 'flashcard' && (!revealed
          ? <button className="primary big" onClick={() => setRevealed(true)} autoFocus>Afficher la réponse</button>
          : <RevealedAnswer itemId={item.id} sessionId={session.id} busy={busy} onGrade={(r) => submit({ rating: r })} />)}

        {item.type === 'open' && (!revealed ? (
          <div className="stack">
            <label htmlFor="own">Votre réponse, sans regarder le cours</label>
            <textarea id="own" rows={4} value={response} onChange={(e) => setResponse(e.target.value)} dir="auto" autoFocus />
            <button className="primary big" onClick={() => setRevealed(true)}>Comparer avec la réponse attendue</button>
          </div>
        ) : (
          <>
            {response && <div className="notice"><small>Votre réponse</small><Txt>{response}</Txt></div>}
            <RevealedAnswer itemId={item.id} sessionId={session.id} busy={busy} onGrade={(r) => submit({ rating: r })} compare />
          </>
        ))}

        {item.type === 'mcq' && (
          <div className="stack">
            <div className="choices" role="group" aria-label="Propositions">
              {(feedback?.choices
                ? item.choices!.map((c) => feedback.choices!.find((f) => f.index === c.index)!)
                : item.choices!.map((c) => ({ ...c, correct: false, why: '' }))
              ).map((c) => {
                const cls = feedback ? (c.correct ? 'right' : picked === c.index ? 'wrong' : '') : '';
                return (
                  <div key={c.index}>
                    <button className={`choice ${cls}`} style={{ width: '100%' }} aria-pressed={picked === c.index} disabled={!!feedback} onClick={() => setPicked(c.index)} dir="auto">
                      {feedback && (c.correct ? '✓ ' : picked === c.index ? '✗ ' : '')}{c.text}
                    </button>
                    {feedback && c.why && <div className="why text" dir="auto">{c.why}</div>}
                  </div>
                );
              })}
            </div>
            {!feedback ? (
              <>
                <label className="check"><input type="checkbox" checked={hesitated} onChange={(e) => setHesitated(e.target.checked)} /> J'ai hésité</label>
                <button className="primary big" disabled={picked == null || busy} onClick={() => submit({ choice_index: picked! })}>Valider</button>
              </>
            ) : (
              <>
                <div className={`notice ${feedback.correct ? 'ok' : 'bad'}`} role="status">
                  <b>{feedback.correct ? 'Bonne réponse.' : 'Ce n’est pas la bonne réponse.'}</b> Prochaine fois : {nextLabel(feedback.next_due)}.
                  {feedback.correct && <div><small>Reconnaître la bonne proposition ne suffit pas toujours : essayez de la reformuler sans les choix.</small></div>}
                </div>
                {feedback.explanation && <Txt>{feedback.explanation}</Txt>}
                <SourceLine source={feedback.source} />
                <button className="primary big" onClick={load} autoFocus>Continuer</button>
              </>
            )}
          </div>
        )}
      </article>
    </div>
  );
}

function SourceLine({ source }: { source: Feedback['source'] }) {
  if (source.status === 'personal') return null;
  return (
    <p className="muted" style={{ fontSize: '.9rem' }}>
      <SourceBadge status={source.status} pages={source.pages} />{' '}
      {source.document_id && <a href={`#/document/${source.document_id}`}>Relire dans le cours</a>}
      {source.excerpt && <span className="text" dir="auto"> — « {source.excerpt} »</span>}
    </p>
  );
}

/** Loads the answer only after the learner chose to reveal it. */
function RevealedAnswer({ itemId, busy, onGrade, compare }: { itemId: string; sessionId: string; busy: boolean; onGrade: (r: number) => void; compare?: boolean }) {
  const [item, setItem] = useState<{ answer: string; explanation: string; source_document_id: string | null; source_pages: number[] | null; source_excerpt: string | null; source_status: Feedback['source']['status'] } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    api.get<{ item: typeof item }>(`/api/items/${itemId}/answer`).then((r) => setItem(r.item), (e) => setErr(errorText(e)));
  }, [itemId]);
  if (err) return <ErrorBox error={err} />;
  if (!item) return <Loading />;
  return (
    <div>
      <div className="answer">
        {compare && <small>Réponse attendue</small>}
        <Txt>{item.answer}</Txt>
        {item.explanation && <Txt className="muted">{item.explanation}</Txt>}
        <SourceLine source={{ document_id: item.source_document_id, pages: item.source_pages, excerpt: item.source_excerpt, status: item.source_status }} />
      </div>
      <p style={{ marginTop: 12, marginBottom: 0 }}><b>{compare ? 'Votre réponse était-elle juste et complète ?' : 'Vous en êtes-vous souvenu ?'}</b></p>
      <div className="grades" role="group" aria-label="Évaluer votre rappel">
        {GRADES.map(([r, l, hint]) => (
          <button key={r} className={r === 3 ? 'primary' : ''} disabled={busy} onClick={() => onGrade(r)} aria-keyshortcuts={String(r)}>
            {l}<small>{hint}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

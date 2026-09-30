import { useState, type FormEvent } from 'react';
import { api, type DocumentInfo } from '../api.ts';
import { go } from '../router.ts';
import { useLoad, Loading, ErrorBox, errorText } from '../components/ui.tsx';

interface Lib { subjects: Array<{ id: string; name: string; chapters: Array<{ id: string; name: string }> }> }
type Kind = 'file' | 'text' | 'import';

export function AddCourse() {
  const lib = useLoad(() => api.get<Lib>('/api/library'), []);
  const [subjectId, setSubjectId] = useState('');
  const [subjectName, setSubjectName] = useState('');
  const [chapterId, setChapterId] = useState('');
  const [chapterName, setChapterName] = useState('');
  const [kind, setKind] = useState<Kind>('file');
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<{ chapter: string; doc: Partial<DocumentInfo> & { id: string } } | null>(null);

  const subject = lib.data?.subjects.find((s) => s.id === subjectId);

  async function ensureChapter(): Promise<string> {
    let sid = subjectId;
    if (!sid) {
      if (!subjectName.trim()) throw new Error('Indiquez la matière.');
      sid = (await api.post<{ id: string }>('/api/subjects', { name: subjectName })).id;
      setSubjectId(sid);
    }
    if (chapterId) return chapterId;
    if (!chapterName.trim()) throw new Error('Indiquez le chapitre.');
    const cid = (await api.post<{ id: string }>('/api/chapters', { subject_id: sid, name: chapterName })).id;
    setChapterId(cid);
    await lib.reload();
    return cid;
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      const cid = await ensureChapter();
      if (kind === 'import') return go(`/chapter/${cid}?tab=import`);
      if (kind === 'file') {
        if (!file) throw new Error('Choisissez un fichier.');
        if (file.size > 30 * 1024 * 1024) throw new Error('Fichier trop volumineux (30 Mo maximum).');
        const fd = new FormData();
        fd.append('title', title || file.name);
        fd.append('file', file);
        const doc = await api.post<DocumentInfo>(`/api/chapters/${cid}/documents/upload`, fd);
        setResult({ chapter: cid, doc });
      } else {
        if (!text.trim()) throw new Error('Collez le texte du cours.');
        const doc = await api.post<DocumentInfo>(`/api/chapters/${cid}/documents/text`, { title: title || 'Texte du cours', text });
        setResult({ chapter: cid, doc: { ...doc, extraction_status: 'ok', extraction_note: '' } });
      }
    } catch (e2) {
      setErr(errorText(e2));
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    const st = result.doc.extraction_status;
    return (
      <div className="stack">
        <h1>Cours ajouté</h1>
        <div className={`notice ${st === 'insufficient' ? 'warn' : st === 'partial' ? 'warn' : 'ok'}`} role="status">
          <b dir="auto">{result.doc.title}</b>
          {result.doc.kind === 'pdf' && <div>{result.doc.page_count} page(s) lue(s).</div>}
          {result.doc.extraction_note && <p style={{ marginTop: 8 }}>{result.doc.extraction_note}</p>}
        </div>
        <p>Prochaine étape : créer vos fiches et questions, ou importer celles préparées ailleurs.</p>
        <div className="grid2">
          <a className="btn primary big" href={`#/document/${result.doc.id}`}>Lire le cours</a>
          <a className="btn big" href={`#/chapter/${result.chapter}?tab=questions`}>Créer des questions</a>
          <a className="btn big" href={`#/chapter/${result.chapter}?tab=import`}>Importer des flashcards</a>
          <button className="big" onClick={() => { setResult(null); setFile(null); setText(''); setTitle(''); }}>Ajouter un autre support</button>
        </div>
      </div>
    );
  }

  return (
    <form className="stack" onSubmit={submit}>
      <h1>Ajouter un cours</h1>
      <ErrorBox error={lib.error} onRetry={lib.reload} />
      {lib.loading && !lib.data ? <Loading /> : (
        <fieldset className="card" style={{ border: 0 }}>
          <legend className="sr-only">Où ranger ce cours ?</legend>
          <h2>1. Où le ranger ?</h2>
          <div className="field">
            <label htmlFor="subj">Matière</label>
            <select id="subj" value={subjectId} onChange={(e) => { setSubjectId(e.target.value); setChapterId(''); }}>
              <option value="">＋ Nouvelle matière…</option>
              {lib.data?.subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            {!subjectId && <input type="text" aria-label="Nom de la nouvelle matière" placeholder="Nom de la matière (ex. Fiqh)" value={subjectName} onChange={(e) => setSubjectName(e.target.value)} style={{ marginTop: 8 }} dir="auto" />}
          </div>
          <div className="field">
            <label htmlFor="chap">Chapitre</label>
            <select id="chap" value={chapterId} onChange={(e) => setChapterId(e.target.value)}>
              <option value="">＋ Nouveau chapitre…</option>
              {subject?.chapters.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            {!chapterId && <input type="text" aria-label="Nom du nouveau chapitre" placeholder="Nom du chapitre (ex. La purification)" value={chapterName} onChange={(e) => setChapterName(e.target.value)} style={{ marginTop: 8 }} dir="auto" />}
          </div>
        </fieldset>
      )}
      <fieldset className="card" style={{ border: 0 }}>
        <legend className="sr-only">Quel support ?</legend>
        <h2>2. Quel support ?</h2>
        <div className="row" role="radiogroup" aria-label="Type de support">
          {([['file', 'Un fichier PDF'], ['text', 'Coller du texte'], ['import', 'Flashcards / questions déjà prêtes']] as const).map(([k, l]) => (
            <label key={k} className="check" style={{ marginRight: 12 }}>
              <input type="radio" name="kind" checked={kind === k} onChange={() => setKind(k)} /> {l}
            </label>
          ))}
        </div>
        <hr />
        {kind === 'file' && (
          <>
            <div className="field">
              <label htmlFor="file">Fichier</label>
              <input id="file" type="file" accept="application/pdf,image/png,image/jpeg,image/webp" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
              <small>PDF jusqu'à 30 Mo. Une image (PNG, JPEG) est gardée comme ressource à consulter, par exemple une carte mentale téléchargée.</small>
            </div>
            <div className="field"><label htmlFor="t1">Titre (facultatif)</label><input id="t1" type="text" value={title} onChange={(e) => setTitle(e.target.value)} dir="auto" /></div>
          </>
        )}
        {kind === 'text' && (
          <>
            <div className="field"><label htmlFor="t2">Titre</label><input id="t2" type="text" value={title} onChange={(e) => setTitle(e.target.value)} dir="auto" /></div>
            <div className="field"><label htmlFor="tx">Texte du cours</label><textarea id="tx" rows={10} value={text} onChange={(e) => setText(e.target.value)} dir="auto" /></div>
          </>
        )}
        {kind === 'import' && <p className="muted">Vous choisirez le fichier (CSV ou JSON) à l'étape suivante, avec un aperçu avant l'enregistrement.</p>}
      </fieldset>
      {err && <div className="notice bad" role="alert">{err}</div>}
      <button className="primary big" disabled={busy}>{busy ? (kind === 'file' ? 'Lecture du document…' : 'Enregistrement…') : kind === 'import' ? 'Continuer' : 'Ajouter'}</button>
    </form>
  );
}

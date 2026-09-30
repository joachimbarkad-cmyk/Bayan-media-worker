import { useMemo, useState } from 'react';
import { api, type DocumentInfo } from '../api.ts';
import { parseCsv, decodeBytes, guessMapping, applyMapping, type Mapping } from '../lib/csv.ts';
import { errorText, Txt } from './ui.tsx';

const ENCODINGS = [['utf-8', 'UTF-8 (recommandé)'], ['windows-1256', 'Windows arabe (1256)'], ['windows-1252', 'Windows occidental (1252)']] as const;
const FIELDS: Array<[keyof Mapping, string, boolean]> = [
  ['question', 'Question (recto)', true], ['answer', 'Réponse (verso)', true], ['explanation', 'Explication', false],
  ['pages', 'Page(s)', false], ['excerpt', 'Extrait du cours', false],
];

export function ImportCsv({ chapterId, docs, onDone }: { chapterId: string; docs: DocumentInfo[]; onDone: () => void }) {
  const [bytes, setBytes] = useState<Uint8Array | null>(null);
  const [fileName, setFileName] = useState('');
  const [encoding, setEncoding] = useState<(typeof ENCODINGS)[number][0]>('utf-8');
  const [delimiter, setDelimiter] = useState('');
  const [hasHeader, setHasHeader] = useState(true);
  const [mapping, setMapping] = useState<Mapping | null>(null);
  const [docId, setDocId] = useState('');
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad' | 'warn'; text: string; list?: string[] } | null>(null);
  const [busy, setBusy] = useState(false);

  const decoded = useMemo(() => (bytes ? decodeBytes(bytes, encoding) : null), [bytes, encoding]);
  const table = useMemo(() => (decoded ? parseCsv(decoded.text, { delimiter, hasHeader }) : null), [decoded, delimiter, hasHeader]);
  const map = mapping ?? (table ? guessMapping(table.headers) : null);
  const rows = table && map ? applyMapping(table.rows, map) : [];

  async function send(dryRun: boolean) {
    setBusy(true);
    setMsg(null);
    try {
      const r = await api.post<{ ok: boolean; count: number; errors: string[] }>(`/api/chapters/${chapterId}/import/csv`, { rows, document_id: docId || null, dry_run: dryRun });
      if (!r.ok) setMsg({ kind: 'bad', text: `${r.errors.length} ligne(s) à corriger avant l'import :`, list: r.errors });
      else if (dryRun) setMsg({ kind: 'ok', text: `${r.count} flashcard(s) prêtes à être importées.` });
      else { setMsg({ kind: 'ok', text: `${r.count} flashcard(s) importées. Elles apparaîtront dans la révision du jour.` }); setBytes(null); onDone(); }
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); } finally { setBusy(false); }
  }

  return (
    <section className="card stack" aria-labelledby="csv-h">
      <h2 id="csv-h">Importer des flashcards (CSV)</h2>
      <p className="muted">Fichier CSV ou TSV : une ligne par carte, avec au moins une colonne question et une colonne réponse. Convient aux flashcards téléchargées depuis NotebookLM ou un tableur. <b>Import générique</b> : la compatibilité avec un export NotebookLM précis n'a pas encore été testée sur un vrai fichier ; vérifiez l'aperçu.</p>
      <div>
        <label htmlFor="csv-file">Fichier</label>
        <input id="csv-file" type="file" accept=".csv,.tsv,.txt,text/csv,text/tab-separated-values" onChange={async (e) => {
          const f = e.target.files?.[0];
          setMsg(null); setMapping(null);
          if (!f) return;
          if (f.size > 5 * 1024 * 1024) { setMsg({ kind: 'bad', text: 'Fichier trop volumineux (5 Mo maximum).' }); return; }
          setFileName(f.name);
          setBytes(new Uint8Array(await f.arrayBuffer()));
        }} />
      </div>
      {table && map && (
        <>
          {decoded?.suspicious && <div className="notice warn">Certains caractères sont illisibles en UTF-8. Si le fichier vient d'un Excel en arabe, choisissez « Windows arabe (1256) ».</div>}
          <div className="grid2">
            <div><label htmlFor="csv-enc">Encodage</label><select id="csv-enc" value={encoding} onChange={(e) => setEncoding(e.target.value as typeof encoding)}>{ENCODINGS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>
            <div><label htmlFor="csv-sep">Séparateur</label>
              <select id="csv-sep" value={delimiter} onChange={(e) => setDelimiter(e.target.value)}>
                <option value="">Automatique (détecté : {table.delimiter === '\t' ? 'tabulation' : `« ${table.delimiter} »`})</option>
                <option value=",">Virgule</option><option value=";">Point-virgule</option><option value={'\t'}>Tabulation</option><option value="|">Barre verticale</option>
              </select></div>
          </div>
          <label className="check"><input type="checkbox" checked={hasHeader} onChange={(e) => { setHasHeader(e.target.checked); setMapping(null); }} /> La première ligne contient les titres des colonnes</label>
          <div className="grid2">
            {FIELDS.map(([k, label, req]) => (
              <div key={k}>
                <label htmlFor={`map-${k}`}>{label}{req ? '' : ' (facultatif)'}</label>
                <select id={`map-${k}`} value={map[k]} onChange={(e) => setMapping({ ...map, [k]: Number(e.target.value) })}>
                  {!req && <option value={-1}>— ne pas utiliser —</option>}
                  {table.headers.map((h, i) => <option key={i} value={i}>{h}</option>)}
                </select>
              </div>
            ))}
          </div>
          <div>
            <label htmlFor="csv-doc">Document source (facultatif)</label>
            <select id="csv-doc" value={docId} onChange={(e) => setDocId(e.target.value)}>
              <option value="">Aucun</option>{docs.filter((d) => d.kind !== 'image').map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
            </select>
            <small>Sans page ni extrait retrouvé dans le document, chaque carte sera marquée « source à vérifier ».</small>
          </div>
          {table.warnings.length > 0 && <div className="notice warn">{table.warnings.join(' · ')}</div>}
          <h3>Aperçu — {fileName} : {rows.length} ligne(s)</h3>
          <div className="table-wrap">
            <table>
              <thead><tr><th>#</th><th>Question</th><th>Réponse</th></tr></thead>
              <tbody>{rows.slice(0, 8).map((r, i) => <tr key={i}><td>{i + 1}</td><td><Txt>{r.question}</Txt></td><td><Txt>{r.answer}</Txt></td></tr>)}</tbody>
            </table>
          </div>
          {rows.length > 8 && <small>… et {rows.length - 8} autre(s).</small>}
          <div className="row end">
            <button onClick={() => send(true)} disabled={busy}>Vérifier</button>
            <button className="primary" onClick={() => send(false)} disabled={busy || rows.length === 0}>Importer {rows.length} carte(s)</button>
          </div>
        </>
      )}
      {msg && <div className={`notice ${msg.kind}`} role="status">{msg.text}{msg.list && <ul>{msg.list.map((l) => <li key={l}>{l}</li>)}</ul>}</div>}
    </section>
  );
}

export function ImportJson({ chapterId, docs, onDone }: { chapterId: string; docs: DocumentInfo[]; onDone: () => void }) {
  const [raw, setRaw] = useState('');
  const [docId, setDocId] = useState('');
  const [preview, setPreview] = useState<Record<string, number | string | null> | null>(null);
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad'; text: string; list?: string[] } | null>(null);
  const [busy, setBusy] = useState(false);

  async function send(dryRun: boolean) {
    setMsg(null);
    let data: unknown;
    try { data = JSON.parse(raw); } catch (e) { setMsg({ kind: 'bad', text: `Ce n'est pas un JSON valide : ${(e as Error).message}` }); return; }
    setBusy(true);
    try {
      const r = await api.post<{ ok: boolean; errors?: string[]; summary?: Record<string, number | string | null> }>(`/api/chapters/${chapterId}/import/json`, { data, document_id: docId || null, dry_run: dryRun });
      if (!r.ok) { setPreview(null); setMsg({ kind: 'bad', text: 'Le fichier ne respecte pas le format attendu :', list: r.errors }); }
      else if (dryRun) setPreview(r.summary!);
      else { setMsg({ kind: 'ok', text: `Import terminé. ${r.summary!.verified_sources ?? 0} élément(s) avec source vérifiée.` }); setPreview(null); setRaw(''); onDone(); }
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); } finally { setBusy(false); }
  }

  return (
    <section className="card stack" aria-labelledby="json-h">
      <h2 id="json-h">Importer des supports structurés (JSON)</h2>
      <p className="muted">Fiches, flashcards, QCM, questions ouvertes, carte mentale et glossaire au format <code>muraja.v1</code> (voir le guide « Préparer ses supports »). Vous pouvez demander ce format à NotebookLM ou à un autre outil ; ce n'est pas un export natif garanti.</p>
      <div>
        <label htmlFor="json-file">Fichier .json</label>
        <input id="json-file" type="file" accept=".json,application/json" onChange={async (e) => { const f = e.target.files?.[0]; if (f) { if (f.size > 5 * 1024 * 1024) { setMsg({ kind: 'bad', text: 'Fichier trop volumineux (5 Mo maximum).' }); return; } setRaw(await f.text()); setPreview(null); } }} />
      </div>
      <div>
        <label htmlFor="json-raw">… ou collez le contenu</label>
        <textarea id="json-raw" rows={6} value={raw} onChange={(e) => { setRaw(e.target.value); setPreview(null); }} spellCheck={false} style={{ fontFamily: 'ui-monospace, monospace', fontSize: '.85rem' }} />
      </div>
      <div>
        <label htmlFor="json-doc">Document source (pour vérifier les extraits cités)</label>
        <select id="json-doc" value={docId} onChange={(e) => setDocId(e.target.value)}>
          <option value="">Aucun</option>{docs.filter((d) => d.kind !== 'image').map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
        </select>
      </div>
      {preview && (
        <div className="notice" role="status">
          <b>Aperçu :</b> {preview.notes} fiche(s), {preview.flashcards} flashcard(s), {preview.mcq} QCM, {preview.open} question(s) ouverte(s)
          {Number(preview.mindmap) > 0 && `, une carte mentale de ${preview.mindmap} nœuds`}{Number(preview.glossary) > 0 && `, ${preview.glossary} terme(s) de glossaire`}.
          {Number(preview.without_source) > 0 && <div>{preview.without_source} élément(s) sans référence seront marqués « source à vérifier ».</div>}
        </div>
      )}
      {msg && <div className={`notice ${msg.kind}`} role="status">{msg.text}{msg.list && <ul>{msg.list.map((l) => <li key={l}>{l}</li>)}</ul>}</div>}
      <div className="row end">
        <button onClick={() => send(true)} disabled={busy || !raw.trim()}>Prévisualiser</button>
        <button className="primary" onClick={() => send(false)} disabled={busy || !preview}>Importer</button>
      </div>
    </section>
  );
}

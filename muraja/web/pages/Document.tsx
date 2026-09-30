import { useState } from 'react';
import { api, type DocumentInfo } from '../api.ts';
import { useLoad, Loading, ErrorBox, Txt } from '../components/ui.tsx';
import { ItemForm } from '../components/ItemForm.tsx';

interface DocView { document: DocumentInfo & { chapter_id: string }; pages: Array<{ page_number: number; text: string; readable: boolean }> }

export function DocumentPage({ id }: { id: string }) {
  const d = useLoad(() => api.get<DocView>(`/api/documents/${id}`), [id]);
  const [draft, setDraft] = useState<{ page: number; excerpt: string } | null>(null);
  const [saved, setSaved] = useState(0);

  if (d.loading && !d.data) return <Loading />;
  if (!d.data) return <ErrorBox error={d.error} onRetry={d.reload} />;
  const { document: doc, pages } = d.data;
  const fileUrl = `/api/documents/${doc.id}/file`;

  function fromSelection(page: number) {
    const sel = window.getSelection()?.toString().trim() ?? '';
    setDraft({ page, excerpt: sel });
  }

  return (
    <div className="stack">
      <p className="muted" style={{ marginBottom: 0 }}><a href={`#/chapter/${doc.chapter_id}`}>← Retour au chapitre</a></p>
      <h1 dir="auto">{doc.title}</h1>
      {doc.extraction_note && <div className={`notice ${doc.extraction_status === 'ok' || doc.extraction_status === 'not_applicable' ? '' : 'warn'}`}>{doc.extraction_note}</div>}
      {doc.kind !== 'text' && <a className="btn" href={fileUrl} target="_blank" rel="noopener">Ouvrir le fichier original</a>}
      {doc.kind === 'image' && <img src={fileUrl} alt={`Image : ${doc.title}`} style={{ maxWidth: '100%', borderRadius: 12, border: '1px solid var(--line)' }} />}
      {saved > 0 && <div className="notice ok" role="status">{saved} question(s) créée(s) depuis ce document.</div>}
      {doc.kind !== 'image' && (
        <>
          <p className="muted">Astuce : sélectionnez une phrase du cours puis « Créer une question » ; l'extrait et la page seront gardés comme source.</p>
          {pages.map((p) => (
            <section key={p.page_number} className={`page ${p.readable ? '' : 'unreadable'}`} aria-label={doc.kind === 'pdf' ? `Page ${p.page_number}` : 'Texte'}>
              <div className="spread">
                {doc.kind === 'pdf' ? <h3>Page {p.page_number}{!p.readable && ' — texte non lisible'}</h3> : <span />}
                {p.readable && <button className="small" onMouseDown={(e) => e.preventDefault()} onClick={() => fromSelection(p.page_number)}>Créer une question</button>}
              </div>
              {draft?.page === p.page_number && (
                <div className="card">
                  <ItemForm chapterId={doc.chapter_id} docs={[doc]}
                    initial={{ source: { document_id: doc.id, pages: doc.kind === 'pdf' ? String(p.page_number) : '', excerpt: draft.excerpt } }}
                    onDone={() => { setSaved(saved + 1); setDraft(null); }} onCancel={() => setDraft(null)} />
                </div>
              )}
              {p.text ? <Txt>{p.text}</Txt> : <p className="muted">(aucun texte extrait)</p>}
            </section>
          ))}
        </>
      )}
    </div>
  );
}

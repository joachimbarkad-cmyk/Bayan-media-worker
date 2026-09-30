import { api } from '../api.ts';
import { useLoad, Loading, ErrorBox, Txt, TYPE_LABEL } from '../components/ui.tsx';

interface P {
  activities: { reviews_today: number; reviews_total: number };
  items: { total: number; new: number; learning: number; mastered: number; recognized: number; to_rework: number };
  difficult: Array<{ id: string; prompt: string; type: 'flashcard' | 'mcq' | 'open'; chapter_id: string; lapses: number }>;
}

export function Progress() {
  const p = useLoad(() => api.get<P>('/api/progress'), []);
  if (p.loading && !p.data) return <Loading />;
  if (!p.data) return <ErrorBox error={p.error} onRetry={p.reload} />;
  const { activities: a, items: i, difficult } = p.data;
  return (
    <div className="stack">
      <h1>Mes progrès</h1>
      <section>
        <h2>Activité</h2>
        <div className="stats">
          <div className="stat"><b>{a.reviews_today}</b>réponses aujourd'hui</div>
          <div className="stat"><b>{a.reviews_total}</b>réponses au total</div>
        </div>
      </section>
      <section>
        <h2>Ce que je retiens</h2>
        <p className="muted">Une réponse donnée n'est pas une notion acquise. « Maîtrisée » signifie : retrouvée sans aide (flashcard ou question ouverte), plusieurs fois, avec un intervalle d'au moins trois semaines. Un QCM réussi indique seulement que vous <em>reconnaissez</em> la réponse.</p>
        <div className="stats">
          <div className="stat"><b>{i.mastered}</b>maîtrisée(s)</div>
          <div className="stat"><b>{i.recognized}</b>QCM reconnu(s)</div>
          <div className="stat"><b>{i.learning}</b>en apprentissage</div>
          <div className="stat"><b>{i.new}</b>jamais vue(s)</div>
        </div>
      </section>
      <section className="card">
        <h2>À reprendre ({i.to_rework})</h2>
        {difficult.length === 0 ? <p className="muted">Aucune difficulté repérée pour le moment.</p> : (
          <ul className="list">
            {difficult.map((d) => (
              <li key={d.id} className="spread">
                <a href={`#/chapter/${d.chapter_id}?tab=questions`} style={{ flex: 1 }}><Txt as="span">{d.prompt}</Txt></a>
                <span className="badge">{TYPE_LABEL[d.type]}{d.lapses ? ` · oubliée ${d.lapses}×` : ''}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

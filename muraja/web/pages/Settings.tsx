import { useState } from 'react';
import { api, type User } from '../api.ts';
import { errorText } from '../components/ui.tsx';
import { AiSettings } from '../components/AiSettings.tsx';

const ZONES = ['Indian/Reunion', 'Europe/Paris', 'Indian/Mauritius', 'Indian/Mayotte', 'Africa/Casablanca', 'Africa/Algiers', 'Africa/Tunis', 'Africa/Cairo', 'Asia/Riyadh', 'America/Montreal', 'UTC'];

export function Settings({ user, onUser }: { user: User; onUser: (u: User | null) => void }) {
  const [tz, setTz] = useState(user.timezone);
  const [s, setS] = useState(user.settings);
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad'; text: string } | null>(null);

  async function save() {
    setMsg(null);
    try {
      const r = await api.put<{ user: User }>('/api/me/settings', { timezone: tz, scheduler: s });
      onUser(r.user);
      setMsg({ kind: 'ok', text: 'Réglages enregistrés.' });
    } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); }
  }

  return (
    <div className="stack">
      <h1>Réglages</h1>
      <section className="card">
        <h2>Mon compte</h2>
        <p>{user.name} · {user.email}</p>
        <div className="row">
          <a className="btn" href="/api/export" download>Exporter mes données (JSON)</a>
          <button onClick={async () => { await api.post('/api/auth/logout'); onUser(null); window.location.hash = '/'; }}>Se déconnecter</button>
        </div>
      </section>
      <section className="card">
        <h2>Révisions</h2>
        <div className="field">
          <label htmlFor="tz">Fuseau horaire</label>
          <select id="tz" value={tz} onChange={(e) => setTz(e.target.value)}>
            {[...new Set([tz, ...ZONES])].map((z) => <option key={z} value={z}>{z}</option>)}
          </select>
          <small>La « révision du jour » suit votre journée locale.</small>
        </div>
        <div className="field">
          <label htmlFor="np">Nouvelles cartes par jour</label>
          <input id="np" type="number" min={0} max={200} value={s.new_per_day} onChange={(e) => setS({ ...s, new_per_day: Number(e.target.value) })} />
        </div>
        <details>
          <summary>Réglages avancés (algorithme FSRS)</summary>
          <div className="field" style={{ marginTop: 10 }}>
            <label htmlFor="rr">Taux de rappel visé : {Math.round(s.request_retention * 100)} %</label>
            <input id="rr" type="range" min={0.7} max={0.97} step={0.01} value={s.request_retention} onChange={(e) => setS({ ...s, request_retention: Number(e.target.value) })} style={{ width: '100%' }} />
            <small>Plus il est élevé, plus les révisions sont fréquentes.</small>
          </div>
          <div className="field">
            <label htmlFor="mi">Intervalle maximal (jours)</label>
            <input id="mi" type="number" min={7} max={36500} value={s.maximum_interval} onChange={(e) => setS({ ...s, maximum_interval: Number(e.target.value) })} />
          </div>
          <label className="check"><input type="checkbox" checked={s.enable_fuzz} onChange={(e) => setS({ ...s, enable_fuzz: e.target.checked })} /> Varier légèrement les intervalles longs</label>
        </details>
        {msg && <div className={`notice ${msg.kind}`} role="status" style={{ marginTop: 12 }}>{msg.text}</div>}
        <div className="row end" style={{ marginTop: 12 }}><button className="primary" onClick={save}>Enregistrer</button></div>
      </section>
      <AiSettings />
    </div>
  );
}

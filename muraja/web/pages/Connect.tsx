import { useState } from 'react';
import { api } from '../api.ts';
import { useLoad, Loading, ErrorBox, errorText } from '../components/ui.tsx';

/** OAuth consent screen: "Autoriser Claude à accéder à mes cours ?" */
export function Connect() {
  const qs = window.location.hash.split('?')[1] ?? '';
  const params = Object.fromEntries(new URLSearchParams(qs));
  const info = useLoad(() => api.get<{ client_name: string; redirect_host: string; loopback: boolean }>(`/api/oauth/request?${qs}`), [qs]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function decide(approve: boolean) {
    setBusy(true); setErr(null);
    try {
      const r = await api.post<{ redirect: string }>('/api/oauth/approve', { approve, params });
      window.location.assign(r.redirect);
    } catch (e) { setErr(errorText(e)); setBusy(false); }
  }

  if (info.loading && !info.data) return <Loading />;
  if (!info.data) return <ErrorBox error={info.error} />;
  return (
    <div className="card stack" style={{ maxWidth: 560, margin: '0 auto' }}>
      <h1>Autoriser « {info.data.client_name} » ?</h1>
      <p>Cette application pourra, avec votre compte Murāja'a :</p>
      <ul>
        <li>lire vos matières, chapitres, cours (texte extrait), fiches et questions ;</li>
        <li>voir les questions que vous ratez souvent ;</li>
        <li>ajouter des chapitres, fiches, flashcards, QCM et cartes mentales.</li>
      </ul>
      <p className="muted">Elle ne peut ni supprimer vos contenus, ni voir votre mot de passe, ni accéder à un autre compte. Retour vers : <b>{info.data.redirect_host}</b>.</p>
      {info.data.loopback && <div className="notice warn">Retour vers une adresse locale de cet appareil : n'autorisez que si vous venez de lancer cette connexion vous-même (par exemple Claude Code).</div>}
      {err && <div className="notice bad" role="alert">{err}</div>}
      <div className="grid2">
        <button className="big" disabled={busy} onClick={() => decide(false)}>Refuser</button>
        <button className="primary big" disabled={busy} onClick={() => decide(true)}>Autoriser</button>
      </div>
      <small className="muted">Vous pourrez déconnecter cette application à tout moment dans Réglages.</small>
    </div>
  );
}

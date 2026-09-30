import { useState, type FormEvent } from 'react';
import { api, type User } from '../api.ts';
import { errorText } from '../components/ui.tsx';

export function Login({ onLogin }: { onLogin: (u: User) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [form, setForm] = useState({ email: '', password: '', name: '', invite: '' });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const r = mode === 'login'
        ? await api.post<{ user: User }>('/api/auth/login', { email: form.email, password: form.password })
        : await api.post<{ user: User }>('/api/auth/register', { ...form, invite: form.invite || undefined });
      onLogin(r.user);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 440, paddingTop: 40 }}>
      <div className="hero">
        <div className="ar" lang="ar" style={{ fontSize: '2.4rem', color: 'var(--primary)' }}>مراجعة</div>
        <h1>Murāja'a</h1>
        <p className="muted">Comprendre son cours, s'entraîner sans regarder, revenir au bon moment.</p>
      </div>
      <form className="card" onSubmit={submit} noValidate>
        <h2>{mode === 'login' ? 'Se connecter' : 'Créer un compte'}</h2>
        {mode === 'register' && (
          <div className="field"><label htmlFor="name">Prénom</label><input id="name" type="text" autoComplete="given-name" value={form.name} onChange={set('name')} required /></div>
        )}
        <div className="field"><label htmlFor="email">Adresse e-mail</label><input id="email" type="email" autoComplete="email" value={form.email} onChange={set('email')} required /></div>
        <div className="field">
          <label htmlFor="password">Mot de passe</label>
          <input id="password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={form.password} onChange={set('password')} required minLength={8} />
          {mode === 'register' && <small>8 caractères au minimum.</small>}
        </div>
        {mode === 'register' && (
          <div className="field"><label htmlFor="invite">Code d'invitation <small>(si demandé)</small></label><input id="invite" type="text" value={form.invite} onChange={set('invite')} /></div>
        )}
        {error && <div className="notice bad" role="alert">{error}</div>}
        <button className="primary big" disabled={busy}>{busy ? 'Un instant…' : mode === 'login' ? 'Se connecter' : 'Créer mon compte'}</button>
        <p style={{ textAlign: 'center', marginTop: 14 }}>
          <button type="button" className="ghost" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null); }}>
            {mode === 'login' ? 'Pas encore de compte ? Créer un compte' : "J'ai déjà un compte"}
          </button>
        </p>
      </form>
    </main>
  );
}

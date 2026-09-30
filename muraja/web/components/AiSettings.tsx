import { useState } from 'react';
import { api } from '../api.ts';
import { useLoad, ErrorBox, errorText } from './ui.tsx';

type ProviderName = 'anthropic' | 'openai' | 'gemini';
interface Status {
  key_storage: boolean;
  configured: { provider: ProviderName; model: string; key_hint: string; readable: boolean } | null;
  providers: Record<ProviderName, { label: string; defaultModel: string | null; models: string[]; privacy: string }>;
  daily_limit: number; used_today: number;
}
interface Conn { connections: Array<{ client_id: string; client_name: string; since: number; last_used: number }>; mcp_url: string }

export function AiSettings() {
  const conn = useLoad(() => api.get<Conn>('/api/connections'), []);
  const st = useLoad(() => api.get<Status>('/api/ai/status'), []);
  const [copied, setCopied] = useState(false);
  const local = conn.data ? /\/\/(localhost|127\.0\.0\.1)/.test(conn.data.mcp_url) || conn.data.mcp_url.startsWith('http:') : false;

  return (
    <>
      <section className="card stack" aria-labelledby="ai-connect">
        <h2 id="ai-connect">Connecter mon Claude ou mon ChatGPT</h2>
        <p>Votre assistant pourra lire vos cours et créer fiches, flashcards, QCM et cartes mentales <b>dans votre compte</b>. Il utilise votre propre abonnement : rien n'est facturé par Murāja'a.</p>
        <ErrorBox error={conn.error} onRetry={conn.reload} />
        {conn.data && (
          <>
            <label htmlFor="mcp-url">Adresse du connecteur</label>
            <div className="row">
              <input id="mcp-url" type="text" readOnly value={conn.data.mcp_url} style={{ flex: 1, minWidth: 220 }} onFocus={(e) => e.target.select()} />
              <button onClick={async () => { try { await navigator.clipboard.writeText(conn.data!.mcp_url); setCopied(true); } catch { /* select manually */ } }}>{copied ? 'Copiée ✓' : 'Copier'}</button>
            </div>
            {local && <div className="notice warn">Cette adresse n'est pas accessible depuis Internet. La connexion fonctionnera une fois le site publié en HTTPS.</div>}
            <details>
              <summary><b>Claude</b> (claude.ai, application mobile ou ordinateur)</summary>
              <ol>
                <li>Dans Claude : <b>Personnaliser › Connecteurs › Ajouter un connecteur personnalisé</b>.</li>
                <li>Collez l'adresse ci-dessus, validez, puis <b>Se connecter</b>.</li>
                <li>Murāja'a s'ouvre : autorisez l'accès.</li>
                <li>Dans une conversation, activez le connecteur puis demandez par exemple : « Lis mon cours “La purification” et crée 10 flashcards avec la page et une phrase du cours pour chacune. »</li>
              </ol>
              <small>Disponible sur les offres gratuites (un connecteur personnalisé) et payantes. Sur une offre Équipe/Entreprise, un administrateur doit d'abord l'ajouter.</small>
            </details>
            <details>
              <summary><b>ChatGPT</b></summary>
              <p>ChatGPT accepte les connecteurs personnalisés (MCP) via le <b>mode développeur</b> des paramètres, sur certaines offres payantes seulement. Les menus et les offres concernées changent : vérifiez dans les paramètres de votre compte ChatGPT. Ce parcours n'a pas encore été testé avec ChatGPT.</p>
            </details>
            <h3>Applications connectées</h3>
            {conn.data.connections.length === 0 ? <p className="muted">Aucune.</p> : (
              <ul className="list">
                {conn.data.connections.map((c) => (
                  <li key={c.client_id} className="spread">
                    <span><b>{c.client_name}</b> <small>depuis le {new Date(c.since).toLocaleDateString('fr-FR')}</small></span>
                    <button className="small danger" onClick={async () => { await api.del(`/api/connections/${encodeURIComponent(c.client_id)}`); conn.reload(); }}>Déconnecter</button>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>

      <section className="card stack" aria-labelledby="ai-key">
        <h2 id="ai-key">IA intégrée au site (clé personnelle, facultatif)</h2>
        <p className="muted">Pour les boutons « Expliquer simplement » et « Générer des questions » directement dans Murāja'a. Il faut une clé API : c'est un compte distinct d'un abonnement Claude.ai ou ChatGPT, facturé à l'usage (Gemini propose une offre gratuite limitée).</p>
        <ErrorBox error={st.error} onRetry={st.reload} />
        {st.data && (st.data.key_storage ? <KeyForm st={st.data} reload={st.reload} /> : (
          <div className="notice">Non activé sur ce site : l'administrateur doit définir <code>MURAJA_SECRET_KEY</code> pour permettre l'enregistrement chiffré des clés.</div>
        ))}
      </section>

      <section className="card">
        <h2>NotebookLM</h2>
        <p className="muted">NotebookLM ne propose pas de connexion pour les comptes personnels. Préparez-y vos supports puis importez-les (flashcards CSV ou format JSON) depuis l'onglet « Importer » d'un chapitre.</p>
      </section>
    </>
  );
}

function KeyForm({ st, reload }: { st: Status; reload: () => void }) {
  const [provider, setProvider] = useState<ProviderName>(st.configured?.provider ?? 'anthropic');
  const [key, setKey] = useState('');
  const [model, setModel] = useState(st.configured?.model ?? st.providers[st.configured?.provider ?? 'anthropic'].defaultModel ?? '');
  const [models, setModels] = useState<string[]>([]);
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad'; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const meta = st.providers[provider];
  const suggestions = [...new Set([...meta.models, ...models])];

  async function run(fn: () => Promise<void>) {
    setBusy(true); setMsg(null);
    try { await fn(); } catch (e) { setMsg({ kind: 'bad', text: errorText(e) }); } finally { setBusy(false); }
  }

  return (
    <div className="stack">
      {st.configured && (
        <div className={`notice ${st.configured.readable ? 'ok' : 'warn'}`}>
          Connectée : {st.providers[st.configured.provider].label} · {st.configured.model} · clé {st.configured.key_hint}
          {!st.configured.readable && ' — clé illisible (clé serveur changée) : saisissez-la à nouveau.'}
          <div><small>{st.used_today} / {st.daily_limit} générations aujourd'hui.</small></div>
        </div>
      )}
      <div>
        <label htmlFor="ai-p">Fournisseur</label>
        <select id="ai-p" value={provider} onChange={(e) => { const p = e.target.value as ProviderName; setProvider(p); setModel(st.providers[p].defaultModel ?? ''); setModels([]); }}>
          {(Object.keys(st.providers) as ProviderName[]).map((p) => <option key={p} value={p}>{st.providers[p].label}</option>)}
        </select>
        <small>{meta.privacy}</small>
      </div>
      <div>
        <label htmlFor="ai-k">Clé API {st.configured?.provider === provider && <small>(laisser vide pour garder la clé actuelle)</small>}</label>
        <input id="ai-k" type="password" autoComplete="off" value={key} onChange={(e) => setKey(e.target.value)} placeholder={st.configured?.provider === provider ? `enregistrée ${st.configured.key_hint}` : ''} />
        <small>Chiffrée sur le serveur, jamais réaffichée ni transmise ailleurs qu'au fournisseur choisi.</small>
      </div>
      <div>
        <label htmlFor="ai-m">Modèle</label>
        <input id="ai-m" type="text" list="ai-models" value={model} onChange={(e) => setModel(e.target.value)} placeholder={meta.defaultModel ?? 'Tester la clé pour voir les modèles'} />
        <datalist id="ai-models">{suggestions.map((m) => <option key={m} value={m} />)}</datalist>
      </div>
      {msg && <div className={`notice ${msg.kind}`} role="status">{msg.text}</div>}
      <div className="row end">
        {st.configured && <button className="danger" disabled={busy} onClick={() => run(async () => { await api.del('/api/ai/key'); setMsg({ kind: 'ok', text: 'Clé supprimée.' }); reload(); })}>Supprimer la clé</button>}
        <button disabled={busy} onClick={() => run(async () => {
          const r = await api.post<{ models: string[] }>('/api/ai/test', { provider, api_key: key || undefined });
          setModels(r.models);
          setMsg({ kind: 'ok', text: `Clé valide : ${r.models.length} modèle(s) disponible(s). Choisissez-en un dans la liste.` });
        })}>Tester la clé</button>
        <button className="primary" disabled={busy} onClick={() => run(async () => {
          await api.put('/api/ai/key', { provider, model: model || undefined, api_key: key || undefined });
          setKey(''); setMsg({ kind: 'ok', text: 'Enregistré.' }); reload();
        })}>Enregistrer</button>
      </div>
    </div>
  );
}

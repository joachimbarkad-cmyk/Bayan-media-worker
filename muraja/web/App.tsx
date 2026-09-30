import { useEffect, useState, type ReactNode } from 'react';
import { api, type User } from './api.ts';
import { useRoute } from './router.ts';
import { Loading } from './components/ui.tsx';
import { Login } from './pages/Login.tsx';
import { Home } from './pages/Home.tsx';
import { Library } from './pages/Library.tsx';
import { AddCourse } from './pages/AddCourse.tsx';
import { Chapter } from './pages/Chapter.tsx';
import { DocumentPage } from './pages/Document.tsx';
import { Review } from './pages/Review.tsx';
import { Progress } from './pages/Progress.tsx';
import { Settings } from './pages/Settings.tsx';
import { Glossary } from './pages/Glossary.tsx';
import { MindMapPage } from './pages/MindMap.tsx';

const icons: Record<string, ReactNode> = {
  home: <path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />,
  library: <path d="M4 4h4v16H4zM10 4h4v16h-4zM16.5 4.5l3.8 1-3.9 15-3.8-1z" />,
  progress: <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />,
  settings: <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12l2-1-1-3-2 .3-1.3-1.3L17 5l-3-1-1 2h-2l-1-2-3 1 .3 2L6 8.3 4 8 3 11l2 1v1l-2 1 1 3 2-.3 1.3 1.3L7 19l3 1 1-2h2l1 2 3-1-.3-2 1.3-1.3 2 .3 1-3-2-1z" />,
};
const NAV = [
  ['home', '#/', 'Accueil'], ['library', '#/library', 'Bibliothèque'], ['progress', '#/progress', 'Progrès'], ['settings', '#/settings', 'Réglages'],
] as const;

export function App() {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const route = useRoute();

  useEffect(() => {
    api.get<{ user: User }>('/api/me').then((r) => setUser(r.user), () => setUser(null));
    const out = () => setUser(null);
    window.addEventListener('muraja:logout', out);
    return () => window.removeEventListener('muraja:logout', out);
  }, []);

  useEffect(() => { window.scrollTo(0, 0); }, [route.path.join('/')]);

  if (user === undefined) return <Loading />;
  if (!user) return <Login onLogin={setUser} />;

  const [section, id] = route.path;
  let page: ReactNode;
  switch (section) {
    case undefined: page = <Home user={user} />; break;
    case 'library': page = <Library />; break;
    case 'add': page = <AddCourse />; break;
    case 'chapter': page = <Chapter id={id} tab={route.query.get('tab') ?? 'supports'} />; break;
    case 'document': page = <DocumentPage id={id} />; break;
    case 'review': page = <Review chapterId={route.query.get('chapter')} />; break;
    case 'progress': page = <Progress />; break;
    case 'settings': page = <Settings user={user} onUser={setUser} />; break;
    case 'glossary': page = <Glossary />; break;
    case 'mindmap': page = <MindMapPage id={id} />; break;
    default: page = <p>Page introuvable. <a href="#/">Retour à l'accueil</a></p>;
  }
  const current = section === undefined ? 'home' : ['library', 'add', 'chapter', 'document', 'mindmap', 'glossary'].includes(section) ? 'library' : section;

  return (
    <div className="shell">
      <a className="skip" href="#contenu" onClick={(e) => { e.preventDefault(); document.getElementById('contenu')?.focus(); }}>Aller au contenu</a>
      <header className="top">
        <a className="brand" href="#/"><span className="ar" lang="ar">مراجعة</span> Murāja'a</a>
        <nav className="main" aria-label="Navigation principale">
          {NAV.map(([k, href, label]) => <a key={k} href={href} aria-current={current === k ? 'page' : undefined}>{label}</a>)}
        </nav>
      </header>
      <main id="contenu" tabIndex={-1}>{page}</main>
      <nav className="bottom" aria-label="Navigation principale (mobile)">
        {NAV.map(([k, href, label]) => (
          <a key={k} href={href} aria-current={current === k ? 'page' : undefined}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" aria-hidden="true">{icons[k]}</svg>
            {label}
          </a>
        ))}
      </nav>
    </div>
  );
}

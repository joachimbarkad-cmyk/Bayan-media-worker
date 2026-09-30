import { useEffect, useState } from 'react';

/** Minimal hash router: "#/chapter/abc?tab=x" → { path: ['chapter','abc'], query }. */
export function useRoute() {
  const [hash, setHash] = useState(() => window.location.hash);
  useEffect(() => {
    const on = () => setHash(window.location.hash);
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  const [p, q = ''] = hash.replace(/^#\/?/, '').split('?');
  return { path: p.split('/').filter(Boolean).map(decodeURIComponent), query: new URLSearchParams(q) };
}

export function go(to: string) {
  window.location.hash = to;
}

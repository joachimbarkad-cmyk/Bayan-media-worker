import { createRoot } from 'react-dom/client';
import '@fontsource/noto-naskh-arabic/400.css';
import '@fontsource/noto-naskh-arabic/700.css';
import './styles.css';
import { App } from './App.tsx';

createRoot(document.getElementById('root')!).render(<App />);

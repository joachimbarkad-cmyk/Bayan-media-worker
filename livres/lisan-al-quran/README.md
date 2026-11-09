# Lisān al-Qurʾān — méthode complète d'arabe coranique (volume unique)

**Le livre : [`Lisan-al-Quran.pdf`](Lisan-al-Quran.pdf)** (A4, 469 pages).

## Contenu

- **Partie I** (L1–2) : lire le texte vocalisé du muṣḥaf.
- **Partie II** (L3–20) : le nom, les pronoms, l'annexion, l'adjectif, la phrase nominale, inna et kāna.
- **Partie III** (L21–32) : le verbe (accompli, inaccompli, modes, passif, formes II–X, maṣdar, participes, verbes faibles).
- **Partie IV** (L33–40) : phrase verbale et compléments, ḥāl, tamyīz, exception, condition, serment, élatif, nombres.
- **Partie V** : 18 lectures suivies (Āyat al-Kursī, Luqmān, Maryam, al-Kahf, Ṭāhā, an-Nūr…).
- **Annexes** : aide-mémoire, recueil des 40 fiches, corrigés, lexique par racine (520 mots), index des notions et des versets.

Chaque leçon : révision express (questions à intervalles croissants), exposé avec versets, fiche, vocabulaire
choisi par fréquence, exercices (corrigés en annexe), texte de lecture analysé mot à mot.

## Révision intégrée à la lecture

Le générateur suit 61 notions de grammaire et 520 mots de vocabulaire. Dans chaque texte, il signale une
notion ou un mot **au moment où il faut le revoir** (intervalle doublé à chaque rappel : 1, 2, 4, 8 leçons),
grise les lignes déjà acquises, et termine par un bilan (part du vocabulaire connu, notions revues, fiches à relire).

## Fiabilité

- Texte coranique (Ḥafṣ, rasm ʿuthmānī) : *Quranic Arabic Corpus* (Tanzil), **contrôlé lettre à lettre**
  contre QuranEnc pour les 506 versets étudiés.
- Toute citation de verset dans les leçons est désignée par sa référence et retrouvée automatiquement dans le
  texte : une citation introuvable bloque la génération.
- L'analyse morphologique du corpus a été contrôlée (terminaison ↔ cas, particule ↔ mode) : 19 erreurs
  d'étiquetage du corpus ont été corrigées (voir `content/corrections.py`, chaque correction est justifiée).
- Traduction du sens : M. Hamidullah (révisée), via QuranEnc.

## Reconstruire

```sh
./build.sh        # télécharge les données si besoin (fetch_data.sh), produit Lisan-al-Quran.pdf
```

Python 3 (+ `pypdf`), Node.js et Playwright/Chromium. Le contenu rédigé est dans `content/` :
`lecons_p*.py` (leçons), `lectures.py`, `aide_memoire.py`, `gloses.py` (lexique), `corrections.py`.

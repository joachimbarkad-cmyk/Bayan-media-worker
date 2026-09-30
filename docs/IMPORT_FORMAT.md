# Préparer ses supports et les importer

Deux chemins gratuits, sans clé d'API :

1. **Flashcards en CSV** — par exemple téléchargées depuis NotebookLM, ou préparées dans un tableur. Colonnes minimales : question, réponse. Facultatives : explication, page(s), extrait du cours. L'écran d'import montre un aperçu et permet de choisir l'encodage, le séparateur et la correspondance des colonnes. *L'import est générique : il n'a pas encore été vérifié sur un vrai fichier exporté de NotebookLM. Envoyez-en un exemple pour qu'il soit testé.*
2. **Supports structurés en JSON** (`muraja.v1`) — fiches, flashcards, QCM, questions ouvertes, carte mentale, glossaire. Vous pouvez demander ce format dans le chat de NotebookLM ou d'un autre outil. **Ce n'est pas un export natif garanti de NotebookLM** : c'est une réponse de chat à copier dans un fichier.

Une carte mentale téléchargée en image s'ajoute comme **support image** : elle reste consultable mais n'est pas convertie en carte interactive. Pour une carte interactive, fournir la structure `mindmap` ci-dessous ou la construire dans l'éditeur.

## Format JSON `muraja.v1`

Tous les champs texte sont conservés comme texte brut (jamais interprétés comme HTML). Champs inconnus refusés.

```json
{
  "format": "muraja.v1",
  "document_title": "Titre exact du PDF déjà ajouté au chapitre (facultatif)",
  "notes": [
    { "title": "La purification", "body": "Texte de la fiche…", "source": { "pages": [3], "excerpt": "phrase exacte du cours" } }
  ],
  "flashcards": [
    { "question": "Une seule question précise ?", "answer": "Réponse courte", "explanation": "facultatif",
      "skill": "definition", "source": { "pages": [2], "excerpt": "phrase exacte du cours" } }
  ],
  "mcq": [
    { "question": "…?",
      "choices": [
        { "text": "Bonne réponse", "correct": true, "why": "Pourquoi c'est juste" },
        { "text": "Distracteur", "correct": false, "why": "Pourquoi c'est faux" }
      ],
      "explanation": "facultatif", "skill": "distinction", "source": { "pages": [4] } }
  ],
  "open": [
    { "question": "Expliquez avec vos mots…", "answer": "Éléments attendus", "skill": "application" }
  ],
  "mindmap": {
    "title": "La purification",
    "nodes": [
      { "id": "r", "label": "الطهارة — La purification" },
      { "id": "a", "label": "L'eau", "parent": "r", "note": "Explication du nœud" }
    ]
  },
  "glossary": [ { "term": "Tahara", "arabic": "الطَّهَارَة", "definition": "Purification rituelle" } ]
}
```

Règles : `skill` ∈ `definition` | `distinction` | `application` ; QCM : 2 à 8 propositions, **exactement une** correcte ; carte : une seule racine (sans `parent`), parents existants, pas de cycle. Limites : 3000 flashcards, 3000 QCM, 1000 questions ouvertes, 500 fiches, 1000 nœuds par import ; fichier ≤ 5 Mo.

**Sources.** Choisir le document du chapitre au moment de l'import (ou renseigner `document_title`). Un élément est marqué « source vérifiée » uniquement si son `excerpt` est retrouvé sur les pages citées du texte extrait. Sinon il reste « source à vérifier ». Ne jamais inventer de page ni de citation : laisser `source` absent si l'information manque.

## Demande à copier dans NotebookLM

> À partir des seules sources de ce notebook, prépare des supports de révision en français pour une personne débutante. Identifie les notions centrales, explique-les simplement, puis prépare des questions précises de définition, de distinction et d'application. Préserve les conditions, exceptions et divergences mentionnées dans le cours. Si le cours contient de l'arabe, conserve les termes importants et explique leur sens. Pour chaque élément, donne la page et une phrase recopiée mot pour mot du document quand elles sont disponibles ; n'invente ni citation ni pagination ; signale une information absente du document. Les flashcards posent une seule question et ont une réponse courte. Les QCM ont une seule bonne réponse et une explication pour chaque proposition. Ajoute un plan hiérarchique de carte mentale et cinq questions ouvertes. Réponds uniquement avec un JSON conforme à ce modèle : (coller le modèle ci-dessus).

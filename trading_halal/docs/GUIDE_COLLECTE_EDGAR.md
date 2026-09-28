# Collecte EDGAR : guide pas à pas (sans adresse électronique)

## C'est quoi ?

EDGAR est la base publique et gratuite de la SEC, le régulateur boursier américain. Les sociétés cotées aux
États-Unis y déposent leurs comptes : rapports annuels (10-K) et trimestriels (10-Q). La SEC en publie deux fichiers
par société, au format JSON :

- **submissions** : la liste des dépôts (dates, types de rapport, numéros) ;
- **companyfacts** : une partie des chiffres de ces rapports (chiffre d'affaires, dette, nombre d'actions…).

Ces chiffres servent au filtre religieux (ratios de dette, de dépôts à intérêt et de revenus illicites). La collecte
n'achète rien, ne passe aucun ordre et ne crée aucun compte.

## Qui la fait

Depuis le 2026-09-28, `data.sec.gov` est autorisé dans l'environnement de Claude : la collecte automatique (`collect`)
a été faite pour Apple (`collecte/apple/`, `data/audit_edgar_apple/`). La voie manuelle ci-dessous reste disponible si
l'accès est de nouveau fermé ou si vous ne voulez pas fournir d'adresse.

## Ce que vous avez à faire (5 minutes par société, aucune adresse électronique)

1. Choisir 2 ou 3 sociétés américaines pour un premier essai. Chacune a un numéro **CIK**. Exemples, à confirmer sur
   la page de recherche EDGAR (https://www.sec.gov/edgar/search/) : Apple = 320193, Microsoft = 789019.
2. Pour chaque société, ouvrir dans votre navigateur ces deux adresses, en complétant le CIK avec des zéros à gauche
   jusqu'à 10 chiffres (320193 devient 0000320193) :
   - `https://data.sec.gov/submissions/CIK0000320193.json`
   - `https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json`
3. Enregistrer chaque page (menu « Enregistrer sous », format JSON ou « page brute »), sans la modifier.
4. **Noter la date et l'heure** du téléchargement, avec le fuseau (ex. 28/09/2026 à 14 h 05, heure de Paris).
5. M'envoyer les fichiers dans cette conversation, avec le CIK et l'heure notée.

Si la SEC affiche une page d'erreur au lieu des données, envoyez-moi une capture : le navigateur a peut-être été refusé.

## Ce que je fais ensuite

```sh
python3 tools/edgar_collect.py import-files --cik 320193 \
    --submissions submissions.json --companyfacts companyfacts.json \
    --retrieved-at 2026-09-28T14:05:00+02:00 --out collecte/apple
python3 tools/edgar_collect.py convert --raw collecte/apple --out data/audit_edgar_apple
python3 -m halal_sim audit-docs data/audit_edgar_apple
```

Le résultat attendu est « 0 erreur, NON EXPLOITABLE ». C'est normal : un dossier fraîchement collecté contient des
informations inconnues (contexte, dimensions, catégorie d'actions, heure de diffusion publique), et aucun chiffre n'a
encore été rapproché à la main du rapport d'origine. La simulation sur données réelles reste refusée tant que le
référentiel religieux n'a pas été validé par un sharia board nommé.

## Variante automatique (plus tard, facultative)

`python3 tools/edgar_collect.py collect --cik 320193 --user-agent "Prénom Nom adresse@domaine" --out collecte/apple`
télécharge directement, mais la SEC demande alors un nom et une adresse électronique de contact. Vous avez préféré ne
pas la fournir pour l'instant : la voie manuelle ci-dessus s'en passe.

## Rapprocher un chiffre de son document (V1.13)

Depuis la V1.17, `www.sec.gov` est accessible : `python3 tools/edgar_normalize.py fetch-filing --audit DOSSIER --doc-id DOC
--user-agent "Prénom Nom adresse@domaine" --raw RAW` télécharge et importe le document. Sans accès réseau, voie manuelle
(adresse dans la colonne `url` de `documents.csv`) :

1. l'ouvrir dans un navigateur et l'enregistrer tel quel (« page HTML uniquement ») sous son nom d'origine ;
2. noter l'heure du téléchargement avec le fuseau ;
3. me l'envoyer ; je lance :

```sh
python3 tools/edgar_normalize.py import-filing --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-25-000079 --fichier aapl-20250927.htm \
    --retrieved-at 2026-09-28T14:05:00+02:00 --raw collecte/apple
python3 tools/edgar_normalize.py reconcile-ixbrl --audit data/audit_edgar_apple \
    --doc-id 0000320193-0000320193-25-000079 --raw collecte/apple --regles config/normalisation/edgar_v4.json
```

Autre voie : ajouter `www.sec.gov` aux domaines autorisés de l'environnement.

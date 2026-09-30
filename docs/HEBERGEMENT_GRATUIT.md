# Héberger Murāja'a gratuitement sur son ordinateur

Coût : 0 €. Le site tourne sur votre ordinateur, et **Tailscale Funnel** (offre personnelle gratuite) le publie en HTTPS à une adresse stable, du type `https://mon-pc.nom-du-reseau.ts.net`. C'est cette adresse qui va dans `MURAJA_PUBLIC_URL`. Claude peut alors se connecter à Murāja'a.

Limites à connaître :
- l'ordinateur doit rester allumé et connecté pour que le site et le connecteur Claude marchent ;
- Tailscale applique des limites de débit non réglables : cela convient à un usage familial, pas à un grand public ;
- l'adresse `.ts.net` ne peut pas être personnalisée ;
- vos cours restent sur votre ordinateur : **sauvegardez** le dossier `muraja/data` (base + PDF).

Écartée : le tunnel rapide Cloudflare (`trycloudflare.com`) change d'adresse à chaque redémarrage et est réservé aux tests ; il faudrait reconnecter Claude à chaque fois.

## 1. Installer Murāja'a (une fois)

1. Installer **Node.js 22 LTS** (22.18 ou plus récent) depuis nodejs.org.
2. Télécharger le dépôt (GitHub › Code › Download ZIP, ou `git clone`), puis ouvrir un terminal dans le dossier `muraja` :
   ```sh
   npm ci
   npm run build
   ```

## 2. Installer Tailscale et ouvrir le tunnel (une fois)

1. Installer Tailscale (tailscale.com/download) et se connecter avec un compte gratuit.
2. Dans un terminal :
   ```sh
   tailscale funnel --bg 8787
   ```
   Au premier lancement, Tailscale affiche un lien pour autoriser HTTPS et Funnel sur votre réseau : ouvrez-le et acceptez.
3. Afficher l'adresse publique :
   ```sh
   tailscale funnel status
   ```
   Elle ressemble à `https://mon-pc.tail1234.ts.net`.

## 3. Configurer et lancer Murāja'a

Dans le dossier `muraja` :
```sh
npm run setup -- https://mon-pc.tail1234.ts.net
npm start
```
`npm run setup` crée le fichier `.env` (jamais publié) avec :
- `MURAJA_PUBLIC_URL`, l'adresse ci-dessus ;
- `MURAJA_SECRET_KEY`, aléatoire, qui chiffre les clés IA personnelles ;
- `MURAJA_INVITE_CODE` : **le code à donner aux personnes qui créent un compte** (affiché à l'écran). Le serveur refuse de démarrer en public sans lui.

Le site n'écoute que sur l'ordinateur lui-même (`127.0.0.1:8787`) ; seul Tailscale le rend accessible depuis Internet.

Ouvrez l'adresse `.ts.net` sur le téléphone, créez votre compte avec le code d'invitation.

### Variante Docker (redémarre tout seul)

Avec Docker Desktop, après `npm run setup -- https://...ts.net` :
```sh
docker compose up -d --build
```
Les données sont alors dans le volume Docker `muraja-data`.

## 4. Connecter Claude

Dans Murāja'a : **Réglages › Connecter mon Claude ou mon ChatGPT**, copiez l'adresse du connecteur (`https://…ts.net/mcp`). Dans Claude : **Personnaliser › Connecteurs › Ajouter un connecteur personnalisé**, collez l'adresse, puis **Se connecter** et autorisez.

## Si quelque chose ne marche pas

- **Le site ne répond pas depuis le téléphone** : l'ordinateur est-il allumé, `npm start` tourne-t-il, `tailscale funnel status` montre-t-il le port 8787 ?
- **Claude dit qu'il ne peut pas joindre le serveur** : vérifiez que `MURAJA_PUBLIC_URL` est exactement l'adresse de `tailscale funnel status` (en `https://`), puis relancez `npm start`.
- **Changer d'adresse** : relancez `npm run setup -- <nouvelle adresse>`, redémarrez, puis supprimez et rajoutez le connecteur dans Claude.

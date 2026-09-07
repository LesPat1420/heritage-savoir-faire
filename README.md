# L'Héritage d'un savoir-faire — site vitrine

Site statique (HTML/CSS/JS, sans dépendance ni build) pour l'activité de conseil,
expertise et formation de **Lou François**.

## Trois maquettes au choix

`index.html` est un **sélecteur** : trois colonnes plein écran, une par direction
graphique. On clique pour explorer chacune.

| Fichier    | Direction              | Esprit |
|------------|------------------------|--------|
| `v1.html`  | Cabinet d'architecte   | sobre, précis, beaucoup d'air (CSS `style.css`, JS `main.js`) |
| `v2.html`  | Atelier                | chaleureux, fait main, polaroïds, écriture (CSS `atelier.css`, JS `atelier.js`) |
| `v3.html`  | Almanach imprimé       | affiche ancienne, letterpress, symétrique (CSS `v3.css`) |

Une fois la version retenue, elle deviendra `index.html` (et on supprimera les autres).

## Structure

```
index.html             sélecteur des 3 maquettes
v1.html / v2.html / v3.html   les 3 versions
assets/css/             style.css · atelier.css · v3.css
assets/js/              main.js · atelier.js
assets/img/             logo (original JPG + PNG détouré approximatif)
```

## Lancer en local

```bash
python3 -m http.server 8777
```

Puis ouvrir http://localhost:8777

## Contenu à valider / remplacer

Les textes actuels sont **provisoires et inventés** pour donner à voir le rendu.
À reprendre avec Lou :

- **Parcours / histoire** : dates, entreprises, régions, diplômes et titres réels,
  formulation sur la santé (mention actuelle discrète, à valider).
- **Réalisations** : remplacer les 6 pavés par de vraies photos de chantiers
  (`assets/img/realisations/`), ajuster lieux / années / natures d'ouvrage.
- **Prestations** : détail concret de chaque prestation, mention tarifaire.
- **Zone d'intervention** : périmètre réel, rayon, déplacements.
- **Contact** : créer l'adresse `contact@heritage-savoir-faire.fr` (ou autre),
  confirmer l'adresse postale (Saulieu / Alligny-en-Morvan).
- **Portrait de Lou** : photo à ajouter (section parcours).
- **Logo** : fournir si possible une version PNG fond transparent + SVG.
- **Mentions légales** : à compléter dès l'immatriculation (SIRET, assurance RC pro,
  médiateur de la consommation, hébergeur).

## Formulaire de contact

Actuellement en `mailto:` (ouvre le logiciel de messagerie). Pour un envoi direct
sans serveur : Formspree, Netlify Forms ou Web3Forms.

## Mise en ligne

Site statique → hébergement gratuit avec HTTPS :

- **Netlify** : glisser-déposer le dossier, ou connecter un dépôt Git.
- **GitHub Pages** : pousser le dossier sur une branche `main`, activer Pages.
- **Cloudflare Pages** : équivalent.

Domaine envisagé : `heritage-savoir-faire.fr` (à enregistrer chez un registrar,
~10 €/an, puis pointer les DNS vers l'hébergeur).

## Polices

Chargées depuis Google Fonts : Cinzel (titres), EB Garamond (texte), Archivo (labels).
Pour un site 100 % autonome, télécharger les .woff2 et les servir localement.

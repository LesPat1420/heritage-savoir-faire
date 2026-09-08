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
assets/css/             style.css · atelier.css · v3.css · lightbox.css (galerie, commun)
assets/js/              main.js · atelier.js · charpente3d.js
                        projets.js  (données des albums chantiers — généré)
                        galerie.js  (visionneuse commune aux 3 maquettes)
assets/img/realisations/   photos réelles, un dossier par chantier (00.jpg = couverture)
                           + _histoire / _mairie / _accompagnement (images de section)
assets/img/             logo (original JPG + PNG détouré approximatif)
```

### Galerie chantiers

Chaque maquette affiche 9 chantiers. Un clic sur une vignette
(`<button class="shot-open" data-projet="…">`) ouvre `galerie.js` : visionneuse
plein écran avec les autres photos du chantier, flèches, miniatures, clavier, swipe.
Les albums (titres, ordre, légendes) sont décrits dans `projets.js`, régénéré par
`scripts/build-albums` à partir du dossier photos source de Lou.

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
- **Réalisations** : 9 albums de photos réelles en place (`assets/img/realisations/`).
  Titres volontairement descriptifs (pas de nom de client ni d'adresse) ; légendes,
  ordre et sélection à valider avec Lou dans `assets/js/projets.js`.
- **Prestations** : détail concret de chaque prestation, mention tarifaire.
- **Zone d'intervention** : Morvan + chantiers un peu partout (Bretagne, Bourgogne,
  Corse) ; à préciser avec Lou.
- **Contact** : créer l'adresse `contact@heritage-savoir-faire.fr` (ou autre),
  confirmer l'adresse postale (Saulieu / Alligny-en-Morvan).
- **Portrait de Lou** : aucune photo de Lou seul pour l'instant ; les sections
  « histoire » utilisent une photo de chantier (maison à toit courbe). Sur cette
  photo, l'ancienne adresse/tél d'entreprise sur la camionnette a été floutée.
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

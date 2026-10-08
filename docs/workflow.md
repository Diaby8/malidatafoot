# Workflow

## Le cycle d'un post

1. **Question.** Ce qu'on veut faire comprendre (un joueur, un match, un phénomène de jeu).
2. **Données.** On vérifie d'abord que la source est autorisée. Ensuite `python taches.py donnees`, puis `python taches.py tests`, qui doivent être tous verts.
3. **Analyse.** Elle est versionnée : SQL dans `sql/`, ou Python dans `malidata/`, jamais un calcul fait à la main hors du dépôt.
4. **Visuel.** D'abord en nouvelle DA, puis la grille numérotée des variantes (`python taches.py grille`). Diaby choisit.
5. **Versions.** X et TikTok du choix.
6. **Audit.** Les données sont recomptées depuis les fichiers bruts. On vérifie la logique, les mots, et le visuel à taille téléphone. Pour un post important, un recomptage indépendant.
7. **Publication.** Le texte explicatif est écrit par Diaby sur X. Le fichier publié est gardé dans `livrables/` (non suivi), et la décision est notée dans `docs/journal_des_gabarits.md`.

## Git

- `main` reste toujours propre : les tests passent et les visuels se régénèrent.
- Une branche par chantier : `source/api-football`, `visuel/carte-de-chaleur`, `post/sinayoko-debut-saison`…
- Des petits commits, avec un message en français qui dit ce qui change et pourquoi.
- **Jamais de clé, de mot de passe ou de fichier `.env` dans git.** Les clés vont dans des variables d'environnement, et plus tard dans les secrets du dépôt GitHub.
- Les données (`data/`) et les rendus (`outputs/`, `livrables/`) ne sont pas versionnés : ils se régénèrent.

## Les contrôles qui bloquent une publication

| Contrôle | Où |
|---|---|
| un test du pipeline rouge | `python taches.py tests` |
| un contrôle qualité en échec (minutes, buts recoupés avec le score officiel, doublons…) | étape `quality` du pipeline |
| une police non chargée dans une capture | les scripts `*.mjs` s'arrêtent d'eux-mêmes |
| un chiffre affiché non recompté, ou une phrase qui lui fait dire plus | audit |
| une source dont on n'a pas le droit de se servir | `docs/sources_de_donnees.md` |

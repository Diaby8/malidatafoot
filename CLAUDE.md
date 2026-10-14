# MaliDataFoot : à lire en premier

Projet de Diaby : le football malien expliqué par la data (@MaliDataFoot sur X, @malidatafoot sur TikTok).
C'est un projet pro de data engineering, d'analyse et de data science. Il faut être strict sur la réussite et la
crédibilité : uniquement des faits vérifiés, et un audit avant chaque envoi.

- **À lire en premier, toujours** : `docs/etat_du_projet.md` (où est quoi, la base de données, les sources, le workflow, les posts en cours). Le mettre à jour à chaque post et à chaque décision.
- **Langue** : français, réponses courtes et simples, peu de listes. Discuter l'objectif avant de produire quand c'est ambigu.
- **Règles** : les trois skills de `.claude/skills/` font foi. Les lire selon la tâche :
  - `malidatafoot-direction-artistique` pour tout visuel ;
  - `malidatafoot-donnees-et-audit` pour tout chiffre ou toute source ;
  - `malidatafoot-production` pour les textes, les vidéos et le workflow.
- **Commandes** : `python taches.py <tâche>` (voir `README.md`). Les visuels se fabriquent depuis `visuels/`. Les rendus vont dans `livrables/`.
- **Jamais** :
  - modifier `visuels/logo-verte.png` ;
  - mettre une clé ou un mot de passe dans le code ou dans la conversation ;
  - publier un chiffre non recompté ;
  - changer un texte ou un son d'une vidéo validée sans le montrer d'abord ;
  - redessiner un gabarit validé « dans l'esprit » au lieu de partir du vrai.
- **Avant de dire « c'est prêt »** :
  - `python taches.py tests` est vert ;
  - le rendu a été regardé à taille réelle et à taille téléphone ;
  - les polices sont chargées (les scripts de capture s'arrêtent sinon).
- **Avant toute idée de visuel, de sujet ou de source** : relire `docs/sources_de_donnees.md`, `docs/boite_a_idees.md`, `docs/journal_des_gabarits.md` et les skills, puis proposer en s'appuyant dessus (règle de Diaby du 14/10/2026). Ne jamais proposer de payer une source non vérifiée.
- **Idées de contenus** : le suivi de tous les sujets dans `docs/boite_a_idees.md`, l'inspiration dans `docs/banque_idees.md` (des exemples, pas une liste fermée ; toujours proposer plusieurs catégories).
- **Décisions** : chaque décision de forme ou de fond est notée en une ligne datée dans `docs/journal_des_gabarits.md`.

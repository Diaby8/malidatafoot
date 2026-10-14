# Audit strict du post 1 « La défense des Aigles » (14/10/2026)

Données : martj42 (fichier brut du 06/10/2026), matchs officiels (CAN, éliminatoires CAN et Mondial), amicaux et phase finale du Mondial exclus.

| Affirmation | Recompte indépendant | Verdict |
|---|---|---|
| Mali 0,44 but encaissé par match depuis 2020 | 22 buts en 50 matchs (fichier brut, sans le pipeline) | juste |
| 2e d'Afrique, derrière le Maroc, juste devant le Sénégal | Maroc 0,417 (20/48), Mali 0,440, Sénégal 0,444 (24/54) ; même ordre avec 10, 20, 30 ou 40 matchs minimum | juste |
| 0,99 de 2000 à 2019, « plus de deux fois moins » | 119 buts en 120 matchs ; 0,99 / 0,44 = 2,25 | juste |
| Face aux mêmes adversaires : environ 44 attendus, 22 encaissés | 43,7 (pipeline) ; 43,73 refait avec un autre code (scikit-learn, Elo de gold.elo_matchs) | juste |
| Le calendrier n'explique qu'un cinquième de la baisse | (0,99 − 43,7/50) / (0,99 − 0,44) = 0,21 | juste |
| 30 matchs sans encaisser sur 50 | 30 | juste |
| Adversaires « un peu moins forts » | Elo moyen 1 565 (2000-2019) contre 1 522 (depuis 2020) | juste |

Points de vigilance trouvés :
1. **2020 est l'année de départ la plus flatteuse** (rapport réel/attendu 0,50). Mais le résultat tient pour toute année de 2014 à 2023 (0,50 à 0,64) : à écrire dans le thread pour couper la critique « vous avez choisi 2020 ».
2. **Le Maroc a joué 31 de ses 48 matchs à domicile, le Mali 14 sur 50** (adversaires de même niveau : Elo moyen 1 531 contre 1 522). Ajout proposé au tweet 3 : c'est de l'analyse, pas une stat.
3. **Fin de la courbe (image 2)** : la ligne rouge monte en 2025-2026 (adversaires forts de la CAN 2025). Lecture juste, la légende suffit.
4. **Rafraîchir les données le jour de la publication** (martj42 bouge).
5. **Version TikTok** (carrousel 1080 × 1920) à faire.

## Limites à écrire dans le post (règle de Diaby : toujours dire les points faibles)
- 50 matchs : petit échantillon.
- Les 10 derniers matchs (CAN 2025 comprise) : 7 encaissés, contre 12,7 attendus (adversaires forts). La courbe remonte, mais reste sous l'attendu.
- Maroc-Mali (26/12/2025) : le modèle attend 3,78 buts, au-delà de tout ce qu'il a vu en 2000-2019 (2,51 au plus) : extrapolation. Sans ce match : 21 encaissés pour 40,0 attendus. Avec un plafond à 2 buts par match : 41,9 attendus. La conclusion tient.

## Image « Les limites » (carrousel TikTok, et image possible du tweet 5) : recompte du 14/10/2026
| Affirmation | Recompte | Verdict |
|---|---|---|
| Un seul but de plus et le Mali serait 3e | 23/50 = 0,46 : derrière le Sénégal (0,444), devant l'Égypte (0,519). Calculé dans `posts_video.py` (assert) | juste |
| Maroc 31 matchs à domicile sur 48, Mali 14 sur 50 | recompté dans le fichier brut martj42 par `posts_video.py` (domicile hors terrain neutre, ou match dans le pays) | juste |
| 7 buts sur les 10 derniers, pour 13 attendus | 7 et 12,67 (du 08/09/2025 au 29/09/2026) | juste |
| 3,78 attendus contre le Maroc chez lui ; sans ce match 21 pour 40 | 3,781 ; 21 et 39,95 | juste |
| 36 à 50 % de moins qu'attendu selon l'année de départ | rapports 0,498 à 0,637 sur 2014-2023 | juste |

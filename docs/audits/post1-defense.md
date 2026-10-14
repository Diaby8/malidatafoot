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

## Contre-vérification du rang (14/10/2026 au soir, demande de Diaby : « aucun piège »)
Code indépendant `poc/audits/verif_rang_post1.py` sur le fichier martj42 retéléchargé (identique à celui du pipeline).
- Autres équipes : même fichier, même règle pour les 53 sélections africaines (CAN ou éliminatoires depuis 2020).
- Périmètre : avec les amicaux, Mali 2e ; avec la phase finale du Mondial, Mali 1er (le Maroc et le Sénégal y encaissent) ; tout sauf amicaux, Mali 1er. L'exclusion du Mondial ne nous avantage pas.
- **Piège trouvé : le rang dépend de l'année de départ.** 2e depuis 2020 et 2021, 3e depuis 2017 à 2019 et 2024, 4e depuis 2014 à 2016 et 2022-2023. Toujours dans le top 4 (avec Maroc, Sénégal, Égypte). Corrigé : tweet 1 « au coude-à-coude », tweet 3 donne les rangs selon l'année, description TikTok idem.
- Fichier de contrôle match par match (Mali, Maroc, Sénégal) : `livrables/post1-defense/controle_matchs_mali_maroc_senegal.csv`.

## Refonte du 14/10/2026 (soir) : seulement les matchs joués, au score du terrain
- **Tapis verts** : `registre/forfaits.csv` (6 matchs 2020-2026, source pour chacun), appliqué dans `malidata/aigles.py` (`appliquer_forfaits`, testé). Mali-Tchad 2021 retiré (jamais joué) ; finale CAN 2025 remise à 0-1 (score du terrain, TAS en cours) ; Afrique du Sud-Lesotho 2-0 ; Tchad-Namibie et les deux matchs de la Guinée équatoriale retirés.
- **Croisement des scores** : martj42 contre RSSSF (158 matchs des éliminatoires du Mondial 2022, zone Afrique) et contre StatsBomb (52 matchs CAN 2023) : 0 écart. Reste à croiser les autres matchs du Mali avec une 3e source (page Wikipédia copiée par Diaby).
- **Nouveaux chiffres** : Mali 22 buts en 49 matchs (0,45), **3e** derrière le Sénégal (0,39) et le Maroc (0,44) ; 2000-2019 : 0,99 ; attendus 43,4 ; part du calendrier 0,20 ; 29 matchs sans encaisser ; rang selon l'année de départ : 4e (2014-2017, 2023), 3e (2018-2022, 2024) ; rapport réel/attendu 0,50 à 0,64 (2014-2023) ; 10 derniers : 7 pour 12,7 ; sans le match au Maroc : 21 pour 39,6.
- **Non audité** : les tapis verts d'avant 2020 (hors Mali, dont les 3-0 de 2000-2019 ont été relus et sont plausibles) ; ils ne touchent que les rangs « depuis 2014-2019 ».
- **Courbe** : moyenne sur 20 matchs (2B), choisie après rejet de la 2A (fausses chutes) et de la 2D (le cumul fait croire que ça empire). Classement des 10 premiers, mise en page inchangée (9e Angola 0,786 et 10e Afrique du Sud 0,791 affichés tous deux 0,79 : question posée à Diaby).

## Décision finale (14/10/2026, soir) : résultats officiels, tapis verts compris
Diaby : « des tapis verts, c'est officiel, donc autant les compter ». `REGLE_TAPIS_VERT = "officiel"` ; le registre reste vérifié.
Chiffres : Mali 22 en 50 (0,44), 2e (Maroc 0,42, Sénégal 0,44) ; attendus 43,7 ; calendrier 0,21 ; 30 sans encaisser ; rapports 0,50 à 0,64 ; 10 derniers 7 pour 12,7 ; sans le Maroc 21 pour 40,0.
Dit dans le post : tweet 4 « Résultats officiels, tapis verts compris : pour le Mali, un seul, Mali-Tchad (3-0, 28/03/2021) ». Pour mémoire, au score du terrain le Mali serait 3e (Sénégal 0,39, Maroc 0,44, Mali 0,45) : un supporter sénégalais peut le relever (finale CAN 2025, TAS en cours) ; réponse prête dans ce fichier.
- Croisement FBref (pages copiées par Diaby, 14/10/2026) : 21 matchs officiels du Mali (éliminatoires Mondial 2026, éliminatoires CAN 2025, CAN 2025) : 0 écart. FBref range les matchs par saison du tournoi (la page « 2024 » ne contient que les amicaux de 2024). Bilan : 32 des 50 matchs du Mali recoupés (RSSSF 6, StatsBomb 5, FBref 21) ; reste les pages FBref 2021, 2023 et 2027.

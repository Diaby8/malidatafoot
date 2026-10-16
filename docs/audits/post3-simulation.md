# Audit du post 3 « On a joué le groupe 100 000 fois » (16/10/2026)

## Chiffres du modèle (pipeline : outputs/analyses/simulation_groupe_k.json, relancé le 15/10/2026)
- Qualif du Mali 98,5 % ; premier 84,6 % ; victoire à domicile 77 % (nul 16, défaite 7) ; à Kigali 44 % (nul 30, défaite 26).
- Victoire à domicile + défaite à Kigali : premier 73,6 %, qualifié 98,8 % (scénario ajouté au pipeline le 15/10).
- Test : appris sur 2 232 matchs (2000-2019), testé sur 995 (2020-2026). Tranche 75-100 % : annoncé 85, réel 82. Tranche 60-75 % : annoncé 67, réel 58.

## Faits sur le Rwanda (angle « le Rwanda est faible, le piège c'est le nul chez lui », Diaby 15/10)
| Fait | Source 1 | Source 2 |
|---|---|---|
| Groupe K après 2 journées : Rwanda 6 pts (5-2), Mali 6 pts (4-1), départage aux buts marqués | martj42 | Bénin Web TV, Africatopsports, foot-africa ; règlement CAF art. 14 (éliminatoires 2025) |
| Rwanda 119e FIFA (classement d'octobre 2026), Mali 47e | registre/classement_fifa.csv (FIFA, 07/10) | The New Times, 07/10/2026 (« climbed nine places to 119th ») |
| Dernière CAN du Rwanda : 2004 (sa seule) | The New Times (« 22-year AFCON wait ») | AllAfrica, « Where are Rwanda's Afcon 2004 heroes now? » |
| Rwanda à domicile contre des équipes africaines, matchs officiels depuis 2020 : 17 matchs, 4 V, 7 N, 6 D | martj42 (calcul) | à recouper match par match si on publie le bilan exact |
| Rwanda 0-3 Mali, 11/11/2021, Kigali (élim. Mondial 2022) | martj42 | KT Press (12/11/2021) |
| Rwanda 1-1 Sénégal, 09/09/2023 (élim. CAN 2023, Huye/Butare) | martj42 | KT Press, beIN Sports, SuperSport |
| Rwanda 0-0 Nigeria, 10/09/2024, Kigali (élim. CAN 2025) | martj42 | SuperSport, AllAfrica |

Point ouvert : le stade de Mali-Rwanda (Bamako probable, comme Mali-Cap-Vert) à confirmer avant publication ; sur les images on écrit « à domicile ».

## Vérification demandée par Diaby (16/10) : « 44 % seulement de gagner au Rwanda ? »
- Le 44 % est la moyenne africaine : visiteur plus fort de 200 à 300 pts d'Elo, matchs officiels africains depuis 2000 : 215 matchs, 44 % V, 32 % N, 24 % D (depuis 2015 : 75 matchs, 45 / 35 / 20). Le modèle colle donc à l'histoire du continent.
- Mais le Mali fait beaucoup mieux : visiteur avec au moins 200 pts d'Elo de plus, depuis 2015 : 9 matchs, 8 V, 1 N, 0 D (pipeline, `exterieur_contre_plus_faible`). Robustesse du seuil : ≥100 pts 12 V 4 N 3 D sur 19 ; ≥150 pts 11 V 2 N 1 D sur 14 ; ≥250 pts 7 sur 7.
- Les 9 matchs recoupés : 2020-2026 déjà recoupés au post 1 (FBref, RSSSF, presse) ; Soudan du Sud 0-3 (04/06/2016, Radio Tamazuj), Soudan du Sud 0-3 (09/09/2018, Wikipédia groupe C), Tchad 0-2 (17/11/2019, N'Djamena, Alwihda Info).
- Angle retenu (Diaby, 16/10) : « le modèle sous-estime les Aigles ? ». Limite à dire : 9 matchs, c'est peu.
- Lieux vérifiés (16/10) : les 14 matchs du seuil 150 pts se sont joués dans le pays hôte (martj42 « neutral = False » + presse pour les cas douteux : Tchad-Mali 2025 au stade Idriss Déby Itno de N'Djamena, tchadinfos ; Liberia-Mali 2026 à Monrovia, dailysports ; Guinée-Bissau 2024 à Bissau et Congo 2023 à Brazzaville, 11v11). Scores des 5 matchs en plus du seuil 200 : Botswana 2-1 (Daily News Botswana), Guinée éq. 0-1 (11v11), Burundi 1-1 (Wikipédia, afrik-foot), Kenya 0-1 et Mozambique 0-1 (recoupés au post 1 / audit des compos).
- Formulation (Diaby, 16/10) : « nettement favori », pas « favori » : en comptant tous les déplacements où le Mali était favori (écart Elo > 0), c'est 20 matchs, 12 V 5 N 3 D (60 %). Les 6 matchs de favori léger (0 à 150 pts) : Bénin 1-1 (2015, 148 pts), Gabon 0-0 (2017), Gabon 0-1 (2018), Ouganda 0-0 (2021), Côte d'Ivoire 2-1 (CAN 2023, quart), Ghana 1-0 (2025). Le Rwanda est à 248 pts : la comparaison avec le seuil de 150 pts est la bonne. Quel que soit le seuil (100, 150, 200 pts), le Mali gagne plus souvent que les 44 % du modèle (63 %, 79 %, 89 %).

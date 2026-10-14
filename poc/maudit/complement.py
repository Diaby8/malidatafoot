"""A lancer apres analyse.py : nuls de groupe recalibres, comparaison de l'exces de nuls, verdict."""
import json, numpy as np, pandas as pd
R = json.load(open('resultats.json'))
d = pd.DataFrame(R['mali_matchs']); g = d[d.tour == 'groupe']
t = R['q5_nuls']['toutes_phases_finales_1994_2026']; r = t['groupes_reel'] / t['groupes_attendu']
def pb(ps):
    x = np.array([1.])
    for p in ps: x = np.convolve(x, [1 - p, p])
    return x
pn = np.clip(g.pN * r, 0, 1); dist = pb(pn); k = int((g.resultat == 'N').sum())
R['q5_nuls']['mali_groupes_recalibre'] = {'facteur': round(r, 3), 'nuls_attendus': round(float(pn.sum()), 2), 'p_aussi_haut_ou_plus': round(float(dist[k:].sum()), 4)}
c = pd.DataFrame(R['q4_comparaison_depuis_1994']['equipes']); c['exces_nuls_par_match'] = (c.nuls - c.nuls_attendus) / c.matchs
R['q5_nuls']['comparaison_exces_nuls_par_match'] = c.sort_values('exces_nuls_par_match', ascending=False)[['equipe', 'nuls', 'nuls_attendus', 'matchs', 'exces_nuls_par_match']].round(3).to_dict('records')
R['verdict'] = {'mot': 'plafond', 'resume': "Les resultats du Mali en phase finale collent a son niveau Elo (legerement au-dessus) ; l'absence de titre est l'issue la plus probable vu ce niveau (P(0 titre) = 62 %). Pas de malchance mesurable, sauf un exces de nuls en phase de groupes qui ne coute pas de points.",
 'reserves': ["1972 : Elo peu fiable (peu de matchs avant, plusieurs equipes encore a 1500).", "Le score de martj42 inclut la prolongation ; prolongation modelisee comme 1/3 de match.", "shootouts.csv incomplet : 3e place 2024 Afrique du Sud - RD Congo ajoutee a la main.", "Titres attendus : tours supposes independants, adversaires des tours non joues = ceux de l'equipe qui a elimine le Mali.", "Le modele sous-estime les nuls en phase finale pour tout le monde (29,2 % reels contre 23,5 % annonces, 606 matchs)."]}
json.dump(R, open('resultats.json', 'w'), ensure_ascii=False, indent=1)

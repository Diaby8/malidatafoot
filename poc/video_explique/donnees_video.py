"""Données de la vidéo explicative, toutes tirées des événements StatsBomb Open Data (CAN 2023, 5 matchs du Mali).
usage : python3 -I donnees_video.py <dossier des events json> <sortie.json>"""
import json, sys, os, collections
D, OUT = sys.argv[1], sys.argv[2]
MATCHS = [3920391, 3920404, 3920417, 3922244, 3922659]
ICI = os.path.dirname(os.path.abspath(__file__))
R = {'source': 'StatsBomb Open Data, CAN 2023 (competition 1267, saison 107), événements des 5 matchs du Mali',
     'tirs': [], 'recuperations': [], 'reseau': {}, 'action': {}}
passes = collections.Counter(); loc = collections.defaultdict(list); minutes = collections.Counter()
for m in MATCHS:
    E = json.load(open(os.path.join(D, f'ev_{m}.json')))
    for e in E:
        if e.get('team', {}).get('name') != 'Mali': continue
        t = e['type']['name']
        if t == 'Shot':
            R['tirs'].append({'x': e['location'][0], 'y': e['location'][1], 'xg': round(e['shot']['statsbomb_xg'], 4),
                              'but': e['shot']['outcome']['name'] == 'Goal', 'penalty': e['shot']['type']['name'] == 'Penalty', 'match': m})
        if t in ('Ball Recovery', 'Interception') and 'location' in e:
            # récupération réussie seulement : Ball Recovery sans échec, interception gagnée (Won, Success In Play / Out)
            ok = (not e.get('ball_recovery', {}).get('recovery_failure')) if t == 'Ball Recovery' else e['interception']['outcome']['name'] in ('Won', 'Success In Play', 'Success Out')
            if ok: R['recuperations'].append({'x': e['location'][0], 'y': e['location'][1], 'type': t})
        if t == 'Pass' and 'outcome' not in e.get('pass', {}) and e['pass'].get('recipient') and e['pass'].get('type', {}).get('name') not in ('Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off'):
            a, b = e['player']['name'], e['pass']['recipient']['name']
            passes[tuple(sorted((a, b)))] += 1; loc[a].append(e['location'])
# réseau : joueurs avec au moins 60 passes réussies dans le jeu, liens d'au moins 12 passes entre deux joueurs
noeuds = {p: [round(sum(l[0] for l in L) / len(L), 2), round(sum(l[1] for l in L) / len(L), 2), len(L)] for p, L in loc.items() if len(L) >= 60}
R['reseau'] = {'definition': 'passes réussies dans le jeu (hors coups de pied arrêtés) ; position = moyenne des points de départ des passes du joueur ; joueurs avec au moins 60 passes, liens d\'au moins 12 passes',
               'noeuds': noeuds, 'liens': [[a, b, n] for (a, b), n in passes.items() if n >= 12 and a in noeuds and b in noeuds]}
# l'action : arrêt sur image au moment de la tête de Sinayoko (Namibie-Mali, index 922)
E = json.load(open(os.path.join(D, 'ev_3920417.json'))); s = next(e for e in E if e.get('index') == 922)
R['action'] = {'tir': {'x': s['location'][0], 'y': s['location'][1], 'joueur': s['player']['name'], 'xg': round(s['shot']['statsbomb_xg'], 4), 'resultat': s['shot']['outcome']['name'],
               'fin': s['shot']['end_location']},
               'joueurs': [{'x': p['location'][0], 'y': p['location'][1], 'mali': p['teammate'], 'nom': p['player']['name'], 'poste': p['position']['name']} for p in s['shot']['freeze_frame']]}
# présence : toutes les actions du Mali avec le ballon (passes, conduites, réceptions, tirs, dribbles, récupérations), 5 matchs, en cases de 6 x 5 yards
TYPES = ('Pass', 'Carry', 'Ball Receipt*', 'Shot', 'Dribble', 'Ball Recovery', 'Interception', 'Clearance', 'Block')
grille = [[0] * 20 for _ in range(16)]; n_act = 0
for m in MATCHS:
    for e in json.load(open(os.path.join(D, f'ev_{m}.json'))):
        if e.get('team', {}).get('name') == 'Mali' and e['type']['name'] in TYPES and 'location' in e:
            x, y = e['location'][:2]; grille[min(15, int(y // 5))][min(19, int(x // 6))] += 1; n_act += 1
# carte lissée (noyau gaussien, écart-type 4 yards) sur une grille de 2 x 2 yards, pour l'affichage
import math
K = [[math.exp(-((i * 6 + 3 - x) ** 2 + (j * 5 + 2.5 - y) ** 2) / (2 * 4 ** 2)) for i in range(20) for j in range(16)] for x, y in [(0, 0)]]
lisse = [[0.0] * 60 for _ in range(40)]
for j in range(16):
    for i in range(20):
        v = grille[j][i]
        if not v: continue
        cx, cy = i * 6 + 3, j * 5 + 2.5
        for b in range(40):
            for a in range(60):
                d2 = (a * 2 + 1 - cx) ** 2 + (b * 2 + 1 - cy) ** 2
                if d2 < 200: lisse[b][a] += v * math.exp(-d2 / 32)
mx = max(max(r) for r in lisse); lisse = [[round(v / mx, 3) for v in r] for r in lisse]
R['presence'] = {'lisse': lisse, 'definition': 'actions du Mali avec le ballon (passes, conduites, réceptions, tirs, dribbles, récupérations, interceptions, dégagements, contres), cases de 6 x 5 yards', 'n': n_act, 'grille': grille}
# tous les événements de Namibie-Mali qui ont une position, dans l'ordre du match, ramenés dans le sens d'attaque du Mali (vers x = 120)
E = json.load(open(os.path.join(D, 'ev_3920417.json')))
R['evenements'] = {'n_total': len(E), 'points': [[round(e['location'][0] if e['team']['name'] == 'Mali' else 120 - e['location'][0], 1),
                    round(e['location'][1] if e['team']['name'] == 'Mali' else 80 - e['location'][1], 1), 1 if e['team']['name'] == 'Mali' else 0]
                   for e in E if 'location' in e and e['period'] <= 2]}
xt = json.load(open(os.path.join(ICI, '..', 'xt', 'xt_grid.json')))
R['xt'] = {'grille': xt['grille'], 'valeurs': xt['valeurs']}
np_ = [t for t in R['tirs'] if not t['penalty']]
R['resume'] = {'tirs': len(R['tirs']), 'tirs_hors_penalty': len(np_), 'buts': sum(t['but'] for t in R['tirs']), 'xg_total': round(sum(t['xg'] for t in R['tirs']), 2),
               'npxg': round(sum(t['xg'] for t in np_), 2), 'recuperations': len(R['recuperations']), 'hauteur_moyenne_recup_yards': round(sum(r['x'] for r in R['recuperations']) / len(R['recuperations']), 1),
               'noeuds': len(noeuds), 'liens': len(R['reseau']['liens']), 'actions_presence': n_act}
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R['resume'], ensure_ascii=False)); print(sorted(noeuds, key=lambda p: -noeuds[p][2]))

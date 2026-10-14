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
            ok = not (t == 'Ball Recovery' and e.get('ball_recovery', {}).get('recovery_failure'))
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
xt = json.load(open(os.path.join(ICI, '..', 'xt', 'xt_grid.json')))
R['xt'] = {'grille': xt['grille'], 'valeurs': xt['valeurs']}
np_ = [t for t in R['tirs'] if not t['penalty']]
R['resume'] = {'tirs': len(R['tirs']), 'tirs_hors_penalty': len(np_), 'buts': sum(t['but'] for t in R['tirs']), 'xg_total': round(sum(t['xg'] for t in R['tirs']), 2),
               'npxg': round(sum(t['xg'] for t in np_), 2), 'recuperations': len(R['recuperations']), 'hauteur_moyenne_recup_yards': round(sum(r['x'] for r in R['recuperations']) / len(R['recuperations']), 1),
               'noeuds': len(noeuds), 'liens': len(R['reseau']['liens'])}
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R['resume'], ensure_ascii=False)); print(sorted(noeuds, key=lambda p: -noeuds[p][2]))

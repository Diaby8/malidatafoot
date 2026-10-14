"""Sujet 19 : le rassemblement de septembre 2026 en data. Recompte depuis les fichiers bruts du dépôt.
Sorties : analyse.json (dans ce dossier)."""
import csv, json, datetime as dt, statistics as st, unicodedata
from pathlib import Path
REPO = Path('/home/claude/repo/malidatafoot')
ICI = Path(__file__).parent

def n(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

R = list(csv.DictReader(open(REPO / 'registre/joueurs.csv', encoding='utf-8')))
L = [x for x in R if x['liste_sept_2026'] == 'oui']
assert len(L) == 26

# ---- âge (au 25/09/2026, premier match du rassemblement)
REF = dt.date(2026, 9, 25)
def age(d, ref=REF):
    b = dt.date.fromisoformat(d); return ref.year - b.year - ((ref.month, ref.day) < (b.month, b.day))
ages = {x['nom']: age(x['date_naissance']) for x in L if x['date_naissance']}
A = sorted(ages.values())
age_inconnu = [x['nom'] for x in L if not x['date_naissance']]

# ---- sélections au 31/03/2026
caps = {x['nom']: int(x['selections_au_2026_03_31']) for x in L if x['selections_au_2026_03_31'] != ''}
caps_inconnu = [x['nom'] for x in L if x['selections_au_2026_03_31'] == '']
premiere = [x['nom'] for x in L if 'première convocation' in x['note']]

# ---- effectif CAN 2023 (feuilles de match StatsBomb des 5 matchs du Mali)
MATCHS = [3920391, 3920404, 3920417, 3922244, 3922659]
can = {}
for m in MATCHS:
    for t in json.load(open(REPO / f'data/bronze/lineups/{m}.json', encoding='utf-8')):
        if t['team_name'] == 'Mali':
            for p in t['lineup']: can[p['player_name']] = p.get('player_nickname')
can_noms = {n(k) for k in can} | {n(v) for v in can.values() if v}
def a_la_can(x): return n(x['nom']) in can_noms or (x['alias'] and n(x['alias']) in can_noms)
rescapes = [x['nom'] for x in L if a_la_can(x)]
# couverture des dates de naissance pour l'effectif 2023 (registre seulement)
idx = {}
for x in R:
    for k in (x['nom'], x['alias']):
        if k: idx[n(k)] = x
can_dates = {}
for nom, nick in can.items():
    x = idx.get(n(nom)) or (idx.get(n(nick)) if nick else None)
    can_dates[nom] = x['date_naissance'] if x and x['date_naissance'] else None

# ---- tranches de sélections et rescapés
def tranche(c):
    return '0' if c == 0 else '1-9' if c < 10 else '10-29' if c < 30 else '30-49' if c < 50 else '50+'
TR = ['0', '1-9', '10-29', '30-49', '50+', 'inconnu']
cols = {t: [] for t in TR}
for x in L:
    nom = x['nom']
    if nom in caps: t = tranche(caps[nom])
    elif nom in premiere: t = '0'   # première convocation = aucune sélection avant septembre
    else: t = 'inconnu'
    cols[t].append({'nom': nom, 'can2023': nom in rescapes})

# ---- clubs : pays et championnat 2026-2027 (vérifié sur le web le 14/10/2026, voir sources)
CLUB = {  # club -> (pays du club, top 5 en 2026-27 ?)
 'Young Africans': ('Tanzanie', False), 'Stade Lavallois': ('France', False), 'Stade Malien': ('Mali', False), 'Genk': ('Belgique', False),
 'Paris FC': ('France', True), 'Zbrojovka Brno': ('Tchéquie', False), 'Charleroi ou Latina': ('Belgique ou Italie', False),
 'Reims': ('France', False), 'Çaykur Rizespor': ('Turquie', False), 'Baltika Kaliningrad': ('Russie', False), 'Angers': ('France', True),
 'Valence': ('Espagne', True), 'Lens ou RB Leipzig': ('France ou Allemagne', True), 'Rayon Sports': ('Rwanda', False), 'Brest': ('France', True),
 'Lecce': ('Italie', True), 'Brentford': ('Angleterre', True), 'West Bromwich Albion': ('Angleterre', False), 'Abha': ('Arabie saoudite', False),
 'Parme': ('Italie', True), 'Feyenoord': ('Pays-Bas', False), 'Schalke 04': ('Allemagne', True), 'Fenerbahçe': ('Turquie', False)}
CONT = {'Tanzanie': 'Afrique', 'Mali': 'Afrique', 'Rwanda': 'Afrique', 'Arabie saoudite': 'Asie'}
clubs = []
for x in L:
    pays, top5 = CLUB[x['club']]
    zone = 'top5' if top5 else CONT.get(pays, 'Europe (hors top 5)')
    clubs.append({'nom': x['nom'], 'club': x['club'], 'pays': pays, 'zone': zone, 'a_confirmer': x['club_a_confirmer'] == 'oui'})
pays_surs = {c['pays'] for c in clubs if ' ou ' not in c['pays']}
from collections import Counter
zones = Counter(c['zone'] for c in clubs)

# ---- buteurs du rassemblement
res = [r for r in csv.DictReader(open(REPO / 'data/bronze/international_results/results.csv', encoding='utf-8'))
       if r['date'] in ('2026-09-25', '2026-09-29', '2026-10-04') and 'Mali' in (r['home_team'], r['away_team'])]
gs = [g for g in csv.DictReader(open(REPO / 'data/bronze/international_results/goalscorers.csv', encoding='utf-8'))
      if g['date'] in ('2026-09-25', '2026-09-29', '2026-10-04')]
derniere_date_buteurs = max(g['date'] for g in csv.DictReader(open(REPO / 'data/bronze/international_results/goalscorers.csv', encoding='utf-8')))

out = {
 'liste': {'joueurs': 26, 'par_poste': dict(Counter(x['poste'] for x in L)), 'source': 'registre/joueurs.csv, liste_sept_2026 = oui (liste Da Silva du 10/09/2026)'},
 'age': {'reference': str(REF), 'connus': len(A), 'inconnus': age_inconnu, 'mediane': st.median(A), 'moyenne': round(st.mean(A), 1),
         'min': A[0], 'max': A[-1], 'moins_de_23_strict': sum(a < 23 for a in A), '23_ou_moins': sum(a <= 23 for a in A),
         '30_ou_plus': sum(a >= 30 for a in A), 'plus_de_30_strict': sum(a > 30 for a in A),
         'repartition': dict(sorted(Counter(A).items())), 'detail': ages,
         'nes_2002_2003': sorted(x['nom'] for x in L if x['date_naissance'][:4] in ('2002', '2003'))},
 'selections': {'date': '2026-03-31', 'connues': len(caps), 'inconnues': caps_inconnu, 'premiere_convocation': premiere,
                'zero_au_31_mars': sorted(k for k, v in caps.items() if v == 0), 'mediane': st.median(caps.values()), 'total_connu': sum(caps.values()),
                'colonnes': cols, 'detail': caps,
                'attention': "Le Mali a joué Iran 2-0 Mali (amical, 4 juin 2026) après le 31 mars : les sélections du registre ne le comptent pas."},
 'can2023': {'effectif': len(can), 'source': 'feuilles de match StatsBomb, 5 matchs du Mali (' + ', '.join(map(str, MATCHS)) + ')',
             'rescapes': rescapes, 'nb_rescapes': len(rescapes),
             'selections_des_rescapes': sum(caps[r] for r in rescapes), 'part_des_selections_connues': round(sum(caps[r] for r in rescapes) / sum(caps.values()), 3),
             'dates_naissance_connues': sum(1 for v in can_dates.values() if v), 'dates_inconnues': sorted(k for k, v in can_dates.items() if not v),
             'comparaison_age': "impossible avec le dépôt : dates de naissance connues pour une partie seulement de l'effectif 2023 (registre)"},
 'clubs': {'detail': clubs, 'zones': dict(zones), 'pays_distincts_surs': len(pays_surs), 'pays': sorted(pays_surs),
           'au_mali': [c['nom'] for c in clubs if c['pays'] == 'Mali'],
           'a_confirmer': [c['nom'] + ' (' + c['club'] + ')' for c in clubs if c['a_confirmer']],
           'sources_championnats': {
             'Ligue 1 2026-27 (Paris FC, Angers, Brest, Lens oui ; Reims, Laval non)': 'en.wikipedia.org/wiki/2026–27_Ligue_1 (lu le 14/10/2026)',
             'Schalke 04 promu en Bundesliga': 'en.wikipedia.org/wiki/2025–26_2._Bundesliga',
             'Serie A : relégués Pisa, Verona, Cremonese ; Lecce sauvé': 'fantamaster.it, verdetti 38e journée 2025-26',
             'Premier League : relégués West Ham, Burnley, Wolves ; WBA en Championship 2026-27': 'news.williamhill.com',
             'LaLiga : relégués Mallorca, Girona, Oviedo': 'lafm.com.co',
             'RB Leipzig en Bundesliga': 'non revérifié (Haïdara est dans un top 5 que ce soit Lens ou Leipzig)'}},
 'matchs': {'resultats_martj42': [f"{r['date']} {r['home_team']} {r['home_score']}-{r['away_score']} {r['away_team']} ({r['tournament']}, {r['city']})" for r in res],
            'buteurs_dans_goalscorers_csv': len(gs), 'goalscorers_csv_s_arrete_au': derniere_date_buteurs,
            'buteurs_web': {
              'Mali 3-1 Cap-Vert (25/09, Bamako)': 'Ange Martial Tia 5e ; Sidny (Lopes) Cabral 10e pour le Cap-Vert ; Nene Dorgeles 39e et 50e (Africa Top Sports) ou 51e (11v11). Sources : africatopsports.com, 11v11.com, fr.apanews.net. Africa Top Sports écrit « Mamady Tia » et « Steven Lopes Cabral » : erreurs de nom probables.',
              'Liberia 0-1 Mali (29/09, Monrovia)': 'Ange Martial Tia, seul but (APA News) ; 79e selon le skill (état du 8/10), minute non recoupée ici (page 11v11 non lue).',
              'Maroc 1-1 Mali (4/10, Tanger)': 'Ezzalzouli 35e, Gaoussou Diarra 77e (skill, état du 8/10 ; non recoupé ici)'}},
}
json.dump(out, open(ICI / 'analyse.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ('age',)}, ensure_ascii=False)[:900])
print(out['selections']['colonnes'])
print(out['can2023']['rescapes'], out['can2023']['selections_des_rescapes'], out['can2023']['part_des_selections_connues'], out['can2023']['dates_naissance_connues'])
print(out['clubs']['zones'], out['clubs']['pays_distincts_surs'], out['clubs']['pays'])
print(out['matchs']['resultats_martj42'], out['matchs']['buteurs_dans_goalscorers_csv'], out['matchs']['goalscorers_csv_s_arrete_au'])

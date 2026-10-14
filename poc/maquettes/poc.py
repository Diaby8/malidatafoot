"""POC : plans clés de tous les sujets (maquettes, format TikTok 1080 x 1920, DA vidéo)."""
import json, math, datetime as dt
SH = '/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
exec(open(SH + '/maq_a.py', encoding='utf-8').read().split('# 1 : le score')[0])
exec(open(SH + '/maq_terrain.py', encoding='utf-8').read().split('# A : le terrain penche')[0].split("exec(open(")[0])
src_t = open(SH + '/maq_terrain.py', encoding='utf-8').read()
exec(src_t[src_t.index('def terrain'):src_t.index('# A : le terrain penche')])
SB = '<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
P = json.load(open(SH + '/poc_data.json', encoding='utf-8'))
A = json.load(open('../outputs/analyses/defense_afrique.json', encoding='utf-8'))
T = json.load(open(SH + '/poc_jeu/transitions.json', encoding='utf-8'))
S = json.load(open(SH + '/poc_jeu/styles.json', encoding='utf-8'))
R = json.load(open(SH + '/poc_maudit/resultats.json', encoding='utf-8'))
SIM = json.load(open('../outputs/analyses/simulation_groupe_k.json', encoding='utf-8'))
out = {}
def sv(inner): return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{inner}</svg>'
def txt(x, y, t, size=26, w=700, col='#064A25', anchor='start', fam='SC', it=False):
    st = f'font:{"italic " if it else ""}{w} {size}px {fam};fill:{col}'
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{st}">{t}</text>'
def big(x, y, t, size=80, col='#064A25', anchor='start'): return txt(x, y, t, size, 900, col, anchor, 'BC', True)

# ---------------- B : trois questions
E = A['equipes'][:5]; b = ''
for i, e in enumerate(E):
    y = 640 + i * 130; m = e['equipe'] == 'Mali'; L = e['par_match'] / 0.6 * 560
    b += f'<div style="position:absolute;left:64px;top:{y}px;display:flex;align-items:center;gap:16px">{drap(e["equipe"],54)}<span style="font:800 32px SC;letter-spacing:.04em;color:{"#0B7A3B" if m else "#04331A"}">{FRN[e["equipe"]].upper()}</span></div>'
    b += f'<div style="position:absolute;left:64px;top:{y+66}px;width:{L:.0f}px;height:30px;border-radius:4px;background:{"#0B7A3B" if m else "#FFF3C4"}"></div><div style="position:absolute;left:{64+L+16:.0f}px;top:{y+58}px;font:italic 900 46px/1 BC;color:#064A25">{fr(e["par_match"])}</div>'
b += '<div class="bigR" style="top:1300px"><b>OUI</b><span>2e DÉFENSE D\'AFRIQUE DEPUIS 2020<br>MÊME FACE AUX <em>MÊMES ADVERSAIRES</em></span></div>'
out['b1'] = pageT('QUESTION 1 · <b>LA DÉFENSE EST-ELLE VRAIMENT MEILLEURE ?</b>', 'QUESTION 1', 'LA DÉFENSE', '', b, 'Buts encaissés par match officiel depuis 2020 · Données : martj42')
# B3 : la courbe de force depuis 1990
el = [(dt.date.fromisoformat(d), e) for d, e in P['elo'] if d >= '1990']
x0, x1, y0, y1 = 110, 950, 620, 1180; t0, t1 = dt.date(1990, 1, 1), dt.date(2027, 1, 1); lo, hi = 1350, 1800
X = lambda d: x0 + (d - t0).days / (t1 - t0).days * (x1 - x0); Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)
g = f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>'
for a in (1990, 2000, 2010, 2020): g += txt(X(dt.date(a, 1, 1)), y1 + 40, a, 26, 700, '#064A25', 'middle')
for v in (1400, 1600, 1800): g += txt(x0 - 14, Y(v) + 9, v, 24, 700, '#064A25', 'end') + f'<line x1="{x0}" y1="{Y(v):.0f}" x2="{x1}" y2="{Y(v):.0f}" stroke="#FCE38A" stroke-width="2"/>'
g += '<path d="M' + 'L'.join(f'{X(d):.1f} {Y(v):.1f}' for d, v in el) + '" fill="none" stroke="#0B7A3B" stroke-width="5" stroke-linejoin="round"/>'
for d, v, lab, dy in ((dt.date(2024, 1, 30), 1772, '2024 · 1772', -30), (dt.date(2004, 2, 7), 1760, '2004 · 1760', -30)):
    g += f'<circle cx="{X(d):.0f}" cy="{Y(v):.0f}" r="12" fill="#D4252A"/>' + txt(X(d), Y(v) + dy, lab, 28, 800, '#D4252A', 'middle')
b = sv(g) + '<div class="bigR" style="top:1290px"><b>2024</b><span>LE PLUS HAUT NIVEAU DU MALI, DEVANT 2022 ET 2004<br>SELON NOTRE INDICE DE FORCE (<em>ELO</em>)</span></div>'
out['b3'] = pageT('QUESTION 3 · <b>LA GÉNÉRATION LA PLUS FORTE ?</b>', 'QUESTION 3', 'LA PLUS FORTE ?', '', b, 'Force Elo du Mali après chaque match depuis 1990 · Calcul MaliDataFoot · Données : martj42')

# ---------------- C : la boîte à outils
b = f'''<div style="position:absolute;left:64px;top:620px;display:flex;align-items:center;gap:22px">{drap("Morocco",90)}<div><div style="font:800 30px SC;letter-spacing:.05em">MAROC</div><div style="font:italic 900 110px/1 BC;color:#064A25">2033 <span style="color:#D4252A;font-size:70px">−8</span></div></div></div>
<div style="position:absolute;left:64px;top:860px;display:flex;align-items:center;gap:22px">{drap("Mali",90)}<div><div style="font:800 30px SC;letter-spacing:.05em;color:#0B7A3B">MALI</div><div style="font:italic 900 110px/1 BC;color:#0B7A3B">1739 <span style="font-size:70px">+8</span></div></div></div>
<div style="position:absolute;left:64px;top:1120px;font:800 36px/1.3 SC;letter-spacing:.04em">CHAQUE ÉQUIPE A DES POINTS DE FORCE.<br>UN NUL CONTRE PLUS FORT QUE SOI,<br><span style="color:#D4252A">ÇA RAPPORTE DES POINTS.</span></div>'''
out['c1'] = pageT('OUTIL 1 · <b>LA FORCE D\'UNE ÉQUIPE</b>', 'OUTIL 1', 'LA FORCE (ELO)', '', b, 'Maroc 1-1 Mali, 4 octobre 2026 · Force avant le match et points échangés · Calcul MaliDataFoot')
# C2 : deux tirs réels, taille = chance de but
pen = {'loc': [107.5, 33.8], 'xg': 0.442}; gol = {'loc': [113.4, 49.7], 'xg': 0.231}  # Mali 2-0 Afrique du Sud, CAN 2023 : Haïdara 48e (à côté), Sinayoko 65e (but)
def demi(extra):  # demi-terrain vu de face, attaque vers le haut ; x StatsBomb 60-120 -> vertical, y 0-80 -> horizontal
    L = 'stroke="#FFF6D0" stroke-width="0.6" fill="none"'
    return f'''<svg viewBox="-2 -2 84 64" width="100%" height="100%"><rect x="0" y="0" width="80" height="60" fill="#0B7A3B"/><rect x="0" y="0" width="80" height="60" {L}/>
<rect x="18" y="0" width="44" height="18" {L}/><rect x="30" y="0" width="20" height="6" {L}/><circle cx="40" cy="12" r=".5" fill="#FFF6D0"/><path d="M32 18A10 10 0 0 0 48 18" {L}/><rect x="36" y="-1.6" width="8" height="1.6" fill="#FFF6D0"/>{extra}</svg>'''
pt = lambda s: (s['loc'][1], 120 - s['loc'][0])
(px, py), (gx, gy) = pt(pen), pt(gol)
ex = f'<circle cx="{px}" cy="{py}" r="{1+7*pen["xg"]**.5:.1f}" fill="#D4252A" stroke="#04331A" stroke-width=".4"/><circle cx="{gx}" cy="{gy}" r="{1+7*gol["xg"]**.5:.1f}" fill="#FFFFFF" stroke="#04331A" stroke-width=".4"/>'
b = f'<div style="position:absolute;left:64px;top:600px;width:882px;height:662px">{demi(ex)}</div>'
b += f'''<div style="position:absolute;left:64px;top:1250px;font:800 30px/1.35 SC;letter-spacing:.04em"><span style="font:italic 900 64px BC;color:#D4252A">{round(100*pen["xg"])} %</span> LA FRAPPE D'AMADOU HAÏDARA · À CÔTÉ<br><span style="font:italic 900 64px BC;color:#064A25">{round(100*gol["xg"])} %</span> LA FRAPPE DE LASSINE SINAYOKO · BUT<br><span style="font:600 22px SC;color:rgba(4,51,26,.8)">TAILLE DU ROND = CHANCE DE BUT</span></div>'''
out['c2'] = pageT('OUTIL 2 · <b>LA QUALITÉ D\'UNE OCCASION</b>', 'OUTIL 2', 'BUTS ATTENDUS', '', b, f'Mali 2-0 Afrique du Sud, CAN 2023 · Chance de but de chaque tir · Données {SB}')
# C3 : la simulation
d = {int(k): v for k, v in SIM['points_mali'].items()}; q = {int(k): v for k, v in SIM['qualifie_selon_points'].items()}
ks = list(range(7, 19)); g = ''; w = 840 / len(ks); mx = max(d.values())
for i, k in enumerate(ks):
    v = d.get(k, 0); h = v / mx * 380; x = 100 + i * w + 6
    g += f'<rect x="{x:.0f}" y="{1180-h:.0f}" width="{w-12:.0f}" height="{h:.0f}" rx="3" fill="{"#0B7A3B" if (q.get(k) or 0) >= .99 else "#FFF3C4"}"/>' + txt(x + (w - 12) / 2, 1220, k, 26, 700, '#064A25', 'middle')
g += f'<line class="ax" x1="100" y1="1180" x2="944" y2="1180"/>'
b = sv(g) + '<div style="position:absolute;left:64px;top:600px;font:italic 900 120px/1 BC;color:#064A25">100 000</div><div style="position:absolute;left:64px;top:720px;font:800 30px SC;letter-spacing:.05em">FOIS LE GROUPE DU MALI, MATCH PAR MATCH</div>'
b += '<div class="bigR" style="top:1290px"><b>+98 %</b><span>DE CHANCES D\'ALLER À LA CAN 2027<br>POINTS DU MALI À LA FIN · <em>VERT = QUALIFIÉ</em></span></div>'
out['c3'] = pageT('OUTIL 3 · <b>LA SIMULATION</b>', 'OUTIL 3', 'LA SIMULATION', '', b, 'Éliminatoires CAN 2027, groupe K · Modèle de buts selon la force et le lieu · Calcul MaliDataFoot')

# ---------------- D : Mali - Côte d'Ivoire décodé
x0, x1, y0, y1 = 110, 950, 640, 1180; ymax = 1.5
X = lambda m: x0 + m / 122 * (x1 - x0); Y = lambda v: y1 - v / ymax * (y1 - y0)
g = f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>'
for m in (0, 45, 90, 120): g += txt(X(m), y1 + 40, f"{m}'", 26, 700, '#064A25', 'middle')
g += f'<line x1="{X(42):.0f}" y1="{y0}" x2="{X(42):.0f}" y2="{y1}" stroke="#D4252A" stroke-width="3" stroke-dasharray="8 7"/>' + txt(X(42) + 10, y0 + 20, 'CARTON ROUGE IVOIRIEN', 22, 800, '#D4252A')
for team, col in (("Mali", '#0B7A3B'), ("Côte d'Ivoire", '#F77F00')):
    c = 0; pts = [(0, 0)]
    for s in sorted([s for s in P['civ_tirs'] if s['team'] == team and s['type'] != 'Penalty'], key=lambda s: s['min']):
        pts.append((s['min'], c)); c += s['xg']; pts.append((s['min'], c))
    pts.append((122, c))
    g += '<path d="M' + 'L'.join(f'{X(m):.1f} {Y(v):.1f}' for m, v in pts) + f'" fill="none" stroke="{col}" stroke-width="6"/>'
    g += big(X(122) - 6, Y(c) - 14, fr(c), 54, col, 'end')
for s in P['civ_tirs']:
    if s['out'] == 'Goal': g += f'<circle cx="{X(s["min"]):.0f}" cy="{y1-14}" r="10" fill="{"#0B7A3B" if s["team"]=="Mali" else "#F77F00"}"/>'
b = sv(g) + '<div class="leg" style="top:1250px"><span><i style="display:block;width:34px;height:9px;border-radius:5px;background:#0B7A3B"></i>MALI</span><span><i style="display:block;width:34px;height:9px;border-radius:5px;background:#F77F00"></i>CÔTE D\'IVOIRE</span><span>● BUT</span></div>'
b += f'<div class="bigR" style="top:1310px"><b>{fr(0.5336)}</b><span>BUT ATTENDU EN JEU EN 120 MINUTES<br>POUR LE MALI, <em>PENALTY ARRÊTÉ NON COMPTÉ</em></span></div>'
out['d1'] = pageT('CAN 2023 · QUART DE FINALE · <b>MALI 1-2 CÔTE D\'IVOIRE</b>', 'LE BALLON,', 'PAS LES OCCASIONS', '', b, f'Buts attendus cumulés en jeu (hors penalty) · Données {SB}')
# D2 : dernier tiers contre surface, après l'expulsion
L = 'stroke="#FFF6D0" stroke-width="0.6" fill="none"'
ter = f'''<svg viewBox="-2 -2 84 124" width="100%" height="100%"><rect x="0" y="0" width="80" height="120" fill="#0B7A3B"/>
<rect x="0" y="0" width="80" height="40" fill="#19A552"/><rect x="18" y="0" width="44" height="18" fill="#FCD116" fill-opacity=".9"/>
<rect x="0" y="0" width="80" height="120" {L}/><line x1="0" y1="60" x2="80" y2="60" {L}/><circle cx="40" cy="60" r="9.15" {L}/><rect x="18" y="0" width="44" height="18" {L}/><rect x="18" y="102" width="44" height="18" {L}/></svg>'''
b = f'<div style="position:absolute;left:64px;top:600px;width:480px;height:720px">{ter}</div>'
b += '<div style="position:absolute;left:600px;top:640px;font:800 28px/1.2 SC;letter-spacing:.04em">PASSES RÉUSSIES<br>DANS LE DERNIER TIERS</div><div style="position:absolute;left:600px;top:710px;font:italic 900 120px/1 BC;color:#0B7A3B">90 <span style="font-size:60px;color:#F77F00">· 19</span></div>'
b += '<div style="position:absolute;left:600px;top:900px;font:800 28px/1.2 SC;letter-spacing:.04em">DONT DANS<br>LA SURFACE</div><div style="position:absolute;left:600px;top:970px;font:italic 900 120px/1 BC;color:#0B7A3B">8 <span style="font-size:60px;color:#F77F00">· 7</span></div>'
b += '<div style="position:absolute;left:600px;top:1150px;font:800 26px/1.3 SC;letter-spacing:.04em">MALI <span style="color:#F77F00">· CÔTE D\'IVOIRE À 10</span><br>DE LA 43e À LA 90e</div>'
b += '<div style="position:absolute;left:64px;top:1360px;font:800 34px/1.25 SC;letter-spacing:.04em">LE MALI ARRIVAIT AUX 30 MÈTRES.<br><span style="color:#D4252A">IL N\'ENTRAIT PAS DANS LA SURFACE.</span></div>'
out['d2'] = pageT('APRÈS L\'EXPULSION · <b>LE MALI À 11 CONTRE 10</b>', 'ARRIVER,', 'PAS ENTRER', '', b, f'Passes réussies, minutes 43 à 90 · Données {SB}')

# ---------------- E : récupérer haut
tm = sorted(T['teams'], key=lambda t: -t['regain_x_mean'])
x0, x1 = 120, 940; lo, hi = 30, 45; X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
g = f'<line class="ax" x1="{x0}" y1="1180" x2="{x1}" y2="1180"/>'
for v in (30, 35, 40, 45): g += txt(X(v), 1220, f'{v*0.914:.0f} m', 24, 700, '#064A25', 'middle')
for i, t in enumerate(tm):
    y = 620 + i * 23; m = t['team'] == 'Mali'
    g += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#FCE38A" stroke-width="1.5"/><circle cx="{X(t["regain_x_mean"]):.0f}" cy="{y}" r="{11 if m else 7}" fill="{"#0B7A3B" if m else "#FFF3C4"}" stroke="#064A25" stroke-width="2"/>'
    if m or i in (1, 2): g += txt(X(t['regain_x_mean']) - 18, y + 8, ('MALI' if m else t['team'].upper()) + f' · {fr(t["regain_x_mean"]*0.914,1)} m', 22, 800, '#0B7A3B' if m else '#04331A', 'end')
b = sv(g) + '<div style="position:absolute;left:64px;top:1240px;font:600 22px SC;color:rgba(4,51,26,.8)">DISTANCE MOYENNE DE LA RÉCUPÉRATION À SON PROPRE BUT · 24 ÉQUIPES</div>'
b += '<div class="bigR" style="top:1300px"><b>1<span style="font:italic 900 70px BC">er</span></b><span>LE MALI RÉCUPÈRE LE BALLON<br>LE PLUS HAUT DE LA CAN, <em>DE JUSTESSE</em></span></div>'
out['e1'] = pageT('CAN 2023 · <b>LES 10 SECONDES APRÈS LA RÉCUPÉRATION</b>', 'RÉCUPÉRER', 'HAUT', '', b, f'Récupérations en jeu (hors coups de pied arrêtés et gardien) · Données {SB}')
b = '<div style="position:absolute;left:64px;top:620px;font:800 30px SC;letter-spacing:.05em">TIRS DANS LES 10 SECONDES</div>'
b += '<div style="position:absolute;left:64px;top:680px;display:flex;gap:60px;align-items:flex-end"><div><div style="font:italic 900 200px/.9 BC;color:#FFF3C4;-webkit-text-stroke:3px #064A25">6,7</div><div style="font:800 28px SC">ATTENDUS VU SA HAUTEUR</div></div><div><div style="font:italic 900 200px/.9 BC;color:#0B7A3B">5</div><div style="font:800 28px SC">RÉELS</div></div></div>'
b += '<div style="position:absolute;left:64px;top:1030px;font:800 30px SC;letter-spacing:.05em">INTENSITÉ DU PRESSING</div><div style="position:absolute;left:64px;top:1080px;font:italic 900 130px/1 BC;color:#0B7A3B">2<span style="font-size:70px">e</span> <span style="font:800 30px SC;color:#04331A">SUR 24, DERRIÈRE L\'ALGÉRIE</span></div>'
b += '<div style="position:absolute;left:64px;top:1300px;font:800 34px/1.25 SC;letter-spacing:.04em">IL PRESSE ET RÉCUPÈRE HAUT.<br><span style="color:#D4252A">5 TIRS POUR 6,7 ATTENDUS : PAS D\'ÉCART NET.</span></div>'
out['e2'] = pageT('CAN 2023 · <b>CE QUE LE MALI FAIT DU BALLON RÉCUPÉRÉ</b>', 'LE PRESSING', 'QUI MARCHE', '', b, f'Attendu = taux de tir du tournoi selon la zone de récupération · Données {SB}')

# ---------------- F : les styles vus par la machine
co = S['pca']['coordinates']
xs = [c['PC1'] for c in co]; ys = [c['PC2'] for c in co]
x0, x1, y0, y1 = 110, 950, 640, 1240
X = lambda v: x0 + (v - min(xs) + .3) / (max(xs) - min(xs) + .6) * (x1 - x0); Y = lambda v: y1 - (v - min(ys) + .3) / (max(ys) - min(ys) + .6) * (y1 - y0)
g = f'<line x1="{x0}" y1="{(y0+y1)/2}" x2="{x1}" y2="{(y0+y1)/2}" stroke="#FCE38A" stroke-width="3"/><line x1="{(x0+x1)/2}" y1="{y0}" x2="{(x0+x1)/2}" y2="{y1}" stroke="#FCE38A" stroke-width="3"/>'
COD = {'Mali': 'MLI', 'Morocco': 'MAR', 'Senegal': 'SEN', 'Algeria': 'ALG', 'Egypt': 'EGY', "Côte d'Ivoire": 'CIV', 'Nigeria': 'NGA', 'South Africa': 'RSA', 'Cameroon': 'CMR', 'Cape Verde Islands': 'CPV', 'Guinea': 'GUI', 'Ghana': 'GHA',
       'Tunisia': 'TUN', 'Congo DR': 'COD', 'Burkina Faso': 'BFA', 'Namibia': 'NAM', 'Angola': 'ANG', 'Mozambique': 'MOZ', 'Gambia': 'GAM', 'Mauritania': 'MTN', 'Tanzania': 'TAN', 'Zambia': 'ZAM', 'Guinea-Bissau': 'GNB', 'Equatorial Guinea': 'EQG'}
for c in co:
    m = c['team'] == 'Mali'; cx, cy = X(c['PC1']), Y(c['PC2'])
    g += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{16 if m else 9}" fill="{"#0B7A3B" if m else "#FFF3C4"}" stroke="#064A25" stroke-width="2"/>' + txt(cx + (22 if m else 14), cy + 8, COD.get(c['team'], c['team'][:3].upper()), 30 if m else 20, 800, '#0B7A3B' if m else '#04331A')
g += txt(x1, y1 + 40, 'GARDE LE BALLON →', 22, 800, '#04331A', 'end') + txt(x0, y1 + 40, '← JOUE LONG', 22, 800, '#04331A') + txt(x0 + 6, y0 - 12, '↑ VERTICAL', 22, 800, '#04331A') + txt(x0 + 6, y1 - 8, '↓ PATIENT', 22, 800, '#04331A')
b = sv(g) + '<div class="bigR" style="top:1320px"><b>23<span style="font:italic 900 70px BC">e</span></b><span>SUR 24 EN VERTICALITÉ :<br>LE MALI A LE BALLON, <em>IL NE VA PAS VERS L\'AVANT</em></span></div>'
out['f1'] = pageT('CAN 2023 · <b>14 MESURES DE JEU, 24 ÉQUIPES</b>', 'LES STYLES', 'VUS PAR LA MACHINE', '', b, f'Analyse en composantes principales · Données {SB}')

# ---------------- G : maudit ?
ed = R['q2_titres']['editions']; g = ''; w = 840 / len(ed)
for i, e in enumerate(ed):
    h = e['p_titre'] / 0.10 * 480; x = 100 + i * w + 5
    g += f'<rect x="{x:.0f}" y="{1180-h:.0f}" width="{w-10:.0f}" height="{h:.0f}" rx="3" fill="#0B7A3B"/>' + txt(x + (w - 10) / 2, 1215, str(e['edition'])[2:], 22, 700, '#064A25', 'middle')
    if e['p_titre'] >= .05: g += big(x + (w - 10) / 2, 1180 - h - 12, f'{round(100*e["p_titre"])}%', 30, '#064A25', 'middle')
g += '<line class="ax" x1="100" y1="1180" x2="944" y2="1180"/>'
b = sv(g) + '<div style="position:absolute;left:64px;top:600px;font:800 30px SC;letter-spacing:.05em">CHANCES DE TITRE DU MALI, ÉDITION PAR ÉDITION</div>'
b += '<div class="bigR" style="top:1290px"><b>62 %</b><span>DE CHANCES DE N\'AVOIR AUCUN TITRE EN 14 CAN :<br>PAS MAUDIT, <em>PAS ENCORE ASSEZ FORT</em></span></div>'
out['g1'] = pageT('CAN 1972-2025 · <b>RÉSULTATS RÉELS CONTRE ATTENDUS</b>', 'MAUDIT ?', 'LA DATA RÉPOND', '', b, 'Modèle de buts selon la force (Elo) et le lieu · 64 matchs de phase finale · Calcul MaliDataFoot')
nl = R['q5_nuls']['mali_groupes']
b = f'''<div style="position:absolute;left:64px;top:620px;font:800 30px SC;letter-spacing:.05em">MATCHS NULS EN PHASE DE GROUPES</div>
<div style="position:absolute;left:64px;top:680px;display:flex;gap:60px;align-items:flex-end"><div><div style="font:italic 900 200px/.9 BC;color:#0B7A3B">{nl["nuls"]}</div><div style="font:800 28px SC">RÉELS SUR {nl["matchs"]}</div></div><div><div style="font:italic 900 200px/.9 BC;color:#FFF3C4;-webkit-text-stroke:3px #064A25">{round(R["q5_nuls"]["mali_groupes_recalibre"]["nuls_attendus"])}</div><div style="font:800 28px SC">ATTENDUS</div></div></div>
<div style="position:absolute;left:64px;top:1030px;font:800 30px/1.3 SC;letter-spacing:.04em">ET CES NULS NE LUI ONT PAS COÛTÉ DE POINTS :<br><span style="font:italic 900 70px BC;color:#0B7A3B">88</span> POINTS PRIS POUR <span style="font:italic 900 70px BC">84</span> ATTENDUS</div>
<div style="position:absolute;left:64px;top:1300px;font:800 34px/1.25 SC;letter-spacing:.04em">DIFFICILE À BATTRE.<br><span style="color:#D4252A">MAIS IL NE TUE PAS LES MATCHS.</span></div>'''
out['g2'] = pageT('CAN 1972-2025 · <b>LE MALI, ROI DU NUL ?</b>', 'ROI', 'DU NUL ?', '', b, 'Attendus : modèle de buts selon la force (Elo) et le lieu · Calcul MaliDataFoot')

for k, h in out.items(): open(f'_poc_{k}.html', 'w', encoding='utf-8').write(h)
print(' '.join(out))

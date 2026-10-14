"""Plans clés T14-T18 (TikTok 1080 x 1920, DA vidéo). A lancer depuis visuels/ : écrit _a14_*.html."""
import json, math, collections
from decimal import Decimal, ROUND_HALF_UP
SH = '/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
exec(open(SH + '/maq_a.py', encoding='utf-8').read().split('# 1 : le score')[0])
src_t = open(SH + '/maq_terrain.py', encoding='utf-8').read()
exec(src_t[src_t.index('def terrain'):src_t.index('# A : le terrain penche')])
SB = '<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
J = {k: json.load(open(f'{SH}/poc_jeu2/{k}.json', encoding='utf-8')) for k in ('t14', 't15', 't16', 't17', 't18')}

def fd(v, d=1):  # arrondi « comme à l'école », virgule française
    q = Decimal(1).scaleb(-d)
    return str(Decimal(str(v)).quantize(q, rounding=ROUND_HALF_UP)).replace('.', ',')
def pc(v, d=0): return fd(100 * Decimal(str(v)), d) + ' %'
def sv(inner): return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{inner}</svg>'
def txt(x, y, t, size=26, w=700, col='#064A25', anchor='start', fam='SC', it=False, ls=''):
    st = f'font:{"italic " if it else ""}{w} {size}px {fam};fill:{col}' + (f';letter-spacing:{ls}' if ls else '')
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="{st}">{t}</text>'
def big(x, y, t, size=80, col='#064A25', anchor='start'): return txt(x, y, t, size, 900, col, anchor, 'BC', True)
def div(x, y, html, style=''): return f'<div style="position:absolute;left:{x}px;top:{y}px;{style}">{html}</div>'
LAB = 'font:800 30px/1.25 SC;letter-spacing:.04em'
SMALL = 'font:600 22px/1.2 SC;letter-spacing:.03em;color:rgba(4,51,26,.8)'
L = 'stroke="#FFF6D0" stroke-width="0.6" fill="none"'
out = {}

# =============== 14 : Sinayoko, le premier défenseur
t = J['t14']; R = t['sinayoko_ranks']; PA = t['possession_adjusted']
vals = [(r['pressures_p90'], r['player']) for r in t['table']]
x0, x1, lo, hi = 104, 944, 4, 28; bw = (x1 - x0) / (hi - lo); base = 1130; step = 34
X = lambda v: x0 + (v - lo) * bw
g = f'<line class="ax" x1="{x0}" y1="{base+20}" x2="{x1}" y2="{base+20}"/>'
for v in range(5, 29, 5): g += txt(X(v), base + 60, v, 26, 700, '#064A25', 'middle')
bins = collections.defaultdict(list)
for v, p in sorted(vals): bins[int(v)].append((v, p))
med = R['pressures_p90']['median']
g += f'<line x1="{X(med):.1f}" y1="{base-375}" x2="{X(med):.1f}" y2="{base+20}" stroke="#D4252A" stroke-width="3" stroke-dasharray="9 7"/>'
g += txt(X(med) - 10, base - 385, f'MÉDIANE {fd(med)}', 24, 800, '#D4252A', 'middle')
for b_, lst in bins.items():
    for i, (v, p) in enumerate(lst):
        cx = X(b_ + .5); cy = base - i * step; m = p == 'Lassine Sinayoko'
        g += f'<circle cx="{cx:.1f}" cy="{cy}" r="16" fill="{"#0B7A3B" if m else "#FFF3C4"}" stroke="#064A25" stroke-width="2"/>'
        if m:
            g += f'<line x1="{cx:.1f}" y1="{cy-20}" x2="{cx:.1f}" y2="{cy-118}" stroke="#0B7A3B" stroke-width="3"/>'
            g += txt(cx, cy - 176, 'SINAYOKO', 30, 800, '#0B7A3B', 'middle') + big(cx, cy - 128, fd(v), 44, '#0B7A3B', 'middle')
b = sv(g) + div(64, 1225, 'PRESSIONS PAR 90 MINUTES · UN ROND = UN ATTAQUANT', SMALL)
b += f'<div class="bigR" style="top:1300px"><b>{R["pressures_p90"]["rank"]}<span style="font:italic 900 70px BC">e</span></b><span>SUR {t["n_forwards"]} ATTAQUANTS DE LA CAN<br>ET <em>1er À POSSESSION ÉGALE</em> ({fd(PA["pressures_p90_padj"]["value"])})</span></div>'
out['s14_1'] = pageT('CAN 2023 · <b>LE PRESSING DES ATTAQUANTS</b>', 'SINAYOKO,', 'LE PREMIER DÉFENSEUR', '', b,
                     f'60 attaquants, 180 min et plus · Possession égale : 50 % de ballon adverse · Données {SB}')
# 14-2 : où il presse
s = t['sinayoko']; n = s['pressures']
ft = round(R['final_third_p90']['value'] * t['table'][[r['player'] for r in t['table']].index('Lassine Sinayoko')]['minutes'] / 90)
zones = [('DERNIER TIERS', 80, 120, ft), ('CAMP ADVERSE,<br>AVANT LE DERNIER TIERS', 60, 80, s['opp_half'] - ft), ('DANS SA MOITIÉ', 0, 60, n - s['opp_half'])]
PX, PY, k = 64, 600, 5.5  # terrain vertical, attaque vers le haut
ty = lambda x: PY + (120 - x) * k
ex = ''
for nm, a, z, c in zones:
    sh = c / n; yc = ty((a + z) / 2)
    ex += f'<rect x="0" y="{(120-z)+((z-a)/2-5)}" width="{80*sh:.2f}" height="10" fill="#FFF6D0"/>'
ter = f'''<svg viewBox="-2 -2 84 124" width="{84*k}" height="{124*k}" style="position:absolute;left:{PX-2*k}px;top:{PY-2*k}px"><rect x="0" y="0" width="80" height="120" fill="#0B7A3B"/>
<rect x="0" y="0" width="80" height="120" {L}/><line x1="0" y1="60" x2="80" y2="60" {L}/><circle cx="40" cy="60" r="9.15" {L}/><rect x="18" y="0" width="44" height="18" {L}/><rect x="18" y="102" width="44" height="18" {L}/>
<line x1="0" y1="40" x2="80" y2="40" stroke="#FFF6D0" stroke-width="0.6" stroke-dasharray="1.6 1.2"/><rect x="36" y="-1.6" width="8" height="1.6" fill="#FFF6D0"/>{ex}</svg>'''
b = ter
for nm, a, z, c in zones:
    yc = ty((a + z) / 2)
    b += div(PX + 80 * k + 34, yc - 62, f'<div style="font:italic 900 96px/1 BC;color:#064A25">{pc(c/n)}</div><div style="font:800 24px/1.15 SC;letter-spacing:.04em;margin-top:2px">{nm}</div>')
b += div(PX, PY - 46, '↑ SENS DE L\'ATTAQUE · BARRE = PART DE SES 105 PRESSIONS', SMALL)
rr = R['regain_rate']
b += f'<div class="bigR" style="top:1300px"><b style="color:#064A25">{pc(rr["value"])}</b><span>DE SES PRESSIONS MÈNENT À UNE<br>RÉCUPÉRATION EN 5 S : {rr["rank"]}e SUR 60, <em>MOYEN</em></span></div>'
out['s14_2'] = pageT(f'CAN 2023 · <b>{R["opp_half_p90"]["rank"]}e SUR 60 EN PRESSIONS DANS LE CAMP ADVERSE</b>', 'IL PRESSE HAUT', 'SANS RÉCUPÉRER PLUS', '', b,
                     f'Pressions de L. Sinayoko, 5 matchs · Récupération : ballon repris en 5 s · Données {SB}')

# =============== 15 : Sinayoko, il finit, on le sert
t = J['t15']; s = t['sinayoko']; M = t['mali']; T18 = J['t18']['mali_ranks']
k = 882 / 50  # zoom sur la surface : y 15-65 (largeur), x 94-120 (hauteur)
ex = ''
served = 0
for sh in s['shots']:
    cx, cy = sh['y'], 120 - sh['x']; r = 0.3 + 1.3 * sh['shot_xg'] ** .5
    srv = sh['origin'] != 'action_perso_sans_passe' and sh['origin'] != 'rebond'; served += srv
    col = '#FFF6D0' if srv else '#D4252A'
    ex += f'<circle cx="{cx}" cy="{cy:.1f}" r="{r+0.35:.2f}" fill="#0B7A3B"/>'
    ex += f'<circle cx="{cx}" cy="{cy:.1f}" r="{r:.2f}" fill="{col if sh["shot_outcome"]=="Goal" else "none"}" stroke="{col}" stroke-width="0.35"/>'
demi = f'''<svg viewBox="15 -2 50 28" width="882" height="{28*k:.0f}" style="position:absolute;left:64px;top:600px"><rect x="15" y="-2" width="50" height="28" fill="#0B7A3B"/>
<line x1="15" y1="0" x2="65" y2="0" {L}/><rect x="18" y="0" width="44" height="18" {L}/><rect x="30" y="0" width="20" height="6" {L}/><circle cx="40" cy="12" r=".35" fill="#FFF6D0"/><path d="M32 18A10 10 0 0 0 48 18" {L}/><rect x="36" y="-1.6" width="8" height="1.6" fill="#FFF6D0"/>{ex}</svg>'''
b = demi
dot = lambda c, f: f'<i style="display:block;width:24px;height:24px;border-radius:50%;border:3px solid {c};background:{c if f else "transparent"}"></i>'
b += f'<div class="leg" style="top:1130px;gap:22px"><span>{dot("#064A25",1)}BUT</span><span>{dot("#064A25",0)}RATÉ</span><span>TAILLE = CHANCE DE BUT (xG)</span></div>'
b += f'<div class="leg" style="top:1176px;gap:22px"><span><i style="display:block;width:24px;height:24px;border-radius:50%;border:3px solid #064A25;background:#FFF3C4"></i>SERVI PAR UNE PASSE CLÉ</span><span><i style="display:block;width:24px;height:24px;border-radius:50%;border:3px solid #064A25;background:#D4252A"></i>SANS PASSE CLÉ</span></div>'
b += f'<div class="bigR" style="top:1290px"><b>{served} <span style="font:italic 900 70px BC">SUR</span> {s["np_shots"]}</b><span>TIRS SERVIS PAR UN COÉQUIPIER<br>{s["np_goals"]} BUTS POUR <em>{fd(s["npxg"],2)} BUT ATTENDU</em></span></div>'
out['s15_1'] = pageT('CAN 2023 · <b>LES 9 TIRS DE LASSINE SINAYOKO</b>', 'SINAYOKO :', 'IL FINIT, ON LE SERT', '', b,
                     f'Tirs hors penalty, 5 matchs · Passe clé : dernière passe avant le tir · Données {SB}')
# 15-2 : qui le sert + part des xG du Mali
NOMS = {'Kamory Doumbia': 'K. DOUMBIA', 'Hamari Traoré': 'H. TRAORÉ', 'Amadou Haïdara': 'A. HAÏDARA', 'Diadie Samassekou': 'D. SAMASSÉKOU', 'Youssoufou Niakaté': 'Y. NIAKATÉ'}
rows = [(NOMS[p], c, '#0B7A3B') for p, c in s['key_passers'].items()] + [('SANS PASSE CLÉ', s['origin_counts']['action_perso_sans_passe'], '#D4252A')]
b = div(64, 600, 'QUI LUI DONNE LE BALLON DU TIR', LAB)
for i, (nm, c, col) in enumerate(rows):
    y = 670 + i * 84
    b += div(64, y, nm, f'font:800 32px/50px SC;letter-spacing:.04em;color:{"#04331A" if col=="#0B7A3B" else col}')
    b += div(420, y, ''.join(f'<i style="display:inline-block;width:46px;height:46px;border-radius:50%;background:{col};margin-right:14px;vertical-align:middle"></i>' for _ in range(c)))
b += div(64, 1180, 'UN ROND = UN TIR DE SINAYOKO · 9 TIRS EN 5 MATCHS : PETIT ÉCHANTILLON', SMALL)
b += f'<div class="bigR" style="top:1290px"><b>{pc(M["sinayoko_share_npxg"])}</b><span>DES BUTS ATTENDUS DU MALI<br>POUR {pc(M["sinayoko_share_shots"])} DE SES TIRS</span></div>'
out['s15_2'] = pageT(f'CAN 2023 · <b>LE MALI CRÉE : {T18["npxg_p90"]["rank"]}e SUR 24 EN BUTS ATTENDUS PAR 90</b>', 'IL CONCLUT', 'CE QUE LE MALI CRÉE', '', b,
                     f'Tirs et buts attendus hors penalty · Données {SB}')

# =============== 16 : 11 contre 10
A = J['t16']['aggregate']; bf, af = A['before'], A['after']; nc = J['t16']['counts']['n_cases']
p90 = lambda d, k: d[k + '_total'] / d['minutes'] * 90
G, Rr, N = '#0B7A3B', '#D4252A', '#04331A'
rows = [('POSSESSION', pc(bf['pass_share']), pc(af['pass_share']), G),
        ('TIRS PAR 90', fd(p90(bf, 'np_shots_for')), fd(p90(af, 'np_shots_for')), G),
        ('BUTS ATTENDUS PAR 90', fd(p90(bf, 'npxg_for'), 2), fd(p90(af, 'npxg_for'), 2), N),
        ('xG PAR TIR', fd(bf['npxg_for_total'] / bf['np_shots_for_total'], 3), fd(af['npxg_for_total'] / af['np_shots_for_total'], 3), Rr),
        ('BUTS MARQUÉS PAR 90', fd(p90(bf, 'goals_for'), 2), fd(p90(af, 'goals_for'), 2), G),
        ('BUTS ENCAISSÉS PAR 90', fd(p90(bf, 'goals_against'), 2), fd(p90(af, 'goals_against'), 2), Rr)]
T16 = rows
g = ''
for i in range(len(rows) + 1): g += f'<line x1="64" y1="{700+i*100}" x2="946" y2="{700+i*100}" stroke="#FCE38A" stroke-width="3"/>'
b = sv(g) + div(500, 610, '11 CONTRE 11', 'width:180px;text-align:center;font:800 26px/1.15 SC;letter-spacing:.04em') + div(756, 610, '11 CONTRE 10', 'width:190px;text-align:center;font:800 26px/1.15 SC;letter-spacing:.04em;color:#0B7A3B')
b += div(500, 645, 'AVANT LE ROUGE', 'width:180px;text-align:center;' + SMALL) + div(756, 645, 'APRÈS', 'width:190px;text-align:center;' + SMALL)
for i, (lb, v0, v1, col) in enumerate(rows):
    y = 700 + i * 100
    b += div(64, y + 30, lb, 'font:800 28px/40px SC;letter-spacing:.04em')
    b += div(500, y + 14, v0, 'width:180px;text-align:center;font:italic 900 70px/72px BC;color:#064A25')
    b += div(690, y + 22, '→', 'font:800 44px/56px SC;color:#064A25')
    b += div(756, y + 14, v1, f'width:190px;text-align:center;font:italic 900 70px/72px BC;color:{col}')
b += f'<div class="leg" style="top:1325px;font-size:23px;gap:18px"><span style="color:#0B7A3B">VERT : MIEUX POUR L\'ÉQUIPE À 11</span><span style="color:#D4252A">ROUGE : MOINS BIEN</span></div>'
b += div(64, 1368, f'PLUS DE BALLON, PLUS DE TIRS.<br><span style="color:#D4252A">PAS PLUS D\'OCCASIONS.</span>', 'font:800 34px/1.2 SC;letter-spacing:.04em;white-space:nowrap')
out['s16_1'] = pageT(f'CAN 2023 · <b>{nc} EXPULSIONS, AVANT ET APRÈS LE ROUGE</b>', '11 CONTRE 10', 'UN VRAI AVANTAGE ?', '', b,
                     f'{nc} cartons rouges · Équipe à 11 · Tirs et xG hors penalty · Données {SB}')
# 16-2 : deux petits graphiques en barres (départ à 0)
sh0, sh1 = p90(bf, 'np_shots_for'), p90(af, 'np_shots_for')
q0, q1 = bf['npxg_for_total'] / bf['np_shots_for_total'], af['npxg_for_total'] / af['np_shots_for_total']
g = ''; yb = 1150; hmax = 400
def pair(xl, a, c, fmt, title, col1):
    o = txt(xl, 640, title, 30, 800, '#04331A') + f'<line class="ax" x1="{xl}" y1="{yb}" x2="{xl+370}" y2="{yb}"/>'
    m = max(a, c)
    for j, (v, lab, fill) in enumerate(((a, 'AVANT', '#FFF3C4'), (c, 'APRÈS', col1))):
        h = v / m * hmax; x = xl + 20 + j * 180
        o += f'<rect x="{x}" y="{yb-h:.0f}" width="140" height="{h:.0f}" rx="4" fill="{fill}"/>'
        o += big(x + 70, yb - h - 16, fmt(v), 56, '#064A25' if j == 0 else col1, 'middle') + txt(x + 70, yb + 40, lab, 26, 800, '#04331A', 'middle')
    return o
g += pair(84, sh0, sh1, lambda v: fd(v), 'TIRS PAR 90', '#0B7A3B') + pair(560, q0, q1, lambda v: fd(v, 3), 'xG PAR TIR', '#D4252A')
b = sv(g) + f'<div class="leg" style="top:1218px;font-size:23px">AVANT = 11 CONTRE 11 · APRÈS = 11 CONTRE 10</div><div class="leg" style="top:1252px;font-size:23px;gap:18px"><span style="color:#0B7A3B">VERT : MIEUX POUR L\'ÉQUIPE À 11</span><span style="color:#D4252A">ROUGE : MOINS BIEN</span></div>'
b += f'<div class="bigR" style="top:1290px"><b>{fd(p90(af,"npxg_for"),2)}</b><span>BUT ATTENDU PAR 90 APRÈS LE ROUGE<br>({fd(p90(bf,"npxg_for"),2)} AVANT) : <em>PAS PLUS D\'OCCASIONS</em></span></div>'
out['s16_2'] = pageT('CAN 2023 · <b>CE QUE CHANGE LE JOUEUR EN PLUS</b>', 'PLUS DE TIRS,', 'MOINS BONS', '', b,
                     f'{nc} cartons rouges · Équipe à 11 · Hors penalty, par 90 min réelles · Données {SB}')

# =============== 17 : par où attaque le Mali
t = J['t17']; mm, tm = t['mali'], t['team_mean']
k = 10; PX, PY = 140, 600  # demi-terrain x 60-120 vertical (600 px), largeur 80 yd (800 px) ; attaque vers le haut
lanes = [('GAUCHE', 'gauche', 0, 26.67), ('AXE', 'centre', 26.67, 53.33), ('DROITE', 'droite', 53.33, 80)]
ex = ''
for nm, key, a, z in lanes:
    w = mm['lane_end_' + key] * 28; cx = (a + z) / 2
    ex += f'<path d="M{cx-w/2:.2f} 40 L{cx-w/2:.2f} 18 L{cx-w/2-2:.2f} 18 L{cx:.2f} 10 L{cx+w/2+2:.2f} 18 L{cx+w/2:.2f} 18 L{cx+w/2:.2f} 40 Z" fill="#FFF6D0"/>'
ter = f'''<svg viewBox="0 -2 80 62" width="{80*k}" height="{62*k}" style="position:absolute;left:{PX}px;top:{PY-2*k}px"><rect x="0" y="0" width="80" height="60" fill="#0B7A3B"/>
<rect x="0" y="0" width="80" height="60" {L}/><rect x="18" y="0" width="44" height="18" {L}/><rect x="30" y="0" width="20" height="6" {L}/><path d="M32 18A10 10 0 0 0 48 18" {L}/><rect x="36" y="-1.6" width="8" height="1.6" fill="#FFF6D0"/>
<line x1="26.67" y1="0" x2="26.67" y2="60" stroke="#FFF6D0" stroke-width="0.3" stroke-dasharray="1 1"/><line x1="53.33" y1="0" x2="53.33" y2="60" stroke="#FFF6D0" stroke-width="0.3" stroke-dasharray="1 1"/>
<line x1="0" y1="40" x2="80" y2="40" stroke="#FFF6D0" stroke-width="0.9"/>{ex}</svg>'''
b = ter
for nm, key, a, z in lanes:
    cx = PX + (a + z) / 2 * k
    b += div(cx - 130, PY - 66, nm, 'width:260px;text-align:center;font:800 28px/1 SC;letter-spacing:.06em')
    b += div(cx - 130, PY + 42 * k, f'<div style="font:italic 900 76px/1 BC;color:#FFF6D0">{pc(mm["lane_end_"+key],1)}</div><div style="font:700 23px/1.2 SC;color:#FFF6D0;margin-top:6px">MOY. CAN {pc(tm["lane_end_"+key],1)}</div>', 'width:260px;text-align:center')
b += div(64, 1235, f'↑ ATTAQUE · LIGNE PLEINE = DÉBUT DU DERNIER TIERS<br>ÉPAISSEUR DES FLÈCHES = PART DES {mm["entries"]} ENTRÉES DU MALI', SMALL)
b += div(64, 1300, 'LE MALI ATTAQUE DES DEUX CÔTÉS,<br><span style="color:#D4252A">COMME LA MOYENNE DE LA CAN.</span>', 'font:800 36px/1.25 SC;letter-spacing:.04em;white-space:nowrap')
out['s17_1'] = pageT('CAN 2023 · <b>LES ENTRÉES DANS LE DERNIER TIERS</b>', 'PAR OÙ', 'ATTAQUE LE MALI ?', '', b,
                     f'Passes et conduites, couloir d\'arrivée · Moyenne des 24 équipes · Données {SB}')
# 17-2 : le couloir de Hamari Traoré
P = sorted(t['mali_players'], key=lambda p: -p['droite_p90'])[:6]
NM = {'Hamari Traoré': 'HAMARI TRAORÉ', 'Fousseni Diabaté': 'FOUSSENI DIABATÉ', 'Diadie Samassekou': 'DIADIÉ SAMASSÉKOU', 'Lassana Coulibaly': 'LASSANA COULIBALY', 'Yves Bissouma': 'YVES BISSOUMA', 'Boubakar Kouyate': 'BOUBAKAR KOUYATÉ'}
b = div(64, 600, 'ENTRÉES CÔTÉ DROIT PAR 90 MINUTES', LAB)
mx = P[0]['droite_p90']
for i, p in enumerate(P):
    y = 668 + i * 98; h = p['player'] == 'Hamari Traoré'; Lw = p['droite_p90'] / mx * 680
    b += div(64, y, NM[p['player']], f'font:800 28px SC;letter-spacing:.04em;color:{"#0B7A3B" if h else "#04331A"}')
    b += div(64, y + 40, '', f'width:{Lw:.0f}px;height:34px;border-radius:4px;background:{"#0B7A3B" if h else "#FFF3C4"}')
    b += div(64 + Lw + 16, y + 30, fd(p['droite_p90']), 'font:italic 900 52px/1 BC;color:#064A25')
b += div(64, 1255, 'JOUEURS DU MALI AVEC 90 MIN ET PLUS · LES 6 PREMIERS', SMALL)
hm = t['hamari_traore']
b += f'<div class="bigR" style="top:1300px"><b>{pc(hm["share_of_mali_right"])}</b><span>DES ENTRÉES DU MALI CÔTÉ DROIT<br>PASSENT PAR <em>HAMARI TRAORÉ</em></span></div>'
out['s17_2'] = pageT(f'CAN 2023 · <b>{hm["entries"]} ENTRÉES : {hm["by_kind"]["passe"]} PASSES, {hm["by_kind"]["conduite"]} CONDUITES</b>', 'LE COULOIR', 'DE HAMARI TRAORÉ', '', b,
                     f'Entrées dans le dernier tiers arrivées dans le couloir droit · Données {SB}')

# =============== 18 : tirer beaucoup ne suffit pas
t = J['t18']; m = t['mali']; R = t['mali_ranks']
k = 882 / 80; PY = 640  # surface : x 75-120 (hauteur 45 yd), y 0-80
yd = lambda metres: metres / 0.9144
rM, rT = yd(m['median_dist_m']), yd(R['median_dist_m']['median'])
arc = lambda r, st: f'<path d="M{40-r:.2f} 0 A{r:.2f} {r:.2f} 0 0 0 {40+r:.2f} 0" fill="none" {st}/>'
ter = f'''<svg viewBox="0 -2 80 34" width="882" height="{34*k:.0f}" style="position:absolute;left:64px;top:{PY-2*k:.0f}px"><rect x="0" y="0" width="80" height="32" fill="#0B7A3B"/>
<line x1="0" y1="0" x2="80" y2="0" {L}/><rect x="18" y="0" width="44" height="18" {L}/><rect x="30" y="0" width="20" height="6" {L}/><circle cx="40" cy="12" r=".35" fill="#FFF6D0"/><rect x="36" y="-1.6" width="8" height="1.6" fill="#FFF6D0"/>
{arc(rT, 'stroke="#D4252A" stroke-width="0.9" stroke-dasharray="1.6 1.1"')}{arc(rM, 'stroke="#FFF6D0" stroke-width="0.9"')}</svg>'''
b = ter
b += f'<div class="leg" style="top:{PY+32*k+28:.0f}px"><span><i style="display:block;width:44px;height:7px;background:#FFF6D0;outline:2px solid #064A25"></i>MALI {fd(m["median_dist_m"])} m</span><span><i style="display:block;width:44px;height:0;border-top:7px dashed #D4252A"></i>MÉDIANE DES 24 ÉQUIPES {fd(R["median_dist_m"]["median"])} m</span></div>'
b += div(64, PY + 32 * k + 74, 'DISTANCE MÉDIANE DES TIRS AU BUT (HORS PENALTY)', SMALL)
b += div(64, PY + 32 * k + 140, f'LE VOLUME Y EST : <span style="color:#0B7A3B">{R["np_shots_p90"]["rank"]}e</span> EN TIRS PAR 90 ({fd(R["np_shots_p90"]["value"])})<br><span style="color:#0B7A3B">{R["npxg_p90"]["rank"]}e</span> EN BUTS ATTENDUS PAR 90 ({fd(R["npxg_p90"]["value"],2)})', 'font:800 32px/1.3 SC;letter-spacing:.04em;white-space:nowrap')
ob = R['out_box_share']
b += f'<div class="bigR" style="top:1300px"><b>{pc(ob["value"],1)}</b><span>DES TIRS DU MALI HORS SURFACE<br><em>{ob["rank"]}e PLUS FORTE PART</em> (MOY. {pc(ob["team_mean"],1)})</span></div>'
out['s18_1'] = pageT('CAN 2023 · <b>TIRER BEAUCOUP NE SUFFIT PAS</b>', 'DE LOIN,', 'TROP SOUVENT', '', b,
                     f'Tirs hors penalty, 24 équipes · Distance médiane au centre du but · Données {SB}')
# 18-2 : xG par tir, match par match
MT = [('AFRIQUE', 'DU SUD'), ('TUNISIE', ''), ('NAMIBIE', ''), ('BURKINA', 'FASO'), ("CÔTE", "D'IVOIRE")]
x0, x1, yb, hmax, vmax = 100, 944, 1150, 470, 0.15
g = f'<line class="ax" x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}"/>'
w = (x1 - x0) / 5
mu = R['npxg_per_shot']['team_mean']
for i, (mt, (l1, l2)) in enumerate(zip(t['mali_by_match'], MT)):
    v = mt['npxg_per_shot']; h = v / vmax * hmax; x = x0 + i * w + 22; bwid = w - 44
    g += f'<rect x="{x:.0f}" y="{yb-h:.0f}" width="{bwid:.0f}" height="{h:.0f}" rx="4" fill="#0B7A3B"/>'
    g += big(x + bwid / 2, yb - h + 50, fd(v, 3), 42, '#FFF6D0', 'middle')
    sc = mt['match'].replace('Mali ', '').split(' ')[0] if mt['match'].startswith('Mali') else mt['match'].split(' ')[-2]
    g += txt(x + bwid / 2, yb + 38, l1, 24, 800, '#04331A', 'middle') + (txt(x + bwid / 2, yb + 66, l2, 24, 800, '#04331A', 'middle') if l2 else '')
yl = yb - mu / vmax * hmax
g += f'<line x1="{x0}" y1="{yl:.0f}" x2="{x1}" y2="{yl:.0f}" stroke="#D4252A" stroke-width="4" stroke-dasharray="12 9"/>'
g += txt(x1, yl - 14, f'MOYENNE DES 24 ÉQUIPES · {fd(mu,3)}', 24, 800, '#D4252A', 'end')
b = div(64, 600, 'BUT ATTENDU PAR TIR, MATCH PAR MATCH', LAB) + sv(g)
b += f'<div class="bigR" style="top:1300px"><b>{fd(m["npxg_per_shot"],3)}</b><span>BUT ATTENDU PAR TIR SUR LA CAN<br><em>{R["npxg_per_shot"]["rank"]}e SUR 24</em></span></div>'
out['s18_2'] = pageT('CAN 2023 · <b>LA QUALITÉ DES TIRS DU MALI</b>', 'LA QUALITÉ', 'CHUTE APRÈS LE 1er MATCH', '', b,
                     f'Buts attendus (xG) par tir hors penalty · Mali, 5 matchs · Données {SB}')

for kk, h in out.items(): open(f'_a14_{kk}.html', 'w', encoding='utf-8').write(h)
print(' '.join(out))
json.dump({'t16': T16}, open(SH + '/agent_maq1418/valeurs.json', 'w'), ensure_ascii=False, indent=1)

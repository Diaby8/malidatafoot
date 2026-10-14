"""Sujet 19 : plans clés TikTok (1080 x 1920), DA des posts. À lancer depuis visuels/ (comme poc.py)."""
import json, math, os
SH = '/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
MOI = SH + '/agent_s19'
exec(open(SH + '/maq_a.py', encoding='utf-8').read().split('# 1 : le score')[0])
SB = '<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
J = json.load(open(MOI + '/analyse.json', encoding='utf-8'))
def sv(inner): return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{inner}</svg>'
def txt(x, y, t, size=26, w=700, col='#064A25', anchor='start', fam='SC', it=False):
    st = f'font:{"italic " if it else ""}{w} {size}px {fam};fill:{col}'
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{st}">{t}</text>'
G, GF, ENC, CR, RO = '#0B7A3B', '#064A25', '#04331A', '#FFF3C4', '#D4252A'

# ---------------- 1 : l'âge (un bloc = un joueur)
rep = {int(k): v for k, v in J['age']['repartition'].items()}
a0, a1 = 22, 36; x0, x1 = 100, 920; yb = 1160; bw, bh, gp = 50, 74, 8
X = lambda a: x0 + (a - a0) / (a1 - a0) * (x1 - x0)
g = ''
xm = X(J['age']['mediane']); hm = rep[J['age']['mediane']] * (bh + gp)
g += f'<line x1="{xm:.1f}" y1="{yb-hm-150}" x2="{xm:.1f}" y2="{yb-hm-10}" stroke="{RO}" stroke-width="4" stroke-dasharray="10 8"/>' + txt(xm, yb - hm - 166, 'MÉDIANE', 26, 800, RO, 'middle')
for a, k in rep.items():
    col = G if a <= 23 else (GF if a >= 30 else CR)
    for i in range(k):
        g += f'<rect x="{X(a)-bw/2:.1f}" y="{yb - 6 - (i+1)*(bh+gp) + gp}" width="{bw}" height="{bh}" rx="4" fill="{col}"/>'
g += f'<line class="ax" x1="{x0-40}" y1="{yb}" x2="{x1+26}" y2="{yb}"/>'
for a in range(a0, a1 + 1, 2): g += txt(X(a), yb + 44, a, 28, 700, GF, 'middle')
g += txt(X(22) - bw/2, yb - 6 - 6*(bh+gp) - 24, '7 ONT 23 ANS OU MOINS', 30, 800, G)
for a, nm in ((30, 'L. COULIBALY'), (31, 'DJIGUI DIARRA'), (34, 'H. TRAORÉ'), (36, 'SAMASSA')):
    g += f'<text transform="translate({X(a)+9:.1f},{yb-6-(bh+gp)-14}) rotate(-90)" style="font:800 24px SC;fill:{ENC}">{nm}</text>'
g += txt(X(36) + bw/2, yb - 6 - (bh+gp) - 230, '4 ONT 30 ANS ET PLUS', 30, 800, GF, 'end')
b = sv(g)
b += f'<div style="position:absolute;left:64px;top:1226px;font:600 24px SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">ÂGE AU 25 SEPTEMBRE 2026 · UN BLOC = UN JOUEUR</div>'
b += f'<div class="bigR" style="top:1300px"><b>25 ANS</b><span>ÂGE MÉDIAN DES 21 JOUEURS<br>DONT LA DATE DE NAISSANCE<br>EST CONNUE</span></div>'
p1 = pageT('LISTE DE SEPTEMBRE 2026 · <b>L\'ÂGE DES AIGLES</b>', '7 JEUNES,', 'ET 4 ANCIENS', '', b,
           'Registre MaliDataFoot · Dates de naissance inconnues : Doucouré, A. Camara, Sagnan, Gory, Tia')

# ---------------- 2 : l'expérience
C = J['selections']['colonnes']; T = ['0', '1-9', '10-29', '30-49', '50+', 'inconnu']
LAB = {'0': '0', '1-9': '1 À 9', '10-29': '10 À 29', '30-49': '30 À 49', '50+': '50 ET +', 'inconnu': '?'}
x0, w = 64, 882 / 6; yb = 1150; r = 36; step = 80
g = f'<line class="ax" x1="{x0}" y1="{yb}" x2="{x0+882}" y2="{yb}"/>'
for j, t in enumerate(T):
    cx = x0 + w * j + w / 2
    g += txt(cx, yb + 46, LAB[t], 30, 800, GF, 'middle')
    for i, p in enumerate(C[t]):
        cy = yb - r - 10 - i * step
        if p['nom'] == 'Ange Martial Tia': fill = RO
        else: fill = G if p['can2023'] else CR
        g += f'<circle cx="{cx:.1f}" cy="{cy}" r="{r}" fill="{fill}"/>'
        if t == 'inconnu': g += txt(cx, cy + 10, '?', 30, 900, GF, 'middle', 'BC', True)
# annotation Tia (rond rouge, colonne 0, dernier rang)
it = [p['nom'] for p in C['0']].index('Ange Martial Tia'); ty = yb - r - 10 - it * step
g += txt(x0, 604, 'TIA, 1re CONVOCATION :', 28, 800, RO) + txt(x0, 636, '2 DES 4 BUTS EN ÉLIMINATOIRES', 28, 800, RO)
g += f'<line x1="{x0+w/2:.1f}" y1="652" x2="{x0+w/2:.1f}" y2="{ty-r-6}" stroke="{RO}" stroke-width="3"/>'
b = sv(g)
b += f'<div style="position:absolute;left:64px;top:1222px;font:600 24px SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">SÉLECTIONS AU 31 MARS 2026 · UN ROND = UN JOUEUR · ? = INCONNU</div>'
b += f'<div class="leg" style="top:1262px"><span><i style="display:block;width:26px;height:26px;border-radius:50%;background:{G}"></i>ÉTAIT À LA CAN 2023</span><span><i style="display:block;width:26px;height:26px;border-radius:50%;background:{CR}"></i>NON</span></div>'
pc = round(100 * J['can2023']['part_des_selections_connues'])
b += f'<div class="bigR" style="top:1330px"><b>{pc} %</b><span>DES SÉLECTIONS RECENSÉES<br>APPARTIENNENT AUX <em>9 RESCAPÉS</em></span></div>'
p2 = pageT('LISTE DE SEPTEMBRE 2026 · <b>L\'EXPÉRIENCE</b>', '9 RESCAPÉS', 'DE LA CAN 2023', '', b,
           f'Registre MaliDataFoot · CAN 2023 : feuilles de match {SB} · Buts : 11v11, APA News')

# ---------------- 3 : où ils jouent
DR.update({
 'France': v3('#0055A4', '#FFFFFF', '#EF4135'), 'Italie': v3('#009246', '#FFFFFF', '#CE2B37'), 'Belgique': v3('#000000', '#FDDA24', '#EF3340'),
 'Allemagne': h3('#000000', '#DD0000', '#FFCE00'), 'Russie': h3('#FFFFFF', '#0039A6', '#D52B1E'), 'Pays-Bas': h3('#AE1C28', '#FFFFFF', '#21468B'),
 'Angleterre': '<rect width="20" height="20" fill="#fff"/><rect x="8" width="4" height="20" fill="#CE1124"/><rect y="8" width="20" height="4" fill="#CE1124"/>',
 'Espagne': '<rect width="20" height="20" fill="#AA151B"/><rect y="5" width="20" height="10" fill="#F1BF00"/>',
 'Turquie': '<rect width="20" height="20" fill="#E30A17"/><circle cx="8.6" cy="10" r="4.6" fill="#fff"/><circle cx="9.8" cy="10" r="3.7" fill="#E30A17"/>' + et(13.6, 10, 1.9, '#fff'),
 'Tchéquie': '<rect width="20" height="10" fill="#fff"/><rect y="10" width="20" height="10" fill="#D7141A"/><polygon points="0,0 10,10 0,20" fill="#11457E"/>',
 'Arabie saoudite': '<rect width="20" height="20" fill="#006C35"/><path d="M5 9.2q1.2-2 2.4 0t2.4 0t2.4 0t2.4 0" stroke="#fff" stroke-width="1" fill="none"/><path d="M5.5 13h9M14.5 12.2v1.6" stroke="#fff" stroke-width=".9"/>',
 'Tanzanie': '<rect width="20" height="20" fill="#00A3DD"/><polygon points="0,0 20,0 0,20" fill="#1EB53A"/><path d="M-2 22L22 -2" stroke="#FCD116" stroke-width="7"/><path d="M-2 22L22 -2" stroke="#000" stroke-width="4.6"/>',
 'Rwanda': '<rect width="20" height="20" fill="#20603D"/><rect width="20" height="15" fill="#FAD201"/><rect width="20" height="10" fill="#00A1DE"/><circle cx="15.5" cy="4.6" r="2.2" fill="#E5BE01"/>'})
def rond(pays, t=72):
    if ' ou ' in pays:
        return f'<svg width="{t}" height="{t}" viewBox="-1 -1 22 22" style="display:block"><circle cx="10" cy="10" r="10" fill="{CR}"/><text x="10" y="14.6" text-anchor="middle" style="font:italic 900 13px BC;fill:{GF}">?</text></svg>'
    return drap(pays, t)
ORD = ['France', 'France ou Allemagne', 'Angleterre', 'Espagne', 'Italie', 'Allemagne', 'Belgique', 'Belgique ou Italie', 'Turquie', 'Pays-Bas', 'Tchéquie', 'Russie', 'Tanzanie', 'Mali', 'Rwanda', 'Arabie saoudite']
cl = J['clubs']['detail']
def groupe(zone): return sorted([c for c in cl if c['zone'] == zone], key=lambda c: ORD.index(c['pays']))
def bloc(top, n, lab, liste, left=64, maxl=11, size=72, gap=8):
    h = f'<div style="position:absolute;left:{left}px;top:{top}px;display:flex;align-items:baseline;gap:14px;white-space:nowrap"><span style="font:italic 900 72px/.9 BC;color:{GF}">{n}</span><span style="font:800 30px SC;letter-spacing:.05em;color:{ENC}">{lab}</span></div>'
    h += f'<div style="position:absolute;left:{left}px;top:{top+82}px;width:{maxl*(size+gap)}px;display:flex;flex-wrap:wrap;gap:{gap}px">' + ''.join(rond(c['pays'], size) for c in liste) + '</div>'
    return h
t5, eu, af, asi = groupe('top5'), groupe('Europe (hors top 5)'), groupe('Afrique'), groupe('Asie')
b = bloc(520, len(t5), 'DANS LES 5 GRANDS CHAMPIONNATS', t5, maxl=6, size=88, gap=10)
b += bloc(810, len(eu), 'AILLEURS EN EUROPE', eu, maxl=6, size=88, gap=10)
b += bloc(1100, len(af), 'EN AFRIQUE', af, maxl=3, size=72, gap=10)
b += bloc(1100, len(asi), 'EN ASIE', asi, left=560, maxl=1, size=72, gap=10)
b += f'<div style="position:absolute;left:64px;top:1268px;font:600 24px SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">UN ROND = UN JOUEUR · DRAPEAU DU PAYS DE SON CLUB · ? = CLUB À CONFIRMER</div>'
b += f'<div class="bigR" style="top:1320px"><b>1</b><span>SEUL JOUE AU MALI :<br>N\'GOLO TRAORÉ, <em>STADE MALIEN</em></span></div>'
p3 = pageT('LISTE DE SEPTEMBRE 2026 · <b>OÙ JOUENT LES AIGLES</b>', f'{J["clubs"]["pays_distincts_surs"]} PAYS', 'POUR 26 AIGLES', '', b,
           'Clubs : liste du 10/09/2026 · Championnats 2026-2027, vérifiés le 14/10/2026')

os.makedirs(MOI, exist_ok=True)
for k, h in (('1', p1), ('2', p2), ('3', p3)): open(f'_a19_{k}.html', 'w', encoding='utf-8').write(h)
print('ok')

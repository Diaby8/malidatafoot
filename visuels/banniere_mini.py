"""Bannières X 1500 x 500 « minimalistes » dans la DA de la vidéo (13 octobre 2026).
Demande de Diaby : « minimaliste, notre data avec un terrain de foot, et MaliDataFoot en bas à gauche avec le logo »,
puis « arrête avec cette couleur (le vert), je veux comme dans la vidéo, la DA ».
Donc le style « vidéo » (vitv.tpl.html) : fond jaune dégradé #FBD134 -> #F6C41C -> #EFA40A, trame de points #FDEBA6 qui
grossit vers le coin haut droit, lignes du terrain crème #FFF3C4, données posées directement sur le fond (vert, blanc, rouge),
grand chiffre fantôme en contour #FFF6D0 (variante 2).
- terrain vu de dessus à l'échelle (105 x 68 m) ; une seule data viz : l'historique des Aigles (aigles_histoire.json, martj42, CC0) ;
- la signature (logo rond + Mali*Data*Foot) en bas, juste à droite de la photo de profil (qui couvre x 40-395, y 287-500).
usage : python3 banniere_mini.py <1..4> <sortie.html> [logo|sanslogo]"""
import json, math, sys, collections
from da import BASE_CSS, fr
K, OUT = int(sys.argv[1]), sys.argv[2]
AVEC_LOGO = (sys.argv[3] if len(sys.argv) > 3 else 'logo') == 'logo'
W, H = 1500, 500
VERT, VERT_D, ROUGE, BLANC, CREME = '#0B7A3B', '#064A25', '#D4252A', '#FFFFFF', '#FFF3C4'
HIST = json.load(open('aigles_histoire.json', encoding='utf-8'))['matchs']

# terrain vu de dessus, à l'échelle, centré ; les lignes de touche sortent du cadre (bannière 3:1, terrain 3:2)
S = 13.5; X0 = (W - 105 * S) / 2; CY = H / 2
px = lambda x: X0 + x * S
py = lambda y: CY + (y - 34) * S
def terrain(op=1, ep=2):
    L = f'stroke="{CREME}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'
    g = f'<rect x="{px(0)}" y="{py(0)}" width="{105*S}" height="{68*S}" {L}/><line x1="{px(52.5)}" y1="{py(0)}" x2="{px(52.5)}" y2="{py(68)}" {L}/>'
    g += f'<circle cx="{px(52.5)}" cy="{CY}" r="{9.15*S}" {L}/><circle cx="{px(52.5)}" cy="{CY}" r="3" fill="{CREME}"/>'
    a = math.degrees(math.acos(5.5 / 9.15)); dy = 9.15 * math.sin(math.radians(a)) * S
    for gauche in (True, False):
        bx = px(0) if gauche else px(105 - 16.5); gx = px(0) if gauche else px(105 - 5.5)
        g += f'<rect x="{bx}" y="{py(34-20.16)}" width="{16.5*S}" height="{40.32*S}" {L}/><rect x="{gx}" y="{py(34-9.16)}" width="{5.5*S}" height="{18.32*S}" {L}/>'
        sx = px(11) if gauche else px(94); g += f'<circle cx="{sx}" cy="{CY}" r="3" fill="{CREME}"/>'
        ax = px(16.5) if gauche else px(88.5)
        g += f'<path d="M{ax} {CY-dy:.1f}A{9.15*S} {9.15*S} 0 0 {1 if gauche else 0} {ax} {CY+dy:.1f}" {L}/>'
    return g

def trame_video(coin=(W, 0), coul='#FDEBA6', op=.85, pas=30):
    """La trame de la vidéo (vitv.tpl.html) : quinconce de 30 px, r = 1,2 + 9 (1 - d)^2,6, d = distance au coin / 1500."""
    g = ''; row = 0; y = pas / 2
    while y < H:
        x = pas / 2 + (pas / 2 if row % 2 else 0)
        while x < W:
            d = math.hypot(x - coin[0], y - coin[1]) / 1500; g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.2 + 9*max(0, 1-d)**2.6:.2f}"/>'; x += pas
        y += pas; row += 1
    return f'<g fill="{coul}" fill-opacity="{op}">{g}</g>'

def fantome(txt, x, y, t=380):
    """Le grand chiffre fantôme en contour de la vidéo."""
    return f'<text x="{x}" y="{y}" text-anchor="end" style="font:italic 900 {t}px BC;fill:none;stroke:#FFF6D0;stroke-width:4;opacity:.6">{txt}</text>'

def etiquette(x, y, txt, ancre='middle', op=.8, t=13, poids=500):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{ancre}" style="font:{poids} {t}px IN;fill:{VERT_D};fill-opacity:{op};letter-spacing:.01em">{txt}</text>'

def legende(x, y, items, op=.85):
    g = ''; cx = x
    for coul, txt in items:
        g += f'<circle cx="{cx+5}" cy="{y-4.5}" r="5" fill="{coul}"/>' + etiquette(cx + 15, y, txt, 'start', op); cx += 15 + len(txt) * 7.2 + 22
    return g

# ---------------------------------------------------------------- les data viz
COUL = {'V': VERT, 'N': BLANC, 'D': ROUGE}
def tous_les_matchs(x0=470, x1=1444, base=372, r=4.5):
    """Un point par match, une colonne par année, empilés victoires, nuls puis défaites."""
    ans = list(range(int(HIST[0]['date'][:4]), int(HIST[-1]['date'][:4]) + 1)); par = collections.defaultdict(list)
    for m in HIST: par[m['annee']].append(m['resultat'])
    pas = (x1 - x0) / len(ans); g = ''; n = 0
    for i, a in enumerate(ans):
        for j, k in enumerate(sorted(par.get(a, []), key='VND'.index)):
            g += f'<circle cx="{x0+(i+.5)*pas:.1f}" cy="{base-(j+.5)*pas:.1f}" r="{r}" fill="{COUL[k]}"/>'; n += 1
    assert n == len(HIST)
    g += f'<line x1="{x0}" y1="{base+6}" x2="{x1}" y2="{base+6}" stroke="{VERT_D}" stroke-opacity=".55" stroke-width="1.4"/>'
    for a in (1960, 1980, 2000, 2020):
        x = x0 + (a - ans[0] + .5) * pas; g += f'<line x1="{x:.1f}" y1="{base+6}" x2="{x:.1f}" y2="{base+12}" stroke="{VERT_D}" stroke-opacity=".55" stroke-width="1.4"/>' + etiquette(x, base + 28, a)
    top = base - 19 * pas
    g += etiquette(x0, top - 30, f'{len(HIST)} matchs des Aigles depuis {ans[0]}, un point par match', 'start', .95, 15, 600)
    g += legende(x0, top - 10, [(VERT, 'victoire'), (BLANC, 'nul'), (ROUGE, 'défaite')])
    return g

def decennies(x0=760, x1=1440, base=380, h=240):
    """Buts marqués et encaissés par match, décennie par décennie (barres fines)."""
    dec = collections.defaultdict(lambda: [0, 0, 0])
    for m in HIST: d = dec[m['annee'] // 10 * 10]; d[0] += 1; d[1] += m['buts_pour']; d[2] += m['buts_contre']
    D_ = sorted(dec); gw = (x1 - x0) / len(D_); bw = 16; ymax = 2.0; g = ''
    for v in (1, 2):
        y = base - v / ymax * h; g += f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{VERT_D}" stroke-opacity=".3" stroke-width="1" stroke-dasharray="2 5"/>' + etiquette(x0 - 10, y + 4, str(v), 'end', .7)
    for i, d in enumerate(D_):
        n, bp, bc = dec[d]; x = x0 + (i + .5) * gw
        for k, (v, c) in enumerate(((bp / n, VERT), (bc / n, ROUGE))):
            xb = x - bw - 3 if k == 0 else x + 3; g += f'<rect x="{xb:.1f}" y="{base-v/ymax*h:.1f}" width="{bw}" height="{v/ymax*h:.1f}" rx="2" fill="{c}"/>'
        g += etiquette(x, base + 24, f"années {str(d)[2:] if d < 2000 else d}")
    g += f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{VERT_D}" stroke-opacity=".55" stroke-width="1.4"/>'
    g += etiquette(x0, base - h - 34, 'Buts par match des Aigles, décennie par décennie', 'start', .95, 15, 600)
    g += legende(x0, base - h - 14, [(VERT, 'marqués'), (ROUGE, 'encaissés')])
    return g

def scores(cx=1010, cy=262, cs=46, K_=5):
    """La grille des scores : buts du Mali (lignes) x buts de l'adversaire (colonnes), la taille suit la fréquence."""
    cap = lambda v: min(v, K_); cnt = collections.Counter((cap(m['buts_pour']), cap(m['buts_contre'])) for m in HIST); mx = max(cnt.values())
    gx, gy = cx - (K_ + 1) * cs / 2, cy - (K_ + 1) * cs / 2 + 14; g = ''
    for i in range(K_ + 1):
        lab = '5+' if i == K_ else str(i)
        g += etiquette(gx + (i + .5) * cs, gy - 10, lab) + etiquette(gx - 12, gy + (i + .5) * cs + 4, lab, 'end')
        for j in range(K_ + 1):
            x, y = gx + (j + .5) * cs, gy + (i + .5) * cs; v = cnt.get((i, j), 0)
            g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.6" fill="{VERT_D}" fill-opacity=".35"/>'
            if v: g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{max(3, math.sqrt(v/mx)*cs*.46):.1f}" fill="{COUL["V" if i > j else ("N" if i == j else "D")]}"/>'
    g += etiquette(gx + (K_ + 1) * cs / 2, gy - 32, 'buts de l’adversaire', 'middle', .7, 12)
    g += f'<text transform="translate({gx-34:.0f} {gy+(K_+1)*cs/2:.0f}) rotate(-90)" text-anchor="middle" style="font:500 12px IN;fill:#064A25;fill-opacity:.75">buts du Mali</text>'
    lx = gx - 300   # la légende à gauche de la grille : à droite, elle passerait sous les boutons de X sur téléphone
    g += etiquette(lx, gy + 22, 'Les scores des Aigles', 'start', .95, 15, 600) + etiquette(lx, gy + 42, f'{len(HIST)} matchs depuis 1960', 'start', .75, 13)
    g += legende(lx, gy + 70, [(VERT, 'victoire')]) + legende(lx, gy + 92, [(BLANC, 'nul')]) + legende(lx, gy + 114, [(ROUGE, 'défaite')])
    return g

def signature(x=432, y=438, t=40):
    logo = (f'<img src="logo-verte.png" style="position:absolute;left:{x}px;top:{y-4}px;width:{t*1.25:.0f}px;height:{t*1.25:.0f}px;border-radius:50%;box-shadow:0 0 0 3px #fff">'
            if AVEC_LOGO else '')
    dx = t * 1.25 + 16 if AVEC_LOGO else 0
    return logo + f'<div style="position:absolute;left:{x+dx:.0f}px;top:{y}px;font:italic 400 {t}px/1.25 \'BCS\';color:#064A25;white-space:nowrap">Mali<i style="font-weight:600">Data</i>Foot</div>'

if K == 1:   corps = terrain() + tous_les_matchs()
elif K == 2: corps = fantome(len(HIST), 1470, 400) + terrain() + tous_les_matchs()
elif K == 3: corps = terrain() + decennies()
else:        corps = terrain() + scores()
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">{trame_video()}{corps}</svg>'
open(OUT, 'w', encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px!important;height:{H}px!important;overflow:hidden!important;background:#F6C41C!important}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)}}svg{{display:block}}
</style></head><body><div id="b">{svg}{signature()}</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok', K, OUT)

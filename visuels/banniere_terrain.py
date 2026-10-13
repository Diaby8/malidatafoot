"""Bannières X 1500 x 500, série « terrain derrière » (13 octobre 2026), nouvelle DA.
Deux familles :
- la data dessine le terrain : un vrai terrain à l'échelle (repère StatsBomb 120 x 80, le Mali attaque vers la droite),
  avec les 2 153 passes réussies et les 64 tirs du Mali à la CAN 2023 (banniere_passes.json, tiré de silver.events) ;
- cartes penchées sur le terrain : les vrais gabarits allégés (reel/<plan><thème>.png, faits par reel_cartes.py).
Aucun nom de joueur, aucun chiffre, aucune écriture hormis le crédit StatsBomb exigé par la licence.
usage : python3 banniere_terrain.py <1..8> <sortie.html>"""
import json, math, sys
from da import BASE_CSS
K, OUT = int(sys.argv[1]), sys.argv[2]
W, H = 1500, 500
OR, VERT, VERT_D, NUIT = '#F6C41C', '#0B7A3B', '#064A25', '#04331A'
RADIAL = 'radial-gradient(120% 95% at 50% 0%, #0A5A2E 0%, #064A25 45%, #04331A 100%)'
D = json.load(open('banniere_passes.json', encoding='utf-8'))

# ---------------------------------------------------------------- repère du terrain à l'échelle
S, X0, CY = 10.5, 120, 250            # 1 m StatsBomb = 10,5 px ; buts à x = 120 et x = 1380 ; axe du terrain à y = 250
px = lambda x: X0 + x * S
py = lambda y: CY + (y - 40) * S
HALF = px(60)

def svg(contenu, defs=''):
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><defs>{defs}</defs>{contenu}</svg>'

def terrain_echelle(coul, op, ep=3):
    L = f'stroke="{coul}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'
    g = f'<rect x="{px(0)}" y="{py(0)}" width="{120*S}" height="{80*S}" {L}/>'
    g += f'<line x1="{HALF}" y1="{py(0)}" x2="{HALF}" y2="{py(80)}" {L}/><circle cx="{HALF}" cy="{CY}" r="{10*S}" {L}/>'
    g += f'<circle cx="{HALF}" cy="{CY}" r="4" fill="{coul}" fill-opacity="{op}"/>'
    a = math.degrees(math.acos(6 / 10)); dy = 10 * math.sin(math.radians(a)) * S
    for gauche in (True, False):
        bx = px(0) if gauche else px(102); gx = px(0) if gauche else px(114); sx = px(12) if gauche else px(108)
        g += f'<rect x="{bx}" y="{py(18)}" width="{18*S}" height="{44*S}" {L}/><rect x="{gx}" y="{py(30)}" width="{6*S}" height="{20*S}" {L}/>'
        g += f'<circle cx="{sx}" cy="{CY}" r="4" fill="{coul}" fill-opacity="{op}"/>'
        ax = px(18) if gauche else px(102)
        g += f'<path d="M{ax} {CY-dy:.1f}A{10*S} {10*S} 0 0 {1 if gauche else 0} {ax} {CY+dy:.1f}" {L}/>'
        but = px(0) - 2.4 * S if gauche else px(120)
        g += f'<rect x="{but}" y="{py(36)}" width="{2.4*S}" height="{8*S}" {L}/>'
    return g

def densite(coul, op_min=1, op_max=1, rmin=1.1, rmax=9.5, pas=26, sigma=3.2, gamma=1.0, clip=''):
    """La trame de points devient la donnée : même quinconce que la trame de la DA, mais chaque point grossit selon la densité
    des actions avec ballon du Mali à cet endroit (passes, conduites, tirs et dribbles, lieu de départ ; 5 matchs de la CAN 2023).
    Densité lissée (noyau gaussien de sigma mètres), rayon proportionnel à la racine de la densité."""
    import numpy as np
    A = np.array(D['actions_avec_ballon'], dtype=float)
    pts = []; row = 0; y = pas / 2
    while y < H:
        x = pas / 2 + (pas / 2 if row % 2 else 0)
        while x < W: pts.append((x, y)); x += pas
        y += pas; row += 1
    P = np.array(pts); mx = (P[:, 0] - X0) / S; my = (P[:, 1] - CY) / S + 40
    dens = np.zeros(len(P))
    for i in range(0, len(A), 500):
        a = A[i:i+500]; d2 = (mx[:, None] - a[None, :, 0])**2 + (my[:, None] - a[None, :, 1])**2
        dens += np.exp(-d2 / (2 * sigma**2)).sum(1)
    v = (dens / dens.max()) ** (gamma / 2)
    c = f' clip-path="url(#{clip})"' if clip else ''
    g = ''.join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rmin+(rmax-rmin)*t:.2f}" fill-opacity="{op_min+(op_max-op_min)*t**.8:.2f}"/>' for (x, y), t in zip(pts, v))
    return f'<g fill="{coul}"{c}>{g}</g>'

def passes(coul, op, ep=1.4, clip=''):
    d = ''.join(f'M{px(x):.0f} {py(y):.0f}L{px(ex):.0f} {py(ey):.0f}' for x, y, ex, ey in D['passes'])
    c = f' clip-path="url(#{clip})"' if clip else ''
    return f'<path d="{d}" stroke="{coul}" stroke-opacity="{op}" stroke-width="{ep}" stroke-linecap="round" fill="none"{c}/>'

def tirs(but, autre, autre_op, fond, clip=''):
    """Même lecture que le gabarit « tirs » : plus le rond est gros, plus l'occasion était belle ; les buts sont pleins."""
    R = lambda v: max(4.5, math.sqrt(v) * 38 * S / 12.1)
    c = f' clip-path="url(#{clip})"' if clip else ''
    g = ''
    for t in sorted(D['shots'], key=lambda t: (t['but'], -t['xg'])):
        x, y, r = px(t['x']), py(t['y']), R(t['xg'])
        if t['but']:
            g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{but}" stroke="{fond}" stroke-width="3"/>'
        else:
            g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{autre}" fill-opacity=".14" stroke="{autre}" stroke-opacity="{autre_op}" stroke-width="2"/>'
    return f'<g{c}>{g}</g>'

# ---------------------------------------------------------------- trame de points (quinconce, les points grossissent vers un coin)
def trame(coul, op, coin=(W, 0), portee=1150, rmax=8.5, pas=26):
    g = ''; row = 0; y = pas / 2
    while y < H:
        x = pas / 2 + (pas / 2 if row % 2 else 0)
        while x < W:
            dd = math.hypot(x - coin[0], y - coin[1]) / portee; r = 1.1 + rmax * max(0, 1 - dd) ** 2.6
            if dd < 1: g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'
            x += pas
        y += pas; row += 1
    return svg(f'<g fill="{coul}" fill-opacity="{op}">{g}</g>')

# ---------------------------------------------------------------- terrain décoratif (pas à l'échelle) derrière les cartes
def terrain_deco(coul='#fff', op=.5):
    L = f'stroke="{coul}" stroke-opacity="{op}" stroke-width="3" fill="none"'
    return svg(f'<rect x="-40" y="-60" width="{W+80}" height="{H+120}" {L}/><line x1="{W/2}" y1="-60" x2="{W/2}" y2="{H+60}" {L}/><circle cx="{W/2}" cy="{H/2}" r="120" {L}/>'
               f'<rect x="-40" y="{H/2-235}" width="250" height="470" {L}/><rect x="-40" y="{H/2-105}" width="95" height="210" {L}/><path d="M210 {H/2-88}A120 120 0 0 1 210 {H/2+88}" {L}/>'
               f'<rect x="{W-210}" y="{H/2-235}" width="250" height="470" {L}/><rect x="{W-55}" y="{H/2-105}" width="95" height="210" {L}/><path d="M{W-210} {H/2-88}A120 120 0 0 0 {W-210} {H/2+88}" {L}/>')

# ---------------------------------------------------------------- cartes (vrais gabarits allégés)
def cartes(L, lisere=True):
    """L : (carte, x, y, largeur, angle). Liseré blanc et ombre comme la bannière « terrain derrière, cartes penchées »."""
    cs = 'border-radius:9px;box-shadow:0 0 0 4px #fff,0 18px 34px rgba(40,26,0,.32)' if lisere else 'border-radius:12px;box-shadow:0 18px 34px rgba(0,0,0,.38)'
    from PIL import Image
    taille = lambda n: Image.open(f'reel/{n}.png').size
    return ''.join(f'<img src="reel/{n}.png" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w*taille(n)[1]/taille(n)[0]:.0f}px;transform:rotate({r}deg);{cs}">' for n, x, y, w, r in L)

def credit(sombre):
    """Crédit exigé par la licence StatsBomb ; sur fond sombre, le logo est posé sur une pastille blanche."""
    img = '<img src="logo_statsbomb.png" alt="StatsBomb" style="height:15px;width:auto;display:block">'
    if sombre: img = f'<span style="display:block;background:#fff;border-radius:5px;padding:3px 6px">{img}</span>'
    c = 'rgba(255,255,255,.78)' if sombre else 'rgba(14,26,19,.72)'
    return f'<div style="position:absolute;right:18px;bottom:14px;display:flex;align-items:center;gap:6px;font:500 13px/1 \'IN\';color:{c}">Données {img}</div>'

# ---------------------------------------------------------------- les variantes
DISPERSE = lambda a, b, c, d: [(a, 150, 22, 316, 2.2), (b, 418, 150, 400, -2.4), (c, 850, 20, 380, 1.8), (d, 1222, 160, 380, -2.6)]
EVENTAIL = lambda a, b, c: [(a, 540, 150, 400, -7), (b, 800, 104, 410, 0), (c, 1056, 156, 400, 7)]
if K == 1:    # la trame de points devient la donnée : où le Mali a eu le ballon, encre verte sur le jaune
    bg = OR; sombre = False
    corps = svg(terrain_echelle('#fff', .7) + densite(VERT_D))
elif K == 2:  # la même, la nuit
    bg = RADIAL; sombre = True
    corps = svg(terrain_echelle('#3E8A5E', .8) + densite(OR))
elif K == 3:  # moitié jaune, moitié nuit, coupé à la ligne médiane
    bg = OR; sombre = True
    defs = f'<clipPath id="g"><rect x="0" y="0" width="{HALF}" height="{H}"/></clipPath><clipPath id="d"><rect x="{HALF}" y="0" width="{W-HALF}" height="{H}"/></clipPath>'
    corps = svg(f'<rect x="{HALF}" y="0" width="{W-HALF}" height="{H}" fill="{NUIT}"/>'
                f'<g clip-path="url(#g)">{terrain_echelle("#fff", .7)}</g><g clip-path="url(#d)">{terrain_echelle("#3E8A5E", .85)}</g>'
                + densite(VERT_D, clip='g') + densite(OR, clip="d"), defs)
elif K == 4:  # la composition qu'il aimait, refaite : terrain jaune, cartes penchées et dispersées, trame
    bg = OR; sombre = False
    corps = trame('#FDEBA6', .9, coin=(W, H), portee=1000) + terrain_deco() + cartes(DISPERSE('tirsA', 'radarA', 'filA', 'reseauB'))
elif K == 5:  # la même sur un terrain de nuit : les cartes jaunes ressortent
    bg = RADIAL; sombre = True
    corps = trame('#19A552', .3, coin=(W, H), portee=1000) + terrain_deco('#3E8A5E', .8) + cartes(DISPERSE('tirsA', 'radarA', 'filA', 'reseauA'), lisere=False)
elif K == 6:  # la trame de données en fond (claire), deux grandes cartes devant
    bg = OR; sombre = False
    corps = svg(terrain_echelle('#fff', .6) + densite('#FFF1B8')) + cartes([('tirsA', 540, 34, 430, -2.2), ('filA', 1010, 150, 420, 2.2)])
elif K == 7:  # éventail : trois grandes cartes ouvertes comme une main, terrain et trame
    bg = OR; sombre = False
    corps = trame('#FDEBA6', .9, coin=(W, 0), portee=1100) + terrain_deco() + cartes(EVENTAIL('filA', 'radarA', 'tirsA'))
else:         # éventail sur la nuit
    bg = RADIAL; sombre = True
    corps = trame('#19A552', .3, coin=(W, 0), portee=1100) + terrain_deco('#3E8A5E', .8) + cartes(EVENTAIL('filA', 'radarA', 'tirsA'), lisere=False)

I800 = '@font-face{font-family:"IN";font-weight:800;src:url(node_modules/@fontsource/inter/files/inter-latin-800-normal.woff2)}'
open(OUT, 'w', encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}{I800}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}svg{{display:block}}img{{display:block}}
</style></head><body><div id="b">{corps}{credit(sombre)}</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok', K, OUT)

"""Bannières X 1500 x 500 « stade de nuit » (13 octobre 2026) : choix de Diaby = stade de nuit en 3D, interfaces qui flottent,
du mouvement, et l'accroche « Les Aigles jouent. La data parle. ».
Le terrain est un vrai terrain (105 x 68 m) vu par une caméra en perspective ; les données sortent du terrain :
les 572 matchs des Aigles depuis 1960 (aigles_histoire.json), un point lumineux par match, une colonne par année
(victoires, puis nuls, puis défaites, du bas vers le haut). Les traînées de lumière sont du décor (pas des trajectoires réelles).
Les cartes qui flottent sont les vrais gabarits « histoire » allégés (reel/<plan><thème>.png, faits par reel_histoire.py).
usage : python3 banniere_stade.py <1..4> <sortie.html> [accroche|nom|rien]   (python3 aigles_export.py et python3 reel_histoire.py d'abord)"""
import json, math, sys, collections
from da import BASE_CSS
K, OUT = int(sys.argv[1]), sys.argv[2]
TEXTE = sys.argv[3] if len(sys.argv) > 3 else 'accroche'   # accroche | nom | rien : Diaby hésite (« le slogan fait trop, mais fais quand même », « peut-être MaliDataFoot ? »)
BOITE = None
W, H = 1500, 500
OR, NUIT, BLANC, CORAIL = '#F6C41C', '#04331A', '#FFFFFF', '#FF7A6B'
HIST = json.load(open('aigles_histoire.json', encoding='utf-8'))['matchs']

# ---------------------------------------------------------------- caméra
class Camera:
    """Caméra à sténopé : position (x, y, z) en mètres, cap (lacet) et inclinaison en degrés, focale en px."""
    def __init__(s, pos, lacet, incl, f, cx, cy):
        s.p, s.f, s.cx, s.cy = pos, f, cx, cy
        a, b = math.radians(lacet), math.radians(incl)
        s.ca, s.sa, s.cb, s.sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    def cam(s, X, Y, Z):
        x, y, z = X - s.p[0], Y - s.p[1], Z - s.p[2]
        x, z = s.ca * x - s.sa * z, s.sa * x + s.ca * z          # lacet autour de l'axe vertical
        y, z = s.cb * y + s.sb * z, -s.sb * y + s.cb * z         # inclinaison vers le bas
        return x, y, z
    def __call__(s, X, Y, Z):
        x, y, z = s.cam(X, Y, Z)
        z = max(z, .5)
        return s.cx + s.f * x / z, s.cy - s.f * y / z, z

def poly(cam, pts, ferme=False):
    P = [cam(*p) for p in pts]
    d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y, _ in P)
    return d + ('Z' if ferme else '')

# ---------------------------------------------------------------- le terrain (repère : x le long du terrain 0..105, z en profondeur 0..68, y vers le haut)
L_, l_ = 105.0, 68.0
def lignes_terrain(cam):
    g = []
    g.append(poly(cam, [(0, 0, 0), (L_, 0, 0), (L_, 0, l_), (0, 0, l_)], True))
    g.append(poly(cam, [(L_/2, 0, 0), (L_/2, 0, l_)]))
    g.append(poly(cam, [(L_/2 + 9.15*math.cos(t/60*2*math.pi), 0, l_/2 + 9.15*math.sin(t/60*2*math.pi)) for t in range(61)]))
    for gauche in (True, False):
        x0 = 0 if gauche else L_; s = 1 if gauche else -1
        g.append(poly(cam, [(x0, 0, l_/2-20.16), (x0+s*16.5, 0, l_/2-20.16), (x0+s*16.5, 0, l_/2+20.16), (x0, 0, l_/2+20.16)]))
        g.append(poly(cam, [(x0, 0, l_/2-9.16), (x0+s*5.5, 0, l_/2-9.16), (x0+s*5.5, 0, l_/2+9.16), (x0, 0, l_/2+9.16)]))
        a0 = math.acos(5.5/9.15)
        arc = [(x0+s*(11+9.15*math.cos(u)), 0, l_/2+9.15*math.sin(u)) for u in [(-a0 + i*(2*a0)/30) for i in range(31)]]
        g.append(poly(cam, arc))
        # buts (2,44 m de haut, 7,32 m de large)
        g.append(poly(cam, [(x0, 0, l_/2-3.66), (x0, 2.44, l_/2-3.66), (x0, 2.44, l_/2+3.66), (x0, 0, l_/2+3.66)]))
    return g

def bandes(cam, n=14):
    """Bandes de tonte, alternées, à peine visibles."""
    out = []
    for i in range(n):
        if i % 2: continue
        x0, x1 = i*L_/n, (i+1)*L_/n
        out.append(poly(cam, [(x0, 0, 0), (x1, 0, 0), (x1, 0, l_), (x0, 0, l_)], True))
    return out

def points_matchs(cam, depart, arrivee, pas_y=1.0, rayon=.36):
    """Les 572 matchs : une colonne par année le long du segment depart -> arrivee (posé sur la pelouse), un point par match."""
    ans = list(range(int(HIST[0]['date'][:4]), int(HIST[-1]['date'][:4]) + 1)); par = collections.defaultdict(list)
    for m in HIST: par[m['annee']].append(m['resultat'])
    coul = {'V': OR, 'N': BLANC, 'D': CORAIL}; pts = []
    for i, a in enumerate(ans):
        t = (i + .5) / len(ans); X = depart[0] + t*(arrivee[0]-depart[0]); Z = depart[1] + t*(arrivee[1]-depart[1])
        for j, k in enumerate(sorted(par.get(a, []), key='VND'.index)):
            x, y, z = cam(X, (j + .6) * pas_y, Z); xr, _, _ = cam(X + rayon, (j + .6) * pas_y, Z)
            pts.append((z, x, y, max(1.1, abs(xr - x)), coul[k]))
    pts.sort(key=lambda p: -p[0])          # du plus loin au plus près
    global BOITE; BOITE = (min(p[1]-p[3] for p in pts), min(p[2]-p[3] for p in pts), max(p[1]+p[3] for p in pts), max(p[2]+p[3] for p in pts))
    return ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}"/>' for _, x, y, r, c in pts), len(pts)

def reflets(cam, depart, arrivee):
    """Le reflet des colonnes sur la pelouse mouillée : quelques points écrasés, très transparents."""
    ans = list(range(1960, 2027)); par = collections.Counter(m['annee'] for m in HIST); g = ''
    for i, a in enumerate(ans):
        t = (i + .5) / len(ans); X = depart[0] + t*(arrivee[0]-depart[0]); Z = depart[1] + t*(arrivee[1]-depart[1])
        x, y, z = cam(X, 0, Z); x2, y2, _ = cam(X, -min(par.get(a, 0), 6) * 1.0, Z)
        g += f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{OR}" stroke-opacity=".16" stroke-width="{max(1.2, 1500/z*.06):.1f}" stroke-linecap="round"/>'
    return g

def trainees(cam, liste):
    """Traînées de lumière (décor) : courbes de Bézier posées à quelques mètres au-dessus de la pelouse."""
    g = ''
    for i, (p0, p1, p2, coul, ep) in enumerate(liste):
        P = [cam(*p) for p in (p0, p1, p2)]
        d = f'M{P[0][0]:.1f} {P[0][1]:.1f}Q{P[1][0]:.1f} {P[1][1]:.1f} {P[2][0]:.1f} {P[2][1]:.1f}'
        g += (f'<linearGradient id="tr{i}" gradientUnits="userSpaceOnUse" x1="{P[0][0]:.0f}" y1="{P[0][1]:.0f}" x2="{P[2][0]:.0f}" y2="{P[2][1]:.0f}">'
              f'<stop offset="0" stop-color="{coul}" stop-opacity="0"/><stop offset=".7" stop-color="{coul}" stop-opacity=".7"/><stop offset="1" stop-color="{coul}" stop-opacity="1"/></linearGradient>'
              f'<path d="{d}" stroke="url(#tr{i})" stroke-width="{ep}" fill="none" stroke-linecap="round" filter="url(#flou)"/>'
              f'<path d="{d}" stroke="url(#tr{i})" stroke-width="{ep*.35:.2f}" fill="none" stroke-linecap="round"/>')
        g += f'<circle cx="{P[2][0]:.1f}" cy="{P[2][1]:.1f}" r="{ep*.9:.1f}" fill="{coul}" filter="url(#flou)"/><circle cx="{P[2][0]:.1f}" cy="{P[2][1]:.1f}" r="{ep*.45:.1f}" fill="#fff"/>'
    return g

def tribunes(cam):
    """Les tribunes au fond : des rangées de petits points (notre trame), plus denses et plus claires près des projecteurs."""
    g = ''
    for row in range(9):
        Y = 3 + row * 2.2; Z = l_ + 8 + row * 2.4
        for k in range(-30, 150, 2):
            X = k * 1.0
            x, y, z = cam(X, Y, Z)
            if -10 < x < W + 10 and -10 < y < H:
                lum = .18 + .5 * max(0, 1 - min(abs(x - 260), abs(x - 1240)) / 520) ** 2
                g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(.9, 1500/z*.035):.2f}" fill="#FDEBA6" fill-opacity="{lum:.2f}"/>'
    return g

def flaques(cam):
    """Là où les projecteurs éclairent la pelouse : deux grandes flaques de lumière (cercles de 30 m posés au sol)."""
    g = ''
    for i, (X, Z) in enumerate(((22, 40), (84, 40))):
        P = [cam(X + 30*math.cos(t/48*2*math.pi), 0, Z + 22*math.sin(t/48*2*math.pi)) for t in range(48)]
        cx, cy, _ = cam(X, 0, Z); rx = (max(p[0] for p in P) - min(p[0] for p in P)) / 2
        g += f'<radialGradient id="fl{i}" cx="{cx:.0f}" cy="{cy:.0f}" r="{rx:.0f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#B8FFC9" stop-opacity=".22"/><stop offset="1" stop-color="#19A552" stop-opacity="0"/></radialGradient>'
        g += '<path d="M' + 'L'.join(f'{x:.0f} {y:.0f}' for x, y, _ in P) + f'Z" fill="url(#fl{i})"/>'
    return g

def projecteurs():
    """Halos des projecteurs en haut à gauche et à droite, et leurs cônes de lumière."""
    g = ''
    for i, (x, y) in enumerate(((250, -40), (1250, -40))):
        g += f'<radialGradient id="h{i}" cx="{x}" cy="{y}" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFF6D0" stop-opacity=".55"/><stop offset=".25" stop-color="#F6C41C" stop-opacity=".16"/><stop offset="1" stop-color="#F6C41C" stop-opacity="0"/></radialGradient>'
        g += f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#h{i})"/>'
        for dx in (-150, -40, 70):
            g += f'<path d="M{x-6} {y}L{x+dx-90} {H+40}L{x+dx+90} {H+40}Z" fill="url(#cone)" opacity=".5"/>'
        for k in range(5):
            g += f'<circle cx="{x-48+k*24}" cy="{y+56}" r="5" fill="#FFFDF2" filter="url(#flou)"/><circle cx="{x-48+k*24}" cy="{y+56}" r="2.4" fill="#fff"/>'
    return g

def accroche(x=440, y=118, t1=44, t2=122, c1='#FFFFFF', c2=OR):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;font:800 {t1}px/1.1 \'IN\';letter-spacing:-.03em;color:{c1};white-space:nowrap;text-shadow:0 4px 24px rgba(0,0,0,.55)">Les Aigles jouent.</div>'
            f'<div style="position:absolute;left:{x-4}px;top:{y+t1*1.1+8:.0f}px;font:italic 900 {t2}px/.88 \'BC\';text-transform:uppercase;color:{c2};white-space:nowrap;text-shadow:0 0 40px rgba(246,196,28,.35),0 6px 28px rgba(0,0,0,.6)">La data<br>parle.</div>')

def signature(x=440, y=176, t=80):
    """La signature de la DA : Mali*Data*Foot (Barlow Condensed penché, « Data » en demi-gras), et la phrase de fin."""
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;font:italic 400 {t}px/1 \'BCS\';color:#fff;white-space:nowrap;text-shadow:0 6px 28px rgba(0,0,0,.45)">Mali<i style="font-weight:600;color:{OR}">Data</i>Foot</div>'
            f'<div style="position:absolute;left:{x+6}px;top:{y+t*1.04:.0f}px;font:500 {t*.25:.0f}px/1 \'IN\';color:#E6F2EA;white-space:nowrap;text-shadow:0 3px 14px rgba(0,0,0,.5)">La data du foot malien</div>')

def texte(y_acc=118, y_nom=176):
    if TEXTE == 'accroche': return accroche(y=y_acc)
    if TEXTE == 'nom': return signature(y=y_nom)
    return ''

def interfaces(L):
    """Cartes qui flottent en perspective, avec liseré lumineux et reflet sur la pelouse."""
    from PIL import Image
    out = ''
    for n, x, y, w, ry, rx, rz in L:
        tw, th = Image.open(f'reel/{n}.png').size; h = w * th / tw
        out += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h:.0f}px;perspective:1100px">'
                f'<img src="reel/{n}.png" style="width:100%;height:100%;display:block;border-radius:12px;transform:rotateY({ry}deg) rotateX({rx}deg) rotateZ({rz}deg);transform-origin:50% 50%;'
                f'box-shadow:0 0 0 1.5px rgba(246,196,28,.55),0 0 34px rgba(246,196,28,.22),0 30px 60px rgba(0,0,0,.55);'
                f'-webkit-box-reflect:below 6px linear-gradient(transparent 62%,rgba(255,255,255,.16))"></div>')
    return out

# ---------------------------------------------------------------- les variantes
DEFS = ('<filter id="flou" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2"/></filter>'
        '<filter id="lueur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF6D0" stop-opacity=".18"/><stop offset="1" stop-color="#FFF6D0" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="vign" cx="50%" cy="45%" r="78%"><stop offset=".62" stop-color="#06521F" stop-opacity="0"/><stop offset="1" stop-color="#06521F" stop-opacity=".42"/></radialGradient>'
        '<linearGradient id="pel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#17B53D"/><stop offset="1" stop-color="#0E922F"/></linearGradient>'
        '<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A6E33"/><stop offset="1" stop-color="#0E8F38"/></linearGradient>'
        '<linearGradient id="voile" x1="0" y1="0" x2="1" y2="0"><stop offset=".2" stop-color="#08612C" stop-opacity=".62"/><stop offset=".58" stop-color="#08612C" stop-opacity="0"/></linearGradient>')

def scene(cam, colonnes=None, trains=(), avec_reflets=True):
    pel = poly(cam, [(-30, 0, -40), (L_+30, 0, -40), (L_+30, 0, l_+8), (-30, 0, l_+8)], True)
    s = f'<rect width="{W}" height="{H}" fill="url(#ciel)"/>' + tribunes(cam)
    s += f'<path d="{pel}" fill="url(#pel)"/>' + ''.join(f'<path d="{d}" fill="#2AD457" fill-opacity=".22"/>' for d in bandes(cam))
    s += flaques(cam)
    s += ''.join(f'<path d="{d}" stroke="#FFFFFF" stroke-opacity=".42" stroke-width="1.8" fill="none" stroke-linejoin="round"/>' for d in lignes_terrain(cam))
    s += projecteurs()
    n = 0
    if colonnes:
        if avec_reflets: s += reflets(cam, *colonnes)
        pts, n = points_matchs(cam, *colonnes); s += f'<g filter="url(#lueur)">{pts}</g>'
    s += trainees(cam, trains)
    s += f'<rect width="{W}" height="{H}" fill="url(#vign)"/>' + (f'<rect width="{W}" height="{H}" fill="url(#voile)"/>' if TEXTE != 'rien' else '')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><defs>{DEFS}</defs>{s}</svg>', n

TRAINS = [((14, 2.2, 8), (46, 9, 26), (86, 3.2, 20)), ((8, 1.4, 40), (40, 7, 54), (72, 2.4, 47))]
CAM_LARGE = Camera((50, 22, -38), -10, 13, 900, 760, 210)      # vue large, un peu de biais
CAM_BAS = Camera((62, 10, -30), -14, 4, 800, 760, 230)          # au ras de la pelouse
if K == 1:    # les 572 matchs se dressent le long de la touche du fond, à droite ; le texte à gauche
    svg_, n = scene(CAM_LARGE, colonnes=((50, 62), (104, 62)), trains=[(a, b, c, BLANC, 3.4) for a, b, c in TRAINS])
    corps = svg_ + texte()
elif K == 2:  # deux interfaces qui flottent au-dessus de la pelouse, traînées de lumière
    svg_, n = scene(CAM_LARGE, trains=[(a, b, c, OR, 3.4) for a, b, c in TRAINS])
    corps = svg_ + texte() + interfaces([('decenniesB', 912, 70, 290, -24, 4, -1.5), ('scoresB', 1176, 110, 290, -28, 4, 1.5)])
elif K == 3:  # les colonnes au fond, à droite, et une interface devant
    svg_, n = scene(CAM_LARGE, colonnes=((50, 62), (104, 62)), trains=[(a, b, c, BLANC, 3.4) for a, b, c in TRAINS[:1]])
    corps = svg_ + texte() + interfaces([('decenniesB', 1060, 168, 360, -26, 5, -1)])
else:         # au ras de la pelouse : les colonnes viennent vers nous, en diagonale
    svg_, n = scene(CAM_BAS, colonnes=((102, 48), (60, 14)), trains=[(a, b, c, OR, 3) for a, b, c in TRAINS[:1]])
    corps = svg_ + texte(y_acc=140, y_nom=190)
if n: assert n == len(HIST), (n, len(HIST))   # chaque match a bien son point

open(OUT, 'w', encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
@font-face{{font-family:"IN";font-weight:800;src:url(node_modules/@fontsource/inter/files/inter-latin-800-normal.woff2)}}
html,body{{width:{W}px!important;height:{H}px!important;overflow:hidden!important;background:#0A6E33!important}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#0A6E33}}svg{{display:block}}
</style></head><body><div id="b">{corps}</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok', K, OUT, n, 'points', 'boîte', tuple(round(v) for v in BOITE) if n else '')

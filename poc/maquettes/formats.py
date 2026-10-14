"""Passe un plan d'un format à l'autre pour les POC : TikTok (1080 x 1920) -> X (1080 x 1350) et inversement.
Le plan source est intégré tel quel (fond rendu transparent) sur un fond neuf au bon format : mêmes textes, mêmes chiffres."""
import math, sys, re
SH = '/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
GRAD = 'linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)'

def trame(W, H, fx=1080, fy=0):
    g = ''; st = 30; y = st / 2; row = 0
    while y < H:
        x = st / 2 + (st / 2 if row % 2 else 0)
        while x < W:
            d = math.hypot(x - fx, y - fy) / 1500; g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.2+9*max(0,1-d)**2.6:.2f}"/>'; x += st
        y += st; row += 1
    return f'<svg style="position:absolute;left:0;top:0" width="{W}" height="{H}"><g fill="#FDEBA6" fill-opacity="0.85">{g}</g></svg>'

TRANSP = '<style>html,body{background:transparent!important}#c{background:none!important}#c>svg:first-of-type{display:none!important}</style>'

def transparent(src, dst):
    h = open(src, encoding='utf-8').read().replace('</head>', TRANSP + '</head>', 1)
    open(dst, 'w', encoding='utf-8').write(h)

def wrapper(dst, W, H, inner, iw, ih, s, left, top):
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}
#c{{position:relative;width:{W}px;height:{H}px;background:{GRAD};overflow:hidden}}
iframe{{position:absolute;left:{left}px;top:{top}px;width:{iw}px;height:{ih}px;border:0;transform:scale({s});transform-origin:0 0;background:transparent}}</style></head>
<body><div id="c">{trame(W, H)}<iframe id="f" src="{inner}" allowtransparency="true"></iframe></div>
<script>const f=document.getElementById('f');f.onload=()=>{{const t=setInterval(()=>{{if(f.contentWindow.READY){{clearInterval(t);window.READY=true}}}},50)}};</script></body></html>'''
    open(dst, 'w', encoding='utf-8').write(html)

def tt_vers_x(src, nom):
    """Plan TikTok -> X : on garde la zone utile (y 150 à 1600), réduite à 90 %."""
    transparent(src, f'_t_{nom}.html')
    s = 0.9; wrapper(f'_X_{nom}.html', 1080, 1350, f'_t_{nom}.html', 1080, 1920, s, int((1080 - 1080 * s) / 2), int(30 - 150 * s))

def x_vers_tt(src, nom):
    """Plan X -> TikTok : réduit à 84 %, posé dans la zone sûre (y 200 à 1335, x 30 à 937)."""
    transparent(src, f'_t_{nom}.html')
    s = 0.84; wrapper(f'_T_{nom}.html', 1080, 1920, f'_t_{nom}.html', 1080, 1350, s, 30, 200)

if __name__ == '__main__':
    sens, src, nom = sys.argv[1:4]
    (tt_vers_x if sens == 'x' else x_vers_tt)(src, nom)

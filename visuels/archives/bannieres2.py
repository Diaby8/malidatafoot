"""Bannières X 1500 x 500 pour le COMPTE MaliDataFoot : des bannières de marque, dessinées pour ce format.
Aucune ne reprend un visuel de la vidéo ou d'un post (ni carte de tirs, ni radar, ni réseau, ni fiche) : seulement la DA
(jaune, verts, rouge, titres penchés, petits points) et l'idée de la page, le football malien raconté par la data.
1 le terrain qui devient des points · 2 le Mali en points · 3 la traînée de points et les trois barres du logo · 4 le terrain-graphique
Zone à laisser libre : en bas à gauche (photo de profil, x 40-395, y 287-500 sur ordinateur) ; le texte commence à x >= 432.
usage : python3 bannieres2.py <1..4> <sortie.html>"""
import json, math, random, sys
from da import BASE_CSS
K,OUT=sys.argv[1],sys.argv[2]; W,H=1500,500
OR,VERT,VERT_D,NUIT,ROUGE,CLAIR='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A','#FDEBA6'

def trame(coul, op, fx, fy, portee=1050, pas=30, rmax=9):
    """La trame de la DA : points en quinconce, gros près d'un coin, de plus en plus petits en s'éloignant."""
    g=''; rang=0; y=pas/2
    while y<H+pas:
        x=pas/2+(pas/2 if rang%2 else 0)
        while x<W+pas:
            d=math.hypot(x-fx,y-fy)/portee; r=1.2+rmax*max(0,1-d)**2.6
            g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=pas
        y+=pas; rang+=1
    return f'<g fill="{coul}" fill-opacity="{op}">{g}</g>'
def terrain(coul='#fff', op=.5, ep=3):
    """Le terrain vu de dessus, plus grand que la bannière : on n'en voit que le milieu."""
    L=f'stroke="{coul}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'
    return (f'<rect x="-40" y="-60" width="{W+80}" height="{H+120}" {L}/><line x1="{W/2}" y1="-60" x2="{W/2}" y2="{H+60}" {L}/><circle cx="{W/2}" cy="{H/2}" r="120" {L}/><circle cx="{W/2}" cy="{H/2}" r="5" fill="{coul}" fill-opacity="{op}"/>'
            f'<rect x="-40" y="{H/2-235}" width="250" height="470" {L}/><rect x="-40" y="{H/2-105}" width="95" height="210" {L}/><path d="M210 {H/2-88}A120 120 0 0 1 210 {H/2+88}" {L}/>'
            f'<rect x="{W-210}" y="{H/2-235}" width="250" height="470" {L}/><rect x="{W-55}" y="{H/2-105}" width="95" height="210" {L}/><path d="M{W-210} {H/2-88}A120 120 0 0 0 {W-210} {H/2+88}" {L}/>')
titre=lambda x,y,t,lignes,al='left':(f'<div style="position:absolute;{"left" if al=="left" else "right"}:{x}px;top:{y}px;text-align:{al};font:italic 900 {t}px/.94 \'BC\';text-transform:uppercase;white-space:nowrap;letter-spacing:.005em">'
                                     +''.join(f'<div style="color:{c}">{s}</div>' for s,c in lignes)+'</div>')
extra=''
if K=='1':      # ---- le terrain qui devient des points : à gauche on joue, à droite la data parle
    bg=OR; k=.3; u0,u1=320,765; pas=20; g=''; rang=0; y=0
    g+=f'<polygon points="0,0 {u0+k*H/2},0 {u0-k*H/2},{H} 0,{H}" fill="{VERT}"/>'
    while y<H+pas:
        x=(pas/2 if rang%2 else 0)
        while x<W:
            u=x+k*(y-H/2); t=max(0,min(1,(u1-u)/(u1-u0)))
            if u>u0-pas*2 and t>0:
                r=pas*.74*t**.85
                if r>.7: g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'
            x+=pas
        y+=pas*.87; rang+=1
    g=f'<g fill="{VERT}">{g}</g>'
    lignes=f'<defs><linearGradient id="f" x1="0" x2="1"><stop offset=".3" stop-color="#fff"/><stop offset=".62" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs><g mask="url(#m)">{terrain("#fff",.75,3)}</g>'
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame(CLAIR,.9,W+40,H+40,900)}{g}{lignes}</svg>'
    extra=titre(54,158,88,(('Les Aigles jouent.',VERT_D),('La data parle.',ROUGE)),'right')
elif K=='2':    # ---- le Mali en points : la carte du pays dessinée avec la trame de la DA
    bg=NUIT; G=json.load(open('geo/mali.json', encoding='utf-8')); ring=G['coordinates'][0]
    lon0,lon1=min(p[0] for p in ring),max(p[0] for p in ring); lat0,lat1=min(p[1] for p in ring),max(p[1] for p in ring); cl=math.cos(math.radians((lat0+lat1)/2))
    S=424/(lat1-lat0); LW=(lon1-lon0)*cl*S; X0=W-52-LW; Y0=38; P=[(X0+(a-lon0)*cl*S,Y0+(lat1-b)*S) for a,b in ring]
    def dedans(x,y):
        c=False; n=len(P)
        for i in range(n):
            (x1,y1),(x2,y2)=P[i],P[(i+1)%n]
            if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
        return c
    pas=14; g=''; rang=0; y=Y0
    while y<Y0+430:
        x=X0-pas+(pas/2 if rang%2 else 0)
        while x<W:
            if dedans(x,y):
                d=math.hypot(x-(X0+LW*.2),y-(Y0+424))/560; r=2.3+3.9*max(0,1-d)**1.5
                g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>'
            x+=pas
        y+=pas*.87; rang+=1
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame(VERT,.55,-40,-40,900)}{terrain(VERT,.42,3)}<g fill="{OR}">{g}</g></svg>'
    extra=titre(432,104,104,(('Le football','#fff'),('malien','#fff'),('par la data.',OR)))
elif K=='3':    # ---- la traînée de points et les trois barres du logo, à l'échelle de la bannière
    bg=OR; random.seed(11); g=''
    bx,base=1168,424; barres=''.join(f'<rect x="{bx+i*96}" y="{base-h}" width="72" height="{h}" rx="9" fill="{c}"/>' for i,(h,c) in enumerate(((104,VERT),(176,'#fff'),(250,ROUGE))))
    # une file de points en cloche, comme la trajectoire d'un ballon : elle part de la photo de profil et retombe sur la plus haute barre
    p0,p1,p2=(392,262),(860,-112),(1396,158); N=30
    for i in range(N):
        t=i/(N-1); a=1-t; x=a*a*p0[0]+2*a*t*p1[0]+t*t*p2[0]; y=a*a*p0[1]+2*a*t*p1[1]+t*t*p2[1]; r=4+10*t**1.15
        c=VERT_D if t<.4 else ('#fff' if t<.74 else ROUGE)
        if i<N-1: g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}"/>'
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame(CLAIR,.9,W+40,-40,900)}{terrain("#fff",.5,3)}{g}{barres}</svg>'
else:           # ---- le terrain-graphique : le rond central devient un anneau de parts, la surface un diagramme en barres
    bg=OR; cx,cy,r=W/2,H/2,120
    def arc(a0,a1,c,ep=34):
        p=lambda a:(cx+r*math.cos(math.radians(a-90)),cy+r*math.sin(math.radians(a-90))); (x0,y0),(x1,y1)=p(a0),p(a1)
        return f'<path d="M{x0:.1f} {y0:.1f}A{r} {r} 0 {1 if a1-a0>180 else 0} 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{c}" stroke-width="{ep}"/>'
    g=arc(4,196,VERT_D)+arc(204,276,ROUGE)+arc(284,356,'#fff')
    ls=(318,236,372,168,274,120); y0,pas_b,eb=62,66,40
    g+=''.join(f'<rect x="{W-l}" y="{y0+i*pas_b}" width="{l+20}" height="{eb}" rx="7" fill="{ROUGE if i==2 else ("#fff" if i==4 else VERT_D)}"/>' for i,l in enumerate(ls))
    pts=((70,236),(168,176),(262,204),(356,118),(452,150),(566,62)); g+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{VERT_D}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>'
    g+=''.join(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{VERT_D}" stroke-width="6"/>' for x,y in pts)
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame(CLAIR,.9,W+40,-40,900)}{terrain("#fff",.5,3)}{g}</svg>'
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}svg{{display:block;position:absolute;left:0;top:0}}
</style></head><body><div id="b">{corps}{extra}</div><script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',K,OUT)

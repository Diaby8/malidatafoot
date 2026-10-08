"""Bannières X 1500 x 500 dans la DA MaliDataFoot : cinq propositions dessinées pour le format, à partir de nos vraies données.
1 carte des tirs (jaune) · 2 réseau de passes (nuit) · 3 trajectoire du but (vert) · 4 accroche (jaune, seule avec du texte) · 5 sobre (jaune).
Aplats et trame de points de la DA (gros points dans un coin, qui s'effacent) ; pas de grain, pas d'anneaux, pas de bande de motifs.   usage : python3 bannieres.py <1..5> <sortie.html>"""
import json, math, sys
from da import BASE_CSS
K,OUT=sys.argv[1],sys.argv[2]; V=json.load(open('vitrine.json',encoding='utf-8')); W,H=1500,500
OR,VERT,VERT_D,NUIT,ROUGE='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A'
def trame(coul, op, fx=W+40, fy=-40, portee=1150, pas=30):
    """La trame de points du style « vidéo » : grille en quinconce, points gros près d'un coin et de plus en plus petits."""
    g=''; rang=0; y=pas/2
    while y<H+pas:
        x=pas/2+(pas/2 if rang%2 else 0)
        while x<W+pas:
            d=math.hypot(x-fx,y-fy)/portee; r=1.2+9*max(0,1-d)**2.6
            g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=pas
        y+=pas; rang+=1
    return f'<g fill="{coul}" fill-opacity="{op}">{g}</g>'
def terrain_h(X0,Y0,s,coul,op,ep=3):
    """Terrain entier vu de dessus, à l'horizontale (le Mali attaque vers la droite). Repère StatsBomb 120 x 80."""
    L=f'stroke="{coul}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'; px=lambda x:X0+x*s; py=lambda y:Y0+y*s
    g=f'<rect x="{px(0)}" y="{py(0)}" width="{120*s}" height="{80*s}" {L}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {L}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*s}" {L}/>'
    for x0,sg in ((0,1),(120,-1)):
        g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*s}" height="{44*s}" {L}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*s}" height="{20*s}" {L}/>'
        a=math.acos(6/10); dy=10*math.sin(a)*s
        g+=f'<path d="M{px(x0+sg*18)} {py(40)-dy:.1f}A{10*s} {10*s} 0 0 {1 if sg>0 else 0} {px(x0+sg*18)} {py(40)+dy:.1f}" {L}/>'
    return g,px,py
if K=='1':      # ---- la carte des tirs : les 64 tirs du Mali à la CAN 2023, le but en haut, gros rond = grosse occasion
    bg=OR; s=13; X0=(W-80*s)/2; Y0=30; px=lambda y:X0+y*s; py=lambda x:Y0+(120-x)*s
    L='stroke="#fff" stroke-opacity=".75" stroke-width="3.5" fill="none"'
    g=f'<path d="M{px(0)} {H+10}V{py(120)}H{px(80)}V{H+10}" {L}/><rect x="{px(18)}" y="{py(120)}" width="{44*s}" height="{18*s}" {L}/><rect x="{px(30)}" y="{py(120)}" width="{20*s}" height="{6*s}" {L}/>'
    a=math.acos(6/10); dx=10*math.sin(a)*s
    g+=f'<path d="M{px(40)-dx:.1f} {py(102)}A{10*s} {10*s} 0 0 0 {px(40)+dx:.1f} {py(102)}" {L}/><rect x="{px(36)}" y="{py(120)-22}" width="{8*s}" height="22" stroke="#fff" stroke-opacity=".9" stroke-width="4" fill="none"/>'
    R=lambda v:max(8,math.sqrt(v)*42)
    for t in sorted(V['tirs'],key=lambda t:(t['is_goal'],-t['xg'])):
        x,y,r=px(t['y']),py(t['x']),R(t['xg'])
        g+=(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff" stroke="{VERT_D}" stroke-width="6"/>' if t['is_goal'] else
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{VERT}" fill-opacity=".5" stroke="{VERT_D}" stroke-opacity=".8" stroke-width="1.8"/>')
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame("#FDEBA6",.85)}{g}</svg>'
elif K=='2':    # ---- le réseau de passes du onze, comme une constellation sur le terrain
    bg=NUIT; s=5.9; X0=(W-120*s)/2; Y0=(H-80*s)/2; g,px,py=terrain_h(X0,Y0,s,OR,.34,2.5)
    R_=V['reseau_passes']; N={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]
    for e in E:
        a,b=N[e['a']],N[e['b']]; first=e is top
        g+=f'<line x1="{px(a["x"]):.1f}" y1="{py(a["y"]):.1f}" x2="{px(b["x"]):.1f}" y2="{py(b["y"]):.1f}" stroke="{"#fff" if first else OR}" stroke-opacity="{1 if first else min(.85,.18+e["n"]/34):.2f}" stroke-width="{1.2+e["n"]*.5:.1f}" stroke-linecap="round"/>'
    for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{9+math.sqrt(n["passes"])*2.3:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="4"/>'
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame("#0B7A3B",.6)}{g}</svg>'
elif K=='3':    # ---- la trajectoire d'un but : onze passes, du milieu jusqu'au fond des filets
    bg=VERT; s=5.9; X0=(W-120*s)/2; Y0=(H-80*s)/2; g,px,py=terrain_h(X0,Y0,s,'#fff',.45,2.5)
    for i in range(0,12,2): g=f'<rect x="{px(i*10)}" y="{py(0)}" width="{10*s}" height="{80*s}" fill="#fff" fill-opacity=".045"/>'+g
    seq=V['but']['seq']
    for e in seq:
        x1,y1,x2,y2=px(e['x']),py(e['y']),px(e['ex']),py(e['ey'])
        if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#fff" stroke-width="4" stroke-dasharray="1 9" stroke-linecap="round"/>'
        elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#fff" stroke-width="5" stroke-linecap="round"/>'
        else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROUGE}" stroke-width="8" stroke-linecap="round"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="15" fill="#fff" stroke="{ROUGE}" stroke-width="6"/>'
    for e in [e for e in seq if e['type']=='Pass']: g+=f'<circle cx="{px(e["x"]):.1f}" cy="{py(e["y"]):.1f}" r="9" fill="{OR}" stroke="{VERT_D}" stroke-width="3.5"/>'
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame("#19A552",.7)}{g}</svg>'
elif K=='4':    # ---- l'accroche de la vidéo, en grand : la seule proposition avec du texte
    bg=OR
    corps=(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">{trame("#FDEBA6",.9)}</svg>'
           f'<div style="position:absolute;left:432px;top:118px;font:italic 900 138px/.94 \'BC\';text-transform:uppercase;white-space:nowrap"><div style="color:{VERT_D}">Les Aigles jouent.</div><div style="color:{ROUGE}">La data parle.</div></div>')
else:           # ---- sobre : le terrain et les trois barres du logo, rien d'autre
    bg=OR; g,px,py=terrain_h((W-120*5.9)/2,(H-80*5.9)/2,5.9,'#fff',.7,3)
    bx=1164; g+=''.join(f'<rect x="{bx+i*98}" y="{410-h}" width="70" height="{h}" rx="8" fill="{c}"/>' for i,(h,c) in enumerate(((130,VERT),(215,'#fff'),(305,ROUGE))))
    corps=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{trame("#FDEBA6",.85)}{g}</svg>'
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}svg{{display:block}}
</style></head><body><div id="b">{corps}</div><script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',K,OUT)

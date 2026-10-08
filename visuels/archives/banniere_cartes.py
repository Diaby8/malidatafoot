"""Bannière X 1500 x 500, DA MaliDataFoot : jaune, lignes de terrain en fond, trame de points, quatre petites cartes penchées.
Même composition que la bannière « nouvelle DA », mais chaque carte est allégée : un titre, un dessin, un grand chiffre. Plus de
tableaux ni de petites lignes. Les cartes sont redessinées ici à partir des vraies données (rien n'est collé depuis un visuel).
usage : python3 banniere_cartes.py <sortie.html>"""
import json, math, sys
from da import BASE_CSS, photo
OUT=sys.argv[1]; W,H=1500,500; CW,CH=318,212
OR,VERT,VERT_D,NUIT,ROUGE='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A'
V=json.load(open('vitrine.json',encoding='utf-8'))
F=json.load(open('../../outputs/fiches/hamari-traore_poste.json',encoding='utf-8'))
D=json.load(open('../../outputs/duel_v2.json',encoding='utf-8'))

# ------------------------------------------------------------------ le fond : terrain + trame de points
L='stroke="#fff" stroke-opacity=".5" stroke-width="3" fill="none"'
terrain=(f'<rect x="-40" y="-60" width="{W+80}" height="{H+120}" {L}/><line x1="{W/2}" y1="-60" x2="{W/2}" y2="{H+60}" {L}/><circle cx="{W/2}" cy="{H/2}" r="120" {L}/><circle cx="{W/2}" cy="{H/2}" r="5" fill="#fff" fill-opacity=".5"/>'
         f'<rect x="-40" y="{H/2-235}" width="250" height="470" {L}/><rect x="-40" y="{H/2-105}" width="95" height="210" {L}/><path d="M210 {H/2-88}A120 120 0 0 1 210 {H/2+88}" {L}/>'
         f'<rect x="{W-210}" y="{H/2-235}" width="250" height="470" {L}/><rect x="{W-55}" y="{H/2-105}" width="95" height="210" {L}/><path d="M{W-210} {H/2-88}A120 120 0 0 0 {W-210} {H/2+88}" {L}/>')
def trame(coul, op, fx, fy, portee=1050, pas=30):
    """La trame du style « vidéo » : points en quinconce, gros près d'un coin, de plus en plus petits en s'éloignant."""
    g=''; rang=0; y=pas/2
    while y<H+pas:
        x=pas/2+(pas/2 if rang%2 else 0)
        while x<W+pas:
            d=math.hypot(x-fx,y-fy)/portee; r=1.2+9*max(0,1-d)**2.6
            g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=pas
        y+=pas; rang+=1
    return f'<g fill="{coul}" fill-opacity="{op}">{g}</g>'

# ------------------------------------------------------------------ petit terrain horizontal (repère StatsBomb 120 x 80)
def mini_terrain(X0,Y0,s,trait,op,fond=None,ep=1.3):
    Lm=f'stroke="{trait}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'; px=lambda x:X0+x*s; py=lambda y:Y0+y*s
    g=(f'<rect x="{px(0)}" y="{py(0)}" width="{120*s}" height="{80*s}" rx="3" fill="{fond}"/>' if fond else '')
    g+=f'<rect x="{px(0)}" y="{py(0)}" width="{120*s}" height="{80*s}" rx="3" {Lm}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {Lm}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*s}" {Lm}/>'
    for x0,sg in ((0,1),(120,-1)):
        g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*s}" height="{44*s}" {Lm}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*s}" height="{20*s}" {Lm}/>'
    return g,px,py
S=1.55; PW,PH=120*S,80*S     # terrain de 186 x 124 dans la carte

# ------------------------------------------------------------------ carte 1 : l'anatomie d'un but
B=V['but']; g,px,py=mini_terrain(0,0,S,VERT,.4,'#EEF4EF')
for e in B['seq']:
    x1,y1,x2,y2=px(e['x']),py(e['y']),px(e['ex']),py(e['ey'])
    if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="1.6" stroke-dasharray=".5 3.4" stroke-linecap="round"/>'
    elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="2" stroke-linecap="round"/>'
    else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROUGE}" stroke-width="3" stroke-linecap="round"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="5" fill="#fff" stroke="{ROUGE}" stroke-width="2.4"/>'
for e in [e for e in B['seq'] if e['type']=='Pass']: g+=f'<circle cx="{px(e["x"]):.1f}" cy="{py(e["y"]):.1f}" r="3.2" fill="{OR}" stroke="{VERT_D}" stroke-width="1.4"/>'
carte1=(f'<div class="tt">L\'anatomie d\'un but</div><div class="pan"><svg class="dessin" width="{PW}" height="{PH}" viewBox="-1 -1 {PW+2} {PH+2}">{g}</svg>'
        f'<div class="ch"><b>{B["passes"]}</b><span>passes<br>de suite</span></div></div>')

# ------------------------------------------------------------------ carte 2 : la fiche d'un joueur (radar seul)
CR=F['criteres']; N=len(CR); cx,cy,R=PW/2,PH/2,60; ang=lambda i:-math.pi/2+i*2*math.pi/N; pol=lambda r,i:(cx+r*math.cos(ang(i)),cy+r*math.sin(ang(i)))
g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R*v/100:.1f}" fill="none" stroke="#DCE4DD" stroke-width="1.1"/>' for v in (25,50,75,100))
for i in range(N): x,y=pol(R,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#DCE4DD" stroke-width="1"/>'
pts=[pol(R*max(c['centile'],2)/100,i) for i,c in enumerate(CR)]
g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{VERT}" fill-opacity=".22" stroke="{VERT}" stroke-width="2.2" stroke-linejoin="round"/>'
g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#fff" stroke="{VERT}" stroke-width="1.8"/>' for x,y in pts)
nom=F['player'].split(' '); carte2=(f'<div class="tt avec"><i class="ph">{photo(F["player_id"])}</i>{F["player"]}</div><div class="pan"><svg class="dessin" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}">{g}</svg>'
        f'<div class="ch"><b>{F["note"]:.0f}</b><span>note du tournoi,<br>sur 100</span></div></div>')

# ------------------------------------------------------------------ carte 3 : le réseau de passes
R_=V['reseau_passes']; ND={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]
g,px,py=mini_terrain(0,0,S,OR,.3,'rgba(255,255,255,.045)')
for e in E:
    a,b=ND[e['a']],ND[e['b']]; first=e is top
    g+=f'<line x1="{px(a["x"]):.1f}" y1="{py(a["y"]):.1f}" x2="{px(b["x"]):.1f}" y2="{py(b["y"]):.1f}" stroke="{"#fff" if first else OR}" stroke-opacity="{1 if first else min(.8,.16+e["n"]/36):.2f}" stroke-width="{.5+e["n"]*.13:.2f}" stroke-linecap="round"/>'
for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{2.6+math.sqrt(n["passes"])*.62:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="1.3"/>'
court=lambda n:n.split(' ')[-1]; duo=f'{court(ND[top["a"]].get("name") or ND[top["a"]].get("player"))} et {court(ND[top["b"]].get("name") or ND[top["b"]].get("player"))}'
carte3=(f'<div class="tt">Le réseau de passes</div><div class="pan"><svg class="dessin" width="{PW}" height="{PH}" viewBox="-1 -1 {PW+2} {PH+2}">{g}</svg>'
        f'<div class="ch"><b>{top["n"]}</b><span>passes entre<br>{duo}</span></div></div>')

# ------------------------------------------------------------------ carte 4 : le duel (barres face à face, sans chiffres)
(nA,JA),(nB,JB)=list(D['j'].items()); CLES=['shots_p90','npxg_p90','key_passes_p90','receptions_in_box_p90','prog_carries_p90','pressures_p90']
AX,DEMI,PASB=CW/2,62,17.5; y0=12; g=''
for i,k in enumerate(CLES):
    y=y0+i*PASB; m=max(JA[k],JB[k]); la,lb=DEMI*JA[k]/m,DEMI*JB[k]/m
    g+=(f'<line x1="{AX-5-DEMI}" y1="{y}" x2="{AX-5}" y2="{y}" stroke="#fff" stroke-opacity=".12" stroke-width="5" stroke-linecap="round"/><line x1="{AX+5}" y1="{y}" x2="{AX+5+DEMI}" y2="{y}" stroke="#fff" stroke-opacity=".12" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="{AX-5-la:.1f}" y1="{y}" x2="{AX-5}" y2="{y}" stroke="{OR}" stroke-width="5" stroke-linecap="round"/><line x1="{AX+5}" y1="{y}" x2="{AX+5+lb:.1f}" y2="{y}" stroke="#fff" stroke-width="5" stroke-linecap="round"/>')
but=lambda n:'but' if n<2 else 'buts'
carte4=(f'<div class="duo"><div class="tt avec"><i class="ph" style="box-shadow:0 0 0 2px {OR}">{photo(int(JA["player_id"]))}</i>{court(nA)}</div><div class="tt avec dr">{court(nB)}<i class="ph" style="box-shadow:0 0 0 2px #fff">{photo(int(JB["player_id"]))}</i></div></div>'
        f'<div class="pan"><svg width="{CW}" height="{PH}" viewBox="0 0 {CW} {PH}" style="position:absolute;left:0;top:10px">{g}</svg>'
        f'<div class="ch g"><b style="color:{OR}">{JA["goals"]:.0f}</b><span>{but(JA["goals"])}</span></div><div class="ch d"><b>{JB["goals"]:.0f}</b><span>{but(JB["goals"])}</span></div></div>')

POS=[(57,62,-2.2,'A',carte1),(413,48,1.6,'A',carte2),(769,64,-1.4,'B',carte3),(1125,50,2.4,'B d4',carte4)]
cartes=''.join(f'<div class="c {cl}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{h}</div>' for x,y,r,cl,h in POS)
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{OR};font-family:"IN",sans-serif}}svg{{display:block}}
.c{{position:absolute;width:{CW}px;height:{CH}px;border-radius:7px;overflow:hidden;box-shadow:0 0 0 4px #fff,0 14px 26px rgba(80,50,0,.3)}}
.c.A{{background:{OR};color:{VERT_D}}}.c.B{{background:{NUIT};color:#fff}}
.tt{{position:absolute;left:15px;top:14px;height:34px;display:flex;align-items:center;gap:9px;font:italic 900 31px/1 "BC";text-transform:uppercase;white-space:nowrap;letter-spacing:.005em}}
.tt.avec{{top:10px}}.ph{{width:34px;height:34px;border-radius:50%;overflow:hidden;background:#fff;flex:none;display:block}}.ph img,.ph svg{{width:100%;height:100%;object-fit:cover;display:block}}
.duo .tt{{font-size:25px}}.duo .tt.dr{{left:auto;right:15px}}
.pan{{position:absolute;left:10px;right:10px;top:54px;bottom:10px;border-radius:6px}}.c.A .pan{{background:#fff}}
.dessin{{position:absolute;left:11px;top:12px}}
.ch{{position:absolute;left:{11+PW+12}px;right:6px;top:22px}}.ch b{{display:block;font:italic 900 66px/.86 "BC"}}.ch span{{display:block;margin-top:7px;font:600 10.5px/1.25 "IN";opacity:.72}}
.c.B .ch b{{color:{OR}}}.c.B .ch span{{opacity:.8}}
.d4 .pan{{left:0;right:0}}.d4 .ch{{top:26px;width:60px;text-align:center}}.d4 .ch.g{{left:14px;right:auto}}.d4 .ch.d{{left:auto;right:14px}}.d4 .ch.d b{{color:#fff}}.d4 .ch span{{font-size:11px;margin-top:6px}}
</style></head><body><div id="b"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">{trame("#FDEBA6",.9,W+40,H+40)}{terrain}</svg>{cartes}</div>
<script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',OUT,'| but',B['passes'],'passes | note',F['note'],'| duo',duo,top['n'],'| buts',JA['goals'],JB['goals'])

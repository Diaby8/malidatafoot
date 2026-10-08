"""Bannière X 1500 x 500 : la composition de la toute première (terrain derrière, trame de points en haut à droite, quatre cartes
penchées aux mêmes places), mais dans la DA actuelle et sans aucun nom de joueur.
DA : jaune uni #F6C41C (plus de dégradé ni de grain), titres Barlow Condensed penché, texte Inter, cartes « cadre blanc » et « nuit ».
Chaque carte = le titre d'un format de la page + son dessin. Ni nom, ni chiffre, ni match ; les formes viennent de vraies données.
usage : python3 banniere_da_legere.py <sortie.html>"""
import json, math, sys
from da import BASE_CSS, SILHOUETTE
OUT=sys.argv[1]; W,H=1500,500; CW,CH=336,226
OR,VERT,VERT_D,NUIT,ROUGE='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A'
V=json.load(open('vitrine.json',encoding='utf-8'))
F=json.load(open('../../outputs/fiches/hamari-traore_poste.json',encoding='utf-8'))
D=json.load(open('../../outputs/duel_v2.json',encoding='utf-8'))

# ------------------------------------------------------------------ le fond : même terrain et même trame que la première bannière, en jaune uni
pts=''; st=26; row=0; y=st/2
while y<H:
    x=st/2+(st/2 if row%2 else 0)
    while x<W:
        dd=math.hypot(x-W,y)/1150; r=1.1+8.5*max(0,1-dd)**2.6; pts+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=st
    y+=st; row+=1
fond=(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><g fill="#FDEBA6" fill-opacity=".85">{pts}</g></svg>'
      '<svg id="pt" viewBox="0 0 120 80"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/><rect x="0" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="102" y="18" width="18" height="44"/><rect x="114" y="30" width="6" height="20"/><path d="M18 32A10 10 0 0 1 18 48"/><path d="M102 32A10 10 0 0 0 102 48"/></svg>')

# ------------------------------------------------------------------ le cadre de dessin des cartes : 316 x 166 sous le titre
BW,BH=CW-20,CH-50-10; svg=lambda g:f'<svg width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}">{g}</svg>'
S=(BH-10)/80; TX,TY=(BW-120*S)/2,5; px=lambda x:TX+x*S; py=lambda y:TY+y*S
def terrain(trait,op,fond_):
    Lm=f'stroke="{trait}" stroke-opacity="{op}" stroke-width="1.4" fill="none"'
    g=f'<rect x="{px(0)}" y="{py(0)}" width="{120*S}" height="{80*S}" rx="3" fill="{fond_}"/><rect x="{px(0)}" y="{py(0)}" width="{120*S}" height="{80*S}" rx="3" {Lm}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {Lm}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*S}" {Lm}/>'
    for x0,sg in ((0,1),(120,-1)): g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*S}" height="{44*S}" {Lm}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*S}" height="{20*S}" {Lm}/>'
    return g

# 1. l'anatomie d'un but : le tracé seul
g=terrain(VERT,.42,'#EEF4EF')
for e in V['but']['seq']:
    x1,y1,x2,y2=px(e['x']),py(e['y']),px(e['ex']),py(e['ey'])
    if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="1.8" stroke-dasharray=".5 3.8" stroke-linecap="round"/>'
    elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="2.4" stroke-linecap="round"/>'
    else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROUGE}" stroke-width="3.6" stroke-linecap="round"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="5.4" fill="#fff" stroke="{ROUGE}" stroke-width="2.6"/>'
for e in [e for e in V['but']['seq'] if e['type']=='Pass']: g+=f'<circle cx="{px(e["x"]):.1f}" cy="{py(e["y"]):.1f}" r="3.7" fill="{OR}" stroke="{VERT_D}" stroke-width="1.6"/>'
c1=svg(g)

# 2. le profil d'un joueur : un radar et six barres, sans nom ni note
CR=F['criteres']; N=len(CR); R0=BH/2-9; cx,cy=R0+24,BH/2; ang=lambda i:-math.pi/2+i*2*math.pi/N; pol=lambda r,i:(cx+r*math.cos(ang(i)),cy+r*math.sin(ang(i)))
g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R0*v/100:.1f}" fill="none" stroke="#DCE4DD" stroke-width="1.2"/>' for v in (25,50,75,100))
for i in range(N): x,y=pol(R0,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#DCE4DD" stroke-width="1"/>'
P=[pol(R0*max(c['centile'],4)/100,i) for i,c in enumerate(CR)]
g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in P)+f'" fill="{VERT}" fill-opacity=".22" stroke="{VERT}" stroke-width="2.6" stroke-linejoin="round"/>'
g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#fff" stroke="{VERT}" stroke-width="2"/>' for x,y in P)
niv=lambda p:(VERT if p>=75 else ('#E3A600' if p>=25 else ROUGE)); bx0=cx+R0+34; bl=BW-18-bx0; nb=6; pas=(BH-44)/(nb-1); TRI=sorted(CR,key=lambda c:-c['centile'])
for i,c in enumerate([TRI[j] for j in (0,2,4,6,8,9)]):
    y=22+i*pas; g+=(f'<line x1="{bx0}" y1="{y:.1f}" x2="{bx0+bl}" y2="{y:.1f}" stroke="#E9EEE9" stroke-width="8" stroke-linecap="round"/>'
                    f'<line x1="{bx0}" y1="{y:.1f}" x2="{bx0+bl*max(c["centile"],4)/100:.1f}" y2="{y:.1f}" stroke="{niv(c["centile"])}" stroke-width="8" stroke-linecap="round"/>')
c2=svg(g)

# 3. le réseau de passes : onze ronds et leurs liens, sans les noms
R_=V['reseau_passes']; ND={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]; k=S/1.55; g=terrain(OR,.3,'rgba(255,255,255,.045)')
for e in E:
    a,b=ND[e['a']],ND[e['b']]; first=e is top
    g+=f'<line x1="{px(a["x"]):.1f}" y1="{py(a["y"]):.1f}" x2="{px(b["x"]):.1f}" y2="{py(b["y"]):.1f}" stroke="{"#fff" if first else OR}" stroke-opacity="{1 if first else min(.8,.16+e["n"]/36):.2f}" stroke-width="{(.5+e["n"]*.13)*k:.2f}" stroke-linecap="round"/>'
for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{(2.6+math.sqrt(n["passes"])*.62)*k:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="{1.3*k:.1f}"/>'
c3=svg(g)

# 4. le duel : deux silhouettes neutres et des barres face à face, jaune contre blanc
(nA,JA),(nB,JB)=list(D['j'].items()); CLES=['shots_p90','npxg_p90','key_passes_p90','receptions_in_box_p90','prog_carries_p90','pressures_p90']
AX,DEMI=BW/2,74; pas=(BH-44)/(len(CLES)-1); g=''
for i,kk in enumerate(CLES):
    y=22+i*pas; m=max(JA[kk],JB[kk]); la,lb=DEMI*JA[kk]/m,DEMI*JB[kk]/m
    g+=(f'<line x1="{AX-6-DEMI}" y1="{y:.1f}" x2="{AX-6}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".13" stroke-width="8" stroke-linecap="round"/><line x1="{AX+6}" y1="{y:.1f}" x2="{AX+6+DEMI}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".13" stroke-width="8" stroke-linecap="round"/>'
        f'<line x1="{AX-6-la:.1f}" y1="{y:.1f}" x2="{AX-6}" y2="{y:.1f}" stroke="{OR}" stroke-width="8" stroke-linecap="round"/><line x1="{AX+6}" y1="{y:.1f}" x2="{AX+6+lb:.1f}" y2="{y:.1f}" stroke="#fff" stroke-width="8" stroke-linecap="round"/>')
sil=lambda coul:SILHOUETTE.replace('#E9EDE8','#0E4A2A').replace('#A9B5AC',coul)
c4=svg(g)+f'<i class="si" style="left:8px;box-shadow:0 0 0 3px {OR}">{sil(OR)}</i><i class="si" style="right:8px;box-shadow:0 0 0 3px #fff">{sil("#fff")}</i>'

CARTES=[(52,56,-2,'A',"L'anatomie d'un but",c1),(406,82,1.5,'A',"Le profil d'un joueur",c2),(760,52,-1.5,'B','Le réseau de passes',c3),(1114,80,2,'B','Le duel',c4)]
cartes=''.join(f'<div class="c {cl}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"><div class="tt">{t}</div><div class="pan">{v}</div></div>' for x,y,r,cl,t,v in CARTES)
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{OR}}}svg{{display:block}}
#pt{{position:absolute;left:0;top:-250px;width:1500px;height:1000px}}#pt *{{fill:none;stroke:#FFF6D0;stroke-width:.34;stroke-opacity:.8}}
.c{{position:absolute;width:{CW}px;height:{CH}px;border-radius:8px;overflow:hidden;box-shadow:0 0 0 5px #fff,0 22px 40px rgba(70,40,0,.34)}}
.c.A{{background:{OR};color:{VERT_D}}}.c.B{{background:{NUIT};color:#fff}}
.tt{{position:absolute;left:15px;top:12px;font:italic 900 32px/1 "BC";text-transform:uppercase;white-space:nowrap;letter-spacing:.005em}}
.pan{{position:absolute;left:10px;top:50px;width:{BW}px;height:{BH}px;border-radius:6px;overflow:hidden}}.c.A .pan{{background:#fff}}
.si{{position:absolute;top:50%;width:46px;height:46px;margin-top:-23px;border-radius:50%;overflow:hidden;display:block}}.si svg{{width:100%;height:100%}}
</style></head><body><div id="b">{fond}{cartes}</div><script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',OUT)

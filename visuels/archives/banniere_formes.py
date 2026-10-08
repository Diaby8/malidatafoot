"""Bannière X 1500 x 500, DA MaliDataFoot : jaune, lignes de terrain, trame de points, quatre cartes penchées.
Les cartes montrent des TYPES de visualisation (carte de tirs, profil de joueur, réseau de passes, fil d'un match), pas un contenu :
aucun nom, aucun chiffre, aucun match. Les formes sont tracées à partir de vraies données pour rester naturelles, mais plus rien n'est à lire.
usage : python3 banniere_formes.py <sortie.html> [mots|sans]      mots = un mot en titre sur chaque carte ; sans = aucun texte"""
import json, math, sys
from da import BASE_CSS
OUT=sys.argv[1]; MOTS=(sys.argv[2] if len(sys.argv)>2 else 'mots')=='mots'
W,H=1500,500; CW,CH=318,212; BX,BW=10,298; BY,BH=(52,150) if MOTS else (10,192)
OR,VERT,VERT_D,NUIT,ROUGE='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A'
V=json.load(open('vitrine.json',encoding='utf-8'))
F=json.load(open('../../outputs/fiches/hamari-traore_poste.json',encoding='utf-8'))

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
svg=lambda g:f'<svg class="viz" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}">{g}</svg>'

# ------------------------------------------------------------------ 1. carte de tirs : la surface vue de dessus, le but en haut
s=BW/60; px=lambda y:(y-10)*s; py=lambda x:7+(120-x)*s; Lt=f'stroke="{VERT}" stroke-opacity=".38" stroke-width="1.6" fill="none"'
a=math.acos(6/10); dx=10*math.sin(a)*s
g=(f'<rect x="{px(18)}" y="{py(120)}" width="{44*s}" height="{18*s}" {Lt}/><rect x="{px(30)}" y="{py(120)}" width="{20*s}" height="{6*s}" {Lt}/>'
   f'<path d="M{px(40)-dx:.1f} {py(102)}A{10*s} {10*s} 0 0 0 {px(40)+dx:.1f} {py(102)}" {Lt}/><line x1="0" y1="{py(120)}" x2="{BW}" y2="{py(120)}" {Lt}/>'
   f'<line x1="{px(36)}" y1="{py(120)}" x2="{px(44)}" y2="{py(120)}" stroke="{VERT_D}" stroke-width="4" stroke-linecap="round"/>')
R=lambda v:max(3.2,math.sqrt(v)*18)
for t in sorted(V['tirs'],key=lambda t:(t['is_goal'],-t['xg'])):
    x,y,r=px(t['y']),py(t['x']),R(t['xg'])
    g+=(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+.6:.1f}" fill="{OR}" stroke="{VERT_D}" stroke-width="2.4"/>' if t['is_goal'] else
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{VERT}" fill-opacity=".42" stroke="{VERT_D}" stroke-opacity=".75" stroke-width="1"/>')
viz1=svg(g)

# ------------------------------------------------------------------ 2. profil de joueur : un radar et quelques barres
CR=F['criteres']; N=len(CR); R0=BH/2-5; cx,cy=R0+8,BH/2; ang=lambda i:-math.pi/2+i*2*math.pi/N; pol=lambda r,i:(cx+r*math.cos(ang(i)),cy+r*math.sin(ang(i)))
g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R0*v/100:.1f}" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="1.2"/>' for v in (25,50,75,100))
for i in range(N): x,y=pol(R0,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".22" stroke-width="1"/>'
pts=[pol(R0*max(c['centile'],4)/100,i) for i,c in enumerate(CR)]
g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{OR}" fill-opacity=".4" stroke="{OR}" stroke-width="2.6" stroke-linejoin="round"/>'
g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.3" fill="#fff" stroke="{VERT}" stroke-width="1.4"/>' for x,y in pts)
bx0=cx+R0+26; bl=BW-8-bx0; nb=6; pas=(BH-24)/(nb-1)
TRI=sorted(CR,key=lambda c:-c['centile'])
for i,c in enumerate([TRI[j] for j in (0,2,4,6,8,9)]):
    y=12+i*pas; g+=(f'<line x1="{bx0}" y1="{y:.1f}" x2="{bx0+bl}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".2" stroke-width="7" stroke-linecap="round"/>'
                    f'<line x1="{bx0}" y1="{y:.1f}" x2="{bx0+bl*max(c["centile"],4)/100:.1f}" y2="{y:.1f}" stroke="#fff" stroke-width="7" stroke-linecap="round"/>')
viz2=svg(g)

# ------------------------------------------------------------------ 3. réseau de passes : onze joueurs, des traits plus ou moins épais
s=min(BW/120,BH/80); X0,Y0=(BW-120*s)/2,(BH-80*s)/2; px=lambda x:X0+x*s; py=lambda y:Y0+y*s; Lr=f'stroke="{OR}" stroke-opacity=".3" stroke-width="1.3" fill="none"'
g=f'<rect x="{px(0)}" y="{py(0)}" width="{120*s}" height="{80*s}" rx="3" fill="#fff" fill-opacity=".045"/><rect x="{px(0)+.7}" y="{py(0)+.7}" width="{120*s-1.4}" height="{80*s-1.4}" rx="3" {Lr}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {Lr}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*s}" {Lr}/>'
for x0,sg in ((0,1),(120,-1)): g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*s}" height="{44*s}" {Lr}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*s}" height="{20*s}" {Lr}/>'
R_=V['reseau_passes']; ND={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]; k=s/1.55
for e in E:
    a_,b_=ND[e['a']],ND[e['b']]; first=e is top
    g+=f'<line x1="{px(a_["x"]):.1f}" y1="{py(a_["y"]):.1f}" x2="{px(b_["x"]):.1f}" y2="{py(b_["y"]):.1f}" stroke="{"#fff" if first else OR}" stroke-opacity="{1 if first else min(.8,.16+e["n"]/36):.2f}" stroke-width="{(.5+e["n"]*.13)*k:.2f}" stroke-linecap="round"/>'
for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{(2.6+math.sqrt(n["passes"])*.62)*k:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="{1.3*k:.1f}"/>'
viz3=svg(g)

# ------------------------------------------------------------------ 4. fil d'un match : deux courbes qui montent à chaque occasion
C=V['xg_chrono']; fin=max(V['periodes_fin']); cum={'equipe':[(0,0)],'adversaire':[(0,0)]}; buts=[]
for t in C:
    c=cum[t['camp']]; v=c[-1][1]+t['xg']; c.append((t['minute_ecoulee'],v))
    if t['is_goal']: buts.append((t['camp'],t['minute_ecoulee'],v))
vmax=max(c[-1][1] for c in cum.values()); mg,mh,mb=12,16,14; fx=lambda m:mg+m/fin*(BW-2*mg); fy=lambda v:BH-mb-v/vmax*(BH-mb-mh)
def marches(c):
    d=f'M{fx(0):.1f} {fy(0):.1f}';
    for m,v in c[1:]: d+=f'H{fx(m):.1f}V{fy(v):.1f}'
    return d+f'H{fx(fin):.1f}'
g=''.join(f'<line x1="{fx(m):.1f}" y1="{mh-6}" x2="{fx(m):.1f}" y2="{BH-mb}" stroke="{VERT_D}" stroke-opacity=".22" stroke-width="1.2" stroke-dasharray="2 5"/>' for m in V['periodes_fin'][:-1])
g+=f'<line x1="{mg}" y1="{BH-mb}" x2="{BW-mg}" y2="{BH-mb}" stroke="{VERT_D}" stroke-opacity=".35" stroke-width="1.5"/>'
g+=f'<path d="{marches(cum["equipe"])}V{fy(0):.1f}Z" fill="{VERT}" fill-opacity=".16"/>'
g+=f'<path d="{marches(cum["adversaire"])}" fill="none" stroke="{ROUGE}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>'
g+=f'<path d="{marches(cum["equipe"])}" fill="none" stroke="{VERT}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>'
for camp,m,v in buts: g+=f'<circle cx="{fx(m):.1f}" cy="{fy(v):.1f}" r="5.2" fill="#fff" stroke="{VERT if camp=="equipe" else ROUGE}" stroke-width="2.8"/>'
viz4=svg(g)

CARTES=[(57,62,-2.2,'A','Tirs',viz1),(413,48,1.6,'V','Joueurs',viz2),(769,64,-1.4,'B','Passes',viz3),(1125,50,2.4,'A','Matchs',viz4)]
cartes=''.join(f'<div class="c {cl}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{f"<div class=tt>{mot}</div>" if MOTS else ""}<div class="pan">{v}</div></div>' for x,y,r,cl,mot,v in CARTES)
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{OR}}}svg{{display:block}}
.c{{position:absolute;width:{CW}px;height:{CH}px;border-radius:7px;overflow:hidden;box-shadow:0 0 0 4px #fff,0 14px 26px rgba(80,50,0,.3)}}
.c.A{{background:{OR};color:{VERT_D}}}.c.B{{background:{NUIT};color:#fff}}.c.V{{background:{VERT};color:#fff}}
.tt{{position:absolute;left:15px;top:11px;font:italic 900 34px/1 "BC";text-transform:uppercase;white-space:nowrap;letter-spacing:.01em}}
.pan{{position:absolute;left:{BX}px;top:{BY}px;width:{BW}px;height:{BH}px;border-radius:6px;overflow:hidden}}.c.A .pan{{background:#fff}}
</style></head><body><div id="b"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">{trame("#FDEBA6",.9,W+40,H+40)}{terrain}</svg>{cartes}</div>
<script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',OUT,'mots' if MOTS else 'sans texte','| buts',buts)

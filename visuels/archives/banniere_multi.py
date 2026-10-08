"""Fabrique de bannières X 1500 x 500 dans la DA MaliDataFoot : des cartes de dataviz posées sur le terrain, en beaucoup de variantes.
Aucun nom de joueur. Les formes sont tracées à partir de vraies données (CAN 2023, StatsBomb Open Data).
usage : python3 banniere_multi.py <sortie.html> <types séparés par des virgules> [options séparées par des points-virgules]
types   : but · roue · reseau · duel · tirs · radar · courbes · chaleur · nuage · barres
options : mise=rang|eventail|bande|droite   (rang : 3, 4 ou 5 cartes penchées ; eventail : 5 cartes qui se chevauchent ;
                                             bande : 6 tuiles droites ; droite : l'accroche + 2 cartes à droite)
          fond=jaune|degrade|nuit|vert      titres=1 (le nom du format sur chaque carte)"""
import json, math, sys
from da import BASE_CSS, SILHOUETTE
OUT=sys.argv[1]; TYPES=sys.argv[2].split(','); NB=len(TYPES); O=dict(o.split('=') for o in (sys.argv[3].split(';') if len(sys.argv)>3 and sys.argv[3] else []))
MISE,FOND,TITRES=O.get('mise','rang'),O.get('fond','jaune'),O.get('titres','0')=='1'
W,H=1500,500; OR,VERT,VERT_D,NUIT,ROUGE,MOY='#F6C41C','#0B7A3B','#064A25','#04331A','#D4252A','#E3A600'
V=json.load(open('vitrine.json',encoding='utf-8')); Z=json.load(open('banniere_viz.json',encoding='utf-8'))
F=json.load(open('../../outputs/fiches/hamari-traore_poste.json',encoding='utf-8')); D=json.load(open('../../outputs/duel_v2.json',encoding='utf-8'))

# ------------------------------------------------------------------ la mise en place : taille des cartes, positions, inclinaisons
if MISE=='eventail': CW,CH=350,236; POS=[(31+i*272,(40,58,68,58,40)[i],(-6,-3,0,3,6)[i]) for i in range(NB)]
elif MISE=='bande': CW,CH=222,150; POS=[(49+i*236,76,0) for i in range(NB)]
elif MISE=='droite': CW,CH=270,184; POS=[(1075,52,-3),(1195,250,2.5)]
elif NB==3: CW,CH=380,256; POS=[(120+i*440,(24,58,30)[i],(-2,1.6,-1.6)[i]) for i in range(3)]
elif NB==4: CW,CH=336,226; POS=[(51+i*354,(56,82,52,80)[i],(-2,1.5,-1.5,2)[i]) for i in range(4)]
else: CW,CH=276,190; POS=[(32+i*290,(60,86,54,84,62)[i],(-2,1.6,-1.4,2,-1.6)[i]) for i in range(NB)]
M=10; TT=round(CW*.149) if TITRES else M; BW,BH=CW-2*M,CH-TT-M; TF=round(CW*.095)

# ------------------------------------------------------------------ le fond : le terrain et la trame de la première bannière
FD=dict(jaune=(OR,'#FDEBA6',.85,'#FFF6D0',.8),degrade=('linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)','#FDEBA6',.85,'#FFF6D0',.8),
        nuit=(NUIT,VERT,.6,VERT,.75),vert=(VERT,'#19A552',.75,'#fff',.38))[FOND]
pts=''; st=26; row=0; y=st/2
while y<H:
    x=st/2+(st/2 if row%2 else 0)
    while x<W:
        dd=math.hypot(x-W,y)/1150; r=1.1+8.5*max(0,1-dd)**2.6; pts+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=st
    y+=st; row+=1
fond=(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><g fill="{FD[1]}" fill-opacity="{FD[2]}">{pts}</g></svg>'
      '<svg id="pt" viewBox="0 0 120 80"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/><rect x="0" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="102" y="18" width="18" height="44"/><rect x="114" y="30" width="6" height="20"/><path d="M18 32A10 10 0 0 1 18 48"/><path d="M102 32A10 10 0 0 0 102 48"/></svg>')

# ------------------------------------------------------------------ les dessins : chacun rend (thème de la carte, svg) dans un cadre BW x BH
S=min(BW/120,BH/80); TX,TY=(BW-120*S)/2,(BH-80*S)/2; px=lambda x:TX+x*S; py=lambda y:TY+y*S; k=S/1.55
def lignes(trait,op,ep=1.4):
    Lm=f'stroke="{trait}" stroke-opacity="{op}" stroke-width="{ep}" fill="none"'
    g=f'<rect x="{px(0)+ep/2}" y="{py(0)+ep/2}" width="{120*S-ep}" height="{80*S-ep}" rx="3" {Lm}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {Lm}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*S}" {Lm}/>'
    for x0,sg in ((0,1),(120,-1)): g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*S}" height="{44*S}" {Lm}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*S}" height="{20*S}" {Lm}/>'
    return g
def but():
    g=f'<rect x="{px(0)}" y="{py(0)}" width="{120*S}" height="{80*S}" rx="3" fill="#EEF4EF"/>'+lignes(VERT,.42)
    for e in V['but']['seq']:
        x1,y1,x2,y2=px(e['x']),py(e['y']),px(e['ex']),py(e['ey'])
        if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="{1.4*k:.1f}" stroke-dasharray="{.4*k:.1f} {3*k:.1f}" stroke-linecap="round"/>'
        elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VERT}" stroke-width="{1.9*k:.1f}" stroke-linecap="round"/>'
        else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROUGE}" stroke-width="{2.8*k:.1f}" stroke-linecap="round"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="{4.2*k:.1f}" fill="#fff" stroke="{ROUGE}" stroke-width="{2*k:.1f}"/>'
    for e in [e for e in V['but']['seq'] if e['type']=='Pass']: g+=f'<circle cx="{px(e["x"]):.1f}" cy="{py(e["y"]):.1f}" r="{2.9*k:.1f}" fill="{OR}" stroke="{VERT_D}" stroke-width="{1.25*k:.1f}"/>'
    return 'A',g,"L'anatomie d'un but"
def roue():
    CR=F['criteres']; N=len(CR); R1,R0=BH/2-4,BH*.09; cx,cy=BW/2,BH/2; pas=360/N; niv=lambda p:(VERT if p>=75 else (MOY if p>=25 else ROUGE)); g=''
    for i,c in enumerate(CR):
        a0,a1=math.radians(i*pas+1.8-90),math.radians((i+1)*pas-1.8-90); P=lambda rr,a:f'{cx+rr*math.cos(a):.1f} {cy+rr*math.sin(a):.1f}'
        part=lambda r:f'M{P(R0,a0)}L{P(r,a0)}A{r:.1f} {r:.1f} 0 0 1 {P(r,a1)}L{P(R0,a1)}A{R0:.1f} {R0:.1f} 0 0 0 {P(R0,a0)}Z'
        g+=f'<path d="{part(R1)}" fill="#EEF1EE"/><path d="{part(R0+(R1-R0)*max(c["centile"],8)/100)}" fill="{niv(c["centile"])}"/>'
    return 'A',g,'Le profil'
def reseau():
    R_=V['reseau_passes']; ND={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]
    g=f'<rect x="{px(0)}" y="{py(0)}" width="{120*S}" height="{80*S}" rx="3" fill="#fff" fill-opacity=".045"/>'+lignes(OR,.3)
    for e in E:
        a,b=ND[e['a']],ND[e['b']]; first=e is top
        g+=f'<line x1="{px(a["x"]):.1f}" y1="{py(a["y"]):.1f}" x2="{px(b["x"]):.1f}" y2="{py(b["y"]):.1f}" stroke="{"#fff" if first else OR}" stroke-opacity="{1 if first else min(.8,.16+e["n"]/36):.2f}" stroke-width="{(.5+e["n"]*.13)*k:.2f}" stroke-linecap="round"/>'
    for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{(2.6+math.sqrt(n["passes"])*.62)*k:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="{1.3*k:.1f}"/>'
    return 'B',g,'Le réseau de passes'
def duel():
    (nA,JA),(nB,JB)=list(D['j'].items()); CL=['shots_p90','npxg_p90','key_passes_p90','receptions_in_box_p90','prog_carries_p90','pressures_p90']
    AX,DEMI=BW/2,BW*.235; pas=(BH-BH*.27)/(len(CL)-1); e=BH*.05; g=''
    for i,kk in enumerate(CL):
        y=BH*.135+i*pas; m=max(JA[kk],JB[kk]); la,lb=DEMI*JA[kk]/m,DEMI*JB[kk]/m
        g+=(f'<line x1="{AX-6-DEMI:.1f}" y1="{y:.1f}" x2="{AX-6}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".13" stroke-width="{e:.1f}" stroke-linecap="round"/><line x1="{AX+6}" y1="{y:.1f}" x2="{AX+6+DEMI:.1f}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".13" stroke-width="{e:.1f}" stroke-linecap="round"/>'
            f'<line x1="{AX-6-la:.1f}" y1="{y:.1f}" x2="{AX-6}" y2="{y:.1f}" stroke="{OR}" stroke-width="{e:.1f}" stroke-linecap="round"/><line x1="{AX+6}" y1="{y:.1f}" x2="{AX+6+lb:.1f}" y2="{y:.1f}" stroke="#fff" stroke-width="{e:.1f}" stroke-linecap="round"/>')
    d=BW*.145
    for xs,coul in ((BW*.03,OR),(BW*.97-d,'#fff')):
        g+=(f'<g transform="translate({xs:.1f} {BH/2-d/2:.1f}) scale({d/100:.4f})"><circle cx="50" cy="50" r="50" fill="#0E4A2A"/><circle cx="50" cy="39" r="17" fill="{coul}"/><path d="M19 91C22 73 34 65 50 65C66 65 78 73 81 91A50 50 0 0 1 19 91Z" fill="{coul}"/>'
            f'<circle cx="50" cy="50" r="48" fill="none" stroke="{coul}" stroke-width="6"/></g>')
    return 'B',g,'Le duel'
def tirs():
    s=BW/60; qx=lambda y:(y-10)*s; qy=lambda x:7+(120-x)*s; Lt=f'stroke="{VERT}" stroke-opacity=".38" stroke-width="1.5" fill="none"'; a=math.acos(6/10); dx=10*math.sin(a)*s
    g=(f'<rect x="{qx(18)}" y="{qy(120)}" width="{44*s}" height="{18*s}" {Lt}/><rect x="{qx(30)}" y="{qy(120)}" width="{20*s}" height="{6*s}" {Lt}/><path d="M{qx(40)-dx:.1f} {qy(102)}A{10*s} {10*s} 0 0 0 {qx(40)+dx:.1f} {qy(102)}" {Lt}/>'
       f'<line x1="0" y1="{qy(120)}" x2="{BW}" y2="{qy(120)}" {Lt}/><line x1="{qx(36)}" y1="{qy(120)}" x2="{qx(44)}" y2="{qy(120)}" stroke="{VERT_D}" stroke-width="4" stroke-linecap="round"/>')
    for t in sorted(V['tirs'],key=lambda t:(t['is_goal'],-t['xg'])):
        x,y,r=qx(t['y']),qy(t['x']),max(.6*s,math.sqrt(t['xg'])*3.4*s)
        g+=(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+.6:.1f}" fill="{OR}" stroke="{VERT_D}" stroke-width="2.4"/>' if t['is_goal'] else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{VERT}" fill-opacity=".42" stroke="{VERT_D}" stroke-opacity=".75" stroke-width="1"/>')
    return 'A',g,'La carte des tirs'
def radar():
    CR=F['criteres']; N=len(CR); R0=BH/2-8; cx,cy=BW/2,BH/2; pol=lambda r,i:(cx+r*math.cos(-math.pi/2+i*2*math.pi/N),cy+r*math.sin(-math.pi/2+i*2*math.pi/N))
    g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R0*v/100:.1f}" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="1.2"/>' for v in (25,50,75,100))
    for i in range(N): x,y=pol(R0,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".22" stroke-width="1"/>'
    P=[pol(R0*max(c['centile'],4)/100,i) for i,c in enumerate(CR)]
    g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in P)+f'" fill="{OR}" fill-opacity=".4" stroke="{OR}" stroke-width="2.6" stroke-linejoin="round"/>'+''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.3" fill="#fff" stroke="{VERT}" stroke-width="1.4"/>' for x,y in P)
    return 'V',g,'Le radar'
def courbes():
    C=V['xg_chrono']; fin=max(V['periodes_fin']); cum={'equipe':[(0,0)],'adversaire':[(0,0)]}; buts=[]
    for t in C:
        c=cum[t['camp']]; v=c[-1][1]+t['xg']; c.append((t['minute_ecoulee'],v))
        if t['is_goal']: buts.append((t['camp'],t['minute_ecoulee'],v))
    vmax=max(c[-1][1] for c in cum.values()); mg,mh,mb=12,16,14; fx=lambda m:mg+m/fin*(BW-2*mg); fy=lambda v:BH-mb-v/vmax*(BH-mb-mh)
    def marches(c):
        d=f'M{fx(0):.1f} {fy(0):.1f}'
        for m,v in c[1:]: d+=f'H{fx(m):.1f}V{fy(v):.1f}'
        return d+f'H{fx(fin):.1f}'
    g=f'<line x1="{mg}" y1="{BH-mb}" x2="{BW-mg}" y2="{BH-mb}" stroke="{VERT_D}" stroke-opacity=".35" stroke-width="1.5"/><path d="{marches(cum["equipe"])}V{fy(0):.1f}Z" fill="{VERT}" fill-opacity=".16"/>'
    g+=f'<path d="{marches(cum["adversaire"])}" fill="none" stroke="{ROUGE}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/><path d="{marches(cum["equipe"])}" fill="none" stroke="{VERT}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>'
    for camp,m,v in buts: g+=f'<circle cx="{fx(m):.1f}" cy="{fy(v):.1f}" r="5.2" fill="#fff" stroke="{VERT if camp=="equipe" else ROUGE}" stroke-width="2.8"/>'
    return 'A',g,'Le fil du match'
def chaleur():
    C=Z['heat']['cases']; mx=max(c[2] for c in C); g=''
    for cx,cy,n in C: g+=f'<rect x="{px(cx*10)+.8:.1f}" y="{py(cy*10)+.8:.1f}" width="{10*S-1.6:.1f}" height="{10*S-1.6:.1f}" rx="2" fill="{VERT}" fill-opacity="{.06+.94*(n/mx)**.85:.2f}"/>'
    return 'A',g+lignes(VERT_D,.5,1.5),'La carte de chaleur'
def nuage():
    P=Z['nuage']['points']; mx,my=max(p[1] for p in P),max(p[2] for p in P); a,b=22,16; fx=lambda v:a+math.sqrt(v/mx)*(BW-a-14); fy=lambda v:BH-b-math.sqrt(v/my)*(BH-b-14)
    g=f'<path d="M{a-8} 8V{BH-b+8}H{BW-8}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.5" stroke-linecap="round"/>'
    g+=''.join(f'<circle cx="{fx(x):.1f}" cy="{fy(y):.1f}" r="{3*k:.1f}" fill="#fff" fill-opacity=".34"/>' for m,x,y in P if not m)
    g+=''.join(f'<circle cx="{fx(x):.1f}" cy="{fy(y):.1f}" r="{5*k:.1f}" fill="{OR}" stroke="{NUIT}" stroke-width="1.6"/>' for m,x,y in P if m)
    return 'B',g,'Le nuage de points'
def barres():
    B=Z['equipes']['barres']; mx=B[0][1]; n=len(B); a=10; pas=(BW-2*a)/n; e=pas*.66; base=BH-12
    g=f'<line x1="{a-2}" y1="{base+1}" x2="{BW-a+2}" y2="{base+1}" stroke="#fff" stroke-opacity=".5" stroke-width="1.6" stroke-linecap="round"/>'
    for i,(t,v,_) in enumerate(B):
        h=(BH-30)*v/mx; g+=f'<rect x="{a+i*pas+(pas-e)/2:.1f}" y="{base-h:.1f}" width="{e:.1f}" height="{h:.1f}" rx="2.4" fill="{OR if t=="Mali" else "#fff"}" fill-opacity="{1 if t=="Mali" else .86}"/>'
    return 'V',g,'Le classement'
FAB=dict(but=but,roue=roue,reseau=reseau,duel=duel,tirs=tirs,radar=radar,courbes=courbes,chaleur=chaleur,nuage=nuage,barres=barres)

cartes=''
for (x,y,r),t in zip(POS,TYPES):
    th,g,nom=FAB[t](); cartes+=(f'<div class="c {th}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">'+(f'<div class="tt">{nom}</div>' if TITRES else '')
                                 +f'<div class="pan"><svg width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}">{g}</svg></div></div>')
slogan=''
if MISE=='droite':
    c1,c2=(('#fff',OR) if FOND in ('nuit','vert') else (VERT_D,ROUGE))
    slogan=f'<div style="position:absolute;left:432px;top:171px;font:italic 900 84px/.94 \'BC\';text-transform:uppercase;white-space:nowrap;letter-spacing:.005em"><div style="color:{c1}">Les Aigles jouent.</div><div style="color:{c2}">La data parle.</div></div>'
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{FD[0]}}}svg{{display:block}}
#pt{{position:absolute;left:0;top:-250px;width:1500px;height:1000px}}#pt *{{fill:none;stroke:{FD[3]};stroke-width:.34;stroke-opacity:{FD[4]}}}
.c{{position:absolute;width:{CW}px;height:{CH}px;border-radius:8px;overflow:hidden;box-shadow:0 0 0 5px #fff,0 22px 40px {"rgba(0,0,0,.4)" if FOND in ("nuit","vert") else "rgba(70,40,0,.34)"}}}
.c.A{{background:{OR};color:{VERT_D}}}.c.B{{background:{NUIT};color:#fff}}.c.V{{background:{VERT};color:#fff}}
.tt{{position:absolute;left:{round(CW*.045)}px;top:{round(TT*.25)}px;font:italic 900 {TF}px/1 "BC";text-transform:uppercase;white-space:nowrap;letter-spacing:.005em}}
.pan{{position:absolute;left:{M}px;top:{TT}px;width:{BW}px;height:{BH}px;border-radius:6px;overflow:hidden}}.c.A .pan{{background:#fff}}
</style></head><body><div id="b">{fond}{slogan}{cartes}</div><script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',OUT,TYPES,O)

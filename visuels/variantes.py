"""Jeu de variantes pour chaque plan : A cadre blanc, B nuit, C encre, D blanc. Format Twitter/X 1080 x 1350.
Un thème = des couleurs et un cadre ; un plan = un dessin qui ne connaît que les couleurs du thème.
usage : python3 variantes.py <plan> <A|B|C|D> <sortie.html> [x|tiktok]     plans : accroche tirs but fil reseau fiche fin
        histoire scores decennies competitions (l'historique des Aigles depuis 1960 : python3 aigles_export.py d'abord)
Le format vertical TikTok (1080 x 1920) existe pour la fiche ; les autres plans y viennent quand une variante est retenue."""
import json, math, sys, os, collections
from da import BASE_CSS, photo, ordi, fr, COUPE, drapeau, pays, score, avec_logo
PLAN,TH_,OUT=sys.argv[1],sys.argv[2],sys.argv[3]; FMT=sys.argv[4] if len(sys.argv)>4 else 'x'; TT=FMT=='tiktok'
V=json.load(open('vitrine.json',encoding='utf-8'))
THEMES={
 'A':dict(nom='Cadre blanc',bg='#F6C41C',carte=True,ink='#0E1A13',titre='#064A25',doux='#5E6B62',trait='#E3E8E3',trait2='#EEF1EE',sA='#0B7A3B',sB='#0E1A13',
          terrain='#F3F6F3',ligne='#C3CCC6',mute='#8E9A91',piste='#E9EDE8',sig='#064A25',ctx='rgba(14,26,19,.72)',note='rgba(14,26,19,.78)',fond='#FFFFFF',but='#D4252A',
          niv=('#0B7A3B','#E3A600','#D4252A'),mono=False,blancs=False,hm='rgba(14,26,19,.72)'),
 'B':dict(nom='Nuit',bg='#04331A',carte=False,ink='#FFFFFF',titre='#FFFFFF',doux='#A9C2B3',trait='#1F5236',trait2='#154630',sA='#F6C41C',sB='#FFFFFF',
          terrain='#073C20',ligne='#2F6E4B',mute='#6F957F',piste='#0C4429',sig='#FFFFFF',ctx='#A9C2B3',note='#A9C2B3',fond='#04331A',but='#FFFFFF',
          niv=('#F6C41C','#CFE3D6','#FF7A6B'),mono=False,blancs=True,hm='#A9C2B3'),
 'C':dict(nom='Encre',bg='#F6C41C',carte=False,ink='#0E1A13',titre='#064A25',doux='rgba(14,26,19,.72)',trait='rgba(6,74,37,.3)',trait2='rgba(6,74,37,.16)',sA='#064A25',sB='#064A25',
          terrain='none',ligne='rgba(6,74,37,.5)',mute='rgba(6,74,37,.5)',piste='rgba(6,74,37,.16)',sig='#064A25',ctx='rgba(14,26,19,.72)',note='rgba(14,26,19,.78)',fond='#F6C41C',but='#064A25',
          niv=('#064A25','rgba(6,74,37,.5)','none'),mono=True,blancs=False,hm='rgba(14,26,19,.72)'),
 'D':dict(nom='Blanc',bg='#FFFFFF',carte=False,ink='#0E1A13',titre='#064A25',doux='#5E6B62',trait='#E3E8E3',trait2='#EEF1EE',sA='#0B7A3B',sB='#0E1A13',
          terrain='#F5F7F5',ligne='#C9D1CB',mute='#8E9A91',piste='#E9EDE8',sig='#064A25',ctx='rgba(14,26,19,.72)',note='#5E6B62',fond='#FFFFFF',but='#D4252A',
          niv=('#0B7A3B','#E3A600','#D4252A'),mono=False,blancs=False,hm='#5E6B62'),
}
T=THEMES[TH_]; W,H=((896,874) if T['carte'] else (968,930)) if not TT else ((818,1040) if T['carte'] else (890,1096)); Y0=50 if T['carte'] else 60
surn=lambda p:p.split(' ')[-1]
def noms_courts(joueurs):
    """Nom de famille, avec l'initiale du prénom quand deux joueurs portent le même nom."""
    c=collections.Counter(surn(p) for p in set(joueurs))
    return {p:(f"{p[0]}. {surn(p)}" if c[surn(p)]>1 else surn(p)) for p in set(joueurs)}

def page(ctx, hero, body, note, css=''):
    note=tuple(avec_logo(n,T['blancs']) for n in note)
    band='<div id="band"></div>' if TH_=='D' else ''
    x,t=('logo_x_blanc.png','logo_tt_blanc.png') if T['blancs'] else ('logo_x.png','logo_tt.png')
    cadre=f'<div id="p"><div id="in">{body}</div></div>' if T['carte'] else f'<div id="in" class="nu">{body}</div>'
    th=f'''#c{{background:{T['bg']};color:{T['ink']}}}#band{{position:absolute;left:0;right:0;top:0;height:124px;background:#F6C41C}}
#brand{{color:{T['sig']}}}#ctx{{color:{T['ctx']}}}
#nm{{position:absolute;left:0;top:4px;max-width:640px;overflow:hidden;font:italic 900 90px/1 "BC";color:{T['titre']};text-transform:uppercase;white-space:nowrap;padding-right:8px}}
#m1{{position:absolute;left:3px;top:100px;font:600 25px/1 "IN";color:{T['ink']};white-space:nowrap}}#m2{{position:absolute;left:3px;top:134px;font:500 21px/1 "IN";color:{T['hm']};white-space:nowrap}}
#sc small{{color:{T['hm']}}}#sc b{{color:{T['titre']}}}#sc span{{color:{T['ink']}}}
#note{{color:{T['note']}}}#note b{{color:{T['sig']}}}
#in{{position:absolute;left:36px;top:28px;width:896px;height:874px}}#in.nu{{left:56px;top:312px;width:968px;height:930px}}
.hd{{position:absolute;left:0;right:0;top:0;display:flex;justify-content:space-between;align-items:center}}#in.nu .hd{{padding-bottom:16px;border-bottom:1.5px solid {T['trait']}}}
.hd h3{{font:700 23px/1 "IN";color:{T['ink']}}}.lg{{display:flex;gap:20px;align-items:center;font:500 17.5px/1 "IN";color:{T['doux']}}}.lg span{{display:flex;align-items:center;gap:8px;white-space:nowrap}}.lg i{{display:block;border-radius:50%}}
.cap{{position:absolute;font:500 16.5px/1 "IN";color:{T['doux']};white-space:nowrap}}
h4{{font:700 19px/1 "IN";color:{T['ink']}}}
.th{{position:relative;height:22px;font:500 15px/1 "IN";color:{T['doux']}}}.th span{{position:absolute;top:0}}
.fam{{font:600 15px/1 "IN";color:{T['doux']};padding:13px 0 7px;border-bottom:1.5px solid {T['trait']}}}
.r{{position:relative;height:39px;border-bottom:1px solid {T['trait2']}}}.r>span{{position:absolute;white-space:nowrap}}
.lab{{font:600 17px "IN";fill:{T['ink']};paint-order:stroke;stroke:{T['fond'] if T['terrain']=='none' else T['terrain']};stroke-width:5px;stroke-linejoin:round}}
'''
    # format vertical : tout entre y = 150 et y = 1580, et à gauche de x = 946
    tt=f'''html,body{{width:1080px;height:1920px}}#c{{height:1920px}}#top{{right:134px;top:150px}}#hero{{right:134px;top:238px}}#band{{height:236px}}
#p{{top:410px;width:890px;height:1096px}}#in{{width:818px;height:1040px}}#in.nu{{top:410px;width:890px;height:1096px}}#nm{{max-width:470px}}
#note{{top:1518px;right:134px;display:block;font-size:16.5px;line-height:1}}#note p{{white-space:nowrap}}#note div{{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}}#note b{{font-size:22px}}''' if TT else ''
    soc=f'<b><img src="{x}" alt="X" style="height:22px"><img src="{t}" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
    pied=f'<p>{note[0]}</p><div><span>{note[1]}</span>{soc}</div>' if TT else f'<span>{note[0]}<br>{note[1]}</span>{soc}'
    fit="document.querySelectorAll('#nm').forEach(e=>{let s=90;while(e.scrollWidth>e.clientWidth+1&&s>40){s-=2;e.style.fontSize=s+'px'}});"
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}{th}{tt}{css}</style></head><body><div id="c">{band}
<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx">{ctx}</div></div>
<div id="hero">{hero}</div>{cadre}
<div id="note">{pied}</div>
</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{{fit}window.READY=true}})</script></body></html>'''
def hero(titre,m1,m2,cle):
    return f'<div id="nm">{titre}</div><div id="m1">{m1}</div><div id="m2">{m2}</div><div id="sc"><small>{cle[0]}</small><b>{cle[1]}</b><span>{cle[2]}</span></div>'
CAN="Coupe d'Afrique des nations 2023"

def terrain_entier(S):
    """Terrain complet vu de haut, l'équipe attaque vers le haut. Repère StatsBomb 120 x 80."""
    L=f'stroke="{T["ligne"]}" stroke-width="2" fill="none"'; PW,PH=80*S,120*S
    px=lambda y:y*S; py=lambda x:(120-x)*S
    g=(f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="{T["terrain"]}"/>' if T['terrain']!='none' else '')+f'<rect x="1" y="1" width="{PW-2}" height="{PH-2}" {L}/>'
    g+=f'<line x1="0" y1="{PH/2}" x2="{PW}" y2="{PH/2}" {L}/><circle cx="{PW/2}" cy="{PH/2}" r="{10*S}" {L}/>'
    for top in (True,False):
        y0=0 if top else PH-18*S; y1=0 if top else PH-6*S
        g+=f'<rect x="{px(18)}" y="{y0}" width="{44*S}" height="{18*S}" {L}/><rect x="{px(30)}" y="{y1}" width="{20*S}" height="{6*S}" {L}/>'
    return g,px,py,PW,PH
def place(cands, boites, PW, PH, tw, th=20):
    """Choisit, parmi des positions candidates (x du début du texte, y de la ligne de base), celle qui gêne le moins."""
    best=None
    for i,(x,yb) in enumerate(cands):
        x0,y0,x1,y1=x-3,yb-th+3,x+tw+3,yb+5; cost=i*.3
        if x0<4 or x1>PW-4 or y0<4 or y1>PH-4: cost+=60
        for (a,b,c,d) in boites:
            ox=min(x1,c)-max(x0,a); oy=min(y1,d)-max(y0,b)
            if ox>0 and oy>0: cost+=10+ox*oy/40
        if best is None or cost<best[0]: best=(cost,x,yb,(x0,y0,x1,y1))
    return best[1],best[2],best[3]
tw=lambda s:len(s)*9.4+4

# ------------------------------------------------------------------ carte des tirs
def plan_tirs():
    Tr=V['tirs']; M=V['matches']; buts=[t for t in Tr if t['is_goal']]; xg=sum(t['xg'] for t in Tr)
    in_box=lambda t:t['x']>=102 and 18<=t['y']<=62
    cadres=[t for t in Tr if t['outcome'] in ('Goal','Saved','Saved to Post')]; csc=sum(m['goals_for'] for m in M)-len(buts)
    S=W/80; X0=80.5; PW=80*S; PH=(120-X0)*S; GH=2.2*S; px=lambda y:y*S; py=lambda x:GH+(120-x)*S
    L=f'stroke="{T["ligne"]}" stroke-width="2.2" fill="none"'
    g=(f'<rect x="0" y="{GH}" width="{PW}" height="{PH}" fill="{T["terrain"]}"/>' if T['terrain']!='none' else '')
    g+=f'<path d="M0 {GH+PH}V{GH}H{PW}V{GH+PH}" {L}/><rect x="{px(18)}" y="{py(120)}" width="{44*S}" height="{18*S}" {L}/><rect x="{px(30)}" y="{py(120)}" width="{20*S}" height="{6*S}" {L}/>'
    g+=f'<rect x="{px(36)}" y="{py(120)-GH+1.5}" width="{8*S}" height="{GH-1.5}" stroke="{T["mute"]}" stroke-width="2.6" fill="none"/>'
    a=math.acos(6/10); ax=10*math.sin(a)*S
    g+=f'<path d="M{px(40)-ax:.1f} {py(102):.1f}A{10*S} {10*S} 0 0 0 {px(40)+ax:.1f} {py(102):.1f}" {L}/>'
    R=lambda v:max(6.5,math.sqrt(v)*38)
    nb=dict(fill=T['mute'],op='.18',st=T['mute']) if not T['mono'] else dict(fill='none',op='0',st=T['mute'])
    for t in sorted(Tr,key=lambda t:(t['is_goal'],-t['xg'])):
        x,y,r=px(t['y']),py(t['x']),R(t['xg'])
        if t['is_goal']: g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{T["sA"]}" stroke="{T["fond"]}" stroke-width="3"/>'
        else: g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{nb["fill"]}" fill-opacity="{nb["op"]}" stroke="{nb["st"]}" stroke-width="1.8"/>'
    C=[(px(t['y'])-R(t['xg']),py(t['x'])-R(t['xg']),px(t['y'])+R(t['xg']),py(t['x'])+R(t['xg'])) for t in Tr]
    for t in [t for t in Tr if t['shot_type']=='Penalty' and not t['is_goal']]:
        x,y,r=px(t['y']),py(t['x']),R(t['xg']); me=(x-r,y-r,x+r,y+r)
        cands=[(x+(r+d)*math.cos(math.radians(a))+(8 if math.cos(math.radians(a))>=0 else -8-tw('Penalty arrêté')), y+(r+d)*math.sin(math.radians(a))+6) for d in range(30,200,10) for a in (20,160,-20,200,40,140,0,180)]
        lx,ly,_=place(cands,[c for c in C if c!=me],PW,PH+GH,tw('Penalty arrêté'))
        g+=f'<line x1="{x+ (r+3)*(1 if lx>x else -1):.1f}" y1="{y:.1f}" x2="{lx-6 if lx>x else lx+tw("Penalty arrêté")+2:.1f}" y2="{ly-6:.1f}" stroke="{T["doux"]}" stroke-width="1.6"/><text x="{lx:.1f}" y="{ly:.1f}" class="lab">Penalty arrêté</text>'
    by=collections.defaultdict(lambda:[0,0.0,0])
    for t in [t for t in Tr if t['shot_type']!='Penalty']: by[t['player']][0]+=1; by[t['player']][1]+=t['xg']; by[t['player']][2]+=int(t['is_goal'])
    top=sorted(by.items(),key=lambda kv:(-kv[1][1],kv[0]))[:5]; mx=top[0][1][1]
    rows=''.join(f'<div class="r"><span class="n">{n}</span><span class="v1">{v[0]}</span><span class="b"><i style="width:{v[1]/mx*100:.0f}%"></i></span><span class="v2">{fr(v[1],2)}</span><span class="c">{v[2]}</span></div>' for n,v in top)
    z=lambda nom,l:f'<div class="r"><span class="n">{nom}</span><span class="zv">{len(l)}</span><span class="c">{sum(t["is_goal"] for t in l)}</span></div>'
    zones='<div class="fam">Zone</div>'+z('Dans la surface',[t for t in Tr if in_box(t)])+z('Hors de la surface',[t for t in Tr if not in_box(t)])+'<div class="fam">Situation</div>'+z('Dans le jeu',[t for t in Tr if t['shot_type']=='Open Play'])+z('Coup franc ou penalty',[t for t in Tr if t['shot_type']!='Open Play'])
    yb=Y0+PH+GH
    gl=f'<i style="width:18px;height:18px;background:{T["sA"]}"></i>'; nl=f'<i style="width:18px;height:18px;border:1.8px solid {T["mute"]}"></i>'
    css=f'''.r .n{{left:0;top:10px;font:500 19px/1 "IN";color:{T['ink']}}}.r .v1{{left:214px;width:44px;top:11px;text-align:right;font:400 18px/1 "IN";color:{T['doux']}}}
.r .b{{left:286px;width:90px;top:16px;height:6px;border-radius:3px;background:{T['piste']};overflow:hidden}}.r .b i{{display:block;height:100%;border-radius:3px;background:{T['sA']}}}
.r .v2{{left:386px;width:52px;top:11px;text-align:right;font:400 18px/1 "IN";color:{T['doux']}}}.r .c{{right:0;top:9px;font:700 20px/1 "IN";color:{T['ink']}}}.r .zv{{right:86px;width:60px;top:11px;text-align:right;font:400 18px/1 "IN";color:{T['doux']}}}
#bt{{position:absolute;left:0;right:0;top:{yb+56:.0f}px;display:grid;grid-template-columns:1.32fr 1fr;gap:56px}}.th.e{{margin-top:16px;border-bottom:1.5px solid {T['trait']};padding-bottom:26px}}.th.n{{margin-top:16px;padding-bottom:6px}}'''
    body=f'''<div class="hd"><h3>Chaque rond est un tir</h3><div class="lg"><span>{gl}but</span><span>{nl}pas de but</span></div></div>
<svg style="position:absolute;left:0;top:{Y0}px;overflow:visible" width="{PW:.0f}" height="{PH+GH:.0f}" viewBox="0 0 {PW:.0f} {PH+GH:.0f}">{g}</svg>
<div class="cap" style="left:0;top:{yb+14:.0f}px">Plus le rond est gros, plus l'occasion était belle (xG)</div>
<div id="bt"><div><h4>Qui a eu les occasions, hors penalty</h4><div class="th e"><span style="left:214px;width:44px;text-align:right">tirs</span><span style="left:286px">buts attendus (xG)</span><span style="right:0">buts</span></div>{rows}</div>
<div><h4>Le détail des tirs</h4><div class="th n"><span style="right:86px;width:60px;text-align:right">tirs</span><span style="right:0">buts</span></div>{zones}</div></div>'''
    h=hero('Les tirs du Mali',f'{len(Tr)} tirs en {len(M)} matchs, dont {len(cadres)} cadrés','Toutes les tentatives des Aigles pendant le tournoi',('Buts marqués sur tir',str(len(buts)),f'pour {fr(xg)} buts attendus (xG)'))
    pens=[t for t in Tr if t['shot_type']=='Penalty']; arr=all(t['outcome']=='Saved' for t in pens if not t['is_goal'])
    note=("xG : la chance qu'un tir finisse au fond."+(f" Les {fr(xg)} comptent un penalty {'arrêté' if arr else 'manqué'}." if any(not t['is_goal'] for t in pens) else ''),(f"Autre but du Mali : {'un' if csc==1 else csc} contre son camp. " if csc>0 else '')+"Données StatsBomb Open Data.")
    return page(CAN,h,body,note,css)

# ------------------------------------------------------------------ l'anatomie d'un but
def plan_but():
    B=V['but']; seq=B['seq']; S=(H-Y0-6)/120; g,px,py,PW,PH=terrain_entier(S)
    nc=noms_courts([e['player'] for e in seq]); r=13
    for e in seq:
        x1,y1,x2,y2=px(e['y']),py(e['x']),px(e['ey']),py(e['ex'])
        if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{T["sA"]}" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round"/>'
        elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{T["sA"]}" stroke-width="3.2" stroke-linecap="round"/>'
        else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{T["but"]}" stroke-width="5" stroke-linecap="round"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="11" fill="{T["fond"]}" stroke="{T["but"]}" stroke-width="5"/>'
    passes=[e for e in seq if e['type']=='Pass']; boites=[(px(e['y'])-r-2,py(e['x'])-r-2,px(e['y'])+r+2,py(e['x'])+r+2) for e in passes]
    vus=set(); nommes=[]; labs=''
    for i,e in enumerate(passes,1):
        x,y=px(e['y']),py(e['x'])
        g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{T["fond"]}" stroke="{T["sA"]}" stroke-width="3"/><text x="{x:.1f}" y="{y+5.5:.1f}" text-anchor="middle" style="font:700 15px IN;fill:{T["ink"]}">{i}</text>'
        if any(q==e['player'] and math.hypot(x-qx,y-qy)<70 for q,qx,qy in nommes): continue   # même joueur, même endroit : un seul nom
        vus.add(e['player']); nommes.append((e['player'],x,y)); n=nc[e['player']]; w=tw(n)
        cands=[(x+r+8,y+6),(x-r-8-w,y+6),(x-w/2,y-r-9),(x-w/2,y+r+21),(x+r+4,y-r-4),(x-r-4-w,y-r-4),(x+r+4,y+r+18),(x-r-4-w,y+r+18),
               (x-w/2+16,y+r+21),(x-w/2-16,y+r+21),(x-w/2+16,y-r-9),(x-w/2-16,y-r-9),(x-w/2+30,y+r+23),(x-w/2-30,y+r+23),
               (x-6-w,y+r+38),(x+6,y+r+38),(x-w/2,y+r+40),(x-6-w,y-r-26),(x+6,y-r-26),(x-w/2,y-r-28)]
        # un nom ne doit jamais être plus près d'une autre pastille que de la sienne
        pres=lambda c:min(passes,key=lambda q:math.hypot(c[0]+w/2-px(q['y']),c[1]-7-py(q['x']))) is e
        cands=[c for c in cands if pres(c)] or cands
        lx,ly,bx=place(cands,boites,PW,PH,w); boites.append(bx); labs+=f'<text x="{lx:.1f}" y="{ly:.1f}" class="lab">{n}</text>'
    sh=seq[-1]; n=nc[sh['player']]; x,y=px(sh['y']),py(sh['x']); lx,ly,bx=place([(x-tw(n)-14,y+8),(x+14,y+8),(x-tw(n)/2,y+26)],boites,PW,PH,tw(n))
    if sh['player'] not in vus: labs+=f'<text x="{lx:.1f}" y="{ly:.1f}" class="lab">{n}</text>'
    XC=PW+44; CW=W-XC
    stat=lambda v,l,y:f'<div class="st" style="top:{y}px"><b>{v}</b><span>{l}</span></div>'
    css=f'''.st{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px}}.st b{{display:block;font:italic 900 124px/.9 "BC";color:{T['titre']}}}.st span{{display:block;font:600 20px/1.25 "IN";color:{T['ink']};margin-top:6px}}
#leg{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px;bottom:8px;font:500 17px/1 "IN";color:{T['doux']}}}#leg div{{display:flex;align-items:center;gap:12px;height:34px;white-space:nowrap}}#leg svg{{flex:none}}'''
    body=f'''<div class="hd"><h3>Onze passes, en repassant par le gardien</h3></div>
<svg style="position:absolute;left:0;top:{Y0}px;overflow:visible" width="{PW:.0f}" height="{PH:.0f}" viewBox="0 0 {PW:.0f} {PH:.0f}">{g}{labs}</svg>
{stat(B['passes'],'passes de suite',Y0+18)}{stat(B['joueurs'],'joueurs sur onze<br>touchent le ballon',Y0+218)}{stat(round(B['duree']),'secondes entre la récupération<br>du ballon et le tir',Y0+448)}
<div id="leg"><div><svg width="46" height="8"><line x1="2" y1="4" x2="44" y2="4" stroke="{T['sA']}" stroke-width="3.2" stroke-linecap="round"/></svg>passe</div>
<div><svg width="46" height="8"><line x1="2" y1="4" x2="44" y2="4" stroke="{T['sA']}" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round"/></svg>conduite de balle</div>
<div><svg width="46" height="8"><line x1="2" y1="4" x2="44" y2="4" stroke="{T['but']}" stroke-width="5" stroke-linecap="round"/></svg>le tir</div></div>'''
    m=B['match']; h=hero("L'anatomie d'un but",f'{score(m[0],m[2],m[3],m[1])}, huitième de finale',f'But de {surn(B["buteur"])} à la {B["minute"]}e minute',("Chance de marquer sur ce tir",f'{B["xg"]*100:.0f} %',"d'après sa position (xG)"))
    return page(CAN,h,body,("Les numéros suivent l'ordre des passes. Le Mali attaque vers le haut.","Données StatsBomb Open Data."),css)

# ------------------------------------------------------------------ le fil du match
def plan_fil():
    X=V['xg_chrono']; PF=V['periodes_fin']; EX=V['expulsions']; M=V['matches'][-1]
    CWd=W-86; CH=H-Y0-26-62-240; tmax=PF[-1]; ymax=1.5; sx=lambda t:t/tmax*CWd; sy=lambda v:CH-v/ymax*CH
    g=''
    r0=next(e for e in EX if e['camp']=='adversaire'); x0=sx(r0['minute_ecoulee'])
    g+=f'<rect x="{x0:.1f}" y="0" width="{CWd-x0:.1f}" height="{CH}" fill="{T["sA"]}" fill-opacity="{.08 if not T["mono"] else .07}"/>'
    g+=f'<text x="{x0+10:.1f}" y="22" style="font:600 16px IN;fill:{T["doux"]}">{M["opponent"]} à dix dès la {r0["minute_aff"]}e minute</text>'
    for t,lab in zip(PF[:3],('mi-temps','prolongation','')):
        g+=f'<line x1="{sx(t):.1f}" y1="0" x2="{sx(t):.1f}" y2="{CH}" stroke="{T["ligne"]}" stroke-width="1.4" stroke-dasharray="3 6"/><text x="{sx(t):.1f}" y="{CH+24}" text-anchor="middle" style="font:500 15px IN;fill:{T["doux"]}">{lab}</text>'
    g+=f'<line x1="0" y1="{CH}" x2="{CWd}" y2="{CH}" stroke="{T["mute"]}" stroke-width="2"/>'
    fin={}; marks=[]
    for camp,col,dash in (('adversaire',T['sB'],'7 6' if T['mono'] else ''),('equipe',T['sA'],'')):
        v=0; d=f'M0 {CH}'
        for s in [s for s in X if s['camp']==camp]:
            d+=f'H{sx(s["minute_ecoulee"]):.1f}'; v+=s['xg']; d+=f'V{sy(v):.1f}'
            if s['is_goal'] or s['shot_type']=='Penalty': marks.append((camp,s,v,col))
        d+=f'H{CWd}'; fin[camp]=v
        da=f' stroke-dasharray="{dash}"' if dash else ''
        g+=f'<path d="{d}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round"{da}/>'
        g+=f'<text x="{CWd+12}" y="{sy(v)+9:.1f}" style="font:italic 900 34px BC;fill:{T["titre"] if camp=="equipe" else T["ink"]}">{fr(v,2)}</text>'
    pos={'Dorgeles':(-14,-16,'end'),'Adingra':(16,30,'start'),'Diakité':(-14,-14,'end'),'Traoré':(16,38,'start')}
    for camp,s,v,col in marks:
        x,y=sx(s['minute_ecoulee']),sy(v); nom=surn(s['player']); dx,dy,an=pos.get(nom,(14,-14,'start'))
        if s['is_goal']:
            g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{T["fond"]}" stroke="{col}" stroke-width="4"/>'; txt=f"But {nom} ({s['minute_aff']}')"
        else: txt=f"Penalty {'arrêté' if s.get('outcome')=='Saved' else 'manqué'} ({s['minute_aff']}')"
        g+=f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{an}" class="lab" style="stroke:{T["fond"]}">{txt}</text>'
    opp=len([s for s in X if s['camp']=='adversaire']); eq=len([s for s in X if s['camp']=='equipe'])
    li=lambda l,a,b,ga,gb:f'<div class="r"><span class="n">{l}</span><span class="a{" w" if ga else ""}">{a}</span><span class="b2{" w" if gb else ""}">{b}</span></div>'
    npa=sum(s['xg'] for s in X if s['camp']=='equipe' and s['shot_type']!='Penalty'); npb=sum(s['xg'] for s in X if s['camp']=='adversaire' and s['shot_type']!='Penalty'); pen=sum(s['xg'] for s in X if s['camp']=='equipe' and s['shot_type']=='Penalty')
    rows=li('Buts',M['goals_for'],M['goals_against'],M['goals_for']>M['goals_against'],M['goals_against']>M['goals_for'])+li('Buts attendus (xG)',fr(M['xg'],2),fr(M['xg_against'],2),M['xg']>M['xg_against'],M['xg_against']>M['xg'])+li('Buts attendus hors penalty',fr(npa,2),fr(npb,2),npa>npb,npb>npa)+li('Tirs',eq,opp,eq>opp,opp>eq)+li('Possession',f"{M['possession_pct']:.0f} %",f"{100-M['possession_pct']:.0f} %",M['possession_pct']>50,M['possession_pct']<50)
    def mk(col,dash):
        da=' stroke-dasharray="7 6"' if dash else ''
        return f'<svg width="34" height="8"><line x1="2" y1="4" x2="32" y2="4" stroke="{col}" stroke-width="4"{da}/></svg>'
    yt=Y0+26+CH+62
    css=f'''#tb{{position:absolute;left:0;top:{yt}px;width:{W}px}}.r .n{{left:0;top:10px;font:500 19px/1 "IN";color:{T['ink']}}}
.r .a,.r .b2{{top:9px;width:150px;text-align:right;font:500 20px/1 "IN";color:{T['doux']}}}.r .a{{right:190px}}.r .b2{{right:0}}.r .w{{font-weight:700;color:{T['ink']}}}
.th.e{{border-bottom:1.5px solid {T['trait']};padding-bottom:26px}}.th span{{display:flex;align-items:center;gap:8px}}'''
    body=f'''<div class="hd"><h3>Les occasions s'additionnent, minute après minute</h3><div class="lg"><span>{mk(T['sA'],False)}Mali</span><span>{mk(T['sB'],T['mono'])}{M['opponent']}</span></div></div>
<svg style="position:absolute;left:0;top:{Y0+26}px;overflow:visible" width="{W}" height="{CH+30}" viewBox="0 0 {W} {CH+30}">{g}</svg>
<div id="tb"><div class="th e"><span style="right:190px;width:150px;justify-content:flex-end;gap:0">{pays('Mali',14)}</span><span style="right:0;width:150px;justify-content:flex-end;gap:0">{pays(M['opponent'],14)}</span></div>{rows}</div>'''
    h=hero('Le fil du match',f"{score('Mali',M['goals_for'],M['goals_against'],M['opponent'])}, quart de finale",'Les occasions de chaque équipe, après prolongation',('Buts attendus du Mali',fr(M['xg'],2),f"dont {fr(pen,2)} sur le penalty"))
    return page(CAN,h,body,("Chaque marche est un tir : plus elle est haute, plus l'occasion était belle (xG).","Possession : calculée sur les passes du match. Données StatsBomb Open Data."),css)

# ------------------------------------------------------------------ le réseau de passes
def plan_reseau():
    R=V['reseau_passes']; N={n['player_id']:n for n in R['nodes']}; E=sorted(R['edges'],key=lambda e:-e['n'])
    av=lambda e:int(e['avant']); S=(H-Y0-6)/120; g,px,py,PW,PH=terrain_entier(S)
    nc=noms_courts([n['player'] for n in R['nodes']]); top=E[0]
    for e in E[::-1]:
        a,b=N[e['a']],N[e['b']]; first=e is top
        col=T['but'] if first else T['mute']; op=1 if first else min(.9,.25+e['n']/40)
        g+=f'<line x1="{px(a["y"]):.1f}" y1="{py(a["x"]):.1f}" x2="{px(b["y"]):.1f}" y2="{py(b["x"]):.1f}" stroke="{col}" stroke-opacity="{op:.2f}" stroke-width="{1.2+e["n"]*.42:.1f}" stroke-linecap="round"/>'
    rr=lambda n:12+math.sqrt(n['passes'])*1.5; boites=[(px(n['y'])-rr(n),py(n['x'])-rr(n),px(n['y'])+rr(n),py(n['x'])+rr(n)) for n in R['nodes']]; labs=''
    for n in R['nodes']:
        x,y,r=px(n['y']),py(n['x']),rr(n); g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{T["sA"]}" stroke="{T["fond"] if T["terrain"]=="none" else T["terrain"]}" stroke-width="3"/>'
        nm=nc[n['player']]; w=tw(nm); cands=[(x-w/2,y+r+21),(x-w/2,y-r-9),(x+r+8,y+6),(x-r-8-w,y+6),(x+r+2,y+r+16),(x-r-2-w,y+r+16),(x+r+2,y-r-4),(x-r-2-w,y-r-4)]
        lx,ly,bx=place(cands,boites,PW,PH,w); boites.append(bx); labs+=f'<text x="{lx:.1f}" y="{ly:.1f}" class="lab">{nm}</text>'
    XC=PW+44; CW=W-XC; a,b=nc[N[top['a']]['player']],nc[N[top['b']]['player']]; M=V['matches'][-1]
    nav=av(top); suite='aucune vers l\'avant' if nav==0 else f'dont {nav} vers l\'avant'
    rows=''.join(f'<div class="r"><span class="n">{nc[N[e["a"]]["player"]]}–{nc[N[e["b"]]["player"]]}</span><span class="c">{e["n"]}</span></div>' for e in E[:5])
    dc=all('Center Back' in (N[top[k]].get('poste') or '') for k in ('a','b')); qui='les deux défenseurs centraux' if dc else None
    avant,apres=round(V['part_passes']['avant_rouge']),round(V['part_passes']['apres_rouge']); r0m=next(e for e in V['expulsions'] if e['camp']=='adversaire')['minute_aff']
    css=f'''.st{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px;top:{Y0+18}px}}.st b{{display:block;font:italic 900 124px/.9 "BC";color:{T['titre']}}}.st span{{display:block;font:600 20px/1.25 "IN";color:{T['ink']};margin-top:6px}}
#ls{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px;top:{Y0+10}px}}#cx{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px;top:{Y0+330}px}}#cx p{{margin-top:12px;font:500 18.5px/1.45 "IN";color:{T['ink']}}}.th.e2{{margin-top:14px;padding-bottom:26px;border-bottom:1.5px solid {T['trait']}}}.r .c1{{right:84px;width:70px;top:10px;text-align:right;font:500 19px/1 "IN";color:{T['doux']}}}
.r .n{{left:0;top:11px;font:500 17px/1 "IN";color:{T['ink']}}}.r .c{{right:0;top:9px;font:700 20px/1 "IN";color:{T['ink']}}}
#leg{{position:absolute;left:{XC:.0f}px;width:{CW:.0f}px;bottom:8px;font:500 17px/1.4 "IN";color:{T['doux']}}}'''
    body=f'''<div class="hd"><h3>Qui joue avec qui</h3></div>
<svg style="position:absolute;left:0;top:{Y0}px;overflow:visible" width="{PW:.0f}" height="{PH:.0f}" viewBox="0 0 {PW:.0f} {PH:.0f}">{g}{labs}</svg>
<div id="ls"><h4>Les duos les plus sollicités</h4><div class="th e2"><span style="right:0">passes</span></div>{rows}</div>
<div id="cx"><h4>Le contexte</h4><p>La {M['opponent']} joue à dix dès la {r0m}e minute. Le Mali a {apres} % de possession après le carton, contre {avant} % avant.</p></div>
<div id="leg">Chaque rond est placé là où le joueur fait ses passes en moyenne ; plus il est gros, plus le joueur en fait. Plus le trait est épais, plus les deux joueurs se sont trouvés (quatre passes au moins).</div>'''
    h=hero('Le réseau de passes',f"{score('Mali',M['goals_for'],M['goals_against'],M['opponent'])}, quart de finale",f"Onze de départ, jusqu'à la {R['until_clock']}e minute",('Passes du duo le plus sollicité',str(top['n']),f"entre {a} et {b}"+(", les deux centraux" if qui else "")))
    return page(CAN,h,body,("Onze de départ, jusqu'au premier changement malien.","Le Mali attaque vers le haut. Données StatsBomb Open Data."),css)

# ------------------------------------------------------------------ la fiche joueur
def plan_fiche():
    F=json.load(open('../outputs/fiches/hamari-traore_poste.json',encoding='utf-8')); B=F['bassin']; CR=F['criteres']
    f1,f2,f3=T['niv']; niv=lambda p:(f1 if p>=75 else (f2 if p>=25 else f3))
    cx,cy,R=(250,262,158) if not TT else (250,206,152); RH=524 if not TT else cy+R+62; N=len(CR); ang=lambda i:-math.pi/2+i*2*math.pi/N; pol=lambda r,i:(cx+r*math.cos(ang(i)),cy+r*math.sin(ang(i)))
    g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R*v/100:.1f}" fill="none" stroke="{T["ligne"]}" stroke-width="1.5"/>' for v in (25,75,100))
    g+=f'<circle cx="{cx}" cy="{cy}" r="{R*.5:.1f}" fill="none" stroke="{T["mute"]}" stroke-width="1.5" stroke-dasharray="3 6"/>'
    for i in range(N): x,y=pol(R,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{T["ligne"]}" stroke-width="1.2"/>'
    pts=[pol(R*max(c['centile'],2)/100,i) for i,c in enumerate(CR)]
    g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{T["sA"]}" fill-opacity=".2" stroke="{T["sA"]}" stroke-width="3" stroke-linejoin="round"/>'
    g+=''.join(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{T["fond"]}" stroke="{T["sA"]}" stroke-width="3"/>' for x,y in pts)
    for i,c in enumerate(CR):
        a=ang(i); deg=math.degrees(a)+90; bas=math.sin(a)>.15; lines=COUPE.get(c['k'],[c['nom']]); n=len(lines)
        for j,t in enumerate(lines):
            rr=R+22+((n-1-j) if not bas else j)*21+(4 if bas else 0); x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
            g+=f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" transform="rotate({deg+(180 if bas else 0):.1f} {x:.1f} {y:.1f})" class="rl" style="font:600 18px IN;fill:{T["ink"]}">{t}</text>'
    def barre(c):
        col=niv(c['centile']); w=max(c['valeur']/c['max']*100,4) if c['max'] else 4; med=c['mediane']/c['max']*100 if c['max'] else 0
        trait=f'<u style="left:{med:.0f}%"></u>'
        return (f'<i style="width:{w:.0f}%;background:{col}"></i>' if col!='none' else f'<i style="width:{max(w,10):.0f}%;box-shadow:inset 0 0 0 1.6px {T["sA"]}"></i>')+trait
    blocs={}                                            # une valeur nulle n'a pas de rang : plusieurs joueurs sont à zéro, les classer entre eux n'a pas de sens
    for c in CR:
        blocs.setdefault(c['famille'],f'<div class="fam">{c["famille"]}</div>')
        blocs[c['famille']]+=f'<div class="r"><span class="n">{c["court"]}</span><span class="v">{fr(c["valeur"],2 if c["k"] in ("xa_p90","npxg_p90") else 1)}</span><span class="b">{barre(c)}</span><span class="c">{ordi(c["rang"]) if c["valeur"]>0 else "–"}</span></div>'
    fams=list(blocs); TH=f'<div class="th"><span class="t1">par 90 min</span><span style="right:0">rang sur {B["effectif"]}</span></div>'
    if TT:                                              # vertical : deux colonnes aussi équilibrées que possible, sans couper une famille
        nb=[sum(1 for c in CR if c['famille']==f) for f in fams]; cut=min(range(1,len(fams)),key=lambda i:abs(sum(nb[:i])-sum(nb[i:])))
        TABLE=f'<div id="tb" class="deux"><div>{TH}{"".join(blocs[f] for f in fams[:cut])}</div><div>{TH}{"".join(blocs[f] for f in fams[cut:])}</div></div>'
    else: TABLE=f'<div id="tb">{TH}{"".join(blocs[f] for f in fams)}</div>'
    colh=max(22+len(fs)*36.5+sum(1 for c in CR if c['famille'] in fs)*(37 if TT else 40) for fs in ((fams[:cut],fams[cut:]) if TT else (fams,)))   # hauteur du tableau
    # « Ce qu'il réussit » : barres neutres, la couleur ne juge pas un taux
    reu=''.join(f'<div class="r q"><span class="n">{x["nom"]}</span><span class="v">{x["reussis"]} sur {x["tentes"]}</span><span class="b"><i style="width:{max(x["pct"] or 0,3)}%;background:{T["mute"]}"></i></span><span class="c">{x["pct"] if x["pct"] is not None else "–"} %</span></div>' for x in F['reussite'])
    notes=list(F['notes_bassin']); notes.remove(F['note']); lo,hi=min(notes+[F['note']]),max(notes+[F['note']])
    ticks=''.join(f'<i style="left:{(v-lo)/(hi-lo)*100:.2f}%"></i>' for v in notes)
    club='';
    import csv
    for r in csv.DictReader(open('../registre/joueurs.csv',encoding='utf-8')):
        if r['nom']==F['player'] and r['club'] and r['club_a_confirmer']!='oui': club=r['club']
    pt=lambda c:(f'<i style="background:{c}"></i>' if c!='none' else f'<i style="box-shadow:inset 0 0 0 1.6px {T["sA"]}"></i>')
    TX=W-412; RT=Y0-8 if not TT else Y0-2; RL=-14 if not TT else (W-500)//2; YT=Y0 if not TT else RT+RH+30; YS=Y0+560 if not TT else YT+colh+12
    css=f'''.phh{{position:absolute;left:0;top:4px;width:150px;height:150px;border-radius:50%;overflow:hidden;background:#E9EDE8;box-shadow:0 0 0 5px {'#fff' if TH_!='C' else T['sA']}}}.phh img,.phh svg{{width:100%;height:100%;display:block;object-fit:cover}}
#nm{{left:178px}}#m1{{left:181px}}#m2{{left:181px}}#m1 .act{{font:500 18px/1 "IN";color:{T['hm']};margin-left:9px}}
.lg i{{width:11px;height:11px}}
#tb{{position:absolute;left:{TX}px;top:{Y0}px;width:412px}}.th .t1{{left:168px;width:100px;text-align:right}}.r .n{{left:0;top:11px;font:500 19px/1 "IN";color:{T['ink']}}}.r .v{{left:212px;width:56px;top:10px;text-align:right;font:700 19px/1 "IN";color:{T['ink']}}}
.r .b{{left:282px;width:74px;top:17px;height:6px;border-radius:3px;background:{T['piste']}}}.r .b i{{display:block;height:100%;border-radius:3px}}.r .b u{{position:absolute;top:-4px;width:2px;height:14px;background:{T['ink']};opacity:.55;text-decoration:none}}
.r .c{{right:0;top:12px;font:500 17px/1 "IN";color:{T['doux']}}}
#bt .r.q .n{{left:0}}#bt .r.q .v{{left:auto;right:212px;width:120px;font:400 17px/1 "IN";color:{T['doux']};top:12px}}#bt .r.q .b{{left:auto;right:78px;width:120px}}#bt .r.q .c{{right:0;top:10px;font:700 19px/1 "IN";color:{T['ink']}}}
#sep{{position:absolute;left:0;right:0;top:{YS}px;border-top:1.5px solid {T['trait']}}}
#bt{{position:absolute;left:0;right:0;top:{YS+(22 if not TT else 16)}px;display:grid;grid-template-columns:1.72fr 1fr;gap:46px}}#bt h4{{padding-bottom:10px;border-bottom:1.5px solid {T['trait']}}}#bt h4{{font-size:18px;display:flex;align-items:center;gap:9px}}#bt h4 i{{width:11px;height:11px;border-radius:50%;display:block}}
#bt ul{{list-style:none}}#bt li{{display:flex;align-items:center;gap:8px;height:39px;font:500 18.5px/1 "IN";color:{T['ink']};border-bottom:1px solid {T['trait2']};white-space:nowrap}}#bt li b{{margin-left:auto;font-weight:700}}#bt li em{{font-style:normal;color:{T['doux']};font-size:16px}}
#stw{{display:none}}#stw h4{{font-size:18px}}#st{{position:relative;height:40px;margin-top:10px;border-bottom:1.5px solid {T['mute']}}}#st i{{position:absolute;bottom:0;width:2px;height:16px;background:{T['mute']}}}
#st b{{position:absolute;bottom:0;width:5px;height:38px;margin-left:-2px;background:{T['sA']};border-radius:3px 3px 0 0}}#st em{{position:absolute;bottom:-24px;font:500 15px/1 "IN";font-style:normal;color:{T['doux']}}}'''
    if TT: css+=f'''#tb.deux{{left:0;top:{YT}px;width:{W}px;display:grid;grid-template-columns:1fr 1fr;gap:46px}}.r{{height:36px}}.th .t1{{left:154px}}.r .n{{font-size:18px;top:9px}}.r .v{{left:198px;top:8px}}.r .b{{left:266px;width:64px;top:15px}}.r .c{{top:10px}}
#bt{{gap:38px}}#bt .r.q .v{{right:186px;width:110px}}#bt .r.q .b{{right:70px;width:104px}}#bt li{{height:36px;font-size:18px}}#cap{{left:0;right:0;text-align:center}}'''
    body=f'''<div class="hd"><h3>Son tournoi en dix critères</h3><div class="lg"><span>{pt(f1)}au-dessus</span><span>{pt(f2)}dans la moyenne</span><span>{pt(f3)}en dessous</span></div></div>
<svg id="rad" style="position:absolute;left:{RL}px;top:{RT}px;overflow:visible" width="500" height="{RH}" viewBox="0 0 500 {RH}">{g}</svg>
<div class="cap" id="cap" style="left:0;top:{Y0+522 if not TT else RT+RH+2}px">Radar : sa place parmi les {B['pluriel']}. Pointillé et petit trait : le {B['singulier']} médian.</div>
{TABLE}
<div id="sep"></div>
<div id="bt"><div><h4>Ce qu'il réussit</h4>{reu}</div>
<div><h4>Performances proches</h4><ul>{''.join(f'<li>{surn(p["player"])}<em>{pays(p["team"],13)}</em><b>{p["proche"]} %</b></li>' for p in F['proches'])}</ul></div></div>
<div id="stw"><h4>Sa note parmi les {B['effectif']} {B['pluriel']} du tournoi</h4><div id="st">{ticks}<b style="left:{(F['note']-lo)/(hi-lo)*100:.2f}%"></b><em style="left:0">{lo:.0f}</em><em style="right:0">{hi:.0f}</em></div></div>'''
    h=f'''<div class="phh">{photo(F['player_id'])}</div><div id="nm">{F['player']}</div><div id="m1">{F['poste']}, {pays(F['team'],19)}{f", {club}<span class='act'>club actuel</span>" if club else ''}</div><div id="m2">{F['minutes']} minutes en {F['matches']} matchs</div>
<div id="sc"><small>Note du tournoi, sur 100</small><b>{F['note']:.0f}</b><span>{ordi(F['rang'])} sur {B['effectif']} {B['pluriel']}</span></div>'''
    seuil=f"{B['effectif']} {B['pluriel']} ayant joué au moins {B['min_minutes']} minutes"
    note=(f"Parmi les {B['effectif']} {B['pluriel']} à {B['min_minutes']} minutes ou plus. Note : part des autres dépassés, en moyenne sur dix critères.","Données StatsBomb Open Data.") if TT else \
         (f"Rang : sa place parmi les {seuil}.",f"Note : la part des autres {B['pluriel']} qu'il dépasse, en moyenne sur les dix critères.<br>Données StatsBomb Open Data.")
    css+='#note{top:1250px;line-height:1.32}' if not TT else '#note{font-size:16px}'
    return page(CAN,h,body,note,css)

# ------------------------------------------------------------------ accroche et fin : quatre habillages
HAB={'A':dict(bg='radial-gradient(120% 70% at 30% 26%, #128F47 0%, #0B7A3B 30%, #064A25 62%, #04331A 100%)',t='#FFFFFF',s='#F6C41C',d='#FFF6D0',band=False,blancs=True),
     'B':dict(bg='#04331A',t='#FFFFFF',s='#F6C41C',d='#A9C2B3',band=False,blancs=True),
     'C':dict(bg='#F6C41C',t='#064A25',s='#064A25',d='rgba(14,26,19,.72)',band=False,blancs=False),
     'D':dict(bg='#FFFFFF',t='#0E1A13',s='#0B7A3B',d='#5E6B62',band=True,blancs=False)}
def plein(inner,css):
    h=HAB[TH_]
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}#c{{background:{h['bg']};color:{h['t']}}}#band{{position:absolute;left:0;right:0;top:0;height:124px;background:#F6C41C}}
#brand{{color:{h['t'] if not h['band'] else '#064A25'}}}{css}</style></head><body><div id="c">{'<div id="band"></div>' if h['band'] else ''}{inner}</div>
<script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>'''
def plan_accroche():
    h=HAB[TH_]
    css=f'''#l{{position:absolute;left:56px;top:{420 if not h['band'] else 450}px;font:800 96px/1.12 "IN";letter-spacing:-.03em;color:{h['t']}}}
#s{{position:absolute;left:52px;top:{720 if not h['band'] else 750}px;font:italic 900 236px/.9 "BC";text-transform:uppercase;color:{h['s']}}}'''
    inner='<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div></div><div id="l">Les Aigles<br>jouent.</div><div id="s">La data<br>parle.</div>'
    return plein(inner,css)
def plan_fin():
    h=HAB[TH_]; x,t=('logo_x_blanc.png','logo_tt_blanc.png') if h['blancs'] else ('logo_x.png','logo_tt.png')
    css=f'''#lo{{position:absolute;left:330px;top:{150 if not h['band'] else 190}px;width:420px;height:420px;border-radius:50%;overflow:hidden;background:#fff;box-shadow:0 0 0 6px #fff}}#lo img{{width:100%;height:100%;display:block}}
#w{{position:absolute;left:0;right:0;top:{640 if not h['band'] else 672}px;text-align:center;font:italic 400 168px/1 "BCS";color:{h['t'] if TH_!='D' else '#064A25'};white-space:nowrap}}#w i{{font-weight:600}}
#g{{position:absolute;left:0;right:0;top:{828 if not h['band'] else 858}px;text-align:center;font:500 40px/1 "IN";color:{h['d']}}}
.cp{{position:absolute;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:20px;font:700 44px/1 "IN";color:{h['t'] if TH_!='D' else '#064A25'}}}.cp img{{display:block}}'''
    inner=f'<div id="lo"><img src="logo-verte.png" alt=""></div><div id="w">Mali<i>Data</i>Foot</div><div id="g">La data du foot malien</div><div class="cp" style="top:{990 if not h["band"] else 1010}px"><img src="{x}" style="height:44px" alt="X">@MaliDataFoot</div><div class="cp" style="top:{1090 if not h["band"] else 1110}px"><img src="{t}" style="height:56px" alt="TikTok">@MaliDataFoot</div>'
    return plein(inner,css)

# ------------------------------------------------------------------ l'histoire des Aigles (martj42/international_results, CC0)
# Données : aigles_histoire.json (python aigles_export.py). Un match par ligne, vu du côté du Mali.
# Le résultat est celui de la fin du match : un match décidé aux tirs au but compte comme un nul.
CTX_H="Équipe du Mali, 1960-2026"; SRC_H="Données : résultats internationaux (martj42, CC0)."
def histoire():
    H_=json.load(open('aigles_histoire.json',encoding='utf-8')); return H_['matchs']
def couleurs_res(): return {'V':T['niv'][0],'N':T['niv'][1],'D':T['niv'][2]}
def leg_res():
    c=couleurs_res(); return ''.join(f'<span><i style="width:15px;height:15px;background:{c[k]}"></i>{n}</span>' for k,n in (('V','victoire'),('N','nul'),('D','défaite')))
def date_fr(iso):
    a,m,j=iso.split('-'); mois=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][int(m)-1]
    return f"{int(j)}{'er' if j=='01' else ''} {mois} {a}"
CSS_H=f'''.r .n{{left:0;top:10px;font:500 19px/1 "IN";color:{T['ink']}}}.r .c{{right:0;top:9px;font:700 20px/1 "IN";color:{T['ink']}}}.r .v1{{top:11px;text-align:right;font:400 18px/1 "IN";color:{T['doux']}}}
.th.e{{margin-top:14px;border-bottom:1.5px solid {T['trait']};padding-bottom:26px}}.ax{{font:500 16px IN;fill:{T['doux']}}}.axt{{font:600 16px IN;fill:{T['doux']}}}'''

def plan_histoire():
    """Un point par match, une colonne par année, empilés victoires, nuls puis défaites."""
    M=histoire(); ans=list(range(int(M[0]['date'][:4]),int(M[-1]['date'][:4])+1)); par=collections.defaultdict(list); c=couleurs_res()
    for m in M: par[m['annee']].append(m['resultat'])
    pas=W/len(ans); r=pas*.39; base=318; g=''
    for i,a in enumerate(ans):
        x=(i+.5)*pas
        for j,k in enumerate(sorted(par.get(a,[]),key='VND'.index)): g+=f'<circle cx="{x:.1f}" cy="{base-(j+.5)*pas:.1f}" r="{r:.2f}" fill="{c[k]}"/>'
    g+=f'<line x1="0" y1="{base+4}" x2="{W}" y2="{base+4}" stroke="{T["mute"]}" stroke-width="1.6"/>'
    for a in range(ans[0],ans[-1]+1,10):
        x=(a-ans[0]+.5)*pas; an='start' if a==ans[0] else 'middle'; tx=0 if a==ans[0] else x
        g+=f'<line x1="{x:.1f}" y1="{base+4}" x2="{x:.1f}" y2="{base+12}" stroke="{T["mute"]}" stroke-width="1.6"/><text x="{tx:.1f}" y="{base+34}" text-anchor="{an}" class="ax">{a}</text>'
    n=collections.Counter(m['resultat'] for m in M); top=max(ans,key=lambda a:(len(par.get(a,[])),-a)); vides=[a for a in ans if a not in par]
    rows=''.join(f'<div class="r"><span class="n"><i style="display:inline-block;width:14px;height:14px;border-radius:50%;background:{c[k]};margin-right:10px;vertical-align:-1px"></i>{l}</span><span class="c">{n[k]}</span></div>' for k,l in (('V','Victoires'),('N','Nuls'),('D','Défaites')))
    yb=Y0+30+base+60
    css=CSS_H+f'''#bt{{position:absolute;left:0;right:0;top:{yb}px;display:grid;grid-template-columns:1fr 1fr;gap:56px}}#bt p{{margin-top:14px;font:500 18.5px/1.45 "IN";color:{T['ink']}}}'''
    body=f'''<div class="hd"><h3>Chaque point est un match</h3><div class="lg">{leg_res()}</div></div>
<svg style="position:absolute;left:0;top:{Y0+30}px;overflow:visible" width="{W}" height="{base+40}" viewBox="0 0 {W} {base+40}">{g}</svg>
<div id="bt"><div><h4>Le bilan</h4><div class="th e"><span style="right:0">matchs</span></div>{rows}</div>
<div><h4>À lire</h4><p>Une colonne par année. L'année la plus chargée : {top}, avec {len(par[top])} matchs.{' Aucun match en '+', '.join(map(str,vides))+'.' if vides else ''}</p></div></div>'''
    h=hero('Tous les matchs des Aigles',f"{len(M)} matchs, amicaux compris",f"Du {date_fr(M[0]['date'])} au {date_fr(M[-1]['date'])}",('Matchs joués',str(len(M)),f"dont {n['V']} victoires"))
    return page(CTX_H,h,body,("Résultat à la fin du match : un match décidé aux tirs au but compte comme un nul.",SRC_H),css)

def plan_scores():
    """Les scores des Aigles : une grille buts du Mali x buts de l'adversaire, la taille du rond suit la fréquence."""
    M=histoire(); c=couleurs_res(); K=5; cap=lambda v:min(v,K)
    cnt=collections.Counter((cap(m['buts_pour']),cap(m['buts_contre'])) for m in M); mx=max(cnt.values())
    cs=66; gx,gy=70,46; g=''
    for i in range(K+1):
        lab='5 ou +' if i==K else str(i)
        g+=f'<text x="{gx+(i+.5)*cs:.0f}" y="{gy-14}" text-anchor="middle" class="ax">{lab}</text><text x="{gx-14}" y="{gy+(i+.5)*cs+6:.0f}" text-anchor="end" class="ax">{lab}</text>'
        for j in range(K+1):
            x,y=gx+(j+.5)*cs,gy+(i+.5)*cs; g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2" fill="{T["ligne"]}"/>'
            v=cnt.get((i,j),0)
            if v: k='V' if i>j else ('N' if i==j else 'D'); g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{max(3.5,math.sqrt(v/mx)*cs*.47):.1f}" fill="{c[k]}"/>'
    g+=f'<text x="{gx+(K+1)*cs/2:.0f}" y="{gy-40}" text-anchor="middle" class="axt">Buts de l\'adversaire</text>'
    g+=f'<text transform="translate({gx-52} {gy+(K+1)*cs/2:.0f}) rotate(-90)" text-anchor="middle" class="axt">Buts du Mali</text>'
    top=sorted(collections.Counter((m['buts_pour'],m['buts_contre']) for m in M).items(),key=lambda kv:(-kv[1],kv[0]))[:6]
    rows=''.join(f'<div class="r"><span class="n"><i style="display:inline-block;width:14px;height:14px;border-radius:50%;background:{c["V" if a>b else ("N" if a==b else "D")]};margin-right:10px;vertical-align:-1px"></i>{a}-{b}</span><span class="c">{v}</span></div>' for (a,b),v in top)
    GW=gx+(K+1)*cs
    css=CSS_H+f'''#ls{{position:absolute;left:{GW+70}px;right:0;top:{Y0+40}px}}'''
    body=f'''<div class="hd"><h3>Plus le rond est gros, plus le score est fréquent</h3><div class="lg">{leg_res()}</div></div>
<svg style="position:absolute;left:0;top:{Y0+70}px;overflow:visible" width="{GW}" height="{gy+(K+1)*cs}" viewBox="0 0 {GW} {gy+(K+1)*cs}">{g}</svg>
<div id="ls"><h4>Les scores les plus fréquents</h4><div class="th e"><span style="left:0">score du Mali</span><span style="right:0">matchs</span></div>{rows}</div>'''
    (a,b),v=top[0]
    h=hero('Les scores des Aigles',f"{len(M)} matchs depuis {M[0]['date'][:4]}",'Le score à la fin du match, vu du côté du Mali',('Le score le plus fréquent',f"{a}-{b}",f"{v} matchs sur {len(M)}"))
    return page(CTX_H,h,body,("Sous la diagonale : victoires ; sur la diagonale : nuls ; au-dessus : défaites.",SRC_H),css)

def plan_decennies():
    """Buts marqués et encaissés par match, décennie par décennie."""
    M=histoire(); dec=collections.defaultdict(lambda:[0,0,0])
    for m in M: d=dec[m['annee']//10*10]; d[0]+=1; d[1]+=m['buts_pour']; d[2]+=m['buts_contre']
    D_=sorted(dec); CH=300; ymax=2.0; G0=44; gw=(W-G0)/len(D_); bw=gw*.3; g=''; sy=lambda v:CH-v/ymax*CH
    for v in (0.5,1,1.5,2):
        g+=f'<line x1="{G0}" y1="{sy(v):.1f}" x2="{W}" y2="{sy(v):.1f}" stroke="{T["trait2"]}" stroke-width="1.2"/><text x="0" y="{sy(v)+6:.1f}" class="ax">{fr(v)}</text>'
    for i,d in enumerate(D_):
        n,bp,bc=dec[d]; x=G0+(i+.5)*gw
        for k,(v,col) in enumerate(((bp/n,T['sA']),(bc/n,T['sB']))):
            xb=x-bw-3 if k==0 else x+3; g+=f'<rect x="{xb:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{CH-sy(v):.1f}" rx="3" fill="{col}"/>'
        g+=f'<text x="{x:.1f}" y="{CH+28}" text-anchor="middle" class="ax">{"années "+str(d) if d>=2000 else "années "+str(d)[2:]}</text>'
    g+=f'<line x1="{G0}" y1="{CH}" x2="{W}" y2="{CH}" stroke="{T["mute"]}" stroke-width="1.6"/><text x="0" y="{CH+6}" class="ax">0</text>'
    rows=''.join(f'<div class="r"><span class="n">{"années "+str(d) if d>=2000 else "années "+str(d)[2:]}</span><span class="v1" style="right:250px;width:80px">{dec[d][0]}</span><span class="v1" style="right:120px;width:100px">{fr(dec[d][1]/dec[d][0],2)}</span><span class="c">{fr(dec[d][2]/dec[d][0],2)}</span></div>' for d in D_)
    css=CSS_H+f'''#bt{{position:absolute;left:0;right:0;top:{Y0+40+CH+70}px}}'''
    mk=lambda col:f'<i style="width:15px;height:15px;border-radius:3px;background:{col}"></i>'
    body=f'''<div class="hd"><h3>Buts par match, en moyenne</h3><div class="lg"><span>{mk(T['sA'])}marqués</span><span>{mk(T['sB'])}encaissés</span></div></div>
<svg style="position:absolute;left:0;top:{Y0+40}px;overflow:visible" width="{W}" height="{CH+40}" viewBox="0 0 {W} {CH+40}">{g}</svg>
<div id="bt"><div class="th e"><span style="right:250px;width:80px;text-align:right">matchs</span><span style="right:120px;width:100px;text-align:right">marqués</span><span style="right:0">encaissés</span></div>{rows}</div>'''
    d=D_[-1]; avant=[dec[x][2]/dec[x][0] for x in D_[:-1]]
    h=hero('Décennie par décennie',f"Buts marqués et encaissés par les Aigles",f"{len(M)} matchs, de {M[0]['date'][:4]} à {M[-1]['date'][:4]}",(f"Encaissés par match depuis {d}",fr(dec[d][2]/dec[d][0],2),f"contre {fr(min(avant),2)} à {fr(max(avant),2)} avant"))
    return page(CTX_H,h,body,(f"Années {d} : jusqu'au {date_fr(M[-1]['date'])}.",SRC_H),css)

COMPET={'Friendly':'Matchs amicaux','African Cup of Nations qualification':'Éliminatoires de la CAN','Amílcar Cabral Cup':'Coupe Amílcar Cabral',
        'African Cup of Nations':"Coupe d'Afrique des nations",'FIFA World Cup qualification':'Éliminatoires de la Coupe du monde'}
def plan_competitions():
    """Les matchs par compétition, en barres empilées victoires, nuls, défaites."""
    M=histoire(); c=couleurs_res(); par=collections.defaultdict(collections.Counter)
    for m in M: par[COMPET.get(m['competition'],'Autres tournois')][m['resultat']]+=1
    ordre=sorted(par,key=lambda k:(k=='Autres tournois',-sum(par[k].values()))); mx=max(sum(par[k].values()) for k in ordre); BW=470
    rows=''
    for k in ordre:
        n=sum(par[k].values()); seg=''.join(f'<i style="width:{par[k][r]/mx*BW:.1f}px;background:{c[r]}"></i>' for r in 'VND' if par[k][r])
        rows+=f'<div class="rb"><span class="n">{k}</span><span class="bar">{seg}</span><span class="c">{n}</span></div>'
    css=CSS_H+f'''#cp{{position:absolute;left:0;right:0;top:{Y0+44}px}}.rb{{position:relative;height:66px;border-bottom:1px solid {T['trait2']}}}.rb>span{{position:absolute}}
.rb .n{{left:0;top:23px;font:500 19px/1 "IN";color:{T['ink']};white-space:nowrap}}.rb .bar{{left:{W-BW-70}px;top:20px;height:26px;display:flex;gap:2px}}.rb .bar i{{display:block;height:100%}}.rb .bar i:first-child{{border-radius:4px 0 0 4px}}.rb .bar i:last-child{{border-radius:0 4px 4px 0}}
.rb .c{{right:0;top:22px;font:700 20px/1 "IN";color:{T['ink']}}}.th.e{{margin-top:0}}'''
    body=f'''<div class="hd"><h3>Combien de matchs, et avec quels résultats</h3><div class="lg">{leg_res()}</div></div>
<div id="cp"><div class="th e"><span style="right:0">matchs</span></div>{rows}</div>'''
    can=par["Coupe d'Afrique des nations"]; ncan=sum(can.values())
    h=hero('Les compétitions',f"{len(M)} matchs des Aigles, compétition par compétition",f"De {M[0]['date'][:4]} à {M[-1]['date'][:4]}",("Matchs en phase finale de CAN",str(ncan),f"dont {can['V']} victoires"))
    return page(CTX_H,h,body,("Autres tournois : Jeux africains, tournoi du Burkina Faso, Jeux de l'amitié africaine.",SRC_H),css)

# ------------------------------------------------------------------ la défense des Aigles depuis 2020 (malidata/analyses.py)
# Données : ../outputs/analyses/defense_aigles.json. Quatre mises en scène du même message (13 octobre 2026).
def defense(): return json.load(open('../outputs/analyses/defense_aigles.json',encoding='utf-8'))
CTX_DEF="Équipe du Mali, matchs officiels"
NOTE_DEF=("Matchs officiels : CAN et éliminatoires. Rang : classement Elo du jour du match.","Données : résultats internationaux (martj42, CC0).")
def hero_def(D):
    r,n=D['reference'],D['depuis_2020']
    return hero('La défense des Aigles','Buts encaissés en match officiel','CAN et éliminatoires' if TT else 'CAN et éliminatoires de la CAN et de la Coupe du monde',
                ('Par match, depuis 2020',fr(n['par_match'],2),f"contre {fr(r['par_match'],2)} de 2000 à 2019"))
def leg_def():
    sq=lambda c,plein=True:f'<i style="width:15px;height:15px;border-radius:3px;{"background:"+c if plein else "box-shadow:inset 0 0 0 2px "+c}"></i>'
    return f'<span>{sq(T["mute"])}2000-2019</span><span>{sq(T["sA"])}depuis 2020</span>'
CSS_DEF=lambda: f'''.r .n{{left:0;top:10px;font:500 19px/1 "IN";color:{T['ink']}}}.r .c{{top:9px;width:120px;text-align:right;font:700 20px/1 "IN";color:{T['ink']}}}
.r .v1{{top:11px;width:120px;text-align:right;font:400 18px/1 "IN";color:{T['doux']}}}.r.tot{{border-bottom:none}}.r.tot .n{{font-weight:700}}
.th.e{{margin-top:14px;border-bottom:1.5px solid {T['trait']};padding-bottom:26px}}.th.g{{height:16px;margin-top:12px}}.th.g span{{font-weight:600;color:{T['ink']}}}
.ax{{font:500 16px IN;fill:{T['doux']}}}.axt{{font:600 16px IN;fill:{T['doux']}}}
#lire{{position:absolute;left:0;right:0}}#lire p{{margin-top:12px;font:500 18.5px/1.45 "IN";color:{T['ink']}}}'''
def bilan_def(D, top):
    """Le bilan des deux périodes, en tableau (les chiffres sont là, pas sur le graphique)."""
    r,n=D['reference'],D['depuis_2020']; pc=lambda b:f"{b['sans_encaisser']} ({round(100*b['sans_encaisser']/b['matchs'])} %)"
    rows=[('Matchs',r['matchs'],n['matchs']),('Buts encaissés',r['buts_encaisses'],n['buts_encaisses']),('Par match',fr(r['par_match'],2),fr(n['par_match'],2)),
          ('Matchs sans encaisser',pc(r),pc(n)),("Rang médian de l'adversaire",f"{int(r['rang_median_adversaire'])}e",f"{int(n['rang_median_adversaire'])}e")]
    li=''.join(f'<div class="r"><span class="n">{a}</span><span class="v1" style="right:170px;width:150px">{b}</span><span class="c" style="right:0;width:150px">{c}</span></div>' for a,b,c in rows)
    return f'''<div style="position:absolute;left:0;right:0;top:{top}px"><h4>Le bilan</h4><div class="th e"><span style="right:170px;width:150px;text-align:right">2000-2019</span><span style="right:0;width:150px;text-align:right">depuis 2020</span></div>{li}</div>'''

def plan_defense():
    """1A : barres par niveau d'adversaire, puis le tableau par niveau."""
    D=defense(); N=D['niveaux']; ref,rec=D['reference'],D['depuis_2020']
    CH=290; ymax=1.5; x0=58; gw=(W-x0)/len(N); bw=min(78,gw*.26); sy=lambda v:CH-v/ymax*CH; g=''
    for v in (0.5,1,1.5):
        g+=f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{W}" y2="{sy(v):.1f}" stroke="{T["trait2"]}" stroke-width="1.4"/><text x="0" y="{sy(v)+6:.1f}" class="ax">{fr(v)}</text>'
    g+=f'<text x="0" y="{CH+6}" class="ax">0</text>'
    for i,n in enumerate(N):
        x=x0+(i+.5)*gw
        for k,(v,c) in enumerate(((n['reference']['par_match'],T['mute']),(n['depuis_2020']['par_match'],T['sA']))):
            xb=x-bw-5 if k==0 else x+5; g+=f'<rect x="{xb:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{CH-sy(v):.1f}" rx="4" fill="{c}"/>'
        g+=f'<text x="{x:.1f}" y="{CH+30}" text-anchor="middle" class="axt">{n["niveau"]}</text>'
    g+=f'<text x="{x0+(W-x0)/2:.0f}" y="{CH+58}" text-anchor="middle" class="ax">Rang Elo de l\'adversaire le jour du match</text>'
    g+=f'<line x1="{x0}" y1="{CH}" x2="{W}" y2="{CH}" stroke="{T["mute"]}" stroke-width="2"/>'
    top=Y0+44; yt=top+CH+84
    cols=lambda a,b,c,d:f'<span class="v1" style="right:390px">{a}</span><span class="c" style="right:270px">{b}</span><span class="v1" style="right:120px">{c}</span><span class="c" style="right:0">{d}</span>'
    li=''.join(f'<div class="r"><span class="n">{n["niveau"]}</span>{cols(n["reference"]["matchs"],fr(n["reference"]["par_match"],2),n["depuis_2020"]["matchs"],fr(n["depuis_2020"]["par_match"],2))}</div>' for n in N)
    li+=f'<div class="r tot"><span class="n">Tous les adversaires</span>{cols(ref["matchs"],fr(ref["par_match"],2),rec["matchs"],fr(rec["par_match"],2))}</div>'
    th=lambda: '<span style="right:390px;width:120px;text-align:right">matchs</span><span style="right:270px;width:120px;text-align:right">par match</span><span style="right:120px;width:120px;text-align:right">matchs</span><span style="right:0;width:120px;text-align:right">par match</span>'
    nt=[n['depuis_2020']['matchs'] for n in N][0]
    css=CSS_DEF()+f'''#tb{{position:absolute;left:0;right:0;top:{yt}px}}'''
    body=f'''<div class="hd"><h3>Selon le niveau de l'adversaire</h3><div class="lg">{leg_def()}</div></div>
<svg style="position:absolute;left:0;top:{top}px;overflow:visible" width="{W}" height="{CH+40}" viewBox="0 0 {W} {CH+40}">{g}</svg>
<div id="tb"><div class="th g"><span style="right:270px;width:240px;text-align:right">2000-2019</span><span style="right:0;width:240px;text-align:right">depuis 2020</span></div>
<div class="th e" style="margin-top:4px">{th()}</div>{li}</div>
<div id="lire" style="top:{yt+276}px"><h4>À lire</h4><p>Les adversaires ne sont pas plus faibles : leur rang Elo médian est {int(ref["rang_median_adversaire"])}e de 2000 à 2019, {int(rec["rang_median_adversaire"])}e depuis 2020. Contre le top 60, l'échantillon reste petit : {nt} matchs depuis 2020.</p></div>'''
    return page(CTX_DEF,hero_def(D),body,NOTE_DEF,css)

def plan_defense_attendu():
    """1B : ce que le Mali d'avant aurait encaissé face aux mêmes adversaires, contre ce qu'il a encaissé."""
    D=defense(); A=D['a_adversaires_egaux']; att,reel=A['buts_attendus'],A['buts_reels']; n=D['depuis_2020']['matchs']
    BW=W-190; sx=lambda v:v/max(att,reel)*BW; top=Y0+70; g=''
    for i,(lab,v,c) in enumerate(((f"Le Mali de 2000-2019 aurait encaissé",att,T['mute']),(f"Le Mali depuis 2020 a encaissé",reel,T['sA']))):
        y=top+i*150
        g+=f'<div style="position:absolute;left:0;top:{y}px;font:600 20px/1 IN;color:{T["ink"]}">{lab}</div>'
        g+=f'<div style="position:absolute;left:0;top:{y+34}px;width:{sx(v):.0f}px;height:62px;border-radius:6px;background:{c}"></div>'
        g+=f'<div style="position:absolute;left:{sx(v)+18:.0f}px;top:{y+30}px;font:italic 900 72px/1 BC;color:{T["titre"]};white-space:nowrap">{round(v)}<small style="font:600 22px IN;color:{T["doux"]};margin-left:10px;font-style:normal">buts</small></div>'
    css=CSS_DEF()
    body=f'''<div class="hd"><h3>Face aux mêmes adversaires, aux mêmes endroits</h3></div>{g}
<div class="cap" style="left:0;top:{top+300}px">Sur les {n} matchs officiels joués depuis le 1er janvier 2020</div>{bilan_def(D,top+370)}'''
    note=("Aurait encaissé : selon la force de l'adversaire (Elo) et le lieu, d'après 2000-2019.",NOTE_DEF[1])
    return page(CTX_DEF,hero_def(D),body,note,css)

def plan_defense_matchs():
    """1C : chaque match est un point, placé selon le rang de l'adversaire et les buts encaissés."""
    D=defense(); M=D['matchs']; ymax=max(m['buts_contre'] for m in M); rmax=max(m['rang_adversaire'] for m in M)
    x0=40; CW=W-x0-10; CH=330; top=Y0+44; lane=CH/(ymax+1); sx=lambda r:x0+(r-1)/(rmax-1)*CW; sy=lambda b,k:top*0+CH-(b+.5)*lane+(-.17 if k else .17)*lane; g=''
    for b in range(ymax+1):
        y=CH-(b+.5)*lane; g+=f'<line x1="{x0}" y1="{y+lane/2:.1f}" x2="{W}" y2="{y+lane/2:.1f}" stroke="{T["trait2"]}" stroke-width="1.2"/><text x="0" y="{y+6:.1f}" class="ax">{b}</text>'
    for r in (1,50,100,150,200):
        if r<=rmax: g+=f'<text x="{sx(r):.1f}" y="{CH+26}" text-anchor="middle" class="ax">{"1er" if r == 1 else str(r) + "e"}</text>'
    for k in (0,1):
        for m in M:
            if (m['periode']=='depuis_2020')!=bool(k): continue
            x,y=sx(m['rang_adversaire']),sy(m['buts_contre'],k)
            g+=(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{T["sA"]}" stroke="{T["fond"]}" stroke-width="1.5"/>' if k else
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" stroke="{T["mute"]}" stroke-width="1.8"/>')
    g+=f'<text x="{x0+CW/2:.0f}" y="{CH+54}" text-anchor="middle" class="axt">Rang Elo de l\'adversaire le jour du match (à gauche, les plus forts)</text>'
    g+=f'<text transform="translate(-26 {CH/2:.0f}) rotate(-90)" text-anchor="middle" class="axt">Buts encaissés</text>'
    lg=f'<span><i style="width:14px;height:14px;box-shadow:inset 0 0 0 2px {T["mute"]}"></i>2000-2019</span><span><i style="width:14px;height:14px;background:{T["sA"]}"></i>depuis 2020</span>'
    css=CSS_DEF()
    body=f'''<div class="hd"><h3>Chaque rond est un match officiel</h3><div class="lg">{lg}</div></div>
<svg style="position:absolute;left:26px;top:{top}px;overflow:visible" width="{W-26}" height="{CH+60}" viewBox="0 0 {W-26} {CH+60}">{g}</svg>{bilan_def(D,top+CH+96)}'''
    return page(CTX_DEF,hero_def(D),body,NOTE_DEF,css)

def plan_defense_sans():
    """1D : chaque case est un match ; pleine quand le Mali n'a pas encaissé de but."""
    D=defense(); M=D['matchs']; cols=20; pas=W/cols; cote=pas-8; top=Y0+44; g=''; y=top
    for per,lab in (('reference','2000-2019'),('depuis_2020','Depuis 2020')):
        L=[m for m in M if m['periode']==per]; b=D[per]; ns=b['sans_encaisser']
        g+=f'<div style="position:absolute;left:0;top:{y}px;font:700 20px/1 IN;color:{T["ink"]}">{lab}<span style="font-weight:500;color:{T["doux"]};margin-left:12px">{ns} matchs sans encaisser sur {b["matchs"]} ({round(100*ns/b["matchs"])} %)</span></div>'
        y+=36
        for i,m in enumerate(L):
            cx,cy=(i%cols)*pas,y+(i//cols)*pas; plein=m['buts_contre']==0; c=T['sA'] if per=='depuis_2020' else T['mute']
            g+=f'<i style="position:absolute;left:{cx:.1f}px;top:{cy:.1f}px;width:{cote:.1f}px;height:{cote:.1f}px;border-radius:5px;{"background:"+c if plein else "box-shadow:inset 0 0 0 2px "+T["trait"]}"></i>'
        y+=math.ceil(len(L)/cols)*pas+30
    css=CSS_DEF()
    body=f'''<div class="hd"><h3>Chaque case est un match ; pleine, le Mali n'a pas encaissé</h3></div>{g}{bilan_def(D,y+6)}'''
    return page(CTX_DEF,hero_def(D),body,NOTE_DEF,css)

# ------------------------------------------------------------------ le classement FIFA et le Rwanda (malidata/analyses.py, fifa.py)
def fifa_d(): return json.load(open('../outputs/analyses/fifa_rwanda.json',encoding='utf-8'))
CTX_F="Éliminatoires de la CAN 2027, novembre 2026"
NOTE_F=("Points gagnés = 25 × (résultat − résultat attendu). Points du 7 octobre 2026.","Données : FIFA. Calcul MaliDataFoot.")
RES_F={'V':'victoire','N':'nul','D':'défaite'}
sg=lambda v,d=1:('+' if v>=0.05 else ('−' if v<=-0.05 else ''))+fr(abs(v),d)
def hero_f(F):
    m,r=F['points_avant']['Mali'],F['points_avant']['Rwanda']; vv=next(s for s in F['deux_matchs'] if s['resultats']=='VV')
    return hero('Le classement FIFA',"Les deux matchs contre le Rwanda",f"Avant : Mali {fr(m,2)} points, Rwanda {fr(r,2)}",
                ('Avec deux victoires',sg(vv['ecart']),'le seul cas qui rapporte'))
def lire_f(F,top):
    u=F['un_match']; a=round(100*F['attendu_mali'])
    return f'''<div id="lire" style="top:{top}px"><h4>À lire</h4><p>Le calcul de la FIFA attend une victoire du Mali : son « résultat attendu » est de {a} %. Une victoire ne rapporte donc que {fr(u['V'],1)} points, un nul en coûte {fr(-u['N'],1)} et une défaite {fr(-u['D'],1)}.</p></div>'''
def col_f(v):
    return T['niv'][0] if v>0 else T['niv'][2]

def plan_fifa():
    """2-1 : les neuf scénarios des deux matchs, en grille aller × retour."""
    F=fifa_d(); S={s['resultats']:s['ecart'] for s in F['deux_matchs']}; mx=max(abs(v) for v in S.values())
    x0=200; cw=(W-x0)/3; ch=128; top=Y0+100; g=''
    for j,r in enumerate('VND'):
        g+=f'<div style="position:absolute;left:{x0+j*cw:.0f}px;top:{top-34}px;width:{cw:.0f}px;text-align:center;font:600 18px/1 IN;color:{T["doux"]}">{RES_F[r]}</div>'
    g+=f'<div style="position:absolute;left:{x0}px;top:{top-68}px;width:{W-x0}px;text-align:center;font:700 19px/1 IN;color:{T["ink"]}">Match retour, à Kigali</div>'
    g+=f'<div style="position:absolute;left:0;top:{top+12-34}px;font:700 19px/1 IN;color:{T["ink"]}">Match aller, à Bamako</div>'
    for i,a in enumerate('VND'):
        y=top+12+i*(ch+10)
        g+=f'<div style="position:absolute;left:0;top:{y+ch/2-10:.0f}px;font:600 18px/1 IN;color:{T["doux"]}">{RES_F[a]}</div>'
        for j,b in enumerate('VND'):
            v=S[a+b]; ms=max(abs(w) for w in S.values() if (w>0)==(v>0)); op=.25+.75*abs(v)/ms; x=x0+j*cw
            g+=(f'<div style="position:absolute;left:{x+5:.0f}px;top:{y}px;width:{cw-10:.0f}px;height:{ch}px;border-radius:10px;background:{col_f(v)};opacity:{op:.2f}"></div>'
                f'<div style="position:absolute;left:{x+5:.0f}px;top:{y+ch/2-26:.0f}px;width:{cw-10:.0f}px;text-align:center;font:italic 900 52px/1 BC;color:{T["fond"] if op>.55 else T["ink"]}">{sg(v)}</div>')
    yl=top+12+3*(ch+10)+24
    css=CSS_DEF()
    lg=f'<span><i style="width:15px;height:15px;border-radius:3px;background:{T["niv"][0]}"></i>le Mali gagne des points</span><span><i style="width:15px;height:15px;border-radius:3px;background:{T["niv"][2]}"></i>il en perd</span>'
    body=f'''<div class="hd"><h3>Les deux matchs, tous les scénarios</h3><div class="lg">{lg}</div></div>{g}{lire_f(F,yl)}'''
    return page(CTX_F,hero_f(F),body,NOTE_F,css)

def plan_fifa_un():
    """2-2 : un seul match, trois résultats, des barres de part et d'autre de zéro."""
    F=fifa_d(); u=F['un_match']; x0=60; CH=330; top=Y0+60; z=top+120; k=180/20; g=''; gw=(W-x0)/3
    g+=f'<div style="position:absolute;left:{x0}px;right:0;top:{z}px;height:2px;background:{T["mute"]}"></div>'
    for i,r in enumerate('VND'):
        v=u[r]; h=abs(v)*k; x=x0+(i+.5)*gw-55; y=z-h if v>0 else z+2
        g+=f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:110px;height:{h:.0f}px;border-radius:5px;background:{col_f(v)}"></div>'
        ly=y-50 if v>0 else y+h+8
        g+=f'<div style="position:absolute;left:{x-40:.0f}px;width:190px;top:{ly:.0f}px;text-align:center;font:italic 900 46px/1 BC;color:{T["titre"]}">{sg(v,2)}</div>'
        g+=f'<div style="position:absolute;left:{x-40:.0f}px;width:190px;top:{z-36 if v<0 else z+12:.0f}px;text-align:center;font:600 19px/1 IN;color:{T["ink"]}">{RES_F[r].capitalize()}</div>'
    S={s['resultats']:s['ecart'] for s in F['deux_matchs']}
    rows=[('Deux victoires','VV'),('Une victoire et un nul',None),('Deux nuls','NN'),('Deux défaites','DD')]
    val=lambda c: sg(S[c],1) if c else f"{sg(S['VN'],1)} ou {sg(S['NV'],1)}"
    li=''.join(f'<div class="r"><span class="n">{a}</span><span class="c" style="right:0;width:220px">{val(c)}</span></div>' for a,c in rows)
    css=CSS_DEF()
    yt=z+250
    body=f'''<div class="hd"><h3>Les points d'un seul match contre le Rwanda</h3></div>{g}
<div style="position:absolute;left:0;right:0;top:{yt}px"><h4>Sur les deux matchs</h4><div class="th e"><span style="right:0">points pour le Mali</span></div>{li}</div>{lire_f(F,yt+230)}'''
    return page(CTX_F,hero_f(F),body,NOTE_F,css)

def plan_fifa_courbe():
    """2-3 : ce que rapporte un match d'éliminatoires selon la force de l'adversaire ; le Rwanda placé sur la courbe."""
    F=fifa_d(); m=F['points_avant']['Mali']; rw=F['points_avant']['Rwanda']; I=F['importance']
    att=lambda p:1/(10**(-(m-p)/600)+1); x0=60; CW=W-x0-20; CH=360; top=Y0+60; lo,hi=1000,1900; ymin,ymax=-25,25
    sx=lambda p:x0+(p-lo)/(hi-lo)*CW; sy=lambda v:CH*(ymax-v)/(ymax-ymin); g=''
    for v in (-20,-10,0,10,20):
        g+=f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+CW}" y2="{sy(v):.1f}" stroke="{T["mute"] if v==0 else T["trait2"]}" stroke-width="{2 if v==0 else 1.2}"/><text x="0" y="{sy(v)+6:.1f}" class="ax">{sg(v,0) if v else "0"}</text>'
    for p in (1000,1200,1400,1600,1800):
        g+=f'<text x="{sx(p):.1f}" y="{CH+26}" text-anchor="middle" class="ax">{p}</text>'
    for r,c,da in (('V',T['niv'][0],''),('N',T['niv'][1],''),('D',T['niv'][2],'')):
        w=RESULT_W[r]; d='M'+'L'.join(f'{sx(p):.1f} {sy(I*(w-att(p))):.1f}' for p in range(lo,hi+1,10))
        g+=f'<path d="{d}" fill="none" stroke="{c}" stroke-width="4" stroke-linejoin="round"/>'
        g+=f'<text x="{x0+CW+8}" y="{sy(I*(w-att(hi)))+6:.1f}" class="axt">{RES_F[r]}</text>'
    for p,lab in ((rw,'Rwanda'),(m,'même niveau que le Mali')):
        g+=f'<line x1="{sx(p):.1f}" y1="0" x2="{sx(p):.1f}" y2="{CH}" stroke="{T["ink"]}" stroke-width="1.5" stroke-dasharray="4 5"/><text x="{sx(p)+8:.1f}" y="18" class="axt" style="fill:{T["ink"]}">{lab}</text>'
        for r in 'VND':
            v=I*(RESULT_W[r]-att(p)); g+=f'<circle cx="{sx(p):.1f}" cy="{sy(v):.1f}" r="7" fill="{T["fond"]}" stroke="{T["ink"]}" stroke-width="2.5"/>'
    g+=f'<text x="{x0+CW/2:.0f}" y="{CH+54}" text-anchor="middle" class="axt">Points FIFA de l\'adversaire</text>'
    css=CSS_DEF()
    body=f'''<div class="hd"><h3>Les points d'un match d'éliminatoires, selon l'adversaire</h3></div>
<svg style="position:absolute;left:0;top:{top}px;overflow:visible" width="{W-60}" height="{CH+60}" viewBox="0 0 {W-60} {CH+60}">{g}</svg>{lire_f(F,top+CH+90)}'''
    return page(CTX_F,hero_f(F),body,NOTE_F,css)
RESULT_W={'V':1.0,'N':0.5,'D':0.0}

def plan_fifa_liste():
    """2-4 : les neuf scénarios, du meilleur au pire, en barres de part et d'autre de zéro."""
    F=fifa_d(); S=sorted(F['deux_matchs'],key=lambda s:-s['ecart']); mx=max(abs(s['ecart']) for s in S)
    lab=lambda c:f"{RES_F[c[0]].capitalize()} à Bamako, {RES_F[c[1]]} à Kigali"
    pos=max(s['ecart'] for s in S); neg=-min(s['ecart'] for s in S); k=(W-360-80)/(pos+neg); zx=360+neg*k; kneg=k; top=Y0+56; rh=50; g=''
    for i,s in enumerate(S):
        y=top+i*rh; v=s['ecart']
        g+=f'<div style="position:absolute;left:0;top:{y+12}px;font:500 18px/1 IN;color:{T["ink"]};white-space:nowrap">{lab(s["resultats"])}</div>'
        if v>0: g+=f'<div style="position:absolute;left:{zx:.0f}px;top:{y+8}px;width:{v*k:.0f}px;height:26px;border-radius:0 5px 5px 0;background:{col_f(v)}"></div><div style="position:absolute;left:{zx+v*k+10:.0f}px;top:{y+9}px;font:700 20px/1 IN;color:{T["ink"]}">{sg(v)}</div>'
        else: g+=f'<div style="position:absolute;left:{zx-(-v)*kneg:.0f}px;top:{y+8}px;width:{-v*kneg:.0f}px;height:26px;border-radius:5px 0 0 5px;background:{col_f(v)}"></div><div style="position:absolute;left:{zx+10:.0f}px;top:{y+9}px;font:700 20px/1 IN;color:{T["ink"]}">{sg(v)}</div>'
    g+=f'<div style="position:absolute;left:{zx-1:.0f}px;top:{top}px;width:2px;height:{9*rh}px;background:{T["mute"]}"></div>'
    css=CSS_DEF()
    body=f'''<div class="hd"><h3>Les neuf scénarios, du meilleur au pire</h3></div>{g}{lire_f(F,top+9*rh+30)}'''
    return page(CTX_F,hero_f(F),body,NOTE_F,css)

# ------------------------------------------------------------------ versions épurées (13 octobre 2026, critique : trop de texte,
# graphique + tableau + paragraphe qui redisent la même chose, cadres à moitié vides). Règle : un graphique par image, en grand,
# le message écrit sur le graphique, pas de tableau ni de paragraphe ; le détail va dans le texte du post.
def _barres_h(items, top, larg, ep, gap, vmax, unite, x0=0):
    """Grandes barres horizontales : (étiquette au-dessus, valeur, couleur). La valeur est écrite au bout de la barre."""
    g=''
    for i,(lab,v,c) in enumerate(items):
        y=top+i*(ep+gap)
        g+=f'<div style="position:absolute;left:{x0}px;top:{y}px;font:600 21px/1 IN;color:{T["ink"]}">{lab}</div>'
        g+=f'<div style="position:absolute;left:{x0}px;top:{y+34}px;width:{v/vmax*larg:.0f}px;height:{ep}px;border-radius:8px;background:{c}"></div>'
        g+=f'<div style="position:absolute;left:{x0+v/vmax*larg+20:.0f}px;top:{y+34+ep/2-46:.0f}px;font:italic 900 92px/1 BC;color:{T["titre"]};white-space:nowrap">{round(v)}<small style="font:600 24px IN;font-style:normal;color:{T["doux"]};margin-left:10px">{unite}</small></div>'
    return g

def plan_defense2():
    """Post 1, image principale : ce que le Mali d'avant aurait encaissé contre ce qu'il a encaissé, puis les trois niveaux."""
    D=defense(); A=D['a_adversaires_egaux']; N=D['niveaux']; n=D['depuis_2020']['matchs']
    top=Y0+56; ep=86; gap=74; larg=W-260
    g=_barres_h([("Le Mali de 2000-2019 aurait encaissé",A['buts_attendus'],T['mute']),("Le Mali depuis 2020 a encaissé",A['buts_reels'],T['sA'])],top,larg,ep,gap,A['buts_attendus'],'buts')
    yb=top+34+ep+gap+ep/2
    g+=(f'<div style="position:absolute;right:0;top:{yb-34:.0f}px;text-align:right;font:italic 900 52px/1 BC;color:{T["titre"]};text-transform:uppercase;white-space:nowrap">'
        f'Deux fois moins</div><div style="position:absolute;right:0;top:{yb+24:.0f}px;text-align:right;font:500 18px/1.3 IN;color:{T["doux"]};white-space:nowrap">sur les {n} matchs officiels depuis 2020</div>')
    # les trois niveaux d'adversaire, en petits groupes de barres
    y2=top+2*(ep+gap)+40; h2=H-y2-70; gw=W/3; bw=min(70,gw*.22); ymax=1.5
    g+=f'<div style="position:absolute;left:0;right:0;top:{y2}px;border-top:1.5px solid {T["trait"]}"></div>'
    g+=f'<div style="position:absolute;left:0;top:{y2+24}px;font:700 21px/1 IN;color:{T["ink"]}">Et c\'est vrai à chaque niveau d\'adversaire</div><div class="lg" style="position:absolute;right:0;top:{y2+24}px">{leg_def()}</div>'
    hb=h2-96; base=y2+70+hb
    for i,nv in enumerate(N):
        x=(i+.5)*gw
        for k,(v,c) in enumerate(((nv['reference']['par_match'],T['mute']),(nv['depuis_2020']['par_match'],T['sA']))):
            hh=v/ymax*hb; g+=f'<div style="position:absolute;left:{x-bw-4 if k==0 else x+4:.0f}px;top:{base-hh:.0f}px;width:{bw:.0f}px;height:{hh:.0f}px;border-radius:5px 5px 0 0;background:{c}"></div>'
        g+=f'<div style="position:absolute;left:{x-gw/2:.0f}px;width:{gw:.0f}px;top:{base+12:.0f}px;text-align:center;font:600 18px/1.25 IN;color:{T["ink"]}">{nv["niveau"]}<br><span style="font-weight:500;color:{T["doux"]}">{nv["depuis_2020"]["matchs"]} matchs depuis 2020</span></div>'
    g+=f'<div style="position:absolute;left:0;right:0;top:{base}px;height:2px;background:{T["mute"]}"></div>'
    note=("Aurait encaissé : selon la force de l'adversaire (classement Elo) et le lieu.","En bas : buts encaissés par match. Données : résultats internationaux (martj42).")
    return page(CTX_DEF,hero_def(D),f'<div class="hd"><h3>Face aux mêmes adversaires, aux mêmes endroits</h3></div>{g}',note,CSS_DEF())

def plan_defense2_sans():
    """Post 1, autre image : les matchs sans encaisser, une case par match, en grand."""
    D=defense(); M=D['matchs']; top=Y0+70; g=''; y=top
    haut=lambda c:2*110+(math.ceil(120/c)+math.ceil(50/c))*W/c      # hauteur occupée avec c colonnes : la plus grande grille qui tient
    cols=min((c for c in range(10,25) if top+haut(c)<=H-40), key=lambda c:H-40-top-haut(c)); pas=W/cols; cote=pas-8
    for per,lab in (('reference','De 2000 à 2019'),('depuis_2020','Depuis 2020')):
        L=[m for m in M if m['periode']==per]; b=D[per]; ns=b['sans_encaisser']; pc=round(100*ns/b['matchs']); c=T['sA'] if per=='depuis_2020' else T['mute']
        g+=f'<div style="position:absolute;left:0;top:{y}px;font:700 22px/1 IN;color:{T["ink"]}">{lab}</div><div style="position:absolute;right:0;top:{y-26}px;font:italic 900 64px/1 BC;color:{T["titre"] if per=="depuis_2020" else T["doux"]}">{pc} %</div>'
        g+=f'<div style="position:absolute;left:0;top:{y+30}px;font:500 18px/1 IN;color:{T["doux"]}">{ns} matchs sans encaisser sur {b["matchs"]}</div>'
        y+=70
        for i,m in enumerate(L):
            cx,cy=(i%cols)*pas,y+(i//cols)*pas; plein=m['buts_contre']==0
            g+=f'<i style="position:absolute;left:{cx:.1f}px;top:{cy:.1f}px;width:{cote:.1f}px;height:{cote:.1f}px;border-radius:6px;{"background:"+c if plein else "box-shadow:inset 0 0 0 2px "+T["trait"]}"></i>'
        y+=math.ceil(len(L)/cols)*pas+40
    return page(CTX_DEF,hero_def(D),f'<div class="hd"><h3>Chaque case est un match officiel. Pleine : le Mali n\'a pas encaissé.</h3></div>{g}',NOTE_DEF,CSS_DEF())

def plan_defense2_niveaux():
    """Post 1, image de preuve : les trois niveaux d'adversaire en grand."""
    D=defense(); N=D['niveaux']; top=Y0+64; x0=56; CH=H-top-150; ymax=1.5; gw=(W-x0)/3; bw=min(96,gw*.28); sy=lambda v:CH-v/ymax*CH; g=''
    for v in (0.5,1,1.5):
        g+=f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{W}" y2="{sy(v):.1f}" stroke="{T["trait2"]}" stroke-width="1.4"/><text x="0" y="{sy(v)+6:.1f}" class="ax">{fr(v)}</text>'
    g+=f'<text x="0" y="{CH+6}" class="ax">0</text>'
    for i,nv in enumerate(N):
        x=x0+(i+.5)*gw
        for k,(v,c) in enumerate(((nv['reference']['par_match'],T['mute']),(nv['depuis_2020']['par_match'],T['sA']))):
            g+=f'<rect x="{x-bw-6 if k==0 else x+6:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{CH-sy(v):.1f}" rx="5" fill="{c}"/>'
        g+=f'<text x="{x:.1f}" y="{CH+34}" text-anchor="middle" style="font:600 19px IN;fill:{T["ink"]}">{nv["niveau"]}</text><text x="{x:.1f}" y="{CH+60}" text-anchor="middle" class="ax">{nv["reference"]["matchs"]} et {nv["depuis_2020"]["matchs"]} matchs</text>'
    g+=f'<line x1="{x0}" y1="{CH}" x2="{W}" y2="{CH}" stroke="{T["mute"]}" stroke-width="2"/>'
    body=f'''<div class="hd"><h3>Par match, selon le niveau de l'adversaire</h3><div class="lg">{leg_def()}</div></div>
<svg style="position:absolute;left:0;top:{top}px;overflow:visible" width="{W}" height="{CH+70}" viewBox="0 0 {W} {CH+70}">{g}</svg>'''
    return page(CTX_DEF,hero_def(D),body,("Niveau : rang de l'adversaire au classement Elo le jour du match.",NOTE_DEF[1]),CSS_DEF())

def hero_f2(F):
    m,r=F['points_avant']['Mali'],F['points_avant']['Rwanda']; vv=next(s for s in F['deux_matchs'] if s['resultats']=='VV')
    return hero('Le classement FIFA',"Contre le Rwanda, il faut gagner deux fois",f"Avant les matchs : Mali {fr(m,2)} points, Rwanda {fr(r,2)}",
                ('Avec deux victoires',sg(vv['ecart']),'points pour le Mali'))
def classe_f(v):
    """Trois classes franches, dans le code des niveaux de la DA : gagne, perd un peu, perd beaucoup."""
    rouge,fonce=(('#FF7A6B','#D4252A') if T['blancs'] else ('#D4252A','#8E1518'))
    return (T['niv'][0],T['fond'] if not T['blancs'] else '#0E1A13',1) if v>0 else (('#E3A600' if not T['blancs'] else T['niv'][1],'#0E1A13',1) if v>-5 else ((rouge,'#fff',1) if v>-20 else (fonce,'#fff',1)))

def plan_fifa2():
    """Post 2, image principale : les neuf scénarios, en grand, avec trois classes franches."""
    F=fifa_d(); S={s['resultats']:s['ecart'] for s in F['deux_matchs']}
    x0=170; cw=(W-x0)/3; top=Y0+120; ch=(H-top-110)/3; g=''
    g+=f'<div style="position:absolute;left:{x0}px;top:{top-82}px;width:{W-x0}px;text-align:center;font:700 20px/1 IN;color:{T["ink"]}">Match retour, à Kigali</div>'
    g+=f'<div style="position:absolute;left:0;top:{top-82}px;font:700 20px/1 IN;color:{T["ink"]}">Match aller,<br>à Bamako</div>'
    for j,r in enumerate('VND'):
        g+=f'<div style="position:absolute;left:{x0+j*cw:.0f}px;top:{top-40}px;width:{cw:.0f}px;text-align:center;font:600 19px/1 IN;color:{T["doux"]}">{RES_F[r]}</div>'
    for i,a in enumerate('VND'):
        y=top+i*ch
        g+=f'<div style="position:absolute;left:0;top:{y+ch/2-11:.0f}px;font:600 19px/1 IN;color:{T["doux"]}">{RES_F[a]}</div>'
        for j,b in enumerate('VND'):
            v=S[a+b]; c,tc,op=classe_f(v); x=x0+j*cw
            g+=(f'<div style="position:absolute;left:{x+5:.0f}px;top:{y+5:.0f}px;width:{cw-10:.0f}px;height:{ch-10:.0f}px;border-radius:12px;background:{c};opacity:{op}"></div>'
                f'<div style="position:absolute;left:{x+5:.0f}px;top:{y+ch/2-(40 if v>0 else 30):.0f}px;width:{cw-10:.0f}px;text-align:center;font:italic 900 {68 if v>0 else 58}px/1 BC;color:{tc}">{sg(v)}</div>')
            if v>0: g+=f'<div style="position:absolute;left:{x+5:.0f}px;top:{y+ch/2+34:.0f}px;width:{cw-10:.0f}px;text-align:center;font:700 16px/1 IN;color:{tc}">le seul qui rapporte</div>'
    sq=lambda c,op=1:f'<i style="width:15px;height:15px;border-radius:3px;background:{c};opacity:{op}"></i>'
    lg=''.join(f'<span>{sq(classe_f(v)[0])}{t}</span>' for v,t in ((1,'gagne'),(-1,'perd un peu'),(-10,'perd'),(-30,'perd beaucoup')))
    a=round(100*F['attendu_mali'])
    g+=f'<div style="position:absolute;left:0;right:0;top:{top+3*ch+22:.0f}px;font:600 20px/1.35 IN;color:{T["ink"]}">La FIFA attend une victoire du Mali à {a} % : gagner rapporte peu, ne pas gagner coûte cher.</div>'
    body=f'<div class="hd"><h3>Tous les scénarios</h3><div class="lg">{lg}</div></div>{g}'
    return page(CTX_F,hero_f2(F),body,NOTE_F,CSS_DEF())

def plan_fifa2_un():
    """Post 2, autre image : ce que vaut un seul match, en trois grandes barres de part et d'autre de zéro."""
    F=fifa_d(); u=F['un_match']; top=Y0+90; z=W*.36; k=(W-z-190)/max(abs(v) for v in u.values()); rh=(H-top-170)/3; g=''
    for i,r in enumerate('VND'):
        v=u[r]; y=top+i*rh; c,_,op=classe_f(v); bh=min(92,rh*.5)
        g+=f'<div style="position:absolute;left:0;top:{y+bh/2-12:.0f}px;font:700 24px/1 IN;color:{T["ink"]}">{RES_F[r].capitalize()}</div>'
        if v>0: g+=f'<div style="position:absolute;left:{z:.0f}px;top:{y:.0f}px;width:{v*k:.0f}px;height:{bh:.0f}px;border-radius:0 8px 8px 0;background:{c}"></div><div style="position:absolute;left:{z+v*k+18:.0f}px;top:{y+bh/2-38:.0f}px;font:italic 900 76px/1 BC;color:{T["titre"]}">{sg(v)}</div>'
        else: g+=f'<div style="position:absolute;left:{z:.0f}px;top:{y:.0f}px;width:{-v*k:.0f}px;height:{bh:.0f}px;border-radius:0 8px 8px 0;background:{c};opacity:{op}"></div><div style="position:absolute;left:{z-v*k+18:.0f}px;top:{y+bh/2-38:.0f}px;font:italic 900 76px/1 BC;color:{T["titre"]}">{sg(v)}</div>'
    g+=f'<div style="position:absolute;left:{z-1:.0f}px;top:{top-16}px;width:2px;height:{3*rh-rh*.3:.0f}px;background:{T["mute"]}"></div>'
    a=round(100*F['attendu_mali'])
    g+=f'<div style="position:absolute;left:0;right:0;top:{top+3*rh:.0f}px;font:600 20px/1.35 IN;color:{T["ink"]}">La FIFA attend une victoire du Mali à {a} %. Contre plus fort, un nul rapporte ; contre plus faible, il coûte.</div>'
    body=f'<div class="hd"><h3>Les points FIFA d\'un seul match contre le Rwanda</h3></div>{g}'
    return page(CTX_F,hero_f2(F),body,NOTE_F,CSS_DEF())

html={'tirs':plan_tirs,'defense2':plan_defense2,'defense2_sans':plan_defense2_sans,'defense2_niveaux':plan_defense2_niveaux,'fifa2':plan_fifa2,'fifa2_un':plan_fifa2_un,'fifa':plan_fifa,'fifa_un':plan_fifa_un,'fifa_courbe':plan_fifa_courbe,'fifa_liste':plan_fifa_liste,'defense':plan_defense,'defense_attendu':plan_defense_attendu,'defense_matchs':plan_defense_matchs,'defense_sans':plan_defense_sans,'but':plan_but,'fil':plan_fil,'reseau':plan_reseau,'fiche':plan_fiche,'accroche':plan_accroche,'fin':plan_fin,
      'histoire':plan_histoire,'scores':plan_scores,'decennies':plan_decennies,'competitions':plan_competitions}[PLAN]()
open(OUT,'w',encoding='utf-8').write(html); print('ok',PLAN,TH_,OUT)

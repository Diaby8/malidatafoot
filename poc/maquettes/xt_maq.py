import json, math
SH='/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'; X=SH+'/xt'
exec(open(SH+'/maq_a.py',encoding='utf-8').read().split('# 1 : le score')[0])
SB='<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
G=json.load(open(X+'/xt_grid.json')); V=G['valeurs']; T=json.load(open(X+'/teams.json')); P=json.load(open(X+'/top_possession.json'))['meilleure']
def mix(c1,c2,t):
    a=[int(c1[i:i+2],16) for i in (1,3,5)]; b=[int(c2[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(x+(y-x)*t):02X}' for x,y in zip(a,b))
STOPS=[(0,'#FFF3C4'),(.25,'#9BD3A2'),(.5,'#19A552'),(.75,'#0B7A3B'),(1,'#04331A')]
def couleur(v,vmax=0.2825):
    t=math.sqrt(min(v,vmax)/vmax)
    for (t0,c0),(t1,c1) in zip(STOPS,STOPS[1:]):
        if t<=t1: return mix(c0,c1,(t-t0)/(t1-t0))
    return STOPS[-1][1]
def terrain_vertical(L,T0,k,inner='',lignes=True):
    """Terrain vu de dessus, attaque vers le haut. StatsBomb (x 0-120, y 0-80) -> écran."""
    W,H=80*k,120*k; ln='stroke="#064A25" stroke-width="3" fill="none"'
    t=f'<rect x="{L}" y="{T0}" width="{W}" height="{H}" fill="none" stroke="#064A25" stroke-width="4"/>'
    if lignes:
        t+=f'<line x1="{L}" y1="{T0+H/2}" x2="{L+W}" y2="{T0+H/2}" {ln}/><circle cx="{L+W/2}" cy="{T0+H/2}" r="{10*k}" {ln}/>'
        t+=f'<rect x="{L+18*k}" y="{T0}" width="{44*k}" height="{18*k}" {ln}/><rect x="{L+30*k}" y="{T0}" width="{20*k}" height="{6*k}" {ln}/>'
        t+=f'<rect x="{L+18*k}" y="{T0+H-18*k}" width="{44*k}" height="{18*k}" {ln}/><rect x="{L+36*k}" y="{T0-1.6*k}" width="{8*k}" height="{1.6*k}" fill="#064A25"/>'
    return inner+t
P2S=lambda L,T0,k:(lambda x,y:(L+y*k, T0+(120-x)*k))
out={}
# W1 : la carte de la menace
k=6.7; L=(1080-80*k)/2-30; T0=560; cells=''
for cy in range(12):
    for cx in range(16):
        v=V[cy][cx]; sx=L+cy*(80/12)*k; sy=T0+(120-(cx+1)*7.5)*k
        cells+=f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{80/12*k+.6:.1f}" height="{7.5*k+.6:.1f}" fill="{couleur(v)}"/>'
vmax=max(max(r) for r in V); cy,cx=max(((cy,cx) for cy in range(12) for cx in range(16)),key=lambda c:V[c[0]][c[1]])
hx=L+(cy+.5)*(80/12)*k; hy=T0+(120-(cx+.5)*7.5)*k
svg=terrain_vertical(L,T0,k,cells)+f'<line x1="{hx+28:.0f}" y1="{hy:.0f}" x2="{L+80*k+40:.0f}" y2="{hy:.0f}" stroke="#D4252A" stroke-width="3"/>'
b=f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{svg}</svg>'
b+=f'<div style="position:absolute;left:{L+80*k+50:.0f}px;top:{hy-50:.0f}px;font:italic 900 80px/1 BC;color:#D4252A">{round(100*vmax)} %</div><div style="position:absolute;left:{L+80*k+50:.0f}px;top:{hy+36:.0f}px;width:150px;font:800 20px/1.25 SC;color:#04331A">LA ZONE<br>LA PLUS<br>DANGEREUSE</div>'
lg=''.join(f'<i style="display:block;width:44px;height:22px;background:{couleur(v)}"></i>' for v in (0,.01,.03,.08,.15,.28))
b+=f'<div class="leg" style="top:1460px;display:none"></div>'
b+=f'<div style="position:absolute;left:64px;top:{T0+120*k+28:.0f}px;display:flex;align-items:center;gap:0">{lg}<span style="margin-left:14px;font:800 22px SC;color:#04331A">DE 0 À {round(100*vmax)} % DE CHANCES DE MARQUER DANS LES ACTIONS QUI SUIVENT</span></div>'
out['w1']=pageT('NOTRE MODÈLE · <b>2 564 MATCHS, 3,35 MILLIONS D\'ACTIONS</b>','LA CARTE','DE LA MENACE','',b,f'Menace attendue (xT, méthode de K. Singh) apprise sur les données ouvertes · Données {SB}')
# W2 : générer / concéder
E=T['equipes']; xs=[e['xt_p90'] for e in E]; ys=[e['xt_concede_p90'] for e in E]
x0,x1,y0,y1=130,940,600,1220
sx=lambda v:x0+(v-min(xs)+.05)/(max(xs)-min(xs)+.1)*(x1-x0); sy=lambda v:y0+(v-min(ys)+.05)/(max(ys)-min(ys)+.1)*(y1-y0)  # haut = concède peu
COD={'Mali':'MALI','Morocco':'MAR','Senegal':'SEN','Algeria':'ALG','Egypt':'EGY',"Côte d'Ivoire":'CIV','Nigeria':'NGA','South Africa':'RSA','Cameroon':'CMR','Cape Verde Islands':'CPV','Guinea':'GUI','Ghana':'GHA','Tunisia':'TUN','Congo DR':'COD','Burkina Faso':'BFA','Namibia':'NAM','Angola':'ANG','Mozambique':'MOZ','Gambia':'GAM','Mauritania':'MTN','Tanzania':'TAN','Zambia':'ZAM','Guinea-Bissau':'GNB','Equatorial Guinea':'EQG'}
g=f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/><line class="ax" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>'
for e in E:
    m=e['equipe']=='Mali'; cx,cy_=sx(e['xt_p90']),sy(e['xt_concede_p90'])
    g+=f'<circle cx="{cx:.0f}" cy="{cy_:.0f}" r="{17 if m else 9}" fill="{"#0B7A3B" if m else "#FFF3C4"}" stroke="#064A25" stroke-width="2"/><text x="{cx+(24 if m else 14):.0f}" y="{cy_+8:.0f}" style="font:800 {30 if m else 19}px SC;fill:{"#0B7A3B" if m else "#04331A"}">{COD.get(e["equipe"],e["equipe"][:3].upper())}</text>'
g+=f'<text x="{x1}" y="{y1+40}" text-anchor="end" style="font:800 22px SC;fill:#04331A">CRÉE PLUS DE MENACE →</text><text x="{x0-16}" y="{y0+10}" text-anchor="end" transform="rotate(-90 {x0-16} {y0+10})" style="font:800 22px SC;fill:#04331A">CONCÈDE MOINS →</text>'
b=f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{g}</svg>'
b+='<div class="bigR" style="top:1300px"><b>1<span style="font:italic 900 70px BC">er</span></b><span>POUR LA MENACE CONCÉDÉE…<br>MAIS <em>21e SUR 24</em> POUR LA MENACE CRÉÉE</span></div>'
out['w2']=pageT('CAN 2023 · <b>MENACE CRÉÉE ET CONCÉDÉE PAR 90 MINUTES</b>','RIEN DONNER,','PEU CRÉER','',b,f'Menace attendue (xT) des passes et conduites réussies · 24 équipes · Données {SB}')
# W3 : la meilleure action
k=6.8; L=(1080-80*k)/2; T0=520; f=P2S(L,T0,k); seq=[e for e in P['sequence'] if e['type'] in ('Pass','Carry') and e.get('end_location')]
lines=''
for e in seq:
    (ax,ay),(bx,by)=f(*e['location'][:2]),f(*e['end_location'][:2]); gain=e.get('xt_ajoute',0) or 0
    col='#D4252A' if gain>0.1 else ('#0B7A3B' if e['type']=='Pass' else '#064A25'); w=8 if gain>0.1 else 4
    lines+=f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" stroke="{col}" stroke-width="{w}" {"stroke-dasharray=\"8 7\"" if e["type"]=="Carry" else ""} stroke-linecap="round"/>'
sh=P['fin']; tx,ty=f(*sh['location'][:2])
lines+=f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="{6+40*sh["xg"]**.5:.0f}" fill="#FFFFFF" stroke="#04331A" stroke-width="3"/>'
pitch='<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#0B7A3B" fill-opacity=".0"/>'
svg=terrain_vertical(L,T0,k,'')+lines
b=f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920">{svg}</svg>'
b+=f'<div style="position:absolute;left:64px;top:{T0+120*k+22:.0f}px;font:800 24px/1.35 SC;letter-spacing:.03em;color:#04331A">22 SECONDES · 8 MALIENS · <span style="color:#D4252A">LE CENTRE DE Y. NIAKATÉ : +0,25</span><br>TÊTE DE SINAYOKO (CHANCE DE BUT 32 %), À CÔTÉ</div>'
out['w3']=pageT('NAMIBIE 0-0 MALI · CAN 2023 · <b>27e MINUTE</b>','L\'ACTION','LA PLUS DANGEREUSE','',b,f'La menace ajoutée par chaque passe (xT) · Trait plein : passe · pointillé : conduite · Données {SB}')
for kk,h in out.items(): open(f'_xt_{kk}.html','w',encoding='utf-8').write(h)
print('ok')

"""Carte des tirs d'une équipe sur un tournoi, dans le cadre commun. Un rond = un tir, sa taille = la qualité de l'occasion (xG),
plein = but. Pas de chiffres sur le terrain : les valeurs sont dans les tableaux dessous."""
import json, math, sys, collections
from da import page, fr
SRC=sys.argv[1] if len(sys.argv)>1 else '../outputs/resultats.json'
OUT=sys.argv[2] if len(sys.argv)>2 else 'tirs_pro.html'
D=json.load(open(SRC,encoding='utf-8')); T=D['tirs']; M=D['matches']
buts=[t for t in T if t['is_goal']]; xg=sum(t['xg'] for t in T)
in_box=lambda t:t['x']>=102 and 18<=t['y']<=62
surf=[t for t in T if in_box(t)]; hors=[t for t in T if not in_box(t)]
cadres=[t for t in T if t['outcome'] in ('Goal','Saved','Saved to Post')]
csc=sum(m['goals_for'] for m in M)-len(buts)            # buts comptés au score mais pas marqués sur un tir de l'équipe
# ---- terrain : moitié offensive, but en haut. Repère StatsBomb 120 x 80, x vers le but adverse, y de gauche à droite pour l'attaquant
S=10.9; X0=80.5; PW=80*S; PH=(120-X0)*S; GH=2.2*S       # GH : profondeur du but dessinée au-dessus de la ligne
px=lambda y:y*S; py=lambda x:GH+(120-x)*S
L='stroke="#C3CCC6" stroke-width="2.2" fill="none"'
g=f'<rect x="0" y="{GH}" width="{PW}" height="{PH}" fill="#F3F6F3"/>'
g+=f'<path d="M0 {GH+PH}V{GH}H{PW}V{GH+PH}" {L}/>'
g+=f'<rect x="{px(18)}" y="{py(120)}" width="{44*S}" height="{18*S}" {L}/><rect x="{px(30)}" y="{py(120)}" width="{20*S}" height="{6*S}" {L}/>'
g+=f'<rect x="{px(36)}" y="{py(120)-GH+1.5}" width="{8*S}" height="{GH-1.5}" stroke="#8E9A91" stroke-width="2.6" fill="#fff"/>'
a=math.acos(6/10); ax=10*math.sin(a)*S                    # arc de la surface : cercle de 10 autour du point de penalty, partie hors surface
g+=f'<path d="M{px(40)-ax:.1f} {py(102):.1f}A{10*S} {10*S} 0 0 0 {px(40)+ax:.1f} {py(102):.1f}" {L}/>'
g+=f'<circle cx="{px(40)}" cy="{py(108)}" r="3.2" fill="#C3CCC6"/>'
R=lambda v:max(6.5,math.sqrt(v)*36)
for t in sorted(T,key=lambda t:(t['is_goal'],-t['xg'])):   # les gros d'abord, les buts par-dessus
    x,y,r=px(t['y']),py(t['x']),R(t['xg'])
    if t['is_goal']: g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#0B7A3B" stroke="#fff" stroke-width="3"/>'
    else: g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#5E6B62" fill-opacity=".16" stroke="#5E6B62" stroke-width="1.8"/>'
pen=[t for t in T if t['shot_type']=='Penalty' and not t['is_goal']]
C=[(px(t['y']),py(t['x']),R(t['xg'])) for t in T]
def libre(x0,y0,x1,y1,moi):                               # le rectangle du texte ne touche aucun autre rond, ni le bord
    if x0<6 or x1>PW-6 or y0<GH+4 or y1>GH+PH-4: return False
    return all(not (cx+cr+3>x0 and cx-cr-3<x1 and cy+cr+3>y0 and cy-cr-3<y1) for cx,cy,cr in C if (cx,cy,cr)!=moi)
for t in pen:                                             # seule étiquette posée sur le terrain : le penalty manqué
    x,y,r=px(t['y']),py(t['x']),R(t['xg']); TW,TH=124,22; ok=None
    for d in range(30,260,6):
        for ang in (0,180,20,160,-20,200,40,140,-40,220,60,120,90,-60,240,-90):
            ex,ey=x+(r+d)*math.cos(math.radians(ang)),y+(r+d)*math.sin(math.radians(ang))
            x0=ex+8 if math.cos(math.radians(ang))>=0 else ex-8-TW
            if libre(x0,ey-TH/2,x0+TW,ey+TH/2,(x,y,r)): ok=(ang,ex,ey,x0); break
        if ok: break
    ang,ex,ey,x0=ok; sx,sy=x+(r+3)*math.cos(math.radians(ang)),y+(r+3)*math.sin(math.radians(ang))
    g+=f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#5E6B62" stroke-width="1.6"/><text x="{x0:.1f}" y="{ey+6:.1f}" class="lab">Penalty arrêté</text>'
# ---- tableaux
by=collections.defaultdict(lambda:[0,0.0,0])
for t in T: by[t['player']][0]+=1; by[t['player']][1]+=t['xg']; by[t['player']][2]+=int(t['is_goal'])
top=sorted(by.items(),key=lambda kv:(-kv[1][1],kv[0]))[:5]; mx=top[0][1][1]
rows=''.join(f'<div class="r"><span class="n">{n}</span><span class="v1">{v[0]}</span><span class="b"><i style="width:{v[1]/mx*100:.0f}%"></i></span><span class="v2">{fr(v[1],2)}</span><span class="c">{v[2]}</span></div>' for n,v in top)
zone=lambda nom,l:f'<div class="z"><span class="n">{nom}</span><span class="v1">{len(l)}</span><span class="c">{sum(t["is_goal"] for t in l)}</span></div>'
jeu=[t for t in T if t['shot_type']=='Open Play']; arr=[t for t in T if t['shot_type']!='Open Play']
zones='<div class="fam">Zone</div>'+zone('Dans la surface',surf)+zone('Hors de la surface',hors)+'<div class="fam">Situation</div>'+zone('Dans le jeu',jeu)+zone('Coup franc ou penalty',arr)
css='''
#nm{position:absolute;left:0;top:4px;font:italic 900 90px/1 "BC";color:var(--vert-d);text-transform:uppercase;white-space:nowrap}
#m1{position:absolute;left:3px;top:100px;font:600 25px/1 "IN";color:var(--encre)}
#m2{position:absolute;left:3px;top:134px;font:500 21px/1 "IN";color:rgba(14,26,19,.7)}
#lg,#cap{display:flex;gap:22px;align-items:center;font:500 18px/1 "IN";color:var(--gris)}#lg span,#cap span{display:flex;align-items:center;gap:8px}
#cap{position:absolute;left:48px;top:540px;font-size:16.5px}#cap i{display:block;border-radius:50%}
#lg i{display:block;border-radius:50%}
#pit{position:absolute;left:48px;top:74px;width:872px;overflow:visible}
.lab{font:600 17px "IN";fill:#3A463E}
#sep{position:absolute;left:36px;right:36px;top:578px;border-top:1.5px solid var(--trait)}
#bt{position:absolute;left:36px;right:36px;top:600px;display:grid;grid-template-columns:1.32fr 1fr;gap:56px}
#bt h4{font:700 19px/1 "IN";color:var(--encre)}
.th{position:relative;height:22px;margin-top:16px;font:500 15px/1 "IN";color:var(--gris);border-bottom:1.5px solid var(--trait);padding-bottom:26px}.th span{position:absolute;top:0}
.r,.z{position:relative;height:39px;border-bottom:1px solid #EEF1EE}
.fam{font:600 15px/1 "IN";color:var(--gris);padding:13px 0 7px;border-bottom:1.5px solid var(--trait)}
.th.nu{border-bottom:none;padding-bottom:6px}
.r .n,.z .n{position:absolute;left:0;top:10px;font:500 19px/1 "IN";white-space:nowrap}
.r .v1{position:absolute;left:214px;width:44px;top:11px;text-align:right;font:400 18px/1 "IN";color:var(--gris)}
.r .b{position:absolute;left:286px;width:90px;top:16px;height:6px;border-radius:3px;background:#E9EDE8;overflow:hidden}.r .b i{display:block;height:100%;border-radius:3px;background:#0B7A3B}
.r .v2{position:absolute;left:386px;width:52px;top:11px;text-align:right;font:400 18px/1 "IN";color:var(--gris)}
.r .c,.z .c{position:absolute;right:0;top:9px;font:700 20px/1 "IN"}
.z .v1{position:absolute;right:86px;width:60px;top:11px;text-align:right;font:400 18px/1 "IN";color:var(--gris)}
'''
hero=f'''<div id="nm">Les tirs du Mali</div><div id="m1">{len(T)} tirs en {len(M)} matchs, dont {len(cadres)} cadrés</div><div id="m2">Toutes les tentatives des Aigles pendant le tournoi</div>
<div id="sc"><small>Buts marqués sur tir</small><b>{len(buts)}</b><span>pour {fr(xg)} buts attendus (xG)</span></div>'''
panel=f'''<div id="ph"><h3>Chaque rond est un tir</h3><div id="lg"><span><i style="width:18px;height:18px;background:#0B7A3B"></i>but</span><span><i style="width:18px;height:18px;border:1.8px solid #5E6B62;background:rgba(94,107,98,.16)"></i>pas de but</span></div></div>
<svg id="pit" viewBox="0 0 {PW:.0f} {PH+GH:.0f}" width="872" height="{(PH+GH)*872/PW:.0f}">{g}</svg>
<div id="cap"><span><i style="width:9px;height:9px;border:1.6px solid #5E6B62"></i><i style="width:24px;height:24px;border:1.6px solid #5E6B62;margin-left:-2px"></i>Plus le rond est gros, plus l'occasion était belle (xG)</span></div>
<div id="sep"></div>
<div id="bt"><div><h4>Les tireurs les plus dangereux</h4><div class="th"><span style="left:214px;width:44px;text-align:right">tirs</span><span style="left:286px">buts attendus (xG)</span><span style="right:0">buts</span></div>{rows}</div>
<div><h4>Le détail des tirs</h4><div class="th nu"><span style="right:86px;width:60px;text-align:right">tirs</span><span style="right:0">buts</span></div>{zones}</div></div>'''
note="xG : la chance qu'un tir finisse au fond, de 0 à 1.<br>"+(f"Autre but du Mali : {'un' if csc==1 else csc} contre son camp. " if csc>0 else '')+"Données StatsBomb Open Data."
open(OUT,'w',encoding='utf-8').write(page("Coupe d'Afrique des nations 2023",hero,panel,note,css))
print('ok',OUT,len(T),'tirs',len(buts),'buts',round(xg,2),'xG | surface',len(surf),'hors',len(hors),'cadrés',len(cadres),'csc',csc,top)

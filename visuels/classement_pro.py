"""Classement des joueurs d'une équipe, dans le cadre commun. Chaque joueur est noté parmi les joueurs de son rôle,
sur les dix critères de ce rôle : la couleur dit où il se situe dans son rôle (meilleur quart, milieu, dernier quart).
usage : python3 classement_pro.py <classement.json de l'étape « profils »> <sortie.html> [x|tiktok]"""
import json, sys
from da import page, fr, ordi
SRC=sys.argv[1] if len(sys.argv)>1 else '../outputs/classement.json'
OUT=sys.argv[2] if len(sys.argv)>2 else 'classement_pro.html'; FMT=sys.argv[3] if len(sys.argv)>3 else 'x'
D=json.load(open(SRC,encoding='utf-8')); J=D['joueurs']; n=len(J)
part=lambda j:1-(j['rang']-1)/(j['effectif']-1)             # part des autres joueurs de son rôle qu'il dépasse
niv=lambda p:('#0B7A3B' if p>=.75 else ('#E3A600' if p>=.25 else '#D4252A'))
haut=sum(part(j)>=.75 for j in J)
H=(50 if n<=13 else max(38,int(650/n))) if FMT=='x' else (58 if n<=13 else max(40,int(754/n)))
rows=''.join(f'''<div class="r"><span class="k">{i}</span><span class="n">{j['player']}</span><span class="p">{j['poste']}</span>
<span class="b"><i style="width:{j['note']:.0f}%;background:{niv(part(j))}"></i></span><span class="v">{fr(j['note'])}</span><span class="g">{ordi(j['rang'])} sur {j['effectif']}</span></div>''' for i,j in enumerate(J,1))
court=[x for x in D['non_notes'] if x['raison']=='temps de jeu']; gard=[x for x in D['non_notes'] if x['raison']=='gardien']
hors=(f"Moins de {D['min_minutes']} minutes : "+', '.join(f"{x['player']} ({x['minutes']})" for x in court)+'. ' if court else '')+ \
     (f"Gardien{'s' if len(gard)>1 else ''}, pas encore de grille : "+', '.join(x['player'] for x in gard)+'.' if gard else '')
C=dict(k=0,n=44,p=330,b=556,bw=150,v=716,vw=62,gw=118) if FMT=='x' else dict(k=0,n=40,p=292,b=478,bw=120,v=606,vw=62,gw=118)
css=f'''
#nm{{position:absolute;left:0;top:4px;font:italic 900 90px/1 "BC";color:var(--vert-d);text-transform:uppercase;white-space:nowrap}}
#m1{{position:absolute;left:3px;top:100px;font:600 25px/1 "IN";color:var(--encre)}}
#m2{{position:absolute;left:3px;top:134px;font:500 21px/1 "IN";color:rgba(14,26,19,.7)}}
#lg{{display:flex;gap:18px;font:500 17px/1 "IN";color:var(--gris)}}#lg i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:7px}}
#tb{{position:absolute;left:36px;right:36px;top:78px}}
.th{{position:relative;height:30px;font:500 15px/1 "IN";color:var(--gris);border-bottom:1.5px solid var(--trait)}}.th span{{position:absolute;top:2px}}
.r{{position:relative;height:{H}px;border-bottom:1px solid #EEF1EE}}
.r span{{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}}
.r .k{{left:{C['k']}px;width:26px;text-align:right;font:500 17px "IN";color:var(--gris)}}
.r .n{{left:{C['n']}px;font:600 20px "IN";color:var(--encre)}}
.r .p{{left:{C['p']}px;font:400 17.5px "IN";color:var(--gris)}}
.r .b{{left:{C['b']}px;width:{C['bw']}px;height:6px;border-radius:3px;background:#E9EDE8;overflow:hidden}}.r .b i{{display:block;height:100%;border-radius:3px}}
.r .v{{left:{C['v']}px;width:{C['vw']}px;text-align:right;font:700 21px "IN";color:var(--encre)}}
.r .g{{right:0;width:{C['gw']}px;text-align:right;font:400 17px "IN";color:var(--gris)}}
#cap{{position:absolute;left:36px;right:36px;top:{78+30+n*(H+1)+14}px;font:500 16.5px/1 "IN";color:var(--gris);white-space:nowrap}}
#hors{{position:absolute;left:36px;right:36px;top:{78+30+n*(H+1)+48}px}}
#hors h4{{font:700 18px/1 "IN";color:var(--encre)}}#hors p{{margin-top:10px;font:400 16.5px/1.45 "IN";color:var(--gris)}}
'''
if FMT=='tiktok': css+='''
#nm{font-size:72px;top:14px}
'''
hero=f'''<div id="nm">Les Aigles notés</div><div id="m1">{n} joueurs, chacun jugé parmi son poste</div><div id="m2">Au moins {D['min_minutes']} minutes jouées pendant le tournoi</div>
<div id="sc"><small>Meilleur quart de leur poste</small><b>{haut}</b><span>joueurs sur {n}</span></div>'''
panel=f'''<div id="ph"><h3>La note sur les dix critères du poste</h3><div id="lg"><span><i style="background:#0B7A3B"></i>meilleur quart</span><span><i style="background:#E3A600"></i>milieu</span><span><i style="background:#D4252A"></i>dernier quart</span></div></div>
<div id="tb"><div class="th"><span style="left:{C['n']}px">joueur</span><span style="left:{C['p']}px">poste</span><span style="left:{C['v']}px;width:{C['vw']}px;text-align:right">note</span><span style="right:0">rang au poste</span></div>{rows}</div>
<div id="cap">Chaque note se lit dans son poste : entre deux postes, elles ne se comparent pas au point près.</div>
<div id="hors"><h4>Pas notés</h4><p>{hors}</p></div>'''
note=("Note : moyenne des centiles sur les dix critères du poste.","Chacun est noté parmi les joueurs de son poste. Données StatsBomb Open Data.")
open(OUT,'w',encoding='utf-8').write(page("Coupe d'Afrique des nations 2023",hero,panel,note,css,FMT))
print('ok',OUT,n,'joueurs | meilleur quart',haut,[(j['player'],j['note'],round(part(j),2)) for j in J])

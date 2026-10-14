"""Fiche joueur, troisième version : construction d'outil pro (radar sans chiffres, valeurs en tableau,
couleur = niveau, critères choisis pour le poste), dans les couleurs MaliDataFoot. Aucun effet : ni grain, ni trame, ni dégradé marqué."""
import json, math, os, sys
# usage : python3 fiche_pro.py <fiche.json produite par l'étape « profils » du pipeline> <sortie.html> [x|tiktok]
# x : 1080 x 1350 pour Twitter/X ; tiktok : 1080 x 1920, tout le contenu entre y = 150 et y = 1580 et à gauche de x = 946
SRC=sys.argv[1] if len(sys.argv)>1 else '../outputs/fiches/hamari-traore_poste.json'
OUT=sys.argv[2] if len(sys.argv)>2 else 'fiche_pro.html'
FMT=sys.argv[3] if len(sys.argv)>3 else 'x'
F=json.load(open(SRC,encoding='utf-8')); B=F['bassin']
# FLOU=1 : chiffres, barres et listes floutés (effet vidéo, illisibles) ; radar remplacé par une forme décorative en zigzag, floutée (aucune donnée).
# Une fiche marquée « fictif » (chiffres d'illustration) ne sort JAMAIS sans flou.
FLOU=os.environ.get('FLOU')=='1'
if F.get('fictif') and not FLOU: sys.exit('fiche fictive : rendu refusé sans FLOU=1')
fr=lambda v,d=1:(f'{v:.{d}f}').replace('.',',')
# coupure des libellés autour du radar (présentation seulement ; la liste des critères vient du pipeline)
COUPE={'passes_into_box_p90':['Passes dans','la surface'],'prog_passes_p90':['Passes','progressives'],'prog_carries_p90':['Conduites','progressives'],
       'dribbles_won_p90':['Dribbles','réussis'],'tackles_interceptions_p90':['Tacles +','interceptions'],'aerials_won_p90':['Duels','aériens gagnés'],
       'xa_p90':['Passes décisives','attendues'],'npxg_p90':['Buts attendus','hors penalty'],'np_goals_p90':['Buts','hors penalty'],
       'receptions_in_box_p90':['Ballons reçus','dans la surface'],'passes_final_third_p90':['Passes vers le','dernier tiers'],
       'pass_pct':['Passes','réussies (%)'],'key_passes_p90':['Passes','clés']}
CRIT=[(c['k'],c['nom'],COUPE.get(c['k'],[c['nom']]),c['famille']) for c in F['criteres']]
PCT={c['k']:c['centile'] for c in F['criteres']}; VAL={c['k']:c['valeur'] for c in F['criteres']}
# couleur = niveau, par quarts : meilleur quart, milieu, dernier quart du bassin
niv=lambda p:('#0B7A3B' if p>=75 else ('#E3A600' if p>=25 else '#D4252A'))
ordi=lambda n:('1er' if n==1 else f'{n}e')
# ---- radar
N=len(CRIT); cx,cy,R=250,262,158
pol=lambda r,i:(cx+r*math.cos(-math.pi/2+i*2*math.pi/N), cy+r*math.sin(-math.pi/2+i*2*math.pi/N))
g=''
for v in (25,75,100): g+=f'<circle cx="{cx}" cy="{cy}" r="{R*v/100:.1f}" fill="none" stroke="#DCE1DC" stroke-width="1.5"/>'
g+=f'<circle cx="{cx}" cy="{cy}" r="{R*.5:.1f}" fill="none" stroke="#8E9A91" stroke-width="1.5" stroke-dasharray="3 6"/>'
for i in range(N):
    x,y=pol(R,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E4E8E3" stroke-width="1.3"/>'
pts=[pol(R*max(PCT[k],2)/100,i) for i,(k,_,_,_) in enumerate(CRIT)]
if os.environ.get('FLOU')=='1':   # vidéo floutée : forme décorative en zigzag, ample, différente par joueur, sans lien avec ses données
    import random; _r=random.Random(F['player']); pts=[pol(R*(_r.uniform(.68,.95) if i%2==0 else _r.uniform(.52,.80)),i) for i in range(N)]
g+='<defs><filter id="bl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter></defs><g'+(' filter="url(#bl)"' if FLOU else '')+'>'
g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'" fill="#19A552" fill-opacity="'+('.38' if FLOU else '.2')+'" stroke="#0B7A3B" stroke-width="3" stroke-linejoin="round"/>'
g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="#0B7A3B" stroke-width="3"/>' for x,y in pts)+'</g>'
HORIZ=(len(sys.argv)>3 and sys.argv[3]=='tiktok')   # en vertical, place sur les côtés : libellés droits, sans chevauchement
for i,(k,_,lines,_) in enumerate(CRIT):
    a=-math.pi/2+i*2*math.pi/N
    if HORIZ:
        ca,sa=math.cos(a),math.sin(a); n=len(lines); lh=21
        anc='middle' if abs(ca)<.2 else ('start' if ca>0 else 'end')
        x0,y0=cx+(R+16)*ca,cy+(R+16)*sa
        dy=sa*((n-1)*lh/2+10)
        for j,t in enumerate(lines):
            g+=f'<text x="{x0:.1f}" y="{y0+dy+(j-(n-1)/2)*lh:.1f}" text-anchor="{anc}" dominant-baseline="middle" class="rl">{t}</text>'
        continue
    deg=math.degrees(a)+90; bas=math.sin(a)>.15      # en bas, on retourne le texte pour qu'il reste lisible
    lh=21; n=len(lines)
    for j,t in enumerate(lines):
        rr=R+22+((n-1-j) if not bas else j)*lh+(4 if bas else 0)
        x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
        g+=f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" transform="rotate({deg+(180 if bas else 0):.1f} {x:.1f} {y:.1f})" class="rl">{t}</text>'
# ---- tableau
rows='';prev=None
for k,nom,_,fam in CRIT:
    if fam!=prev: rows+=f'<div class="fam">{fam}</div>'; prev=fam
    p=PCT[k]; rows+=f'<div class="r"><span class="n">{nom}</span><span class="v">{fr(VAL[k],2)}</span><span class="b"><i style="width:{max(p,3)}%;background:{niv(p)}"></i></span><span class="c">{p}</span></div>'
order=sorted(CRIT,key=lambda c:-PCT[c[0]])
forts=''.join(f'<li>{c[1]}<b>{PCT[c[0]]}</b></li>' for c in order[:3])
faibles=''.join(f'<li>{c[1]}<b>{PCT[c[0]]}</b></li>' for c in order[::-1] if PCT[c[0]]<25) or '<li>Aucun critère dans le dernier quart</li>'
sim=''.join(f'<li>{p["player"].split(" ")[-1]}<em>{p["team"]}</em><b>{p["proche"]} %</b></li>' for p in F['proches'])
notes=list(F['notes_bassin']); notes.remove(F['note']); lo,hi=min(notes+[F['note']]),max(notes+[F['note']])
ticks=''.join(f'<i style="left:{(v-lo)/(hi-lo)*100:.2f}%"></i>' for v in notes); me=(F['note']-lo)/(hi-lo)*100
_ph=f"photos/{F['player_id']}.png"
PHOTO=f'<img src="{_ph}" alt="">' if os.path.exists(_ph) else '<svg viewBox="0 0 100 100"><rect width="100" height="100" fill="#E9EDE8"/><circle cx="50" cy="39" r="18" fill="#A9B5AC"/><path d="M16 104C16 77 31 65 50 65C69 65 84 77 84 104Z" fill="#A9B5AC"/></svg>'
_cr=f"photos/{F['player_id']}.txt"
CREDIT=('<br>'+open(_cr,encoding='utf-8').read().strip()) if os.path.exists(_ph) and os.path.exists(_cr) else ''
# club actuel : lu dans le registre, affiché seulement s'il est confirmé
import csv
CLUB=''
_reg='../registre/joueurs.csv'
if os.path.exists(_reg):
    for r in csv.DictReader(open(_reg,encoding='utf-8')):
        if r['nom']==F['player'] and r['club'] and r['club_a_confirmer']!='oui': CLUB=r['club']
CLUBH=f' · {CLUB}<span class="act">club actuel</span>' if CLUB else ''
NOTE_TOP,NOTE_FS=(1257,16.5) if CREDIT else (1264,17.5)
NB={1:'Un',2:'Deux',3:'Trois',4:'Quatre',5:'Cinq',6:'Six',7:'Sept'}.get(F['matches'],str(F['matches']))
f='node_modules/@fontsource/'
TH='<div class="th"><span style="left:168px;width:100px;text-align:right">par 90 min</span><span style="right:0">centile</span></div>'
L1=f"Centile : part des autres {B['pluriel']} qu'il dépasse. Note : moyenne des dix centiles."
L2=f"{NB} matchs seulement, à lire avec prudence. Données StatsBomb Open Data." if not F.get('fictif') else "Chiffres d'illustration, floutés : pas encore de données mesurées pour ce joueur."
SOC='<b><img src="logo_x.png" alt="X" style="height:22px"><img src="logo_tt.png" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
if FMT=='tiktok':
    # format vertical : radar au-dessus, tableau sur deux colonnes (les deux premières familles à gauche, le reste à droite)
    blocs={}
    for k,nom,_,fam in CRIT:
        p=PCT[k]; blocs.setdefault(fam,f'<div class="fam">{fam}</div>')
        blocs[fam]+=f'<div class="r"><span class="n">{nom}</span><span class="v">{fr(VAL[k],2)}</span><span class="b"><i style="width:{max(p,3)}%;background:{niv(p)}"></i></span><span class="c">{p}</span></div>'
    fams=list(blocs); nrow={x:sum(1 for c in CRIT if c[3]==x) for x in fams}
    # coupure qui équilibre les deux colonnes (hauteur = lignes x 39 px + titre de famille x 37 px)
    hcol=lambda fs:sum(nrow[x]*39+37 for x in fs)
    cut=min(range(1,len(fams)),key=lambda i:max(hcol(fams[:i]),hcol(fams[i:]))) if len(fams)>1 else 1
    HT=22+max(hcol(fams[:cut]),hcol(fams[cut:]))
    SEP=552+HT+22
    TABLE=f'<div id="tb" class="deux"><div>{TH}{"".join(blocs[x] for x in fams[:cut])}</div><div>{TH}{"".join(blocs[x] for x in fams[cut:])}</div></div>'
    NOTE=f'<div id="note" class="v"><p>{L1}{CREDIT.replace("<br>"," ")}</p><div><span>{L2}</span>{SOC}</div></div>'
    CSSV='''
html,body{width:1080px;height:1920px}#c{height:1920px}
#top{right:134px;top:150px}
#hero{right:140px;top:250px}
#nm{font-size:80px;top:10px}
#p{top:428px;width:890px;height:1078px}
#rad{left:195px;top:24px}
#cap{top:522px}
#tb.deux{left:36px;top:552px;width:818px;display:grid;grid-template-columns:1fr 1fr;gap:38px}
#sep{top:@SEP@px}#bt{top:@BT@px;gap:26px}#bt li{padding:7px 0;font-size:18px}
#tb.deux .r .n{font-size:16.5px}#tb.deux .r .v{left:220px;width:50px;font-size:15px}#tb.deux .r .b{left:282px;width:54px}
#tb.deux .th span:first-child{left:170px!important}
#stw{display:none}
#note.v{top:1518px;right:134px;display:block;font-size:16.5px;line-height:1}
#note.v p{white-space:nowrap}
#note.v div{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}
#note.v b{font-size:22px}
'''.replace('@SEP@',str(SEP)).replace('@BT@',str(SEP+20))
else:
    TABLE=f'<div id="tb">{TH}{rows}</div>'
    NOTE=f'<div id="note"><span>{L1}<br>{L2}{CREDIT}</span>{SOC}</div>'
    CSSV=''
FLOUCSS='#sc span,#m2,.r .v,.r .b,.r .c,#bt ul,#st{filter:blur(9px)}#sc b{filter:blur(24px)}' if FLOU else ''
html=f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face{{font-family:"BC";font-style:italic;font-weight:900;src:url({f}barlow-condensed/files/barlow-condensed-latin-900-italic.woff2)}}
@font-face{{font-family:"BCS";font-style:italic;font-weight:400;src:url({f}barlow-condensed/files/barlow-condensed-latin-400-italic.woff2)}}
@font-face{{font-family:"BCS";font-style:italic;font-weight:600;src:url({f}barlow-condensed/files/barlow-condensed-latin-600-italic.woff2)}}
@font-face{{font-family:"IN";font-weight:400;src:url({f}inter/files/inter-latin-400-normal.woff2)}}
@font-face{{font-family:"IN";font-weight:500;src:url({f}inter/files/inter-latin-500-normal.woff2)}}
@font-face{{font-family:"IN";font-weight:600;src:url({f}inter/files/inter-latin-600-normal.woff2)}}
@font-face{{font-family:"IN";font-weight:700;src:url({f}inter/files/inter-latin-700-normal.woff2)}}
:root{{--or:#F6C41C;--vert:#0B7A3B;--vert-d:#064A25;--rouge:#D4252A;--encre:#0E1A13;--gris:#5E6B62;--trait:#E3E8E3}}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1350px;overflow:hidden}}
#c{{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F6C41C;font-family:"IN",sans-serif;color:var(--encre);font-variant-numeric:tabular-nums;font-feature-settings:"cv11","ss01"}}
#top{{position:absolute;left:56px;right:56px;top:26px;display:flex;justify-content:space-between;align-items:center}}
#brand{{display:flex;align-items:center;gap:15px;color:var(--vert-d)}}
#brand img{{width:72px;height:72px;border-radius:50%;display:block}}
#brand div{{display:flex;flex-direction:column;gap:6px}}
#brand b{{font:italic 400 47px/1 "BCS";letter-spacing:.005em;white-space:nowrap}}#brand b i{{font-weight:600}}
#brand em{{font:500 16px/1 "IN";font-style:normal;color:rgba(14,26,19,.7);padding-left:1px}}
#ctx{{font:600 21px/1 "IN";color:rgba(14,26,19,.72)}}
#hero{{position:absolute;left:56px;right:62px;top:128px;height:160px}}
.ph{{position:absolute;left:0;top:4px;width:150px;height:150px;border-radius:50%;overflow:hidden;background:#E9EDE8;box-shadow:0 0 0 5px #fff}}.ph img,.ph svg{{width:100%;height:100%;display:block;object-fit:cover}}
#nm{{position:absolute;left:178px;top:4px;font:italic 900 90px/1 "BC";color:var(--vert-d);text-transform:uppercase;white-space:nowrap}}
#m1{{position:absolute;left:181px;top:100px;font:600 25px/1 "IN";color:var(--encre)}}
#m1 .act{{font:500 18px/1 "IN";color:rgba(14,26,19,.62);margin-left:9px}}
#m2{{position:absolute;left:181px;top:134px;font:500 21px/1 "IN";color:rgba(14,26,19,.7)}}
#sc{{position:absolute;right:0;top:0;text-align:right}}
#sc small{{display:block;font:600 19px/1 "IN";color:rgba(14,26,19,.7)}}
#sc b{{display:block;font:italic 900 112px/.95 "BC";color:var(--vert-d);margin-top:6px}}
#sc span{{display:block;font:600 21px/1 "IN";color:var(--encre);margin-top:2px}}
#p{{position:absolute;left:56px;top:312px;width:968px;height:930px;background:#fff;border-radius:20px;box-shadow:0 16px 36px rgba(90,60,0,.2)}}
#ph{{position:absolute;left:36px;right:36px;top:28px;display:flex;justify-content:space-between;align-items:center}}
#ph h3{{font:700 23px/1 "IN";color:var(--encre)}}
#lg{{display:flex;gap:20px;font:500 18px/1 "IN";color:var(--gris)}}#lg i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:7px;vertical-align:0}}
#rad{{position:absolute;left:10px;top:70px;width:500px;height:524px;overflow:visible}}
.rl{{font:600 18px "IN";fill:#24332A}}
#cap{{position:absolute;left:36px;top:590px;font:500 16.5px/1 "IN";color:var(--gris)}}
#tb{{position:absolute;left:540px;top:78px;width:392px}}
.th{{position:relative;height:22px;font:500 15px/1 "IN";color:var(--gris)}}.th span{{position:absolute;top:0}}
.fam{{font:600 15px/1 "IN";color:var(--gris);padding:15px 0 7px;border-bottom:1.5px solid var(--trait)}}
.r{{position:relative;height:39px;border-bottom:1px solid #EEF1EE}}
.r .n{{position:absolute;left:0;top:11px;font:500 19px/1 "IN";color:var(--encre);white-space:nowrap}}
.r .v{{position:absolute;left:206px;width:62px;top:13px;text-align:right;font:400 17px/1 "IN";color:var(--gris)}}
.r .b{{position:absolute;left:284px;width:62px;top:17px;height:6px;border-radius:3px;background:#E9EDE8;overflow:hidden}}.r .b i{{display:block;height:100%;border-radius:3px}}
.r .c{{position:absolute;right:0;top:10px;font:700 20px/1 "IN";color:var(--encre)}}
#sep{{position:absolute;left:36px;right:36px;top:626px;border-top:1.5px solid var(--trait)}}
#bt{{position:absolute;left:36px;right:36px;top:648px;display:grid;grid-template-columns:1.15fr 1fr 1.1fr;gap:34px}}
#bt h4{{font:700 18px/1 "IN";color:var(--encre);display:flex;align-items:center;gap:9px}}#bt h4 i{{width:11px;height:11px;border-radius:50%;display:block}}
#bt ul{{list-style:none;margin-top:12px}}#bt li{{display:flex;align-items:baseline;gap:8px;font:500 18.5px/1 "IN";color:var(--encre);padding:8px 0;border-bottom:1px solid #EEF1EE;white-space:nowrap}}
#bt li b{{margin-left:auto;font-weight:700}}#bt li em{{font-style:normal;color:var(--gris);font-size:16px}}
#stw{{position:absolute;left:36px;right:36px;top:822px}}
#stw h4{{font:700 18px/1 "IN";color:var(--encre)}}
#st{{position:relative;height:40px;margin-top:10px;border-bottom:1.5px solid #B9C4BC}}
#st i{{position:absolute;bottom:0;width:2px;height:16px;background:#B9C4BC}}
#st b{{position:absolute;bottom:0;width:5px;height:38px;margin-left:-2px;background:var(--vert);border-radius:3px 3px 0 0}}
#st em{{position:absolute;bottom:-24px;font:500 15px/1 "IN";font-style:normal;color:var(--gris)}}
#note{{position:absolute;left:56px;right:56px;top:{NOTE_TOP}px;display:flex;justify-content:space-between;align-items:flex-start;font:500 {NOTE_FS}px/1.4 "IN";color:rgba(14,26,19,.78);white-space:nowrap}}
#note b{{display:flex;align-items:center;gap:12px;font:700 23px/1 "IN";color:var(--vert-d)}}#note b img{{display:block}}
{CSSV}{FLOUCSS}</style></head><body><div id="c">
<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx">{F.get("contexte","Coupe d'Afrique des nations 2023")}</div></div>
<div id="hero"><div class="ph">{PHOTO}</div>
 <div id="nm">{F['player']}</div><div id="m1">{F['poste']} · {F['team']}{CLUBH}</div><div id="m2">{F['minutes']} minutes en {F['matches']} matchs</div>
 <div id="sc"><small>{'Note' if F.get('fictif') else 'Note du tournoi'}</small><b>{F['note']:.0f}</b><span>{ordi(F['rang'])} sur {B['effectif']} {B['pluriel']}</span></div></div>
<div id="p">
 <div id="ph"><h3>{'Son profil' if F.get('fictif') else 'Son tournoi'} sur dix critères du poste</h3><div id="lg"><span><i style="background:#0B7A3B"></i>fort</span><span><i style="background:#E3A600"></i>moyen</span><span><i style="background:#D4252A"></i>faible</span></div></div>
 <svg id="rad" viewBox="0 0 500 524">{g}</svg>
 <div id="cap">Pointillé : le niveau médian des {B['pluriel']}</div>
 {TABLE}
 <div id="sep"></div>
 <div id="bt"><div><h4><i style="background:#0B7A3B"></i>Points forts</h4><ul>{forts}</ul></div><div><h4><i style="background:#D4252A"></i>À surveiller</h4><ul>{faibles}</ul></div><div><h4>Profils proches</h4><ul>{sim}</ul></div></div>
 <div id="stw"><h4>Sa note parmi les {B['effectif']} {B['pluriel']} du tournoi</h4><div id="st">{ticks}<b style="left:{me:.2f}%"></b><em style="left:0">{lo:.0f}</em><em style="right:0">{hi:.0f}</em></div></div>
</div>
{NOTE}
</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>'''
open(OUT,'w',encoding='utf-8').write(html); print('ok',OUT,F['note'],F['rang'],B['effectif'],B['pluriel'])

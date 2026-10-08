"""Duel entre deux joueurs du même rôle, style « nuit ». Ni rang sur 100 ni note : deux blocs qui disent ce qu'ils mesurent.
Le volume (vraie valeur pour 90 minutes, barre = part du meilleur joueur du rôle) et la réussite (taux, avec le nombre de tentatives).
Les données viennent de duel_export.py.   usage : python3 duel_v2.py <duel_v2.json> <sortie.html> [x|tiktok] [A|B|C|D]
Quatre habillages, les mêmes que les autres plans : A cadre blanc, B nuit (par défaut), C encre, D blanc."""
import json, sys
from da import BASE_CSS, photo, fr, drapeau, credit
from duel_commun import charger, VOL, EFF, tentatives, synthese, buts as but, NOTE1, seuil
OUT=sys.argv[2]; FMT=sys.argv[3] if len(sys.argv)>3 else 'x'; TT=FMT=='tiktok'; TH_=sys.argv[4] if len(sys.argv)>4 else 'B'
D,nA,A,nB,B,sA,sB,PLUR=charger(sys.argv[1])
TH={'A':dict(bg='#F6C41C',ink='#0E1A13',nom='#064A25',doux='#5E6B62',hm='rgba(14,26,19,.72)',ta='#0B7A3B',tb='#0E1A13',piste='#E9EDE8',trait='#E3E8E3',trait2='#EEF1EE',sig='#064A25',carte=True,band=False,blancs=False,syn='#0E1A13',note='rgba(14,26,19,.78)',sep='rgba(14,26,19,.25)'),
    'B':dict(bg='#04331A',ink='#FFFFFF',nom='#FFFFFF',doux='#A9C2B3',hm='#A9C2B3',ta='#F6C41C',tb='#FFFFFF',piste='#0C4429',trait='#1F5236',trait2='#123F29',sig='#FFFFFF',carte=False,band=False,blancs=True,syn='#FFFFFF',note='#A9C2B3',sep='#2A5A3F'),
    'C':dict(bg='#F6C41C',ink='#0E1A13',nom='#064A25',doux='rgba(14,26,19,.72)',hm='rgba(14,26,19,.72)',ta='#064A25',tb='#064A25',piste='rgba(6,74,37,.16)',trait='rgba(6,74,37,.3)',trait2='rgba(6,74,37,.16)',sig='#064A25',carte=False,band=False,blancs=False,syn='#064A25',note='rgba(14,26,19,.78)',sep='rgba(6,74,37,.3)'),
    'D':dict(bg='#FFFFFF',ink='#0E1A13',nom='#064A25',doux='#5E6B62',hm='#5E6B62',ta='#0B7A3B',tb='#0E1A13',piste='#E9EDE8',trait='#E3E8E3',trait2='#EEF1EE',sig='#064A25',carte=False,band=True,blancs=False,syn='#0E1A13',note='#5E6B62',sep='#C9D1CB')}[TH_]
TA,TB,DOUX=TH['ta'],TH['tb'],TH['doux']
PLUR={'ATT':'avants-centres','LAT':'latéraux','DC':'défenseurs centraux','MDF':'milieux défensifs','MIL':'milieux','MOF':'milieux offensifs et ailiers'}[D.get('role','ATT')]
def ligne(a,b,la,lb,wa,wb,lab,sa='',sb=''):
    ga,gb=(a>b and la!=lb),(b>a and la!=lb)      # à valeur affichée égale, personne n'est mis en avant
    return (f'<div class="r"><span class="va{" w" if ga else ""}">{la}<small>{sa}</small></span><span class="ta"><i style="width:{max(wa,2):.0f}%"></i></span>'
            f'<span class="lb">{lab}</span><span class="tb"><i style="width:{max(wb,2):.0f}%"></i></span><span class="vb{" w" if gb else ""}">{lb}<small>{sb}</small></span></div>')
vol=''
for k,lab,d in VOL:
    a,b,m=A[k],B[k],D['max'][k]
    vol+=ligne(a,b,fr(a,d),fr(b,d),a/m*100,b/m*100,lab)
eff=''
for k,lab,num,den in EFF:
    a,b=A[k],B[k]
    ra,ta=tentatives(A,num,den); rb,tb=tentatives(B,num,den)
    eff+=ligne(a,b,f'{a:.0f} %',f'{b:.0f} %',a,b,lab,f'{ra} sur {ta}',f'{rb} sur {tb}')
SYN=synthese(A,B,sA)+'<br>'+synthese(B,A,sB)
cote=lambda nom,J,cl,t:f'<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(int(J["player_id"]))}</div><div><div class="nm">{nom.split(" ")[-1]}</div><div class="m">{drapeau(J["team"],17)}{J["team"]}</div></div></div>'
# géométrie : X = 968 px de large ; TikTok = 890 px (rien à droite de x = 946), tout entre y = 150 et y = 1580
G=dict(w=968,lb=340,lw=288,bar=216,tb=640,h1=116,sco=146,b1=392,b2=786,syn=1132,rh=56) if not TT else dict(w=890,lb=301,lw=288,bar=185,tb=597,h1=244,sco=158,b1=540,b2=1000,syn=1398,rh=66)
css=f'''#c{{background:{TH['bg']};color:{TH['ink']}}}#brand{{color:{TH['sig']}}}#ctx{{color:{TH['hm']}}}#band{{position:absolute;left:0;right:0;top:0;height:{236 if TT else 110}px;background:#F6C41C}}
#card{{position:absolute;left:32px;width:{G['w']+48}px;top:{G['b1']-16}px;height:{G['syn']+78-G['b1']+16}px;background:#fff;border-radius:20px;box-shadow:0 16px 36px rgba(90,60,0,.2)}}
#hero{{left:56px;width:{G['w']}px;right:auto;top:{G['h1']}px;height:auto}}#hero .side{{position:absolute;top:0}}#hero .side.a{{left:0}}#hero .side.b{{right:0}}
#sco{{position:absolute;left:0;right:0;top:{G['sco']-(12 if TH['carte'] else 0)}px;justify-content:center}}
.side{{display:flex;align-items:center;gap:18px;min-width:0}}.side.b{{flex-direction:row-reverse;text-align:right}}
.ph{{flex:none;width:124px;height:124px;margin:5px;border-radius:50%;overflow:hidden;background:#E9EDE8}}.ph img,.ph svg{{width:100%;height:100%;display:block;object-fit:cover}}
.nm{{font:italic 900 54px/1 "BC";text-transform:uppercase;white-space:nowrap;color:{TH['nom']}}}.m{{font:500 18px/1 "IN";color:{TH['hm']};margin-top:8px;white-space:nowrap}}
#sco{{display:flex;align-items:flex-end;gap:22px}}#sco div{{text-align:center}}#sco b{{display:block;font:italic 900 88px/.9 "BC"}}#sco small{{display:block;font:500 15.5px/1 "IN";color:{TH['hm']};margin-top:6px;white-space:nowrap}}
#sco u{{display:block;width:1.5px;height:84px;background:{TH['sep']};margin-bottom:22px;text-decoration:none}}
.blk{{position:absolute;left:56px;width:{G['w']}px}}
.bh{{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:13px;border-bottom:1.5px solid {TH['trait']}}}.bh h3{{font:700 23px/1 "IN";color:{TH['ink']}}}.bh span{{font:500 16px/1 "IN";color:{DOUX}}}
.r{{position:relative;height:{G['rh']}px;border-bottom:1px solid {TH['trait2']}}}
.r>span{{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}}
.r .lb{{left:{G['lb']}px;width:{G['lw']}px;text-align:center;font:500 19px "IN";color:{TH['ink']}}}
.r .ta,.r .tb{{height:9px;width:{G['bar']}px;border-radius:5px;background:{TH['piste']};overflow:hidden}}.r .ta{{left:{G['lb']-8-G['bar']}px}}.r .tb{{left:{G['tb']}px}}
.r .ta i,.r .tb i{{display:block;height:100%;border-radius:5px}}.r .ta i{{background:{TA};margin-left:auto}}.r .tb i{{background:{TB}}}
.r .va,.r .vb{{font:500 22px "IN";color:{DOUX};width:100px}}.r .va{{left:0;text-align:left}}.r .vb{{right:0;text-align:right}}.r .w{{font-weight:700;color:{TH['ink']}}}
.r small{{display:block;font:500 14px/1 "IN";color:{DOUX};margin-top:5px}}.r small:empty{{display:none}}
#syn{{top:{G['syn']}px;text-align:center;font:600 20px/1.55 "IN";color:{TH['syn']}}}
#note{{color:{TH['note']}}}#note b{{color:{TH['sig']}}}'''
if TT: css+=f'''html,body{{width:1080px;height:1920px}}#c{{height:1920px}}#top{{right:134px;top:150px}}
#note{{top:1518px;right:134px;display:block;font-size:16.5px;line-height:1}}#note p{{white-space:nowrap}}#note div{{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}}#note b{{font-size:22px}}'''
LX,LT=('logo_x_blanc.png','logo_tt_blanc.png') if TH['blancs'] else ('logo_x.png','logo_tt.png')
SOC=f'<b><img src="{LX}" alt="X" style="height:22px"><img src="{LT}" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
n1=NOTE1; seuil=seuil(PLUR)
CR=credit(TH['blancs'])
pied=f'<p>{n1} {seuil}</p><div><span>{CR}</span>{SOC}</div>' if TT else f'<span>{n1}<br>{seuil} {CR}</span>{SOC}'
body=f'''{'<div id="band"></div>' if TH['band'] else ''}{'<div id="card"></div>' if TH['carte'] else ''}<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx">Coupe d'Afrique des nations 2023</div></div>
<div id="hero">{cote(nA,A,'a',TA)}<div id="sco"><div><b style="color:{TA}">{int(A['goals'])}</b><small>{but(A)}</small></div><u></u><div><b style="color:{TB}">{int(B['goals'])}</b><small>{but(B)}</small></div></div>{cote(nB,B,'b',TB)}</div>
<div class="blk" id="b1" style="top:{G['b1']}px"><div class="bh"><h3>Ce qu'ils font, pour 90 minutes jouées</h3><span>barre pleine : le meilleur des {D['n']} {PLUR}</span></div>{vol}</div>
<div class="blk" id="b2" style="top:{G['b2']}px"><div class="bh"><h3>Ce qu'ils réussissent</h3><span>taux de réussite, et le nombre de tentatives</span></div>{eff}</div>
<div class="blk" id="syn">{SYN}</div>
<div id="note">{pied}</div>'''
open(OUT,'w',encoding='utf-8').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}{css}</style></head><body><div id="c">{body}</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>')
print('ok',OUT,SYN)

"""Gabarit des posts (validé par Diaby le 13 octobre 2026) : le style de la vidéo de lancement, sans aucun effet.
Produit _pv_1.html (classement des défenses africaines), _pv_2.html (la courbe depuis 2000) et _pv_3.html (points FIFA contre le Rwanda).
Capture : node shotu.mjs _pv_1.html sortie.png 1080 1350 2"""
import json, math
from pathlib import Path
ICI = Path(__file__).parent
W,H=1080,1350
FONTS='''@font-face{font-family:"BC";font-style:italic;font-weight:900;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-900-italic.woff2)}
@font-face{font-family:"BC";font-style:italic;font-weight:800;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-800-italic.woff2)}
@font-face{font-family:"BCS";font-style:italic;font-weight:400;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-400-italic.woff2)}
@font-face{font-family:"BCS";font-style:italic;font-weight:600;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-600-italic.woff2)}
@font-face{font-family:"SC";font-weight:600;src:url(node_modules/@fontsource/barlow-semi-condensed/files/barlow-semi-condensed-latin-600-normal.woff2)}
@font-face{font-family:"SC";font-weight:700;src:url(node_modules/@fontsource/barlow-semi-condensed/files/barlow-semi-condensed-latin-700-normal.woff2)}
@font-face{font-family:"SC";font-weight:800;src:url(node_modules/@fontsource/barlow-semi-condensed/files/barlow-semi-condensed-latin-800-normal.woff2)}'''
CSS=FONTS+'''*{box-sizing:border-box;margin:0;padding:0}html,body{width:1080px;height:1350px;overflow:hidden}
#c{position:relative;width:1080px;height:1350px;overflow:hidden;background:linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%);font-family:"SC";color:#04331A}
.kick{position:absolute;left:64px;top:66px;font:600 26px/1 "SC";letter-spacing:.06em;color:#04331A;white-space:nowrap}.kick b{font-weight:800}
.h1{position:absolute;left:58px;top:104px;font:italic 900 150px/.9 "BC";color:#064A25;white-space:nowrap}
.h2{position:absolute;left:64px;top:244px;font:italic 800 76px/1 "BC";color:#D4252A;white-space:nowrap}
.ghost{position:absolute;right:56px;top:46px;font:italic 900 330px/1 "BC";color:transparent;-webkit-text-stroke:4px #FFF6D0;opacity:.6;white-space:nowrap}
#foot{position:absolute;left:64px;right:64px;top:1186px;display:flex;align-items:center;gap:14px}#foot>img{width:64px;height:64px;border-radius:50%;display:block}
.wm{font:italic 400 48px/1 "BCS";color:#064A25;white-space:nowrap}.wm i{font-style:inherit;font-weight:600}
.soc{margin-left:auto;display:flex;align-items:center;gap:12px;font:700 28px/1 "SC";color:#064A25}.soc img{display:block}
#src{position:absolute;left:64px;top:1270px;font:600 19px/1 "SC";color:rgba(4,51,26,.75);white-space:nowrap}
.bigR{position:absolute;left:64px;display:flex;align-items:center;gap:18px;white-space:nowrap}.bigR b{font:italic 900 140px/.86 "BC";color:#064A25}
.bigR span{font:800 30px/1.15 "SC";letter-spacing:.05em;color:#04331A}.bigR em{font-style:normal;color:#D4252A}
.ax{stroke:#064A25;stroke-width:4;fill:none}.pl{stroke:#FCE38A;stroke-width:3}
.t{font:700 26px "SC";fill:#064A25}
.leg{position:absolute;left:64px;display:flex;gap:26px;align-items:center;font:800 25px/1 "SC";letter-spacing:.04em;color:#04331A;white-space:nowrap}.leg span{display:flex;align-items:center;gap:10px}'''
def trame(fx=1080,fy=0,col='#FDEBA6',op='0.85',H=H):
    g='';st=30;y=st/2;row=0
    while y<H:
        x=st/2+(st/2 if row%2 else 0)
        while x<W: d=math.hypot(x-fx,y-fy)/1500; g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.2+9*max(0,1-d)**2.6:.2f}"/>'; x+=st
        y+=st;row+=1
    return f'<svg style="position:absolute;left:0;top:0" width="{W}" height="{H}"><g fill="{col}" fill-opacity="{op}">{g}</g></svg>'
# TikTok (1080 x 1920) : la même page X (1350 de haut), en taille réelle, descendue de DY_TT. Elle tient dans la zone sûre
# (rien au-dessus de 150 px ni dans les 340 px du bas). À droite, sous y = 880, rester avant x = 946 (boutons TikTok).
DY_TT=200
def page(kick,h1,h2,ghost,body,src,tt=False):
    css,tr,z0,z1=CSS,trame(),'',''
    if tt:
        css=CSS.replace('html,body{width:1080px;height:1350px','html,body{width:1080px;height:1920px').replace('#c{position:relative;width:1080px;height:1350px','#c{position:relative;width:1080px;height:1920px')+'#foot{right:134px}'
        tr=trame(H=1920); z0=f'<div style="position:absolute;left:0;top:{DY_TT}px;width:1080px;height:1350px">'; z1='</div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div id="c">{tr}{z0}
<div class="ghost">{ghost}</div><div class="kick">{kick}</div><div class="h1">{h1}</div><div class="h2">{h2}</div>{body}
<div id="foot"><img src="logo-verte.png"><div class="wm">Mali<i>Data</i>Foot</div><div class="soc"><img src="logo_x.png" style="height:28px"><img src="logo_tt.png" style="height:36px">@MaliDataFoot</div></div>
<div id="src">{src}</div>{z1}</div><script>document.fonts.ready.then(()=>{{window.READY=true}})</script></body></html>'''
# Les trois couleurs de la DA (comme dans la vidéo : scènes jaunes, scènes vertes, éléments blancs).
# Même mise en page ; seules les couleurs changent.
FOND_JAUNE='linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)'
TEINTES={
 'vert':{'fond':'radial-gradient(120% 70% at 30% 26%, #128F47 0%, #0B7A3B 30%, #064A25 62%, #04331A 100%)',
         'cible':{'.h2{position:absolute;left:64px;top:244px;font:italic 800 76px/1 "BC";color:#D4252A':'.h2{position:absolute;left:64px;top:244px;font:italic 800 76px/1 "BC";color:#F6C41C',
                  '.bigR em{font-style:normal;color:#D4252A}':'.bigR em{font-style:normal;color:#F6C41C}',
                  '<img src="logo_x.png" style="height:28px">':'<img src="logo_x.png" style="height:28px;filter:brightness(0) invert(1)">',
                  '<img src="logo_tt.png" style="height:36px">':'<img src="logo_tt.png" style="height:36px;filter:brightness(0) invert(1)">',
                  'fill-opacity="0.85"':'fill-opacity="0.5"'},
         'couleurs':{'#0B7A3B':'#F6C41C','#064A25':'#FFFFFF','#04331A':'#FFFFFF','#FFF3C4':'#CFE6D6','#FDEBA6':'#19A552',
                     '#FFF6D0':'#19A552','#FCE38A':'#19A552','rgba(4,51,26,.75)':'rgba(255,255,255,.75)','rgba(4,51,26,.8)':'rgba(255,255,255,.8)'}},
 'blanc':{'fond':'#FFFFFF','cible':{},
          'couleurs':{'#FFF3C4':'#E3E8E3','#FDEBA6':'#EEF2EC','#FFF6D0':'#DDE3DD','#FCE38A':'#E3E8E3'}}}
def teinte(html,nom):
    if nom=='jaune': return html
    T=TEINTES[nom]; html=html.replace(FOND_JAUNE,'@@FOND@@')
    for a,b in T['cible'].items(): html=html.replace(a,b)
    for a,b in T['couleurs'].items(): html=html.replace(a,b)
    return html.replace('@@FOND@@',T['fond'])
def ecrire(k,html):
    for nom in ('jaune','vert','blanc'):
        open(ICI/f'_pv_{k}{"" if nom=="jaune" else "_"+nom}.html','w',encoding='utf-8').write(teinte(html,nom))
fr=lambda v,d=2:f'{v:.{d}f}'.replace('.',',')
# drapeaux ronds (dessinés sur 20 x 20)
v3=lambda a,b,c:f'<rect width="6.7" height="20" fill="{a}"/><rect x="6.7" width="6.7" height="20" fill="{b}"/><rect x="13.3" width="6.7" height="20" fill="{c}"/>'
h3=lambda a,b,c:f'<rect width="20" height="6.7" fill="{a}"/><rect y="6.7" width="20" height="6.7" fill="{b}"/><rect y="13.3" width="20" height="6.7" fill="{c}"/>'
def et(cx,cy,r,c): return '<polygon points="'+' '.join(f'{cx+(r if k%2==0 else r*.4)*math.sin(k*math.pi/5):.2f},{cy-(r if k%2==0 else r*.4)*math.cos(k*math.pi/5):.2f}' for k in range(10))+f'" fill="{c}"/>'
DR={'Morocco':'<rect width="20" height="20" fill="#C1272D"/><polygon points="10,5.2 12.8,13.9 5.4,8.5 14.6,8.5 7.2,13.9" fill="none" stroke="#006233" stroke-width="1.1"/>',
 'Mali':v3('#14B53A','#FCD116','#CE1126'),'Senegal':v3('#00853F','#FDEF42','#E31B23')+et(10,10,2.6,'#00853F'),
 'Egypt':h3('#CE1126','#FFFFFF','#000000')+'<rect x="8.6" y="8" width="2.8" height="4" rx=".8" fill="#C09300"/>',
 'Tunisia':'<rect width="20" height="20" fill="#E70013"/><circle cx="10" cy="10" r="5.2" fill="#fff"/><circle cx="10.6" cy="10" r="3.6" fill="#E70013"/><circle cx="11.6" cy="10" r="2.9" fill="#fff"/>'+et(11.8,10,1.7,'#E70013'),
 'Ivory Coast':v3('#F77F00','#FFFFFF','#009E60'),
 'DR Congo':'<rect width="20" height="20" fill="#007FFF"/><path d="M-2 22L22 -2" stroke="#F7D618" stroke-width="7"/><path d="M-2 22L22 -2" stroke="#CE1021" stroke-width="4.6"/>'+et(5.6,6.2,2.8,'#F7D618'),
 'Nigeria':v3('#008751','#FFFFFF','#008751'),
 'Angola':'<rect width="20" height="10" fill="#CC092F"/><rect y="10" width="20" height="10" fill="#000"/>'+et(9,9.5,1.8,'#FFCB00')+'<path d="M7 13.5 A4.5 4.5 0 0 0 13.5 8" stroke="#FFCB00" stroke-width="1.2" fill="none"/>',
 'Algeria':'<rect width="10" height="20" fill="#006233"/><rect x="10" width="10" height="20" fill="#fff"/><circle cx="10" cy="10" r="4.6" fill="#D21034"/><circle cx="11.3" cy="10" r="3.8" fill="#fff"/>'+et(12,10,1.8,'#D21034'),
 'Cameroon':v3('#007A5E','#CE1126','#FCD116')+et(10,10,2.6,'#FCD116'),
 'South Africa':'<rect width="20" height="10" fill="#E03C31"/><rect y="10" width="20" height="10" fill="#001489"/><path d="M-1 -1L8 10L-1 21M8 10H21" stroke="#fff" stroke-width="6.6" fill="none"/><path d="M-1 -1L8 10L-1 21M8 10H21" stroke="#007749" stroke-width="4" fill="none"/><polygon points="-1,1.2 6.6,10 -1,18.8" fill="#FFB81C"/><polygon points="-1,3.2 4.9,10 -1,16.8" fill="#000"/>'}
FRN={'Morocco':'Maroc','Mali':'Mali','Senegal':'Sénégal','Egypt':'Égypte','Tunisia':'Tunisie','Ivory Coast':"Côte d'Ivoire",'DR Congo':'RD Congo','Nigeria':'Nigeria','Angola':'Angola','Algeria':'Algérie','Cameroon':'Cameroun','South Africa':'Afrique du Sud'}
def drap(p,t=38):
    k='k'+''.join(c for c in p if c.isalnum())  # identifiant sans espace (« DR Congo » cassait le découpage rond)
    return f'<svg width="{t}" height="{t}" viewBox="-1 -1 22 22" style="display:block"><clipPath id="{k}"><circle cx="10" cy="10" r="10"/></clipPath><g clip-path="url(#{k})">{DR[p]}</g><circle cx="10" cy="10" r="10" fill="none" stroke="#fff" stroke-width="1.4"/></svg>'

# ---------- post 1, image 1 : le classement des défenses africaines
A=json.load(open(ICI/'../outputs/analyses/defense_afrique.json',encoding='utf-8')); D=json.load(open(ICI/'../outputs/analyses/defense_aigles.json',encoding='utf-8'))
def p1_image1(tt=False):
    # TikTok : barres plus courtes, pour que les chiffres des rangs 6 à 10 restent avant x = 946
    E=A['equipes'][:10]; mx=max(e['par_match'] for e in E); x0,x1=470,(830 if tt else 880); top=380; rh=58; b=''
    for e in E:
        # barres des autres pays : 1C, vert foncé atténué (choix de Diaby, 14/10/2026)
        y=top+(e['rang']-1)*rh; mali=e['equipe']=='Mali'; c='#0B7A3B' if mali else 'rgba(6,74,37,.35)'; L=e['par_match']/mx*(x1-x0)
        b+=(f'<div style="position:absolute;left:64px;top:{y}px;width:44px;text-align:right;font:italic 900 40px/1 BC;color:#064A25">{e["rang"]}</div>'
            f'<div style="position:absolute;left:126px;top:{y}px">{drap(e["equipe"])}</div>'
            f'<div style="position:absolute;left:180px;top:{y+6}px;font:800 30px/1 SC;letter-spacing:.03em;text-transform:uppercase;color:{"#0B7A3B" if mali else "#04331A"}">{FRN[e["equipe"]]}</div>'
            f'<div style="position:absolute;left:{x0}px;top:{y+8}px;width:{L:.0f}px;height:24px;border-radius:3px;background:{c}"></div>'
            f'<div style="position:absolute;left:{x0+L+14:.0f}px;top:{y+1}px;font:italic 900 40px/1 BC;color:{"#0B7A3B" if mali else "#064A25"}">{fr(e["par_match"])}</div>')
    r=D['reference']['par_match']
    b+=f'<div class="bigR" style="top:{top+10*rh+44}px"><b>{A["mali"]["rang"]}<span style="font:italic 900 70px BC;color:#064A25;letter-spacing:0">e</span></b><span>DÉFENSE D\'AFRIQUE DEPUIS 2020<br>CONTRE <em>{fr(r)}</em> BUT PAR MATCH DE 2000 À 2019</span></div>'
    return page('DEPUIS 2020 · MATCHS OFFICIELS · <b>BUTS ENCAISSÉS PAR MATCH</b>','LA DÉFENSE','DES AIGLES',fr(A['mali']['par_match']),b,
         'Matchs officiels : CAN et éliminatoires (CAN, Coupe du monde) · Données : résultats internationaux (martj42)',tt)
ecrire(1,p1_image1()); ecrire('1_tt',p1_image1(True))

# ---------- post 1, image 2 : la courbe depuis 2000, avec ce que le Mali d'avant aurait encaissé
import datetime as dt
def p1_image2(tt=False):
    M=D['matchs']; n=20  # 20 matchs : sur 10, la courbe faisait de fausses grosses chutes (Diaby, 14/10/2026)
    roll=lambda k:[sum(m[k] for m in M[i-n+1:i+1])/n for i in range(n-1,len(M))]
    re_,at_=roll('buts_contre'),roll('attendu'); ds=[dt.date.fromisoformat(m['date']) for m in M][n-1:]
    cx0,cx1,cy0,cy1=110,900,390,880; t0,t1=dt.date(2001,1,1),dt.date(2026,12,31); ymax=2.0
    sx=lambda d:cx0+(d-t0).days/(t1-t0).days*(cx1-cx0); sy=lambda v:cy1-v/ymax*(cy1-cy0)
    g=f'<line class="ax" x1="{cx0}" y1="{cy0}" x2="{cx0}" y2="{cy1}"/><line class="ax" x1="{cx0}" y1="{cy1}" x2="{cx1}" y2="{cy1}"/>'
    for v in (0.5,1,1.5,2): g+=f'<text class="t" x="{cx0-14}" y="{sy(v)+9:.0f}" text-anchor="end">{fr(v,1).replace(",0","")}</text>'
    for a in (2005,2010,2015,2020,2025): g+=f'<text class="t" x="{sx(dt.date(a,1,1)):.0f}" y="{cy1+38}" text-anchor="middle">{a}</text>'
    x20=sx(dt.date(2020,1,1)); g+=f'<line class="pl" x1="{x20:.0f}" y1="{cy0}" x2="{x20:.0f}" y2="{cy1}"/>'
    pa=lambda vs:'M'+'L'.join(f'{sx(d):.1f} {sy(v):.1f}' for d,v in zip(ds,vs))
    g+=f'<path d="{pa(at_)}" fill="none" stroke="#D4252A" stroke-width="4" stroke-dasharray="11 9"/><path d="{pa(re_)}" fill="none" stroke="#0B7A3B" stroke-width="6" stroke-linejoin="round"/>'
    body=f'<svg style="position:absolute;left:0;top:0" width="{W}" height="{H}">{g}</svg>'
    body+=f'<div class="leg" style="top:{cy1+70}px{";font-size:23px;gap:20px" if tt else ""}"><span><i style="display:block;width:34px;height:9px;border-radius:5px;background:#0B7A3B"></i>BUTS ENCAISSÉS</span><span><svg width="36" height="9"><line x1="0" y1="4.5" x2="36" y2="4.5" stroke="#D4252A" stroke-width="5" stroke-dasharray="11 7"/></svg>LE MALI DE 2000-2019, FACE AUX MÊMES ADVERSAIRES</span></div>'
    body+=f'<div style="position:absolute;left:64px;top:{cy1+104}px;font:600 22px/1 SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">PAR MATCH, EN MOYENNE SUR LES {n} DERNIERS MATCHS OFFICIELS</div>'
    AE=D['a_adversaires_egaux']
    body+=f'<div class="bigR" style="top:{cy1+160}px"><b>{AE["buts_reels"]}</b><span>BUTS ENCAISSÉS EN {D["depuis_2020"]["matchs"]} MATCHS DEPUIS 2020<br>POUR <em>{round(AE["buts_attendus"])}</em> ATTENDUS FACE AUX MÊMES ADVERSAIRES</span></div>'
    return page('2000-2026 · MATCHS OFFICIELS · <b>DEUX FOIS MOINS DE BUTS ENCAISSÉS</b>','LA DÉFENSE','DEPUIS 2000','22',body,
         'Attendus : selon la force de l\'adversaire (classement Elo) et le lieu · Données : résultats internationaux (martj42)',tt)
ecrire(2,p1_image2()); ecrire('2_tt',p1_image2(True))

# ---------- post 2 : le classement FIFA, gros chiffres empilés comme « L'anatomie d'un but »
F=json.load(open(ICI/'../outputs/analyses/fifa_rwanda.json',encoding='utf-8')); u=F['un_match']; S={s['resultats']:s['ecart'] for s in F['deux_matchs']}
sg=lambda v:('+' if v>0 else '−')+fr(abs(v),1)
b=''
for i,(r,lab) in enumerate((('V','SI VICTOIRE'),('N','SI NUL'),('D','SI DÉFAITE'))):
    y=380+i*215; c='#0B7A3B' if u[r]>0 else '#D4252A'
    b+=f'<div style="position:absolute;left:58px;top:{y}px;font:italic 900 170px/.86 BC;color:{c};white-space:nowrap">{sg(u[r])}</div><div style="position:absolute;left:64px;top:{y+152}px;font:800 30px/1 SC;letter-spacing:.05em;color:#04331A">POINTS {lab}</div>'
b+='<div style="position:absolute;left:600px;top:392px;font:800 26px/1 SC;letter-spacing:.06em;color:#04331A">SUR LES DEUX MATCHS</div>'
rows=[('VICTOIRE + VICTOIRE','VV'),('VICTOIRE + NUL','VN'),('NUL + VICTOIRE','NV'),('NUL + NUL','NN'),('DÉFAITE + VICTOIRE','DV'),('DÉFAITE + DÉFAITE','DD')]
for i,(lab,k) in enumerate(rows):
    y=444+i*70; v=S[k]; c='#0B7A3B' if v>0 else '#D4252A'
    b+=f'<div style="position:absolute;left:600px;top:{y}px;width:416px;border-top:3px solid #064A25"></div><div style="position:absolute;left:600px;top:{y+20}px;font:800 24px/1 SC;letter-spacing:.04em;color:#04331A">{lab}</div><div style="position:absolute;right:64px;top:{y+12}px;font:italic 900 46px/1 BC;color:{c}">{sg(v)}</div>'
b+=f'<div class="bigR" style="top:1030px"><b>{fr(F["attendu_mali"],2)}<span style="font:italic 900 70px BC;color:#064A25;letter-spacing:0"> /1</span></b><span>RÉSULTAT ATTENDU PAR LA FIFA (1 = VICTOIRE) :<br>GAGNER RAPPORTE PEU, NE PAS GAGNER <em>COÛTE CHER</em></span></div>'
ecrire(3,page('CAN 2027 · CONTRE LE RWANDA EN NOVEMBRE · <b>POINTS FIFA DU MALI</b>','GAGNER','DEUX FOIS',sg(S['VV']),b,
     'Points du 7 octobre 2026 : Mali 1474,14, Rwanda 1156,16 · Formule officielle de la FIFA · Calcul MaliDataFoot'))
print('ok')

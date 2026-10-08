"""Direction artistique MaliDataFoot, version « pro » : le cadre commun à tous les visuels fixes 1080 x 1350.
Fond jaune uni, signature en haut à gauche, grand titre penché, cadre blanc, pied de page avec les comptes.
Aucun effet : ni grain, ni trame, ni dégradé. Deux polices : Barlow Condensed (titres, signature) et Inter (tout le reste)."""
F='node_modules/@fontsource/'
OR,VERT,VERT_D,ROUGE,ENCRE,GRIS,TRAIT='#F6C41C','#0B7A3B','#064A25','#D4252A','#0E1A13','#5E6B62','#E3E8E3'
from decimal import Decimal, ROUND_HALF_UP
def fr(v,d=1):
    """Nombre à la française, arrondi comme à l'école (2,25 donne 2,3) : un lecteur qui refait le calcul doit trouver pareil."""
    return str(Decimal(repr(round(float(v),6))).quantize(Decimal(1).scaleb(-d),rounding=ROUND_HALF_UP)).replace('.',',')
def _ff(fam,pkg,w,st='normal'): return f'@font-face{{font-family:"{fam}";font-style:{st};font-weight:{w};src:url({F}{pkg}/files/{pkg}-latin-{w}-{st}.woff2)}}'
BASE_CSS=_ff('BC','barlow-condensed',900,'italic')+_ff('BCS','barlow-condensed',400,'italic')+_ff('BCS','barlow-condensed',600,'italic')+''.join(_ff('IN','inter',w) for w in (400,500,600,700))+'''
:root{--or:#F6C41C;--vert:#0B7A3B;--vert-d:#064A25;--rouge:#D4252A;--encre:#0E1A13;--gris:#5E6B62;--trait:#E3E8E3}
*{box-sizing:border-box;margin:0;padding:0}html,body{width:1080px;height:1350px;overflow:hidden}
#c{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F6C41C;font-family:"IN",sans-serif;color:var(--encre);font-variant-numeric:tabular-nums;font-feature-settings:"cv11","ss01"}
#top{position:absolute;left:56px;right:56px;top:26px;display:flex;justify-content:space-between;align-items:center}
#brand{display:flex;align-items:center;gap:15px;color:var(--vert-d)}
#brand img{width:72px;height:72px;border-radius:50%;display:block}
#brand b{font:italic 400 47px/1 "BCS";letter-spacing:.005em;white-space:nowrap}#brand b i{font-weight:600}
#ctx{font:600 21px/1 "IN";color:rgba(14,26,19,.72)}
#hero{position:absolute;left:56px;right:62px;top:128px;height:160px}
#sc{position:absolute;right:0;top:0;text-align:right}
#sc small{display:block;font:600 19px/1 "IN";color:rgba(14,26,19,.7)}
#sc b{display:block;font:italic 900 112px/.95 "BC";color:var(--vert-d);margin-top:6px}
#sc span{display:block;font:600 21px/1 "IN";color:var(--encre);margin-top:2px}
#p{position:absolute;left:56px;top:312px;width:968px;height:930px;background:#fff;border-radius:20px;box-shadow:0 16px 36px rgba(90,60,0,.2)}
#ph{position:absolute;left:36px;right:36px;top:28px;display:flex;justify-content:space-between;align-items:center}
#ph h3{font:700 23px/1 "IN";color:var(--encre)}
#note{position:absolute;left:56px;right:56px;top:1264px;display:flex;justify-content:space-between;align-items:flex-start;font:500 17.5px/1.4 "IN";color:rgba(14,26,19,.78);white-space:nowrap}
#note b{display:flex;align-items:center;gap:12px;font:700 23px/1 "IN";color:var(--vert-d)}#note b img{display:block}
'''
# coupure des libellés autour d'un radar (présentation seulement ; la liste des critères vient du pipeline)
COUPE={'passes_into_box_p90':['Passes dans','la surface'],'prog_passes_p90':['Passes','progressives'],'prog_carries_p90':['Conduites','progressives'],
       'dribbles_won_p90':['Dribbles','réussis'],'tackles_interceptions_p90':['Tacles +','interceptions'],'aerials_won_p90':['Duels aériens','gagnés'],
       'receptions_in_box_p90':['Ballons reçus','dans la surface'],'np_goals_p90':['Buts hors','penalty'],'npxg_p90':['Buts attendus','hors penalty'],'xa_p90':['Passes déc.','attendues'],
       'passes_final_third_p90':['Passes vers le','dernier tiers'],'pass_pct':['Passes','réussies']}
import math, os
def radar(criteres, series, cx=250, cy=262, R=158):
    """Radar sans chiffres. criteres : [(clé, nom)] ; series : [(centiles, trait, fond, opacité du fond)].
    Anneaux à 25, 75, 100 ; pointillé à 50 = le niveau médian du bassin."""
    N=len(criteres); ang=lambda i:-math.pi/2+i*2*math.pi/N
    pol=lambda r,i:(cx+r*math.cos(ang(i)), cy+r*math.sin(ang(i)))
    g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R*v/100:.1f}" fill="none" stroke="#DCE1DC" stroke-width="1.5"/>' for v in (25,75,100))
    g+=f'<circle cx="{cx}" cy="{cy}" r="{R*.5:.1f}" fill="none" stroke="#8E9A91" stroke-width="1.5" stroke-dasharray="3 6"/>'
    for i in range(N):
        x,y=pol(R,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E4E8E3" stroke-width="1.3"/>'
    for pcts,trait,fond,op in series:
        pts=[pol(R*max(p,2)/100,i) for i,p in enumerate(pcts)]
        g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{fond}" fill-opacity="{op}" stroke="{trait}" stroke-width="3" stroke-linejoin="round"/>'
        g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="{trait}" stroke-width="3"/>' for x,y in pts)
    for i,(k,nom) in enumerate(criteres):
        a=ang(i); deg=math.degrees(a)+90; bas=math.sin(a)>.15; lines=COUPE.get(k,[nom]); n=len(lines)   # en bas, le texte est retourné pour rester lisible
        for j,t in enumerate(lines):
            rr=R+22+((n-1-j) if not bas else j)*21+(4 if bas else 0); x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
            g+=f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" transform="rotate({deg+(180 if bas else 0):.1f} {x:.1f} {y:.1f})" class="rl">{t}</text>'
    return g
SILHOUETTE='<svg viewBox="0 0 100 100"><rect width="100" height="100" fill="#E9EDE8"/><circle cx="50" cy="39" r="18" fill="#A9B5AC"/><path d="M16 104C16 77 31 65 50 65C69 65 84 77 84 104Z" fill="#A9B5AC"/></svg>'
def photo(player_id):
    """Portrait du joueur s'il a été déposé dans photos/<identifiant>.png, sinon une silhouette neutre."""
    p=f'photos/{player_id}.png'
    return f'<img src="{p}" alt="">' if os.path.exists(p) else SILHOUETTE
ordi=lambda n:('1er' if n==1 else f'{n}e')
# crédit des données : la licence StatsBomb demande leur logo, pas seulement leur nom. Le logo n'est jamais recoloré ;
# sur fond sombre il est posé sur une pastille blanche.
CREDIT_TXT='Données StatsBomb Open Data.'
def credit(sombre=False, h=22):
    img=f'<img src="logo_statsbomb.png" alt="StatsBomb" style="display:inline-block;height:{h}px;width:auto;vertical-align:{-h*.24:.1f}px">'
    if sombre: img=f'<span style="display:inline-block;background:#fff;border-radius:6px;padding:4px 8px 3px;vertical-align:{-h*.36:.1f}px;line-height:0">{img.replace(f"vertical-align:{-h*.24:.1f}px","vertical-align:0")}</span>'
    return f'Données {img}'
def avec_logo(texte, sombre=False, h=22):
    return texte.replace(CREDIT_TXT, credit(sombre,h))
SOC='<b><img src="logo_x.png" alt="X" style="height:22px"><img src="logo_tt.png" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
# format vertical TikTok : tout le contenu entre y = 150 et y = 1580, et à gauche de x = 946
CSS_TIKTOK='''
html,body{width:1080px;height:1920px}#c{height:1920px}
#top{right:134px;top:150px}
#hero{right:134px;top:250px}
#p{top:428px;width:890px;height:1078px}
#note{top:1518px;right:134px;display:block;font-size:16.5px;line-height:1}
#note p{white-space:nowrap}
#note div{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}
#note b{font-size:22px}
'''
FIT="document.querySelectorAll('[data-fit]').forEach(e=>{let s=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth+1&&s>20){s-=1;e.style.fontSize=s+'px'}});"
def _etoile(cx,cy,r,coul):
    p=' '.join(f'{cx+(r if k%2==0 else r*.4)*math.sin(k*math.pi/5):.2f},{cy-(r if k%2==0 else r*.4)*math.cos(k*math.pi/5):.2f}' for k in range(10))
    return f'<polygon points="{p}" fill="{coul}"/>'
# drapeaux ronds, comme dans les applis de foot : dessinés sur un carré de 20 x 20, puis coupés en cercle
_v=lambda a,b,c:f'<rect width="6.67" height="20" fill="{a}"/><rect x="6.67" width="6.67" height="20" fill="{b}"/><rect x="13.33" width="6.67" height="20" fill="{c}"/>'
_h=lambda a,b,c:f'<rect width="20" height="6.67" fill="{a}"/><rect y="6.67" width="20" height="6.67" fill="{b}"/><rect y="13.33" width="20" height="6.67" fill="{c}"/>'
DRAPEAUX={
 'Mali':_v('#14B53A','#FCD116','#CE1126'), 'Nigeria':_v('#008751','#FFFFFF','#008751'), "Côte d'Ivoire":_v('#F77F00','#FFFFFF','#009E60'),
 'Guinée':_v('#CE1126','#FCD116','#009460'), 'Sénégal':_v('#00853F','#FDEF42','#E31B23')+_etoile(10,10,2.6,'#00853F'),
 'Cameroun':_v('#007A5E','#CE1126','#FCD116')+_etoile(10,10,2.6,'#FCD116'),
 'Burkina Faso':'<rect width="20" height="10" fill="#EF2B2D"/><rect y="10" width="20" height="10" fill="#009E49"/>'+_etoile(10,10,3.6,'#FCD116'),
 'Égypte':_h('#CE1126','#FFFFFF','#000000')+'<rect x="8.6" y="8" width="2.8" height="4" rx=".8" fill="#C09300"/>',
 'RD Congo':'<rect width="20" height="20" fill="#007FFF"/><path d="M-2 22L22 -2" stroke="#F7D618" stroke-width="7"/><path d="M-2 22L22 -2" stroke="#CE1021" stroke-width="4.6"/>'+_etoile(5.6,6.2,2.8,'#F7D618'),
 'Maroc':'<rect width="20" height="20" fill="#C1272D"/><polygon points="10,5.2 12.8,13.9 5.4,8.5 14.6,8.5 7.2,13.9" fill="none" stroke="#006233" stroke-width="1"/>',
 'Ghana':_h('#CE1126','#FCD116','#006B3F')+_etoile(10,10,2.6,'#000'),
}
_ALIAS={'Ivory Coast':"Côte d'Ivoire",'Egypt':'Égypte','Congo DR':'RD Congo','Senegal':'Sénégal','Cameroon':'Cameroun','Guinea':'Guinée','Morocco':'Maroc'}
def drapeau(pays, h=18, marge='0 7px 0 0'):
    """Petit drapeau rond, à mettre devant un nom de pays. Rien si le pays n'est pas encore dessiné."""
    d=DRAPEAUX.get(_ALIAS.get(pays,pays))
    if not d: return ''
    t=round(h*1.15)
    return (f'<svg width="{t}" height="{t}" viewBox="0 0 20 20" style="display:inline-block;vertical-align:-{t*.2:.1f}px;margin:{marge};border-radius:50%;overflow:hidden;box-shadow:0 0 0 1.5px rgba(255,255,255,.9),0 0 0 2.5px rgba(0,0,0,.14)">{d}</svg>')
def pays(nom, h=18):
    return f'{drapeau(nom,h)}{_ALIAS.get(nom,nom)}'
def score(a, ba, bb, b, h=20):
    """Affiche façon tableau de score : drapeau, équipe, score, équipe, drapeau."""
    return f'{drapeau(a,h)}{a} {ba}-{bb} {b}{drapeau(b,h,"0 0 0 8px")}'
def page(ctx, hero, panel, note, css='', fmt='x'):
    """Assemble un visuel : contexte en haut à droite, bloc titre, contenu du cadre blanc, note de bas de page.
    note : une chaîne (deux lignes séparées par <br>) ou un couple (ligne 1, ligne 2). fmt : 'x' (1080 x 1350) ou 'tiktok' (1080 x 1920)."""
    l1,l2=note if isinstance(note,(tuple,list)) else (note.split('<br>')+[''])[:2]
    l1,l2=avec_logo(l1),avec_logo(l2)
    pied=f'<p>{l1}</p><div><span>{l2}</span>{SOC}</div>' if fmt=='tiktok' else f'<span>{l1}<br>{l2}</span>{SOC}'
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}{css}{CSS_TIKTOK if fmt=='tiktok' else ''}</style></head><body><div id="c" class="{fmt}">
<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx">{ctx}</div></div>
<div id="hero">{hero}</div>
<div id="p">{panel}</div>
<div id="note">{pied}</div>
</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{{FIT}window.READY=true}})</script></body></html>'''

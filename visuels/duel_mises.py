"""Trois autres mises en scène du duel, vraiment différentes de la « nuit » (duel_v2.py), avec la même logique et les mêmes chiffres :
A « cadre blanc » : radar (part du meilleur du poste) + tableau des vraies valeurs ; C « encre » : deux ronds reliés par critère ;
D « blanc » : une barre d'écart par critère, triée du plus favorable à l'un au plus favorable à l'autre.
Format Twitter/X 1080 x 1350 (le vertical se fait une fois la mise en scène choisie).
usage : python3 duel_mises.py <duel_v2.json> <sortie.html> <A|C|D>"""
import sys, math
from da import BASE_CSS, photo, fr, drapeau, credit
from duel_commun import charger, VOL, EFF, COURT, tentatives, synthese, buts, NOTE1, seuil
D,nA,A,nB,B,sA,sB,PLUR=charger(sys.argv[1]); OUT=sys.argv[2]; V=sys.argv[3]
SYN=synthese(A,B,sA)+'<br>'+synthese(B,A,sB)
part=lambda J,k:J[k]/D['max'][k]*100                     # volume ramené au meilleur joueur du poste (0 à 100)
val=lambda J,k,d:fr(J[k],d)
def tete(sig,ctx): return f'<div id="top"><div id="brand" style="color:{sig}"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx" style="color:{ctx}">Coupe d\'Afrique des nations 2023</div></div>'
def pied(coul,coulh):
    soc=f'<b style="color:{coulh}"><img src="logo_x.png" alt="X" style="height:22px"><img src="logo_tt.png" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
    return f'<div id="note" style="color:{coul}"><span>{NOTE1}<br>{seuil(PLUR)} {credit()}</span>{soc}</div>'
COMMUN='''.ph{flex:none;border-radius:50%;overflow:hidden;background:#E9EDE8}.ph img,.ph svg{width:100%;height:100%;display:block;object-fit:cover}
.nm{font:italic 900 54px/1 "BC";text-transform:uppercase;white-space:nowrap}
.r{position:relative}.r>span{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}
small{display:block;font:500 14px/1 "IN";margin-top:5px}'''

if V=='A':      # ---------------- cadre blanc : radar à six branches + tableau, puis les taux de réussite
    TA,TB,INK,GRIS='#0B7A3B','#0E1A13','#0E1A13','#5E6B62'
    cx,cy,R=250,214,140; N=len(VOL); ang=lambda i:-math.pi/2+i*2*math.pi/N; pol=lambda r,i:(cx+r*math.cos(ang(i)),cy+r*math.sin(ang(i)))
    g=''.join(f'<circle cx="{cx}" cy="{cy}" r="{R*v/100:.1f}" fill="none" stroke="#DCE1DC" stroke-width="1.5"/>' for v in (25,50,75))
    g+=f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#8E9A91" stroke-width="1.8"/>'
    for i in range(N): x,y=pol(R,i); g+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E4E8E3" stroke-width="1.3"/>'
    for J,t,f,op in ((B,TB,TB,.07),(A,TA,'#19A552',.2)):
        pts=[pol(R*max(part(J,k),2)/100,i) for i,(k,_,_) in enumerate(VOL)]
        g+='<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{f}" fill-opacity="{op}" stroke="{t}" stroke-width="3" stroke-linejoin="round"/>'
        g+=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="{t}" stroke-width="3"/>' for x,y in pts)
    for i,(k,lab,_) in enumerate(VOL):
        a=ang(i); lines=COURT.get(k,[lab]); n=len(lines); co,si=math.cos(a),math.sin(a)
        anc='middle' if abs(co)<.3 else ('start' if co>0 else 'end'); x=cx+(R+16)*co; y0=cy+(R+16)*si+(6 if abs(si)<.3 else (-(n-1)*20-4 if si<0 else 16))
        g+=''.join(f'<text x="{x:.1f}" y="{y0+j*20:.1f}" text-anchor="{anc}" class="rl">{t}</text>' for j,t in enumerate(lines))
    NOMC={'npxg_p90':'Buts attendus hors pen.','receptions_in_box_p90':'Reçus dans la surface'}
    def lv(k,lab,d):
        a,b=A[k],B[k]; la,lb=val(A,k,d),val(B,k,d)
        return f'<div class="r"><span class="n">{NOMC.get(k,lab)}</span><span class="ca{" w" if a>b and la!=lb else ""}">{la}</span><span class="cb{" w" if b>a and la!=lb else ""}">{lb}</span></div>'
    def le(k,lab,num,den):
        a,b=A[k],B[k]; ra,ta=tentatives(A,num,den); rb,tb=tentatives(B,num,den)
        return (f'<div class="r e"><span class="n">{lab}</span><span class="bb"><i style="width:{max(a,2):.0f}%;background:{TA}"></i><i style="width:{max(b,2):.0f}%;background:{TB}"></i></span>'
                f'<span class="ca{" w" if a>b else ""}">{a:.0f} %<em>{ra} sur {ta}</em></span><span class="cb{" w" if b>a else ""}">{b:.0f} %<em>{rb} sur {tb}</em></span></div>')
    pt=lambda c:f'<i class="pt" style="background:{c}"></i>'
    css=f'''#hero{{left:56px;width:968px;right:auto;top:116px;height:auto}}.side{{position:absolute;top:0;display:flex;align-items:center;gap:18px}}.side.a{{left:0}}.side.b{{right:0;flex-direction:row-reverse;text-align:right}}
.ph{{width:124px;height:124px;margin:5px}}.nm{{color:#064A25}}.m{{font:500 18px/1 "IN";color:rgba(14,26,19,.72);margin-top:8px;white-space:nowrap}}
#sco{{position:absolute;left:0;right:0;top:134px;display:flex;justify-content:center;align-items:flex-end;gap:22px}}#sco div{{text-align:center}}#sco b{{display:block;font:italic 900 88px/.9 "BC"}}
#sco small{{font:500 15.5px/1 "IN";color:rgba(14,26,19,.72);margin-top:6px;white-space:nowrap}}#sco u{{display:block;width:1.5px;height:84px;background:rgba(14,26,19,.25);margin-bottom:22px}}
#p{{top:382px;height:858px}}#in{{position:absolute;left:36px;top:28px;width:896px;height:802px}}
.hd{{display:flex;justify-content:space-between;align-items:center}}.hd h3{{font:700 23px/1 "IN";color:{INK}}}.hd span{{font:500 17.5px/1 "IN";color:{GRIS}}}.pt{{display:inline-block;width:11px;height:11px;border-radius:50%;margin:0 7px 0 18px}}
#rad{{position:absolute;left:-10px;top:36px;overflow:visible}}.rl{{font:600 17.5px "IN";fill:#24332A}}
#cap{{position:absolute;left:0;top:474px;font:500 16.5px/1 "IN";color:{GRIS};white-space:nowrap}}
#tb{{position:absolute;left:520px;top:92px;width:376px}}.th{{position:relative;height:26px;border-bottom:1.5px solid #E3E8E3}}.th i{{position:absolute;top:4px;margin:0}}
.r{{height:46px;border-bottom:1px solid #EEF1EE}}.r .n{{left:0;font:500 18.5px "IN";color:{INK}}}.r .ca,.r .cb{{width:62px;text-align:right;font:500 20px "IN";color:{GRIS}}}.r .ca{{right:74px}}.r .cb{{right:0}}.r .w{{font-weight:700;color:{INK}}}
#b2{{position:absolute;left:0;right:0;top:516px;padding-top:22px;border-top:1.5px solid #E3E8E3}}#b2 .hd{{padding-bottom:12px;border-bottom:1.5px solid #E3E8E3}}
.r.e{{height:45px}}.r.e .bb{{left:262px;width:250px;height:15px;background:linear-gradient(#E9EDE8,#E9EDE8) 0 0/100% 6px no-repeat,linear-gradient(#E9EDE8,#E9EDE8) 0 9px/100% 6px no-repeat}}
.r.e .bb i{{display:block;height:6px;border-radius:3px}}.r.e .bb i+i{{margin-top:3px}}.r.e .ca,.r.e .cb{{width:160px}}.r.e .ca{{right:172px}}.r.e em{{font:500 14px/1 "IN";font-style:normal;color:{GRIS};margin-left:9px}}'''
    cote=lambda nom,J,cl,t:f'<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(int(J["player_id"]))}</div><div><div class="nm">{nom.split(" ")[-1]}</div><div class="m">{drapeau(J["team"],17)}{J["team"]}</div></div></div>'
    body=tete('#064A25','rgba(14,26,19,.72)')+f'''<div id="hero">{cote(nA,A,'a',TA)}{cote(nB,B,'b',TB)}<div id="sco"><div><b style="color:{TA}">{int(A['goals'])}</b><small>{buts(A)}</small></div><u></u><div><b style="color:{TB}">{int(B['goals'])}</b><small>{buts(B)}</small></div></div></div>
<div id="p"><div id="in"><div class="hd"><h3>Ce qu'ils font, pour 90 minutes jouées</h3><span>{pt(TA)}{sA}{pt(TB)}{sB}</span></div>
<svg id="rad" width="500" height="430" viewBox="0 0 500 430">{g}</svg><div id="cap">Bord du radar : le meilleur des {D['n']} {PLUR}.</div>
<div id="tb"><div class="th"><i class="pt" style="right:92px;background:{TA}"></i><i class="pt" style="right:18px;background:{TB}"></i></div>{''.join(lv(k,l,d) for k,l,d in VOL)}</div>
<div id="b2"><div class="hd"><h3>Ce qu'ils réussissent</h3><span>taux de réussite, et le nombre de tentatives</span></div>{''.join(le(*e) for e in EFF)}</div></div></div>'''+pied('rgba(14,26,19,.78)','#064A25')

elif V=='C':    # ---------------- encre : tout sur le jaune, une seule encre verte, deux ronds reliés par critère
    INK,DOUX='#064A25','rgba(14,26,19,.72)'
    def lh(lab,pa,pb,la,lb,sa='',sb='',ga=False,gb=False):
        lo,hi=min(pa,pb),max(pa,pb)
        return (f'<div class="r"><span class="lb">{lab}</span><span class="tk"><i class="ax"></i><i class="ln" style="left:{lo:.1f}%;width:{hi-lo:.1f}%"></i><i class="pb" style="left:{pb:.1f}%"></i><i class="pa" style="left:{pa:.1f}%"></i></span>'
                f'<span class="va{" w" if ga else ""}">{la}<small>{sa}</small></span><span class="vb{" w" if gb else ""}">{lb}<small>{sb}</small></span></div>')
    r1=''
    for k,lab,d in VOL:
        la,lb=val(A,k,d),val(B,k,d); r1+=lh(lab,part(A,k),part(B,k),la,lb,ga=A[k]>B[k] and la!=lb,gb=B[k]>A[k] and la!=lb)
    r2=''
    for k,lab,num,den in EFF:
        ra,ta=tentatives(A,num,den); rb,tb=tentatives(B,num,den); r2+=lh(lab,A[k],B[k],f'{A[k]:.0f} %',f'{B[k]:.0f} %',f'{ra} sur {ta}',f'{rb} sur {tb}',A[k]>B[k],B[k]>A[k])
    css=f'''#c{{background:#F6C41C;color:{INK}}}
#hero{{left:56px;right:56px;top:122px;height:auto}}
.li{{position:relative;height:92px;display:flex;align-items:center;gap:16px;border-bottom:1.5px solid rgba(6,74,37,.3)}}.li:first-child{{border-top:1.5px solid rgba(6,74,37,.3)}}
.ph{{width:72px;height:72px}}.mk{{flex:none;width:22px;height:22px;border-radius:50%}}.mk.a{{background:{INK}}}.mk.b{{box-shadow:inset 0 0 0 4.5px {INK}}}
.nm{{color:{INK};font-size:64px;padding-right:8px}}.m{{font:500 19px/1 "IN";color:{DOUX};white-space:nowrap;margin-top:20px}}
.nt{{margin-left:auto;display:flex;align-items:baseline;gap:14px}}.nt span{{font:500 17px/1 "IN";color:{DOUX};white-space:nowrap}}.nt b{{font:italic 900 74px/1 "BC";color:{INK};min-width:44px;text-align:right}}
.blk{{position:absolute;left:56px;right:56px}}.blk h3{{font:700 23px/1 "IN";color:#0E1A13}}
.axe{{position:relative;height:30px;margin-top:10px;border-bottom:1.5px solid rgba(6,74,37,.3);font:500 15px/1 "IN";color:{DOUX}}}.axe span{{position:absolute;top:4px;white-space:nowrap}}
.axe i{{position:absolute;top:2px;width:18px;height:18px;border-radius:50%}}.axe .a{{right:110px;background:{INK}}}.axe .b{{right:26px;box-shadow:inset 0 0 0 4px {INK}}}
.r{{height:var(--h);border-bottom:1px solid rgba(6,74,37,.16)}}
.r .lb{{left:0;font:500 20px "IN";color:#0E1A13}}
.r .tk{{left:300px;width:440px;height:24px}}.tk i{{position:absolute;display:block}}
.tk .ax{{left:0;right:0;top:11px;height:2px;background:rgba(6,74,37,.28)}}.tk .ln{{top:9.5px;height:5px;background:{INK}}}
.tk .pa,.tk .pb{{top:1px;width:22px;height:22px;margin-left:-11px;border-radius:50%}}.tk .pa{{background:{INK};box-shadow:0 0 0 2.5px #F6C41C}}.tk .pb{{background:#F6C41C;box-shadow:inset 0 0 0 4.5px {INK}}}
.r .va,.r .vb{{width:76px;text-align:right;font:500 21px "IN";color:rgba(14,26,19,.62)}}.r .va{{right:84px}}.r .vb{{right:0}}.r .w{{font-weight:700;color:#0E1A13}}
.r small{{color:{DOUX}}}.r small:empty{{display:none}}
#syn{{top:1128px;font:600 20px/1.5 "IN";color:#0E1A13}}'''
    ligne=lambda nom,J,cl:f'<div class="li"><i class="mk {cl}"></i><div class="ph">{photo(int(J["player_id"]))}</div><div class="nm">{nom.split(" ")[-1]}</div><div class="m">{drapeau(J["team"],16)}{J["team"]}</div><div class="nt"><span>{buts(J)}</span><b>{int(J["goals"])}</b></div></div>'
    axe=lambda g,d:f'<div class="axe"><span style="left:300px">{g}</span><span style="left:740px;transform:translateX(-100%)">{d}</span><i class="a"></i><i class="b"></i></div>'
    body=tete(INK,DOUX)+f'''<div id="hero">{ligne(nA,A,'a')}{ligne(nB,B,'b')}</div>
<div class="blk" style="top:332px;--h:52px"><h3>Ce qu'ils font, pour 90 minutes jouées</h3>{axe('0',f"le meilleur des {D['n']} {PLUR}")}{r1}</div>
<div class="blk" style="top:742px;--h:58px"><h3>Ce qu'ils réussissent</h3>{axe('0 %','100 %')}{r2}</div>
<div class="blk" id="syn">{SYN}</div>'''+pied('rgba(14,26,19,.78)',INK)

else:           # ---------------- blanc : bandeau jaune, une barre d'écart par critère, triée de l'avantage de l'un à celui de l'autre
    TA,TB,GRIS='#0B7A3B','#0E1A13','#5E6B62'
    ECH=220/max([abs(part(A,k)-part(B,k)) for k,_,_ in VOL]+[abs(A[k]-B[k]) for k,_,_,_ in EFF])   # une seule échelle pour les deux blocs : le plus gros écart remplit la demi-largeur
    def le(lab,ecart,la,lb,sa='',sb=''):
        if la==lb and not sa: ecart=0                      # même valeur affichée : pas d'écart dessiné
        bar=f'<i class="ba" style="width:{min(abs(ecart)*ECH,228):.0f}px"></i>' if ecart>0 else (f'<i class="bb" style="width:{min(abs(ecart)*ECH,228):.0f}px"></i>' if ecart<0 else '')
        return f'<div class="r"><span class="lb">{lab}</span><span class="ch"><i class="ax"></i>{bar}</span><span class="va{" w" if ecart>0 and la!=lb else ""}">{la}<small>{sa}</small></span><span class="vb{" w" if ecart<0 and la!=lb else ""}">{lb}<small>{sb}</small></span></div>'
    r1=''.join(le(lab,part(A,k)-part(B,k),val(A,k,d),val(B,k,d)) for k,lab,d in sorted(VOL,key=lambda v:part(B,v[0])-part(A,v[0])))
    r2=''
    for k,lab,num,den in sorted(EFF,key=lambda e:B[e[0]]-A[e[0]]):
        ra,ta=tentatives(A,num,den); rb,tb=tentatives(B,num,den); r2+=le(lab,A[k]-B[k],f'{A[k]:.0f} %',f'{B[k]:.0f} %',f'{ra} sur {ta}',f'{rb} sur {tb}')
    css=f'''#c{{background:#fff;color:#0E1A13}}#band{{position:absolute;left:0;right:0;top:0;height:124px;background:#F6C41C}}
#hero{{left:56px;right:56px;top:146px;height:150px;display:grid;grid-template-columns:1fr 1fr;gap:34px;align-items:center}}
.side{{display:flex;align-items:center;gap:16px;min-width:0}}.side.b{{flex-direction:row-reverse;text-align:right}}
.ph{{width:112px;height:112px;margin:5px}}.nm{{color:#064A25}}.m{{font:500 18px/1 "IN";color:{GRIS};margin-top:6px;white-space:nowrap}}
.nt{{flex:none;margin:0 4px;text-align:center}}.nt b{{display:block;font:italic 900 78px/.9 "BC"}}.nt span{{display:block;font:500 15px/1.2 "IN";color:{GRIS};margin-top:4px;white-space:nowrap}}
.blk{{position:absolute;left:56px;right:56px;padding-top:22px;border-top:1.5px solid #E3E8E3}}.blk h3{{font:700 23px/1 "IN"}}
.dir{{position:relative;height:36px;border-bottom:1.5px solid #E3E8E3;font:600 16px/1 "IN"}}.dir span{{position:absolute;top:12px;white-space:nowrap}}
.dir i{{position:absolute;top:13px;width:12px;height:12px;border-radius:50%}}.dir .a{{right:108px;background:{TA}}}.dir .b{{right:24px;background:{TB}}}
.r{{height:var(--h);border-bottom:1px solid #EEF1EE}}
.r .lb{{left:0;font:500 20px "IN"}}
.r .ch{{left:286px;width:470px;height:100%}}.ch i{{position:absolute;display:block}}
.ch .ax{{left:234px;top:0;bottom:0;width:2px;background:#C9D1CB}}
.ch .ba{{right:236px;top:calc(50% - 8px);height:16px;background:{TA};border-radius:5px 0 0 5px}}.ch .bb{{left:236px;top:calc(50% - 8px);height:16px;background:{TB};border-radius:0 5px 5px 0}}
.r .va,.r .vb{{width:76px;text-align:right;font:500 21px "IN";color:#7A867E}}.r .va{{right:84px}}.r .vb{{right:0}}.r .w{{font-weight:700;color:#0E1A13}}
.r small{{color:{GRIS}}}.r small:empty{{display:none}}
#syn{{top:1126px;border:0;padding:0;font:600 20px/1.5 "IN"}}'''
    cote=lambda nom,J,cl,t:f'<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(int(J["player_id"]))}</div><div style="flex:1;min-width:0"><div class="nm">{nom.split(" ")[-1]}</div><div class="m">{drapeau(J["team"],16)}{J["team"]}</div></div><div class="nt"><b style="color:{t}">{int(J["goals"])}</b><span>{buts(J).replace(" en "," en<br>")}</span></div></div>'
    dirs=f'<div class="dir"><span style="left:286px;width:226px;text-align:right;color:{TA}">avantage {sA}</span><span style="left:530px">avantage {sB}</span><i class="a"></i><i class="b"></i></div>'
    body='<div id="band"></div>'+tete('#064A25','rgba(14,26,19,.72)')+f'''<div id="hero">{cote(nA,A,'a',TA)}{cote(nB,B,'b',TB)}</div>
<div class="blk" style="top:316px;--h:50px"><h3>Ce qu'ils font, pour 90 minutes jouées</h3>{dirs}{r1}</div>
<div class="blk" style="top:724px;--h:56px"><h3>Ce qu'ils réussissent</h3>{dirs}{r2}</div>
<div class="blk" id="syn">{SYN}</div>'''+pied(GRIS,'#064A25')
FIN="<script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{}))]).then(()=>{window.READY=true})</script>"
open(OUT,'w',encoding='utf-8').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}{COMMUN}{css}</style></head><body><div id="c">{body}</div>{FIN}</body></html>')
print('ok',V,OUT)

"""Trois autres mises en scène du duel, pour choisir : B « nuit » (barres en miroir), C « encre » (haltères sur fond jaune, sans cadre),
D « blanc » (barres d'écart triées). Mêmes données que duel_pro.py. Format Twitter/X 1080 x 1350.
usage : python3 duel_variantes.py <fiche A.json> <fiche B.json> <B|C|D> <sortie.html>"""
import json, sys
from da import BASE_CSS, photo, ordi, drapeau
A=json.load(open(sys.argv[1],encoding='utf-8')); B=json.load(open(sys.argv[2],encoding='utf-8')); V=sys.argv[3]; OUT=sys.argv[4]; FMT=sys.argv[5] if len(sys.argv)>5 else 'x'
BA=A['bassin']; nA,nB=A['player'].split(' ')[-1],B['player'].split(' ')[-1]
CA,CB={c['k']:c['centile'] for c in A['criteres']},{c['k']:c['centile'] for c in B['criteres']}; CRIT=A['criteres']
wa=sum(CA[k]>CB[k] for k in CA); wb=sum(CB[k]>CA[k] for k in CA)
bilan=f"{nA} devant sur {wa} critères, {nB} sur {wb}"
L1=f"Centile : part des autres {BA['pluriel']} dépassés. Note : moyenne des dix centiles."; L2=f"{A['minutes']} et {B['minutes']} minutes jouées, à lire avec prudence. Données StatsBomb Open Data."
fams=[]
for c in CRIT:
    if not fams or fams[-1][0]!=c['famille']: fams.append((c['famille'],[]))
    fams[-1][1].append(c)
def tete(coul_sig='var(--vert-d)',coul_ctx='rgba(14,26,19,.72)'):
    return f'<div id="top"><div id="brand" style="color:{coul_sig}"><img src="logo-verte.png" alt=""><div><b>Mali<i>Data</i>Foot</b></div></div><div id="ctx" style="color:{coul_ctx}">Coupe d\'Afrique des nations 2023</div></div>'
def pied(coul='rgba(14,26,19,.78)',coulh='var(--vert-d)',blanc=False):
    x,t=('logo_x_blanc.png','logo_tt_blanc.png') if blanc else ('logo_x.png','logo_tt.png')
    soc=f'<b style="color:{coulh}"><img src="{x}" alt="X" style="height:22px"><img src="{t}" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
    if FMT=='tiktok': return f'<div id="note" style="color:{coul}"><p>{L1}</p><div><span>{L2}</span>{soc}</div></div>'
    return f'<div id="note" style="color:{coul}"><span>{L1}<br>{L2}</span>{soc}</div>'
FIN="<script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{}))]).then(()=>{window.READY=true})</script>"
COMMUN='''.ph{flex:none;border-radius:50%;overflow:hidden;background:#E9EDE8}.ph img,.ph svg{width:100%;height:100%;display:block;object-fit:cover}
.nm{font:italic 900 64px/1 "BC";text-transform:uppercase;white-space:nowrap}
.fam{font:600 15px/1 "IN"}'''

if V=='B':      # ---------------- nuit : fond vert profond, barres en miroir autour des libellés
    TA,TB='#F6C41C','#FFFFFF'; DOUX='#A9C2B3'
    rows=''
    for fam,cs in fams:
        rows+=f'<div class="sepf"><i></i><span class="fam">{fam}</span><i></i></div>'
        for c in cs:
            a,b=CA[c['k']],CB[c['k']]
            rows+=(f'<div class="r"><span class="va{" w" if a>b else ""}">{a}</span><span class="ta"><i style="width:{max(a,2)}%"></i></span>'
                   f'<span class="lb">{c["court"]}</span><span class="tb"><i style="width:{max(b,2)}%"></i></span><span class="vb{" w" if b>a else ""}">{b}</span></div>')
    css=f'''#c{{background:#04331A;color:#fff}}
#hero{{left:56px;right:56px;top:126px;height:190px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:30px}}
.side{{display:flex;align-items:center;gap:18px;min-width:0}}.side.b{{flex-direction:row-reverse;text-align:right}}
.ph{{width:124px;height:124px;margin:5px}}.nm{{color:#fff;font-size:50px}}.m{{font:500 18px/1 "IN";color:{DOUX};margin-top:8px;white-space:nowrap}}
#sco{{display:flex;align-items:flex-end;gap:22px}}#sco div{{text-align:center}}#sco b{{display:block;font:italic 900 88px/.9 "BC"}}#sco small{{display:block;font:500 15.5px/1 "IN";color:{DOUX};margin-top:6px;white-space:nowrap}}
#sco u{{display:block;width:1.5px;height:84px;background:#2A5A3F;margin-bottom:22px;text-decoration:none}}
#tt{{position:absolute;left:56px;right:56px;top:344px;display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:1.5px solid #1F5236}}
#tt h3{{font:700 23px/1 "IN";color:#fff}}#lg{{display:flex;gap:20px;font:500 18px/1 "IN";color:{DOUX}}}#lg i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:7px}}
#bf{{position:absolute;left:56px;right:56px;top:392px}}
.sepf{{display:flex;align-items:center;gap:14px;height:38px;padding-top:8px}}.sepf i{{flex:1;height:1px;background:#1F5236}}.sepf .fam{{color:{DOUX}}}
.r{{position:relative;height:58px}}
.r span{{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}}
.r .lb{{left:334px;width:300px;text-align:center;font:500 19.5px "IN";color:#fff}}
.r .ta,.r .tb{{height:9px;width:250px;border-radius:5px;background:#0C4429;overflow:hidden}}.r .ta{{left:72px}}.r .tb{{left:646px}}
.r .ta i,.r .tb i{{display:block;height:100%;border-radius:5px}}.r .ta i{{background:{TA};margin-left:auto}}.r .tb i{{background:{TB}}}
.r .va,.r .vb{{font:500 21px "IN";color:{DOUX};width:52px}}.r .va{{left:0;text-align:left}}.r .vb{{right:0;text-align:right}}.r .w{{font-weight:700;color:#fff}}
#bil{{position:absolute;left:56px;right:56px;top:1178px;text-align:center;font:600 21px/1 "IN";color:#fff;padding-top:20px;border-top:1.5px solid #1F5236}}
'''
    cote=lambda F,cl,t:f'<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(F["player_id"])}</div><div><div class="nm">{F["player"].split(" ")[-1]}</div><div class="m">{drapeau(F["team"],16)}{F["team"]}, {F["minutes"]} minutes</div></div></div>'
    if FMT=='tiktok': css+='''html,body{width:1080px;height:1920px}#c{height:1920px}
#top{right:134px;top:150px}
#hero{right:134px;top:250px;gap:16px}.side{gap:12px}.ph{width:104px;height:104px}.nm{font-size:42px}.m{font-size:16px}#sco{gap:16px}#sco b{font-size:78px}#sco small{font-size:14.5px}
#tt{right:134px;top:470px}#bf{right:134px;top:522px}
.r{height:70px}.sepf{height:46px}
.r .lb{left:305px;width:280px}.r .ta{left:60px;width:235px}.r .tb{left:595px;width:235px}.r .va,.r .vb{width:46px}
#bil{right:134px;top:1424px}
#note{top:1518px;right:134px;display:block;font-size:16.5px;line-height:1}#note p{white-space:nowrap}
#note div{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}#note b{font-size:22px}
'''
    body=tete('#fff',DOUX)+f'''<div id="hero">{cote(A,'a',TA)}<div id="sco"><div><b style="color:{TA}">{A['note']:.0f}</b><small>{ordi(A['rang'])} sur {BA['effectif']}</small></div><u></u><div><b style="color:{TB}">{B['note']:.0f}</b><small>{ordi(B['rang'])} sur {BA['effectif']}</small></div></div>{cote(B,'b',TB)}</div>
<div id="tt"><h3>Leur tournoi, critère par critère</h3><div id="lg"><span><i style="background:{TA}"></i>{nA}</span><span><i style="background:{TB}"></i>{nB}</span></div></div>
<div id="bf">{rows}</div><div id="bil">{bilan}</div>'''+pied(DOUX,'#fff',True)

elif V=='C':    # ---------------- encre : tout sur le jaune, une seule encre verte, haltères
    INK='#064A25'
    rows=''
    for fam,cs in fams:
        rows+=f'<div class="sepf"><span class="fam">{fam}</span></div>'
        for c in cs:
            a,b=CA[c['k']],CB[c['k']]; lo,hi=min(a,b),max(a,b)
            rows+=(f'<div class="r"><span class="lb">{c["court"]}</span><span class="tk"><i class="ax"></i><i class="md"></i><i class="ln" style="left:{lo}%;width:{hi-lo}%"></i>'
                   f'<i class="pb" style="left:{b}%"></i><i class="pa" style="left:{a}%"></i></span><span class="va{" w" if a>b else ""}">{a}</span><span class="vb{" w" if b>a else ""}">{b}</span></div>')
    css=f'''#c{{background:#F6C41C;color:{INK}}}
#hero{{left:56px;right:56px;top:124px;height:210px}}
.li{{position:relative;height:100px;display:flex;align-items:center;gap:16px;border-bottom:1.5px solid rgba(6,74,37,.3)}}.li:first-child{{border-top:1.5px solid rgba(6,74,37,.3)}}
.ph{{width:76px;height:76px}}.mk{{flex:none;width:22px;height:22px;border-radius:50%}}.mk.a{{background:{INK}}}.mk.b{{box-shadow:inset 0 0 0 4.5px {INK}}}
.nm{{color:{INK};font-size:70px;padding-right:8px}}.m{{font:500 19px/1 "IN";color:rgba(14,26,19,.72);white-space:nowrap;margin-top:22px}}
.nt{{margin-left:auto;display:flex;align-items:baseline;gap:14px}}.nt small{{font:500 17px/1 "IN";color:rgba(14,26,19,.72);white-space:nowrap}}.nt b{{font:italic 900 78px/1 "BC";color:{INK};min-width:86px;text-align:right}}
#tt{{position:absolute;left:56px;right:56px;top:356px}}
#tt h3{{font:700 23px/1 "IN";color:#0E1A13}}
#axe{{position:absolute;left:294px;top:36px;width:500px;height:18px;font:500 15px/1 "IN";color:rgba(14,26,19,.72)}}#axe span{{position:absolute;top:0;transform:translateX(-50%)}}
#bf{{position:absolute;left:56px;right:56px;top:412px}}
.sepf{{height:36px;display:flex;align-items:flex-end;padding-bottom:7px;border-bottom:1.5px solid rgba(6,74,37,.3)}}.sepf .fam{{color:rgba(14,26,19,.72)}}
.r{{position:relative;height:55px;border-bottom:1px solid rgba(6,74,37,.16)}}
.r>span{{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}}
.r .lb{{left:0;font:500 20px "IN";color:#0E1A13}}
.r .tk{{left:294px;width:500px;height:24px}}.tk i{{position:absolute;display:block}}
.tk .ax{{left:0;right:0;top:11px;height:2px;background:rgba(6,74,37,.28)}}.tk .md{{left:50%;top:3px;width:2px;height:18px;margin-left:-1px;background:rgba(6,74,37,.45)}}
.tk .ln{{top:9.5px;height:5px;background:{INK}}}
.tk .pa,.tk .pb{{top:1px;width:22px;height:22px;margin-left:-11px;border-radius:50%}}.tk .pa{{background:{INK};box-shadow:0 0 0 2.5px #F6C41C}}.tk .pb{{background:#F6C41C;box-shadow:inset 0 0 0 4.5px {INK}}}
.r .va,.r .vb{{width:50px;text-align:right;font:500 21px "IN";color:rgba(14,26,19,.62)}}.r .va{{right:74px}}.r .vb{{right:0}}.r .w{{font-weight:700;color:#0E1A13}}
#th{{position:absolute;right:56px;top:390px;width:124px;height:22px}}#th i{{position:absolute;top:0;width:18px;height:18px;border-radius:50%}}#th .a{{right:90px;background:{INK}}}#th .b{{right:16px;box-shadow:inset 0 0 0 4px {INK}}}
#bil{{position:absolute;left:56px;right:56px;top:1186px;font:600 21px/1 "IN";color:#0E1A13}}
'''
    ligne=lambda F,cl,lab:f'<div class="li"><i class="mk {cl}"></i><div class="ph">{photo(F["player_id"])}</div><div class="nm">{F["player"].split(" ")[-1]}</div><div class="m">{drapeau(F["team"],16)}{F["team"]}, {F["minutes"]} minutes</div><div class="nt"><small>{lab}{ordi(F["rang"])} sur {BA["effectif"]} {BA["pluriel"]}</small><b>{F["note"]:.0f}</b></div></div>'
    body=tete()+f'''<div id="hero">{ligne(A,'a','')}{ligne(B,'b','')}</div>
<div id="tt"><h3>Leur tournoi sur dix critères du poste</h3><div id="axe"><span style="left:0">0</span><span style="left:50%">médiane</span><span style="left:100%">100</span></div></div><div id="th"><i class="a"></i><i class="b"></i></div>
<div id="bf">{rows}</div><div id="bil">{bilan}</div>'''+pied()

else:           # ---------------- blanc : bandeau jaune, barres d'écart triées du plus favorable à l'un au plus favorable à l'autre
    TA,TB='#0B7A3B','#0E1A13'
    tri=sorted(CRIT,key=lambda c:CB[c['k']]-CA[c['k']])
    rows=''
    for c in tri:
        a,b=CA[c['k']],CB[c['k']]; d=a-b
        bar=f'<i class="ba" style="width:{abs(d)*2.4:.0f}px"></i>' if d>0 else (f'<i class="bb" style="width:{abs(d)*2.4:.0f}px"></i>' if d<0 else '')
        rows+=f'<div class="r"><span class="lb">{c["court"]}</span><span class="ch"><i class="ax"></i>{bar}</span><span class="va{" w" if a>b else ""}">{a}</span><span class="vb{" w" if b>a else ""}">{b}</span></div>'
    css=f'''#c{{background:#fff;color:#0E1A13}}
#band{{position:absolute;left:0;right:0;top:0;height:124px;background:#F6C41C}}
#hero{{left:56px;right:56px;top:150px;height:170px;display:grid;grid-template-columns:1fr 1fr;gap:34px;align-items:center}}
.side{{display:flex;align-items:center;gap:16px;min-width:0}}.side.b{{flex-direction:row-reverse;text-align:right}}
.ph{{width:118px;height:118px;margin:5px}}.nm{{color:#064A25;font-size:58px}}.m{{font:500 18px/1 "IN";color:#5E6B62;margin-top:6px;white-space:nowrap}}
.nt{{flex:none;margin:0 6px}}.nt b{{display:block;font:italic 900 74px/.95 "BC";color:#064A25}}.nt small{{display:block;font:500 15.5px/1 "IN";color:#5E6B62;margin-top:4px;white-space:nowrap}}
#tt{{position:absolute;left:56px;right:56px;top:346px;padding-top:26px;border-top:1.5px solid #E3E8E3}}
#tt h3{{font:700 23px/1 "IN"}}
#dir{{position:absolute;left:322px;width:480px;top:416px;display:flex;justify-content:space-between;font:600 16px/1 "IN"}}#dir span:first-child{{color:{TA}}}
#th{{position:absolute;right:56px;top:414px;width:124px;height:20px}}#th i{{position:absolute;top:2px;width:12px;height:12px;border-radius:50%}}#th .a{{right:78px;background:{TA}}}#th .b{{right:4px;background:{TB}}}
#bf{{position:absolute;left:56px;right:56px;top:446px;border-top:1.5px solid #E3E8E3}}
.r{{position:relative;height:62px;border-bottom:1px solid #EEF1EE}}
.r>span{{position:absolute;top:50%;transform:translateY(-50%);white-space:nowrap;line-height:1}}
.r .lb{{left:0;font:500 20px "IN"}}
.r .ch{{left:266px;width:480px;height:62px}}.ch i{{position:absolute;display:block}}
.ch .ax{{left:239px;top:0;bottom:0;width:2px;background:#C9D1CB}}
.ch .ba{{right:241px;top:23px;height:16px;background:{TA};border-radius:5px 0 0 5px}}.ch .bb{{left:241px;top:23px;height:16px;background:{TB};border-radius:0 5px 5px 0}}
.r .va,.r .vb{{width:50px;text-align:right;font:500 21px "IN";color:#7A867E}}.r .va{{right:74px}}.r .vb{{right:0}}.r .w{{font-weight:700;color:#0E1A13}}
#bil{{position:absolute;left:56px;right:56px;top:1092px;font:600 21px/1 "IN"}}
#stw{{position:absolute;left:56px;right:56px;top:1140px}}#stw h4{{font:500 16.5px/1 "IN";color:#5E6B62}}
#st{{position:relative;height:36px;margin-top:6px;border-bottom:1.5px solid #B9C4BC}}#st i{{position:absolute;bottom:0;width:2px;height:14px;background:#B9C4BC}}#st b{{position:absolute;bottom:0;width:5px;height:34px;margin-left:-2px;border-radius:3px 3px 0 0}}
#note{{top:1268px}}
'''
    notes=A['notes_bassin']; lo,hi=min(notes),max(notes); pos=lambda v:(v-lo)/(hi-lo)*100
    rest=list(notes); [rest.remove(v) for v in (A['note'],B['note'])]
    ticks=''.join(f'<i style="left:{pos(v):.2f}%"></i>' for v in rest)
    cote=lambda F,cl,t:f'<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(F["player_id"])}</div><div style="flex:1;min-width:0"><div class="nm">{F["player"].split(" ")[-1]}</div><div class="m">{drapeau(F["team"],16)}{F["team"]}, {F["minutes"]} minutes</div></div><div class="nt"><b>{F["note"]:.0f}</b><small>{ordi(F["rang"])} sur {BA["effectif"]}</small></div></div>'
    body='<div id="band"></div>'+tete()+f'''<div id="hero">{cote(A,'a',TA)}{cote(B,'b',TB)}</div>
<div id="tt"><h3>L'écart entre eux sur chacun des dix critères du poste</h3></div>
<div id="dir"><span>avantage {nA}</span><span>avantage {nB}</span></div><div id="th"><i class="a"></i><i class="b"></i></div>
<div id="bf">{rows}</div><div id="bil">{bilan}</div>
<div id="stw"><h4>Leurs notes parmi les {BA['effectif']} {BA['pluriel']} du tournoi</h4><div id="st">{ticks}<b style="left:{pos(A['note']):.2f}%;background:{TA}"></b><b style="left:{pos(B['note']):.2f}%;background:{TB}"></b></div></div>'''+pied('#5E6B62','#064A25')
open(OUT,'w',encoding='utf-8').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{BASE_CSS}{COMMUN}{css}</style></head><body><div id="c">{body}</div>{FIN}</body></html>')
print('ok',V,OUT)

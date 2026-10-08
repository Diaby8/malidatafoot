"""Duel entre deux joueurs du même rôle, dans le cadre commun. Deux profils superposés sur un radar sans chiffres,
les centiles côte à côte dans un tableau, et l'écart sur chaque critère. Les deux fiches viennent de l'étape « profils ».
usage : python3 duel_pro.py <fiche A.json> <fiche B.json> <sortie.html> [x|tiktok]"""
import json, sys
from da import page, fr, radar, photo, ordi, drapeau
A=json.load(open(sys.argv[1],encoding='utf-8')); B=json.load(open(sys.argv[2],encoding='utf-8'))
OUT=sys.argv[3] if len(sys.argv)>3 else 'duel_pro.html'; FMT=sys.argv[4] if len(sys.argv)>4 else 'x'
assert A['role']==B['role'] and A['bassin']==B['bassin'], 'un duel compare deux joueurs du même rôle, dans le même bassin'
BA=A['bassin']; nomA,nomB=A['player'].split(' ')[-1],B['player'].split(' ')[-1]
CA,CB={c['k']:c['centile'] for c in A['criteres']},{c['k']:c['centile'] for c in B['criteres']}
CRIT=A['criteres']
TA,TB='#0B7A3B','#0E1A13'                                  # vert pour le premier joueur, encre pour le second
g=radar([(c['k'],c['nom']) for c in CRIT],[([CB[c['k']] for c in CRIT],TB,TB,.07),([CA[c['k']] for c in CRIT],TA,'#19A552',.2)])
# ---- tableau : une ligne par critère, les deux centiles et deux fines barres
def ligne(c):
    a,b=CA[c['k']],CB[c['k']]
    return (f'<div class="r"><span class="n">{c["court"]}</span><span class="bb"><i style="width:{max(a,3)}%;background:{TA}"></i><i style="width:{max(b,3)}%;background:{TB}"></i></span>'
            f'<span class="ca{" w" if a>b else ""}">{a}</span><span class="cb{" w" if b>a else ""}">{b}</span></div>')
blocs={}
for c in CRIT: blocs.setdefault(c['famille'],f'<div class="fam">{c["famille"]}</div>'); blocs[c['famille']]+=ligne(c)
TH=f'<div class="th"><span style="left:222px">centiles</span><span style="right:52px;width:40px;text-align:right"><i class="pt" style="background:{TA}"></i></span><span style="right:0;width:40px;text-align:right"><i class="pt" style="background:{TB}"></i></span></div>'
fams=list(blocs)
if FMT=='tiktok':                                           # deux colonnes aussi équilibrées que possible, sans couper une famille
    n=[sum(1 for c in CRIT if c['famille']==f) for f in fams]
    cut=min(range(1,len(fams)),key=lambda i:abs(sum(n[:i])-sum(n[i:])))
    TABLE=f'<div id="tb" class="deux"><div>{TH}{"".join(blocs[f] for f in fams[:cut])}</div><div>{TH}{"".join(blocs[f] for f in fams[cut:])}</div></div>'
else:
    TABLE=f'<div id="tb">{TH}{"".join(blocs[f] for f in fams)}</div>'
# ---- bas du cadre : les plus gros écarts de chacun, et le bilan
ecarts=sorted(CRIT,key=lambda c:CA[c['k']]-CB[c['k']])
plusA=[c for c in ecarts[::-1] if CA[c['k']]>CB[c['k']]][:3]; plusB=[c for c in ecarts if CB[c['k']]>CA[c['k']]][:3]
li=lambda l,s:''.join(f'<li>{c["court"]}<b>+{abs(CA[c["k"]]-CB[c["k"]])}</b></li>' for c in l) or '<li>Aucun critère</li>'
wa=sum(CA[k]>CB[k] for k in CA); wb=sum(CB[k]>CA[k] for k in CA); eg=len(CA)-wa-wb
bilan=f'<li>{nomA} devant<b>{wa} sur {len(CA)}</b></li><li>{nomB} devant<b>{wb} sur {len(CA)}</b></li>'+(f'<li>À égalité<b>{eg}</b></li>' if eg else '')
notes=BA and A['notes_bassin']; lo,hi=min(notes),max(notes); pos=lambda v:(v-lo)/(hi-lo)*100
rest=list(notes)
for v in (A['note'],B['note']): rest.remove(v)
ticks=''.join(f'<i style="left:{pos(v):.2f}%"></i>' for v in rest)
cote=lambda F,cl,t:f'''<div class="side {cl}"><div class="ph" style="box-shadow:0 0 0 5px {t}">{photo(F['player_id'])}</div>
 <div class="id"><div class="nm" data-fit>{F['player'].split(' ')[-1]}</div><div class="m">{drapeau(F['team'],16)}{F['team']}, {F['minutes']} minutes</div></div>
 <div class="nt"><small>Note</small><b>{F['note']:.0f}</b><span>{ordi(F['rang'])} sur {BA['effectif']}</span></div></div>'''
css=f'''
#hero{{right:56px;display:grid;grid-template-columns:1fr 1fr;gap:34px;align-items:center}}
.side{{display:flex;align-items:center;gap:16px;min-width:0}}.side.b{{flex-direction:row-reverse;text-align:right}}
.ph{{flex:none;width:104px;height:104px;border-radius:50%;overflow:hidden;background:#E9EDE8;margin:5px}}.ph img,.ph svg{{width:100%;height:100%;display:block;object-fit:cover}}
.id{{flex:1;min-width:0}}
.nm{{font:italic 900 60px/1 "BC";color:var(--vert-d);text-transform:uppercase;white-space:nowrap;overflow:hidden;padding-right:6px}}.side.b .nm{{padding:0 0 0 6px}}
.m{{font:500 18px/1 "IN";color:rgba(14,26,19,.72);margin-top:6px;white-space:nowrap}}
.nt{{flex:none}}.nt small{{display:block;font:600 15px/1 "IN";color:rgba(14,26,19,.7);margin-bottom:3px}}.nt b{{display:block;font:italic 900 66px/.95 "BC";color:var(--vert-d)}}.nt span{{display:block;font:600 16.5px/1 "IN";color:var(--encre);margin-top:3px;white-space:nowrap}}
#lg{{display:flex;gap:20px;font:500 18px/1 "IN";color:var(--gris)}}#lg i,.pt{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:7px}}.th .pt{{margin:0 4px 0 0}}
#rad{{position:absolute;left:10px;top:70px;width:500px;height:524px;overflow:visible}}
.rl{{font:600 18px "IN";fill:#24332A}}
#cap{{position:absolute;left:36px;top:590px;font:500 16.5px/1 "IN";color:var(--gris)}}
#tb{{position:absolute;left:540px;top:78px;width:392px}}
.th{{position:relative;height:22px;font:500 15px/1 "IN";color:var(--gris)}}.th span{{position:absolute;top:0}}
.fam{{font:600 15px/1 "IN";color:var(--gris);padding:12px 0 6px;border-bottom:1.5px solid var(--trait)}}
.r{{position:relative;height:36px;border-bottom:1px solid #EEF1EE}}
.r .n{{position:absolute;left:0;top:9px;font:500 18.5px/1 "IN";color:var(--encre);white-space:nowrap}}
.r .bb{{position:absolute;left:222px;width:70px;top:11px;height:13px;background:linear-gradient(#E9EDE8,#E9EDE8) 0 0/100% 5px no-repeat,linear-gradient(#E9EDE8,#E9EDE8) 0 8px/100% 5px no-repeat}}
.r .bb i{{display:block;height:5px;border-radius:2.5px}}.r .bb i+i{{margin-top:3px}}
.r .ca,.r .cb{{position:absolute;top:8px;width:40px;text-align:right;font:500 19px/1 "IN";color:var(--gris)}}.r .ca{{right:52px}}.r .cb{{right:0}}
.r .w{{font-weight:700;color:var(--encre)}}
#sep{{position:absolute;left:36px;right:36px;top:626px;border-top:1.5px solid var(--trait)}}
#bt{{position:absolute;left:36px;right:36px;top:648px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:34px}}
#bt h4{{font:700 18px/1 "IN";color:var(--encre);display:flex;align-items:center;gap:9px;white-space:nowrap}}#bt h4 i{{width:11px;height:11px;border-radius:50%;display:block}}
#bt ul{{list-style:none;margin-top:12px}}#bt li{{display:flex;align-items:baseline;gap:8px;font:500 18.5px/1 "IN";color:var(--encre);padding:8px 0;border-bottom:1px solid #EEF1EE;white-space:nowrap}}
#bt li b{{margin-left:auto;font-weight:700}}
#stw{{position:absolute;left:36px;right:36px;top:822px}}
#stw h4{{font:700 18px/1 "IN";color:var(--encre)}}
#st{{position:relative;height:40px;margin-top:10px;border-bottom:1.5px solid #B9C4BC}}
#st i{{position:absolute;bottom:0;width:2px;height:16px;background:#B9C4BC}}
#st b{{position:absolute;bottom:0;width:5px;height:38px;margin-left:-2px;border-radius:3px 3px 0 0}}
#st em{{position:absolute;bottom:-24px;font:500 15px/1 "IN";font-style:normal;color:var(--gris)}}
'''
if FMT=='tiktok': css+='''
#hero{right:134px;gap:22px}.ph{width:88px;height:88px}.nm{font-size:52px}.nt b{font-size:58px}.m{font-size:16.5px}.side{gap:12px}
#rad{left:195px;top:24px}#cap{top:522px}
#tb.deux{left:36px;top:556px;width:818px;display:grid;grid-template-columns:1fr 1fr;gap:38px}
#sep{top:880px}#bt{top:902px;gap:26px}#bt li{font-size:18px}
#stw{display:none}
'''
hero=cote(A,'a',TA)+cote(B,'b',TB)
panel=f'''<div id="ph"><h3>Leur tournoi sur dix critères du poste</h3><div id="lg"><span><i style="background:{TA}"></i>{nomA}</span><span><i style="background:{TB}"></i>{nomB}</span></div></div>
<svg id="rad" viewBox="0 0 500 524">{g}</svg>
<div id="cap">Pointillé : le niveau médian des {BA['pluriel']}</div>
{TABLE}
<div id="sep"></div>
<div id="bt"><div><h4><i style="background:{TA}"></i>Avantage {nomA}</h4><ul>{li(plusA,TA)}</ul></div><div><h4><i style="background:{TB}"></i>Avantage {nomB}</h4><ul>{li(plusB,TB)}</ul></div><div><h4>Le bilan</h4><ul>{bilan}</ul></div></div>
<div id="stw"><h4>Leurs notes parmi les {BA['effectif']} {BA['pluriel']} du tournoi</h4><div id="st">{ticks}<b style="left:{pos(A['note']):.2f}%;background:{TA}"></b><b style="left:{pos(B['note']):.2f}%;background:{TB}"></b><em style="left:0">{lo:.0f}</em><em style="right:0">{hi:.0f}</em></div></div>'''
note=(f"Centile : part des autres {BA['pluriel']} dépassés. Note : moyenne des dix centiles.",
      f"{A['minutes']} et {B['minutes']} minutes jouées, à lire avec prudence. Données StatsBomb Open Data.")
open(OUT,'w',encoding='utf-8').write(page("Coupe d'Afrique des nations 2023",hero,panel,note,css,FMT))
print('ok',OUT,nomA,A['note'],A['rang'],'|',nomB,B['note'],B['rang'],'| devant',wa,wb,eg,[(c['court'],CA[c['k']],CB[c['k']]) for c in CRIT])

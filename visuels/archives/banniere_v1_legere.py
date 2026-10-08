"""La toute première bannière X (bv1 : fond jaune dégradé, terrain derrière, trame de points, quatre cartes penchées), en plus léger.
Même fond, mêmes places, même style de cartes ; chaque carte garde son dessin et une seule information.
Les chiffres sont ceux d'après l'audit (note 60, 11e sur 49 latéraux, 398 et 646 minutes) : l'ancienne bannière portait encore
69,3 / 7e sur 109 / 63,3 contre 61,6, qui ne sont plus vrais. Le grain est retiré (règle : on garde la trame, pas le grain).
usage : python3 banniere_v1_legere.py <sortie.html> [A|B]      A = léger (une info par carte) · B = très léger (les dessins seuls)"""
import json, math, sys
from da import fr
OUT=sys.argv[1]; NIV=sys.argv[2] if len(sys.argv)>2 else 'A'; W,H=1500,500
FS='node_modules/@fontsource/'
V=json.load(open('vitrine.json',encoding='utf-8'))
F=json.load(open('../../outputs/fiches/hamari-traore_poste.json',encoding='utf-8'))
D=json.load(open('../../outputs/duel_v2.json',encoding='utf-8'))
VD,ROUGE='#064A25','#D4252A'

# ------------------------------------------------------------------ le fond, repris tel quel de la première bannière
pts=''; st=26; row=0; y=st/2
while y<H:
    x=st/2+(st/2 if row%2 else 0)
    while x<W:
        dd=math.hypot(x-W,y)/1150; r=1.1+8.5*max(0,1-dd)**2.6; pts+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=st
    y+=st; row+=1
fond=(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><g fill="#FDEBA6" fill-opacity=".85">{pts}</g></svg>'
      '<svg id="pt" viewBox="0 0 120 80"><rect x="0" y="0" width="120" height="80"/><line x1="60" y1="0" x2="60" y2="80"/><circle cx="60" cy="40" r="10"/><rect x="0" y="18" width="18" height="44"/><rect x="0" y="30" width="6" height="20"/><rect x="102" y="18" width="18" height="44"/><rect x="114" y="30" width="6" height="20"/><path d="M18 32A10 10 0 0 1 18 48"/><path d="M102 32A10 10 0 0 0 102 48"/></svg>')

# ------------------------------------------------------------------ petit terrain jaune des cartes (326 x 220)
CW,CH=326,220; px=lambda x:4+x*(CW-8)/120; py=lambda y:4+y*(CH-8)/80; s=(CW-8)/120
def pelouse(uid):
    Lp='stroke="#fff" stroke-opacity=".92" stroke-width="1.5" fill="none"'
    g=(f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6C620"/><stop offset=".5" stop-color="#F3B811"/><stop offset="1" stop-color="#EFA70C"/></linearGradient>'
       f'<pattern id="p{uid}" width="11" height="11" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".9" fill="#FCE07A" fill-opacity=".55"/></pattern></defs>'
       f'<rect width="{CW}" height="{CH}" fill="url(#g{uid})"/><rect width="{CW}" height="{CH}" fill="url(#p{uid})"/>')
    g+=f'<rect x="{px(0)}" y="{py(0)}" width="{120*s}" height="{py(80)-py(0)}" {Lp}/><line x1="{px(60)}" y1="{py(0)}" x2="{px(60)}" y2="{py(80)}" {Lp}/><circle cx="{px(60)}" cy="{py(40)}" r="{10*s}" {Lp}/>'
    for x0,sg in ((0,1),(120,-1)):
        g+=f'<rect x="{px(min(x0,x0+sg*18))}" y="{py(18)}" width="{18*s}" height="{py(62)-py(18)}" {Lp}/><rect x="{px(min(x0,x0+sg*6))}" y="{py(30)}" width="{6*s}" height="{py(50)-py(30)}" {Lp}/>'
        g+=f'<path d="M{px(x0+sg*18)} {py(32)}A{10*s} {10*s} 0 0 {1 if sg>0 else 0} {px(x0+sg*18)} {py(48)}" {Lp}/>'
    return g
puce=lambda style,n,t:f'<div class="puce" style="{style}"><b>{n}</b><span>{t}</span></div>'

# ------------------------------------------------------------------ carte 1 : le but (le tracé seul, une puce)
B=V['but']; g=pelouse(1)
for e in B['seq']:
    x1,y1,x2,y2=px(e['x']),py(e['y']),px(e['ex']),py(e['ey'])
    if e['type']=='Carry': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VD}" stroke-width="1.8" stroke-dasharray=".4 3.6" stroke-linecap="round"/>'
    elif e['type']=='Pass': g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{VD}" stroke-width="2.3" stroke-linecap="round"/>'
    else: g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROUGE}" stroke-width="3.6" stroke-linecap="round"/>'
for e in [e for e in B['seq'] if e['type']=='Pass']: g+=f'<circle cx="{px(e["x"]):.1f}" cy="{py(e["y"]):.1f}" r="3" fill="#fff" stroke="{VD}" stroke-width="1.5"/>'
c1=f'<svg width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">{g}</svg>'+(puce('right:26px;top:13px',B['passes'],'passes') if NIV in 'AC' else '')

# ------------------------------------------------------------------ carte 3 : le réseau (sans les noms, une puce)
R_=V['reseau_passes']; ND={n['player_id']:n for n in R_['nodes']}; E=sorted(R_['edges'],key=lambda e:e['n']); top=E[-1]; g=pelouse(3)
for e in E:
    a,b=ND[e['a']],ND[e['b']]; first=e is top
    g+=f'<line x1="{px(a["x"]):.1f}" y1="{py(a["y"]):.1f}" x2="{px(b["x"]):.1f}" y2="{py(b["y"]):.1f}" stroke="{ROUGE if first else "#0A7538"}" stroke-opacity="{1 if first else .5}" stroke-width="{4.6 if first else .6+e["n"]*.17:.2f}" stroke-linecap="round"/>'
for n in R_['nodes']: g+=f'<circle cx="{px(n["x"]):.1f}" cy="{py(n["y"]):.1f}" r="{4.6+math.sqrt(n["passes"])*.8:.1f}" fill="#0A7538" stroke="#fff" stroke-width="1.7"/>'
court=lambda n:n.split(' ')[-1]; nomn=lambda n:court(n.get('name') or n.get('player'))
c3=f'<svg width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">{g}</svg>'+(puce('left:8px;bottom:8px',top['n'],f'passes entre {nomn(ND[top["a"]])} et {nomn(ND[top["b"]])}') if NIV=='A' else '')

# ------------------------------------------------------------------ carte 2 : la fiche (la roue seule, le rang)
FW,FH,HB=336,220,31; CR=F['criteres']; N=len(CR); COUL={'Création':'#EDA109','Progression':'#16A04D','Défense':'#064723','Production':'#D4262A'}
cx,cy,R1,R0=(94 if NIV in 'AC' else FW/2),HB+(FH-HB)/2,82,15; pas=360/N
def part(i,r):
    a0,a1=math.radians(i*pas+1.6-90),math.radians((i+1)*pas-1.6-90); P=lambda rr,a:f'{cx+rr*math.cos(a):.1f} {cy+rr*math.sin(a):.1f}'
    return f'M{P(R0,a0)}L{P(r,a0)}A{r:.1f} {r:.1f} 0 0 1 {P(r,a1)}L{P(R0,a1)}A{R0} {R0} 0 0 0 {P(R0,a0)}Z'
g=''.join(f'<path d="{part(i,R1)}" fill="#F3ECD8"/><path d="{part(i,R0+(R1-R0)*max(c["centile"],5)/100)}" fill="{COUL[c["famille"]]}"/>' for i,c in enumerate(CR))
g+=f'<circle cx="{cx}" cy="{cy}" r="{R0-2.5}" fill="#fff" stroke="#E6DFC9" stroke-width="1"/>'
fams=list(dict.fromkeys(c['famille'] for c in CR)); eff=len(F['notes_bassin'])
droite=((f'<div class="rang"><b>{F["rang"]}e</b><span>sur {eff}<br>latéraux</span></div>' if NIV=='A' else '')+f'<div class="leg"{" style=top:92px" if NIV=="C" else ""}>'+''.join(f'<i><u style="background:{COUL[f_]}"></u>{f_}</i>' for f_ in fams)+'</div>') if NIV in 'AC' else ''
c2=((f'<div class="hd"><b>{F["player"]}</b><span>{F["poste"]} · {F["team"]}</span><em>{F["note"]:.0f}<small>/100</small></em></div>' if NIV!='C' else '<div class="hd"><b>Le profil d\'un joueur</b></div>')
    +f'<svg width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" style="position:absolute;left:0;top:0">{g}</svg>{droite}')

# ------------------------------------------------------------------ carte 4 : le duel (trois lignes au lieu de sept, plus de « player score »)
(nA,JA),(nB,JB)=list(D['j'].items()); LIG=[('Buts','goals',0),('Buts attendus','xg',2),('Tirs','shots',0)]; HD=40
y0,dy=(HD+38,50); rows=''
for i,(lab,k,dec) in enumerate(LIG):
    a,b=JA[k],JB[k]; m=max(a,b); y=y0+i*dy; la,lb=86*a/m,86*b/m; fa,fb=('' if a>=b else ' class="f"'),('' if b>=a else ' class="f"')
    rows+=(f'<rect x="44" y="{y-6}" width="86" height="12" fill="#F3ECD8"/><rect x="{130-la:.1f}" y="{y-6}" width="{la:.1f}" height="12" fill="#09793A"/>'
           f'<rect x="206" y="{y-6}" width="86" height="12" fill="#F3ECD8"/><rect x="206" y="{y-6}" width="{lb:.1f}" height="12" fill="#0B1E13"/>')
    if NIV in 'AC': rows+=(f'<text x="10" y="{y+5.5}" font-family="BC" font-style="italic" font-weight="900" font-size="16" fill="#09793A"{" fill-opacity=\'.45\'" if a<b else ""}>{fr(a,dec)}</text>'
                        f'<text x="326" y="{y+5.5}" text-anchor="end" font-family="BC" font-style="italic" font-weight="900" font-size="16" fill="#0B1E13"{" fill-opacity=\'.4\'" if b<a else ""}>{fr(b,dec)}</text>'
                        f'<text x="168" y="{y+2.4}" text-anchor="middle" font-family="MO" font-weight="800" font-size="5.6" letter-spacing=".7" fill="#0B1E13">{lab.upper()}</text>')
c4=((f'<div class="hd2"><div class="g"><b>{nA}</b><span>{JA["team"]} · {JA["minutes"]:.0f} minutes</span></div><div class="d"><b>{nB}</b><span>{JB["team"]} · {JB["minutes"]:.0f} minutes</span></div><i>VS</i></div>' if NIV!='C' else '<div class="hd2"><div class="g" style="top:11px"><b style="font-size:20px">Le duel</b></div><i>VS</i></div>')
    +f'<svg width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" style="position:absolute;left:0;top:0">{rows}</svg>')

cartes=(f'<div class="cd b" style="left:52px;top:56px;transform:rotate(-2deg)">{c1}</div><div class="cd f" style="left:406px;top:82px;transform:rotate(1.5deg)">{c2}</div>'
        f'<div class="cd b" style="left:760px;top:52px;transform:rotate(-1.5deg)">{c3}</div><div class="cd f" style="left:1114px;top:80px;transform:rotate(2deg)">{c4}</div>')
ff=lambda fam,pkg,w,stl='normal':f'@font-face{{font-family:"{fam}";font-style:{stl};font-weight:{w};src:url({FS}{pkg}/files/{pkg}-latin-{w}-{stl}.woff2)}}'
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{ff('BC','barlow-condensed',900,'italic')}{ff('MO','montserrat',700)}{ff('MO','montserrat',800)}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}
#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)}}svg{{display:block}}
#pt{{position:absolute;left:0;top:-250px;width:1500px;height:1000px}}#pt *{{fill:none;stroke:#FFF6D0;stroke-width:.34;stroke-opacity:.8}}
.cd{{position:absolute;width:336px;box-shadow:0 22px 40px rgba(70,40,0,.34);background:#fff;overflow:hidden}}.cd.b{{border:5px solid #fff;height:{CH+10}px}}.cd.f{{height:{FH}px}}
.puce{{position:absolute;display:flex;align-items:center;gap:5px;background:#fff;padding:3px 7px 3px 6px;box-shadow:0 3px 8px rgba(70,40,0,.22);white-space:nowrap}}
.puce b{{font:italic 900 17px/1 "BC";color:{VD}}}.puce span{{font:800 5.6px/1 "MO";letter-spacing:.09em;text-transform:uppercase;color:{VD}}}
.hd{{position:absolute;left:0;top:0;right:0;height:{HB}px;background:#044F23;display:flex;align-items:center;padding:0 10px;gap:10px;white-space:nowrap}}
.hd b{{font:italic 900 22px/1 "BC";color:#fff;text-transform:uppercase}}.hd span{{font:700 5.6px/1 "MO";letter-spacing:.13em;text-transform:uppercase;color:#F7C41F;margin-top:2px}}
.hd em{{margin-left:auto;font:italic 900 25px/1 "BC";color:#F7C41F}}.hd em small{{font-size:9px;color:#F3ECD8;margin-left:2px}}
.rang{{position:absolute;left:206px;top:78px;display:flex;align-items:center;gap:6px}}.rang b{{font:italic 900 40px/.9 "BC";color:{VD}}}.rang span{{font:800 7px/1.25 "MO";letter-spacing:.08em;text-transform:uppercase;color:#0E1A13}}
.leg{{position:absolute;left:207px;top:128px;display:flex;flex-direction:column;gap:6px}}.leg i{{font:800 5.8px/1 "MO";font-style:normal;letter-spacing:.09em;text-transform:uppercase;color:#0E1A13;display:flex;align-items:center;gap:5px}}.leg u{{width:7px;height:7px;display:block}}
.hd2{{position:absolute;left:0;top:0;right:0;height:{HD}px;background:linear-gradient(90deg,#0E8141 50%,#0B1E13 50%);white-space:nowrap}}
.hd2 div{{position:absolute;top:7px}}.hd2 .g{{left:10px}}.hd2 .d{{right:10px;text-align:right}}.hd2 b{{display:block;font:italic 900 17px/1 "BC";color:#fff;text-transform:uppercase}}
.hd2 span{{display:block;margin-top:3px;font:700 5.2px/1 "MO";letter-spacing:.13em;text-transform:uppercase;color:#F7C41F}}
.hd2 i{{position:absolute;left:50%;top:50%;width:32px;height:32px;margin:-14px 0 0 -16px;border-radius:50%;background:#F4C41C;font:italic 900 13px/32px "BC";color:#0B1E13;text-align:center;box-shadow:0 3px 7px rgba(0,0,0,.25)}}
</style></head><body><div id="b">{fond}{cartes}</div><script>Promise.all([document.fonts.ready]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',OUT,NIV,'| note',F['note'],'rang',F['rang'],'sur',eff,'|',nA,JA['goals'],fr(JA['xg'],2),JA['shots'],'|',nB,JB['goals'],fr(JB['xg'],2),JB['shots'])

"""Vidéo « le compte expliqué » : maquettes des plans clés. Toutes les flèches et positions = vraie action (StatsBomb)."""
import json
SH='/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
exec(open(SH+'/maq_a.py',encoding='utf-8').read().split('# 1 : le score')[0])
SB='<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
P=json.load(open(SH+'/xt/top_possession.json'))['meilleure']; seq=P['sequence']
def scene(theme, zoom=False, data=False):
    nuit = theme=='nuit'
    herbe = '#0B5E30' if nuit else '#0B7A3B'; ligne = '#FFF6D0'
    cp = '#F6C41C' if nuit else '#FFF3C4'; cc='#FFFFFF'; rouge='#FF6B5E' if nuit else '#D4252A'
    L=f'stroke="{ligne}" stroke-width=".35" fill="none" stroke-opacity=".9"'
    g=f'''<rect x="-6" y="-6" width="132" height="92" fill="{herbe}"/>'''
    for i in range(12): g+=f'<rect x="{i*10}" y="0" width="5" height="80" fill="#FFFFFF" fill-opacity=".035"/>'
    g+=f'''<rect x="0" y="0" width="120" height="80" {L}/><line x1="60" y1="0" x2="60" y2="80" {L}/><circle cx="60" cy="40" r="9.15" {L}/>
<rect x="0" y="18" width="18" height="44" {L}/><rect x="102" y="18" width="18" height="44" {L}/><rect x="0" y="30" width="6" height="20" {L}/><rect x="114" y="30" width="6" height="20" {L}/>
<path d="M18 32A9 9 0 0 1 18 48" {L}/><path d="M102 32A9 9 0 0 0 102 48" {L}/><rect x="120" y="36" width="1.4" height="8" fill="{ligne}"/>'''
    g+='<defs>'+''.join(f'<marker id="m{n}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for n,c in (('p',cp),('c',cc),('r',rouge)))+'</defs>'
    for e in seq:
        if e['type']=='Ball Receipt*' and e.get('equipe')=='Mali':
            x,y=e['location'][:2]; g+=f'<circle cx="{x}" cy="{y}" r="2.2" fill="none" stroke="{cp}" stroke-width=".55"/><circle cx="{x}" cy="{y}" r=".7" fill="{cp}"/>'
    for e in seq:
        if e['type'] in ('Pass','Carry') and e.get('end_location'):
            (x1,y1),(x2,y2)=e['location'][:2],e['end_location'][:2]; gain=e.get('xt_ajoute') or 0
            if e['type']=='Pass':
                c,m=(rouge,'r') if gain>.1 else (cp,'p'); g+=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{.75 if gain>.1 else .5}" marker-end="url(#m{m})"/>'
            elif ((x2-x1)**2+(y2-y1)**2)**.5>2: g+=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cc}" stroke-width=".4" stroke-dasharray="1.2 1" marker-end="url(#mc)"/>'
    sh=P['fin']; sx,sy=sh['location'][:2]; g+=f'<line x1="{sx}" y1="{sy}" x2="120" y2="{sh["end_location"][1]}" stroke="{cc}" stroke-width=".4" stroke-dasharray=".6 .8"/><circle cx="{sx}" cy="{sy}" r="2.2" fill="none" stroke="{rouge}" stroke-width=".6"/>'
    if zoom: vb='78 8 46 64'; rot=48
    else: vb='-6 -6 132 92'; rot=58
    plan=f'<div style="position:absolute;left:-60px;top:{560 if not zoom else 470}px;width:1200px;height:{820 if not zoom else 700}px;perspective:1300px"><div style="width:100%;height:100%;transform:rotateX({rot}deg);transform-origin:50% 60%"><svg viewBox="{vb}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{g}</svg></div></div>'
    return plan
def fond_nuit(html):
    html=html.replace('linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)','radial-gradient(90% 55% at 50% 42%, #0D5A2E 0%, #063D20 45%, #021A0D 100%)')
    for a,b in (('#064A25','#FFFFFF'),('#04331A','#FFFFFF'),('#FDEBA6','#0F6B37'),('rgba(4,51,26,.75)','rgba(255,255,255,.75)'),('rgba(4,51,26,.8)','rgba(255,255,255,.8)')):
        html=html.replace(a,b)
    html=html.replace('.h2{position:absolute;left:64px;top:366px;font:italic 800 86px/1 "BC";color:#D4252A','.h2{position:absolute;left:64px;top:366px;font:italic 800 86px/1 "BC";color:#F6C41C')
    for img in ('logo_x.png','logo_tt.png'): html=html.replace(f'src="{img}" style="',f'src="{img}" style="filter:brightness(0) invert(1);')
    return html
out={}
leg=lambda nuit:(f'<div class="leg" style="top:1330px;color:{"#FFFFFF" if nuit else "#04331A"}"><span><svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" stroke="{"#F6C41C" if nuit else "#FFF3C4"}" stroke-width="5"/></svg>PASSE</span><span><svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" stroke="#FFF" stroke-width="4" stroke-dasharray="7 5"/></svg>COURSE</span><span><svg width="26" height="26"><circle cx="13" cy="13" r="10" fill="none" stroke="{"#F6C41C" if nuit else "#FFF3C4"}" stroke-width="3"/></svg>JOUEUR</span></div>')
for th in ('jaune','nuit'):
    nuit=th=='nuit'
    b=scene(th)+leg(nuit)+f'<div style="position:absolute;left:64px;top:1380px;font:800 28px/1.3 SC;letter-spacing:.04em;color:{"#FFFFFF" if nuit else "#04331A"}">22 SECONDES · 8 MALIENS · 12 GESTES MESURÉS</div>'
    h=pageT('NAMIBIE 0-0 MALI · CAN 2023 · <b>27e MINUTE</b>','UNE ACTION,','DES DONNÉES','',b,f'Positions et trajectoires réelles · Données {SB}')
    out['1'+('A' if th=='jaune' else 'B')]=fond_nuit(h) if nuit else h
    b=scene(th,zoom=True)+f'''<div style="position:absolute;left:64px;top:1230px;display:flex;gap:46px;color:{"#FFFFFF" if nuit else "#04331A"}">
<div><div style="font:italic 900 110px/1 BC;color:{"#FF6B5E" if nuit else "#D4252A"}">+0,25</div><div style="font:800 24px/1.2 SC">MENACE AJOUTÉE<br>PAR LE CENTRE DE Y. NIAKATÉ</div></div>
<div><div style="font:italic 900 110px/1 BC;color:{"#F6C41C" if nuit else "#0B7A3B"}">32 %</div><div style="font:800 24px/1.2 SC">CHANCE DE BUT<br>DE LA TÊTE DE SINAYOKO</div></div></div>'''
    h=pageT('LE ZOOM · <b>CE QUE LA DATA VOIT</b>','LE CENTRE,','LA TÊTE','',b,f'Menace : modèle MaliDataFoot (xT) · Chance de but : StatsBomb · Données {SB}')
    out['2'+('A' if th=='jaune' else 'B')]=fond_nuit(h) if nuit else h
for k,h in out.items(): open(f'_ex_{k}.html','w',encoding='utf-8').write(h)
print(list(out))

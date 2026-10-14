exec(open('/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad/maq_a.py',encoding='utf-8').read().split('# 1 : le score')[0])
def terrain(w=105,h=68,extra=''):
    L='stroke="#FFF6D0" stroke-width="0.6" fill="none"'
    return f'''<svg viewBox="-3 -3 {w+6} {h+6}" width="100%" height="100%" style="display:block;overflow:visible">
<rect x="0" y="0" width="{w}" height="{h}" fill="#0B7A3B"/>
<rect x="0" y="0" width="{w/2}" height="{h}" fill="#0E8A43"/>
<rect x="0" y="0" width="{w}" height="{h}" {L}/><line x1="{w/2}" y1="0" x2="{w/2}" y2="{h}" {L}/><circle cx="{w/2}" cy="{h/2}" r="9.15" {L}/>
<rect x="0" y="{h/2-20.16}" width="16.5" height="40.32" {L}/><rect x="{w-16.5}" y="{h/2-20.16}" width="16.5" height="40.32" {L}/>
<rect x="0" y="{h/2-9.16}" width="5.5" height="18.32" {L}/><rect x="{w-5.5}" y="{h/2-9.16}" width="5.5" height="18.32" {L}/>
<rect x="-2" y="{h/2-3.66}" width="2" height="7.32" fill="#FFF6D0"/><rect x="{w}" y="{h/2-3.66}" width="2" height="7.32" fill="#FFF6D0"/>{extra}</svg>'''
def plan3d(top,tilt,extra='',hpx=520):
    return f'<div style="position:absolute;left:90px;top:{top}px;width:860px;height:{hpx}px;perspective:1600px"><div style="width:100%;height:100%;transform:rotateX(52deg) rotateZ({-tilt}deg);transform-origin:50% 60%">{terrain(extra=extra)}</div></div>'
# A : le terrain penche (angle proportionnel à l'avantage : 1 degré pour 25 points d'Elo)
b=''
for i,(z,v,c) in enumerate([('EN EUROPE',169,'#04331A'),('EN AFRIQUE',317,'#0B7A3B')]):
    y=560+i*420
    b+=plan3d(y+30,v/25,hpx=330)
    b+=f'<div style="position:absolute;left:64px;top:{y-10}px;font:800 34px SC;letter-spacing:.05em;color:{c}">{z}</div><div style="position:absolute;right:134px;top:{y-30}px;font:italic 900 80px/1 BC;color:{c}">{v} <span style="font-size:40px">PTS</span></div>'
b+='<div style="position:absolute;left:64px;top:1360px;font:800 32px/1.25 SC;letter-spacing:.04em">L\'AVANTAGE DU TERRAIN VAUT<br><span style="color:#D4252A">PRESQUE DEUX FOIS PLUS</span> EN AFRIQUE</div>'
open('_vt_1.html','w',encoding='utf-8').write(pageT('COUCHE 2 · <b>LE TERRAIN</b>','LE TERRAIN','PENCHE','',b,'Écart domicile / extérieur en points de force (Elo) · Matchs officiels depuis 2000 · Inclinaison proportionnelle'))
# B : ce qui était attendu, en buts, sur le terrain (flèches proportionnelles aux buts attendus du modèle)
fl=('<defs><marker id="pm" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L10 5L0 10z" fill="#D4252A"/></marker>'
    '<marker id="pv" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L10 5L0 10z" fill="#FCD116"/></marker></defs>'
    '<line x1="40" y1="30" x2="96" y2="34" stroke="#D4252A" stroke-width="7.3" marker-end="url(#pm)"/>'
    '<line x1="64" y1="40" x2="10" y2="34" stroke="#FCD116" stroke-width="1.35" marker-end="url(#pv)"/>')
b=plan3d(640,0,fl,460)
b+=f'''<div style="position:absolute;left:64px;top:560px;display:flex;align-items:center;gap:14px">{D("Mali",56)}<span style="font:800 30px SC;letter-spacing:.05em;color:#0B7A3B">MALI · <span style="font:italic 900 56px BC">0,5</span> BUT ATTENDU</span></div>
<div style="position:absolute;right:134px;top:1130px;display:flex;align-items:center;gap:14px"><span style="font:800 30px SC;letter-spacing:.05em;color:#D4252A">MAROC · <span style="font:italic 900 56px BC">2,4</span> BUTS ATTENDUS</span>{D("Morocco",56)}</div>
<div class="bigR" style="top:1250px"><b>1-1</b><span>LE MALI A FAIT MIEUX<br>QUE <em>CE QU'ON ATTENDAIT</em></span></div>'''
open('_vt_2.html','w',encoding='utf-8').write(pageT('COUCHE 3 · <b>CE QUI ÉTAIT ATTENDU</b>','CE QU\'ON','ATTENDAIT','',b,'Selon notre modèle : force (Elo) et lieu · Épaisseur des flèches proportionnelle aux buts attendus'))

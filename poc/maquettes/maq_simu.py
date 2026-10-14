import json
src=open('posts_video.py',encoding='utf-8').read(); exec(src.split('# ---------- post 1')[0])
S=json.load(open('/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad/simu.json'))
d={int(k):v for k,v in S['dist'].items()}; q={int(k):v for k,v in S['qual'].items()}
ks=list(range(7,19)); x0,x1,yb,hmax=110,1010,890,420; w=(x1-x0)/len(ks); mx=max(d.values())
g=f'<line class="ax" x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}"/>'
for i,k in enumerate(ks):
    v=d.get(k,0); h=v/mx*hmax; x=x0+i*w+8; c='#0B7A3B' if (q.get(k) or 0)>=.99 else '#FFF3C4'
    g+=f'<rect x="{x:.0f}" y="{yb-h:.0f}" width="{w-16:.0f}" height="{h:.0f}" rx="3" fill="{c}"/>'
    g+=f'<text class="t" x="{x+(w-16)/2:.0f}" y="{yb+38}" text-anchor="middle">{k}</text>'
    if v>=.01: g+=f'<text x="{x+(w-16)/2:.0f}" y="{yb-h-12:.0f}" text-anchor="middle" style="font:italic 900 30px BC;fill:#064A25">{round(100*v)}</text>'
body=f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350">{g}</svg>'
body+=f'<div class="leg" style="top:{yb+66}px"><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#0B7A3B"></i>QUALIFIÉ À COUP SÛR</span><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#FFF3C4"></i>ÇA DÉPEND DES AUTRES</span></div>'
body+=f'<div style="position:absolute;left:64px;top:{yb+100}px;font:600 22px/1 SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">POINTS DU MALI À LA FIN DU GROUPE · % DES 100 000 SIMULATIONS</div>'
body+=f'<div class="bigR" style="top:{yb+150}px"><b>+{int(100*S["top2"])}<span style="font:italic 900 70px BC;color:#064A25"> %</span></b><span>DE CHANCES DE JOUER LA CAN 2027<br>AVANT LES DEUX MATCHS <em>CONTRE LE RWANDA</em></span></div>'
open('_ms_1.html','w',encoding='utf-8').write(page('ÉLIMINATOIRES CAN 2027 · GROUPE K · <b>100 000 SIMULATIONS</b>','ON A JOUÉ','LE GROUPE','',body,'Modèle de buts selon la force (Elo) et le lieu, appris sur 3 227 matchs officiels africains depuis 2000 · Les 2 premiers sont qualifiés'))
# image 2 : le modèle testé
cal=[('40',45,222),('52',50,284),('67',58,234),('85',82,255)]
b2=''
for i,(a,r,n) in enumerate(cal):
    y=400+i*140
    b2+=f'<div style="position:absolute;left:64px;top:{y}px;font:800 26px/1 SC;letter-spacing:.04em;color:#04331A">QUAND ON ANNONCE <span style="font:italic 900 40px BC;color:#064A25">{a} %</span></div>'
    b2+=f'<div style="position:absolute;left:64px;top:{y+46}px;width:{int(a)*8}px;height:22px;border-radius:3px;background:#FFF3C4"></div>'
    b2+=f'<div style="position:absolute;left:64px;top:{y+74}px;width:{r*8}px;height:22px;border-radius:3px;background:#0B7A3B"></div><div style="position:absolute;left:{64+r*8+14}px;top:{y+64}px;font:italic 900 40px BC;color:#0B7A3B">{r} %</div>'
b2+='<div class="leg" style="top:975px"><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#FFF3C4"></i>CE QUE LE MODÈLE ANNONCE POUR LE FAVORI</span><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#0B7A3B"></i>CE QUI EST ARRIVÉ</span></div>'
b2+='<div class="bigR" style="top:1030px"><b>995</b><span>MATCHS AFRICAINS DEPUIS 2020<br>QUE LE MODÈLE N\'AVAIT <em>JAMAIS VUS</em></span></div>'
open('_ms_2.html','w',encoding='utf-8').write(page('AVANT DE PRÉDIRE · <b>ON TESTE LE MODÈLE</b>','LE MODÈLE','EST-IL FIABLE ?','82%',b2,'Appris sur 2000-2019, testé sur 2020-2026 · Matchs officiels entre sélections africaines · Données : martj42'))

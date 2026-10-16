"""Post 3 « On a joué le groupe 100 000 fois » : les 4 images du thread X (gabarit posts_video.py, DA jaune).
Chiffres : outputs/analyses/simulation_groupe_k.json (pipeline). Sortie : _p3_1.html … _p3_4.html (1080 x 1350, capture ×2)."""
import json
src=open('posts_video.py',encoding='utf-8').read(); exec(src.split('# ---------- post 1')[0])
S=json.load(open(ICI/'../outputs/analyses/simulation_groupe_k.json',encoding='utf-8'))
pc=lambda v:round(100*v)
# drapeaux supplémentaires (dessin simplifié sur 20 x 20)
DR['Rwanda']='<rect width="20" height="10" fill="#00A1DE"/><rect y="10" width="20" height="5" fill="#FAD201"/><rect y="15" width="20" height="5" fill="#20603D"/><circle cx="15" cy="4.6" r="2.2" fill="#FAD201"/>'
DR['Cape Verde']='<rect width="20" height="20" fill="#003893"/><rect y="10.5" width="20" height="1.4" fill="#fff"/><rect y="11.9" width="20" height="1.4" fill="#CF2027"/><rect y="13.3" width="20" height="1.4" fill="#fff"/>'+''.join(f'<circle cx="{7.5+3.6*math.cos(k*math.pi/5):.2f}" cy="{12.4+3.6*math.sin(k*math.pi/5):.2f}" r=".55" fill="#F7D116"/>' for k in range(10))
DR['Liberia']=''.join(f'<rect y="{i*20/11:.2f}" width="20" height="{20/11+.05:.2f}" fill="{"#BF0A30" if i%2==0 else "#fff"}"/>' for i in range(11))+'<rect width="9" height="9.1" fill="#002868"/>'+et(4.5,4.6,2.6,'#fff')
CF={'Mali':'ml','Rwanda':'rw','Cape Verde':'cv','Liberia':'lr','South Sudan':'ss','Chad':'td','Namibia':'na','Congo':'cg','Guinea-Bissau':'gw','Botswana':'bw','Equatorial Guinea':'gq','Burundi':'bi','Kenya':'ke','Mozambique':'mz'}
def drapv(p,t=44): return f'<img src="drapeaux/{CF[p]}.svg" style="width:{t}px;height:{t}px;display:block;border-radius:50%">'
FRN.update({'Rwanda':'Rwanda','Cape Verde':'Cap-Vert','Liberia':'Liberia','South Sudan':'Soudan du Sud','Chad':'Tchad','Namibia':'Namibie','Congo':'Congo','Guinea-Bissau':'Guinée-Bissau','Botswana':'Botswana','Equatorial Guinea':'Guinée équat.','Burundi':'Burundi','Kenya':'Kenya','Mozambique':'Mozambique'})

# ---- image 1 : le classement du groupe K après 2 journées (calculé depuis les matchs joués)
tab={e:dict(j=0,pts=0,bp=0,bc=0) for e in S['equipes']}
for h,a,x,y in S['joues']:
    for e,f,c in ((h,x,y),(a,y,x)):
        t=tab[e]; t['j']+=1; t['bp']+=f; t['bc']+=c; t['pts']+=3 if f>c else 1 if f==c else 0
ordre=sorted(tab,key=lambda e:(-tab[e]['pts'],-(tab[e]['bp']-tab[e]['bc']),-tab[e]['bp']))
b=''; y0=430
b+=f'<div style="position:absolute;left:64px;top:{y0}px;width:952px;display:flex;font:800 22px/1 SC;letter-spacing:.06em;color:rgba(4,51,26,.75)"><span style="width:470px"></span><span style="width:120px;text-align:center">JOUÉS</span><span style="width:120px;text-align:center">POINTS</span><span style="width:120px;text-align:center">DIFF.</span><span style="width:122px;text-align:center">BUTS</span></div>'
for i,e in enumerate(ordre):
    t=tab[e]; y=y0+44+i*92; m=e=='Mali'
    col='#0B7A3B' if m else '#04331A'; acc='#0B7A3B' if m else '#064A25'
    d=t['bp']-t['bc']; ds=f'+{d}' if d>0 else str(d)
    bu=f'<b style="color:#D4252A">{t["bp"]}</b>' if e in('Mali','Rwanda') else str(t['bp'])
    b+=f'''<div style="position:absolute;left:64px;top:{y}px;width:952px;height:76px;display:flex;align-items:center;color:{col};border-bottom:2px solid rgba(6,74,37,.22)">
<span style="width:70px;text-align:center;font:italic 900 46px/1 BC;color:{acc}">{i+1}</span><span style="width:60px">{drapv(e,44)}</span>
<span style="width:340px;font:800 34px/1 SC;letter-spacing:.03em">{FRN[e].upper()}</span>
<span style="width:120px;text-align:center;font:700 32px/1 SC">{t["j"]}</span><span style="width:120px;text-align:center;font:italic 900 50px/1 BC;color:{acc}">{t["pts"]}</span>
<span style="width:120px;text-align:center;font:700 32px/1 SC">{ds}</span><span style="width:122px;text-align:center;font:italic 900 46px/1 BC">{bu}</span></div>'''
rM=ordre.index('Mali')+1
b+=f'<div class="bigR" style="top:1010px"><b>{rM}<span style="font:italic 900 80px BC">e</span></b><span>LE MALI, À 6 POINTS COMME LE RWANDA<br><em>4 BUTS MARQUÉS CONTRE 5</em></span></div>'
open(ICI/'_p3_1.html','w',encoding='utf-8').write(page('ÉLIMINATOIRES CAN 2027 · GROUPE K · <b>APRÈS 2 JOURNÉES</b>','GROUPE K','LE RWANDA DEVANT','6',b,
  'Résultats : martj42, recoupés avec la presse · Départage : règlement CAF des éliminatoires'))

# ---- image 2 : le modèle testé (même gabarit que la maquette du 14/10, la tranche où il force est signalée)
cal=S['test_honnete']['dixon_coles']['calibration']
b2=''
for i,c in enumerate(cal):
    a,r=pc(c['annonce']),pc(c['reel']); y=400+i*140; force=a-r>=6
    b2+=f'<div style="position:absolute;left:64px;top:{y}px;font:800 26px/1 SC;letter-spacing:.04em;color:#04331A">QUAND ON ANNONCE <span style="font:italic 900 40px BC;color:#064A25">{a} %</span></div>'
    b2+=f'<div style="position:absolute;left:64px;top:{y+46}px;width:{a*8}px;height:22px;border-radius:3px;background:#FFF3C4"></div>'
    b2+=f'<div style="position:absolute;left:64px;top:{y+74}px;width:{r*8}px;height:22px;border-radius:3px;background:#0B7A3B"></div><div style="position:absolute;left:{64+r*8+14}px;top:{y+64}px;font:italic 900 40px BC;color:#0B7A3B">{r} %</div>'
    if force: b2+=f'<div style="position:absolute;left:{64+a*8+24}px;top:{y+46}px;font:italic 900 40px/1 BC;color:#D4252A">−{a-r} PTS</div>'
b2+='<div class="leg" style="top:975px"><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#FFF3C4"></i>CE QUE LE MODÈLE ANNONCE POUR LE FAVORI</span><span><i style="display:block;width:28px;height:18px;border-radius:3px;background:#0B7A3B"></i>CE QUI EST ARRIVÉ</span></div>'
b2+=f'<div class="bigR" style="top:1030px"><b>{S["test_honnete"]["teste_sur"]}</b><span>MATCHS AFRICAINS DEPUIS 2020<br>QUE LE MODÈLE N\'AVAIT <em>JAMAIS VUS</em></span></div>'
open(ICI/'_p3_2.html','w',encoding='utf-8').write(page('AVANT DE PRÉDIRE · <b>ON TESTE LE MODÈLE</b>','LE MODÈLE','EST-IL FIABLE ?','82%',b2,
  f'Appris sur 2000-2019 ({S["test_honnete"]["appris_sur"]} matchs), testé sur 2020-2026 · Matchs officiels entre sélections africaines · Données : martj42'))

# ---- image 3 : les points du Mali sur 100 000 simulations (légende corrigée : 11-12 points = 99,8 %, pas « à coup sûr »)
d={int(k):v for k,v in S['points_mali'].items()}; q={int(k):v for k,v in S['qualifie_selon_points'].items()}
ks=list(range(7,19)); x0,x1,yb,hmax=110,1010,890,420; w=(x1-x0)/len(ks); mx=max(d.values())
C3=lambda k:'#064A25' if q.get(k,0)>=.99 else '#FFF3C4'
g=f'<line class="ax" x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}"/>'
for i,k in enumerate(ks):
    v=d.get(k,0); h=v/mx*hmax; x=x0+i*w+8
    g+=f'<rect x="{x:.0f}" y="{yb-h:.0f}" width="{w-16:.0f}" height="{h:.0f}" rx="3" fill="{C3(k)}"/>'
    g+=f'<text class="t" x="{x+(w-16)/2:.0f}" y="{yb+38}" text-anchor="middle">{k}</text>'
    if v>=.01: g+=f'<text x="{x+(w-16)/2:.0f}" y="{yb-h-12:.0f}" text-anchor="middle" style="font:italic 900 30px BC;fill:#064A25">{pc(v)}</text>'
sw=lambda c:f'<i style="display:block;width:28px;height:18px;border-radius:3px;background:{c}"></i>'
b3=f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350">{g}</svg>'
b3+=f'<div class="leg" style="top:{yb+62}px;gap:20px;font-size:22px"><span>{sw("#064A25")}QUALIFIÉ AU MOINS 998 FOIS SUR 1 000</span><span>{sw("#FFF3C4")}ÇA DÉPEND DES AUTRES</span></div>'
b3+=f'<div style="position:absolute;left:64px;top:{yb+98}px;font:600 22px/1 SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">POINTS DU MALI À LA FIN DU GROUPE · % DES 100 000 SIMULATIONS</div>'
b3+=f'<div class="bigR" style="top:{yb+150}px"><b>+98<span style="font:italic 900 70px BC;color:#064A25"> %</span></b><span>DE CHANCES DE JOUER LA CAN 2027<br>ET PREMIER <em>PLUS DE 8 FOIS SUR 10</em></span></div>'
open(ICI/'_p3_3.html','w',encoding='utf-8').write(page('ÉLIMINATOIRES CAN 2027 · GROUPE K · <b>100 000 SIMULATIONS</b>','ON A JOUÉ','LE GROUPE','',b3,
  f'Modèle (force Elo et lieu) appris sur {S["modele"]["appris_sur_matchs"]:,} matchs officiels africains depuis 2000 · Les 2 premiers sont qualifiés'.replace(',',' ')))

# ---- image 4 : à Kigali, le modèle (moyenne africaine) contre le vrai bilan du Mali à l'extérieur face à bien plus faible
X=S['exterieur_contre_plus_faible']; XM=X['Mali']; tx=pc(XM['victoires']/XM['matchs'])
b4=f'''<div style="position:absolute;left:64px;top:390px;width:440px">
<div style="font:italic 900 150px/.86 BC;color:#064A25">{pc(S["match_kigali"]["victoire"])}<span style="font-size:80px"> %</span></div>
<div style="margin-top:14px;font:800 26px/1.25 SC;letter-spacing:.04em;color:#04331A">CHANCES DE VICTOIRE À KIGALI<br>SELON LE MODÈLE</div></div>
<div style="position:absolute;left:560px;top:390px;width:460px">
<div style="font:italic 900 150px/.86 BC;color:#0B7A3B">{tx}<span style="font-size:80px"> %</span></div>
<div style="margin-top:14px;font:800 26px/1.25 SC;letter-spacing:.04em;color:#04331A">{XM["victoires"]} VICTOIRES SUR {XM["matchs"]} DU MALI<br>CHEZ BIEN PLUS FAIBLE</div></div>'''
L=list(reversed(X['matchs_mali'])); half=(len(L)+1)//2
for k,(d,adv,x,y) in enumerate(L):
    col,row=k//half,k%half; xx=64+col*480; yy=650+row*66
    c='#0B7A3B' if y>x else ('#D4252A' if y<x else '#064A25')
    b4+=f'''<div style="position:absolute;left:{xx}px;top:{yy}px;width:452px;height:56px;display:flex;align-items:center;gap:14px;border-bottom:2px solid rgba(6,74,37,.22)">
<span style="width:62px;font:700 24px/1 SC;color:rgba(4,51,26,.75)">{d[:4]}</span>{drapv(adv,34)}<span style="flex:1;font:800 25px/1 SC;letter-spacing:.02em;color:#04331A;white-space:nowrap">{FRN[adv].upper()}</span>
<span style="font:italic 900 38px/1 BC;color:{c}">{x}-{y}</span></div>'''
open(ICI/'_p3_4.html','w',encoding='utf-8').write(page('NOVEMBRE · <b>RWANDA - MALI, À KIGALI</b>','LE MODÈLE','SOUS-ESTIME LES AIGLES ?',f'{tx}%',b4,
  'Matchs officiels africains depuis 2015 où le Mali, visiteur, avait au moins 150 pts d\'Elo de plus · Données : martj42'))
print('ok')

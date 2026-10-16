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
CF={'Mali':'ml','Rwanda':'rw','Cape Verde':'cv','Liberia':'lr'}
def drapv(p,t=44): return f'<img src="drapeaux/{CF[p]}.svg" style="width:{t}px;height:{t}px;display:block;border-radius:50%">'
FRN.update({'Rwanda':'Rwanda','Cape Verde':'Cap-Vert','Liberia':'Liberia'})

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

# ---- image 4 : les deux matchs contre le Rwanda
def jauge(y,titre,m):
    v,n,dd=pc(m['victoire']),pc(m['nul']),pc(m['defaite'])
    s=f'<div style="position:absolute;left:64px;top:{y}px;font:800 30px/1 SC;letter-spacing:.04em;color:#04331A">{titre}</div>'
    s+=f'<div style="position:absolute;left:64px;top:{y+48}px;width:952px;height:84px;display:flex;border-radius:3px;overflow:hidden">'
    for val,c,tc,lab in ((v,'#064A25','#FFFFFF','VICTOIRE'),(n,'#FFF3C4','#04331A','NUL'),(dd,'#D4252A','#FFFFFF','DÉFAITE')):
        s+=f'<div style="width:{val}%;background:{c};color:{tc};display:flex;flex-direction:column;justify-content:center;padding-left:{14 if val>=12 else 6}px;overflow:hidden;white-space:nowrap"><b style="font:italic 900 {46 if val>=12 else 30}px/1 BC">{val}&#8239;%</b>'+(f'<span style="font:800 16px/1 SC;letter-spacing:.05em">{lab}</span>' if val>=12 else '')+'</div>'
    return s+'</div>'
b4=jauge(420,'MALI - RWANDA · À DOMICILE',S['match_bamako'])+jauge(620,'RWANDA - MALI · À KIGALI',S['match_kigali'])
b4+='<div class="leg" style="top:790px;gap:22px"><span>'+sw('#064A25')+'VICTOIRE DU MALI</span><span>'+sw('#FFF3C4')+'NUL</span><span>'+sw('#D4252A')+'DÉFAITE DU MALI</span></div>'
b4+=f'<div class="bigR" style="top:900px"><b>{pc(S["match_kigali"]["nul"])}<span style="font:italic 900 70px BC;color:#064A25"> %</span></b><span>DE CHANCES DE NUL À KIGALI<br>CHEZ LUI, IL A TENU <em>LE SÉNÉGAL ET LE NIGERIA</em></span></div>'
open(ICI/'_p3_4.html','w',encoding='utf-8').write(page('NOVEMBRE · <b>MALI - RWANDA, ALLER ET RETOUR</b>','LE PIÈGE','C\'EST LE NUL','30%',b4,
  'Chances selon notre modèle (force Elo et lieu) · Rwanda 1-1 Sénégal (09/2023), Rwanda 0-0 Nigeria (09/2024)'))
print('ok')

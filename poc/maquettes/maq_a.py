import math
src=open('posts_video.py',encoding='utf-8').read(); exec(src.split('# ---------- post 1')[0])
W,H=1080,1920
def trameT():
    g='';st=30;y=st/2;row=0
    while y<H:
        x=st/2+(st/2 if row%2 else 0)
        while x<W: d=math.hypot(x-1080,y)/1500; g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.2+9*max(0,1-d)**2.6:.2f}"/>'; x+=st
        y+=st;row+=1
    return f'<svg style="position:absolute;left:0;top:0" width="{W}" height="{H}"><g fill="#FDEBA6" fill-opacity="0.85">{g}</g></svg>'
CSS2=CSS.replace('html,body{width:1080px;height:1350px','html,body{width:1080px;height:1920px').replace('#c{position:relative;width:1080px;height:1350px','#c{position:relative;width:1080px;height:1920px')
CSS2=CSS2.replace('.kick{position:absolute;left:64px;top:66px;font:600 26px','.kick{position:absolute;left:64px;top:166px;font:600 30px').replace('.h1{position:absolute;left:58px;top:104px;font:italic 900 150px','.h1{position:absolute;left:58px;top:206px;font:italic 900 170px').replace('.h2{position:absolute;left:64px;top:244px;font:italic 800 76px','.h2{position:absolute;left:64px;top:366px;font:italic 800 86px').replace('.ghost{position:absolute;right:56px;top:46px;font:italic 900 330px','.ghost{position:absolute;right:40px;top:150px;font:italic 900 360px').replace('#foot{position:absolute;left:64px;right:64px;top:1186px','#foot{position:absolute;left:64px;right:134px;top:1472px').replace('#src{position:absolute;left:64px;top:1270px;font:600 19px','#src{position:absolute;left:64px;top:1557px;font:600 22px')
def pageT(kick,h1,h2,ghost,body,srcl):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS2}</style></head><body><div id="c">{trameT()}
<div class="ghost">{ghost}</div><div class="kick">{kick}</div><div class="h1">{h1}</div><div class="h2">{h2}</div>{body}
<div id="foot"><img src="logo-verte.png"><div class="wm">Mali<i>Data</i>Foot</div><div class="soc"><img src="logo_x.png" style="height:28px"><img src="logo_tt.png" style="height:36px">@MaliDataFoot</div></div>
<div id="src">{srcl}</div></div><script>document.fonts.ready.then(()=>{{window.READY=true}})</script></body></html>'''
D=lambda p,t=150:drap(p,t)
# 1 : le score
b=f'''<div style="position:absolute;left:64px;right:134px;top:640px;display:flex;align-items:center;justify-content:space-between">
<div style="text-align:center">{D("Morocco")}<div style="font:800 34px SC;letter-spacing:.05em;margin-top:14px">MAROC</div></div>
<div style="font:italic 900 260px/1 BC;color:#064A25">1-1</div>
<div style="text-align:center">{D("Mali")}<div style="font:800 34px SC;letter-spacing:.05em;margin-top:14px;color:#0B7A3B">MALI</div></div></div>
<div style="position:absolute;left:64px;top:1080px;font:800 40px/1.25 SC;letter-spacing:.04em">SUR LE PAPIER :<br><span style="color:#D4252A">UN SIMPLE NUL.</span></div>'''
open('_va_1.html','w',encoding='utf-8').write(pageT('AMICAL · TANGER · <b>4 OCTOBRE 2026</b>','CE QUE LE 1-1','NE DIT PAS','',b,'Score : FRMF, ESPN'))
# 2 : la force
b=f'''<div style="position:absolute;left:64px;top:620px;display:flex;align-items:center;gap:28px">{D("Morocco",120)}<div><div style="font:italic 900 210px/.86 BC;color:#064A25">6<span style="font-size:110px">e</span></div><div style="font:800 32px SC;letter-spacing:.05em">MAROC · MONDIAL</div></div></div>
<div style="position:absolute;left:64px;top:930px;display:flex;align-items:center;gap:28px">{D("Mali",120)}<div><div style="font:italic 900 210px/.86 BC;color:#0B7A3B">53<span style="font-size:110px">e</span></div><div style="font:800 32px SC;letter-spacing:.05em">MALI · MONDIAL</div></div></div>
<div style="position:absolute;left:64px;top:1260px;font:800 36px/1.25 SC;letter-spacing:.04em">47 PLACES D'ÉCART AU CLASSEMENT FIFA<br>AU COUP D'ENVOI</div>'''
open('_va_2.html','w',encoding='utf-8').write(pageT('COUCHE 1 · <b>LA FORCE DES DEUX ÉQUIPES</b>','LA FORCE','47 PLACES','',b,'Classement FIFA du 20 juillet 2026, le dernier avant le match'))
# 3 : le terrain
Z=[('AMÉRIQUE DU SUD',411),('AFRIQUE',317),('ASIE',217),('EUROPE',169)]
b=''
for i,(z,v) in enumerate(Z):
    y=640+i*150; af=z=='AFRIQUE'
    b+=f'<div style="position:absolute;left:64px;top:{y}px;font:800 32px SC;letter-spacing:.05em;color:{"#0B7A3B" if af else "#04331A"}">{z}</div><div style="position:absolute;left:64px;top:{y+48}px;width:{v*1.9:.0f}px;height:46px;border-radius:4px;background:{"#0B7A3B" if af else "#FFF3C4"}"></div><div style="position:absolute;left:{64+v*1.9+18:.0f}px;top:{y+38}px;font:italic 900 64px/1 BC;color:{"#0B7A3B" if af else "#064A25"}">{v}</div>'
b+='<div style="position:absolute;left:64px;top:1250px;font:800 34px/1.25 SC;letter-spacing:.04em">JOUER À L\'EXTÉRIEUR EN AFRIQUE,<br>LE TERRAIN VAUT <span style="color:#D4252A">PRESQUE DEUX FOIS PLUS</span> QU\'EN EUROPE</div>'
b+='<div style="position:absolute;left:64px;top:1360px;font:600 24px SC;letter-spacing:.03em;color:rgba(4,51,26,.8)">ÉCART DOMICILE / EXTÉRIEUR, EN POINTS DE FORCE (ELO)</div>'
open('_va_3.html','w',encoding='utf-8').write(pageT('COUCHE 2 · <b>LE TERRAIN</b>','LE TERRAIN','PÈSE PRESQUE DOUBLE','',b,'Matchs officiels depuis 2000 · Modèle MaliDataFoot · Données : martj42'))
# 4 : l'attendu
P=[('MAROC GAGNE',81,'#D4252A'),('NUL',14,'#FFF3C4'),('MALI GAGNE',5,'#0B7A3B')]
b='<div style="position:absolute;left:64px;top:700px;width:882px;height:90px;display:flex;border-radius:6px;overflow:hidden">'+''.join(f'<div style="width:{p}%;background:{c}"></div>' for _,p,c in P)+'</div>'
for i,(l,p,c) in enumerate(P):
    b+=f'<div style="position:absolute;left:64px;top:{850+i*110}px;display:flex;align-items:baseline;gap:20px"><span style="font:italic 900 80px/1 BC;color:{"#064A25" if c=="#FFF3C4" else c}">{p} %</span><span style="font:800 32px SC;letter-spacing:.05em">{l}</span></div>'
b+='<div class="bigR" style="top:1230px"><b>19<span style="font:italic 900 70px BC;color:#064A25"> %</span></b><span>DE CHANCES DE NE PAS PERDRE.<br>LE MALI L\'A FAIT : <em>UN TRÈS BON RÉSULTAT</em></span></div>'
open('_va_4.html','w',encoding='utf-8').write(pageT('COUCHE 3 · <b>CE QUI ÉTAIT ATTENDU</b>','CE QU\'ON','ATTENDAIT','19%',b,'Modèle MaliDataFoot : force (Elo) et lieu, appris sur 3 227 matchs officiels africains'))
# 5 : la fin
b='''<div style="position:absolute;left:64px;top:640px;font:800 44px/1.3 SC;letter-spacing:.04em">CHAQUE MATCH,<br>CHAQUE JOUEUR,<br>CHAQUE CHIFFRE,<br><span style="color:#D4252A">REMIS DANS SON CONTEXTE.</span></div>
<div style="position:absolute;left:64px;top:1090px;display:flex;flex-direction:column;gap:22px;font:italic 900 70px/1 BC;color:#064A25"><span>LES AIGLES</span><span>LES MALIENS EN CLUB</span><span>L'HISTOIRE</span></div>'''
open('_va_5.html','w',encoding='utf-8').write(pageT('<b>MALIDATAFOOT</b>','LE FOOT MALIEN','PAR LA DATA','',b,''))

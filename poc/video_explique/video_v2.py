"""Vidéo TikTok « le compte expliqué », version 2 (idée validée par Diaby le 14/10/2026) :
1 l'accroche « 0-0, rien à voir ? » ; 2 la plongée « rayons X » dans un stade dessiné, couche par couche (le ballon, les joueurs,
la menace, le tir) ; 3 le tournoi du Mali en trois flashs (64 tirs, réseau de passes, récupérations) ; 4 le carrousel des fiches
de gauche à droite, qui s'arrête sur Dorgeles (il était dans l'action) ; 5 le dézoom sur le mur de fiches ; 6 la signature.
Tout ce qui est dessiné sur le terrain vient des événements StatsBomb (donnees_video.json, top_possession.json).
Usage (depuis visuels/, node_modules lié) : python3 ../poc/video_explique/video_v2.py <dossier des fiches floutées> [sortie.html]"""
import json, os, re, sys, random
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(os.path.dirname(ICI))
FICHES = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else '_v2.html'
DV = json.load(open(os.path.join(ICI, 'donnees_video.json'), encoding='utf-8'))
P = json.load(open(os.path.join(RACINE, 'poc/xt/top_possession.json')))['meilleure']
FONTS = re.search(r"FONTS='''(.*?)'''", open('posts_video.py', encoding='utf-8').read(), re.S).group(1)
FONTS += '@font-face{font-family:"IN";font-weight:700;src:url(node_modules/@fontsource/inter/files/inter-latin-700-normal.woff2)}'

# ---- l'action : passes et conduites du Mali, temps réel
def ts(e):
    h, m, s = e['timestamp'].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
seq = P['sequence']; t0 = ts(seq[0]); mali = [e for e in seq if e.get('equipe') == 'Mali']
GESTES = []
for k, e in enumerate(mali):
    if e['type'] in ('Pass', 'Carry') and e.get('end_location'):
        (x1, y1), (x2, y2) = e['location'][:2], e['end_location'][:2]
        if e['type'] == 'Carry' and ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5 < 2: continue
        suiv = next((f for f in mali[k + 1:] if ts(f) > ts(e)), None)
        GESTES.append({'k': 'p' if e['type'] == 'Pass' else 'c', 'a': round(ts(e) - t0, 3), 'b': round((ts(suiv) if suiv else ts(e) + 1) - t0, 3),
                       'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'xt': e.get('xt_ajoute') or 0})
RECEP = [{'a': round(ts(e) - t0, 3), 'x': e['location'][0], 'y': e['location'][1]} for e in mali if e['type'] == 'Ball Receipt*']
DUREE_REELLE = P['fin']['t_relatif_s']

# ---- le mur et les fiches
SIX = ['hamari-traore_poste', 'lassine-sinayoko_poste', 'amadou-haidara_poste', 'kamory-doumbia_poste', 'mamadou-sangare-2002_FICTIF', 'nene-dorgeles-2002_FICTIF']
TUILES = sorted(f for f in os.listdir(FICHES) if f.startswith('tile_'))
os.makedirs('_vx', exist_ok=True)
for f in os.listdir(FICHES):
    if f.startswith(('full_', 'tile_')) and not os.path.exists(os.path.join('_vx', f)): os.symlink(os.path.join(FICHES, f), os.path.join('_vx', f))
COLS, ROWS = 23, 19; rc, cc0 = ROWS // 2, COLS // 2; rnd = random.Random(7); CASES = []
for r in range(ROWS):
    for c in range(COLS):
        f = 'tile_nene-dorgeles-2002_FICTIF.jpg' if (r, c) == (rc, cc0) else TUILES[rnd.randrange(len(TUILES))]
        CASES.append([r, c, TUILES.index(f)])
imgs = ''.join(f'<img id="ti{i}" src="_vx/{f}" class="cache">' for i, f in enumerate(TUILES))
imgs += ''.join(f'<img id="fp{i}" src="_vx/full_{f}.png" class="cache">' for i, f in enumerate(SIX))

DATA = {'gestes': GESTES, 'recep': RECEP, 'reel': DUREE_REELLE, 'tir': DV['action']['tir'], 'joueurs': DV['action']['joueurs'],
        'xt': DV['xt']['valeurs'], 'tirs': DV['tirs'], 'recup': DV['recuperations'], 'reseau': DV['reseau'], 'resume': DV['resume'],
        'cases': CASES, 'cols': COLS, 'rows': ROWS, 'rc': rc, 'cc': cc0}

HTML = '''<!doctype html><html><head><meta charset="utf-8"><style>@@FONTS@@
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#021A0D}
#c{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(90% 55% at 50% 42%,#0D5A2E 0%,#063D20 45%,#021A0D 100%)}
canvas{position:absolute;left:0;top:0}.cache{display:none}
.t{position:absolute;left:64px;white-space:nowrap;opacity:0}
.kick{font:600 30px/1 "SC";letter-spacing:.06em;color:#FFFFFF}.kick b{font-weight:800}
.h1{font:italic 900 150px/.9 "BC";color:#FFFFFF;text-transform:uppercase}
.h2{font:italic 800 80px/1 "BC";color:#F6C41C;text-transform:uppercase}
.lab{font:800 30px/1 "SC";letter-spacing:.07em;color:#F6C41C}
.lab span{color:#FFFFFF}
.big{font:italic 900 120px/1 "BC"}
.sm{font:800 24px/1.2 "SC";letter-spacing:.04em;color:#FFFFFF}
#zero{position:absolute;left:0;right:0;top:620px;text-align:center;font:italic 900 430px/1 "BC";color:#FFFFFF;opacity:0}
#foot{position:absolute;left:64px;right:134px;top:1472px;display:flex;align-items:center;gap:16px;opacity:0}
#foot img.lg{width:64px;height:64px;border-radius:50%}
#foot .wm{font:italic 400 46px/1 "BCS";color:#FFFFFF}#foot .wm i{font-weight:600}
#foot .soc{margin-left:auto;display:flex;align-items:center;gap:12px;font:700 28px/1 "SC";color:#FFFFFF}
#src{position:absolute;left:64px;top:1557px;font:600 22px/1 "SC";color:rgba(255,255,255,.75);white-space:nowrap;opacity:0}
#jaune{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#F6C41C;opacity:0}
#fin{position:absolute;left:0;right:0;top:700px;text-align:center;color:#064A25;opacity:0}
#fin img.lg{width:190px;height:190px;border-radius:50%;display:block;margin:0 auto}
#fin .wm{font:italic 400 128px/1 "BCS";margin-top:34px}#fin .wm i{font-weight:600}
#fin .so{display:flex;justify-content:center;align-items:center;gap:20px;margin-top:34px;font:700 40px/1 "IN"}
#voile{position:absolute;left:0;top:0;width:1080px;height:1920px;background:linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%);opacity:0}
</style></head><body><div id="c">
<canvas id="cv" width="1080" height="1920"></canvas>
<div id="jaune"></div><canvas id="cv2" width="1080" height="1920"></canvas>
<div id="zero">0-0</div>
<div class="t kick" id="k0" style="top:470px">NAMIBIE · MALI · <b>CAN 2023</b></div>
<div class="t h2" id="q0" style="top:1110px;left:0;right:0;text-align:center">RIEN À VOIR ?</div>
<div class="t kick" id="k1" style="top:166px">NAMIBIE 0-0 MALI · CAN 2023 · <b>27e MINUTE</b></div>
<div class="t h1" id="h1" style="top:206px">AUX RAYONS X</div>
<div class="t lab" id="L1" style="top:372px">COUCHE 1 · <span>LE BALLON · 22 SECONDES · 9 PASSES · 8 MALIENS</span></div>
<div class="t lab" id="L2" style="top:372px">COUCHE 2 · <span>LES JOUEURS AU MOMENT DE LA TÊTE</span></div>
<div class="t lab" id="L3" style="top:372px">COUCHE 3 · <span>LA MENACE · NOTRE MODÈLE (xT)</span></div>
<div class="t lab" id="L4" style="top:372px">COUCHE 4 · <span>LE TIR · 32 % DE CHANCE DE BUT</span></div>
<div class="t" id="clk" style="top:428px;font:italic 900 72px/1 BC;color:#FFFFFF"><span id="clkv">26'40</span> <span id="clkl" style="font:800 26px SC;letter-spacing:.06em;color:#F6C41C;vertical-align:14px">TEMPS DE JEU RÉEL</span></div>
<div class="t sm" id="s1" style="top:430px">22 SECONDES · 8 MALIENS · 12 GESTES MESURÉS</div>
<div class="t sm" id="n3" style="top:430px">LE CENTRE DE Y. NIAKATÉ AJOUTE <span style="color:#FF6B5E">+0,25</span> DE MENACE<br><span style="color:rgba(255,255,255,.75)">PLUS LA CASE EST CHAUDE, PLUS UN BUT Y EST PROCHE</span><span id="v3" style="display:none"></span></div>
<div class="t sm" id="n4" style="top:430px">LA TÊTE DE SINAYOKO : <span style="color:#F6C41C">32 % DE CHANCE DE BUT</span><br><span style="color:#F6C41C">À CÔTÉ. LE SCORE DIT 0-0.</span><span id="v4" style="display:none"></span></div>
<div class="t kick" id="k5" style="top:166px">LE MALI À LA CAN 2023 · <b>5 MATCHS</b></div>
<div class="t h1" id="h5a" style="top:206px">@@TIRS@@ TIRS</div>
<div class="t h1" id="h5b" style="top:206px">LES PASSES</div>
<div class="t h1" id="h5c" style="top:206px">@@RECUP@@ BALLONS</div>
<div class="t lab" id="l5a" style="top:372px">TAILLE DU POINT = <span>QUALITÉ DE L'OCCASION (xG)</span></div>
<div class="t lab" id="l5b" style="top:372px">QUI JOUE AVEC QUI · <span>@@LIENS@@ LIENS DE 12 PASSES ET PLUS</span></div>
<div class="t lab" id="l5c" style="top:372px">RÉCUPÉRÉS · <span>LIGNE = HAUTEUR MOYENNE</span></div>
<div id="foot"><img class="lg" src="logo-verte.png"><div class="wm">Mali<i>Data</i>Foot</div><div class="soc"><img src="logo_x.png" style="height:28px;filter:brightness(0) invert(1)"><img src="logo_tt.png" style="height:36px;filter:brightness(0) invert(1)">@MaliDataFoot</div></div>
<div id="src">Positions et trajectoires réelles · Menace : modèle MaliDataFoot (xT) · Données <img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px"></div>
<div class="t h2" id="dor" style="top:1560px;left:0;right:0;text-align:center;color:#064A25">LUI, <span style="color:#D4252A">IL ÉTAIT DANS L'ACTION.</span></div>
<div id="voile"></div>
<div id="fin"><img class="lg" src="logo-verte.png"><div class="wm">Mali<i>Data</i>Foot</div><div class="so"><img src="logo_x.png" style="height:40px"><img src="logo_tt.png" style="height:52px"><span>@MaliDataFoot</span></div><div id="qq" style="margin-top:70px;font:italic 800 64px/1.1 BC;color:#064A25;text-transform:uppercase">Quel joueur on passe<br><span style="color:#D4252A">aux rayons X ensuite ?</span></div></div>
@@IMGS@@
</div><script>
const D=@@DATA@@;
@@JS@@
</script></body></html>'''

JS = r'''
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), lerp=(a,b,u)=>a+(b-a)*u, io=u=>u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2, oc=u=>1-Math.pow(1-u,3);
const $=id=>document.getElementById(id), W=1080, H=1920;
const cv=$('cv'), X=cv.getContext('2d'), cv2=$('cv2'), X2=cv2.getContext('2d');
// ---------------------------------------------------------------- caméra
let C={p:[0,0,0],r:[0,0,0],u:[0,0,0],f:[0,0,0],F:1000,cy:1000};
function camera(p,t,F,cy){const f=nrm(sub(t,p)), r=nrm(crs([0,0,1],f)), u=crs(f,r); C={p,r,u,f,F,cy};}
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]], dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2], crs=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const nrm=a=>{const l=Math.hypot(...a);return [a[0]/l,a[1]/l,a[2]/l]};
const cam=q=>{const d=sub(q,C.p);return [dot(d,C.r),dot(d,C.u),dot(d,C.f)]};
const scr=c=>[W/2+C.F*c[0]/c[2], C.cy-C.F*c[1]/c[2]];
const P=(x,y,z=0)=>{const c=cam([x,y,z]);return c[2]>.5?scr(c):null};
const kz=(x,y,z=0)=>{const c=cam([x,y,z]);return c[2]>.5?C.F/c[2]:0};   // pixels par yard à cet endroit
function poly(g,pts,fill,stroke,lw){   // polygone au sol, coupé au plan proche
  let c=pts.map(q=>cam(q)), o=[];
  for(let i=0;i<c.length;i++){const a=c[i],b=c[(i+1)%c.length];const ia=a[2]>.5, ib=b[2]>.5;
    if(ia)o.push(a); if(ia!=ib){const u=(.5-a[2])/(b[2]-a[2]);o.push([lerp(a[0],b[0],u),lerp(a[1],b[1],u),.5]);}}
  if(o.length<3)return; g.beginPath(); o.forEach((q,i)=>{const s=scr(q);i?g.lineTo(s[0],s[1]):g.moveTo(s[0],s[1])}); g.closePath();
  if(fill){g.fillStyle=fill;g.fill()} if(stroke){g.strokeStyle=stroke;g.lineWidth=lw;g.stroke()}}
function seg(g,a,b,col,w,dash){   // segment 3D, épaisseur en yards
  let ca=cam(a), cb=cam(b); if(ca[2]<.5&&cb[2]<.5)return;
  if(ca[2]<.5){const u=(.5-ca[2])/(cb[2]-ca[2]);ca=ca.map((v,i)=>lerp(v,cb[i],u))} if(cb[2]<.5){const u=(.5-cb[2])/(ca[2]-cb[2]);cb=cb.map((v,i)=>lerp(v,ca[i],u))}
  const s=scr(ca), e=scr(cb), k=C.F/((ca[2]+cb[2])/2); g.strokeStyle=col; g.lineWidth=Math.max(1,w*k); g.lineCap='round';
  g.setLineDash(dash?dash.map(v=>v*k):[]); g.beginPath(); g.moveTo(s[0],s[1]); g.lineTo(e[0],e[1]); g.stroke(); g.setLineDash([]);}
function ring(g,x,y,r,col,w,fill){const pts=[];for(let i=0;i<40;i++){const a=i/40*2*Math.PI;pts.push([x+r*Math.cos(a),y+r*Math.sin(a),0])} poly(g,pts,fill||null,col,Math.max(1.5,w*kz(x,y)));}
function fleche(g,x1,y1,x2,y2,col,w,dash,u){   // flèche au sol qui se dessine (u de 0 à 1)
  const xe=lerp(x1,x2,u), ye=lerp(y1,y2,u); seg(g,[x1,y1,.02],[xe,ye,.02],col,w,dash);
  if(u>=1){const L=Math.hypot(x2-x1,y2-y1)||1, ux=(x2-x1)/L, uy=(y2-y1)/L, h=Math.max(1.4,w*4);
    poly(g,[[x2,y2,.03],[x2-ux*h-uy*h*.55,y2-uy*h+ux*h*.55,.03],[x2-ux*h+uy*h*.55,y2-uy*h-ux*h*.55,.03]],col);}}
function texte(g,x,y,z,txt,col,px,align){const s=P(x,y,z); if(!s)return; g.font=`800 ${px}px SC`; g.textAlign=align||'center'; const w=g.measureText(txt).width, x0=align=='left'?s[0]:(align=='right'?s[0]-w:s[0]-w/2); if(x0<16||x0+w>1064)return; g.fillStyle=col; g.fillText(txt,s[0],s[1]);}   // un nom coupé par le bord n'est pas affiché
// ---------------------------------------------------------------- le stade
function stade(g,alpha){
  g.globalAlpha=alpha;
  const T='#031A0D', T2='#05261A';
  poly(g,[[-6,-14,0],[126,-14,0],[136,-26,16],[-16,-26,16]],T2); poly(g,[[-6,94,0],[126,94,0],[136,106,16],[-16,106,16]],T2);
  poly(g,[[122.5,-14,0],[122.5,94,0],[140,106,18],[140,-26,18]],T); poly(g,[[-6,-14,0],[-6,94,0],[-20,106,18],[-20,-26,18]],T);
  poly(g,[[-6,-6,0],[122.5,-6,0],[122.5,86,0],[-6,86,0]],'#0B5E30');
  for(let i=0;i<12;i++) if(i%2) poly(g,[[i*10,-6,0],[Math.min(i*10+10,122.5),-6,0],[Math.min(i*10+10,122.5),86,0],[i*10,86,0]],'#0E6935');
  // panneaux au bord du terrain
  poly(g,[[-2,-9,0],[122,-9,0],[122,-9,1.1],[-2,-9,1.1]],'#0A4A26'); 
  const L='#FFF6D0', w=.18;
  const rect=(a,b,c,d)=>{seg(g,[a,b,0],[c,b,0],L,w);seg(g,[c,b,0],[c,d,0],L,w);seg(g,[c,d,0],[a,d,0],L,w);seg(g,[a,d,0],[a,b,0],L,w)};
  rect(0,0,120,80); seg(g,[60,0,0],[60,80,0],L,w); rect(0,18,18,62); rect(102,18,120,62); rect(0,30,6,50); rect(114,30,120,50);
  const arc=(cx,cy,r,a0,a1)=>{let p=null;for(let i=0;i<=30;i++){const a=lerp(a0,a1,i/30), q=[cx+r*Math.cos(a),cy+r*Math.sin(a),0];if(p)seg(g,p,q,L,w);p=q}};
  arc(60,40,9.15,0,2*Math.PI); arc(108,40,9.15,Math.PI*0.705,Math.PI*1.295); arc(12,40,9.15,-Math.PI*0.295,Math.PI*0.295);
  // les buts : poteaux et barre
  for(const gx of [0,120]){const s=gx?1:-1; seg(g,[gx,36,0],[gx,36,2.67],'#FFFFFF',.14); seg(g,[gx,44,0],[gx,44,2.67],'#FFFFFF',.14); seg(g,[gx,36,2.67],[gx,44,2.67],'#FFFFFF',.14);
    seg(g,[gx+s*2,36,0],[gx,36,2.67],'rgba(255,255,255,.35)',.06); seg(g,[gx+s*2,44,0],[gx,44,2.67],'rgba(255,255,255,.35)',.06); seg(g,[gx+s*2,36,0],[gx+s*2,44,0],'rgba(255,255,255,.35)',.06);}
  // pylônes d'éclairage (sans halo)
  for(const [px,py] of [[-14,-22],[134,-22],[-14,102],[134,102]]){seg(g,[px,py,0],[px,py,26],'#0A3D22',.5); poly(g,[[px-3,py,26],[px+3,py,26],[px+3,py,29],[px-3,py,29]],'#E8EFE9');}
  g.globalAlpha=1;}
// ---------------------------------------------------------------- les couches de données
function menace(g,a){ if(a<=0)return; const V=D.xt; let mx=0; V.forEach(r=>r.forEach(v=>mx=Math.max(mx,v)));
  for(let cy=0;cy<12;cy++)for(let cx=0;cx<16;cx++){const v=V[cy][cx]/mx; if(v<.08)continue;
    const r=Math.round(lerp(246,255,v)), gg=Math.round(lerp(196,107,v)), b=Math.round(lerp(28,94,v));
    poly(g,[[cx*7.5+.15,cy*6.667+.15,.01],[cx*7.5+7.35,cy*6.667+.15,.01],[cx*7.5+7.35,cy*6.667+6.52,.01],[cx*7.5+.15,cy*6.667+6.52,.01]],`rgba(${r},${gg},${b},${(a*lerp(.08,.42,v)).toFixed(3)})`);}}
function action(g,tt,hl){ // tt = temps réel de l'action (0 à 21,3 s)
  for(const e of D.gestes){if(tt<e.a)continue; const u=cl((tt-e.a)/Math.max(.4,e.b-e.a)); const fort=e.xt>.1;
    const col=fort?'#FF6B5E':(e.k=='p'?'#F6C41C':'#FFFFFF'), w=fort?.42+hl*.3:(e.k=='p'?.3:.22);
    fleche(g,e.x1,e.y1,e.x2,e.y2,col,w,e.k=='c'?[1.2,1]:null,io(u));}
  for(const r of D.recep){if(tt<r.a)continue; const u=oc(cl((tt-r.a)/.5)); ring(g,r.x,r.y,1.25*u,'#F6C41C',.22);}}
function texteBig(g,x,y,z,txt,col,px){const q=P(x,y,z); if(!q)return; g.font=`italic 900 ${px}px BC`; g.fillStyle=col; g.textAlign='center'; g.fillText(txt,q[0],q[1]);}
function joueurs(g,a,tir,lab3){ if(a<=0)return; g.globalAlpha=a;
  const J=D.joueurs.concat([{x:D.tir.x,y:D.tir.y,mali:true,nom:'Lassine Sinayoko',tireur:true}]);
  J.sort((p,q)=>q.x-p.x);
  for(const j of J){const col=j.tireur?'#FF6B5E':(j.mali?'#F6C41C':'#FFFFFF'); ring(g,j.x,j.y,1.5,col,.26);}
  for(const j of J){const col=j.tireur?'#FF6B5E':(j.mali?'#F6C41C':'#FFFFFF'); seg(g,[j.x,j.y,0],[j.x,j.y,2.1],col,.16); const s=P(j.x,j.y,2.35); if(s){g.fillStyle=col;g.beginPath();g.arc(s[0],s[1],Math.max(4,.42*kz(j.x,j.y,2.35)),0,7);g.fill();}}
  for(const j of J){ if(!j.mali)continue; const n=j.nom=='Nene Dorgeles'?'DORGELES':j.nom.split(' ').slice(-1)[0].toUpperCase(); const al=j.tireur?'right':(j.nom=='Nene Dorgeles'?'left':'center'); texte(g,j.x,j.y,3.7,n,j.tireur?'#FF6B5E':'#F6C41C',Math.round(lerp(26,40,cl((kz(j.x,j.y)-20)/40))),al);}
  g.globalAlpha=1;
  if(lab3>0){const c=D.gestes.find(e=>e.xt>.1); X.globalAlpha=lab3*a; ring(g,c.x1,c.y1,1.5,'#F6C41C',.26); seg(g,[c.x1,c.y1,0],[c.x1,c.y1,2.1],'#F6C41C',.16); texte(g,c.x1,c.y1,3.7,'Y. NIAKATÉ','#F6C41C',34,'left'); X.globalAlpha=a;}
  if(lab3>0){const c=D.gestes.find(e=>e.xt>.1); const mx=(c.x1+c.x2)/2, my=(c.y1+c.y2)/2; X.globalAlpha=lab3; texteBig(g,mx,my,4.2,'+'+(.25*oc(lab3)).toFixed(2).replace('.',','),'#FF6B5E',96); X.globalAlpha=a;}
  if(tir>0){X.globalAlpha=cl(tir*2); texteBig(g,D.tir.x,D.tir.y,6.2,Math.round(32*oc(cl(tir)))+' %','#F6C41C',110); X.globalAlpha=1;}
  if(tir>.6){X.globalAlpha=cl((tir-.6)*3); texte(g,D.tir.fin[0],D.tir.fin[1]-1.5,3.4,'À CÔTÉ','#FFFFFF',34); X.globalAlpha=1;}
  if(tir>0){const e=D.tir.fin; const u=io(cl(tir)); seg(g,[D.tir.x,D.tir.y,1.9],[lerp(D.tir.x,e[0],u),lerp(D.tir.y,e[1],u),lerp(1.9,e[2]||.9,u)],'#FFFFFF',.16,[.5,.5]);}}
function tirs(g,a){ if(a<=0)return; for(const s of D.tirs){const r=.6+Math.sqrt(s.xg)*3.6; ring(g,s.x,s.y,r*a,s.but?'#F6C41C':'#FFFFFF',.18,s.but?'rgba(246,196,28,.85)':'rgba(255,255,255,.12)');}}
function reseau(g,a){ if(a<=0)return; const N=D.reseau.noeuds; let mx=0; D.reseau.liens.forEach(l=>mx=Math.max(mx,l[2]));
  for(const [p,q,n] of D.reseau.liens){const A=N[p],B=N[q]; const u=io(cl(a*1.6-.3)); seg(g,[A[0],A[1],.02],[lerp(A[0],B[0],u),lerp(A[1],B[1],u),.02],'#F6C41C',.08+.42*n/mx);}
  for(const p in N){const v=N[p]; ring(g,v[0],v[1],1.2+v[2]/220*a,'#F6C41C',.2,'#063D20');}
  const NOMS={'Boubakar Kouyate':'KOUYATÉ','Sikou Niakate':'S. NIAKATÉ','Hamari Traoré':'HAMARI'}; g.globalAlpha=cl(a*2-.6);
  for(const p in NOMS) if(N[p]) texte(g,N[p][0],N[p][1],3.2,NOMS[p],'#FFFFFF',30); g.globalAlpha=1;}
function recup(g,a){ if(a<=0)return; let sx=0; for(const r of D.recup){sx+=r.x; ring(g,r.x,r.y,.75*a,'#F6C41C',.16,'rgba(246,196,28,.55)');}
  const m=sx/D.recup.length; if(a>.5) seg(g,[m,-3,.02],[m,83,.02],'#FF6B5E',.35,[1.4,1]);}
// ---------------------------------------------------------------- le carrousel et le mur (canevas 2)
const T={hook:0, plonge:2.0, couche1:3.2, couche2:6.7, couche3:8.0, couche4:9.3, tournoi:11.2, flash:1.15, carrousel:15.0, mur:17.8, fin:20.9, duree:25.0};
window.DUREE=T.duree;
function mur(m){ const S=lerp(.78,.10,m), rx=lerp(0,28,m)*Math.PI/180, rz=lerp(0,-14,m)*Math.PI/180, yc=lerp(960,960,m), co=Math.cos(rx), GX=1180, GY=1580, DD=2400;
  const L=[]; for(const [r,c,k] of D.cases){const x0=(c-D.cc)*GX, y0=(r-D.rr)*GY; const Xr=x0*Math.cos(rz)-y0*Math.sin(rz), Yr=x0*Math.sin(rz)+y0*Math.cos(rz);
    const Xs=Xr*S, Ys=Yr*S, z=-Ys*Math.sin(rx), f=DD/(DD+z), sx=540+Xs*f, sy=yc+Ys*co*f, k2=S*f;
    if(sx<-700*k2||sx>1080+700*k2||sy<-800*k2||sy>1920+800*k2)continue; L.push([z,sx,sy,k2,k,r==D.rc&&c==D.cc]);}
  L.sort((a,b)=>b[0]-a[0]);
  for(const [z,sx,sy,k2,k,centre] of L){X2.save();X2.translate(sx,sy);X2.rotate(rz);X2.scale(k2,k2*co);
    if(centre&&k2>.3)X2.drawImage($('fp5'),0,120,1080,1460,-540,-730,1080,1460); else X2.drawImage($('ti'+k),-540,-730,1080,1460); X2.restore();}}
D.rr=D.rc;
function carrousel(t){ // un train de fiches côte à côte qui file de gauche à droite et s'arrête sur Dorgeles (la dernière)
  const N=6, S=.78, PAS=880, u=cl((t-T.carrousel-.2)/2.3), e=1-Math.pow(1-u,4);
  const tete=lerp(-460,540+(N-1)*PAS,e);   // position de la 1re fiche (Hamari), en tête du train
  for(let i=0;i<N;i++){const x=tete-i*PAS; if(x<-460||x>1540)continue; X2.save(); X2.translate(x,960); X2.scale(S,S); X2.drawImage($('fp'+i),0,120,1080,1460,-540,-730,1080,1460);
    if(i<2){X2.fillStyle='#D4252A'; X2.fillRect(-540,-830,560,84); X2.fillStyle='#FFFFFF'; X2.font='800 46px SC'; X2.textAlign='left'; X2.fillText("DANS L'ACTION",-512,-772);}
    X2.restore();}}
// ---------------------------------------------------------------- le temps
function vis(id,t,a,b,dy=30){const e=$(id); const u=oc(cl((t-a)/.4)), v=b==null?0:cl((t-b)/.3); e.style.opacity=(u*(1-v)).toFixed(3); e.style.transform=`translateY(${((1-u)*dy).toFixed(1)}px)`;}
const K=[ // images clés de la caméra : temps, position, cible, focale, centre vertical (caméra derrière le but que le Mali attaque)
 [0,[88,40,200],[88.5,40,0],1250,1000],[T.plonge,[88,40,200],[88.5,40,0],1250,1000],[T.couche1,[150,40,36],[84,40,0],1250,950],
 [T.couche2-.2,[146,40,30],[92,40,0],1350,950],[T.couche2+.9,[143,43,28],[100,43,0],1220,960],[T.couche4+1.6,[141,43,26],[102,43,0],1220,960],
 [T.tournoi+.5,[152,40,72],[70,40,0],1300,920],[T.carrousel,[152,40,72],[70,40,0],1300,920]];
function camAt(t){let i=0; while(i<K.length-2&&t>K[i+1][0])i++; const a=K[i], b=K[i+1]; const u=io(cl((t-a[0])/(b[0]-a[0])));
  camera(a[1].map((v,j)=>lerp(v,b[1][j],u)),a[2].map((v,j)=>lerp(v,b[2][j],u)),lerp(a[3],b[3],u),lerp(a[4],b[4],u));}
window.seek=function(t){
  X.clearRect(0,0,W,H); X2.clearRect(0,0,W,H);
  // 1. l'accroche
  const z=$('zero'); const zu=oc(cl(t/.35)), zo=cl((t-T.plonge)/.45); z.style.opacity=(zu*(1-zo)).toFixed(3); z.style.transform=`scale(${(1+.6*io(zo)).toFixed(3)})`;
  vis('k0',t,.15,T.plonge); vis('q0',t,.75,T.plonge);
  // 2. le terrain
  if(t<T.carrousel+.6){ camAt(t); const sa=cl((t-T.plonge)/.6); X.globalAlpha=1; stade(X,sa);
    const reel=cl((t-T.couche1)/(T.couche2-T.couche1-.3))*D.reel;
    const mena=cl((t-T.couche3)/.6)*(1-cl((t-T.tournoi)/.4)), act=1-cl((t-T.tournoi)/.4);
    menace(X,mena*sa);
    if(act>0){X.globalAlpha=act; action(X,t>=T.couche1?reel:-1, Math.sin(Math.PI*cl((t-T.couche3)/.9)) ); joueurs(X,cl((t-T.couche2)/.5)*act, cl((t-T.couche4-.2)/.5), cl((t-T.couche3-.2)/.6)*act); X.globalAlpha=1;}
    const f=T.flash, t5=T.tournoi;
    const fa=cl((t-t5)/.35)*(1-cl((t-t5-f)/.15)), fb=cl((t-t5-f)/.35)*(1-cl((t-t5-2*f)/.15)), fc=cl((t-t5-2*f)/.35)*(1-cl((t-T.carrousel)/.3));
    tirs(X,fa); reseau(X,fb); recup(X,fc);
    // le terrain s'efface vers la droite quand le jaune entre
  }
  vis('k1',t,T.plonge+.5,T.tournoi); vis('h1',t,T.plonge+.65,T.tournoi);
  vis('L1',t,T.couche1,T.couche2); vis('clk',t,T.couche1,T.couche3);
  {const r=cl((t-T.couche1)/(T.couche2-T.couche1-.3))*D.reel, sec=1600+r; $('clkv').textContent=Math.floor(sec/60)+"'"+String(Math.floor(sec%60)).padStart(2,'0'); $('clkl').textContent=t>=T.couche2?'ARRÊT SUR IMAGE · LA TÊTE':'TEMPS DE JEU RÉEL';} vis('L2',t,T.couche2,T.couche3); vis('L3',t,T.couche3,T.couche4); vis('L4',t,T.couche4,T.tournoi);
  $('s1').style.opacity=0; $('n3').style.opacity=0; $('n4').style.opacity=0;
  $('v3').textContent='+'+(.25*oc(cl((t-T.couche3-.2)/.7))).toFixed(2).replace('.',','); $('v4').textContent=Math.round(32*oc(cl((t-T.couche4-.25)/.7)));
  const f=T.flash, t5=T.tournoi; vis('k5',t,t5,T.carrousel); vis('h5a',t,t5,t5+f); vis('l5a',t,t5+.1,t5+f); vis('h5b',t,t5+f,t5+2*f); vis('l5b',t,t5+f+.1,t5+2*f); vis('h5c',t,t5+2*f,T.carrousel); vis('l5c',t,t5+2*f+.1,T.carrousel);
  vis('foot',t,T.plonge+.4,T.carrousel,0); vis('src',t,T.plonge+.6,T.carrousel,0);
  // 3. le jaune entre par la gauche, puis le carrousel
  const j=io(cl((t-T.carrousel)/.45)); $('jaune').style.opacity=j>0?1:0; $('jaune').style.clipPath=`inset(0 ${(100-100*j).toFixed(2)}% 0 0)`;
  if(t>=T.carrousel&&t<T.mur) carrousel(t);
  vis('dor',t,T.carrousel+2.0,T.mur+.2,20);
  // 4. le mur
  if(t>=T.mur) mur(io(cl((t-T.mur)/2.6)));
  // 5. la fin
  const fi=oc(cl((t-T.fin)/.6)); $('voile').style.opacity=(fi*.94).toFixed(3); vis('fin',t,T.fin+.25,null,40);
};
Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{}))]).then(()=>{window.seek(0);window.READY=true});
'''
h = HTML.replace('@@FONTS@@', FONTS).replace('@@DATA@@', json.dumps(DATA, ensure_ascii=False)).replace('@@JS@@', JS).replace('@@IMGS@@', imgs)
h = h.replace('@@TIRS@@', str(DV['resume']['tirs'])).replace('@@RECUP@@', str(DV['resume']['recuperations'])).replace('@@LIENS@@', str(len(DV['reseau']['liens'])))
open(OUT, 'w', encoding='utf-8').write(h); print('ok', OUT)

"""Vidéo TikTok « le compte expliqué » : montage animé (sans voix).
Plans : 1B la plongée sur le terrain de nuit et l'action Namibie-Mali (vraies positions StatsBomb, vrai rythme accéléré),
2B le zoom (+0,25 de menace, 32 % de chance de but), 3 les six fiches floutées qui défilent, 4 le dézoom sur le mur de fiches, la fin.
Usage (depuis visuels/, polices liées dans node_modules) :
  python3 ../poc/maquettes/video_explique_montage.py <dossier des images de fiches floutées>
puis : node capture_video.mjs _vx_main.html sortie.mp4 30
Les fiches floutées se fabriquent avec FLOU=1 python3 fiche_pro.py <fiche.json> x.html tiktok (voir journal du 14/10/2026)."""
import json, math, os, sys, random
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(os.path.dirname(ICI))
FICHES = sys.argv[1]
exec(open(os.path.join(ICI, 'maq_a.py'), encoding='utf-8').read().split('# 1 : le score')[0])
SB = '<img src="logo_statsbomb.png" style="height:22px;vertical-align:-5px">'
P = json.load(open(os.path.join(RACINE, 'poc/xt/top_possession.json')))['meilleure']; seq = P['sequence']

# ---------------------------------------------------------------- temps : l'action réelle (22 s) jouée en 6 s
T0, K = 1.7, 0.28
def ts(e):
    h, m, s = e['timestamp'].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
t_debut = ts(seq[0])
vt = lambda e: T0 + (ts(e) - t_debut) * K
mali = [e for e in seq if e.get('equipe') == 'Mali']
herbe, ligne, cp, cc, rouge = '#0B5E30', '#FFF6D0', '#F6C41C', '#FFFFFF', '#FF6B5E'
L = f'stroke="{ligne}" stroke-width=".35" fill="none" stroke-opacity=".9"'
g = f'<rect x="-6" y="-6" width="132" height="92" fill="{herbe}"/>'
for i in range(12): g += f'<rect x="{i*10}" y="0" width="5" height="80" fill="#FFFFFF" fill-opacity=".035"/>'
g += f'''<rect x="0" y="0" width="120" height="80" {L}/><line x1="60" y1="0" x2="60" y2="80" {L}/><circle cx="60" cy="40" r="9.15" {L}/>
<rect x="0" y="18" width="18" height="44" {L}/><rect x="102" y="18" width="18" height="44" {L}/><rect x="0" y="30" width="6" height="20" {L}/><rect x="114" y="30" width="6" height="20" {L}/>
<path d="M18 32A9 9 0 0 1 18 48" {L}/><path d="M102 32A9 9 0 0 0 102 48" {L}/><rect x="120" y="36" width="1.4" height="8" fill="{ligne}"/>'''
g += '<defs>' + ''.join(f'<marker id="m{n}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for n, c in (('p', cp), ('c', cc), ('r', rouge))) + '</defs>'
ANIM = []   # éléments animés : [id, type, t0, t1, ...]
n = 0
for k, e in enumerate(mali):
    if e['type'] in ('Pass', 'Carry') and e.get('end_location'):
        (x1, y1), (x2, y2) = e['location'][:2], e['end_location'][:2]; gain = e.get('xt_ajoute') or 0
        suiv = next((f for f in mali[k + 1:] if ts(f) > ts(e)), None)
        t0 = vt(e); t1 = max(t0 + .12, vt(suiv) if suiv else t0 + .3)
        if e['type'] == 'Pass':
            c, m = (rouge, 'r') if gain > .1 else (cp, 'p'); w = .75 if gain > .1 else .5
            g += f'<line id="a{n}" x1="{x1}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{c}" stroke-width="{w}" data-m="url(#m{m})" opacity="0"/>'
        elif math.hypot(x2 - x1, y2 - y1) > 2:
            g += f'<line id="a{n}" x1="{x1}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{cc}" stroke-width=".4" stroke-dasharray="1.2 1" data-m="url(#mc)" opacity="0"/>'
        else: continue
        ANIM.append([f'a{n}', 'ligne', round(t0, 3), round(t1, 3), x1, y1, x2, y2, 1 if gain > .1 else 0]); n += 1
    elif e['type'] == 'Ball Receipt*':
        x, y = e['location'][:2]
        g += f'<g id="a{n}" opacity="0"><circle cx="{x}" cy="{y}" r="2.2" fill="none" stroke="{cp}" stroke-width=".55"/><circle cx="{x}" cy="{y}" r=".7" fill="{cp}"/></g>'
        ANIM.append([f'a{n}', 'joueur', round(vt(e), 3), round(vt(e) + .25, 3), x, y]); n += 1
sh = P['fin']; sx, sy = sh['location'][:2]; t_tir = T0 + sh['t_relatif_s'] * K
g += f'<line id="tir" x1="{sx}" y1="{sy}" x2="{sx}" y2="{sy}" stroke="{cc}" stroke-width=".4" stroke-dasharray=".6 .8" opacity="0"/><circle id="tirc" cx="{sx}" cy="{sy}" r="2.2" fill="none" stroke="{rouge}" stroke-width=".6" opacity="0"/>'
ANIM.append(['tir', 'ligne', round(t_tir, 3), round(t_tir + .35, 3), sx, sy, 120, sh['end_location'][1], 0])
ANIM.append(['tirc', 'joueur', round(t_tir - .05, 3), round(t_tir + .2, 3), sx, sy])
FIN_ACTION = max(a[3] for a in ANIM)

# ---------------------------------------------------------------- page de nuit (plans 1 et 2)
leg = f'<div id="leg" class="leg" style="top:1330px;color:#FFFFFF"><span><svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" stroke="{cp}" stroke-width="5"/></svg>PASSE</span><span><svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" stroke="#FFF" stroke-width="4" stroke-dasharray="7 5"/></svg>CONDUITE</span><span><svg width="26" height="26"><circle cx="13" cy="13" r="10" fill="none" stroke="{cp}" stroke-width="3"/></svg>JOUEUR</span></div>'
stat = '<div id="stat" style="position:absolute;left:64px;top:1380px;font:800 28px/1.3 SC;letter-spacing:.04em;color:#FFFFFF">22 SECONDES · 8 MALIENS · 12 GESTES MESURÉS</div>'
chif = f'''<div id="chif" style="position:absolute;left:64px;top:1230px;display:flex;gap:46px;color:#FFFFFF">
<div id="c1"><div style="font:italic 900 110px/1 BC;color:{rouge}"><span id="v1">+0,00</span></div><div style="font:800 24px/1.2 SC">MENACE AJOUTÉE<br>PAR LE CENTRE DE Y. NIAKATÉ</div></div>
<div id="c2"><div style="font:italic 900 110px/1 BC;color:{cp}"><span id="v2">0</span> %</div><div style="font:800 24px/1.2 SC">CHANCE DE BUT<br>DE LA TÊTE DE SINAYOKO</div></div></div>'''
cam = f'<div id="cam" style="position:absolute;left:-60px;top:560px;width:1200px;height:820px;perspective:1300px"><div id="rot" style="width:100%;height:100%;transform-origin:50% 60%"><svg id="pv" viewBox="-6 -6 132 92" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{g}</svg></div></div>'
body = cam + leg + stat + chif
h = pageT('NAMIBIE 0-0 MALI · CAN 2023 · <b>27e MINUTE</b>', 'UNE ACTION,', 'DES DONNÉES', '', body, f'<span id="s1">Positions et trajectoires réelles · Données {SB}</span>')
# fond de nuit (même recette que la planche 1B / 2B)
h = h.replace('linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)', 'radial-gradient(90% 55% at 50% 42%, #0D5A2E 0%, #063D20 45%, #021A0D 100%)')
for a, b in (('#064A25', '#FFFFFF'), ('#04331A', '#FFFFFF'), ('#FDEBA6', '#0F6B37'), ('rgba(4,51,26,.75)', 'rgba(255,255,255,.75)'), ('rgba(4,51,26,.8)', 'rgba(255,255,255,.8)')):
    h = h.replace(a, b)
h = h.replace('.h2{position:absolute;left:64px;top:366px;font:italic 800 86px/1 "BC";color:#D4252A', '.h2{position:absolute;left:64px;top:366px;font:italic 800 86px/1 "BC";color:#F6C41C')
for img in ('logo_x.png', 'logo_tt.png'): h = h.replace(f'src="{img}" style="', f'src="{img}" style="filter:brightness(0) invert(1);')
h = h.replace('<div class="kick">', '<div class="kick" id="k1">', 1).replace('<div class="h1">', '<div class="h1" id="t1">', 1).replace('<div class="h2">', '<div class="h2" id="u1">', 1)
deux = '<div class="kick" id="k2" style="opacity:0">LE ZOOM · <b>CE QUE LA DATA VOIT</b></div><div class="h1" id="t2" style="opacity:0">LE CENTRE,</div><div class="h2" id="u2" style="opacity:0">LA TÊTE</div>'
h = h.replace('<div id="foot">', deux + '<div id="foot">', 1)
h = h.replace(f'<span id="s1">Positions et trajectoires réelles · Données {SB}</span>', f'<span id="s1">Positions et trajectoires réelles · Données {SB}</span><span id="s2" style="position:absolute;left:0;top:0;white-space:nowrap;opacity:0">Menace : modèle MaliDataFoot (xT) · Chance de but : StatsBomb · Données {SB}</span>')
h = h.replace('<div id="src">', '<div id="src" style="position:absolute">', 1)
JSN = '''<script>
const A=__ANIM__, FIN=__FIN__;
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), lerp=(a,b,u)=>a+(b-a)*u, io=u=>u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2, oc=u=>1-Math.pow(1-u,3);
const $=id=>document.getElementById(id), fx=(id,t,a,d=.45,dy=40)=>{const u=oc(cl((t-a)/d));const e=$(id);e.style.opacity=u;e.style.transform=`translateY(${(1-u)*dy}px)`;};
const fo=(id,t,a,d=.35)=>{const e=$(id);const u=cl((t-a)/d);e.style.opacity=Math.min(parseFloat(e.style.opacity||1),1-u);};
const VB0=[-6,-6,132,92], VB1=[78,8,46,64], Z0=FIN+1.3, Z1=Z0+1.4, C1=Z1+.2, C2=C1+.9;
window.seek=function(t){
  // la plongée : vue du dessus qui bascule en perspective
  const d=io(cl(t/1.6)), z=io(cl((t-Z0)/(Z1-Z0)));
  const rot=lerp(lerp(0,58,d),48,z), sc=lerp(1.45,1,d);
  $('rot').style.transform=`rotateX(${rot}deg) scale(${sc})`; $('cam').style.opacity=cl(t/.5);
  $('cam').style.top=lerp(560,470,z)+'px'; $('cam').style.height=lerp(820,700,z)+'px';
  $('pv').setAttribute('viewBox',VB0.map((v,i)=>lerp(v,VB1[i],z).toFixed(3)).join(' '));
  // l'action, geste par geste
  for(const a of A){const e=$(a[0]);const u=cl((t-a[2])/(a[3]-a[2]));
    if(a[1]=='ligne'){e.setAttribute('opacity',t>=a[2]?1:0);e.setAttribute('x2',lerp(a[4],a[6],io(u)));e.setAttribute('y2',lerp(a[5],a[7],io(u)));
      if(u>=1&&e.dataset.m)e.setAttribute('marker-end',e.dataset.m);else e.removeAttribute('marker-end');
      if(a[8]){const p=cl((t-C1)/.9);e.setAttribute('stroke-width',(.75+.55*Math.sin(Math.PI*p)).toFixed(3));}}
    else{e.setAttribute('opacity',oc(u));}}
  // textes du plan 1
  fx('k1',t,.35); fx('t1',t,.5); fx('u1',t,.7); fx('leg',t,1.9); fx('stat',t,FIN+.25); fx('s1',t,.9,.45,0);
  // passage au zoom
  for(const id of ['k1','t1','u1','leg','stat','s1'])fo(id,t,Z0);
  fx('k2',t,Z0+.45); fx('t2',t,Z0+.6); fx('u2',t,Z0+.8); fx('s2',t,Z0+.6,.45,0);
  fx('c1',t,C1); fx('c2',t,C2);
  $('v1').textContent='+'+(0.25*oc(cl((t-C1)/.8))).toFixed(2).replace('.',',');
  $('v2').textContent=Math.round(32*oc(cl((t-C2)/.8)));
};
Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{}))]).then(()=>{window.seek(0);window.READY=true});
</script>'''.replace('__ANIM__', json.dumps(ANIM)).replace('__FIN__', str(round(FIN_ACTION, 3)))
h = h.replace('<script>document.fonts.ready.then(()=>{window.READY=true})</script>', JSN)
open('_vx_nuit.html', 'w', encoding='utf-8').write(h)

# ---------------------------------------------------------------- page principale
SIX = ['hamari-traore_poste', 'lassine-sinayoko_poste', 'amadou-haidara_poste', 'kamory-doumbia_poste', 'mamadou-sangare-2002_FICTIF', 'nene-dorgeles-2002_FICTIF']
TUILES = sorted(f for f in os.listdir(FICHES) if f.startswith('tile_'))
for f in SIX: assert os.path.exists(os.path.join(FICHES, f'full_{f}.png')), f
os.makedirs('_vx', exist_ok=True)
for f in os.listdir(FICHES):
    if f.startswith(('full_', 'tile_')):
        src, dst = os.path.join(FICHES, f), os.path.join('_vx', f)
        if not os.path.exists(dst): os.symlink(src, dst)
T_FICHE, PAS = round(FIN_ACTION + 1.3 + 1.4 + .2 + .9 + 2.2, 2), 1.25           # entrée de la 1re fiche, intervalle entre deux fiches
T_MUR = T_FICHE + PAS * 5 + 1.0     # la dernière fiche devient une case du mur
T_FIN = T_MUR + 3.6; DUREE = T_FIN + 3.0
# le mur : grille de cases (cartes de fiche 1080 x 1460), la case centrale = la dernière fiche
COLS, ROWS, GX, GY = 23, 19, 1180, 1580
rc, cc0 = ROWS // 2, COLS // 2
rnd = random.Random(7); CASES = []
for r in range(ROWS):
    for c in range(COLS):
        f = 'tile_nene-dorgeles-2002_FICTIF.jpg' if (r, c) == (rc, cc0) else TUILES[rnd.randrange(len(TUILES))]
        CASES.append([r, c, TUILES.index(f)])
imgs = ''.join(f'<img id="ti{i}" src="_vx/{f}" style="display:none">' for i, f in enumerate(TUILES)) + '<img id="tigrand" src="_vx/full_nene-dorgeles-2002_FICTIF.png" style="display:none">'
fiches = ''.join(f'<img class="fi" id="f{i}" src="_vx/full_{f}.png">' for i, f in enumerate(SIX))
logo_fin = '''<div id="fin"><img src="logo-verte.png" id="lg"><div id="wm">Mali<i>Data</i>Foot</div>
<div id="so"><img src="logo_x.png" style="height:40px"><img src="logo_tt.png" style="height:52px"><span>@MaliDataFoot</span></div></div>'''
main = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:"BCS";font-style:italic;font-weight:400;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-400-italic.woff2)}}
@font-face{{font-family:"BCS";font-style:italic;font-weight:600;src:url(node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-600-italic.woff2)}}
@font-face{{font-family:"IN";font-weight:700;src:url(node_modules/@fontsource/inter/files/inter-latin-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#F6C41C}}
#c{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#F6C41C}}
#nuit{{position:absolute;left:0;top:0;width:1080px;height:1920px;border:0;z-index:5}}
.fi{{position:absolute;left:0;top:0;width:1080px;height:1920px;display:block;z-index:4}}
#mur{{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:3}}
#voile{{position:absolute;left:0;top:0;width:1080px;height:1920px;background:linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%);z-index:6;opacity:0}}
#fin{{position:absolute;left:0;right:0;top:700px;z-index:7;text-align:center;color:#064A25;opacity:0}}
#lg{{width:190px;height:190px;border-radius:50%;display:block;margin:0 auto}}
#wm{{font:italic 400 128px/1 "BCS";margin-top:34px}}#wm i{{font-weight:600}}
#so{{display:flex;justify-content:center;align-items:center;gap:20px;margin-top:34px;font:700 40px/1 "IN"}}
</style></head><body><div id="c">
<iframe id="nuit" src="_vx_nuit.html"></iframe>{fiches}
<canvas id="mur" width="1080" height="1920"></canvas>{imgs}<div id="voile"></div>{logo_fin}
</div><script>
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), lerp=(a,b,u)=>a+(b-a)*u, io=u=>u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2, oc=u=>1-Math.pow(1-u,3);
const $=id=>document.getElementById(id); window.DUREE={DUREE:.2f};
const TF={T_FICHE}, PAS={PAS}, TM={T_MUR:.3f}, TFIN={T_FIN:.3f}, N={len(SIX)}, GX={GX}, GY={GY}, RC={rc}, CC={cc0};
const CASES={json.dumps(CASES)}, D=2400;
function mur(m){{   // le mur dessiné sur un canevas : vraie perspective approchée case par case
  const cv=$('mur'), x=cv.getContext('2d'); x.clearRect(0,0,1080,1920); if(m<0) return;
  const S=lerp(1,.11,m), rx=lerp(0,28,m)*Math.PI/180, rz=lerp(0,-14,m)*Math.PI/180, yc=lerp(850,960,m), co=Math.cos(rx);
  const L=[];
  for(const [r,c,k] of CASES){{const X=(c-CC)*GX, Y=(r-RC)*GY; const Xr=X*Math.cos(rz)-Y*Math.sin(rz), Yr=X*Math.sin(rz)+Y*Math.cos(rz);
    const Xs=Xr*S, Ys=Yr*S, z=-Ys*Math.sin(rx), f=D/(D+z); const sx=540+Xs*f, sy=yc+Ys*co*f, k2=S*f;
    if(sx<-700*k2||sx>1080+700*k2||sy<-800*k2||sy>1920+800*k2) continue; L.push([z,sx,sy,k2,k,r==RC&&c==CC]);}}
  L.sort((a,b)=>b[0]-a[0]);
  for(const [z,sx,sy,k2,k,centre] of L){{x.save(); x.translate(sx,sy); x.rotate(rz); x.scale(k2,k2*co);
    if(centre&&k2>.4) x.drawImage($('tigrand'),0,120,1080,1460,-540,-730,1080,1460); else x.drawImage($('ti'+k),-540,-730,1080,1460);
    x.restore();}}
}}
window.seek=function(t){{
  const nu=$('nuit').contentWindow; if(nu.seek) nu.seek(Math.min(t,TF+.6));
  // glissement vers le haut, comme un fil TikTok : la nuit part, les fiches arrivent une par une
  const s0=io(cl((t-TF)/.55)); $('nuit').style.transform=`translateY(${{-1920*s0}}px)`; $('nuit').style.display=s0>=1?'none':'block';
  for(let i=0;i<N;i++){{const e=$('f'+i);const a=TF+i*PAS;const u=io(cl((t-a)/.55));const v=i<N-1?io(cl((t-a-PAS)/.55)):0;
    e.style.transform=`translateY(${{1920*(1-u)-1920*v}}px)`; e.style.display=(u>0&&v<1&&t<TM+.05)?'block':'none';}}
  // le dézoom : la dernière fiche devient une case du mur, qui recule et se penche
  const m=io(cl((t-TM)/3.2)); mur(t>=TM?m:-1);
  // la fin : la signature
  const f=oc(cl((t-TFIN)/.6)); $('voile').style.opacity=f*.94; $('fin').style.opacity=oc(cl((t-TFIN-.25)/.5));
  $('fin').style.transform=`translateY(${{(1-oc(cl((t-TFIN-.25)/.5)))*40}}px)`;
}};
const nf=$('nuit'); nf.onload=()=>{{const k=setInterval(()=>{{if(nf.contentWindow.READY){{clearInterval(k);
 Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.seek(0);window.READY=true}});}}}},50)}};
</script></body></html>'''
open('_vx_main.html', 'w', encoding='utf-8').write(main)
print('ok', round(DUREE, 2), 's ; action', round(T0, 2), '->', round(FIN_ACTION, 2), '; fiches', T_FICHE, '; mur', round(T_MUR, 2), '; fin', round(T_FIN, 2))

"""Vidéo de lancement : transforme les pages fixes de la nouvelle DA (fiche joueur, duel) en scènes animées.
Chaque scène est une page autonome avec sa propre ligne de temps en pause et une fonction seek(t) en secondes locales.
Les pages fixes viennent de variantes.py (fiche, cadre blanc, vertical) et de duel_v2.py (duel, nuit, vertical) :
la vidéo montre donc exactement les mêmes chiffres que les images publiées."""
import re, subprocess, sys
GSAP='<script src="node_modules/gsap/dist/gsap.min.js"></script>'
FICHE='''
const $=s=>document.querySelector(s), S=gsap.set, tl=gsap.timeline({paused:true,defaults:{ease:'power3.out'}});
S('#top',{opacity:0,y:-18}); tl.to('#top',{opacity:1,y:0,duration:.45},.15);
S('.phh',{scale:.5,opacity:0}); tl.to('.phh',{scale:1,opacity:1,duration:.55,ease:'back.out(1.5)'},.3);
S(['#nm','#m1','#m2'],{opacity:0,x:-30}); tl.to(['#nm','#m1','#m2'],{opacity:1,x:0,duration:.5,stagger:.08},.42);
S('#sc',{opacity:0}); tl.to('#sc',{opacity:1,duration:.3},.6);
{const nb=$('#sc b'), cible=+nb.textContent, o={v:0}; nb.textContent='0'; tl.to(o,{v:cible,duration:.9,ease:'power2.out',onUpdate:()=>{nb.textContent=Math.round(o.v)}},.6);}
S('#p',{opacity:0,y:70}); tl.to('#p',{opacity:1,y:0,duration:.6},.75);
S('#rad .rl',{opacity:0}); tl.to('#rad .rl',{opacity:1,duration:.3,stagger:.03},1.15);
{const pg=$('#rad polygon'), c=$('#rad circle'); S(pg,{scale:0,svgOrigin:c.getAttribute('cx')+' '+c.getAttribute('cy')}); tl.to(pg,{scale:1,duration:.8,ease:'back.out(1.3)'},1.3);}
S('#rad .pt',{opacity:0}); tl.to('#rad .pt',{opacity:1,duration:.25,stagger:.03},1.75);
S(['#cap','#tb .th','#tb .fam'],{opacity:0}); tl.to(['#cap','#tb .th','#tb .fam'],{opacity:1,duration:.35},1.85);
S('#tb .r',{opacity:0,x:-14}); tl.to('#tb .r',{opacity:1,x:0,duration:.35,stagger:.06},1.95);
S('#tb .b i',{scaleX:0,transformOrigin:'0 50%'}); tl.to('#tb .b i',{scaleX:1,duration:.5,stagger:.06},2.05);
S(['#sep','#bt > div'],{opacity:0,y:12}); tl.to('#sep',{opacity:1,y:0,duration:.3},2.85).to('#bt > div',{opacity:1,y:0,duration:.4,stagger:.12},2.95);
S('#bt .b i',{scaleX:0,transformOrigin:'0 50%'}); tl.to('#bt .b i',{scaleX:1,duration:.45,stagger:.05},3.05);
S('#note',{opacity:0}); tl.to('#note',{opacity:1,duration:.4},3.35);
'''
DUEL='''
const $=s=>document.querySelector(s), S=gsap.set, tl=gsap.timeline({paused:true,defaults:{ease:'power3.out'}});
S('#top',{opacity:0,y:-18}); tl.to('#top',{opacity:1,y:0,duration:.45},.15);
S('.side.a',{opacity:0,x:-70}); S('.side.b',{opacity:0,x:70}); tl.to(['.side.a','.side.b'],{opacity:1,x:0,duration:.55},.3);
S('#sco',{opacity:0}); tl.to('#sco',{opacity:1,duration:.3},.6);
document.querySelectorAll('#sco b').forEach((nb,i)=>{const cible=+nb.textContent, o={v:0}; nb.textContent='0'; tl.to(o,{v:cible,duration:.9,ease:'power2.out',onUpdate:()=>{nb.textContent=Math.round(o.v)}},.65+i*.12)});
[['#b1',1.0],['#b2',1.85]].forEach(([b,t])=>{
  S(b+' .bh',{opacity:0}); tl.to(b+' .bh',{opacity:1,duration:.35},t);
  S(b+' .r',{opacity:0}); tl.to(b+' .r',{opacity:1,duration:.25,stagger:.05},t+.15);
  S(b+' .r .lb',{y:8}); tl.to(b+' .r .lb',{y:0,duration:.3,stagger:.05},t+.15);
  S(b+' .r .ta i',{scaleX:0,transformOrigin:'100% 50%'}); S(b+' .r .tb i',{scaleX:0,transformOrigin:'0 50%'});
  tl.to(b+' .r .ta i',{scaleX:1,duration:.5,stagger:.05},t+.3).to(b+' .r .tb i',{scaleX:1,duration:.5,stagger:.05},t+.35);
  S([b+' .r .va',b+' .r .vb'],{opacity:0}); tl.to(b+' .r .va',{opacity:1,duration:.25,stagger:.05},t+.5).to(b+' .r .vb',{opacity:1,duration:.25,stagger:.05},t+.55);});
S('#syn',{opacity:0,y:10}); tl.to('#syn',{opacity:1,y:0,duration:.4},2.85);
S('#note',{opacity:0}); tl.to('#note',{opacity:1,duration:.4},3.1);
'''
FIT="document.querySelectorAll('#nm').forEach(e=>{let s=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth+1&&s>40){s-=2;e.style.fontSize=s+'px'}});"
FIN="window.tl=tl; window.seek=t=>{tl.time(Math.max(0,Math.min(t,tl.duration())),false)}; tl.time(0);\nPromise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{}))]).then(()=>{"+FIT+"window.READY=true});"
def animer(src, dst, code):
    h=open(src,encoding='utf-8').read()
    h,n=re.subn(r'<script>Promise\.all.*?</script>','',h,flags=re.S); assert n==1, (src,n)
    h=h.replace('</body>',f'{GSAP}<script>{code}{FIN}</script></body>'); assert GSAP in h
    open(dst,'w',encoding='utf-8').write(h); print('ok',dst)
run=lambda *a:subprocess.run([sys.executable,*a],check=True,stdout=subprocess.DEVNULL)
run('variantes.py','fiche','A','fiche_tt2.html','tiktok')
run('duel_v2.py','../outputs/duel_v2.json','duel_tt2.html','tiktok')
animer('fiche_tt2.html','fiche_anim.html',FICHE)
animer('duel_tt2.html','duel_anim.html',DUEL)

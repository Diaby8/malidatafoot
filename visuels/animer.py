"""Motion design des POC : anime des plans statiques (pages HTML de la DA) et prépare la page à capturer.

Usage : python animer.py sortie.html plan1.html:7 plan2.html:8 ...   (durée de chaque plan en secondes)
Chaque plan est chargé dans un calque (iframe). À son début, ses éléments entrent dans l'ordre de la page :
ligne d'info, titre (glisse vers le haut), deuxième ligne, puis le contenu (fondu + montée), les barres poussent depuis
la gauche, les rectangles d'histogramme depuis le bas, les courbes se tracent, les points et ronds grossissent.
Entre deux plans : un volet jaune de la DA. Pas d'effet de grain, d'ombre ni de lueur.
window.seek(t) place toute la vidéo à l'instant t (secondes) ; window.DUREE donne la durée totale ; window.READY quand tout est chargé.
"""
import json, sys

PAGE = r'''<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0;padding:0}html,body{width:1080px;height:1920px;overflow:hidden;background:#F6C41C}
.cal{position:absolute;left:0;top:0;width:1080px;height:1920px;border:0;visibility:hidden}
#volet{position:absolute;left:0;top:0;width:1080px;height:1920px;background:linear-gradient(180deg,#FBD134,#EFA40A);transform:translateX(-100%)}
#volet i{position:absolute;right:0;top:0;width:28px;height:100%;background:#0B7A3B}</style></head><body>
__CALQUES__<div id="volet"><i></i></div>
<script>
const PLANS=__PLANS__; const T=0.45; // durée du volet
let debut=[],acc=0; PLANS.forEach(p=>{debut.push(acc);acc+=p.d}); window.DUREE=acc;
const cals=[...document.querySelectorAll('.cal')]; const anims=[];
function docFinal(d){const f=d.querySelector('iframe#f'); return f?docFinal(f.contentDocument):d}
function ajoute(el,kf,opt,base){const a=el.animate(kf,Object.assign({fill:'both',easing:'cubic-bezier(.2,.8,.2,1)'},opt));a.pause();anims.push([a,base]);}
function prepare(i){
  const d=docFinal(cals[i].contentDocument), c=d.getElementById('c'); if(!c) return; const b=debut[i]*1000; let k=0;
  const ent=(el,dl,kf)=>ajoute(el,kf||[{opacity:0,transform:'translateY(36px)'},{opacity:1,transform:'none'}],{duration:600,delay:dl},b);
  ['.kick','.h1','.h2','.ghost'].forEach((s,j)=>{const el=c.querySelector(s); if(el) ent(el,150+j*170, s=='.ghost'?[{opacity:0},{opacity:getComputedStyle(el).opacity}]:null)});
  let dl=750;
  [...c.children].forEach(el=>{
    if(el.matches('.kick,.h1,.h2,.ghost,#foot,#src')) return;
    if(el.tagName=='svg' && el===c.firstElementChild) return; // la trame
    if(el.tagName=='svg'){ // graphiques
      [...el.querySelectorAll('path,line,rect,circle,text,polygon')].forEach(s=>{
        const cs=getComputedStyle(s);
        if(s.tagName=='path' && cs.fill=='none'){const L=s.getTotalLength(); s.style.strokeDasharray=L+' '+L; ajoute(s,[{strokeDashoffset:L},{strokeDashoffset:0}],{duration:1600,delay:dl,easing:'ease-in-out'},b);}
        else if(s.tagName=='rect'){s.style.transformBox='fill-box';s.style.transformOrigin='50% 100%'; ajoute(s,[{transform:'scaleY(0)'},{transform:'scaleY(1)'}],{duration:700,delay:dl+(k++)*45},b);}
        else if(s.tagName=='circle'){s.style.transformBox='fill-box';s.style.transformOrigin='50% 50%'; ajoute(s,[{transform:'scale(0)'},{transform:'scale(1)'}],{duration:450,delay:dl+(k++)*30},b);}
        else ajoute(s,[{opacity:0},{opacity:1}],{duration:500,delay:dl+400},b);
      }); dl+=500; return;}
    const bg=getComputedStyle(el).backgroundColor, w=el.getBoundingClientRect().width, h=el.getBoundingClientRect().height;
    if(bg!='rgba(0, 0, 0, 0)' && h<=110 && w>40 && !el.children.length){el.style.transformOrigin='0 50%'; ajoute(el,[{transform:'scaleX(0)'},{transform:'scaleX(1)'}],{duration:800,delay:dl},b); dl+=90; return;}
    ent(el,dl); dl+=180;
  });
  [c.querySelector('#foot'),c.querySelector('#src')].forEach(el=>{if(el) ent(el,300)});
}
window.seek=function(t){
  const ms=t*1000; let i=debut.findIndex((d,j)=>t>=d && t<d+PLANS[j].d); if(i<0) i=PLANS.length-1;
  cals.forEach((c,j)=>c.style.visibility=(j==i)?'visible':'hidden');
  anims.forEach(([a,b])=>{a.currentTime=Math.max(0,ms-b)});
  // volet : traverse l'écran autour de chaque changement de plan
  const v=document.getElementById('volet'); let x=-100;
  debut.slice(1).forEach(d=>{const u=(t-(d-T/2))/T; if(u>=0&&u<=1) x=-100+200*u});
  v.style.transform='translateX('+x+'%)';
};
let n=0; cals.forEach((c,i)=>{const go=()=>{const tick=setInterval(()=>{let d=c.contentDocument; while(d&&d.querySelector('iframe#f')){d=d.querySelector('iframe#f').contentDocument}
  const w=d&&d.defaultView; if(w&&w.READY){clearInterval(tick);prepare(i);if(++n==cals.length){window.seek(0);window.READY=true}}},40)}; c.onload=go;});
</script></body></html>'''

def construire(sortie, plans):
    calques = ''.join(f'<iframe class="cal" src="{p}"></iframe>' for p, _ in plans)
    html = PAGE.replace('__CALQUES__', calques).replace('__PLANS__', json.dumps([{'src': p, 'd': d} for p, d in plans]))
    open(sortie, 'w', encoding='utf-8').write(html)

if __name__ == '__main__':
    construire(sys.argv[1], [(a.rsplit(':', 1)[0], float(a.rsplit(':', 1)[1])) for a in sys.argv[2:]])

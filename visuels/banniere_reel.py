"""Bannières X 1500 x 500 dans la NOUVELLE DA (celle de la grille des variantes : signature, titres penchés, cadre blanc, nuit, Inter).
Les cartes sont les vrais gabarits allégés (reel_cartes.py -> reel/<plan><thème>.png), l'accroche et la signature reprennent
exactement les plans « accroche » et « fin » de variantes.py. Aucun nom de joueur.
usage : python3 banniere_reel.py <1..16> <sortie.html>"""
import math, sys
from da import BASE_CSS
K,OUT=int(sys.argv[1]),sys.argv[2]; W,H=1500,500; OR,VERT,VERT_D,NUIT='#F6C41C','#0B7A3B','#064A25','#04331A'
RADIAL='radial-gradient(120% 90% at 30% 26%, #128F47 0%, #0B7A3B 30%, #064A25 62%, #04331A 100%)'
I800='@font-face{font-family:"IN";font-weight:800;src:url(node_modules/@fontsource/inter/files/inter-latin-800-normal.woff2)}'
def trame(coul,op):
    g=''; st=26; row=0; y=st/2
    while y<H:
        x=st/2+(st/2 if row%2 else 0)
        while x<W:
            dd=math.hypot(x-W,y)/1150; r=1.1+8.5*max(0,1-dd)**2.6; g+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>'; x+=st
        y+=st; row+=1
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><g fill="{coul}" fill-opacity="{op}">{g}</g></svg>'
def terrain(coul='#fff',op=.5):
    L=f'stroke="{coul}" stroke-opacity="{op}" stroke-width="3" fill="none"'
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><rect x="-40" y="-60" width="{W+80}" height="{H+120}" {L}/><line x1="{W/2}" y1="-60" x2="{W/2}" y2="{H+60}" {L}/><circle cx="{W/2}" cy="{H/2}" r="120" {L}/>'
            f'<rect x="-40" y="{H/2-235}" width="250" height="470" {L}/><rect x="-40" y="{H/2-105}" width="95" height="210" {L}/><path d="M210 {H/2-88}A120 120 0 0 1 210 {H/2+88}" {L}/>'
            f'<rect x="{W-210}" y="{H/2-235}" width="250" height="470" {L}/><rect x="{W-55}" y="{H/2-105}" width="95" height="210" {L}/><path d="M{W-210} {H/2-88}A120 120 0 0 0 {W-210} {H/2+88}" {L}/></svg>')
def cartes(L,style='penche'):
    """L : (nom, x, y, largeur, angle). penche : liseré blanc et ombre, comme la bannière « nouvelle DA » ; droit : sans liseré, ombre douce de la DA."""
    cs='border-radius:8px;box-shadow:0 0 0 4px #fff,0 14px 26px rgba(60,40,0,.3)' if style=='penche' else 'border-radius:12px'
    return ''.join(f'<img src="reel/{n}.png" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w*760/1080:.0f}px;transform:rotate({r}deg);{cs}">' for n,x,y,w,r in L)
def accroche(c1,c2,x=432,y=100,t1=50,t2=138):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;font:800 {t1}px/1.12 \'IN\';letter-spacing:-.03em;color:{c1};white-space:nowrap">Les Aigles jouent.</div>'
            f'<div style="position:absolute;left:{x-3}px;top:{y+t1*1.12+12:.0f}px;font:italic 900 {t2}px/.9 \'BC\';text-transform:uppercase;color:{c2};white-space:nowrap">La data<br>parle.</div>')
def signature(coul,x,y,t=150,sous=None,c2=None):
    s=f'<div style="position:absolute;left:{x}px;top:{y}px;font:italic 400 {t}px/1 \'BCS\';color:{coul};white-space:nowrap">Mali<i style="font-weight:600">Data</i>Foot</div>'
    if sous: s+=f'<div style="position:absolute;left:{x+6}px;top:{y+t*1.06:.0f}px;font:500 {t*.24:.0f}px/1 \'IN\';color:{c2};white-space:nowrap">{sous}</div>'
    return s
RANG4=lambda a,b,c,d:[(a,57,62,318,-2.2),(b,413,48,318,1.6),(c,769,64,318,-1.4),(d,1125,50,318,2.4)]
DROIT4=lambda a,b,c,d:[(n,60+i*350,44,330,0) for i,n in enumerate((a,b,c,d))]
TROIS=lambda a,b,c:[(a,902,96,262,-3),(b,1062,170,262,1.5),(c,1214,88,262,3)]
if   K==1:  bg=OR;   corps=terrain()+cartes(RANG4('butA','ficheA','reseauB','filB'))
elif K==2:  bg=OR;   corps=trame('#FDEBA6',.85)+terrain()+cartes(RANG4('tirsA','filA','reseauB','ficheB'))
elif K==3:  bg=OR;   corps=trame('#FDEBA6',.85)+cartes(RANG4('tirsA','butB','filA','reseauB'))
elif K==4:  bg=OR;   corps=terrain()+cartes([(n,32+i*290,(60,86,54,84,62)[i],272,(-2,1.6,-1.4,2,-1.6)[i]) for i,n in enumerate(('tirsA','butB','ficheA','reseauB','filA'))])
elif K==5:  bg=OR;   corps=cartes(DROIT4('tirsA','butA','filA','reseauA'),'droit')
elif K==6:  bg=NUIT; corps=cartes(DROIT4('tirsB','butB','filB','reseauB'),'droit')
elif K==7:  bg=OR;   corps=cartes(DROIT4('tirsA','reseauB','filA','ficheB'),'droit')
elif K==8:  bg=OR;   corps=accroche(VERT_D,VERT_D)+cartes(TROIS('tirsA','reseauB','filA'))
elif K==9:  bg=RADIAL; corps=accroche('#fff',OR)+cartes(TROIS('tirsA','reseauB','ficheA'))
elif K==10: bg=RADIAL; corps=trame('#19A552',.45)+accroche('#fff',OR,x=432,y=84,t1=64,t2=150)+signature('#fff',930,196,118,'La data du foot malien','#FFF6D0')
elif K==11: bg=RADIAL; corps=signature('#fff',452,130,170,'La data du foot malien','#FFF6D0')
elif K==12: bg=OR;   corps=signature(VERT_D,452,130,170,'La data du foot malien','rgba(14,26,19,.72)')
elif K==13: bg=OR;   corps=terrain()+cartes(RANG4('tirsA','butA','filA','reseauA'))
elif K==14: bg=NUIT; corps=terrain(VERT,.7)+cartes(RANG4('tirsB','ficheB','reseauB','filB'))
elif K==15: bg=OR;   corps=accroche(VERT_D,VERT_D,x=432,y=84,t1=64,t2=150)+signature(VERT_D,930,196,118,'La data du foot malien','rgba(14,26,19,.72)')
else:       bg=RADIAL; corps=trame('#19A552',.45)+accroche('#fff',OR)+cartes(TROIS('butA','reseauB','filA'))
open(OUT,'w',encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}{I800}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}#b{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}svg{{display:block}}img{{display:block}}
</style></head><body><div id="b">{corps}</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
print('ok',K,OUT)

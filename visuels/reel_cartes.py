"""Cartes de bannière tirées des VRAIS gabarits de la nouvelle DA (variantes.py), en plus léger :
on garde le titre penché, le cadre blanc, l'intertitre et le graphique ; on masque les sous-titres, le grand chiffre,
les tableaux, les notes et les noms posés sur les graphiques. Rien n'est redessiné.
usage : python3 reel_cartes.py   ->  reel/<plan><thème>.png (1080 x 760)"""
import subprocess, sys
from PIL import Image
HAUT=760
LEGER='''#top,#note,#m1,#m2,#sc{visibility:hidden!important}#bt,#tb,#ls,#cx,#leg,.cap{display:none!important}
#hero{top:36px!important}#p{top:132px!important;height:596px!important;overflow:hidden!important;box-shadow:none!important}#in.nu{top:132px!important;height:596px!important;overflow:hidden!important}#in svg text{display:none!important}'''
FICHE='''#top,#note,#hero{visibility:hidden!important}#p{top:28px!important;height:700px!important;overflow:hidden!important;box-shadow:none!important}#in.nu{top:28px!important;height:700px!important;overflow:hidden!important}'''
LOT=[('tirs','A',LEGER),('tirs','B',LEGER),('but','A',LEGER),('but','B',LEGER),('fil','A',LEGER),('fil','B',LEGER),
     ('reseau','A',LEGER),('reseau','B',LEGER),('fiche','A',FICHE),('fiche','B',FICHE)]
for plan,th,css in LOT:
    f=f'reel_{plan}{th}.html'; subprocess.run([sys.executable,'variantes.py',plan,th,f],check=True,capture_output=True)
    s=open(f,encoding='utf-8').read(); s=s.replace('</head>',f'<style>{css}</style></head>',1); open(f,'w',encoding='utf-8').write(s)
    subprocess.run(['node','shotu.mjs',f,f'reel/_{plan}{th}.png','1080','1350','1'],check=True)
    Image.open(f'reel/_{plan}{th}.png').convert('RGB').crop((0,0,1080,HAUT)).save(f'reel/{plan}{th}.png'); print('ok',plan,th)

"""Cartes de bannière tirées des vrais gabarits « histoire des Aigles » (variantes.py : histoire, scores, decennies,
competitions), en A (cadre blanc) et B (nuit) : on garde le titre penché et le graphique, on coupe le cadre juste sous
le graphique (les tableaux, la signature, le grand chiffre et les notes ne viennent pas). Rien n'est redessiné.
usage : python3 reel_histoire.py  ->  reel/<plan><thème>.png (1080 de large)"""
import subprocess, sys
from PIL import Image
# hauteur du cadre gardée, en px, pour que la coupe tombe sous le graphique
HAUT = {'histoire': (474, 444), 'scores': (600, 600), 'decennies': (462, 462), 'competitions': (552, 552)}   # (cadre blanc, nuit)
CAPTURE = sys.argv[1] if len(sys.argv) > 1 else 'shotu.mjs'
for plan, hh in HAUT.items():
    for th in 'AB':
        h = hh[0] if th == 'A' else hh[1]
        css = (f'#top,#note,#m1,#m2,#sc{{visibility:hidden!important}}#hero{{top:36px!important}}'
               f'#p{{top:132px!important;height:{h}px!important;overflow:hidden!important;box-shadow:none!important}}'
               f'#in.nu{{top:132px!important;height:{h}px!important;overflow:hidden!important}}')
        f = f'reel_{plan}{th}.html'; subprocess.run([sys.executable, 'variantes.py', plan, th, f], check=True, capture_output=True)
        s = open(f, encoding='utf-8').read().replace('</head>', f'<style>{css}</style></head>', 1); open(f, 'w', encoding='utf-8').write(s)
        subprocess.run(['node', CAPTURE, f, f'reel/_{plan}{th}.png', '1080', '1350', '1'], check=True)
        bas = 132 + h + (32 if th == 'A' else 14)
        Image.open(f'reel/_{plan}{th}.png').convert('RGB').crop((0, 0, 1080, bas)).save(f'reel/{plan}{th}.png'); print('ok', plan, th, bas)

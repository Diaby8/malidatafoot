"""Carte « son tournoi en dix critères » pour la bannière : le vrai gabarit fiche (variantes.py), sans l'en-tête (nom, photo),
sans le titre « Son tournoi… » (sans nom, le « son » ne renvoie à personne), coupé juste sous le tableau pour ne garder ni la note du radar ni « Performances proches » (où figure un nom).
usage : python3 reel_radar.py  ->  reel/radarA.png, reel/radarB.png (1080 x HAUT)"""
import subprocess, sys
from PIL import Image
DECOUPE = {'A': (596, 656), 'B': (596, 607)}   # hauteur du cadre, hauteur de la carte
def css(PANEL): return f'''#top,#note,#hero{{visibility:hidden!important}}#p{{top:28px!important;height:{PANEL}px!important;overflow:hidden!important;box-shadow:none!important}}#in.nu{{top:28px!important;height:{PANEL}px!important;overflow:hidden!important}}.hd h3{{visibility:hidden!important}}'''
for th in 'AB':
    PANEL, HAUT = DECOUPE[th]
    f = f'reel_radar{th}.html'; subprocess.run([sys.executable, 'variantes.py', 'fiche', th, f], check=True, capture_output=True)
    s = open(f, encoding='utf-8').read().replace('</head>', f'<style>{css(PANEL)}</style></head>', 1); open(f, 'w', encoding='utf-8').write(s)
    subprocess.run(['node', 'shotu.mjs', f, f'reel/_radar{th}.png', '1080', '1350', '1'], check=True)
    Image.open(f'reel/_radar{th}.png').convert('RGB').crop((0, 0, 1080, HAUT)).save(f'reel/radar{th}.png'); print('ok', th)

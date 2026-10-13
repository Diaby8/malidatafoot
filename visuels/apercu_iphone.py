"""Aperçu « iPhone » mesuré sur la capture d'écran de Diaby du 13 octobre 2026 (profil X, appli iOS) :
l'appli agrandit la bannière (0,875 px d'écran par px de bannière sur une capture de 923 px de large) et n'en montre que
x 338 à 1393 et y 79 à 500 ; l'heure et le réseau passent par-dessus le haut (jusqu'à y = 205 environ), les boutons
retour et recherche sont à mi-hauteur (centres (434, 313) et (1294, 313), rayon 54), et la photo de profil couvre x 360 à 575
à partir de y = 455. usage : python3 apercu_iphone.py <banniere.png> <sortie.png> [zones]"""
import sys
from PIL import Image, ImageDraw
X0, Y0, X1, Y1 = 338, 79, 1393, 500
b = Image.open(sys.argv[1]).convert('RGB').resize((1500, 500), Image.LANCZOS).crop((X0, Y0, X1, Y1))
k = 923 / (X1 - X0); b = b.resize((923, round((Y1 - Y0) * k)), Image.LANCZOS)
can = Image.new('RGB', (923, 640), '#FFFFFF'); can.paste(b, (0, 0)); d = ImageDraw.Draw(can, 'RGBA')
e = lambda x, y: ((x - X0) * k, (y - Y0) * k)
for cx in (434, 1294):
    x, y = e(cx, 313); r = 54 * k; d.ellipse((x - r, y - r, x + r, y + r), fill=(60, 50, 0, 150))
d.text((95, 55), '17:24', fill='white'); d.text((720, 55), '5G  35', fill='white')
logo = Image.open('logo-verte.png').convert('RGBA').resize((180, 180), Image.LANCZOS)
m = Image.new('L', (180, 180), 0); ImageDraw.Draw(m).ellipse((0, 0, 179, 179), fill=255)
d.ellipse((20, 332, 208, 520), fill='#FFFFFF'); can.paste(logo, (24, 336), m)
if len(sys.argv) > 3:   # zone sûre : visible sur ordinateur ET sur l'iPhone, hors boutons, heure et photo
    x, y = e(560, 210); x2, y2 = e(1230, 448); d.rectangle((x, y, x2, y2), outline=(212, 37, 42, 255), width=3)
can.save(sys.argv[2])

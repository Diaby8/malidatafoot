"""Aperçu téléphone : bannière à 390 px de large (largeur d'un écran), avec les boutons que X pose en haut
(retour à gauche, recherche et menu à droite) et la photo de profil, pour juger de l'effet à taille réelle."""
import sys
from PIL import Image, ImageDraw
b = Image.open(sys.argv[1]).convert('RGB').resize((780, 260), Image.LANCZOS)   # 390 px x 2 (écran retina)
can = Image.new('RGB', (780, 360), '#FFFFFF'); can.paste(b, (0, 0)); d = ImageDraw.Draw(can, 'RGBA')
for cx in (52, 640, 724): d.ellipse((cx-30, 22, cx+30, 82), fill=(0, 0, 0, 140))
logo = Image.open('logo-verte.png').convert('RGBA').resize((150, 150), Image.LANCZOS)
m = Image.new('L', (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
d.ellipse((28, 180, 192, 344), fill='#FFFFFF'); can.paste(logo, (35, 187), m)
can.save(sys.argv[2])

"""Aperçu « profil X » : la bannière avec la photo de profil posée par-dessus (rond centré en (217, 465), rayon 178, liseré),
pour vérifier que rien d'important n'est caché. usage : python3 apercu_profil.py <banniere.png> <sortie.png>"""
import sys
from PIL import Image, ImageDraw
b = Image.open(sys.argv[1]).convert('RGB').resize((1500, 500), Image.LANCZOS)
can = Image.new('RGB', (1500, 660), '#FFFFFF'); can.paste(b, (0, 0))
logo = Image.open('logo-verte.png').convert('RGBA').resize((340, 340), Image.LANCZOS)
m = Image.new('L', (340, 340), 0); ImageDraw.Draw(m).ellipse((0, 0, 339, 339), fill=255)
d = ImageDraw.Draw(can); d.ellipse((217-178, 465-178, 217+178, 465+178), fill='#FFFFFF')
can.paste(logo, (217-170, 465-170), m)
can.save(sys.argv[2])

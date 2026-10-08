"""Grille numérotée des variantes : une colonne par plan, une ligne par habillage (A cadre blanc, B nuit, C encre, D blanc).
Régénère les 32 pages avec les données du pipeline, les capture, range chaque case dans <sortie>/variantes/<n><L>-<plan>.png
et assemble la grille.   usage : python3 grille.py <dossier de sortie>"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
OUT=sys.argv[1]; os.makedirs(f'{OUT}/variantes',exist_ok=True)
PLANS=[('accroche',"L'accroche"),('tirs','La carte des tirs'),('but',"L'anatomie d'un but"),('fil','Le fil du match'),('reseau','Le réseau de passes'),('fiche','La fiche joueur'),('duel','Le duel'),('fin','La fin')]
VAR=[('A','Cadre blanc'),('B','Nuit'),('C','Encre'),('D','Blanc')]
jobs=[]
for n,(plan,_) in enumerate(PLANS,1):
    for L,_ in VAR:
        h=f'vr_{plan}_{L}.html'
        if plan=='duel':                      # quatre mises en scène différentes : radar, barres face à face, ronds reliés, barres d'écart
            J='../outputs/duel_v2.json'
            subprocess.run([sys.executable,'duel_v2.py',J,h,'x','B'] if L=='B' else [sys.executable,'duel_mises.py',J,h,L],check=True,stdout=subprocess.DEVNULL)
        else: subprocess.run([sys.executable,'variantes.py',plan,L,h],check=True,stdout=subprocess.DEVNULL)
        jobs.append(f'{h}:{OUT}/variantes/{n}{L}-{plan}.png')
subprocess.run(['node','shotmany.mjs','2',*jobs],check=True)
TW,TH,GX,GY,LEFT,TOP=480,600,14,50,200,96
from polices import police
B=police(30,True); S=police(22,True)
R=police(22); XL=police(64,True)
W=LEFT+len(PLANS)*TW+(len(PLANS)-1)*GX+30; H=TOP+len(VAR)*(TH+GY)+10
G=Image.new('RGB',(W,H),'#151915'); d=ImageDraw.Draw(G)
for i,(plan,nom) in enumerate(PLANS): d.text((LEFT+i*(TW+GX),24),f'{i+1}. {nom}',font=B,fill='#FFFFFF')
for j,(L,nom) in enumerate(VAR):
    y=TOP+j*(TH+GY)+GY-14
    d.text((36,y+30),L,font=XL,fill='#F6C41C'); d.text((36,y+112),nom,font=R,fill='#C9D1CB')
    for i,(plan,_) in enumerate(PLANS):
        x=LEFT+i*(TW+GX)
        d.text((x,y-30),f'{i+1}{L}',font=S,fill='#F6C41C')
        G.paste(Image.open(f'{OUT}/variantes/{i+1}{L}-{plan}.png').convert('RGB').resize((TW,TH),Image.LANCZOS),(x,y))
G.save(f'{OUT}/grille-variantes-par-plan.png'); print('ok',G.size)

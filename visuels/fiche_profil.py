"""Carte « profil » : même cadre que la fiche joueur (fiche_pro.py, format TikTok), pour un joueur sans données de match
(moins de 180 minutes à la CAN 2023 ou absent de StatsBomb). Tout vient du registre : âge, poste, club, sélections, buts.
Les stats viendront plus tard d'une autre source ; la carte le dit.
usage : python3 fiche_profil.py <joueur_id du registre> <sortie.html>"""
import csv, os, sys, datetime
JID, OUT = sys.argv[1], sys.argv[2]
AUJ = datetime.date(2026, 10, 14)
R = next(r for r in csv.DictReader(open('../registre/joueurs.csv', encoding='utf-8')) if r['joueur_id'] == JID)
assert R['club_a_confirmer'] != 'oui', 'club à confirmer : pas de carte'
n = datetime.date.fromisoformat(R['date_naissance'])
AGE = AUJ.year - n.year - ((AUJ.month, AUJ.day) < (n.month, n.day))
POSTE = {'G': 'Gardien', 'D': 'Défenseur', 'M': 'Milieu', 'A': 'Attaquant'}[R['poste']]
PH = f'photos/{JID}.png'
assert os.path.exists(PH), 'photo manquante'
f = 'node_modules/@fontsource/'
SOC = '<b><img src="logo_x.png" alt="X" style="height:22px"><img src="logo_tt.png" alt="TikTok" style="height:30px">@MaliDataFoot</b>'
tuile = lambda v, u, l: f'<div class="t"><b>{v}<small>{u}</small></b><span>{l}</span></div>'
html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face{{font-family:"BC";font-style:italic;font-weight:900;src:url({f}barlow-condensed/files/barlow-condensed-latin-900-italic.woff2)}}
@font-face{{font-family:"BCS";font-style:italic;font-weight:400;src:url({f}barlow-condensed/files/barlow-condensed-latin-400-italic.woff2)}}
@font-face{{font-family:"BCS";font-style:italic;font-weight:600;src:url({f}barlow-condensed/files/barlow-condensed-latin-600-italic.woff2)}}
@font-face{{font-family:"IN";font-weight:500;src:url({f}inter/files/inter-latin-500-normal.woff2)}}
@font-face{{font-family:"IN";font-weight:600;src:url({f}inter/files/inter-latin-600-normal.woff2)}}
@font-face{{font-family:"IN";font-weight:700;src:url({f}inter/files/inter-latin-700-normal.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1920px;overflow:hidden}}
#c{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#F6C41C;font-family:"IN",sans-serif;color:#0E1A13;font-variant-numeric:tabular-nums}}
#top{{position:absolute;left:56px;right:134px;top:150px;display:flex;justify-content:space-between;align-items:center}}
#brand{{display:flex;align-items:center;gap:15px;color:#064A25}}#brand img{{width:72px;height:72px;border-radius:50%;display:block}}
#brand b{{font:italic 400 47px/1 "BCS";white-space:nowrap}}#brand b i{{font-weight:600}}
#ctx{{font:600 21px/1 "IN";color:rgba(14,26,19,.72)}}
#hero{{position:absolute;left:56px;right:140px;top:250px;height:160px}}
.ph{{position:absolute;left:0;top:4px;width:150px;height:150px;border-radius:50%;overflow:hidden;background:#E9EDE8;box-shadow:0 0 0 5px #fff}}.ph img{{width:100%;height:100%;display:block;object-fit:cover}}
#nm{{position:absolute;left:178px;top:10px;font:italic 900 80px/1 "BC";color:#064A25;text-transform:uppercase;white-space:nowrap}}
#m1{{position:absolute;left:181px;top:100px;font:600 25px/1 "IN"}}#m1 .act{{font:500 18px/1 "IN";color:rgba(14,26,19,.62);margin-left:9px}}
#m2{{position:absolute;left:181px;top:134px;font:500 21px/1 "IN";color:rgba(14,26,19,.7)}}
#p{{position:absolute;left:56px;top:428px;width:890px;height:540px;background:#fff;border-radius:20px;box-shadow:0 16px 36px rgba(90,60,0,.2)}}
#p h3{{position:absolute;left:36px;top:28px;font:700 23px/1 "IN"}}
#g{{position:absolute;left:36px;right:36px;top:92px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 34px}}
.t{{padding:34px 0 30px;border-bottom:1.5px solid #E3E8E3}}
.t b{{display:block;font:italic 900 132px/.9 "BC";color:#064A25}}.t b small{{font:italic 900 56px/1 "BC";margin-left:10px}}
.t span{{display:block;margin-top:14px;font:600 22px/1.25 "IN";color:#5E6B62}}
#cl{{position:absolute;left:36px;right:36px;top:350px}}
#cl div{{display:flex;justify-content:space-between;align-items:baseline;padding:16px 0;border-bottom:1px solid #EEF1EE;font:500 22px/1.2 "IN"}}
#cl div b{{font-weight:700;text-align:right}}
#av{{position:absolute;left:36px;right:36px;bottom:34px;font:600 21px/1.35 "IN";color:#0B7A3B}}
#note{{position:absolute;left:56px;right:134px;top:984px;font:500 16.5px/1 "IN";color:rgba(14,26,19,.78)}}
#note div{{display:flex;justify-content:space-between;align-items:center;margin-top:7px;height:30px}}
#note b{{display:flex;align-items:center;gap:12px;font:700 22px/1 "IN";color:#064A25}}#note b img{{display:block}}
</style></head><body><div id="c">
<div id="top"><div id="brand"><img src="logo-verte.png" alt=""><b>Mali<i>Data</i>Foot</b></div><div id="ctx">Profil</div></div>
<div id="hero"><div class="ph"><img src="{PH}" alt=""></div><div id="nm">{R['nom']}</div>
 <div id="m1">{POSTE} · Mali · {R['club']}<span class="act">club actuel</span></div><div id="m2">Né le {n.day} {['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][n.month-1]} {n.year}</div></div>
<div id="p"><h3>Son profil en sélection</h3>
 <div id="g">{tuile(AGE,'ans','Âge')}{tuile(R['selections_au_2026_03_31'],'','Sélections avec le Mali')}{tuile(R['buts_au_2026_03_31'],'','Buts avec le Mali')}</div>
 <div id="cl"><div><span>Dernière convocation</span><b>{R['derniere_convocation']}</b></div></div>
 <div id="av">Sa fiche data (radar, centiles, profils proches) arrive avec ses matchs en club.</div>
</div>
<div id="note"><p>Sélections et buts au 31 mars 2026 · registre MaliDataFoot · photo {R['club']}, non libre.</p><div><span>Pas assez de minutes mesurées à la CAN 2023 pour une fiche data.</span>{SOC}</div></div>
</div><script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>'''
open(OUT, 'w', encoding='utf-8').write(html); print('ok', OUT, AGE, POSTE)

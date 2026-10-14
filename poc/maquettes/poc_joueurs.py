SH='/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
exec(open(SH + '/maq_a.py', encoding='utf-8').read().split('# 1 : le score')[0])
src_t = open(SH + '/maq_terrain.py', encoding='utf-8').read(); exec(src_t[src_t.index('def terrain'):src_t.index('# A : le terrain penche')])
out = {}
def ballon(lab, sina, x, y):
    c = '#0B7A3B' if sina else '#FFF3C4'
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:110px;text-align:center"><div style="width:96px;height:96px;margin:0 auto;border-radius:50%;background:{c};border:3px solid #064A25"></div><div style="font:800 22px/1.2 SC;margin-top:10px;color:{"#0B7A3B" if sina else "#04331A"}">{lab}</div></div>'
B23 = [("H. TRAORÉ<br>60'", 0), ("SINAYOKO<br>66'", 1), ("SINAYOKO<br>10'", 1), ("C.S.C.<br>3'", 0), ("SINAYOKO<br>47'", 1), ("DORGELES<br>71'", 0)]
B25 = [("SINAYOKO<br>61'", 1), ("SINAYOKO<br>64' (PEN.)", 1), ("SINAYOKO<br>90' (PEN.)", 1)]
b = '<div style="position:absolute;left:64px;top:600px;font:800 32px SC;letter-spacing:.05em">CAN 2023 · 6 BUTS DU MALI</div>'
b += ''.join(ballon(l, s, 64 + i * 140, 660) for i, (l, s) in enumerate(B23))
b += '<div style="position:absolute;left:64px;top:900px;font:800 32px SC;letter-spacing:.05em">CAN 2025 · 3 BUTS DU MALI</div>'
b += ''.join(ballon(l, s, 64 + i * 140, 960) for i, (l, s) in enumerate(B25))
b += '<div class="bigR" style="top:1250px"><b>6/9</b><span>BUTS DU MALI MARQUÉS PAR SINAYOKO<br>SUR LES DEUX DERNIÈRES CAN, <em>DONT LES 3 DE 2025</em></span></div>'
out['s1'] = pageT('CAN 2023 ET CAN 2025 · <b>QUI MARQUE POUR LE MALI ?</b>', 'TOUT PASSE', 'PAR SINAYOKO', '', b, 'Buteurs : martj42 (à recouper) · C.S.C. = contre son camp')
# S2 : part du meilleur buteur dans les buts de son équipe, CAN 2025
R = [('MALI · SINAYOKO', 3, 3, 1), ('ÉGYPTE · SALAH', 4, 9, 0), ('MAROC · BRAHIM DÍAZ', 5, 12, 0), ('RD CONGO · KAKUTA', 2, 5, 0)]
b = ''
for i, (n, x, t, m) in enumerate(R):
    y = 620 + i * 150
    b += f'<div style="position:absolute;left:64px;top:{y}px;font:800 30px SC;letter-spacing:.04em;color:{"#0B7A3B" if m else "#04331A"}">{n}</div>'
    b += f'<div style="position:absolute;left:64px;top:{y+46}px;width:700px;height:40px;border-radius:4px;background:#FFF3C4"></div><div style="position:absolute;left:64px;top:{y+46}px;width:{700*x/t:.0f}px;height:40px;border-radius:4px;background:{"#0B7A3B" if m else "#064A25"}"></div>'
    b += f'<div style="position:absolute;left:790px;top:{y+36}px;font:italic 900 56px/1 BC;color:#064A25">{x}/{t}</div>'
b += '<div class="bigR" style="top:1250px"><b>3</b><span>BUTS EN 5 MATCHS À LA CAN 2025 :<br>LE MALI <em>NE MARQUE PAS SANS LUI</em></span></div>'
out['s2'] = pageT('CAN 2025 · <b>PART DES BUTS DE L\'ÉQUIPE</b>', 'LE SEUL', 'BUTEUR ?', '', b, 'Buts du meilleur buteur / buts de son équipe · Données : martj42 (à recouper)')
def attente(top, h, txt): return f'<div style="position:absolute;left:64px;right:134px;top:{top}px;height:{h}px;border:4px dashed #064A25;border-radius:8px;display:flex;align-items:center;justify-content:center;text-align:center;font:800 30px/1.3 SC;letter-spacing:.05em;color:#064A25">{txt}</div>'
b = attente(600, 560, 'CARTE DE SES TIRS EN LIGUE 1 CETTE SAISON<br>TAILLE = CHANCE DE BUT<br><br>DONNÉES UNDERSTAT À VENIR')
b += '<div class="bigR" style="top:1250px"><b>? / ?</b><span>BUTS / BUTS ATTENDUS AVEC LE PARIS FC<br>TALENT OU RÉUSSITE : <em>À MESURER</em></span></div>'
out['s3'] = pageT('LIGUE 1 2026-2027 · <b>LASSINE SINAYOKO</b>', 'TALENT', 'OU RÉUSSITE ?', '', b, 'Maquette : les chiffres viendront d\'Understat')
def profil(nom1, nom2, lignes, attente_txt, kick, srcl):
    b = ''.join(f'<div style="position:absolute;left:64px;top:{600+i*64}px;font:800 34px SC;letter-spacing:.05em">{l}</div>' for i, l in enumerate(lignes))
    b += attente(620 + len(lignes) * 64, 560, attente_txt)
    return pageT(kick, nom1, nom2, '', b, srcl)
out['k1'] = profil('NOUHOUM', 'KAMISSOKO', ['21 ANS · MILIEU · OLYMPIQUE DE MARSEILLE', 'NÉ À BAMAKO · FORMÉ AUX ÉTOILES MANDÉ', '1er MATCH EN LIGUE 1 : 26 AVRIL 2026'],
                   'SES MINUTES ET SES ACTIONS<br>CETTE SAISON<br><br>DONNÉES UNDERSTAT À VENIR', 'LE VIVIER · <b>LES MALIENS EN CLUB</b>', 'Maquette · Biographie : Wikipédia (à recouper)')
out['g1'] = profil('MAMADOU', 'SANGARÉ', ['24 ANS · MILIEU · BRENTFORD', 'PREMIER LEAGUE · 14 SÉLECTIONS AVEC LE MALI'],
                   'CE QU\'IL APPORTE AU MILIEU<br>EN PREMIER LEAGUE<br><br>DONNÉES UNDERSTAT À VENIR', 'LE VIVIER · <b>LES MALIENS EN CLUB</b>', 'Maquette · Sélections au 31 mars 2026 (registre MaliDataFoot)')
for k, h in out.items(): open(f'_pj_{k}.html', 'w', encoding='utf-8').write(h)

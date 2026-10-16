"""Post 4 « Le onze type de Chelle et de Saintfiet » : brouillon de 2 images X (gabarit posts_video.py, DA jaune).
Titularisations : poc/onze_type/compos_relevees.csv (deux sources par match) + StatsBomb pour la CAN 2023.
Le système et les postes viennent des compos où on les connaît (voir docs/audits/post4-onze-type.md)."""
import csv, collections, re, duckdb
src=open('posts_video.py',encoding='utf-8').read(); exec(src.split('# ---------- post 1')[0])
R=list(csv.DictReader(open(ICI/'../poc/onze_type/compos_relevees.csv',encoding='utf-8')))
N={'Boubakar Kouyate':'Boubakar Kouyaté','Sikou Niakate':'Sikou Niakaté','Diadie Samassekou':'Diadié Samassékou','Sekou Koita':'Sékou Koïta','Nene Dorgeles':'Néné Dorgeles','Adama Traoré':'Adama Traoré','Youssoufou Niakaté':'Youssouf Niakaté'}
con=duckdb.connect(str(ICI/'../data/warehouse.duckdb'),read_only=True)
xi=con.execute("select match_id,player from silver.starting_xi where team='Mali'").fetchdf()
T=collections.defaultdict(collections.Counter); NB=collections.Counter()
for mid,g in xi.groupby('match_id'):
    NB['Chelle']+=1
    for p in g.player: T['Chelle'][N.get(p,p)]+=1
for r in R:
    if r['coach'] not in ('Chelle','Saintfiet'): continue
    NB[r['coach']]+=1
    for p in r['titulaires'].split(';'): T[r['coach']][re.sub(r' \((probable|Malouda)\)','',p)]+=1
# onze par poste (système le plus vu) : (nom affiché, clé, x, y) sur le terrain 0-100 (y = 0 en attaque)
ONZE={'Chelle':('4-4-2 LOSANGE',[('D. DIARRA','Djigui Diarra',50,86),('H. TRAORÉ','Hamari Traoré',88,62),('KOUYATÉ','Boubakar Kouyaté',66,67),('S. NIAKATÉ','Sikou Niakaté',34,67),('SACKO','Falaye Sacko',12,62),
   ('M. CAMARA','Mohamed Camara',50,52),('DIENG','Aliou Dieng',76,36),('A. HAÏDARA','Amadou Haïdara',24,36),('K. DOUMBIA','Kamory Doumbia',50,27),('A. TRAORÉ','Adama Traoré',66,10),('SINAYOKO','Lassine Sinayoko',34,10)]),
 'Saintfiet':('4-2-3-1',[('D. DIARRA','Djigui Diarra',50,86),('DOUCOURÉ','Fodé Doucouré',88,62),('FOFANA','Mamadou Fofana',66,67),('DIABY','Abdoulaye Diaby',34,67),('DANTÉ','Amadou Danté',12,62),
   ('DIENG','Aliou Dieng',67,47),('L. COULIBALY','Lassana Coulibaly',33,47),('K. DOUMBIA','Kamory Doumbia',84,26),('BISSOUMA','Yves Bissouma',50,26),('DORGELES','Néné Dorgeles',16,26),('SINAYOKO','Lassine Sinayoko',50,5)])}
PHOTO={'Djigui Diarra':'djigui-diarra','Hamari Traoré':'3248','Boubakar Kouyaté':'kiki-kouyate','Sikou Niakaté':'sikou-niakate','Falaye Sacko':'falaye-sacko',
 'Mohamed Camara':'mohamed-camara','Aliou Dieng':'aliou-dieng','Amadou Haïdara':'amadou-haidara-1998','Kamory Doumbia':'kamory-doumbia-2003','Adama Traoré':'adama-traore-malouda',
 'Lassine Sinayoko':'105182','Fodé Doucouré':'fode-doucoure','Mamadou Fofana':'mamadou-fofana','Abdoulaye Diaby':'abdoulaye-diaby','Amadou Danté':'amadou-dante',
 'Lassana Coulibaly':'lassana-coulibaly','Yves Bissouma':'yves-bissouma','Néné Dorgeles':'nene-dorgeles-2002'}
def terrain(coach):
    sysm,J=ONZE[coach]; n=NB[coach]; X0,Y0,W0,H0=64,366,952,722
    g=f'<rect x="{X0}" y="{Y0}" width="{W0}" height="{H0}" rx="6" fill="#0B7A3B"/>'
    L='stroke="#FFF3C4" stroke-width="3" fill="none" opacity=".75"'
    g+=f'<rect x="{X0+20}" y="{Y0+20}" width="{W0-40}" height="{H0-40}" {L}/><line x1="{X0+20}" y1="{Y0+H0/2}" x2="{X0+W0-20}" y2="{Y0+H0/2}" {L}/><circle cx="{X0+W0/2}" cy="{Y0+H0/2}" r="80" {L}/>'
    g+=f'<rect x="{X0+W0/2-200}" y="{Y0+20}" width="400" height="130" {L}/><rect x="{X0+W0/2-200}" y="{Y0+H0-150}" width="400" height="130" {L}/>'
    for nom,cle,x,y in J:
        cx,cy=X0+40+(W0-80)*x/100, Y0+30+(H0-60)*y/100; t=T[coach][cle]
        R0=48; i=PHOTO[cle]; bx,by=cx+R0*.72,cy+R0*.72
        g+=f'<clipPath id="c{i}"><circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R0}"/></clipPath><circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R0}" fill="#FFF3C4"/>'
        g+=f'<image href="photos/{i}.png" x="{cx-R0:.0f}" y="{cy-R0:.0f}" width="{2*R0}" height="{2*R0}" clip-path="url(#c{i})" preserveAspectRatio="xMidYMid slice"/>'
        g+=f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R0}" fill="none" stroke="#F6C41C" stroke-width="4"/>'
        g+=f'<text x="{cx:.0f}" y="{cy+R0+30:.0f}" text-anchor="middle" style="font:800 23px SC;letter-spacing:.03em;fill:#FFFFFF;stroke:#0B7A3B;stroke-width:7px;paint-order:stroke;stroke-linejoin:round">{nom}<tspan dx="6" style="font:700 19px SC;fill:#F6C41C">({t})</tspan></text>'
    return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350">{g}</svg>', sysm, n
COACH={'Chelle':('eric-chelle',('ml','fr')),'Saintfiet':('tom-saintfiet',('be',))}
def photo_coach(coach):
    ph,drs=COACH[coach]; D=196; F=50; x0=(D-len(drs)*F-(len(drs)-1)*4)/2
    h=f'<div style="position:absolute;left:{1016-D}px;top:100px;width:{D}px;height:{D}px"><img src="photos/{ph}.png" style="display:block;width:{D}px;height:{D}px;border-radius:50%;background:#FFF3C4;border:6px solid #064A25;box-sizing:border-box;object-fit:cover">'
    for j,d in enumerate(drs):
        h+=f'<img src="drapeaux/{d}.svg" style="position:absolute;left:{x0+j*(F+4)-4:.0f}px;bottom:-14px;width:{F}px;height:{F}px;border-radius:50%;border:4px solid #FBD134">'
    return h+'</div>'
for k,(coach,per,h2) in enumerate((('Chelle','2022-2024','ÉRIC CHELLE'),('Saintfiet','2024-2026','TOM SAINTFIET')),1):
    body,sysm,n=terrain(coach)
    onze={c for _,c,_,_ in ONZE[coach][1]}; reste=[(p,v) for p,v in T[coach].most_common() if p not in onze]
    suiv=reste[:4]; assert reste[4][1]<suiv[-1][1], 'égalité coupée'
    COURT={'Lassana Coulibaly':'L. COULIBALY','Mamadou Fofana':'M. FOFANA','Diadié Samassékou':'SAMASSÉKOU','Ismaël Diawara':'DIAWARA','Mohamed Camara':'M. CAMARA','Mamadou Sangaré':'SANGARÉ','Salim Diakité':'S. DIAKITÉ','El Bilal Touré':'E. B. TOURÉ'}
    js=' · '.join(f'{COURT[p]} ({v})' for p,v in suiv)
    body+=f'<div class="leg" style="top:1104px;font-size:22px;font-weight:500"><span>{js}</span></div>'
    body+=f'<div class="leg" style="top:1138px;font-size:22px"><span>ENTRE PARENTHÈSES : TITULARISATIONS SUR {n} MATCHS · SYSTÈME : {sysm}</span></div>'
    for suf,tt in (('',False),('_tt',True)):
        open(ICI/f'_p4_{k}{suf}.html','w',encoding='utf-8').write(page(f'MALI · {per} · <b>{n} MATCHS OFFICIELS</b>','LE ONZE TYPE',h2,'',photo_coach(coach)+body,'Matchs amicaux exclus',tt=tt))
for c in ('Chelle','Saintfiet'): print(c, NB[c], [(cle,T[c][cle]) for _,cle,_,_ in ONZE[c][1]])

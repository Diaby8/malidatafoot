"""Ce que toutes les mises en scène du duel partagent : les critères, les libellés, la phrase de synthèse, les notes de bas de page.
Le volume = vraie valeur pour 90 minutes ; la réussite = taux, avec le nombre de tentatives. Données : duel_export.py."""
import json
from da import fr
PLURIELS={'ATT':'avants-centres','LAT':'latéraux','DC':'défenseurs centraux','MDF':'milieux défensifs','MIL':'milieux','MOF':'milieux offensifs et ailiers'}
VOL=[('shots_p90','Tirs',1),('npxg_p90','Buts attendus hors penalty',2),('key_passes_p90','Passes clés',1),('receptions_in_box_p90','Ballons reçus dans la surface',1),('prog_carries_p90','Conduites progressives',1),('pressures_p90','Pressions',1)]
EFF=[('sot_pct','Tirs cadrés','shots_on_target','shots'),('conv_pct','Tirs transformés en but','goals','shots'),('drib_pct','Dribbles réussis','dribbles_won','dribbles'),('air_pct','Duels aériens gagnés','aerials_won',None),('pass_pct','Passes réussies','passes_completed','passes')]
COURT={'npxg_p90':['Buts attendus','hors penalty'],'key_passes_p90':['Passes','clés'],'receptions_in_box_p90':['Ballons reçus','dans la surface'],'prog_carries_p90':['Conduites','progressives']}
VERBE={'shots_p90':'tire {r} fois plus','npxg_p90':"se crée {r} fois plus d'occasions",'key_passes_p90':'donne {r} fois plus de passes clés','receptions_in_box_p90':'reçoit {r} fois plus de ballons dans la surface',
       'prog_carries_p90':"porte {r} fois plus le ballon vers l'avant",'pressures_p90':'presse {r} fois plus'}
REUSS={'sot_pct':'cadre {p} % de ses tirs','conv_pct':'transforme {p} % de ses tirs','drib_pct':'réussit {p} % de ses dribbles','air_pct':'gagne {p} % de ses duels aériens','pass_pct':'réussit {p} % de ses passes'}
def charger(chemin):
    D=json.load(open(chemin,encoding='utf-8')); (nA,A),(nB,B)=list(D['j'].items())
    return D,nA,A,nB,B,nA.split(' ')[-1],nB.split(' ')[-1],PLURIELS[D.get('role','ATT')]
def tentatives(J,num,den): return int(J[num]), (int(J[den]) if den else int(J['aerials_won']+J['aerials_lost']))
def synthese(X,Y,nom):
    """Le plus gros écart du joueur, en volume puis en réussite ; le rapport est calculé sur les vraies valeurs."""
    kv=max(VERBE,key=lambda k:X[k]/max(Y[k],1e-9)); ke=max(REUSS,key=lambda k:X[k]-Y[k])
    return f"{nom} {VERBE[kv].format(r=fr(X[kv]/Y[kv],1))} et {REUSS[ke].format(p=round(X[ke]))}."
buts=lambda J:f'but{"s" if J["goals"]>1 else ""} en {J["minutes"]:.0f} minutes'
NOTE1="Buts attendus : la somme des chances de marquer sur ses tirs."
seuil=lambda plur:f"{plur.capitalize()} ayant joué au moins 180 minutes."

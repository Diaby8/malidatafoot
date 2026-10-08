"""Données du duel : les deux joueurs et, pour chaque volume, le meilleur et la médiane des joueurs du même rôle.
Tout vient des tables gold du pipeline (même bassin que les fiches).   usage : python3 duel_export.py "<joueur A>" "<joueur B>" <sortie.json>"""
import json, sys, duckdb
A,B,OUT=sys.argv[1],sys.argv[2],sys.argv[3]
c=duckdb.connect('../data/warehouse.duckdb',read_only=True)
P=c.execute("select * from gold.player_profiles").df()
VOL=['shots_p90','npxg_p90','key_passes_p90','receptions_in_box_p90','prog_carries_p90','pressures_p90']
ja,jb=P[P.player==A].iloc[0],P[P.player==B].iloc[0]
assert ja.role==jb.role,'un duel compare deux joueurs du même rôle'
pool=P[P.role==ja.role]
pct=lambda n,d:float(n)/float(d)*100 if d else 0.0
def joueur(j):
    d={k:float(j[k]) for k in VOL+['minutes','matches','goals','np_goals','shots','shots_on_target','dribbles','dribbles_won','aerials_won','aerials_lost','passes','passes_completed','xg','npxg']}
    d.update(team=j.team,player_id=int(j.player_id),sot_pct=pct(j.shots_on_target,j.shots),conv_pct=pct(j.goals,j.shots),drib_pct=pct(j.dribbles_won,j.dribbles),
             air_pct=pct(j.aerials_won,j.aerials_won+j.aerials_lost),pass_pct=pct(j.passes_completed,j.passes))
    return d
D={'n':int(len(pool)),'role':ja.role,'max':{k:float(pool[k].max()) for k in VOL},'med':{k:float(pool[k].median()) for k in VOL},'j':{A:joueur(ja),B:joueur(jb)}}
json.dump(D,open(OUT,'w',encoding='utf-8'),ensure_ascii=False,indent=1); print('ok',OUT,D['n'],{k:round(v,2) for k,v in D['max'].items()})

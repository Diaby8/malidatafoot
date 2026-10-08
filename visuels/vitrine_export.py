"""Données de la vidéo vitrine : tout vient de l'entrepôt du pipeline (CAN 2023, StatsBomb Open Data)."""
import json, re
import duckdb, numpy as np
W='../data/warehouse.duckdb'
con=duckdb.connect(W,read_only=True)
D=json.load(open('../outputs/resultats.json',encoding='utf-8'))  # une seule source : la sortie du pipeline
out={k:D[k] for k in ('tirs','xg_chrono','periodes_fin','expulsions','totaux','volumes','reseau_passes','part_passes','matches','joueurs')}
out['scores']=D['scores'][:5]

# --- anatomie d'un but : Mali - Burkina Faso, Sinayoko 47'
mid,pos=3922244,95
rows=con.execute("""select e.idx,e.type,coalesce(p.display_name,e.player) as player,e.x,e.y,e.end_x,e.end_y,e.minute,e.second,e.ts,e.duration,e.team,e.pass_outcome
  from silver.events e left join silver.players p using(player_id)
  where e.match_id=? and e.possession=? and e.type in ('Pass','Carry','Shot') order by e.idx""",[mid,pos]).fetchall()
assert all(r[11]=='Mali' for r in rows) and all(r[12] is None for r in rows if r[1]=='Pass'), 'possession non continue'
t0=rows[0][9]
seq=[{'type':r[1],'player':r[2],'x':round(r[3],1),'y':round(r[4],1),'ex':round(r[5],1),'ey':round(r[6],1),'t':round(r[9]-t0,2),'d':round(r[10] or 0,2)} for r in rows]
m=con.execute("select home_team,away_team,home_score,away_score,stage from silver.matches where match_id=?",[mid]).fetchone()
out['but']={'seq':seq,'passes':sum(1 for s in seq if s['type']=='Pass'),'joueurs':len({s['player'] for s in seq}),'duree':round(rows[-1][9]-t0,1),
            'minute':rows[-1][7]+1,'match':list(m),'buteur':seq[-1]['player'],'xg':round(con.execute("select shot_xg from silver.events where match_id=? and possession=? and type='Shot' and shot_outcome='Goal'",[mid,pos]).fetchone()[0],2)}
print('but :',out['but']['passes'],'passes,',out['but']['joueurs'],'joueurs,',out['but']['duree'],'s', m, [s['player'] for s in seq if s['type']=='Pass'])

# --- fiche joueur : Hamari Traoré
IND=[('npxg_p90','Buts attendus','production'),('np_goals_p90','Buts','production'),('shots_p90','Tirs','production'),
     ('xa_p90','Passes déc. attendues','creation'),('key_passes_p90','Passes clés','creation'),('passes_into_box_p90','Passes dans la surface','creation'),
     ('prog_passes_p90','Passes vers l\'avant','progression'),('prog_carries_p90','Conduites vers l\'avant','progression'),('dribbles_won_p90','Dribbles réussis','progression'),
     ('tackles_interceptions_p90','Tacles et interceptions','defense'),('pressures_p90','Pressions','defense'),('recoveries_p90','Récupérations','defense'),('aerials_won_p90','Duels aériens','defense')]
pcols=[i[0]+'_pct' for i in IND]
import yaml
FR=yaml.safe_load(open('../config.yaml',encoding='utf-8')).get('team_labels',{})
assert float(con.execute('select max(npxg_p90_pct) from gold.player_scores').fetchone()[0])>1.5, 'centiles attendus sur 0-100'
df=con.execute("select * from gold.player_scores").df()
def fiche(name):
    r=df[df.player==name].iloc[0]
    grp=df[df.pos_group==r.pos_group]
    X=grp[pcols].to_numpy(float); v=r[pcols].to_numpy(float)
    dist=np.sqrt(((X-v)**2).sum(1)); o=np.argsort(dist)
    sim=[{'player':grp.iloc[i].player,'team':FR.get(grp.iloc[i].team,grp.iloc[i].team),'proche':int(round(100*(1-dist[i]/(100*np.sqrt(len(pcols)))))) } for i in o[1:4]]
    return {'player':r.player,'team':FR.get(r.team,r.team),'pos':r.pos_group,'poste':r.position,'minutes':int(round(r.minutes)),'matches':int(r.matches),'score':round(float(r.score),1),
            'rang':int(r.rang_poste),'effectif':int(r.effectif_poste),
            'ind':[{'k':k,'label':lab,'pilier':pil,'pct':int(round(float(r[k+'_pct'])))} for k,lab,pil in IND],
            'piliers':{p:round(float(r['pilier_'+p]),1) for p in ('production','creation','progression','defense','temps_de_jeu')},
            'brut':{'buts':int(r.goals),'xg':round(float(r.xg),2),'tirs':int(r.shots),'passes_cles':int(r.key_passes),'passes_dec':int(r.assists)},'proches':sim,'pid':int(r.player_id)}
F=fiche('Hamari Traoré')
h=con.execute("select x,y from silver.events where player_id=? and type in ('Pass','Carry','Ball Receipt*','Dribble','Shot','Ball Recovery','Interception','Duel','Clearance','Block','Pressure') and x is not null",[F['pid']]).fetchall()
gx,gy=12,8; grid=np.zeros((gy,gx),int)
for x,y in h: grid[min(gy-1,int(y/80*gy)),min(gx-1,int(x/120*gx))]+=1
F['chaleur']={'nx':gx,'ny':gy,'n':len(h),'max':int(grid.max()),'cells':grid.tolist()}
out['fiche']=F
print('fiche :',F['player'],F['score'],F['rang'],'/',F['effectif'],F['piliers'],[ (i['label'],i['pct']) for i in F['ind']],F['proches'],'actions',len(h))

# --- duel : Sinayoko / Osimhen
A,B=fiche('Lassine Sinayoko'),fiche('Victor Osimhen')
out['duel']=[{k:x[k] for k in ('player','team','minutes','matches','score','rang','effectif','piliers','brut')} for x in (A,B)]
print('duel :',[(x['player'],x['score'],x['rang'],x['minutes'],x['piliers'],x['brut']) for x in out['duel']])
print('réseau :',len(D['reseau_passes']['nodes']),'joueurs,',len(D['reseau_passes']['edges']),'liaisons, jusqu\'à',D['reseau_passes']['until_min'],'min', [n['player'] for n in D['reseau_passes']['nodes']])
json.dump(out,open('vitrine.json','w',encoding='utf-8'),ensure_ascii=False)
print('ok', len(json.dumps(out)))

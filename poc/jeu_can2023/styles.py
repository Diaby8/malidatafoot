import pandas as pd, numpy as np, json
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import pdist
E=pd.read_pickle('events.pkl'); M=pd.read_pickle('matches.pkl')
E=E[E.period<=4].copy()
SETP=['Corner','Free Kick','Goal Kick','Throw-in','Kick Off']
def metrics(E,M,only=None):
    rows=[]
    teams=only or sorted(set(M.home)|set(M.away))
    for tm in teams:
        mids=M[(M.home==tm)|(M.away==tm)].match_id; mins=M[M.match_id.isin(mids)].minutes.sum()
        e=E[E.match_id.isin(mids)]; us=e[e.team==tm]; them=e[e.team!=tm]
        p=us[us.type=='Pass']; op=p[~p['sub'].isin(SETP)]; opc=op[op.outcome.isna()]
        tp=them[them.type=='Pass']; top=tp[~tp['sub'].isin(SETP)]
        nposs=e[e.poss_team==tm].groupby('match_id').poss.nunique().sum()
        # final-third entries (open play completed passes + carries)
        ent=pd.concat([opc[(opc.x<80)&(opc.ex>=80)], us[(us.type=='Carry')&(us.x<80)&(us.ex>=80)]])
        wing=((ent.ey<80/3)|(ent.ey>160/3)).mean()
        pr=us[us.type=='Pressure']
        opp_pass_zone=top[top.x<=72]   # opponent's own 60% (opponent orientation)
        da=us[((us.type=='Duel')&(us['sub']=='Tackle'))|us.type.isin(['Interception','Foul Committed','Dribbled Past'])]
        da=da[da.x>=48]                # same zone in our orientation
        sh=us[(us.type=='Shot')&(us['sub']!='Penalty')]
        rows.append(dict(team=tm,matches=len(mids),minutes=int(mins),
          possession_share=len(p)/(len(p)+len(tp)),
          pass_length_mean_yd=op.length.mean(),
          long_pass_share=(op.length>=35).mean(),
          passes_per_possession=len(p[p.poss_team==tm])/nposs,
          directness=(opc.ex-opc.x).sum()/opc.length.sum(),
          crosses_p90=op.cross.sum()/mins*90,
          wing_entry_share=wing,
          pressures_p90=len(pr)/mins*90,
          pressure_x_mean=pr.x.mean(),
          ppda=len(opp_pass_zone)/len(da),
          shots_p90=len(sh)/mins*90,
          xg_per_shot=sh.xg.mean(),
          counter_shot_share=(sh.pp=='From Counter').mean(),
          dribbles_p90=(us.type=='Dribble').sum()/mins*90,
          press_per100_opp_pass=len(pr)/len(tp)*100, n_shots=len(sh), n_passes=len(p), n_pressures=len(pr), n_possessions=int(nposs)))
    return pd.DataFrame(rows).set_index('team')
FEAT=['possession_share','pass_length_mean_yd','long_pass_share','passes_per_possession','directness','crosses_p90','wing_entry_share',
      'pressures_p90','pressure_x_mean','ppda','shots_p90','xg_per_shot','counter_shot_share','dribbles_p90']
T=metrics(E,M)
def z(X): return (X-X.mean())/X.std(ddof=0)
Z=z(T[FEAT])
pca=PCA().fit(Z.values); C=pca.transform(Z.values)
load=pd.DataFrame(pca.components_[:3].T,index=FEAT,columns=['PC1','PC2','PC3'])
# orient: PC1 positive = possession ; PC2 positive = pressing intensity (pressures_p90)
s1=np.sign(load.loc['possession_share','PC1']); s2=np.sign(load.loc['pressures_p90','PC2']) or 1
load['PC1']*=s1; load['PC2']*=s2; C[:,0]*=s1; C[:,1]*=s2
coords=pd.DataFrame(C[:,:3],index=Z.index,columns=['PC1','PC2','PC3'])
sil={}; KM={}
for k in (3,4,5):
    km=KMeans(k,n_init=200,random_state=0).fit(Z.values); KM[k]=km.labels_; sil[k]=silhouette_score(Z.values,km.labels_)
kbest=max(sil,key=sil.get)
L=linkage(Z.values,'ward'); coph=cophenet(L,pdist(Z.values))[0]
H={k:fcluster(L,k,'maxclust') for k in (3,4,5)}
ari={k:adjusted_rand_score(KM[k],H[k]) for k in (3,4,5)}
lab=pd.Series(KM[kbest],index=Z.index); hlab=pd.Series(H[kbest],index=Z.index)
clusters={int(c):sorted(lab[lab==c].index) for c in sorted(lab.unique())}
hclusters={int(c):sorted(hlab[hlab==c].index) for c in sorted(hlab.unique())}
prof=Z.groupby(lab).mean().round(2)
dist=pd.Series(np.linalg.norm(Z.values-Z.loc['Mali'].values,axis=1),index=Z.index).drop('Mali').sort_values()
# Mali in PC space too
dpc=pd.Series(np.linalg.norm(coords[['PC1','PC2']].values-coords.loc['Mali',['PC1','PC2']].values,axis=1),index=Z.index).drop('Mali').sort_values()
# robustness: kmeans with different seeds -> how often each team shares Mali's cluster
co={t:0 for t in Z.index}
for seed in range(100):
    l=KMeans(kbest,n_init=10,random_state=seed).fit(Z.values).labels_
    for i,t in enumerate(Z.index): co[t]+= l[i]==l[list(Z.index).index('Mali')]
# sensitivity: Mali without the quarter-final vs CIV (red card 11v10)
E2=E[~((E.match_id==3922659))]; M2=M[M.match_id!=3922659]
T2=metrics(E2,M2); mali_wo=T2.loc['Mali',FEAT]
Zs=z(pd.concat([T[FEAT].drop('Mali'),mali_wo.to_frame().T]))
dist2=pd.Series(np.linalg.norm(Zs.values-Zs.loc['Mali'].values,axis=1),index=Zs.index).drop('Mali').sort_values()
ranks=T[FEAT+['press_per100_opp_pass']].rank(ascending=False,method='min').astype(int)
ranks['ppda_intensity_rank']=T.ppda.rank(ascending=True,method='min').astype(int)
# match bootstrap for Mali (1000 resamples of its 5 matches) -> 90% interval of value and rank vs other 23 point values
rng=np.random.default_rng(7); mm=list(M[(M.home=='Mali')|(M.away=='Mali')].match_id); BT=[]
KEYS=['possession_share','passes_per_possession','directness','dribbles_p90','crosses_p90','pressures_p90','pressure_x_mean','ppda','press_per100_opp_pass','shots_p90']
for b in range(1000):
    smp=rng.choice(mm,5,replace=True); Eb=pd.concat([E[E.match_id==m].assign(match_id=m*10+i) for i,m in enumerate(smp)])
    Mb=pd.concat([M[M.match_id==m].assign(match_id=m*10+i) for i,m in enumerate(smp)])
    BT.append(metrics(Eb,Mb,only=['Mali']).loc['Mali',KEYS])
BT=pd.DataFrame(BT); oth=T.drop('Mali')
boot={k:dict(value_90=[round(float(BT[k].quantile(.05)),4),round(float(BT[k].quantile(.95)),4)],
   rank_90=[int(x) for x in ((BT[k].apply(lambda v:(oth[k]>v).sum()+1)).quantile([.05,.95]).values)]) for k in KEYS}
res=dict(definitions=dict(
 scope="CAN 2023 (52 matchs StatsBomb), périodes 1-4 (tirs au but exclus). Coordonnées StatsBomb 120x80 yards, chaque équipe attaque vers x=120. Par 90 = total / minutes au chrono (90 ou 120 par match) x 90. Ratios = cumulés sur tous les matchs de l'équipe.",
 possession_share="passes de l'équipe / (passes de l'équipe + passes adverses) dans ses matchs (toutes passes)",
 pass_length_mean_yd="longueur moyenne des passes dans le jeu (hors corner, coup franc, six-mètres, touche, engagement), yards",
 long_pass_share="part des passes dans le jeu de 35 yards (32 m) ou plus",
 passes_per_possession="passes de l'équipe pendant ses possessions / nombre de possessions StatsBomb de l'équipe",
 directness="somme des gains vers l'avant (x_fin - x_début) / somme des longueurs, passes réussies dans le jeu",
 crosses_p90="centres dans le jeu (pass.cross) par 90",
 wing_entry_share="part des entrées dans le dernier tiers (passe réussie dans le jeu ou conduite de x<80 vers x>=80) qui arrivent dans un couloir (y<26,7 ou y>53,3)",
 pressures_p90="événements Pressure par 90", pressure_x_mean="x moyen des pressions (plus haut = presse plus loin)",
 ppda="passes adverses dans le jeu effectuées dans leurs 60 % de terrain (x<=72 côté adversaire) / nos actions défensives dans cette zone (x>=48 chez nous) : tacles (Duel Tackle, toutes issues), interceptions, fautes commises, duels perdus (Dribbled Past). Plus bas = pressing plus intense",
 shots_p90="tirs hors penalty par 90", xg_per_shot="xG StatsBomb moyen par tir hors penalty",
 counter_shot_share="part des tirs hors penalty dont le play_pattern est 'From Counter'", dribbles_p90="dribbles tentés par 90",
 standardization="z-score sur les 24 équipes (écart-type population)", pca="PCA sur les 14 z-scores ; signes orientés : PC1>0 = plus de possession, PC2>0 = plus de pressions par 90",
 clustering=f"k-means (200 initialisations) pour k=3..5, k retenu = meilleure silhouette ; contrôle Ward hiérarchique coupé au même k (ARI)"),
 teams=T.round(4).reset_index().to_dict('records'), zscores=Z.round(3).reset_index().to_dict('records'), ranks=ranks.reset_index().to_dict('records'),
 pca=dict(variance_explained=[round(v,4) for v in pca.explained_variance_ratio_[:6]], loadings=load.round(3).reset_index().rename(columns={'index':'metric'}).to_dict('records'),
          coordinates=coords.round(3).reset_index().rename(columns={'index':'team'}).to_dict('records')),
 clustering=dict(silhouette={int(k):round(v,4) for k,v in sil.items()}, k=int(kbest), kmeans_clusters=clusters, cluster_profiles_z=prof.reset_index().to_dict('records'),
   kmeans_all_k={int(k):{int(c):sorted(pd.Series(KM[k],index=Z.index)[lambda s:s==c].index) for c in set(KM[k])} for k in KM},
   ward_clusters=hclusters, ward_vs_kmeans_ARI={int(k):round(v,3) for k,v in ari.items()}, ward_cophenetic=round(coph,3),
   share_with_mali_over_100_seeds={t:v/100 for t,v in sorted(co.items(),key=lambda x:-x[1])}),
 mali=dict(values=T.loc['Mali'].round(4).to_dict(), z=Z.loc['Mali'].round(3).to_dict(), ranks=ranks.loc['Mali'].to_dict(), pc=coords.loc['Mali'].round(3).to_dict(),
   bootstrap_by_match=boot, cluster=int(lab['Mali']), cluster_members=clusters[int(lab['Mali'])], nearest_standardized=dist.head(5).round(3).to_dict(), nearest_pc12=dpc.head(5).round(3).to_dict(),
   sensitivity_without_QF_CIV=dict(values=mali_wo.round(4).to_dict(), nearest=dist2.head(5).round(3).to_dict())))
json.dump(res,open('styles.json','w'),indent=1,ensure_ascii=False,default=lambda o: o.item() if hasattr(o,'item') else str(o))
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(T[FEAT].round(3).sort_values('possession_share',ascending=False))
print(ranks.loc['Mali']); print(pd.DataFrame(boot).T)
print('var',pca.explained_variance_ratio_[:5].round(3)); print(load.round(2))
print(coords.round(2).sort_values('PC1'))
print('sil',sil,'k',kbest,'ARI',ari,'coph',coph); print(clusters); print(hclusters); print(prof)
print(dist.head(6)); print(dpc.head(5)); print(sorted(co.items(),key=lambda x:-x[1])[:10]); print(dist2.head(5)); print(mali_wo.round(3))
for k in KM: print(k,{c:sorted(pd.Series(KM[k],index=Z.index)[lambda s:s==c].index) for c in set(KM[k])})

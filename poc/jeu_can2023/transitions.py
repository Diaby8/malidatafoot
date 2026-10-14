import pandas as pd, numpy as np, json
E=pd.read_pickle('events.pkl'); M=pd.read_pickle('matches.pkl')
E=E[E.period<=4].sort_values(['match_id','index']).reset_index(drop=True)
NONPLAY=['Starting XI','Half Start','Half End','Tactical Shift','Substitution','Player On','Player Off',
 'Injury Stoppage','Referee Ball-Drop','Bad Behaviour','Own Goal For','Own Goal Against']
Ep=E[~E.type.isin(NONPLAY)]
P=Ep.drop_duplicates(['match_id','poss'])[['match_id','poss','poss_team','pp','period','type','t','x','y','sub']].copy()
P['prev_team']=P.groupby('match_id').poss_team.shift()
WINDOW=10.0
def regains(include_keeper=False):
    pats=['Regular Play','From Counter']+(['From Keeper'] if include_keeper else [])
    R=P[P.pp.isin(pats)&(P.prev_team.notna())&(P.prev_team!=P.poss_team)].copy()
    if not include_keeper: R=R[R.type!='Goal Keeper']
    return R
G=Ep.groupby(['match_id','poss'])
ONBALL={'Pass','Carry','Ball Receipt*','Dribble','Shot','Miscontrol','Dispossessed','Foul Won','Ball Recovery','Duel','Interception','50/50','Clearance','Block','Goal Keeper'}
def inbox(x,y): return (x>=102)&(y>=18)&(y<=62)
def measure(R):
    out=[]
    for r in R.itertuples():
        ev=G.get_group((r.match_id,r.poss)); ev=ev[(ev.team==r.poss_team)&(ev.period==r.period)]
        t0=r.t; w=ev[ev.t<=t0+WINDOW]
        pts=[]  # (x,y) points the ball reached with possession team, within window
        for e in w.itertuples():
            if e.type not in ONBALL or pd.isna(e.x): continue
            if e.type=='Ball Receipt*' and e.outcome=='Incomplete': continue
            pts.append((e.x,e.y))
            if e.type=='Carry' and (e.t+(e.duration or 0))<=t0+WINDOW and not pd.isna(e.ex): pts.append((e.ex,e.ey))
        xs=np.array([p[0] for p in pts]) if pts else np.array([r.x]); ys=np.array([p[1] for p in pts]) if pts else np.array([r.y])
        sh=w[w.type=='Shot']
        out.append(dict(match_id=r.match_id,team=r.poss_team,poss=r.poss,pp=r.pp,start=r.type,x0=r.x,y0=r.y,
            prog=max(0.0,xs.max()-r.x), reach_f3=bool((xs>=80).any()), reach_box=bool(inbox(xs,ys).any()),
            shot10=len(sh)>0, xg10=float(sh.xg.fillna(0).sum()), goal10=int((sh.outcome=='Goal').sum())))
    return pd.DataFrame(out)
mins={}
for m in M.itertuples():
    for tm in (m.home,m.away): mins[tm]=mins.get(tm,0)+m.minutes
nmatch=pd.concat([M.home,M.away]).value_counts().to_dict()
def agg(D):
    def f(d):
        tm=d.name; o=d[d.x0<80]; b=d[~inbox(d.x0,d.y0)]
        return pd.Series(dict(matches=nmatch[tm],minutes=mins[tm],regains=len(d),regains_p90=len(d)/mins[tm]*90,
          shot10_share=d.shot10.mean(), shots10_p90=d.shot10.sum()/mins[tm]*90,
          f3_entry_share=o.reach_f3.mean(), n_regains_outside_f3=len(o),
          box_entry_share=b.reach_box.mean(), n_regains_outside_box=len(b),
          prog_median_yd=d.prog.median(), prog_mean_yd=d.prog.mean(),
          xg10_per_regain=d.xg10.sum()/len(d), xg10_p90=d.xg10.sum()/mins[tm]*90, goals10=d.goal10.sum(),
          regain_x_mean=d.x0.mean(), regain_opp_half_share=(d.x0>60).mean()))
    return D.groupby('team').apply(f, include_groups=False)
RANKCOLS=['regains','regains_p90','shot10_share','shots10_p90','f3_entry_share','box_entry_share','prog_median_yd','prog_mean_yd','xg10_per_regain','xg10_p90','regain_x_mean','regain_opp_half_share']
def ranks(T): return T[RANKCOLS].rank(ascending=False,method='min').astype(int)
D=measure(regains()); T=agg(D); Rk=ranks(T)
# bootstrap Mali by match (cluster bootstrap) -> interval of value and rank vs others' point estimates
rng=np.random.default_rng(42); mm=D[D.team=='Mali'].match_id.unique(); boots=[]
others=T.drop('Mali')
for b in range(3000):
    s=rng.choice(mm,len(mm),replace=True)
    d=pd.concat([D[(D.team=='Mali')&(D.match_id==x)] for x in s]); 
    mn=sum(M.set_index('match_id').loc[x,'minutes'] for x in s); o=d[d.x0<80]; bb=d[~inbox(d.x0,d.y0)]
    v=dict(regains_p90=len(d)/mn*90, shot10_share=d.shot10.mean(), shots10_p90=d.shot10.sum()/mn*90,f3_entry_share=o.reach_f3.mean(),
       box_entry_share=bb.reach_box.mean(),prog_median_yd=d.prog.median(),prog_mean_yd=d.prog.mean(),xg10_per_regain=d.xg10.mean(),
       xg10_p90=d.xg10.sum()/mn*90,regain_x_mean=d.x0.mean(),regain_opp_half_share=(d.x0>60).mean())
    v.update({'rank_'+k:int((others[k]>val).sum()+1) for k,val in list(v.items())})
    boots.append(v)
B=pd.DataFrame(boots); boot={k:[float(B[k].quantile(.05)),float(B[k].quantile(.95))] for k in B.columns}
# sensitivity incl. keeper regains
D2=measure(regains(True)); T2=agg(D2); Rk2=ranks(T2)
# Mali per match
pm=D[D.team=='Mali'].groupby('match_id').agg(regains=('x0','size'),shot10=('shot10','mean'),xg10=('xg10','sum'),x0=('x0','mean'),prog_med=('prog','median'))
pm=pm.join(M.set_index('match_id')[['home','away','hs','as_','stage','minutes']])
# league-wide
lw=dict(regains=len(D),shot10_share=D.shot10.mean(),f3=D[D.x0<80].reach_f3.mean(),box=D[~inbox(D.x0,D.y0)].reach_box.mean(),
  prog_median=D.prog.median(),xg10_per_regain=D.xg10.mean(),regain_x_mean=D.x0.mean(),opp_half=(D.x0>60).mean(),
  start_types=D.start.value_counts().to_dict(), pp=D.pp.value_counts().to_dict())
# Mali: shots10 by match & by regain zone
mz=D[D.team=='Mali'].assign(zone=pd.cut(D.x0,[0,40,60,80,120.1],labels=['def_third_0-40','mid_own_40-60','mid_opp_60-80','att_third_80+']))
lz=D.assign(zone=pd.cut(D.x0,[0,40,60,80,120.1],labels=['def_third_0-40','mid_own_40-60','mid_opp_60-80','att_third_80+']))
zones={'Mali':mz.groupby('zone',observed=False).agg(n=('x0','size'),shot10=('shot10','mean'),xg10=('xg10','mean')).reset_index().to_dict('records'),
       'all':lz.groupby('zone',observed=False).agg(n=('x0','size'),shot10=('shot10','mean'),xg10=('xg10','mean')).reset_index().to_dict('records')}
res=dict(definitions=dict(
  regain="Début d'une possession StatsBomb dont le play_pattern est 'Regular Play' ou 'From Counter', dont la possession précédente (même match) appartenait à l'adversaire, et dont le premier événement n'est pas une action du gardien (exclut arrêts/prises, cohérent avec l'exclusion de 'From Keeper'). Exclut coups francs, corners, touches, six-mètres, engagements. Premier événement observé : Ball Recovery, passe de type Recovery/Interception, Duel Tackle gagné, Interception gagnée, 50/50 gagné, Block-déviation. Périodes 1-4 (tirs au but exclus).",
  window="10,0 s après l'horodatage du premier événement, même période, seulement les événements de l'équipe dans la MÊME possession StatsBomb (une perte de balle arrête la fenêtre).",
  points_reached="positions des événements balle au pied de l'équipe (passe, conduite, réception réussie, dribble, tir, etc.) + fin de conduite si la conduite se termine avant 10 s ; la fin d'une passe est comptée via la réception réussie horodatée.",
  shot10_share="part des récupérations suivies d'au moins un tir dans les 10 s",
  f3_entry_share="part des récupérations faites hors du dernier tiers (x<80) où le ballon atteint x>=80 dans les 10 s",
  box_entry_share="part des récupérations faites hors de la surface où le ballon atteint la surface (x>=102, 18<=y<=62) dans les 10 s",
  prog="max(x atteint) - x de récupération, en yards StatsBomb (terrain 120x80 yd ; 1 yd = 0,914 m), plancher 0",
  xg10_per_regain="somme des xG StatsBomb des tirs dans la fenêtre / nombre de récupérations",
  regain_x_mean="x moyen de la récupération (0 = propre but, 120 = but adverse) ; regain_opp_half_share = part avec x>60",
  per90="divisé par les minutes jouées par l'équipe au chrono (90 ou 120 par match) x 90",
  ranks="1 = valeur la plus élevée parmi 24 équipes (ex aequo = même rang). Pour regain_x_mean, 1 = récupère le plus haut.",
  bootstrap="Mali : bootstrap par match (3000 tirages des 5 matchs avec remise), intervalle 5-95 % de la valeur et du rang de Mali face aux valeurs ponctuelles des 23 autres."),
  league_wide=lw, teams=T.round(4).reset_index().to_dict('records'), ranks=Rk.reset_index().to_dict('records'),
  mali=dict(values=T.loc['Mali'].round(4).to_dict(), ranks=Rk.loc['Mali'].to_dict(), bootstrap_90=boot,
     per_match=pm.reset_index().to_dict('records'), by_zone=zones,
     sensitivity_incl_keeper=dict(values=T2.loc['Mali'].round(4).to_dict(),ranks=Rk2.loc['Mali'].to_dict())))
json.dump(res,open('transitions.json','w'),indent=1,ensure_ascii=False,default=lambda o: o.item() if hasattr(o,'item') else str(o))
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(T.sort_values('shot10_share',ascending=False).round(3))
print(Rk.loc['Mali']); print(pd.Series(boot)); print(pm); print(lw); print(zones)
print('sens',Rk2.loc['Mali'].to_dict()); print(T2.loc['Mali'].round(3).to_dict())
D.to_pickle('regains.pkl')
# --- zone-adjusted expectation (league rate per regain zone x team's regain locations)
bins=[0,40,60,80,120.1]
D['zone']=pd.cut(D.x0,bins).astype(str)
rate=D.groupby('zone').agg(s_rate=('shot10','mean'),xg_rate=('xg10','mean'))
D=D.join(rate,on='zone')
Z=D.groupby('team').agg(n=('x0','size'),obs_shots10=('shot10','sum'),exp_shots10=('s_rate','sum'),obs_xg10=('xg10','sum'),exp_xg10=('xg_rate','sum'))
Z['exp_shot10_share_from_location']=Z.exp_shots10/Z.n; Z['obs_over_exp_shots']=Z.obs_shots10/Z.exp_shots10
ZR=Z[['exp_shot10_share_from_location','obs_over_exp_shots']].rank(ascending=False,method='min').astype(int)
ms=D[(D.team=="Mali")&D.shot10]
shots_list=[]
for r in ms.itertuples():
    ev=Ep[(Ep.match_id==r.match_id)&(Ep.poss==r.poss)&(Ep.type=='Shot')]
    for s in ev.itertuples(): shots_list.append(dict(match_id=r.match_id,minute=s.minute,player=s.player,xg=round(s.xg,3),outcome=s.outcome,regain_type=r.start,regain_x=r.x0,play_pattern=r.pp))
res['zone_adjusted']=dict(definition="Taux de tir à 10 s de l'ensemble du tournoi par zone de récupération (x: 0-40, 40-60, 60-80, 80-120), appliqué aux récupérations de chaque équipe = ce que sa hauteur de récupération 'promet' ; obs/exp = ce qu'elle en a fait.",
   league_rates=rate.reset_index().to_dict('records'), teams=Z.round(4).reset_index().to_dict('records'), mali=Z.loc['Mali'].round(4).to_dict(), mali_ranks=ZR.loc['Mali'].to_dict())
res['mali']['shots_within_10s']=shots_list
json.dump(res,open('transitions.json','w'),indent=1,ensure_ascii=False,default=lambda o: o.item() if hasattr(o,'item') else str(o))
print(Z.loc['Mali'], ZR.loc['Mali'], shots_list)

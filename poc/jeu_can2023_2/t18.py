"""T18 — Tirer beaucoup ne suffit pas : volume et qualité des tirs par équipe."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

d = load(); E, M = d['E'], d['M']
SEMIS = ["Côte d'Ivoire", 'Nigeria', 'South Africa', 'Congo DR']
TM = team_minutes(M).groupby('team').agg(minutes=('minutes', 'sum'), matches=('match_id', 'nunique'))
sh = E[E.type == 'Shot'].copy()
sh['np'] = sh.shot_type != 'Penalty'
sh['goal'] = sh.shot_outcome == 'Goal'
sh['out_box'] = ~in_box(sh.x, sh.y)
sh['dist_m'] = np.hypot(120 - sh.x, 40 - sh.y) * YD
og = E[E.type == 'Own Goal For'].groupby('team').size()
rows = []
for t, g in sh.groupby('team'):
    n = g[g.np]
    mins = TM.loc[t, 'minutes']
    rows.append(dict(team=t, matches=int(TM.loc[t, 'matches']), minutes=int(mins), shots=int(len(g)), pens=int((~g.np).sum()), np_shots=int(len(n)),
                     shots_p90=len(g) / mins * 90, np_shots_p90=len(n) / mins * 90, npxg=n.shot_xg.sum(), npxg_p90=n.shot_xg.sum() / mins * 90,
                     npxg_per_shot=n.shot_xg.sum() / len(n), out_box_share=n.out_box.mean(), box_shots_p90=(~n.out_box).sum() / mins * 90,
                     big_chances=int((n.shot_xg >= 0.3).sum()), big_chances_p90=(n.shot_xg >= 0.3).sum() / mins * 90,
                     median_dist_m=n.dist_m.median(), np_goals=int(n.goal.sum()), g_minus_npxg=n.goal.sum() - n.shot_xg.sum(),
                     own_goals_for=int(og.get(t, 0)), pen_goals=int(g[~g.np].goal.sum()),
                     on_target_share=n.shot_outcome.isin(['Goal', 'Saved', 'Saved To Post']).mean()))
T = pd.DataFrame(rows)
metrics = ['shots_p90', 'np_shots_p90', 'npxg_p90', 'npxg_per_shot', 'out_box_share', 'box_shots_p90', 'big_chances_p90', 'median_dist_m', 'g_minus_npxg', 'on_target_share']
for c in metrics:
    T[c + '_rank'] = T[c].rank(ascending=False, method='min').astype(int)
mali = T[T.team == 'Mali'].iloc[0]
rk = {c: dict(value=round(float(mali[c]), 3), rank=int(mali[c + '_rank']), n=len(T), team_mean=round(float(T[c].mean()), 3),
              median=round(float(T[c].median()), 3)) for c in metrics}
# Mali par match
mm = []
for mid, g in sh[sh.team == 'Mali'].groupby('match_id'):
    m = M[M.match_id == mid].iloc[0]; n = g[g.np]
    mm.append(dict(match=f"{m.home} {m.hs}-{m.as_} {m.away}", minutes=int(m.reg_len), shots=int(len(g)), np_shots=int(len(n)), npxg=round(float(n.shot_xg.sum()), 2),
                   npxg_per_shot=round(float(n.shot_xg.mean()), 3), out_box_share=round(float(n.out_box.mean()), 2), np_goals=int(n.goal.sum())))
# corrélation entre équipes : qu'est-ce qui suit le npxG/90, le volume ou la qualité ?
corr = dict(npxg_p90_vs_np_shots_p90=round(float(T.npxg_p90.corr(T.np_shots_p90, method='spearman')), 3),
            npxg_p90_vs_npxg_per_shot=round(float(T.npxg_p90.corr(T.npxg_per_shot, method='spearman')), 3))
# contrefactuel simple : le volume du Mali avec la qualité moyenne par tir des demi-finalistes / du tournoi
semi = T[T.team.isin(SEMIS)]
cf = dict(mali_np_shots=int(mali.np_shots), mali_npxg=round(float(mali.npxg), 2),
          with_tournament_xg_per_shot=round(float(mali.np_shots * T.npxg.sum() / T.np_shots.sum()), 2),
          with_semis_xg_per_shot=round(float(mali.np_shots * semi.npxg.sum() / semi.np_shots.sum()), 2),
          tournament_pooled_xg_per_shot=round(float(T.npxg.sum() / T.np_shots.sum()), 3), semis_pooled_xg_per_shot=round(float(semi.npxg.sum() / semi.np_shots.sum()), 3))
out = dict(
    definitions=dict(
        minutes="Minutes d'équipe à l'horloge réglementaire : 90 par match, 120 avec prolongation ; séance de tirs au but exclue.",
        shots="Tous les tirs StatsBomb (penalties compris) pour 'shots' ; np = hors penalty. npxG = somme du statsbomb_xg des tirs hors penalty.",
        out_box="Tir hors surface : x < 102 ou y hors de 18..62 (surface de 16,5 m).",
        g_minus_npxg="Buts hors penalty (contre-son-camp exclus) moins npxG.",
        big_chances="Tirs hors penalty à xG >= 0,30 (seuil choisi par nous, indicatif).",
        on_target="Part des tirs hors penalty cadrés (but, arrêté, arrêté sur le poteau).",
        ranks="Rang 1 = valeur la plus haute (pour median_dist_m, 1 = tirs les plus lointains ; pour out_box_share, 1 = plus forte part de loin). 24 équipes.",
    ),
    mali=T[T.team == 'Mali'].round(3).to_dict('records')[0], mali_ranks=rk, mali_by_match=mm, semifinalists=semi.round(3).to_dict('records'),
    correlations_between_teams=corr, counterfactual=cf,
    teams=T.sort_values('np_shots_p90', ascending=False).round(3).to_dict('records'),
)
save('t18.json', out)
if __name__ == '__main__':
    import pprint
    pprint.pprint({k: out[k] for k in ['mali', 'mali_ranks', 'mali_by_match', 'correlations_between_teams', 'counterfactual']}, width=170)
    print(T.sort_values('np_shots_p90', ascending=False)[['team', 'matches', 'shots', 'np_shots', 'np_shots_p90', 'npxg', 'npxg_p90', 'npxg_per_shot', 'out_box_share', 'big_chances', 'np_goals', 'g_minus_npxg', 'median_dist_m', 'npxg_p90_rank', 'npxg_per_shot_rank']].round(3).to_string())

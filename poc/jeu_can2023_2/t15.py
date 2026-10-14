"""T15 — Sinayoko, le buteur d'une équipe qui ne crée pas."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

d = load(); E, P = d['E'], d['P']
MIN_MIN = 180
CARRY_M = 5.0  # conduite cumulée (m) au-delà de laquelle le tir est compté comme « action personnelle » après la passe
OPP_TOUCH = {'Clearance', 'Block', 'Interception', 'Error', 'Ball Recovery', 'Goal Keeper', 'Miscontrol', 'Dispossessed', 'Duel', '50/50'}

S = E[(E.type == 'Shot') & (E.shot_type != 'Penalty')].copy()
byid = E.set_index('id')
cls = []
for r in S.itertuples():
    g = E[(E.match_id == r.match_id)]
    if r.shot_key_pass_id is not None and r.shot_key_pass_id in byid.index:
        kp = byid.loc[r.shot_key_pass_id]
        btw = g[(g.idx > kp.idx) & (g.idx < r.idx)]
        opp = btw[(btw.team != r.team) & btw.type.isin(OPP_TOUCH - {'Duel'})]
        own_c = btw[(btw.player_id == r.player_id) & (btw.type == 'Carry')]
        dist = (np.hypot(own_c.ex - own_c.x, own_c.ey - own_c.y).sum()) * YD
        drib = ((btw.player_id == r.player_id) & (btw.type == 'Dribble')).any()
        if len(opp):
            c = 'passe_puis_ballon_devie'
        elif dist >= CARRY_M or drib:
            c = 'passe_puis_action_perso'
        else:
            c = 'passe_directe'
        cls.append((r.id, c, kp.pass_type if isinstance(kp.pass_type, str) else 'Jeu', round(dist, 1), bool(drib)))
    else:
        if r.shot_type in ('Free Kick', 'Corner'):
            c = 'coup_franc_direct'
        else:
            prev = g[(g.idx < r.idx) & (g.t_match >= r.t_match - 10) & (g.period == r.period)]
            if ((prev.type == 'Shot') & (prev.team == r.team)).any():
                c = 'rebond'
            elif ((prev.player_id == r.player_id) & prev.type.isin(['Carry', 'Dribble', 'Ball Recovery', 'Interception'])).any():
                c = 'action_perso_sans_passe'
            else:
                c = 'autre_sans_passe'
        cls.append((r.id, c, None, None, None))
C = pd.DataFrame(cls, columns=['id', 'origin', 'kp_type', 'carry_m', 'dribble'])
S = S.merge(C, on='id')
S['goal'] = S.shot_outcome == 'Goal'
S['assisted'] = S.shot_key_pass_id.notna()

g = S.groupby('player_id').agg(np_shots=('id', 'size'), npxg=('shot_xg', 'sum'), np_goals=('goal', 'sum'),
                               ast_shots=('assisted', 'sum'), ast_xg=('shot_xg', lambda s: s[S.loc[s.index, 'assisted']].sum()),
                               direct_xg=('shot_xg', lambda s: s[S.loc[s.index, 'origin'] == 'passe_directe'].sum()),
                               direct_shots=('origin', lambda s: (s == 'passe_directe').sum()),
                               box_shots=('x', lambda s: in_box(s, S.loc[s.index, 'y']).sum()))
pens = E[(E.type == 'Shot') & (E.shot_type == 'Penalty')].groupby('player_id').agg(pens=('id', 'size'), pen_goals=('shot_outcome', lambda s: (s == 'Goal').sum()))
F = P[(P.fwd_share >= 0.5) & (P.minutes >= MIN_MIN)].merge(g, left_on='player_id', right_index=True, how='left').merge(pens, left_on='player_id', right_index=True, how='left').fillna(0)
F['np_shots_p90'] = F.np_shots / F.minutes * 90
F['npxg_p90'] = F.npxg / F.minutes * 90
F['xg_per_shot'] = F.npxg / F.np_shots.replace(0, np.nan)
F['g_minus_npxg'] = F.np_goals - F.npxg
F['np_goals_p90'] = F.np_goals / F.minutes * 90
F['ast_xg_p90'] = F.ast_xg / F.minutes * 90
F['direct_xg_p90'] = F.direct_xg / F.minutes * 90
F['assisted_share'] = F.ast_shots / F.np_shots.replace(0, np.nan)
N = len(F)
sin = F[F.player == 'Lassine Sinayoko'].iloc[0]
ranks = {}
for c in ['np_shots', 'np_shots_p90', 'npxg', 'npxg_p90', 'xg_per_shot', 'np_goals', 'np_goals_p90', 'g_minus_npxg', 'ast_xg_p90', 'direct_xg_p90', 'assisted_share']:
    s = F[c].dropna()
    ranks[c] = dict(value=round(float(sin[c]), 3), rank=int((s > sin[c]).sum() + 1), n=int(len(s)), median=round(float(s.median()), 3),
                    max=round(float(s.max()), 3), leader=F.loc[s.idxmax(), 'player'])
# part de Sinayoko dans le npxG du Mali
mali = S[S.team == 'Mali']
mali_tot = dict(np_shots=int(len(mali)), npxg=round(float(mali.shot_xg.sum()), 3), np_goals=int(mali.goal.sum()),
                sinayoko_share_npxg=round(float(mali[mali.player == 'Lassine Sinayoko'].shot_xg.sum() / mali.shot_xg.sum()), 3),
                sinayoko_share_shots=round(float((mali.player == 'Lassine Sinayoko').mean()), 3),
                sinayoko_share_goals=round(float(mali[mali.player == 'Lassine Sinayoko'].goal.sum() / mali.goal.sum()), 3))
# même part chez les autres équipes : meilleur « porteur » de npxG
team_lead = []
for t, gg in S.groupby('team'):
    s = gg.groupby('player').shot_xg.sum().sort_values(ascending=False)
    team_lead.append(dict(team=t, top_player=s.index[0], top_share=round(float(s.iloc[0] / s.sum()), 3), team_npxg=round(float(s.sum()), 2)))
team_lead = sorted(team_lead, key=lambda r: -r['top_share'])
shots_sin = S[S.player == 'Lassine Sinayoko'][['match_id', 'minute', 'x', 'y', 'shot_xg', 'shot_outcome', 'origin', 'kp_type', 'carry_m', 'dribble', 'pp']]
shots_sin = shots_sin.assign(x_m=(shots_sin.x * YD).round(1), dist_goal_m=(np.hypot(120 - shots_sin.x, 40 - shots_sin.y) * YD).round(1))
key_passers = []
for r in S[(S.player == 'Lassine Sinayoko') & S.assisted].itertuples():
    key_passers.append(byid.loc[r.shot_key_pass_id].player)
out = dict(
    definitions=dict(
        population=f"Mêmes attaquants que T14 : >= 50 % des actions à un poste d'avant-centre ou d'ailier, >= {MIN_MIN} min. N={N}.",
        shots="Tirs hors penalty, séance de tirs au but exclue ; buts = tirs hors penalty marqués (contre-son-camp exclus). npxG = somme du statsbomb_xg de ces tirs.",
        origin=f"passe_directe : tir avec passe clé (key_pass_id) et moins de {CARRY_M:.0f} m de conduite du tireur, sans dribble, entre la passe et le tir ; passe_puis_action_perso : passe clé puis >= {CARRY_M:.0f} m de conduite ou un dribble du tireur ; passe_puis_ballon_devie : un adversaire touche le ballon entre la passe et le tir ; sans passe clé : rebond (tir de son équipe dans les 10 s avant), action_perso_sans_passe (conduite/dribble/récupération du tireur dans les 10 s), coup_franc_direct, autre.",
        ast_xg_p90="npxG des tirs précédés d'une passe clé d'un coéquipier, par 90 minutes (« xG servi »). direct_xg_p90 : seulement les tirs 'passe_directe'.",
    ),
    n_forwards=N,
    sinayoko=dict(minutes=round(float(sin.minutes), 1), np_shots=int(sin.np_shots), npxg=round(float(sin.npxg), 3), np_goals=int(sin.np_goals),
                  penalties=int(sin.pens), origin_counts=S[S.player == 'Lassine Sinayoko'].origin.value_counts().to_dict(),
                  origin_xg=S[S.player == 'Lassine Sinayoko'].groupby('origin').shot_xg.sum().round(3).to_dict(),
                  key_passers=pd.Series(key_passers).value_counts().to_dict(), shots=shots_sin.round(3).to_dict('records')),
    sinayoko_ranks=ranks, mali=mali_tot, top_npxg_share_by_team=team_lead,
    pool_origin_share=S[S.player_id.isin(F.player_id)].origin.value_counts(normalize=True).round(3).to_dict(),
    pool_pooled=dict(xg_per_shot=round(float(F.npxg.sum() / F.np_shots.sum()), 3), npxg_p90=round(float(F.npxg.sum() / F.minutes.sum() * 90), 3),
                     ast_xg_p90=round(float(F.ast_xg.sum() / F.minutes.sum() * 90), 3), g_minus_npxg_total=round(float(F.g_minus_npxg.sum()), 2)),
    table=F[['player', 'team', 'main_pos', 'minutes', 'np_shots', 'np_shots_p90', 'npxg', 'npxg_p90', 'xg_per_shot', 'np_goals', 'g_minus_npxg',
             'ast_shots', 'ast_xg', 'ast_xg_p90', 'direct_shots', 'direct_xg_p90', 'pens']].sort_values('npxg', ascending=False).round(3).to_dict('records'),
)
save('t15.json', out)
if __name__ == '__main__':
    import pprint
    pprint.pprint({k: out[k] for k in out if k not in ('table', 'definitions', 'top_npxg_share_by_team')}, width=170)
    pprint.pprint(team_lead[:8])
    print(pd.DataFrame(out['table']).head(20).to_string())

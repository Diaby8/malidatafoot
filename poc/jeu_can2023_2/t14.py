"""T14 — Sinayoko, premier défenseur : pressing des attaquants de la CAN 2023."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

d = load(); E, P = d['E'], d['P']
MIN_MIN = 180
SETP = {'From Throw In', 'From Free Kick', 'From Corner', 'From Goal Kick', 'From Kick Off'}
WIN = 5.0

# actions de contrôle du ballon (définition de la récupération)
ctrl = E[(E.type.isin(['Pass', 'Carry', 'Shot', 'Dribble']) & ~E.pass_type.isin(SET_PIECE_PASS) & ~((E.type == 'Shot') & (E.shot_type != 'Open Play')))
         | ((E.type == 'Ball Recovery') & ~E.recovery_failure)
         | ((E.type == 'Interception') & E.interception_outcome.isin(['Won', 'Success In Play']))
         | ((E.type == 'Duel') & (E.duel_type == 'Tackle') & E.duel_outcome.isin(['Won', 'Success In Play']))]
# variante : nouvelle possession de l'équipe qui presse (premier événement de la possession), hors reprises arrêtées
first = E.sort_values('idx').groupby(['match_id', 'poss']).first().reset_index()
pr = E[E.type == 'Pressure'].copy()
res = []
for (mid, team), g in pr.groupby(['match_id', 'team']):
    c = ctrl[(ctrl.match_id == mid) & (ctrl.team == team)]
    f = first[(first.match_id == mid) & (first.poss_team == team) & ~first.pp.isin(SETP)]
    cp, ct, ci, cpl = c.period.values, c.t.values, c.idx.values, c.player_id.values
    fp, ft, fpo = f.period.values, f.t.values, f.poss.values
    for r in g.itertuples():
        m = (cp == r.period) & (ci > r.idx) & (ct <= r.t + WIN) & (ct >= r.t)
        k = np.flatnonzero(m)
        mf = (fp == r.period) & (fpo > r.poss) & (ft >= r.t) & (ft <= r.t + WIN)
        res.append((r.id, len(k) > 0, len(k) > 0 and cpl[k[0]] == r.player_id, bool(mf.any())))
R = pd.DataFrame(res, columns=['id', 'regain5', 'own_regain5', 'regain5_newposs'])
pr = pr.merge(R, on='id')
pr['on_opp_ball'] = pr.poss_team != pr.team  # pression pendant une possession adverse
pr['opp_half'] = pr.x > 60

g = pr.groupby('player_id').agg(pressures=('id', 'size'), opp_half=('opp_half', 'sum'), final_third=('x', lambda s: (s >= 80).sum()),
                                mean_x=('x', 'mean'), median_x=('x', 'median'), regains5=('regain5', 'sum'), regains5_np=('regain5_newposs', 'sum'), own_regains5=('own_regain5', 'sum'),
                                counterpress=('counterpress', 'sum'),
                                cp_regains5=('regain5', lambda s: (s & pr.loc[s.index, 'counterpress']).sum()))
F = P[(P.fwd_share >= 0.5) & (P.minutes >= MIN_MIN)].merge(g, left_on='player_id', right_index=True, how='left').fillna(0)
for c in ['regains5_np', 'pressures', 'opp_half', 'final_third', 'regains5', 'own_regains5', 'counterpress', 'cp_regains5']:
    F[c + '_p90'] = F[c] / F.minutes * 90
F['regain_rate'] = F.regains5 / F.pressures
F['regain_rate_np'] = F.regains5_np / F.pressures
F['cp_regain_rate'] = np.where(F.counterpress > 0, F.cp_regains5 / F.counterpress.replace(0, np.nan), np.nan)
F['opp_half_share'] = F.opp_half / F.pressures
F['mean_x_m'] = F.mean_x * YD
F['median_x_m'] = F.median_x * YD
N = len(F)
ranks = {}
sin = F[F.player == 'Lassine Sinayoko'].iloc[0]
for c in ['pressures_p90', 'opp_half_p90', 'final_third_p90', 'regains5_p90', 'regain_rate', 'counterpress_p90', 'cp_regains5_p90',
          'cp_regain_rate', 'opp_half_share', 'mean_x_m', 'own_regains5_p90', 'regains5_np_p90', 'regain_rate_np']:
    s = F[c].dropna()
    ranks[c] = dict(value=round(float(sin[c]), 3), rank=int((s > sin[c]).sum() + 1), n=int(len(s)),
                    median=round(float(s.median()), 3), p75=round(float(s.quantile(.75)), 3), max=round(float(s.max()), 3),
                    leader=F.loc[s.idxmax(), 'player'])
CF = {'Center Forward', 'Left Center Forward', 'Right Center Forward', 'Secondary Striker'}
S = F[F.main_pos.isin(CF)]
ranks_cf = {c: dict(value=round(float(sin[c]), 3), rank=int((S[c] > sin[c]).sum() + 1), n=int(len(S)), median=round(float(S[c].median()), 3))
            for c in ['pressures_p90', 'opp_half_p90', 'regains5_p90', 'regain_rate', 'mean_x_m', 'median_x_m', 'counterpress_p90']}
cols = ['player', 'team', 'main_pos', 'minutes', 'pressures', 'pressures_p90', 'opp_half', 'opp_half_p90', 'opp_half_share', 'regains5',
        'regains5_p90', 'regain_rate', 'regains5_np', 'regain_rate_np', 'own_regains5', 'counterpress', 'counterpress_p90', 'cp_regains5', 'cp_regain_rate', 'mean_x_m', 'median_x_m']
table = F[cols].sort_values('pressures_p90', ascending=False).round(3).to_dict('records')
# Mali : contexte équipe
mali_pr = pr[pr.team == 'Mali']
out = dict(
    definitions=dict(
        population=f"Attaquants : au moins 50 % de leurs actions (événements StatsBomb avec poste) à un poste d'avant-centre (Center/Left/Right Center Forward, Secondary Striker) ou d'ailier (Left/Right Wing), et au moins {MIN_MIN} minutes (horloge réglementaire, prolongations comprises, arrêts de jeu non). N={N}.",
        pressure="Événement StatsBomb 'Pressure' (le joueur presse le porteur ou le receveur). Séance de tirs au but exclue.",
        opp_half="Pression avec x > 60 yards (repère de l'équipe qui presse, qui attaque vers x=120).",
        regain5=f"Récupération collective dans les {WIN:.0f} s : dans les {WIN:.0f} s qui suivent le début de la pression (même période), l'équipe qui presse a une action de contrôle du ballon : récupération réussie, interception gagnée, tacle gagné, ou passe/conduite/dribble/tir dans le jeu (hors coups de pied arrêtés). Ce n'est pas forcément le joueur lui-même qui récupère.",
        regain5_newposs="Variante plus stricte : une nouvelle possession StatsBomb de l'équipe qui presse démarre dans les 5 s, hors reprises arrêtées (touche, coup franc, corner, sortie de but, engagement).",
        own_regain5="Idem, mais le premier événement de la nouvelle possession est fait par le joueur qui pressait.",
        counterpress="Pression marquée 'counterpress' par StatsBomb : pression dans les 5 s qui suivent une perte de balle de l'équipe.",
        mean_x="Position moyenne des pressions le long du terrain, en mètres depuis la ligne de but de l'équipe qui presse (terrain StatsBomb 120 yards = 109,7 m ; moitié = 54,9 m).",
    ),
    n_forwards=N, sinayoko=dict(minutes=round(float(sin.minutes), 1), matches=int(sin.matches), pressures=int(sin.pressures),
                                opp_half=int(sin.opp_half), regains5=int(sin.regains5), regains5_newposs=int(sin.regains5_np), own_regains5=int(sin.own_regains5),
                                counterpress=int(sin.counterpress), cp_regains5=int(sin.cp_regains5)),
    sinayoko_ranks=ranks,
    sinayoko_ranks_among_centre_forwards=ranks_cf,
    pool_pooled=dict(pressures_p90=round(F.pressures.sum() / F.minutes.sum() * 90, 2), regain_rate=round(F.regains5.sum() / F.pressures.sum(), 3), regain_rate_np=round(F.regains5_np.sum() / F.pressures.sum(), 3),
                     mean_x_m=round(float((pr[pr.player_id.isin(F.player_id)].x).mean() * YD), 1)),
    mali_team=dict(pressures=int(len(mali_pr)), regain_rate=round(float(mali_pr.regain5.mean()), 3),
                   sinayoko_share_of_mali_pressures=round(float((mali_pr.player == 'Lassine Sinayoko').mean()), 3)),
    pressures_on_own_possession=int((~pr.on_opp_ball).sum()),
    table=table,
)
save('t14.json', out)
if __name__ == '__main__':
    import pprint; pprint.pprint({k: out[k] for k in out if k not in ('table', 'definitions')}, width=160)
    print(pd.DataFrame(table).head(15).to_string())

# ajustement à la possession adverse (proxy : part des passes de l'adversaire dans les matchs du joueur, pondérée par ses minutes)
PM = d['PM']
pas = E[E.type == 'Pass'].groupby(['match_id', 'team']).size().rename('n').reset_index()
tot = pas.groupby('match_id').n.sum()
pas['share'] = pas.n / pas.match_id.map(tot)
pm = PM[PM.player_id.isin(F.player_id)].merge(pas[['match_id', 'team', 'share']], on=['match_id', 'team'])
w = pm.groupby('player_id').apply(lambda g: ((1 - g.share) * g.minutes).sum() / g.minutes.sum(), include_groups=False)
F['opp_pass_share'] = F.player_id.map(w)
F['pressures_p90_padj'] = F.pressures_p90 * 0.5 / F.opp_pass_share
F['opp_half_p90_padj'] = F.opp_half_p90 * 0.5 / F.opp_pass_share
sin = F[F.player == 'Lassine Sinayoko'].iloc[0]
out['possession_adjusted'] = dict(
    definition="Par 90 minutes ramené à une possession adverse de 50 % : valeur x 0,5 / part des passes adverses dans les matchs du joueur (pondérée par ses minutes).",
    sinayoko_opp_pass_share=round(float(sin.opp_pass_share), 3),
    **{c: dict(value=round(float(sin[c]), 2), rank=int((F[c] > sin[c]).sum() + 1), n=N, median=round(float(F[c].median()), 2)) for c in ['pressures_p90_padj', 'opp_half_p90_padj']})
save('t14.json', out)
if __name__ == '__main__':
    print(out['possession_adjusted'])

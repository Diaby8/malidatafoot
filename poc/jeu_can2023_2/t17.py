"""T17 — Par où attaque le Mali ? Entrées dans le dernier tiers par couloir."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

d = load(); E, M, PM, P = d['E'], d['M'], d['PM'], d['P']
MIN_MIN_MALI = 90

# 1) vérification de la convention y : position moyenne des actions des joueurs de gauche et de droite
chk = {}
for pos in ['Left Back', 'Right Back', 'Left Wing', 'Right Wing', 'Left Center Back', 'Right Center Back', 'Left Midfield', 'Right Midfield']:
    s = E[(E.position == pos) & E.y.notna() & E.type.isin(['Pass', 'Carry', 'Ball Receipt*'])]
    chk[pos] = dict(mean_y=round(float(s.y.mean()), 1), n=int(len(s)))
# repère : y en 0..80, attaque vers x=120 ; un joueur de gauche a un y moyen faible => y < 26,67 = couloir gauche vu de l'attaquant
assert chk['Left Back']['mean_y'] < 30 and chk['Right Back']['mean_y'] > 50

comp_pass = (E.type == 'Pass') & E.pass_outcome.isna() & ~E.pass_type.isin(SET_PIECE_PASS)
carry = E.type == 'Carry'
ent = E[(comp_pass | carry) & (E.x < 80) & (E.ex >= 80)].copy()
W = 80 / 3


def lane(y):
    return np.where(y < W, 'gauche', np.where(y <= 2 * W, 'centre', 'droite'))


ent['lane_end'] = lane(ent.ey)  # couloir d'arrivée (définition principale)
# couloir au moment de franchir la ligne x=80 (interpolation linéaire)
f = (80 - ent.x) / (ent.ex - ent.x)
ent['y80'] = ent.y + f * (ent.ey - ent.y)
ent['lane_cross'] = lane(ent.y80)
ent['lane_start'] = lane(ent.y)
ent['kind'] = np.where(ent.type == 'Pass', 'passe', 'conduite')

TM = team_minutes(M).groupby('team').minutes.sum()
rows = []
for t, g in ent.groupby('team'):
    r = dict(team=t, entries=int(len(g)), entries_p90=round(len(g) / TM[t] * 90, 2), minutes=int(TM[t]))
    for k in ['lane_end', 'lane_cross']:
        vc = g[k].value_counts(normalize=True)
        for l in ['gauche', 'centre', 'droite']:
            r[f'{k}_{l}'] = round(float(vc.get(l, 0)), 3)
    r['carry_share'] = round(float((g.kind == 'conduite').mean()), 3)
    r['right_minus_left'] = round(r['lane_end_droite'] - r['lane_end_gauche'], 3)
    rows.append(r)
T = pd.DataFrame(rows)
avg = {c: round(float(T[c].mean()), 3) for c in T.columns if c.startswith('lane_')}
pooled = ent.lane_end.value_counts(normalize=True).round(3).to_dict()
mali = T[T.team == 'Mali'].iloc[0].to_dict()
rk = {}
for c in ['lane_end_droite', 'lane_end_gauche', 'lane_end_centre', 'right_minus_left', 'lane_cross_droite', 'entries_p90']:
    rk[c] = dict(value=mali[c], rank=int((T[c] > mali[c]).sum() + 1), n=len(T), mean=round(float(T[c].mean()), 3),
                 sd=round(float(T[c].std()), 3), max=float(T[c].max()), leader=T.loc[T[c].idxmax(), 'team'])
# bootstrap par match : incertitude sur la part droite du Mali
mg = ent[ent.team == 'Mali']
rng = np.random.default_rng(0)
mids = mg.match_id.unique()
bs = []
for _ in range(5000):
    pick = rng.choice(mids, len(mids))
    s = pd.concat([mg[mg.match_id == m] for m in pick])
    bs.append(((s.lane_end == 'droite').mean(), (s.lane_end == 'gauche').mean()))
bs = np.array(bs)
per_match = mg.groupby('match_id').lane_end.value_counts().unstack(fill_value=0)
per_match = per_match.merge(M[['match_id', 'home', 'away']], left_index=True, right_on='match_id').to_dict('records')
# joueurs maliens
mins = PM[PM.team == 'Mali'].groupby('player').minutes.sum()
pl = mg.groupby(['player', 'lane_end']).size().unstack(fill_value=0)
pl['total'] = pl.sum(axis=1)
pl = pl.join(mins.rename('minutes'))
for l in ['gauche', 'centre', 'droite', 'total']:
    pl[f'{l}_p90'] = pl[l] / pl.minutes * 90
pl['share_of_mali_right'] = pl['droite'] / pl['droite'].sum()
pl['share_of_mali_left'] = pl['gauche'] / pl['gauche'].sum()
pl['share_of_mali_total'] = pl['total'] / pl['total'].sum()
plq = pl[pl.minutes >= MIN_MIN_MALI].round(3)
# Hamari Traoré : ses entrées par couloir et type
ht = mg[mg.player == 'Hamari Traoré']
out = dict(
    definitions=dict(
        y_convention="StatsBomb : terrain 120 x 80 yards, origine en haut à gauche, chaque événement dans le repère de l'équipe qui agit (attaque vers x=120). y croît vers la droite de l'attaquant : vérifié par le y moyen des actions des latéraux gauches (petit y) et droits (grand y), voir y_check.",
        entry="Entrée dans le dernier tiers : passe réussie dans le jeu (hors corner, coup franc, touche, sortie de but, engagement) ou conduite de balle qui part de x<80 et finit à x>=80 (x en yards ; 80 yards = 73,2 m).",
        lanes="Trois couloirs égaux de 26,7 yards (24,4 m) de large : gauche y<26,67, centre 26,67<=y<=53,33, droite y>53,33, vus de l'équipe qui attaque. Définition principale : couloir du point d'arrivée de la passe ou de la conduite ; variante : couloir au franchissement de la ligne x=80 (interpolation).",
        tournament_average="Moyenne simple des parts des 24 équipes ('team_mean') ; part de toutes les entrées regroupées ('pooled').",
        players=f"Joueurs maliens avec au moins {MIN_MIN_MALI} minutes ; entrées par 90 minutes (horloge réglementaire) selon le couloir d'arrivée.",
    ),
    y_check=chk, n_entries_total=int(len(ent)), team_mean=avg, pooled=pooled, mali=mali, mali_ranks=rk,
    mali_bootstrap_by_match=dict(right_share_ci95=[round(float(np.percentile(bs[:, 0], 2.5)), 3), round(float(np.percentile(bs[:, 0], 97.5)), 3)],
                                 left_share_ci95=[round(float(np.percentile(bs[:, 1], 2.5)), 3), round(float(np.percentile(bs[:, 1], 97.5)), 3)],
                                 n_matches=int(len(mids))),
    mali_per_match=per_match,
    mali_players=plq.sort_values('total_p90', ascending=False).reset_index().to_dict('records'),
    hamari_traore=dict(entries=int(len(ht)), by_lane=ht.lane_end.value_counts().to_dict(), by_kind=ht.kind.value_counts().to_dict(),
                       share_of_mali_right=round(float((ht.lane_end == 'droite').sum() / (mg.lane_end == 'droite').sum()), 3)),
    teams=T.sort_values('right_minus_left', ascending=False).to_dict('records'),
)
save('t17.json', out)
if __name__ == '__main__':
    import pprint
    pprint.pprint({k: out[k] for k in ['y_check', 'n_entries_total', 'team_mean', 'pooled', 'mali', 'mali_ranks', 'mali_bootstrap_by_match', 'hamari_traore']}, width=170)
    print(pd.DataFrame(out['mali_players'])[['player', 'minutes', 'gauche', 'centre', 'droite', 'total', 'gauche_p90', 'centre_p90', 'droite_p90', 'share_of_mali_right', 'share_of_mali_left']].to_string())
    print(T.sort_values('right_minus_left', ascending=False)[['team', 'entries', 'entries_p90', 'lane_end_gauche', 'lane_end_centre', 'lane_end_droite', 'lane_cross_gauche', 'lane_cross_centre', 'lane_cross_droite']].to_string())
    print(pd.DataFrame(per_match))

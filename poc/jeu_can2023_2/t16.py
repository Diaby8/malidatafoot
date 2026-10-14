"""T16 — Jouer à 11 contre 10, un vrai avantage ?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *

d = load(); E, M = d['E'], d['M']
LAST = 120  # secondes : cartons dans les 2 dernières minutes (temps réel avant le coup de sifflet final) ignorés
REDS = E[E.card.isin(['Red Card', 'Second Yellow'])].sort_values(['match_id', 't_match'])

op = ~E.pass_type.isin(SET_PIECE_PASS)
comp = (E.type == 'Pass') & E.pass_outcome.isna()
E = E.assign(
    is_pass=E.type == 'Pass',
    np_shot=(E.type == 'Shot') & (E.shot_type != 'Penalty'),
    npxg=np.where((E.type == 'Shot') & (E.shot_type != 'Penalty'), E.shot_xg.fillna(0), 0.0),
    pen=(E.type == 'Shot') & (E.shot_type == 'Penalty'),
    f3=comp & op & (E.x < 80) & (E.ex >= 80),
    box=comp & op & ~in_box(E.x, E.y) & in_box(E.ex, E.ey),
    goal=((E.type == 'Shot') & (E.shot_outcome == 'Goal')) | (E.type == 'Own Goal For'),
)


def window(mid, t0, t1, team, opp):
    g = E[(E.match_id == mid) & (E.t_match >= t0) & (E.t_match < t1)]
    a, b = g[g.team == team], g[g.team == opp]
    r = dict(minutes=(t1 - t0) / 60)
    for k, s in (('for', a), ('against', b)):
        r[f'passes_{k}'] = int(s.is_pass.sum()); r[f'np_shots_{k}'] = int(s.np_shot.sum()); r[f'npxg_{k}'] = float(s.npxg.sum())
        r[f'pens_{k}'] = int(s.pen.sum()); r[f'f3_{k}'] = int(s.f3.sum()); r[f'box_{k}'] = int(s.box.sum()); r[f'goals_{k}'] = int(s.goal.sum())
    r['pass_share'] = r['passes_for'] / max(1, r['passes_for'] + r['passes_against'])
    return r


cases, skipped = [], []
for mid, g in REDS.groupby('match_id'):
    m = M[M.match_id == mid].iloc[0]
    end = m.real_len * 60
    first_red_t = g.t_match.min()
    for r in g.itertuples():
        if r.t_match > end - LAST:
            skipped.append(dict(match=f"{m.home} {m.hs}-{m.as_} {m.away}", minute=f"{r.minute + 1}'", team=r.team, player=r.player, reason='2 dernières minutes')); continue
        if r.t_match > first_red_t:
            skipped.append(dict(match=f"{m.home} {m.hs}-{m.as_} {m.away}", minute=f"{r.minute + 1}'", team=r.team, player=r.player, reason="pas un 11 contre 10 (deuxième rouge du match : 10 contre 10)")); continue
        adv = m.away if r.team == m.home else m.home
        later = g[g.t_match > r.t_match]
        t_end = later.t_match.min() if len(later) else end
        before = window(mid, 0, r.t_match, adv, r.team)
        after = window(mid, r.t_match, t_end, adv, r.team)
        # score au moment du carton (vu de l'équipe en supériorité)
        gl = E[(E.match_id == mid) & E.goal & (E.t_match < r.t_match)]
        sc_for, sc_ag = int((gl.team == adv).sum()), int((gl.team == r.team).sum())
        fin_for = m.hs if adv == m.home else m.as_; fin_ag = m.as_ if adv == m.home else m.hs
        cases.append(dict(match=f"{m.home} {m.hs}-{m.as_} {m.away}", stage=m.stage, match_id=int(mid), card_minute=f"{r.minute + 1}'",
                          card=r.card, sent_off=f"{r.player} ({r.team})", team_extra_man=adv,
                          score_at_card=f"{sc_for}-{sc_ag}", final_score=f"{fin_for}-{fin_ag}",
                          after_ends=('autre rouge' if len(later) else 'fin du match') + f" ({(t_end - r.t_match) / 60:.1f} min réelles)",
                          before=before, after=after))


def per90(ws):
    mins = sum(w['minutes'] for w in ws)
    o = dict(minutes=round(mins, 1))
    for k in ['np_shots', 'npxg', 'f3', 'box', 'goals', 'pens']:
        for s in ('for', 'against'):
            o[f'{k}_{s}_p90'] = round(sum(w[f'{k}_{s}'] for w in ws) / mins * 90, 3)
            o[f'{k}_{s}_total'] = round(sum(w[f'{k}_{s}'] for w in ws), 3)
    o['pass_share'] = round(sum(w['passes_for'] for w in ws) / sum(w['passes_for'] + w['passes_against'] for w in ws), 3)
    o['npxg_per_shot_for'] = round(o['npxg_for_total'] / max(1, o['np_shots_for_total']), 3)
    o['box_per_f3_for'] = round(o['box_for_total'] / max(1, o['f3_for_total']), 3)
    return o


agg = dict(before=per90([c['before'] for c in cases]), after=per90([c['after'] for c in cases]))
for c in cases:
    for w in ('before', 'after'):
        x = c[w]; mins = x['minutes']
        for k in ['np_shots', 'npxg', 'f3', 'box', 'goals']:
            for s in ('for', 'against'):
                x[f'{k}_{s}_p90'] = round(x[f'{k}_{s}'] / mins * 90, 2)
        x['minutes'] = round(mins, 1); x['npxg_for'] = round(x['npxg_for'], 3); x['npxg_against'] = round(x['npxg_against'], 3); x['pass_share'] = round(x['pass_share'], 3)
cnt = dict(n_cases=len(cases),
           score_state_at_card=dict(menait=sum(int(c['score_at_card'].split('-')[0]) > int(c['score_at_card'].split('-')[1]) for c in cases),
                                    egalite=sum(int(c['score_at_card'].split('-')[0]) == int(c['score_at_card'].split('-')[1]) for c in cases),
                                    menee=sum(int(c['score_at_card'].split('-')[0]) < int(c['score_at_card'].split('-')[1]) for c in cases)),
           pass_share_up=sum(c['after']['pass_share'] > c['before']['pass_share'] for c in cases),
           npxg_for_p90_up=sum(c['after']['npxg_for_p90'] > c['before']['npxg_for_p90'] for c in cases),
           shots_for_p90_up=sum(c['after']['np_shots_for_p90'] > c['before']['np_shots_for_p90'] for c in cases),
           box_for_p90_up=sum(c['after']['box_for_p90'] > c['before']['box_for_p90'] for c in cases),
           f3_for_p90_up=sum(c['after']['f3_for_p90'] > c['before']['f3_for_p90'] for c in cases),
           npxg_against_p90_down=sum(c['after']['npxg_against_p90'] < c['before']['npxg_against_p90'] for c in cases),
           scored_after=sum(c['after']['goals_for'] > 0 for c in cases), conceded_after=sum(c['after']['goals_against'] > 0 for c in cases),
           goal_diff_after=sum(c['after']['goals_for'] - c['after']['goals_against'] for c in cases))
# sans Mali–Côte d'Ivoire et sans le cas Namibie (fenêtre courte) : robustesse
rob = {}
for name, filt in {'sans_Mali_CIV': lambda c: c['match_id'] != 3922659,
                   'sans_Angola_Namibia': lambda c: c['match_id'] != 3922237,
                   'apres_au_moins_20min': lambda c: c['after']['minutes'] >= 20}.items():
    sub = [c for c in cases if filt(c)]
    rob[name] = dict(n=len(sub), before=per90([c['before'] for c in sub]), after=per90([c['after'] for c in sub]))
out = dict(
    definitions=dict(
        cases="Rouge direct ou second jaune (foul_committed.card ou bad_behaviour.card). Ignorés : cartons dans les 2 dernières minutes réelles du match, et deuxième rouge d'un match (il ne crée pas un 11 contre 10).",
        windows="Avant = du coup d'envoi au carton (11 contre 11, même match). Après = du carton au coup de sifflet final (prolongation comprise, tirs au but exclus) ou au rouge suivant. Durées en temps réellement écoulé (arrêts de jeu compris), d'où des 'par 90' calculés sur le temps réel.",
        metrics="Possession = part des passes tentées. Tirs et xG hors penalty (penalties comptés à part). Passes réussies vers le dernier tiers : départ x<80, arrivée x>=80. Passes réussies dans la surface : départ hors surface, arrivée dans la surface (x>=102, 18<=y<=62). Ces deux mesures excluent les coups de pied arrêtés (corner, coup franc, touche, sortie de but, engagement). Buts = tous les buts (penalties et contre-son-camp compris).",
        aggregate="Agrégat pondéré par les minutes : somme des totaux / somme des minutes x 90 (possession : somme des passes).",
        side="'for' = équipe en supériorité numérique, 'against' = équipe réduite à 10.",
    ),
    aggregate=agg, counts=cnt, robustness=rob, cases=cases, skipped=skipped,
)
save('t16.json', out)
if __name__ == '__main__':
    import pprint
    for c in cases:
        b, a = c['before'], c['after']
        print(f"{c['match']:42s} {c['card_minute']:5s} +1:{c['team_extra_man']:14s} score {c['score_at_card']} -> {c['final_score']} | {c['after_ends']:28s} "
              f"poss {b['pass_share']:.2f}->{a['pass_share']:.2f} shots90 {b['np_shots_for_p90']:.1f}->{a['np_shots_for_p90']:.1f} xg90 {b['npxg_for_p90']:.2f}->{a['npxg_for_p90']:.2f} "
              f"box90 {b['box_for_p90']:.1f}->{a['box_for_p90']:.1f} f3 {b['f3_for_p90']:.1f}->{a['f3_for_p90']:.1f} G {a['goals_for']}-{a['goals_against']} xgA {b['npxg_against_p90']:.2f}->{a['npxg_against_p90']:.2f}")
    pprint.pprint(agg, width=200); pprint.pprint(cnt); pprint.pprint(skipped)
    for k, v in rob.items(): print(k, v['n'], {x: (v['before'][x], v['after'][x]) for x in ['pass_share', 'np_shots_for_p90', 'npxg_for_p90', 'box_for_p90', 'goals_for_p90', 'goals_against_p90', 'npxg_against_p90', 'npxg_per_shot_for']})

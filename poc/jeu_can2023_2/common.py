"""Chargement commun CAN 2023 (StatsBomb open data), lecture seule du dépôt.

Conventions :
- Séance de tirs au but (period 5) exclue partout.
- Minutes de jeu : horloge réglementaire (45/45/15/15, arrêts de jeu ramenés à la fin de leur période),
  reconstruites depuis Starting XI + Substitution + expulsions (même règle que malidata/silver.py),
  recoupées avec silver/player_match_minutes.parquet.
- Coordonnées StatsBomb : 120 x 80 yards, chaque événement dans le repère de l'équipe qui agit (attaque vers x=120).
- Distances converties en mètres : yards x 0.9144.
"""
import json, os, pickle
import pandas as pd

B = '/home/claude/repo/malidatafoot/data/bronze'
OUT = os.path.dirname(os.path.abspath(__file__))
YD = 0.9144
FWD_POS = {'Center Forward', 'Left Center Forward', 'Right Center Forward', 'Secondary Striker', 'Left Wing', 'Right Wing'}
SET_PIECE_PASS = {'Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off'}


def ts(s):
    h, m, r = s.split(':')
    return int(h) * 3600 + int(m) * 60 + float(r)


def _n(o, k='name'):
    return o.get(k) if o else None


def load():
    cache = os.path.join(OUT, 'cache.pkl')
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))
    matches = json.load(open(f'{B}/matches/1267/107.json'))
    rows, mrows, xi = [], [], []
    for m in matches:
        mid = m['match_id']
        ev = json.load(open(f'{B}/events/{mid}.json'))
        ev = [e for e in ev if e['period'] <= 4]
        plen = {}
        for e in ev:
            plen[e['period']] = max(plen.get(e['period'], 0), ts(e['timestamp']))
        offs = {p: sum(plen[q] for q in plen if q < p) for p in plen}
        last = max(plen)
        mrows.append(dict(match_id=mid, home=m['home_team']['home_team_name'], away=m['away_team']['away_team_name'],
                          hs=m['home_score'], as_=m['away_score'], stage=m['competition_stage']['name'],
                          date=m['match_date'], last_period=last, reg_len=120 if last >= 3 else 90,
                          real_len=sum(plen.values()) / 60))
        for e in ev:
            t = e['type']['name']
            p, s, c = e.get('pass') or {}, e.get('shot') or {}, e.get('carry') or {}
            loc = e.get('location') or [None, None]
            end = p.get('end_location') or s.get('end_location') or c.get('end_location') or [None, None]
            card = _n((e.get('foul_committed') or {}).get('card')) or _n((e.get('bad_behaviour') or {}).get('card'))
            per, tt = e['period'], ts(e['timestamp'])
            reg = {1: 0, 2: 2700, 3: 5400, 4: 6300}[per] + min(tt, 2700 if per <= 2 else 900)
            if t == 'Starting XI':
                for pl in e['tactics']['lineup']:
                    xi.append(dict(match_id=mid, team=e['team']['name'], player_id=pl['player']['id'],
                                   player=pl['player']['name'], position=pl['position']['name']))
            rows.append(dict(
                match_id=mid, id=e['id'], idx=e['index'], period=per, t=tt, t_match=tt + offs[per], t_reg=reg,
                minute=e['minute'], second=e['second'], type=t, team=e['team']['name'],
                player_id=_n(e.get('player'), 'id'), player=_n(e.get('player')), position=_n(e.get('position')),
                poss=e['possession'], poss_team=e['possession_team']['name'], pp=e['play_pattern']['name'],
                x=loc[0], y=loc[1], ex=end[0], ey=end[1], duration=e.get('duration'),
                counterpress=bool(e.get('counterpress', False)), under_pressure=bool(e.get('under_pressure', False)),
                pass_type=_n(p.get('type')), pass_outcome=_n(p.get('outcome')), pass_recipient_id=_n(p.get('recipient'), 'id'),
                pass_shot_assist=bool(p.get('shot_assist')), pass_goal_assist=bool(p.get('goal_assist')),
                pass_cross=bool(p.get('cross')),
                shot_xg=s.get('statsbomb_xg'), shot_outcome=_n(s.get('outcome')), shot_type=_n(s.get('type')),
                shot_key_pass_id=s.get('key_pass_id'), shot_body=_n(s.get('body_part')),
                shot_first_time=bool(s.get('first_time')),
                card=card, sub_replacement_id=_n((e.get('substitution') or {}).get('replacement'), 'id'),
                sub_replacement=_n((e.get('substitution') or {}).get('replacement')),
                recovery_failure=bool((e.get('ball_recovery') or {}).get('recovery_failure')),
                duel_type=_n((e.get('duel') or {}).get('type')), duel_outcome=_n((e.get('duel') or {}).get('outcome')),
                interception_outcome=_n((e.get('interception') or {}).get('outcome')),
                related=e.get('related_events') or [],
            ))
    E = pd.DataFrame(rows).sort_values(['match_id', 'idx']).reset_index(drop=True)
    M = pd.DataFrame(mrows)
    XI = pd.DataFrame(xi)
    # minutes par joueur-match (horloge réglementaire)
    ins = [dict(match_id=r.match_id, team=r.team, player_id=r.player_id, player=r.player, r_in=0.0, t_in=0.0)
           for r in XI.itertuples()]
    subs = E[E.type == 'Substitution']
    ins += [dict(match_id=r.match_id, team=r.team, player_id=r.sub_replacement_id, player=r.sub_replacement,
                 r_in=r.t_reg, t_in=r.t_match) for r in subs.itertuples()]
    I = pd.DataFrame(ins)
    outs = E[(E.type == 'Substitution') | E.card.isin(['Red Card', 'Second Yellow'])]
    O = outs.groupby(['match_id', 'player_id']).agg(r_out=('t_reg', 'min'), t_out=('t_match', 'min')).reset_index()
    PM = I.merge(O, on=['match_id', 'player_id'], how='left').merge(M[['match_id', 'reg_len', 'real_len']], on='match_id')
    PM['r_out'] = PM.r_out.fillna(PM.reg_len * 60)
    PM['t_out'] = PM.t_out.fillna(PM.real_len * 60)
    PM['minutes'] = (PM.r_out - PM.r_in) / 60
    PM = PM.drop(columns=['reg_len', 'real_len'])
    # poste principal : poste où le joueur a le plus d'actions (événements avec position), hors 'Substitute'
    pos = E[E.position.notna() & (E.position != 'Substitute') & E.player_id.notna()].groupby(['player_id', 'position']).size().rename('n').reset_index()
    tot = pos.groupby('player_id').n.sum()
    top = pos.sort_values('n', ascending=False).drop_duplicates('player_id').set_index('player_id')
    P = PM.groupby(['player_id', 'player', 'team']).agg(minutes=('minutes', 'sum'), matches=('match_id', 'nunique')).reset_index()
    P['main_pos'] = P.player_id.map(top.position)
    P['main_pos_share'] = P.player_id.map(top.n / tot)
    # part des actions faites à un poste d'attaquant (avant-centre ou ailier)
    fw = pos[pos.position.isin(FWD_POS)].groupby('player_id').n.sum()
    P['fwd_share'] = P.player_id.map(fw / tot).fillna(0)
    res = dict(E=E, M=M, XI=XI, PM=PM, P=P)
    pickle.dump(res, open(cache, 'wb'))
    return res


def team_minutes(M):
    """Minutes réglementaires jouées par chaque équipe (90 ou 120 par match)."""
    rows = []
    for r in M.itertuples():
        rows += [dict(team=r.home, match_id=r.match_id, minutes=r.reg_len), dict(team=r.away, match_id=r.match_id, minutes=r.reg_len)]
    return pd.DataFrame(rows)


def in_box(x, y):
    return (x >= 102) & (y >= 18) & (y <= 62)


def save(name, obj):
    def conv(o):
        if hasattr(o, 'item'):
            return o.item()
        raise TypeError(type(o))
    json.dump(obj, open(os.path.join(OUT, name), 'w'), ensure_ascii=False, indent=1, default=conv)

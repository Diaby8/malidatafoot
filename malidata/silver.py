"""Étape 2 — SILVER : des fichiers bruts aux tables propres et typées.

Un événement StatsBomb est un objet imbriqué dont la forme dépend de son type
(passe, tir, duel…). On l'aplatit ici en une ligne par événement, avec des colonnes
stables, puis on reconstruit le temps de jeu de chaque joueur.

Choix d'ingénierie : le temps de jeu est recalculé à partir des événements
(titularisations, remplacements, expulsions) et non du fichier des compositions,
dont les plages horaires sont incohérentes sur plusieurs matchs.

Convention des minutes : celle de tous les sites de statistiques. Un match entier vaut 90 minutes
(120 avec prolongation), les arrêts de jeu ne s'ajoutent pas. On garde à côté le temps réellement
écoulé (minutes_reelles), utile pour dessiner une chronologie.
"""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from .config import Config, get_logger

log = get_logger("silver")

AERIAL_PARENTS = ("clearance", "miscontrol", "pass", "shot")


def _name(obj: dict | None, key: str = "name"):
    return obj.get(key) if obj else None


def _seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def flatten_event(match_id: int, e: dict) -> dict:
    """Une ligne à plat pour un événement, quel que soit son type."""
    loc = e.get("location") or [None, None]
    p, s, c = e.get("pass") or {}, e.get("shot") or {}, e.get("carry") or {}
    end = p.get("end_location") or s.get("end_location") or c.get("end_location") or [None, None]
    card = _name((e.get("foul_committed") or {}).get("card")) or _name((e.get("bad_behaviour") or {}).get("card"))
    sub = e.get("substitution") or {}
    return {
        "match_id": match_id,
        "event_id": e["id"],
        "idx": e["index"],
        "period": e["period"],
        "ts": _seconds(e["timestamp"]),
        "minute": e["minute"],
        "second": e["second"],
        "type": e["type"]["name"],
        "team": e["team"]["name"],
        "player_id": _name(e.get("player"), "id"),
        "player": _name(e.get("player")),
        "position": _name(e.get("position")),
        "possession": e["possession"],
        "possession_team": e["possession_team"]["name"],
        "play_pattern": e["play_pattern"]["name"],
        "x": loc[0],
        "y": loc[1],
        "end_x": end[0],
        "end_y": end[1],
        "duration": e.get("duration"),
        "under_pressure": bool(e.get("under_pressure", False)),
        "counterpress": bool(e.get("counterpress", False)),
        "pass_recipient_id": _name(p.get("recipient"), "id"),
        "pass_length": p.get("length"),
        "pass_height": _name(p.get("height")),
        "pass_type": _name(p.get("type")),
        "pass_outcome": _name(p.get("outcome")),  # vide = passe réussie
        "pass_shot_assist": bool(p.get("shot_assist", False)),
        "pass_goal_assist": bool(p.get("goal_assist", False)),
        "pass_assisted_shot_id": p.get("assisted_shot_id"),
        "pass_cross": bool(p.get("cross", False)),
        "shot_xg": s.get("statsbomb_xg"),
        "shot_outcome": _name(s.get("outcome")),
        "shot_type": _name(s.get("type")),
        "shot_body_part": _name(s.get("body_part")),
        "dribble_outcome": _name((e.get("dribble") or {}).get("outcome")),
        "duel_type": _name((e.get("duel") or {}).get("type")),
        "duel_outcome": _name((e.get("duel") or {}).get("outcome")),
        "interception_outcome": _name((e.get("interception") or {}).get("outcome")),
        "recovery_failure": bool((e.get("ball_recovery") or {}).get("recovery_failure", False)),
        "receipt_incomplete": _name((e.get("ball_receipt") or {}).get("outcome")) == "Incomplete",   # ballon adressé mais pas contrôlé
        "aerial_won": any((e.get(k) or {}).get("aerial_won", False) for k in AERIAL_PARENTS),
        "card": card,
        "sub_replacement_id": _name(sub.get("replacement"), "id"),
        "sub_replacement": _name(sub.get("replacement")),
    }


def starting_xi(match_id: int, events: list[dict]) -> list[dict]:
    rows = []
    for e in events:
        if e["type"]["name"] == "Starting XI":
            for pl in e["tactics"]["lineup"]:
                rows.append({"match_id": match_id, "team": e["team"]["name"], "player_id": pl["player"]["id"],
                             "player": pl["player"]["name"], "position": pl["position"]["name"],
                             "jersey": pl["jersey_number"], "formation": str(e["tactics"]["formation"])})
    return rows


def build_minutes(con: duckdb.DuckDBPyConnection) -> None:
    """Temps de jeu par joueur et par match, reconstruit depuis les événements.

    Temps écoulé = durée réelle des périodes précédentes + horodatage dans la période
    (le temps additionnel compte, la séance de tirs au but non).
    """
    con.execute("""
    create or replace table silver.period_lengths as
    select match_id, period, max(ts) as length_s
    from silver.events where period <= 4 group by 1, 2;

    create or replace table silver.match_lengths as
    select match_id, sum(length_s) as length_s, max(period) as last_period from silver.period_lengths group by 1;

    create or replace view silver.events_clock as
    select e.*, e.ts + coalesce((select sum(p.length_s) from silver.period_lengths p
                                 where p.match_id = e.match_id and p.period < e.period), 0) as t_match,
           -- horloge réglementaire en secondes : 45 + 45 (+ 15 + 15), les arrêts de jeu sont ramenés à la fin de leur période
           case e.period when 1 then 0 when 2 then 2700 when 3 then 5400 else 6300 end
             + least(e.ts, case when e.period <= 2 then 2700 else 900 end) as t_regl
    from silver.events e where e.period <= 4;

    create or replace table silver.player_match_minutes as
    with ins as (   -- entrées : titulaires à 0, remplaçants à l'heure du changement
        select match_id, team, player_id, player, 0.0 as t_in, 0.0 as r_in, true as started from silver.starting_xi
        union all
        select match_id, team, sub_replacement_id, sub_replacement, t_match, t_regl, false
        from silver.events_clock where type = 'Substitution'
    ),
    outs as (       -- sorties : remplacement ou expulsion (rouge direct ou second jaune)
        select match_id, player_id, min(t_match) as t_out, min(t_regl) as r_out
        from silver.events_clock
        where type = 'Substitution' or card in ('Red Card', 'Second Yellow')
        group by 1, 2
    )
    select i.match_id, i.team, i.player_id, i.player, i.started,
           i.t_in, coalesce(o.t_out, m.length_s) as t_out,
           (coalesce(o.r_out, case when m.last_period >= 3 then 7200 else 5400 end) - i.r_in) / 60.0 as minutes,
           (coalesce(o.t_out, m.length_s) - i.t_in) / 60.0 as minutes_reelles
    from ins i
    join silver.match_lengths m using (match_id)
    left join outs o on o.match_id = i.match_id and o.player_id = i.player_id and o.t_out > i.t_in;
    """)


def run(cfg: Config) -> dict:
    bronze, silver = cfg.path("bronze"), cfg.path("silver")
    raw_matches = json.loads((bronze / f"matches/{cfg.competition_id}/{cfg.season_id}.json").read_text(encoding="utf-8"))

    matches = pd.DataFrame([{
        "match_id": m["match_id"], "match_date": m["match_date"], "kick_off": m["kick_off"],
        "stage": m["competition_stage"]["name"],
        "home_team": m["home_team"]["home_team_name"], "away_team": m["away_team"]["away_team_name"],
        "home_score": m["home_score"], "away_score": m["away_score"],
        "stadium": _name(m.get("stadium")),
    } for m in raw_matches])
    matches["match_date"] = pd.to_datetime(matches["match_date"]).dt.date

    ev_rows, xi_rows, pl_rows = [], [], []
    for mid in matches["match_id"]:
        events = json.loads(Path(bronze / f"events/{mid}.json").read_text(encoding="utf-8"))
        ev_rows.extend(flatten_event(mid, e) for e in events)
        xi_rows.extend(starting_xi(mid, events))
        for team in json.loads(Path(bronze / f"lineups/{mid}.json").read_text(encoding="utf-8")):
            for p in team["lineup"]:
                pl_rows.append({"player_id": p["player_id"], "player": p["player_name"],
                                "nickname": p.get("player_nickname"), "team": team["team_name"]})

    events = pd.DataFrame(ev_rows)
    for col in ("player_id", "pass_recipient_id", "sub_replacement_id"):
        events[col] = events[col].astype("Int64")
    xi = pd.DataFrame(xi_rows)
    players = pd.DataFrame(pl_rows).drop_duplicates("player_id")
    players["display_name"] = players["nickname"].fillna(players["player"])

    con = duckdb.connect(str(cfg.path("warehouse")))
    con.execute("create schema if not exists silver")
    for name, df in {"matches": matches, "events": events, "starting_xi": xi, "players": players}.items():
        con.register("df_tmp", df)
        con.execute(f"create or replace table silver.{name} as select * from df_tmp")
        con.unregister("df_tmp")
        con.execute(f"copy silver.{name} to '{silver / (name + '.parquet')}' (format parquet)")
    build_minutes(con)
    con.execute(f"copy silver.player_match_minutes to '{silver / 'player_match_minutes.parquet'}' (format parquet)")
    stats = {
        "matches": len(matches), "events": len(events), "players": len(players),
        "player_matches": con.execute("select count(*) from silver.player_match_minutes").fetchone()[0],
    }
    con.close()
    log.info("silver : %(matches)d matchs, %(events)d événements, %(players)d joueurs", stats)
    return stats

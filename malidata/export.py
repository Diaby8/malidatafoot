"""Exporte un résumé JSON des résultats : c'est le fichier que lisent les visuels et la vidéo."""
from __future__ import annotations

import json

import duckdb

from .config import Config, get_logger

log = get_logger("export")


def pass_network(con: duckdb.DuckDBPyConnection, match_id: int, team: str) -> dict:
    """Positions moyennes et liaisons de passes du onze de départ, jusqu'au premier changement."""
    t_end = con.execute("""select coalesce(min(t_match), 1e9) from silver.events_clock
                           where match_id = ? and team = ? and type = 'Substitution'""", [match_id, team]).fetchone()[0]
    nodes = con.execute("""
        select e.player_id, p.display_name as player, avg(e.x) as x, avg(e.y) as y, count(*) as passes, any_value(x.position) as poste
        from silver.events_clock e join silver.players p using (player_id)
        left join silver.starting_xi x on x.match_id = e.match_id and x.player_id = e.player_id
        where e.match_id = ? and e.team = ? and e.type = 'Pass' and e.t_match < ?
        group by 1, 2 order by 1""", [match_id, team, t_end]).df()
    edges = con.execute("""
        select least(player_id, pass_recipient_id) as a, greatest(player_id, pass_recipient_id) as b, count(*) as n,
               sum(case when end_x - x >= 10 then 1 else 0 end)::int as avant   -- passes qui gagnent au moins 10 yards (9 m) vers le but adverse
        from silver.events_clock
        where match_id = ? and team = ? and type = 'Pass' and pass_outcome is null
          and pass_recipient_id is not null and t_match < ?
        group by 1, 2 having count(*) >= 4 order by 1, 2""", [match_id, team, t_end]).df()
    # minute affichée, sur l'horloge du match (61:21 = 62e minute), à ne pas confondre avec le temps écoulé
    clock = con.execute("""select min(minute) + 1 from silver.events where match_id = ? and team = ? and type = 'Substitution'""", [match_id, team]).fetchone()[0]
    return {"until_min": round(min(t_end, 1e9) / 60, 1), "until_clock": int(clock) if clock else None, "nodes": nodes.round(2).to_dict("records"), "edges": edges.to_dict("records")}


def part_passes(con: duckdb.DuckDBPyConnection, match_id: int, team: str) -> dict:
    """Part des passes tentées par l'équipe sur le match, et avant / après le premier carton rouge adverse s'il y en a un."""
    rouge = con.execute("""select min(t_match) from silver.events_clock where match_id = ? and team <> ?
                             and card in ('Red Card', 'Second Yellow')""", [match_id, team]).fetchone()[0]
    part = lambda cond, *a: con.execute(f"""select round(100.0 * sum(case when team = ? then 1 else 0 end) / count(*), 1)
        from silver.events_clock where match_id = ? and type = 'Pass' and {cond}""", [team, match_id, *a]).fetchone()[0]  # noqa: E731
    out = {"match": part("true")}
    if rouge is not None:
        out.update(avant_rouge=part("t_match < ?", rouge), apres_rouge=part("t_match >= ?", rouge))
    return out


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    team = cfg.team
    rec = lambda sql, *a: json.loads(con.execute(sql, list(a)).df().to_json(orient="records", date_format="iso"))  # noqa: E731

    matches = rec("""select match_id, match_date, stage, opponent, goals_for, goals_against, shots, shots_on_target,
                            round(xg, 2) as xg, round(xg_against, 2) as xg_against, round(possession_pct, 1) as possession_pct,
                            round(field_tilt_pct, 1) as field_tilt_pct, round(ppda, 2) as ppda, round(pass_pct, 1) as pass_pct
                     from gold.team_match_stats where team = ? order by match_date""", team)
    labels = cfg.raw.get("team_labels", {})
    for m in matches:
        m["opponent"] = labels.get(m["opponent"], m["opponent"])
    last = matches[-1]
    data = {
        "source": "StatsBomb Open Data — Coupe d'Afrique des Nations 2023",
        "volumes": {
            "fichiers_bruts": len(json.loads((cfg.path("bronze") / "_manifest.json").read_text())),
            "matchs": con.execute("select count(*) from silver.matches").fetchone()[0],
            "evenements": con.execute("select count(*) from silver.events").fetchone()[0],
            "joueurs": con.execute("select count(*) from silver.players").fetchone()[0],
            "joueurs_classes": con.execute("select count(*) from gold.player_scores").fetchone()[0],
            "evenements_equipe": con.execute("""select count(*) from silver.events e join silver.matches m using (match_id)
                                                where ? in (m.home_team, m.away_team)""", [team]).fetchone()[0],
        },
        "matches": matches,
        "totaux": rec("""select sum(goals_for)::int as buts, sum(goals_against)::int as buts_contre, round(sum(xg), 2) as xg,
                               round(sum(xg_against), 2) as xg_contre, sum(shots)::int as tirs, sum(shots_on_target)::int as tirs_cadres,
                               round(avg(possession_pct), 1) as possession, round(avg(ppda), 2) as ppda
                        from gold.team_match_stats where team = ?""", team)[0],
        "tirs": rec("""select match_id, player, minute, case when period = 1 and minute >= 45 then '45+' || (minute - 44) when period = 2 and minute >= 90 then '90+' || (minute - 89)
                                       when period = 3 and minute >= 105 then '105+' || (minute - 104) when period = 4 and minute >= 120 then '120+' || (minute - 119)
                                       else cast(minute + 1 as varchar) end as minute_aff, round(x, 1) as x, round(y, 1) as y, round(xg, 3) as xg, outcome, shot_type, is_goal
                      from gold.shots where team = ? order by match_date, t_match""", team),
        # minute_ecoulee : temps réellement joué depuis le coup d'envoi (arrêts de jeu compris)
        "xg_chrono": rec("""select case when team = ? then 'equipe' else 'adversaire' end as camp, minute + 1 as minute, case when period = 1 and minute >= 45 then '45+' || (minute - 44) when period = 2 and minute >= 90 then '90+' || (minute - 89)
                                       when period = 3 and minute >= 105 then '105+' || (minute - 104) when period = 4 and minute >= 120 then '120+' || (minute - 119)
                                       else cast(minute + 1 as varchar) end as minute_aff,
                                  round(t_match / 60, 2) as minute_ecoulee, round(xg, 3) as xg, is_goal, player, shot_type, outcome
                           from gold.shots where match_id = ? order by t_match""", team, last["match_id"]),
        "periodes_fin": [round(r[0] / 60, 2) for r in con.execute(
            """select sum(length_s) over (order by period) from silver.period_lengths where match_id = ? order by period""",
            [last["match_id"]]).fetchall()],
        "expulsions": rec("""select case when team = ? then 'equipe' else 'adversaire' end as camp, minute + 1 as minute, case when period = 1 and minute >= 45 then '45+' || (minute - 44) when period = 2 and minute >= 90 then '90+' || (minute - 89)
                                       when period = 3 and minute >= 105 then '105+' || (minute - 104) when period = 4 and minute >= 120 then '120+' || (minute - 119)
                                       else cast(minute + 1 as varchar) end as minute_aff,
                                   round(t_match / 60, 2) as minute_ecoulee, player
                            from silver.events_clock where match_id = ? and card in ('Red Card', 'Second Yellow') order by t_match""", team, last["match_id"]),
        "reseau_passes": pass_network(con, last["match_id"], team),
        "part_passes": part_passes(con, last["match_id"], team),
        # rang de l'équipe parmi toutes les équipes du tournoi, sur des moyennes par match
        "rangs_equipe": rec("""
            with t as (select team, avg(xg) as xg_cree, avg(xg_against) as xg_concede, avg(possession_pct) as possession,
                              avg(ppda) as ppda from gold.team_match_stats group by 1)
            select count(*) over () as equipes,
                   round(ppda, 1) as ppda, rank() over (order by ppda) as rang_pressing,
                   round(possession, 1) as possession, rank() over (order by possession desc) as rang_possession,
                   round(xg_concede, 2) as xg_concede, rank() over (order by xg_concede) as rang_defense,
                   round(xg_cree, 2) as xg_cree, rank() over (order by xg_cree desc) as rang_attaque, team
            from t qualify team = ?""", team)[0],
        "scores": rec("""select player, pos_group, round(minutes) as minutes, round(score, 1) as score, rang_poste, effectif_poste,
                                round(pilier_production, 1) as production, round(pilier_creation, 1) as creation,
                                round(pilier_progression, 1) as progression, round(pilier_defense, 1) as defense,
                                round(pilier_temps_de_jeu, 1) as temps_de_jeu
                         from gold.player_scores where team = ? order by score desc, player""", team),
        "joueurs": rec("""select player, pos_group, round(minutes) as minutes, goals, round(xg, 2) as xg, round(npxg, 2) as npxg,
                                 round(xa, 2) as xa, shots, key_passes, prog_passes, prog_carries, dribbles_won,
                                 tackles_won + interceptions as tacles_interceptions, pressures, recoveries
                          from gold.player_tournament where team = ? order by minutes desc, player""", team),
    }
    con.close()
    out = cfg.path("outputs") / "resultats.json"
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    log.info("export : %s (%d tirs, %d joueurs classés)", out.name, len(data["tirs"]), len(data["scores"]))
    return {"file": str(out)}

"""Contrôles de qualité : le pipeline s'arrête si une règle n'est pas respectée.

Le contrôle clé recoupe les données avec une vérité extérieure : les buts recomptés
depuis les événements doivent redonner le score officiel de chaque match.
"""
from __future__ import annotations

import hashlib
import json

import duckdb

from .config import Config, get_logger

log = get_logger("quality")


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    one = lambda sql: con.execute(sql).fetchone()[0]  # noqa: E731
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append((name, bool(ok), detail))

    # --- bronze : fichiers complets et inchangés depuis la collecte
    bronze = cfg.path("bronze")
    manifest = json.loads((bronze / "_manifest.json").read_text(encoding="utf-8"))
    n_matches = one("select count(*) from silver.matches")
    check("bronze_fichiers_complets", len(manifest) == 2 + 2 * n_matches, f"{len(manifest)} fichiers pour {n_matches} matchs")
    altered = [rel for rel, meta in manifest.items()
               if hashlib.sha256((bronze / rel).read_bytes()).hexdigest() != meta["sha256"]]
    check("bronze_empreintes_intactes", not altered, f"{len(altered)} fichier(s) modifié(s)")

    # --- silver : clés, domaines de valeurs
    n_events = one("select count(*) from silver.events")
    check("events_cle_unique", one("select count(distinct event_id) from silver.events") == n_events, f"{n_events} événements")
    check("events_match_couvert", one("select count(distinct match_id) from silver.events") == n_matches, "chaque match a ses événements")
    out_of_pitch = one("select count(*) from silver.events where x < 0 or x > 120 or y < 0 or y > 80")
    check("coordonnees_dans_le_terrain", out_of_pitch == 0, f"{out_of_pitch} hors terrain")
    bad_xg = one("select count(*) from silver.events where type = 'Shot' and (shot_xg is null or shot_xg < 0 or shot_xg > 1)")
    check("xg_entre_0_et_1", bad_xg == 0, f"{bad_xg} tirs invalides")

    # --- temps de jeu : 11 joueurs x durée du match, moins le temps perdu sur expulsion
    bad_minutes = one("""
        with t as (select match_id, team, sum(minutes) tot from silver.player_match_minutes group by 1, 2),
             reds as (select match_id, team, count(*) n from silver.events where card in ('Red Card', 'Second Yellow') and period <= 4 group by 1, 2)
        select count(*) from t join silver.match_lengths l using (match_id) left join reds r using (match_id, team)
        where tot > 11 * (case when l.last_period >= 3 then 120 else 90 end) + 0.01
           or (r.n is null and abs(tot - 11 * (case when l.last_period >= 3 then 120 else 90 end)) > 0.01)""")
    check("temps_de_jeu_coherent", bad_minutes == 0, f"{bad_minutes} équipe-match(s) incohérent(s)")
    # (un carton pour comportement peut viser un joueur resté sur le banc : on l'écarte de la règle)
    orphans = one("""select count(*) from (select distinct match_id, player_id from silver.events
                                            where player_id is not null and period <= 4 and type <> 'Bad Behaviour') e
                     anti join silver.player_match_minutes m using (match_id, player_id)""")
    check("joueurs_sans_temps_de_jeu", orphans == 0, f"{orphans} joueur(s) avec des actions mais sans minutes")

    # --- gold : recoupement avec le score officiel
    mism = one("select count(*) from gold.team_match_stats where goals_for <> goals_from_events")
    check("buts_recomptes_egal_score_officiel", mism == 0, f"{mism} écart(s) sur {2 * n_matches} équipe-matchs")
    bad_score = one("select count(*) from gold.player_scores where score < 0 or score > 100 or score is null")
    check("score_entre_0_et_100", bad_score == 0, f"{bad_score} score(s) invalide(s)")
    dup = one("select count(*) - count(distinct player_id) from gold.player_scores")
    check("un_score_par_joueur", dup == 0, f"{dup} doublon(s)")

    # --- source 2 : l'historique des Aigles (résultats internationaux, CC0)
    dossier = bronze / "international_results"
    man2 = json.loads((dossier / "_manifest.json").read_text(encoding="utf-8"))
    alt2 = [n for n, meta in man2.items() if hashlib.sha256((dossier / n).read_bytes()).hexdigest() != meta["sha256"]]
    check("aigles_bronze_intact", len(man2) == len(cfg.raw["resultats_internationaux"]["fichiers"]) and not alt2,
          f"{len(man2)} fichier(s), {len(alt2)} modifié(s)")
    # la clé (date, équipes) doit être unique pour les matchs du Mali, ceux qu'on publie. Ailleurs, la source
    # contient au moins un cas de deux matchs le même jour (Tahiti–Nouvelle-Calédonie, 17/02/1974) : on le signale seulement.
    dup_mali = one("select count(*) - count(distinct (date, adversaire)) from gold.aigles_matchs")
    dup_monde = one("select count(*) from silver.intl_matches") - one(
        "select count(*) from (select distinct date, home_team, away_team from silver.intl_matches)")
    check("aigles_matchs_cle_unique", dup_mali == 0, f"{dup_mali} doublon(s) chez le Mali ({dup_monde} ailleurs dans la source, signalé)")
    neg = one("select count(*) from silver.intl_matches where home_score < 0 or away_score < 0")
    check("aigles_scores_valides", neg == 0, f"{neg} score(s) négatif(s)")
    n_mali, age = con.execute("select count(*), current_date - max(date) from gold.aigles_matchs").fetchone()
    limite = int(cfg.raw["resultats_internationaux"]["fraicheur_max_jours"])
    check("aigles_source_a_jour", n_mali > 500 and age <= limite, f"{n_mali} matchs du Mali, le dernier il y a {age} jours (limite {limite})")
    # les buteurs sont incomplets, mais ceux qui sont saisis ne doivent jamais dépasser le score
    trop = one(f"""select count(*) from (
        select g.date, g.home_team, g.away_team, g.team, count(*) n,
               max(case when g.team = m.home_team then m.home_score else m.away_score end) score
        from silver.intl_goals g join silver.intl_matches m using (date, home_team, away_team)
        group by 1, 2, 3, 4) where n > score""")
    check("aigles_buteurs_coherents", trop == 0, f"{trop} équipe-match(s) avec plus de buteurs que de buts")
    # recoupement entre les deux sources : les matchs du Mali à la CAN 2023 doivent avoir le même score
    ecarts, communs = con.execute(f"""
        with sb as (select match_date as date,
                           case when home_team = '{cfg.team}' then home_score else away_score end pour,
                           case when home_team = '{cfg.team}' then away_score else home_score end contre
                    from silver.matches where home_team = '{cfg.team}' or away_team = '{cfg.team}')
        select count(*) filter (sb.pour <> a.buts_pour or sb.contre <> a.buts_contre), count(*)
        from sb join gold.aigles_matchs a using (date)""").fetchone()
    n_sb = one(f"select count(*) from silver.matches where home_team = '{cfg.team}' or away_team = '{cfg.team}'")
    check("aigles_recoupe_statsbomb", ecarts == 0 and communs == n_sb, f"{communs}/{n_sb} matchs retrouvés, {ecarts} écart(s) de score")
    con.close()

    report = {"checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
              "passed": sum(ok for _, ok, _ in checks), "total": len(checks)}
    (cfg.path("outputs") / "quality_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    for n, ok, d in checks:
        (log.info if ok else log.error)("%s %-36s %s", "OK " if ok else "KO ", n, d)
    if report["passed"] != report["total"]:
        raise SystemExit("contrôles de qualité en échec : voir outputs/quality_report.json")
    return report

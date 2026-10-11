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
    con.close()

    report = {"checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
              "passed": sum(ok for _, ok, _ in checks), "total": len(checks)}
    (cfg.path("outputs") / "quality_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    for n, ok, d in checks:
        (log.info if ok else log.error)("%s %-36s %s", "OK " if ok else "KO ", n, d)
    if report["passed"] != report["total"]:
        raise SystemExit("contrôles de qualité en échec : voir outputs/quality_report.json")
    return report

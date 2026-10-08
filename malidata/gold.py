"""Étape 3 — GOLD : indicateurs d'analyse, comparaisons par poste et Mali Player Score."""
from __future__ import annotations

import duckdb
import pandas as pd

from .config import ROOT, Config, get_logger

log = get_logger("gold")


def position_group(position: str | None) -> str:
    """Regroupe les 23 postes StatsBomb en quatre familles."""
    if position == "Goalkeeper":
        return "GAR"
    if position and "Back" in position:
        return "DEF"
    if position and "Midfield" in position:
        return "MIL"
    return "ATT"


def percentiles(players: pd.DataFrame, metrics: list[str], min_minutes: int) -> pd.DataFrame:
    """Rang centile (0-100) de chaque indicateur, parmi les joueurs du même groupe de postes
    ayant assez joué. 100 = meilleur du tournoi à son poste."""
    pop = players[(players["minutes"] >= min_minutes) & (players["pos_group"] != "GAR")].copy()
    for m in metrics:
        pop[m + "_pct"] = pop.groupby("pos_group")[m].rank(pct=True, method="average") * 100
    return pop


def player_score(pop: pd.DataFrame, pillars: dict[str, list[str]], weights: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Mali Player Score : moyenne pondérée des piliers, chaque pilier étant la moyenne
    des centiles de ses indicateurs. Le temps de jeu est un pilier à part entière."""
    out = pop.copy()
    for pillar, metrics in pillars.items():
        out["pilier_" + pillar] = out[[m + "_pct" for m in metrics]].mean(axis=1)
    out["pilier_temps_de_jeu"] = out.groupby("pos_group")["minutes"].rank(pct=True) * 100

    def score(row: pd.Series) -> float:
        w = weights[row["pos_group"]]
        return sum(row["pilier_" + k] * v for k, v in w.items()) / sum(w.values())

    out["score"] = out.apply(score, axis=1)
    out["rang_poste"] = out.groupby("pos_group")["score"].rank(ascending=False, method="min").astype(int)
    out["effectif_poste"] = out.groupby("pos_group")["score"].transform("size")
    return out


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")))
    con.execute("create schema if not exists gold")
    for sql_file in sorted((ROOT / "sql").glob("*.sql")):
        con.execute(sql_file.read_text(encoding="utf-8"))
        log.info("modèle SQL exécuté : %s", sql_file.name)

    players = con.execute("select * from gold.player_tournament").df()
    pillars = cfg.raw["score_pillars"]
    metrics = [m for ms in pillars.values() for m in ms]
    pop = percentiles(players, metrics, cfg.min_minutes)
    scored = player_score(pop, pillars, cfg.raw["score_weights"])
    con.register("df_scored", scored)
    con.execute("create or replace table gold.player_scores as select * from df_scored")

    gold_dir = cfg.path("gold")
    tables = ["player_match_stats", "player_tournament", "team_match_stats", "shots", "player_scores"]
    for t in tables:
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.parquet')}' (format parquet)")
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.csv')}' (header, delimiter ',')")
    stats = {"scored_players": len(scored), "tables": len(tables)}
    con.close()
    log.info("gold : %d tables, %d joueurs classés (>= %d min)", len(tables), len(scored), cfg.min_minutes)
    return stats

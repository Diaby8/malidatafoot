"""Classement Elo maison de toutes les sélections, calculé sur l'historique complet (martj42, CC0).

Pourquoi : pour juger un chiffre des Aigles (buts encaissés, victoires…), il faut savoir contre qui. Un 0-0 contre
le Maroc et un 0-0 contre une petite sélection ne pèsent pas pareil. L'Elo donne à chaque équipe, avant chaque match,
une force mesurée sur tous ses résultats passés.

Méthode : celle du World Football Elo Ratings (eloratings.net), écrite en clair pour pouvoir la vérifier.
- Chaque nouvelle équipe démarre à 1500.
- Résultat attendu : We = 1 / (10^(-dr/400) + 1), avec dr l'écart d'Elo, +100 pour l'équipe qui reçoit (sauf terrain neutre).
- Mise à jour : Elo += K × G × (W - We), W = 1 victoire, 0,5 nul, 0 défaite (une séance de tirs au but compte comme un nul).
- K selon le match : 60 Coupe du monde ; 50 phase finale continentale (CAN, Euro, Copa América, Coupe d'Asie, Gold Cup…) ;
  40 éliminatoires et Ligues des nations ; 30 autres tournois ; 20 matchs amicaux.
- G selon l'écart de buts N : 1 si N ≤ 1, 1,5 si N = 2, (11 + N) / 8 au-delà.
Ce que l'un gagne, l'autre le perd : la somme des Elo ne bouge pas (contrôlé dans quality.py).
"""
from __future__ import annotations

import duckdb
import pandas as pd

from .config import Config, get_logger

log = get_logger("elo")
DEPART, AVANTAGE_DOMICILE = 1500.0, 100.0
PHASES_FINALES = {"FIFA World Cup": 60, "African Cup of Nations": 50, "UEFA Euro": 50, "Copa América": 50, "AFC Asian Cup": 50,
                  "Gold Cup": 50, "CONCACAF Championship": 50, "Confederations Cup": 50, "Oceania Nations Cup": 50}


def poids(tournoi: str) -> int:
    if tournoi in PHASES_FINALES:
        return PHASES_FINALES[tournoi]
    if "qualification" in tournoi or "Nations League" in tournoi:
        return 40
    if tournoi == "Friendly":
        return 20
    return 30


def multiplicateur(ecart: int) -> float:
    n = abs(ecart)
    return 1.0 if n <= 1 else 1.5 if n == 2 else (11 + n) / 8


def rang(elo: dict, dernier: dict, equipe: str, jour, fenetre_jours: int = 4 * 365) -> int:
    """Place de l'équipe parmi les sélections actives ce jour-là (au moins un match dans les 4 ans), comme eloratings.net."""
    limite = pd.Timestamp(jour) - pd.Timedelta(days=fenetre_jours)
    e = elo.get(equipe, DEPART)
    return 1 + sum(1 for t, v in elo.items() if t != equipe and v > e and dernier[t] >= limite)


def calculer(matchs: pd.DataFrame, suivie: str | None = None) -> pd.DataFrame:
    """matchs : date, home_team, away_team, home_score, away_score, tournament, neutral, triés par date.
    Renvoie une ligne par match avec l'Elo de chaque équipe avant et après. Pour les matchs de l'équipe `suivie`,
    ajoute le rang de chaque équipe avant le match (sinon la colonne est vide : le calcul est coûteux)."""
    elo: dict[str, float] = {}
    dernier: dict[str, pd.Timestamp] = {}
    lignes = []
    for r in matchs.itertuples(index=False):
        a, b = elo.get(r.home_team, DEPART), elo.get(r.away_team, DEPART)
        rangs = ((rang(elo, dernier, r.home_team, r.date), rang(elo, dernier, r.away_team, r.date))
                 if suivie in (r.home_team, r.away_team) else (None, None))
        dr = a - b + (0.0 if r.neutral else AVANTAGE_DOMICILE)
        attendu = 1 / (10 ** (-dr / 400) + 1)
        w = 1.0 if r.home_score > r.away_score else 0.0 if r.home_score < r.away_score else 0.5
        delta = poids(r.tournament) * multiplicateur(r.home_score - r.away_score) * (w - attendu)
        elo[r.home_team], elo[r.away_team] = a + delta, b - delta
        dernier[r.home_team] = dernier[r.away_team] = pd.Timestamp(r.date)
        lignes.append((r.date, r.home_team, r.away_team, r.home_score, r.away_score, r.tournament, r.neutral,
                       a, b, a + delta, b - delta, attendu, *rangs))
    return pd.DataFrame(lignes, columns=["date", "home_team", "away_team", "home_score", "away_score", "tournament", "neutral",
                                         "elo_home_avant", "elo_away_avant", "elo_home_apres", "elo_away_apres", "attendu_home",
                                         "rang_home_avant", "rang_away_avant"]).astype({"rang_home_avant": "Int64", "rang_away_avant": "Int64"})


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")))
    m = con.execute("""select date, home_team, away_team, home_score, away_score, tournament, neutral
                       from silver.intl_matches order by date, home_team, away_team""").df()
    equipe = cfg.raw["resultats_internationaux"]["equipe"]
    e = calculer(m, suivie=equipe)
    con.execute("create schema if not exists gold")
    con.register("e", e)
    con.execute("create or replace table gold.elo_matchs as select * from e")
    con.unregister("e")
    # Elo actuel : dernière valeur de chaque équipe ; classées seulement celles qui ont joué depuis 4 ans (comme eloratings.net)
    con.execute("""create or replace table gold.elo_actuel as
        with t as (
            select home_team as equipe, date, elo_home_apres as elo from gold.elo_matchs
            union all select away_team, date, elo_away_apres from gold.elo_matchs)
        select equipe, arg_max(elo, date) as elo, max(date) as dernier_match,
               max(date) >= (select max(date) from gold.elo_matchs) - interval 4 year as active
        from t group by equipe""")
    con.execute("""create or replace table gold.elo_actuel as
        select *, case when active then rank() over (partition by active order by elo desc) end as rang
        from gold.elo_actuel order by elo desc""")
    equipe = equipe.replace("'", "''")
    # les matchs du Mali avec la force de l'adversaire avant le match
    con.execute(f"""create or replace table gold.aigles_elo as
        select a.*,
               case when e.home_team = '{equipe}' then e.elo_home_avant else e.elo_away_avant end as elo_mali_avant,
               case when e.home_team = '{equipe}' then e.elo_away_avant else e.elo_home_avant end as elo_adversaire_avant,
               case when e.home_team = '{equipe}' then e.elo_home_apres else e.elo_away_apres end as elo_mali_apres,
               case when e.home_team = '{equipe}' then e.rang_away_avant else e.rang_home_avant end as rang_adversaire_avant,
               case when e.home_team = '{equipe}' then e.rang_home_avant else e.rang_away_avant end as rang_mali_avant
        from gold.aigles_matchs a
        join gold.elo_matchs e on e.date = a.date and '{equipe}' in (e.home_team, e.away_team)
             and a.adversaire in (e.home_team, e.away_team)
        order by a.date""")
    gold_dir = cfg.path("gold")
    for t in ("elo_actuel", "aigles_elo"):
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.parquet')}' (format parquet)")
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.csv')}' (header, delimiter ',')")
    elo_mali, rang = con.execute(f"select round(elo), rang from gold.elo_actuel where equipe = '{equipe}'").fetchone()
    n = con.execute("select count(*) from gold.elo_matchs").fetchone()[0]
    con.close()
    log.info("elo : %d matchs ; %s : %d points, %se des sélections actives", n, equipe, elo_mali, rang)
    return {"matchs": n, "elo_mali": elo_mali, "rang_mali": rang}

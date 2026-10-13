"""Analyses qui alimentent les posts. Chaque analyse lit l'entrepôt, calcule, et écrit un JSON dans outputs/analyses/
(lu par les gabarits de visuels/). Rien n'est recopié à la main.

defense_aigles : « Depuis 2020, les Aigles encaissent deux fois moins. Est-ce parce que les adversaires sont plus faibles ? »
- matchs officiels = phase finale de la CAN, éliminatoires de la CAN, éliminatoires de la Coupe du monde (les tournois
  régionaux comme la Coupe Amílcar Cabral sont laissés de côté : niveau trop variable) ;
- référence = 2000-2019 ; période étudiée = depuis le 1er janvier 2020 ;
- niveau de l'adversaire = son rang Elo le jour du match (gold.aigles_elo, voir elo.py) ;
- « à adversaires égaux » = modèle de Poisson appris sur la référence : buts encaissés selon l'Elo de l'adversaire et le lieu,
  appliqué aux matchs depuis 2020. C'est ce que le Mali de 2000-2019 aurait encaissé face aux mêmes adversaires, aux mêmes endroits.
"""
from __future__ import annotations

import json
import math

import duckdb
import numpy as np
import pandas as pd

from .config import Config, get_logger

log = get_logger("analyses")
OFFICIELS = ("African Cup of Nations", "African Cup of Nations qualification", "FIFA World Cup qualification")
NIVEAUX = ((1, 60, "Top 60"), (61, 100, "61e à 100e"), (101, 10_000, "Au-delà du 100e"))


def poisson_irls(X: np.ndarray, y: np.ndarray, iterations: int = 50) -> np.ndarray:
    """Régression de Poisson (lien log) par moindres carrés repondérés : log E[y] = X·b. Renvoie b."""
    b = np.zeros(X.shape[1]); b[0] = math.log(max(y.mean(), 1e-9))
    for _ in range(iterations):
        mu = np.exp(X @ b)
        z = X @ b + (y - mu) / mu
        nb = np.linalg.solve(X.T @ (X * mu[:, None]), X.T @ (mu * z))
        if np.max(np.abs(nb - b)) < 1e-10:
            return nb
        b = nb
    return b


def _plan(d: pd.DataFrame) -> np.ndarray:
    return np.column_stack([np.ones(len(d)), (d["elo_adversaire_avant"] - 1500) / 100,
                            (d["lieu"] == "domicile").astype(float), (d["lieu"] == "extérieur").astype(float)])


def poisson_cdf(k: int, lam: float) -> float:
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def defense_aigles(con: duckdb.DuckDBPyConnection) -> dict:
    d = con.execute(f"""select date, annee, competition, adversaire, buts_pour, buts_contre, lieu,
                               elo_adversaire_avant, rang_adversaire_avant
                        from gold.aigles_elo where competition in {OFFICIELS} and annee >= 2000 order by date""").df()
    ref, rec = d[d.annee < 2020], d[d.annee >= 2020]
    b = poisson_irls(_plan(ref), ref["buts_contre"].to_numpy(float))
    attendus = float(np.exp(_plan(rec) @ b).sum())
    bilan = lambda s: {"matchs": int(len(s)), "buts_encaisses": int(s.buts_contre.sum()),  # noqa: E731
                       "par_match": float(s.buts_contre.mean()), "sans_encaisser": int((s.buts_contre == 0).sum()),
                       "rang_median_adversaire": float(s.rang_adversaire_avant.median())}
    niveaux = []
    for lo, hi, nom in NIVEAUX:
        f = lambda s: s[(s.rang_adversaire_avant >= lo) & (s.rang_adversaire_avant <= hi)]  # noqa: E731
        a, r = f(ref), f(rec)
        niveaux.append({"niveau": nom, "rang_min": lo, "rang_max": hi,
                        "reference": {"matchs": int(len(a)), "buts": int(a.buts_contre.sum()), "par_match": float(a.buts_contre.mean())},
                        "depuis_2020": {"matchs": int(len(r)), "buts": int(r.buts_contre.sum()), "par_match": float(r.buts_contre.mean())}})
    par_annee = [{"annee": int(a), "matchs": int(len(s)), "par_match": float(s.buts_contre.mean()),
                  "attendus_par_match": float(np.exp(_plan(s) @ b).mean())}
                 for a, s in d.groupby("annee")]
    return {
        "question": "Depuis 2020, les Aigles encaissent-ils moins parce que les adversaires sont plus faibles ?",
        "perimetre": "Phase finale de la CAN, éliminatoires de la CAN et de la Coupe du monde",
        "reference": {"periode": "2000-2019", **bilan(ref)},
        "depuis_2020": {"periode": f"2020-{int(d.annee.max())}", "dernier_match": str(d.date.max())[:10], **bilan(rec)},
        "a_adversaires_egaux": {"buts_attendus": attendus, "buts_reels": int(rec.buts_contre.sum()),
                                "probabilite_si_rien_n_avait_change": poisson_cdf(int(rec.buts_contre.sum()), attendus),
                                "modele": {"constante": b[0], "par_100_points_elo_adverse": b[1], "domicile": b[2], "exterieur": b[3]}},
        "niveaux": niveaux,
        "par_annee": par_annee,
        "matchs": [{"date": str(r.date)[:10], "periode": "depuis_2020" if r.annee >= 2020 else "reference", "competition": r.competition,
                    "adversaire": r.adversaire, "buts_pour": int(r.buts_pour), "buts_contre": int(r.buts_contre),
                    "rang_adversaire": int(r.rang_adversaire_avant), "lieu": r.lieu} for r in d.itertuples()],
        "source": "martj42/international_results (CC0) ; Elo calculé par MaliDataFoot (méthode eloratings.net)",
    }


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    dossier = cfg.path("outputs") / "analyses"
    dossier.mkdir(parents=True, exist_ok=True)
    res = defense_aigles(con)
    con.close()
    (dossier / "defense_aigles.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    r, n, e = res["reference"], res["depuis_2020"], res["a_adversaires_egaux"]
    log.info("défense des Aigles : %.2f but encaissé par match depuis 2020 (%d matchs) contre %.2f en 2000-2019 ; "
             "à adversaires égaux, %.1f buts attendus pour %d réels", n["par_match"], n["matchs"], r["par_match"], e["buts_attendus"], e["buts_reels"])
    return res

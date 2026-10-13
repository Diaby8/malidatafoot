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


def robustesse(d: pd.DataFrame) -> list[dict]:
    """Le résultat dépend-il de l'année choisie (2020) ? On refait le calcul pour chaque année de coupure de 2014 à 2023 :
    buts réels après la coupure / buts attendus à adversaires égaux (modèle appris avant la coupure)."""
    out = []
    for coupe in range(2014, 2024):
        a, r = d[d.annee < coupe], d[d.annee >= coupe]
        b = poisson_irls(_plan(a), a["buts_contre"].to_numpy(float))
        att = float(np.exp(_plan(r) @ b).sum())
        out.append({"coupure": coupe, "matchs_apres": int(len(r)), "attendus": att, "reels": int(r.buts_contre.sum()),
                    "rapport": float(r.buts_contre.sum() / att)})
    return out


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
        "robustesse_annee_de_coupure": robustesse(d),
        "par_annee": par_annee,
        "matchs": [{"date": str(r.date)[:10], "periode": "depuis_2020" if r.annee >= 2020 else "reference", "competition": r.competition,
                    "adversaire": r.adversaire, "buts_pour": int(r.buts_pour), "buts_contre": int(r.buts_contre),
                    "rang_adversaire": int(r.rang_adversaire_avant), "lieu": r.lieu} for r in d.itertuples()],
        "source": "martj42/international_results (CC0) ; Elo calculé par MaliDataFoot (méthode eloratings.net)",
    }


def fifa_rwanda(registre) -> dict:
    """« Contre le Rwanda, le Mali a plus à perdre qu'à gagner au classement FIFA. » Points avant (registre/classement_fifa.csv),
    calcul de la FIFA (fifa.py), deux matchs d'éliminatoires (I = 25). Vérification : en partant des points de juillet, le calcul
    doit retrouver les points d'octobre du Mali (3-1 contre le Cap-Vert, 1-0 au Liberia, 1-1 au Maroc en amical)."""
    from . import fifa
    c = pd.read_csv(registre / "classement_fifa.csv")
    pt = lambda e, d: float(c[(c.equipe == e) & (c.date_classement == d)].points.iloc[0])  # noqa: E731
    mali, rwa = pt("Mali", "2026-10-07"), pt("Rwanda", "2026-10-07")
    un = {r: fifa.match(mali, rwa, r, fifa.IMPORTANCE["eliminatoires"])[0] - mali for r in "VND"}
    sc = fifa.scenarios(mali, rwa, fifa.IMPORTANCE["eliminatoires"])
    # vérification sur la fenêtre de septembre-octobre (points des adversaires : ceux de juillet, donc à quelques centièmes près)
    p = pt("Mali", "2026-07-20")
    p, _ = fifa.match(p, pt("Cape Verde", "2026-07-20"), "V", 25)
    p, _ = fifa.match(p, pt("Liberia", "2026-07-20"), "V", 25)
    p, _ = fifa.match(p, pt("Morocco", "2026-07-20"), "N", 10)
    return {"question": "Combien de points FIFA le Mali peut-il gagner ou perdre contre le Rwanda ?",
            "points_avant": {"Mali": mali, "Rwanda": rwa, "date": "2026-10-07"},
            "attendu_mali": fifa.attendu(mali, rwa), "importance": fifa.IMPORTANCE["eliminatoires"],
            "un_match": un, "deux_matchs": sc,
            "verification_octobre": {"recalcule": p, "officiel": mali, "ecart": p - mali},
            "a_confirmer": c[c.a_confirmer == "oui"].equipe.tolist(),
            "source": "registre/classement_fifa.csv ; formule FIFA (SUM, 2018)"}


def run(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    dossier = cfg.path("outputs") / "analyses"
    dossier.mkdir(parents=True, exist_ok=True)
    res = defense_aigles(con)
    con.close()
    (dossier / "defense_aigles.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    from .config import ROOT
    fr_ = fifa_rwanda(ROOT / "registre")
    (dossier / "fifa_rwanda.json").write_text(json.dumps(fr_, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log.info("FIFA contre le Rwanda : victoire %+.2f, nul %+.2f, défaite %+.2f ; vérification d'octobre : écart %.2f point",
             fr_["un_match"]["V"], fr_["un_match"]["N"], fr_["un_match"]["D"], fr_["verification_octobre"]["ecart"])
    r, n, e = res["reference"], res["depuis_2020"], res["a_adversaires_egaux"]
    log.info("défense des Aigles : %.2f but encaissé par match depuis 2020 (%d matchs) contre %.2f en 2000-2019 ; "
             "à adversaires égaux, %.1f buts attendus pour %d réels", n["par_match"], n["matchs"], r["par_match"], e["buts_attendus"], e["buts_reels"])
    return res

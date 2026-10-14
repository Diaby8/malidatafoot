"""Source 2 — l'historique des Aigles : tous les matchs internationaux depuis 1872.

Jeu de données public (CC0) tenu sur GitHub par Mart Jürisoo : résultats, buteurs et tirs au but.
Même chemin que StatsBomb : bronze (fichiers bruts + manifeste) → silver (tables propres) →
gold (modèles SQL de sql/aigles/, vus du côté du Mali). Les buteurs y sont incomplets :
on ne s'en sert que recoupés (voir les contrôles dans quality.py).
"""
from __future__ import annotations

import hashlib
import io
import json
import time
import urllib.request
from datetime import datetime, timezone

import duckdb
import pandas as pd

from .config import ROOT, Config, get_logger

log = get_logger("aigles")
DOSSIER = "international_results"


def _telecharger(url: str, essais: int = 4) -> bytes:
    for n in range(1, essais + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            entete = data[:200].decode("utf-8", errors="replace")
            if not entete.startswith("date,"):  # refuse une page d'erreur ou un fichier tronqué
                raise ValueError(f"en-tête inattendu : {entete[:60]!r}")
            return data
        except Exception as exc:  # noqa: BLE001
            if n == essais:
                raise RuntimeError(f"échec du téléchargement de {url}") from exc
            time.sleep(1.5 * n)
    raise AssertionError("unreachable")


def bronze(cfg: Config, force: bool = False) -> dict:
    """Télécharge les CSV bruts, une seule fois par jour, et les inscrit au manifeste."""
    src = cfg.raw["resultats_internationaux"]
    dossier = cfg.path("bronze") / DOSSIER
    dossier.mkdir(parents=True, exist_ok=True)
    chemin_manifeste = dossier / "_manifest.json"
    manifeste = json.loads(chemin_manifeste.read_text(encoding="utf-8")) if chemin_manifeste.exists() else {}
    aujourd_hui = datetime.now(timezone.utc).date().isoformat()
    for nom in src["fichiers"]:
        dest = dossier / nom
        deja = manifeste.get(nom, {}).get("fetched_at", "")[:10] == aujourd_hui and dest.exists()
        if deja and not force:
            continue
        data = _telecharger(f"{src['base_url']}/{nom}")
        tmp = dest.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
        manifeste[nom] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                          "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                          "source": f"{src['base_url']}/{nom}"}
    chemin_manifeste.write_text(json.dumps(manifeste, indent=1, sort_keys=True), encoding="utf-8")
    return manifeste


def silver(cfg: Config) -> dict:
    dossier = cfg.path("bronze") / DOSSIER
    lire = lambda nom: pd.read_csv(io.StringIO((dossier / nom).read_text(encoding="utf-8")))  # noqa: E731
    matchs, buts, tab = lire("results.csv"), lire("goalscorers.csv"), lire("shootouts.csv")
    for df in (matchs, buts, tab):
        df["date"] = pd.to_datetime(df["date"]).dt.date
    matchs = matchs.dropna(subset=["home_score", "away_score"])  # matchs annoncés mais pas encore joués
    matchs[["home_score", "away_score"]] = matchs[["home_score", "away_score"]].astype(int)
    matchs, forfaits = appliquer_forfaits(matchs)
    con = duckdb.connect(str(cfg.path("warehouse")))
    con.execute("create schema if not exists silver")
    for nom, df in (("intl_matches", matchs), ("intl_goals", buts), ("intl_shootouts", tab)):
        con.register("df", df)
        con.execute(f"create or replace table silver.{nom} as select * from df")
        con.unregister("df")
    con.close()
    return {"matchs": len(matchs), "buts": len(buts), "tab": len(tab), "forfaits": forfaits}


def appliquer_forfaits(matchs: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Règle MaliDataFoot (14/10/2026) : seulement les matchs joués, avec le score du terrain.
    martj42 garde le score officiel des matchs gagnés sur tapis vert ; `registre/forfaits.csv` liste ces matchs avec la source.
    Un match jamais joué (ou dont le score du terrain n'est pas confirmé) est retiré ; sinon on remet le score du terrain.
    Chaque ligne du registre doit retrouver exactement un match avec le score officiel attendu : sinon on arrête tout."""
    f = pd.read_csv(ROOT / "registre" / "forfaits.csv", dtype=str)
    matchs = matchs.copy()
    for r in f.itertuples():
        d = pd.to_datetime(r.date).date()
        m = (matchs["date"] == d) & (matchs["home_team"] == r.home_team) & (matchs["away_team"] == r.away_team)
        if m.sum() != 1:
            raise ValueError(f"forfait introuvable dans martj42 : {r.date} {r.home_team}-{r.away_team}")
        i = matchs.index[m][0]
        officiel = f"{matchs.at[i, 'home_score']}-{matchs.at[i, 'away_score']}"
        if officiel != r.score_officiel:
            raise ValueError(f"score inattendu pour {r.date} {r.home_team}-{r.away_team} : {officiel} au lieu de {r.score_officiel}")
        if r.decision == "exclure":
            matchs = matchs.drop(index=i)
        elif r.decision == "score_terrain":
            matchs.at[i, "home_score"], matchs.at[i, "away_score"] = int(r.home_score_terrain), int(r.away_score_terrain)
        else:
            raise ValueError(f"décision inconnue : {r.decision}")
    log.info("forfaits et tapis verts : %d matchs corrigés ou retirés (registre/forfaits.csv)", len(f))
    return matchs, len(f)


def gold(cfg: Config) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")))
    con.execute("create schema if not exists gold")
    equipe = cfg.raw["resultats_internationaux"]["equipe"].replace("'", "''")
    for f in sorted((ROOT / "sql" / "aigles").glob("*.sql")):
        con.execute(f.read_text(encoding="utf-8").replace("{equipe}", equipe))
        log.info("modèle SQL exécuté : aigles/%s", f.name)
    gold_dir = cfg.path("gold")
    for t in ("aigles_matchs", "aigles_bilan_annuel"):
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.parquet')}' (format parquet)")
        con.execute(f"copy gold.{t} to '{gold_dir / (t + '.csv')}' (header, delimiter ',')")
    n, dernier = con.execute("select count(*), max(date) from gold.aigles_matchs").fetchone()
    con.close()
    return {"matchs_mali": n, "dernier": str(dernier)}


def run(cfg: Config, force: bool = False) -> dict:
    m = bronze(cfg, force)
    s = silver(cfg)
    g = gold(cfg)
    log.info("aigles : %d matchs internationaux, %d buts, %d séances de tirs au but ; %d matchs du Mali (dernier : %s) ; %d fichiers bruts",
             s["matchs"], s["buts"], s["tab"], g["matchs_mali"], g["dernier"], len(m))
    return {**s, **g}

"""Étape 3 bis — PROFILS : lire un joueur parmi ses vrais pairs, sur les critères de son poste.

Trois règles, écrites ici pour qu'elles soient les mêmes partout (fiches, vidéos, fils) :

1. Le bassin de comparaison. Par défaut on compare un joueur aux joueurs du même rôle
   (un latéral aux latéraux), pas à toute sa ligne : un défenseur central ne crée pas
   d'occasions et ne presse pas comme un latéral. Le bassin « ligne » (tous les défenseurs)
   reste disponible pour comparer les deux lectures.
2. Le centile. C'est la part des AUTRES joueurs du bassin que le joueur dépasse strictement.
   Un joueur à zéro dribble ne dépasse personne : centile 0, même s'ils sont vingt à zéro.
   Le meilleur, s'il est seul, dépasse tous les autres : centile 100.
3. La note. C'est la moyenne des centiles sur les critères du rôle, ceux que la fiche montre.
   Le temps de jeu n'entre pas dans la note : il sert de seuil d'entrée (min_minutes).
"""
from __future__ import annotations

import json
import re
import unicodedata

import duckdb
import pandas as pd

from .config import Config, get_logger

log = get_logger("profils")

PART_MIN = 0.5     # il faut avoir fait au moins la moitié de ses actions dans son rôle principal
LIGNES = {"DEF": ("défenseur", "défenseurs"), "MIL": ("milieu", "milieux"), "ATT": ("attaquant", "attaquants")}


def role(position: str | None) -> str | None:
    """Rôle fin d'un poste StatsBomb. Sept rôles : assez fins pour comparer des joueurs
    qui font le même métier, assez larges pour garder des bassins de taille correcte."""
    if not position:
        return None
    if position == "Goalkeeper":
        return "GAR"
    if "Center Back" in position:
        return "DC"
    if "Back" in position:                       # arrières latéraux et pistons
        return "LAT"
    if "Defensive Midfield" in position:
        return "MDF"
    if "Attacking Midfield" in position or position.endswith("Wing"):
        return "MOF"
    if "Midfield" in position:
        return "MIL"
    return "ATT"


def centile_strict(values: pd.Series) -> pd.Series:
    """Part (0-100) des autres joueurs strictement dépassés. Les ex æquo reçoivent tous
    le même centile, celui du bas de leur groupe."""
    n = len(values)
    if n < 2:
        return pd.Series(50.0, index=values.index)
    return (values.rank(method="min") - 1) / (n - 1) * 100


def profil_bassin(pop: pd.DataFrame, criteres: list[str]) -> pd.DataFrame:
    """Centiles, note, rang et effectif pour tous les joueurs d'un bassin déjà filtré."""
    out = pop.copy()
    for k in criteres:
        out[k + "_ctl"] = centile_strict(out[k])
        out[k + "_rg"] = out[k].rank(ascending=False, method="min").astype(int)      # sa place : 1 = le meilleur du bassin
        out[k + "_max"] = out[k].max(); out[k + "_med"] = out[k].median()
    # arrondi avant le classement : deux joueurs à égalité exacte ne doivent pas être départagés par une erreur d'arrondi machine
    out["note"] = out[[k + "_ctl" for k in criteres]].mean(axis=1).round(6)
    out["rang"] = out["note"].rank(ascending=False, method="min").astype(int)
    out["effectif"] = len(out)
    return out


def proches(prof: pd.DataFrame, player_id: int, criteres: list[str], n: int = 3) -> list[dict]:
    """Profils les plus proches dans le bassin. Proximité = 100 moins l'écart moyen, en points
    de centile, sur les critères du rôle : 85 veut dire quinze points d'écart en moyenne."""
    cols = [k + "_ctl" for k in criteres]
    me = prof.loc[prof["player_id"] == player_id, cols].iloc[0]
    autres = prof[prof["player_id"] != player_id].copy()
    autres["proche"] = 100 - (autres[cols] - me).abs().mean(axis=1)
    top = autres.sort_values(["proche", "player"], ascending=[False, True]).head(n)
    return [{"player_id": int(r.player_id), "player": r.player, "team": r.team, "proche": round(float(r.proche))}
            for r in top.itertuples()]


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def joueurs(con: duckdb.DuckDBPyConnection, min_minutes: int) -> pd.DataFrame:
    """Tous les joueurs de champ ayant assez joué, avec leur rôle fin."""
    df = con.execute("select * from gold.player_tournament where minutes >= ? and position <> 'Goalkeeper'",
                     [min_minutes]).df()
    # le rôle d'un joueur est celui où il a fait le plus d'actions, à condition d'y avoir fait au moins la moitié de ses actions :
    # un ailier aligné un match en piston ne doit pas se retrouver classé parmi les latéraux
    pos = con.execute("select * from gold.player_positions").df()
    pos["role"] = pos["position"].map(role)
    par_role = pos.groupby(["player_id", "role"])["n"].sum().reset_index()
    par_role["part"] = par_role["n"] / par_role.groupby("player_id")["n"].transform("sum")
    principal = par_role.sort_values("n", ascending=False).drop_duplicates("player_id").rename(columns={"part": "part_role"})
    df = df.drop(columns=["role"], errors="ignore").merge(principal[["player_id", "role", "part_role"]], on="player_id", how="left")
    ecartes = df[df["part_role"] < PART_MIN]
    if len(ecartes):
        log.info("profils : %d joueur(s) sans rôle net, écartés des comparaisons (%s)", len(ecartes), ", ".join(ecartes["player"].head(8)))
    return df[df["part_role"] >= PART_MIN].reset_index(drop=True)


def fiche(cfg: Config, df: pd.DataFrame, player: str, bassin: str = "poste") -> dict:
    """Tout ce qu'une fiche joueur affiche, pour un bassin donné :
    « poste » = les joueurs du même rôle ; « ligne » = toute sa ligne (défenseurs, milieux, attaquants)."""
    lignes = df[df["player"] == player]
    if len(lignes) != 1:
        raise ValueError(f"{player!r} : {len(lignes)} joueur(s) trouvé(s) au-dessus du seuil de temps de jeu")
    me = lignes.iloc[0]
    spec = cfg.raw["roles"].get(me["role"])
    if not spec or not spec.get("criteres"):
        raise ValueError(f"pas encore de critères définis pour le rôle {me['role']}")
    criteres = [c["k"] for c in spec["criteres"]]
    if bassin == "poste":
        pop, noms, code = df[df["role"] == me["role"]], (spec["singulier"], spec["pluriel"]), me["role"]
    elif bassin == "ligne":
        pop, noms, code = df[df["pos_group"] == me["pos_group"]], LIGNES[me["pos_group"]], me["pos_group"]
    else:
        raise ValueError("bassin attendu : 'poste' ou 'ligne'")
    prof = profil_bassin(pop, criteres)
    r = prof[prof["player_id"] == me["player_id"]].iloc[0]
    fr = cfg.raw.get("team_labels", {})
    sim = proches(prof, int(me["player_id"]), criteres)
    for s in sim:
        s["team"] = fr.get(s["team"], s["team"])
    # ce qu'il réussit : part de réussite et nombre de tentatives (jamais un pourcentage sans son effectif)
    defaut = [{"nom": "Passes réussies", "num": "passes_completed", "den": "passes"}, {"nom": "Dribbles réussis", "num": "dribbles_won", "den": "dribbles"},
              {"nom": "Duels aériens gagnés", "num": "aerials_won", "den": "aerials_won+aerials_lost"}]
    reussite = []
    for x in spec.get("reussite", defaut):
        num, den = int(me[x["num"]]), int(sum(me[c] for c in x["den"].split("+")))
        reussite.append({"nom": x["nom"], "reussis": num, "tentes": den, "pct": round(num / den * 100) if den else None})
    return {
        "reussite": reussite,
        "player": player, "player_id": int(me["player_id"]), "team": fr.get(me["team"], me["team"]),
        "poste": cfg.raw.get("position_labels", {}).get(me["position"], me["position"]), "role": me["role"],
        "minutes": int(round(me["minutes"])), "matches": int(me["matches"]),
        "bassin": {"type": bassin, "code": code, "singulier": noms[0], "pluriel": noms[1],
                   "effectif": int(r["effectif"]), "min_minutes": cfg.min_minutes},
        "note": round(float(r["note"]), 1), "rang": int(r["rang"]),
        "criteres": [{"k": c["k"], "nom": c["nom"], "court": c.get("court", c["nom"]), "famille": c["famille"], "valeur": round(float(r[c["k"]]), 4), "rang": int(r[c["k"] + "_rg"]),
                      "max": round(float(r[c["k"] + "_max"]), 2), "mediane": round(float(r[c["k"] + "_med"]), 2),
                      "centile": int(round(float(r[c["k"] + "_ctl"])))} for c in spec["criteres"]],
        "proches": sim,
        "notes_bassin": [round(float(v), 1) for v in sorted(prof["note"])],
    }


def run(cfg: Config) -> dict:
    """Table gold.player_profiles (bassin « poste », rôles dont les critères sont définis)
    et un fichier JSON par joueur de l'équipe suivie et par bassin."""
    con = duckdb.connect(str(cfg.path("warehouse")))
    df = joueurs(con, cfg.min_minutes)
    blocs = []
    for code, spec in cfg.raw["roles"].items():
        if spec.get("criteres") and (df["role"] == code).any():
            blocs.append(profil_bassin(df[df["role"] == code], [c["k"] for c in spec["criteres"]]))
    profils = pd.concat(blocs, ignore_index=True)
    con.register("df_profils", profils)
    con.execute("create or replace table gold.player_profiles as select * from df_profils")
    gold_dir = cfg.path("gold")
    con.execute(f"copy gold.player_profiles to '{gold_dir / 'player_profiles.parquet'}' (format parquet)")
    con.execute(f"copy gold.player_profiles to '{gold_dir / 'player_profiles.csv'}' (header, delimiter ',')")
    con.close()

    out_dir = cfg.path("outputs") / "fiches"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    equipe = df[(df["team"] == cfg.team) & df["role"].isin([c for c, s in cfg.raw["roles"].items() if s.get("criteres")])]
    noms = list(equipe["player"]) + [p for p in cfg.raw.get("fiches_supplementaires", []) if (df["player"] == p).any()]
    for player in noms:
        for bassin in ("poste", "ligne"):
            data = fiche(cfg, df, player, bassin)
            (out_dir / f"{_slug(player)}_{bassin}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
            n += 1
    # classement de l'équipe suivie : chaque joueur noté parmi son rôle, et ceux qui ne le sont pas (avec la raison)
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    tous = con.execute("select player, position, minutes, matches from gold.player_tournament where team = ? order by minutes desc, player", [cfg.team]).df()
    con.close()
    labels = cfg.raw.get("position_labels", {})
    notes = profils[profils["team"] == cfg.team].sort_values(["note", "player"], ascending=[False, True])
    classement = {
        "equipe": cfg.team, "min_minutes": cfg.min_minutes,
        "joueurs": [{"player": r.player, "poste": labels.get(r.position, r.position), "role": r.role,
                     "pluriel": cfg.raw["roles"][r.role]["pluriel"], "minutes": int(round(r.minutes)), "matches": int(r.matches),
                     "note": round(float(r.note), 1), "rang": int(r.rang), "effectif": int(r.effectif)} for r in notes.itertuples()],
        "non_notes": [{"player": r.player, "minutes": int(round(r.minutes)),
                       "raison": "gardien" if r.position == "Goalkeeper" else "temps de jeu"}
                      for r in tous.itertuples() if r.player not in set(notes["player"])],
    }
    (cfg.path("outputs") / "classement.json").write_text(json.dumps(classement, indent=1, ensure_ascii=False), encoding="utf-8")
    log.info("profils : %d joueurs profilés, %d fiches écrites dans %s", len(profils), n, out_dir.name)
    return {"profiled": len(profils), "fiches": n}

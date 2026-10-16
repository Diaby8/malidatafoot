"""Le groupe K des éliminatoires de la CAN 2027, simulé match par match.

La question : le Mali va-t-il à la CAN 2027, et finit-il premier du groupe ?

1. Un modèle de buts (Dixon et Coles, 1997), écrit en clair :
   - chaque équipe marque selon une loi de Poisson : log(buts attendus) = a + b × (écart d'Elo / 100) + c (domicile) + d (extérieur) ;
   - la correction de Dixon et Coles (paramètre rho) rend aux scores serrés (0-0, 1-0, 0-1, 1-1) leur vraie fréquence :
     un modèle de Poisson simple sous-estime les matchs nuls ;
   - appris sur les matchs officiels entre sélections africaines depuis 2000 (CAN, éliminatoires CAN et Coupe du monde),
     avec l'Elo de chaque équipe avant le match (elo.py).
2. Un test honnête avant d'y croire : appris sur 2000-2019, jugé sur 2020-2026, des matchs qu'il n'a jamais vus.
3. La simulation : les matchs restants sont joués 100 000 fois (Elo du jour, tenu fixe), puis on classe le groupe avec
   les règles de la CAF : points, puis confrontations directes (points, différence de buts, buts marqués), puis différence
   de buts générale et buts marqués. Les deux premiers vont à la CAN.
"""
from __future__ import annotations

import json
import math

import duckdb
import numpy as np
import pandas as pd

from .analyses import poisson_irls
from .config import ROOT, Config, get_logger

log = get_logger("simulation")
OFFICIELS = ("African Cup of Nations", "African Cup of Nations qualification", "FIFA World Cup qualification")
MAX_BUTS = 10


# ------------------------------------------------------------------------------------------------ le modèle
def matchs_africains(con, depuis: str = "2000-01-01") -> pd.DataFrame:
    """Matchs officiels entre sélections africaines (= ont joué la CAN ou ses éliminatoires depuis 2000), avec l'Elo avant le match."""
    return con.execute(f"""
        with caf as (select home_team e from silver.intl_matches where tournament like 'African Cup of Nations%' and date >= '{depuis}'
                     union select away_team from silver.intl_matches where tournament like 'African Cup of Nations%' and date >= '{depuis}')
        select date, home_team, away_team, home_score, away_score, neutral, elo_home_avant, elo_away_avant
        from gold.elo_matchs
        where tournament in {OFFICIELS} and date >= '{depuis}'
          and home_team in (select e from caf) and away_team in (select e from caf)
        order by date""").df()


def _plan(ecart, dom, ext):
    return np.column_stack([np.ones(len(ecart)), ecart, dom, ext])


def lambdas(b, elo_dom, elo_ext, neutre):
    """Buts attendus de l'équipe qui reçoit et de l'autre."""
    e = (np.asarray(elo_dom, float) - np.asarray(elo_ext, float)) / 100
    lieu = 1.0 - np.asarray(neutre, float)
    return np.exp(b[0] + b[1] * e + b[2] * lieu), np.exp(b[0] - b[1] * e + b[3] * lieu)


def tau(x, y, lh, la, rho):
    """Correction de Dixon et Coles, pour les scores 0-0, 0-1, 1-0 et 1-1 seulement."""
    return np.where((x == 0) & (y == 0), 1 - lh * la * rho,
           np.where((x == 0) & (y == 1), 1 + lh * rho,
           np.where((x == 1) & (y == 0), 1 + la * rho,
           np.where((x == 1) & (y == 1), 1 - rho, 1.0))))


def ajuster(m: pd.DataFrame) -> dict:
    """Étape 1 : la régression de Poisson (une ligne par équipe et par match). Étape 2 : rho, au maximum de vraisemblance."""
    dom = (~m.neutral.astype(bool)).astype(float).to_numpy()
    e = ((m.elo_home_avant - m.elo_away_avant) / 100).to_numpy()
    X = np.vstack([_plan(e, dom, np.zeros(len(m))), _plan(-e, np.zeros(len(m)), dom)])
    y = np.concatenate([m.home_score.to_numpy(float), m.away_score.to_numpy(float)])
    b = poisson_irls(X, y)
    lh, la = lambdas(b, m.elo_home_avant, m.elo_away_avant, m.neutral.astype(bool))
    x, z = m.home_score.to_numpy(), m.away_score.to_numpy()
    grille = np.linspace(-0.25, 0.25, 501)
    vrais = [np.log(np.clip(tau(x, z, lh, la, r), 1e-12, None)).sum() for r in grille]
    return {"b": b.tolist(), "rho": float(grille[int(np.argmax(vrais))]), "matchs": int(len(m))}


def matrice(modele: dict, elo_dom: float, elo_ext: float, neutre: bool = False, rho: float | None = None) -> np.ndarray:
    """Probabilité de chaque score (buts de l'équipe qui reçoit en ligne, de l'autre en colonne), de 0 à MAX_BUTS."""
    lh, la = (float(v[0]) for v in lambdas(modele["b"], [elo_dom], [elo_ext], [neutre]))
    k = np.arange(MAX_BUTS + 1)
    ph = np.exp(-lh) * lh ** k / np.array([math.factorial(i) for i in k])
    pa = np.exp(-la) * la ** k / np.array([math.factorial(i) for i in k])
    p = np.outer(ph, pa) * tau(k[:, None], k[None, :], lh, la, modele["rho"] if rho is None else rho)
    return p / p.sum()


def vnd(p: np.ndarray) -> tuple[float, float, float]:
    """Victoire de l'équipe qui reçoit, nul, victoire de l'autre."""
    return float(np.tril(p, -1).sum()), float(np.trace(p)), float(np.triu(p, 1).sum())


def tester(m: pd.DataFrame, coupure: str = "2020-01-01") -> dict:
    """Le test honnête : appris avant la coupure, jugé après. Score de Brier (0 = parfait ; plus bas = mieux),
    calibration du favori, et part de matchs nuls annoncée contre réelle. Comparé à Poisson simple (rho = 0)
    et à une prédiction naïve (les fréquences moyennes)."""
    avant, apres = m[m.date < coupure], m[m.date >= coupure]
    mod = ajuster(avant)
    res = np.select([apres.home_score > apres.away_score, apres.home_score == apres.away_score], [0, 1], 2)
    sortie = {"appris_sur": int(len(avant)), "teste_sur": int(len(apres)), "rho": mod["rho"]}
    for nom, rho in (("dixon_coles", mod["rho"]), ("poisson_simple", 0.0)):
        P = np.array([vnd(matrice(mod, r.elo_home_avant, r.elo_away_avant, bool(r.neutral), rho)) for r in apres.itertuples()])
        fav = P[:, [0, 2]].max(1); cote = np.where(P[:, 0] >= P[:, 2], 0, 2)
        cal = []
        for lo, hi in ((0.3, 0.45), (0.45, 0.6), (0.6, 0.75), (0.75, 1.01)):
            s = (fav >= lo) & (fav < hi)
            cal.append({"tranche": f"{lo:.0%}-{min(hi, 1):.0%}", "matchs": int(s.sum()),
                        "annonce": float(fav[s].mean()), "reel": float((res[s] == cote[s]).mean())})
        sortie[nom] = {"brier": float(np.mean(((P - np.eye(3)[res]) ** 2).sum(1))),
                       "nuls_annonces": float(P[:, 1].mean()), "nuls_reels": float((res == 1).mean()),
                       "bon_resultat_le_plus_probable": float((P.argmax(1) == res).mean()), "calibration": cal}
    freq = np.bincount(np.select([avant.home_score > avant.away_score, avant.home_score == avant.away_score], [0, 1], 2), minlength=3) / len(avant)
    sortie["naif"] = {"brier": float(np.mean(((freq - np.eye(3)[res]) ** 2).sum(1))), "frequences": freq.tolist()}
    return sortie


# ------------------------------------------------------------------------------------------------ le classement
def classer(equipes: list[str], matchs: list[tuple[str, str, int, int]]) -> list[str]:
    """Classement CAF : points ; à égalité, mini-classement des confrontations directes (points, différence, buts) ;
    puis différence de buts générale, buts marqués. (Fair-play et tirage au sort non modélisés.)"""
    def table(eqs, ms):
        t = {e: [0, 0, 0] for e in eqs}  # points, buts pour, buts contre
        for h, a, x, y in ms:
            if h in t and a in t:
                t[h][1] += x; t[h][2] += y; t[a][1] += y; t[a][2] += x
                t[h][0] += 3 if x > y else 1 if x == y else 0
                t[a][0] += 3 if y > x else 1 if x == y else 0
        return t
    g = table(equipes, matchs)
    def ordre(eqs):
        groupes: dict[int, list[str]] = {}
        for e in eqs:
            groupes.setdefault(g[e][0], []).append(e)
        sortie = []
        for p in sorted(groupes, reverse=True):
            ex = groupes[p]
            if len(ex) > 1:
                d = table(ex, matchs)
                ex = sorted(ex, key=lambda e: (d[e][0], d[e][1] - d[e][2], d[e][1], g[e][1] - g[e][2], g[e][1]), reverse=True)
            sortie += ex
        return sortie
    return ordre(equipes)


def simuler(modele: dict, elo: dict, joues: list, restants: list, n: int = 100_000, graine: int = 2027) -> dict:
    """Joue les matchs restants n fois. Renvoie, pour chaque simulation, le classement et les scores des matchs restants."""
    rng = np.random.default_rng(graine)
    tirages = []
    for h, a in restants:
        p = matrice(modele, elo[h], elo[a]).ravel()
        idx = rng.choice(p.size, size=n, p=p)
        tirages.append((idx // (MAX_BUTS + 1), idx % (MAX_BUTS + 1)))
    equipes = sorted({t for m in joues for t in m[:2]} | {t for m in restants for t in m})
    rangs, points = [], []
    for i in range(n):
        ms = list(joues) + [(h, a, int(tirages[k][0][i]), int(tirages[k][1][i])) for k, (h, a) in enumerate(restants)]
        cl = classer(equipes, ms)
        rangs.append({e: cl.index(e) + 1 for e in equipes})
        pt = {e: 0 for e in equipes}
        for h, a, x, y in ms:
            pt[h] += 3 if x > y else 1 if x == y else 0
            pt[a] += 3 if y > x else 1 if x == y else 0
        points.append(pt)
    return {"equipes": equipes, "rangs": pd.DataFrame(rangs), "points": pd.DataFrame(points), "tirages": tirages}


# ------------------------------------------------------------------------------------------------ l'étape du pipeline
def run(cfg: Config, n: int = 100_000) -> dict:
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    m = matchs_africains(con)
    test = tester(m)
    modele = ajuster(m)
    cal = pd.read_csv(ROOT / "registre" / "calendrier_groupe_k.csv")
    elo = dict(con.execute("select equipe, elo from gold.elo_actuel").fetchall())
    joues, restants = [], []
    for r in cal.itertuples():
        s = con.execute("select home_score, away_score from silver.intl_matches where date = ? and home_team = ? and away_team = ?",
                        [r.date, r.domicile, r.exterieur]).fetchone()
        (joues.append((r.domicile, r.exterieur, int(s[0]), int(s[1]))) if s else restants.append((r.domicile, r.exterieur)))
    con.close()
    sim = simuler(modele, elo, joues, restants, n)
    # robustesse : le même calcul avec un modèle appris seulement depuis 2010 (football africain plus récent)
    m10 = ajuster(m[m.date >= "2010-01-01"]); s10 = simuler(m10, elo, joues, restants, 30_000, graine=5)
    R, P = sim["rangs"], sim["points"]
    equipe = cfg.raw["resultats_internationaux"]["equipe"]
    # les deux matchs de novembre contre le Rwanda, vus du Mali
    k1, k2 = restants.index((equipe, "Rwanda")), restants.index(("Rwanda", equipe))
    bamako = np.sign(sim["tirages"][k1][0] - sim["tirages"][k1][1])
    kigali = np.sign(sim["tirages"][k2][1] - sim["tirages"][k2][0])
    scen = {"deux_victoires": (bamako == 1) & (kigali == 1), "une_victoire_un_nul": ((bamako == 1) & (kigali == 0)) | ((bamako == 0) & (kigali == 1)),
            "deux_nuls": (bamako == 0) & (kigali == 0), "une_victoire_une_defaite": ((bamako == 1) & (kigali == -1)) | ((bamako == -1) & (kigali == 1)),
            "nul_et_defaite": ((bamako == 0) & (kigali == -1)) | ((bamako == -1) & (kigali == 0)), "deux_defaites": (bamako == -1) & (kigali == -1),
            "victoire_bamako_defaite_kigali": (bamako == 1) & (kigali == -1)}
    # le Mali à l'extérieur contre bien plus faible que lui (au moins 200 points d'Elo d'écart), comparé au favori africain moyen
    # dans la même situation (même critère, matchs officiels africains depuis 2015). Le Rwanda est à 248 points sous le Mali.
    ext = m[~m.neutral.astype(bool)].copy(); ext["ecart"] = ext.elo_away_avant - ext.elo_home_avant
    ext = ext[(ext.ecart >= 200) & (ext.date >= "2015-01-01")]
    vnd_ = lambda d: {"matchs": int(len(d)), "victoires": int((d.away_score > d.home_score).sum()),
                      "nuls": int((d.away_score == d.home_score).sum()), "defaites": int((d.away_score < d.home_score).sum())}
    mx = ext[ext.away_team == equipe]
    exterieur = {"critere": "visiteur plus fort d'au moins 200 points d'Elo, matchs officiels africains depuis 2015",
                 "tous": vnd_(ext), equipe: vnd_(mx),
                 "matchs_mali": [[str(r.date)[:10], r.home_team, int(r.home_score), int(r.away_score)] for r in mx.itertuples()]}
    rm = R[equipe].to_numpy(); pm = P[equipe].to_numpy()
    sortie = {
        "question": "Le Mali va-t-il à la CAN 2027, et finit-il premier du groupe K ?",
        "modele": {"methode": "Poisson + correction de Dixon et Coles ; buts selon l'écart d'Elo et le lieu",
                   "appris_sur_matchs": modele["matchs"], "coefficients": modele["b"], "rho": modele["rho"]},
        "test_honnete": test,
        "elo_du_jour": {e: elo[e] for e in sim["equipes"]},
        "joues": joues, "restants": restants, "simulations": n,
        "equipes": {e: {"qualifie": float((R[e] <= 2).mean()), "premier": float((R[e] == 1).mean()),
                        "points_moyens": float(P[e].mean())} for e in sim["equipes"]},
        "points_mali": {int(k): float((pm == k).mean()) for k in np.unique(pm)},
        "qualifie_selon_points": {int(k): float((rm[pm == k] <= 2).mean()) for k in np.unique(pm)},
        "match_bamako": dict(zip(("victoire", "nul", "defaite"), vnd(matrice(modele, elo[equipe], elo["Rwanda"])))),
        "match_kigali": dict(zip(("victoire", "nul", "defaite"), vnd(matrice(modele, elo["Rwanda"], elo[equipe]))[::-1])),
        "novembre": {k: {"probabilite": float(v.mean()), "qualifie": float((rm[v] <= 2).mean()) if v.any() else None,
                         "premier": float((rm[v] == 1).mean()) if v.any() else None} for k, v in scen.items()},
        "exterieur_contre_plus_faible": exterieur,
        "robustesse_modele_depuis_2010": {"matchs": m10["matchs"], "qualifie": float((s10["rangs"][cfg.raw["resultats_internationaux"]["equipe"]] <= 2).mean()),
                                          "premier": float((s10["rangs"][cfg.raw["resultats_internationaux"]["equipe"]] == 1).mean())},
        "regles": "Les deux premiers du groupe vont à la CAN 2027 (CAF). Classement simplifié : points, confrontations directes (points, différence, buts ; un seul passage, sans buts à l'extérieur), différence de buts générale, buts. Les critères omis changent la probabilité du Mali de moins de 0,3 point (recomptage du 14 octobre 2026).",
        "limites": "Sur 2020-2026, le modèle annonce un peu moins de nuls qu'il n'y en a eu (23 % contre 26 %) et, quand il donne le favori à 60-75 %, celui-ci gagne un peu moins souvent ; Elo et paramètres tenus fixes pendant la simulation, donc les probabilités sont sans doute un peu trop sûres d'elles ; ni blessures, ni compositions ; fair-play et tirage au sort non modélisés.",
        "source": "martj42/international_results (CC0) ; Elo MaliDataFoot ; calendrier : registre/calendrier_groupe_k.csv",
    }
    dossier = cfg.path("outputs") / "analyses"
    dossier.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(cfg.path("warehouse")), read_only=True)
    terrain = avantage_terrain(con)
    con.close()
    (dossier / "avantage_terrain.json").write_text(json.dumps(terrain, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("avantage du terrain (points d'Elo) : %s", ", ".join(f"{z} {v['ecart_domicile_exterieur_en_points_elo']:.0f}" for z, v in terrain.items()))
    (dossier / "simulation_groupe_k.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    t = sortie["equipes"][equipe]
    log.info("groupe K, %d simulations : %s qualifié %.1f %%, premier %.1f %% ; test du modèle : Brier %.3f (Poisson simple %.3f, naïf %.3f)",
             n, equipe, 100 * t["qualifie"], 100 * t["premier"], test["dixon_coles"]["brier"], test["poisson_simple"]["brier"], test["naif"]["brier"])
    return sortie


# ------------------------------------------------------------------------------------------------ l'avantage du terrain
CONMEBOL = ("Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Paraguay", "Peru", "Uruguay", "Venezuela")
ZONES = {  # continent : (compétitions officielles, définition des équipes du continent)
    "Afrique": (("African Cup of Nations", "African Cup of Nations qualification", "FIFA World Cup qualification"), "African Cup of Nations%"),
    "Europe": (("UEFA Euro", "UEFA Euro qualification", "FIFA World Cup qualification"), "UEFA Euro%"),
    "Amérique du Sud": (("Copa América", "FIFA World Cup qualification"), None),
    "Asie": (("AFC Asian Cup", "AFC Asian Cup qualification", "FIFA World Cup qualification"), "AFC Asian Cup%"),
}


def matchs_zone(con, zone: str, depuis: str = "2000-01-01") -> pd.DataFrame:
    comps, motif = ZONES[zone]
    if motif:
        equipes = f"""(select home_team from silver.intl_matches where tournament like '{motif}' and date >= '{depuis}'
                       union select away_team from silver.intl_matches where tournament like '{motif}' and date >= '{depuis}')"""
    else:
        equipes = "(" + ", ".join("'" + e + "'" for e in CONMEBOL) + ")"
    return con.execute(f"""select date, home_team, away_team, home_score, away_score, neutral, elo_home_avant, elo_away_avant
        from gold.elo_matchs where tournament in {comps} and date >= '{depuis}'
          and home_team in {equipes} and away_team in {equipes} order by date""").df()


def avantage_terrain(con, tirages: int = 300, graine: int = 1) -> dict:
    """Combien vaut le fait de jouer chez soi plutôt que chez l'adversaire, continent par continent ?
    Même modèle de buts que pour la simulation. L'écart domicile / extérieur est traduit en points d'Elo :
    (effet domicile − effet extérieur) / effet de 100 points d'Elo × 100. Intervalle à 95 % par rééchantillonnage des matchs."""
    rng = np.random.default_rng(graine)
    sortie = {}
    for zone in ZONES:
        m = matchs_zone(con, zone)
        mod = ajuster(m); b = mod["b"]
        ecart = lambda b: (b[2] - b[3]) / b[1] * 100  # noqa: E731
        boot = []
        for _ in range(tirages):
            s = m.iloc[rng.integers(0, len(m), len(m))]
            boot.append(ecart(ajuster(s)["b"]))
        v, n, d = vnd(matrice(mod, 1600, 1600))
        sortie[zone] = {"matchs": int(len(m)), "matchs_sur_terrain_neutre": int(m.neutral.astype(bool).sum()),
                        "ecart_domicile_exterieur_en_points_elo": float(ecart(b)),
                        "intervalle_95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                        "equipes_egales": {"victoire_de_celle_qui_recoit": v, "nul": n, "victoire_de_celle_qui_se_deplace": d}}
    return sortie

"""Tests unitaires : logique d'aplatissement, temps de jeu, regroupement des postes, score."""
import duckdb
import pandas as pd
import pytest

from malidata.config import load_config
from malidata.gold import percentiles, player_score, position_group
from malidata.profils import centile_strict, profil_bassin, proches, role
from malidata.silver import build_minutes, flatten_event


def _event(**kw):
    base = {"id": "e1", "index": 1, "period": 1, "timestamp": "00:10:30.500", "minute": 10, "second": 30,
            "type": {"name": "Pass"}, "team": {"name": "Mali"}, "possession": 3,
            "possession_team": {"name": "Mali"}, "play_pattern": {"name": "Regular Play"}}
    base.update(kw)
    return base


def test_flatten_pass_reussie_et_ratee():
    ok = flatten_event(1, _event(location=[50, 40], **{"pass": {"end_location": [70, 30], "length": 22.4}}))
    assert ok["ts"] == pytest.approx(630.5)
    assert (ok["x"], ok["end_x"]) == (50, 70)
    assert ok["pass_outcome"] is None          # pas d'issue renseignée = passe réussie
    ko = flatten_event(1, _event(**{"pass": {"end_location": [70, 30], "outcome": {"name": "Incomplete"}}}))
    assert ko["pass_outcome"] == "Incomplete"


def test_flatten_tir_et_carton():
    shot = flatten_event(1, _event(type={"name": "Shot"}, shot={"statsbomb_xg": 0.31, "outcome": {"name": "Goal"},
                                                               "type": {"name": "Open Play"}, "end_location": [120, 40, 1]}))
    assert shot["shot_xg"] == 0.31 and shot["shot_outcome"] == "Goal"
    foul = flatten_event(1, _event(type={"name": "Foul Committed"}, foul_committed={"card": {"name": "Second Yellow"}}))
    assert foul["card"] == "Second Yellow"


@pytest.mark.parametrize("position,expected", [
    ("Goalkeeper", "GAR"), ("Right Center Back", "DEF"), ("Left Wing Back", "DEF"),
    ("Center Defensive Midfield", "MIL"), ("Right Attacking Midfield", "MIL"),
    ("Left Wing", "ATT"), ("Center Forward", "ATT"),
])
def test_groupes_de_postes(position, expected):
    assert position_group(position) == expected


def test_temps_de_jeu_remplacement_expulsion_et_arrets_de_jeu():
    """Mi-temps de 47 puis 50 minutes : un titulaire remplacé à la 60e (horloge) et son remplaçant
    se partagent tout le match ; un expulsé à la 30e ne joue que 30 minutes."""
    con = duckdb.connect()
    con.execute("create schema silver")
    events = pd.DataFrame([
        dict(match_id=1, period=1, ts=47 * 60.0, type="Half End", team="A", player_id=None, card=None, sub_replacement_id=None, sub_replacement=None),
        dict(match_id=1, period=2, ts=50 * 60.0, type="Half End", team="A", player_id=None, card=None, sub_replacement_id=None, sub_replacement=None),
        dict(match_id=1, period=2, ts=15 * 60.0, type="Substitution", team="A", player_id=10, card=None, sub_replacement_id=12, sub_replacement="Remplaçant"),
        dict(match_id=1, period=1, ts=30 * 60.0, type="Foul Committed", team="A", player_id=11, card="Red Card", sub_replacement_id=None, sub_replacement=None),
    ])
    xi = pd.DataFrame([dict(match_id=1, team="A", player_id=i, player=f"J{i}") for i in (9, 10, 11)])
    con.register("ev", events), con.register("xi", xi)
    con.execute("create table silver.events as select * from ev; create table silver.starting_xi as select * from xi")
    build_minutes(con)
    got = dict(con.execute("select player_id, minutes from silver.player_match_minutes").fetchall())
    assert got[9] == pytest.approx(90)            # match entier : 90 minutes, les arrêts de jeu ne s'ajoutent pas
    assert got[10] == pytest.approx(60)           # sorti à la 60e
    assert got[12] == pytest.approx(30)           # entré à la 60e, joue jusqu'au bout
    assert got[11] == pytest.approx(30)           # expulsé à la 30e
    assert got[10] + got[12] == pytest.approx(90)
    reel = dict(con.execute("select player_id, minutes_reelles from silver.player_match_minutes").fetchall())
    assert reel[9] == pytest.approx(97)           # le temps réellement écoulé reste disponible à côté


def test_score_borne_et_ordonne():
    cfg = load_config()
    pillars, weights = cfg.raw["score_pillars"], cfg.raw["score_weights"]
    metrics = [m for ms in pillars.values() for m in ms]
    rows = []
    for i in range(6):                             # six attaquants, du plus faible au plus fort partout
        rows.append({"player_id": i, "pos_group": "ATT", "minutes": 200 + 50 * i, **{m: float(i) for m in metrics}})
    rows.append({"player_id": 99, "pos_group": "ATT", "minutes": 20, **{m: 50.0 for m in metrics}})  # trop peu joué
    scored = player_score(percentiles(pd.DataFrame(rows), metrics, cfg.min_minutes), pillars, weights)
    assert 99 not in set(scored["player_id"])
    assert scored["score"].between(0, 100).all()
    assert list(scored.sort_values("score")["player_id"]) == [0, 1, 2, 3, 4, 5]
    assert scored.loc[scored["player_id"] == 5, "score"].iloc[0] == pytest.approx(100)


def test_poids_du_score_somment_a_100():
    for group, w in load_config().raw["score_weights"].items():
        assert sum(w.values()) == 100, group


@pytest.mark.parametrize("position,expected", [
    ("Goalkeeper", "GAR"), ("Right Center Back", "DC"), ("Center Back", "DC"), ("Right Back", "LAT"),
    ("Left Wing Back", "LAT"), ("Center Defensive Midfield", "MDF"), ("Left Center Midfield", "MIL"),
    ("Right Attacking Midfield", "MOF"), ("Left Wing", "MOF"), ("Center Forward", "ATT"), (None, None),
])
def test_roles_fins(position, expected):
    assert role(position) == expected


def test_centile_strict_ex_aequo_et_extremes():
    """Trois joueurs à zéro ne dépassent personne ; le meilleur, seul, dépasse tout le monde."""
    c = centile_strict(pd.Series([0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 5.0]))
    assert list(c[:3]) == [0, 0, 0]
    assert c[3] == pytest.approx(50)               # dépasse 3 des 6 autres
    assert c[4] == c[5] == pytest.approx(4 / 6 * 100)
    assert c[6] == pytest.approx(100)


def test_note_est_la_moyenne_des_centiles_affiches():
    pop = pd.DataFrame({"player_id": range(5), "player": list("abcde"), "team": "X",
                        "a": [0.0, 1, 2, 3, 4], "b": [4.0, 3, 2, 1, 0]})
    prof = profil_bassin(pop, ["a", "b"])
    assert prof["note"].tolist() == pytest.approx([50] * 5)      # fort d'un côté, faible de l'autre
    assert (prof["rang"] == 1).all() and (prof["effectif"] == 5).all()
    prof = profil_bassin(pop, ["a"])
    assert prof.sort_values("rang")["player"].tolist() == list("edcba")
    assert prof.loc[prof["player"] == "e", "note"].iloc[0] == pytest.approx(100)


def test_profils_proches_dans_le_bassin():
    pop = pd.DataFrame({"player_id": range(4), "player": list("abcd"), "team": "X", "a": [0.0, 1, 2, 9], "b": [0.0, 1, 2, 9]})
    prof = profil_bassin(pop, ["a", "b"])
    p = proches(prof, 1, ["a", "b"], n=2)
    assert {x["player"] for x in p} == {"a", "c"} and all(x["player"] != "b" for x in p)
    assert p[0]["proche"] == pytest.approx(100 - 100 / 3, abs=0.5)   # un rang d'écart sur trois


def test_rang_par_critere_et_ex_aequo():
    pop = pd.DataFrame({"player_id": range(4), "player": list("abcd"), "team": "X", "a": [5.0, 5.0, 2.0, 0.0]})
    prof = profil_bassin(pop, ["a"])
    assert prof["a_rg"].tolist() == [1, 1, 3, 4]          # deux premiers ex æquo, le suivant est troisième
    assert prof["a_max"].iloc[0] == 5 and prof["a_med"].iloc[0] == 3.5


def test_note_ex_aequo_meme_rang():
    """Deux joueurs dont la note est mathématiquement égale partagent le même rang, même si l'ordre des additions diffère."""
    pop = pd.DataFrame({"player_id": range(7), "a": [0, 1, 2, 3, 4, 5, 6], "b": [6, 4, 5, 3, 1, 2, 0], "c": [3, 5, 2, 0, 6, 1, 4]})
    prof = profil_bassin(pop, ["a", "b", "c"])
    egaux = prof[(prof["a"] + prof["b"] + prof["c"]) == 9]            # même somme de places : même note
    assert len(egaux) >= 2 and egaux["rang"].nunique() == 1


def test_fichiers_texte_lus_en_utf8():
    """Sous Windows, Python lit par défaut en cp1252 : « Traoré » devient « TraorÃ© » (bug du 11 octobre 2026).
    Toute lecture ou écriture de texte du pipeline doit donc préciser encoding="utf-8"."""
    import re
    from pathlib import Path
    racine = Path(__file__).resolve().parents[1]
    fautifs = []
    for f in list((racine / "malidata").rglob("*.py")) + list((racine / "visuels").glob("*.py")):
        for n, ligne in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\.(read_text|write_text)\(", ligne) and "encoding" not in ligne:
                fautifs.append(f"{f.name}:{n}")
            if re.search(r"(?<![\w.])open\([^)]*\.(json|csv|html|md|txt|yaml)['\"]", ligne) and "encoding" not in ligne:
                fautifs.append(f"{f.name}:{n}")
    assert not fautifs, "fichiers texte lus sans encoding='utf-8' : " + ", ".join(fautifs)


def test_aigles_vus_du_cote_du_mali():
    """Le modèle gold des Aigles remet chaque match du côté du Mali : adversaire, buts, lieu, tirs au but."""
    from pathlib import Path
    racine = Path(__file__).resolve().parents[1]
    con = duckdb.connect()
    con.execute("create schema silver; create schema gold")
    con.execute("""create table silver.intl_matches as select * from (values
        (date '2026-09-25', 'Mali', 'Cape Verde', 3, 1, 'African Cup of Nations qualification', 'Bamako', 'Mali', false),
        (date '2026-09-29', 'Liberia', 'Mali', 0, 1, 'African Cup of Nations qualification', 'Monrovia', 'Liberia', false),
        (date '2026-01-03', 'Mali', 'Tunisia', 1, 1, 'African Cup of Nations', 'Casablanca', 'Morocco', true),
        (date '2026-01-04', 'Senegal', 'Egypt', 2, 0, 'Friendly', 'Dakar', 'Senegal', false)
    ) t(date, home_team, away_team, home_score, away_score, tournament, city, country, neutral)""")
    con.execute("""create table silver.intl_shootouts as select * from (values
        (date '2026-01-03', 'Mali', 'Tunisia', 'Mali')) t(date, home_team, away_team, winner)""")
    for f in sorted((racine / "sql" / "aigles").glob("*.sql")):
        con.execute(f.read_text(encoding="utf-8").replace("{equipe}", "Mali"))
    df = con.execute("select * from gold.aigles_matchs order by date").df()
    assert len(df) == 3                                     # le match Sénégal–Égypte n'est pas gardé
    tun, cpv, lib = df.iloc[0], df.iloc[1], df.iloc[2]
    assert (cpv.adversaire, cpv.buts_pour, cpv.buts_contre, cpv.resultat, cpv.lieu) == ("Cape Verde", 3, 1, "V", "domicile")
    assert (lib.adversaire, lib.buts_pour, lib.buts_contre, lib.resultat, lib.lieu) == ("Liberia", 1, 0, "V", "extérieur")
    assert (tun.resultat, tun.lieu, bool(tun.tirs_au_but), bool(tun.tab_gagnes)) == ("N", "neutre", True, True)
    bilan = con.execute("select * from gold.aigles_bilan_annuel").df().iloc[0]
    assert (bilan.matchs, bilan.victoires, bilan.nuls, bilan.defaites, bilan.buts_pour) == (3, 2, 1, 0, 5)


def test_elo_methode_eloratings():
    """Deux équipes à 1500. Victoire 1-0 à domicile en amical : We = 1/(10^-0,25 + 1), K = 20, G = 1.
    Puis 3-0 sur terrain neutre en Coupe du monde : We = 0,5, K = 60, G = (11 + 3) / 8."""
    from malidata.elo import calculer, multiplicateur, poids
    assert (poids("FIFA World Cup"), poids("African Cup of Nations"), poids("FIFA World Cup qualification"),
            poids("UEFA Nations League"), poids("Friendly"), poids("COSAFA Cup")) == (60, 50, 40, 40, 20, 30)
    assert (multiplicateur(0), multiplicateur(-1), multiplicateur(2), multiplicateur(-4)) == (1, 1, 1.5, 15 / 8)
    m = pd.DataFrame([("2020-01-01", "A", "B", 1, 0, "Friendly", False), ("2020-02-01", "C", "D", 3, 0, "FIFA World Cup", True),
                      ("2020-03-01", "A", "C", 2, 2, "Friendly", True)],
                     columns=["date", "home_team", "away_team", "home_score", "away_score", "tournament", "neutral"])
    e = calculer(m, suivie="A")
    d1 = 20 * (1 - 1 / (10 ** (-100 / 400) + 1))
    assert e.loc[0, "elo_home_apres"] == pytest.approx(1500 + d1) and e.loc[0, "elo_away_apres"] == pytest.approx(1500 - d1)
    assert e.loc[1, "elo_home_apres"] - 1500 == pytest.approx(60 * 1.75 * 0.5)
    # nul : le moins bien classé gagne des points ; la somme ne bouge pas
    assert e.loc[2, "elo_home_apres"] > e.loc[2, "elo_home_avant"]
    assert (e.elo_home_apres + e.elo_away_apres - e.elo_home_avant - e.elo_away_avant).abs().max() < 1e-9
    # rang avant le match : C (1552,5) est devant A (1507,2) le 1er mars
    assert (e.loc[2, "rang_home_avant"], e.loc[2, "rang_away_avant"]) == (2, 1)
    assert pd.isna(e.loc[1, "rang_home_avant"])     # match sans l'équipe suivie : pas de rang


def test_poisson_irls_retrouve_les_coefficients():
    import numpy as np
    from malidata.analyses import poisson_cdf, poisson_irls
    rng = np.random.default_rng(1)
    x = rng.normal(size=20000)
    X = np.column_stack([np.ones_like(x), x])
    y = rng.poisson(np.exp(-0.3 + 0.25 * x))
    b = poisson_irls(X, y.astype(float))
    assert b == pytest.approx([-0.3, 0.25], abs=0.02)
    assert poisson_cdf(0, 2.0) == pytest.approx(np.exp(-2.0)) and poisson_cdf(50, 2.0) == pytest.approx(1.0)


def test_calcul_fifa():
    """Formule FIFA : à points égaux, une victoire en éliminatoires rapporte 25 × 0,5 ; ce que l'un gagne, l'autre le perd ;
    en élimination directe d'une phase finale, le perdant ne perd rien ; tirs au but : 0,75 et 0,5."""
    from malidata import fifa
    assert fifa.match(1500, 1500, "V", 25) == pytest.approx((1512.5, 1487.5))
    a, b = fifa.match(1474.14, 1156.16, "N", 25)
    assert a - 1474.14 == pytest.approx(-(b - 1156.16))
    assert fifa.match(1500, 1500, "D", 40, elimination_directe=True)[0] == 1500
    assert fifa.match(1500, 1500, "TAB_V", 40)[0] == pytest.approx(1510)
    s = {x["resultats"]: x["ecart"] for x in fifa.scenarios(1474.14, 1156.16, 25)}
    assert len(s) == 9 and [k for k, v in s.items() if v > 0] == ["VV"]


def test_simulation_classement_et_modele():
    import numpy as np
    from malidata import simulation as s
    # A et B finissent à 7 points ; B a une bien meilleure différence de buts (+11 contre +1),
    # mais A a pris 4 points sur 6 contre B : la règle CAF met A devant
    ms = [("A", "B", 1, 0), ("B", "A", 0, 0), ("A", "C", 1, 0), ("C", "A", 1, 0), ("B", "C", 6, 0), ("C", "B", 0, 6)]
    assert s.classer(["A", "B", "C"], ms) == ["A", "B", "C"]
    # la matrice des scores est une vraie loi de probabilité, et le favori est bien favori
    mod = {"b": [0.06, 0.19, 0.29, -0.30], "rho": -0.03}
    p = s.matrice(mod, 1750, 1500)
    assert abs(p.sum() - 1) < 1e-9 and (p >= 0).all()
    v, n, d = s.vnd(p)
    assert v > d and abs(v + n + d - 1) < 1e-9
    # la simulation est reproductible et chaque simulation a exactement deux qualifiés
    sim = s.simuler(mod, {"A": 1700, "B": 1500, "C": 1400}, [("A", "B", 1, 0)], [("B", "A"), ("A", "C"), ("C", "A"), ("B", "C"), ("C", "B")], n=500)
    assert ((sim["rangs"] <= 2).sum(axis=1) == 2).all()
    assert sim["rangs"].equals(s.simuler(mod, {"A": 1700, "B": 1500, "C": 1400}, [("A", "B", 1, 0)], [("B", "A"), ("A", "C"), ("C", "A"), ("B", "C"), ("C", "B")], n=500)["rangs"])


def test_forfaits_retires_ou_score_du_terrain():
    """Seulement les matchs joués : un tapis vert est retiré, ou remis au score du terrain ; un registre faux arrête tout."""
    import datetime as dt
    from malidata.aigles import appliquer_forfaits
    d = lambda s: dt.date.fromisoformat(s)  # noqa: E731
    m = pd.DataFrame([
        {"date": d("2021-03-24"), "home_team": "Chad", "away_team": "Namibia", "home_score": 0, "away_score": 3},
        {"date": d("2021-03-28"), "home_team": "Mali", "away_team": "Chad", "home_score": 3, "away_score": 0},
        {"date": d("2023-11-15"), "home_team": "Equatorial Guinea", "away_team": "Namibia", "home_score": 0, "away_score": 3},
        {"date": d("2023-11-20"), "home_team": "Liberia", "away_team": "Equatorial Guinea", "home_score": 3, "away_score": 0},
        {"date": d("2025-03-21"), "home_team": "South Africa", "away_team": "Lesotho", "home_score": 0, "away_score": 3},
        {"date": d("2026-01-18"), "home_team": "Morocco", "away_team": "Senegal", "home_score": 3, "away_score": 0},
        {"date": d("2026-09-29"), "home_team": "Liberia", "away_team": "Mali", "home_score": 0, "away_score": 1},
    ])
    out, n = appliquer_forfaits(m)
    assert n == 6 and len(out) == 3
    assert not ((out["home_team"] == "Mali") & (out["away_team"] == "Chad")).any()
    finale = out[(out["home_team"] == "Morocco") & (out["away_team"] == "Senegal")].iloc[0]
    assert (finale["home_score"], finale["away_score"]) == (0, 1)
    m.loc[5, "home_score"] = 2  # le score officiel ne colle plus au registre : on doit s'arrêter
    with pytest.raises(ValueError):
        appliquer_forfaits(m)

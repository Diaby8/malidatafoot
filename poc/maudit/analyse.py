"""Le Mali est-il maudit a la CAN ? Comparaison resultats reels / attendus (modele Poisson + Dixon-Coles sur l'Elo)."""
import json
import math
import sys

import duckdb
import numpy as np
import pandas as pd

REPO = "/home/claude/repo/malidatafoot"
OUT = "/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad/poc_maudit"
sys.path.insert(0, REPO)
from malidata.simulation import ajuster, matrice, vnd, matchs_africains, MAX_BUTS  # noqa: E402

RNG = np.random.default_rng(1972)
con = duckdb.connect(f"{REPO}/data/warehouse.duckdb", read_only=True)

# ------------------------------------------------------------------ modeles
m00 = matchs_africains(con, "2000-01-01")
MOD00 = ajuster(m00)
m80 = matchs_africains(con, "1980-01-01")
m80 = m80[m80.date < "2000-01-01"]
MOD80 = ajuster(m80)
m10 = m00[m00.date >= "2010-01-01"]
MOD10 = ajuster(m10)


def modele_pour(date, variante="base"):
    if variante == "can":
        return MODCAN
    if variante == "tout2000":
        return MOD00
    if variante == "depuis2010":
        return MOD10 if date >= pd.Timestamp("2010-01-01") else (MOD00 if date >= pd.Timestamp("2000-01-01") else MOD80)
    return MOD00 if date >= pd.Timestamp("2000-01-01") else MOD80


# ------------------------------------------------------------------ matchs de phase finale, editions, tours
af = con.execute("""select date, home_team, away_team, home_score, away_score, neutral, elo_home_avant, elo_away_avant
                    from gold.elo_matchs where tournament = 'African Cup of Nations' order by date""").df()
af["gap"] = af.date.diff().dt.days.fillna(999)
af["ed_id"] = (af.gap > 60).cumsum()
lab = {}
for k, g in af.groupby("ed_id"):
    y = g.date.min().year
    lab[k] = {2022: 2021, 2024: 2023}.get(y, y)
af["edition"] = af.ed_id.map(lab)
af = af[af.edition.isin([1972] + list(range(1994, 2027)))].copy()

so = pd.read_csv(f"{REPO}/data/bronze/international_results/shootouts.csv", parse_dates=["date"])
so_key = {(r.date, r.home_team, r.away_team): r.winner for r in so.itertuples()}

af["tour"] = "groupe"
for ed, g in af.groupby("edition"):
    n = len(set(g.home_team) | set(g.away_team))
    B = 4 if n <= 8 else (8 if n <= 16 else 16)
    g = g.sort_values("date", kind="stable")
    fin = g.iloc[-1]
    finalistes = {fin.home_team, fin.away_team}
    av = g.iloc[-2]
    has3 = not ({av.home_team, av.away_team} & finalistes)
    k = B - 1 + int(has3)
    ko = g.iloc[-k:]
    noms = ["finale"] + (["3e place"] if has3 else []) + ["demi"] * 2 + ["quart"] * 4 + ["huitieme"] * 8
    for idx, nom in zip(ko.index[::-1], noms):
        af.loc[idx, "tour"] = nom
af["vainqueur"] = None
for i, r in af.iterrows():
    if r.home_score > r.away_score:
        af.at[i, "vainqueur"] = r.home_team
    elif r.home_score < r.away_score:
        af.at[i, "vainqueur"] = r.away_team
    elif r.tour != "groupe":
        af.at[i, "vainqueur"] = so_key.get((r.date, r.home_team, r.away_team))
MANQUANTS = {(pd.Timestamp("2024-02-10"), "South Africa", "DR Congo"): "South Africa"}  # absent de shootouts.csv (0-0, 6-5 t.a.b.)
for i, r in af[(af.tour != "groupe") & af.vainqueur.isna()].iterrows():
    af.at[i, "vainqueur"] = MANQUANTS.get((r.date, r.home_team, r.away_team))
assert af[(af.tour != "groupe") & af.vainqueur.isna()].empty, af[(af.tour != "groupe") & af.vainqueur.isna()]
hotes = {ed: set(g[~g.neutral].home_team) for ed, g in af.groupby("edition")}
# robustesse : modele appris sur les seuls matchs de groupe des phases finales 1994-2026 (plus serres que les eliminatoires)
MODCAN = ajuster(af[(af.edition >= 1994) & (af.tour == "groupe")].reset_index(drop=True))


# ------------------------------------------------------------------ probabilites d'un match
def pois(l):
    k = np.arange(MAX_BUTS + 1)
    return np.exp(-l) * l ** k / np.array([math.factorial(i) for i in k])


def probas(mod, elo_a, elo_b, lieu_a):
    """Matrice des scores vue de A (A en ligne). lieu_a : 'dom', 'ext', 'neutre'."""
    if lieu_a == "dom":
        return matrice(mod, elo_a, elo_b, False)
    if lieu_a == "ext":
        return matrice(mod, elo_b, elo_a, False).T
    return matrice(mod, elo_a, elo_b, True)


def lam_a_b(mod, elo_a, elo_b, lieu_a):
    b = mod["b"]; e = (elo_a - elo_b) / 100
    la = math.exp(b[0] + b[1] * e + (b[2] if lieu_a == "dom" else b[3] if lieu_a == "ext" else 0))
    lb = math.exp(b[0] - b[1] * e + (b[3] if lieu_a == "dom" else b[2] if lieu_a == "ext" else 0))
    return la, lb


def match_vu_de(mod, elo_a, elo_b, lieu_a, ko):
    """Renvoie dict : V/N/D au score enregistre (apres prolongation si ko), buts attendus, P(qualifie)."""
    p = probas(mod, elo_a, elo_b, lieu_a)
    v, n, d = vnd(p)
    la, lb = lam_a_b(mod, elo_a, elo_b, lieu_a)
    k = np.arange(MAX_BUTS + 1)
    ga, gb = float((p.sum(1) * k).sum()), float((p.sum(0) * k).sum())
    if not ko:
        return {"V": v, "N": n, "D": d, "bp": ga, "bc": gb, "qualif": None}
    q = np.outer(pois(la / 3), pois(lb / 3))
    ve, ne, de = vnd(q)
    return {"V": v + n * ve, "N": n * ne, "D": d + n * de, "bp": ga + n * la / 3, "bc": gb + n * lb / 3,
            "qualif": v + n * ve + n * ne * 0.5, "N90": n}


def lieu(r, equipe):
    if r.neutral:
        return "neutre"
    return "dom" if r.home_team == equipe else "ext"


def lignes_equipe(equipe, variante="base"):
    rows = []
    for r in af[(af.home_team == equipe) | (af.away_team == equipe)].itertuples():
        dom = r.home_team == equipe
        adv = r.away_team if dom else r.home_team
        ea, eb = (r.elo_home_avant, r.elo_away_avant) if dom else (r.elo_away_avant, r.elo_home_avant)
        bp, bc = (r.home_score, r.away_score) if dom else (r.away_score, r.home_score)
        ko = r.tour != "groupe"
        mm = match_vu_de(modele_pour(r.date, variante), ea, eb, lieu(r, equipe), ko)
        res = "V" if bp > bc else "N" if bp == bc else "D"
        rows.append({"edition": int(r.edition), "date": str(r.date.date()), "tour": r.tour, "adversaire": adv,
                     "lieu": lieu(r, equipe), "score": f"{bp}-{bc}", "bp": int(bp), "bc": int(bc), "resultat": res,
                     "tab": (("gagne" if r.vainqueur == equipe else "perdu") if (ko and bp == bc) else None),
                     "qualifie": (r.vainqueur == equipe) if ko else None,
                     "elo": round(float(ea)), "elo_adv": round(float(eb)),
                     "pts": 3 if res == "V" else 1 if res == "N" else 0,
                     "pts_att": 3 * mm["V"] + mm["N"], "pV": mm["V"], "pN": mm["N"], "pD": mm["D"],
                     "bp_att": mm["bp"], "bc_att": mm["bc"], "p_qualif": mm["qualif"]})
    return pd.DataFrame(rows)


def sim_points(df, n=100_000):
    P = df[["pV", "pN", "pD"]].to_numpy()
    u = RNG.random((n, len(df)))
    pts = np.where(u < P[:, 0], 3, np.where(u < P[:, 0] + P[:, 1], 1, 0)).sum(1)
    return pts


def poisbin(ps):
    d = np.array([1.0])
    for p in ps:
        d = np.convolve(d, [1 - p, p])
    return d


def resume_points(df):
    s = sim_points(df)
    act = int(df.pts.sum())
    return {"matchs": int(len(df)), "points": act, "points_attendus": round(float(df.pts_att.sum()), 2),
            "ecart": round(act - float(df.pts_att.sum()), 2),
            "ecart_par_match": round((act - float(df.pts_att.sum())) / len(df), 3),
            "intervalle_95_points_sous_modele": [int(np.percentile(s, 2.5)), int(np.percentile(s, 97.5))],
            "p_aussi_bas_ou_moins": round(float((s <= act).mean()), 3),
            "buts_pour": int(df.bp.sum()), "buts_pour_attendus": round(float(df.bp_att.sum()), 2),
            "buts_contre": int(df.bc.sum()), "buts_contre_attendus": round(float(df.bc_att.sum()), 2),
            "nuls": int((df.resultat == "N").sum()), "nuls_attendus": round(float(df.pN.sum()), 2)}


# ------------------------------------------------------------------ simulation des groupes (P(sortir du groupe))
def groupes(g):
    gs = g[g.tour == "groupe"]
    par = {}
    for r in gs.itertuples():
        a, b = r.home_team, r.away_team
        ga, gb = par.get(a, {a}), par.get(b, {b})
        u = ga | gb
        for t in u:
            par[t] = u
    return list({frozenset(v) for v in par.values()})


def p_sortie_groupe(ed, variante="base", n=20_000):
    g = af[af.edition == ed]
    grs = [sorted(x) for x in groupes(g)]
    nko = len(g[g.tour != "groupe"])
    B = 16 if nko >= 15 else (8 if nko >= 7 else 4)
    tiers = B - 2 * len(grs)
    gs = g[g.tour == "groupe"]
    equipes = sorted(set(gs.home_team) | set(gs.away_team))
    ix = {e: i for i, e in enumerate(equipes)}
    pts = np.zeros((n, len(equipes))); dif = np.zeros_like(pts); bp = np.zeros_like(pts)
    for r in gs.itertuples():
        p = matrice(modele_pour(r.date, variante), r.elo_home_avant, r.elo_away_avant, bool(r.neutral)).ravel()
        idx = RNG.choice(p.size, size=n, p=p)
        x, y = idx // (MAX_BUTS + 1), idx % (MAX_BUTS + 1)
        h, a = ix[r.home_team], ix[r.away_team]
        pts[:, h] += np.where(x > y, 3, np.where(x == y, 1, 0)); pts[:, a] += np.where(y > x, 3, np.where(x == y, 1, 0))
        dif[:, h] += x - y; dif[:, a] += y - x; bp[:, h] += x; bp[:, a] += y
    cle = pts * 1e6 + (dif + 50) * 1e3 + bp + RNG.random(pts.shape)  # tirage au sort en dernier
    qual = np.zeros_like(pts, dtype=bool)
    cles3 = []
    for grp in grs:
        cols = [ix[e] for e in grp]
        ordre = np.argsort(-cle[:, cols], axis=1)
        c = np.array(cols)
        for rang in (0, 1):
            qual[np.arange(n), c[ordre[:, rang]]] = True
        if tiers > 0:
            t3 = c[ordre[:, 2]]
            cles3.append((t3, cle[np.arange(n), t3]))
    if tiers > 0:
        T = np.column_stack([t for t, _ in cles3]); K = np.column_stack([k for _, k in cles3])
        best = np.argsort(-K, axis=1)[:, :tiers]
        for j in range(tiers):
            qual[np.arange(n), T[np.arange(n), best[:, j]]] = True
    return {e: float(qual[:, ix[e]].mean()) for e in equipes}


# ------------------------------------------------------------------ chemin du titre (adversaires reellement rencontres)
ORDRE_KO = ["huitieme", "quart", "demi", "finale"]


def elo_avant(ed, equipe, date=None):
    g = af[(af.edition == ed) & ((af.home_team == equipe) | (af.away_team == equipe))].sort_values("date")
    if date is not None:
        g = g[g.date <= date]
    r = g.iloc[-1]
    return float(r.elo_home_avant if r.home_team == equipe else r.elo_away_avant)


def lieu_cf(ed, a, b):
    h = hotes[ed]
    return "dom" if a in h else "ext" if b in h else "neutre"


def chemin_titre(ed, equipe, variante="base"):
    """Probabilite de gagner tous les tours a elimination directe : tours joues = adversaires reels ; tours non joues =
    l'equipe qui occupe la place du Mali dans le tableau (celle qui l'a elimine, puis celle qui a elimine celle-ci...)
    rencontre l'adversaire qu'elle a reellement rencontre. Hors tableau : adversaire moyen du tour."""
    g = af[af.edition == ed]
    ko = g[g.tour.isin(ORDRE_KO)]
    tours = [t for t in ORDRE_KO if t in set(ko.tour)]
    mes = ko[(ko.home_team == equipe) | (ko.away_team == equipe)]
    det = []
    occ = equipe
    e_eq = elo_avant(ed, equipe)
    for t in tours:
        km = ko[ko.tour == t]
        if occ == equipe:
            rr = mes[mes.tour == t]
        else:
            rr = km[(km.home_team == occ) | (km.away_team == occ)]
        if len(rr):
            r = rr.iloc[0]
            adv = r.away_team if r.home_team == occ else r.home_team
            e_adv = float(r.elo_away_avant if r.home_team == occ else r.elo_home_avant)
            if occ == equipe:
                e_m = float(r.elo_home_avant if r.home_team == equipe else r.elo_away_avant)
                l = lieu(r, equipe)
                joue = True
            else:
                e_m, l, joue = elo_avant(ed, equipe), lieu_cf(ed, equipe, adv), False
            occ = r.vainqueur if (occ == equipe and r.vainqueur != equipe) or occ != equipe else equipe
        else:  # equipe hors tableau : adversaire moyen du tour
            adv = "moyen du tour"
            e_adv = float(np.mean(np.r_[km.elo_home_avant, km.elo_away_avant]))
            e_m, l, joue = e_eq, ("dom" if equipe in hotes[ed] else "neutre"), False
        pq = match_vu_de(modele_pour(g.date.min(), variante), e_m, e_adv, l, True)["qualif"]
        det.append({"tour": t, "adversaire": adv, "elo": round(e_m), "elo_adv": round(e_adv), "joue": joue,
                    "p_qualif": round(pq, 3)})
    return float(np.prod([d["p_qualif"] for d in det])), det


def titres(equipe, variante="base", editions=None):
    eds = sorted(set(af[(af.home_team == equipe) | (af.away_team == equipe)].edition))
    if editions:
        eds = [e for e in eds if e in editions]
    out = []
    for ed in eds:
        pg = P_GROUPE[variante][ed][equipe]
        pk, det = chemin_titre(ed, equipe, variante)
        champion = af[(af.edition == ed) & (af.tour == "finale")].iloc[0].vainqueur
        out.append({"edition": int(ed), "p_sortie_groupe": round(pg, 3), "p_titre_si_tableau": round(pk, 4),
                    "p_titre": round(pg * pk, 4), "titre": champion == equipe, "chemin": det})
    return out


# ------------------------------------------------------------------ calculs
P_GROUPE = {v: {ed: p_sortie_groupe(ed, v) for ed in sorted(af.edition.unique())} for v in ("base", "tout2000", "depuis2010", "can")}

R = {"question": "Le Mali est-il maudit a la CAN ? Resultats reels contre resultats attendus selon l'Elo d'avant-match.",
     "modele": {"methode": "Poisson + Dixon-Coles sur l'ecart d'Elo et le lieu (malidata/simulation.py) ; prolongation = 1/3 de match "
                           "(Poisson simple), tirs au but = 50/50",
                "depuis_2000": {"matchs": MOD00["matchs"], "b": MOD00["b"], "rho": MOD00["rho"]},
                "1980_1999 (utilise pour 1972 et 1994-1998)": {"matchs": MOD80["matchs"], "b": MOD80["b"], "rho": MOD80["rho"]},
                "depuis_2010 (robustesse)": {"matchs": MOD10["matchs"], "b": MOD10["b"], "rho": MOD10["rho"]}}}

mali = lignes_equipe("Mali")
R["mali_matchs"] = mali.round(4).to_dict("records")
R["q1_points"] = {"total": resume_points(mali),
                  "groupes": resume_points(mali[mali.tour == "groupe"]),
                  "elimination_directe": resume_points(mali[mali.tour != "groupe"]),
                  "depuis_1994": resume_points(mali[mali.edition >= 1994]),
                  "par_edition": {int(ed): resume_points(g) for ed, g in mali.groupby("edition")}}
for v in ("tout2000", "depuis2010", "can"):
    R["q1_points"][f"robustesse_{v}"] = resume_points(lignes_equipe("Mali", v))

kom = mali[mali.tour.isin(ORDRE_KO)]
d = poisbin(kom.p_qualif.to_numpy())
act = int(kom.qualifie.sum())
tm = mali[mali.tour == "3e place"]
R["q2_tours"] = {"tours_a_elimination_directe_joues": int(len(kom)), "gagnes": act,
                 "gagnes_attendus": round(float(kom.p_qualif.sum()), 2),
                 "p_aussi_peu_ou_moins": round(float(d[:act + 1].sum()), 3),
                 "intervalle_95": [int(np.searchsorted(np.cumsum(d), 0.025)), int(np.searchsorted(np.cumsum(d), 0.975))],
                 "detail": kom[["edition", "tour", "adversaire", "score", "tab", "qualifie", "elo", "elo_adv", "p_qualif"]].round(3).to_dict("records"),
                 "matchs_pour_la_3e_place": {"joues": int(len(tm)), "gagnes": int((tm.qualifie).sum()),
                                             "attendus": round(float(tm.p_qualif.sum()), 2)}}
tt = titres("Mali")
pt = np.array([t["p_titre"] for t in tt])
R["q2_titres"] = {"editions": tt, "titres_attendus": round(float(pt.sum()), 3),
                  "p_zero_titre": round(float(np.prod(1 - pt)), 3),
                  "titres_attendus_robustesse": {v: round(float(sum(t["p_titre"] for t in titres("Mali", v))), 3) for v in ("tout2000", "depuis2010", "can")},
                  "lecture": "p_titre = P(sortir du groupe, simule avec les vrais adversaires et le reglement, tirage au sort compris) "
                             "x P(gagner chaque tour du tableau). Tours joues : adversaire reel. Tours non joues : le Mali prend la place "
                             "de l'equipe qui l'a elimine et affronte ceux qu'elle a affrontes. Tours independants entre eux."}

# q3 tirs au but
def tab_bilan(df):
    w = int((df.winner == "Mali").sum()); n = len(df)
    from math import comb
    p2 = min(1.0, 2 * min(sum(comb(n, k) for k in range(0, w + 1)), sum(comb(n, k) for k in range(w, n + 1))) / 2 ** n)
    return {"seances": n, "gagnees": w, "taux": round(w / n, 3), "p_bilateral_vs_50": round(p2, 3)}


som = so[(so.home_team == "Mali") | (so.away_team == "Mali")]
can_dates = set(af.date)
som_can = som[som.date.isin(can_dates)]
R["q3_tab"] = {"phase_finale_can": tab_bilan(som_can), "toutes": tab_bilan(som),
               "liste": [{"date": str(r.date.date()), "match": f"{r.home_team} - {r.away_team}", "vainqueur": r.winner} for r in som.itertuples()],
               "note": "2015 : le Mali est sorti au tirage au sort (egalite parfaite avec la Guinee, groupe D)."}
g15 = mali[(mali.edition == 2015)]
R["q3_tab"]["controle_2015_mali"] = {"points": int(g15.pts.sum()), "bp": int(g15.bp.sum()), "bc": int(g15.bc.sum())}

# q4 comparaison
sf = af[(af.edition >= 1994) & (af.tour == "demi")]
nsf = pd.Series(list(sf.home_team) + list(sf.away_team)).value_counts()
pairs = list(nsf[nsf >= 3].index)
champ = af[(af.edition >= 1994) & (af.tour == "finale")]
comp = []
for e in pairs:
    df = lignes_equipe(e); df = df[df.edition >= 1994]
    s = sim_points(df)
    ko = df[df.tour.isin(ORDRE_KO)]
    tt_e = titres(e, editions=list(range(1994, 2027)))
    pt_e = np.array([t["p_titre"] for t in tt_e])
    nt = int((champ.vainqueur == e).sum())
    dist = poisbin(pt_e)
    comp.append({"equipe": e, "demi_finales": int(nsf[e]), "editions": len(tt_e), "matchs": len(df),
                 "elo_moyen_avant_match": round(float(df.elo.mean())),
                 "pts_par_match": round(float(df.pts.mean()), 3), "pts_att_par_match": round(float(df.pts_att.mean()), 3),
                 "ecart_par_match": round(float((df.pts - df.pts_att).mean()), 3),
                 "p_aussi_bas_ou_moins": round(float((s <= df.pts.sum()).mean()), 3),
                 "tours_ko_joues": len(ko), "tours_ko_gagnes": int(ko.qualifie.sum()), "tours_ko_attendus": round(float(ko.p_qualif.sum()), 2),
                 "titres": nt, "titres_attendus": round(float(pt_e.sum()), 2),
                 "p_titres_aussi_peu_ou_moins": round(float(dist[:nt + 1].sum()), 3),
                 "nuls": int((df.resultat == "N").sum()), "nuls_attendus": round(float(df.pN.sum()), 2)})
comp = sorted(comp, key=lambda x: x["ecart_par_match"])
R["q4_comparaison_depuis_1994"] = {"critere": ">= 3 demi-finales de CAN depuis 1994", "equipes": comp}

# q5 nuls : Mali vs modele, et calibration du modele sur toutes les phases finales depuis 1994
P = []
for r in af[af.edition >= 1994].itertuples():
    mm = match_vu_de(modele_pour(r.date), r.elo_home_avant, r.elo_away_avant,
                     "neutre" if r.neutral else "dom", r.tour != "groupe")
    P.append({"tour": r.tour, "pN": mm["N"], "nul": int(r.home_score == r.away_score)})
P = pd.DataFrame(P)
nm = mali
dnul = poisbin(nm.pN.to_numpy()); kn = int((nm.resultat == "N").sum())
gm = nm[nm.tour == "groupe"]; dg = poisbin(gm.pN.to_numpy()); kg = int((gm.resultat == "N").sum())
R["q5_nuls"] = {"mali_tous": {"matchs": len(nm), "nuls": kn, "taux": round(kn / len(nm), 3), "attendus": round(float(nm.pN.sum()), 2),
                              "taux_attendu": round(float(nm.pN.mean()), 3), "p_aussi_haut_ou_plus": round(float(dnul[kn:].sum()), 3)},
                "mali_groupes": {"matchs": len(gm), "nuls": kg, "taux": round(kg / len(gm), 3), "attendus": round(float(gm.pN.sum()), 2),
                                 "taux_attendu": round(float(gm.pN.mean()), 3), "p_aussi_haut_ou_plus": round(float(dg[kg:].sum()), 3)},
                "toutes_phases_finales_1994_2026": {"matchs": len(P), "taux_reel": round(float(P.nul.mean()), 3), "taux_attendu": round(float(P.pN.mean()), 3),
                                                    "groupes_reel": round(float(P[P.tour == 'groupe'].nul.mean()), 3),
                                                    "groupes_attendu": round(float(P[P.tour == 'groupe'].pN.mean()), 3)},
                "note": "Score enregistre : un match a elimination directe ne compte comme nul que s'il l'est encore apres prolongation."}

# bootstrap par edition de l'ecart de points du Mali (incertitude sur l'echantillon, en plus de l'intervalle sous modele)
eds = mali.edition.unique()
bs = []
for _ in range(10_000):
    pick = RNG.choice(eds, size=len(eds))
    sub = pd.concat([mali[mali.edition == e] for e in pick])
    bs.append((sub.pts - sub.pts_att).mean())
R["q1_points"]["bootstrap_editions_ecart_par_match_ic95"] = [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)]

R["modele"]["phases_finales_groupes_1994_2026 (robustesse, en echantillon)"] = {"matchs": MODCAN["matchs"], "b": MODCAN["b"], "rho": MODCAN["rho"]}
# niveau : rang Elo du Mali parmi les participants, avant le premier match de chaque edition
rangs = []
for ed, g in af.groupby("edition"):
    eq = sorted(set(g.home_team) | set(g.away_team))
    el = {e: elo_avant(ed, e, g.date.min() + pd.Timedelta(days=4)) if False else float(
        (lambda r: r.elo_home_avant if r.home_team == e else r.elo_away_avant)(g[(g.home_team == e) | (g.away_team == e)].sort_values("date").iloc[0])) for e in eq}
    cl = sorted(eq, key=lambda e: -el[e])
    champion = g[g.tour == "finale"].iloc[0].vainqueur
    rangs.append({"edition": int(ed), "participants": len(eq), "rang_elo_champion": cl.index(champion) + 1,
                  "rang_elo_mali": (cl.index("Mali") + 1) if "Mali" in eq else None,
                  "elo_mali": round(el["Mali"]) if "Mali" in eq else None, "elo_champion": round(el[champion]), "champion": champion,
                  "elo_max": round(el[cl[0]]), "favori_elo": cl[0]})
R["niveau_rang_elo_par_edition"] = rangs
# nuls : recalibrage sur l'exces de nuls de toutes les phases finales
ratio = R["q5_nuls"]["toutes_phases_finales_1994_2026"]["taux_reel"] / R["q5_nuls"]["toutes_phases_finales_1994_2026"]["taux_attendu"]
pn = np.clip(mali.pN.to_numpy() * ratio, 0, 1); dd = poisbin(pn)
R["q5_nuls"]["mali_recalibre_sur_toutes_phases_finales"] = {"facteur": round(ratio, 3), "nuls_attendus": round(float(pn.sum()), 2),
                                                             "p_aussi_haut_ou_plus": round(float(dd[kn:].sum()), 3)}
mc = lignes_equipe("Mali", "can"); dc = poisbin(mc.pN.to_numpy())
R["q5_nuls"]["mali_modele_phases_finales"] = {"nuls_attendus": round(float(mc.pN.sum()), 2), "p_aussi_haut_ou_plus": round(float(dc[kn:].sum()), 3)}
R["q1_points"]["mali_VND"] = {"reel": {k: int((mali.resultat == k).sum()) for k in "VND"},
                              "attendu": {"V": round(float(mali.pV.sum()), 2), "N": round(float(mali.pN.sum()), 2), "D": round(float(mali.pD.sum()), 2)},
                              "attendu_modele_phases_finales": {"V": round(float(mc.pV.sum()), 2), "N": round(float(mc.pN.sum()), 2), "D": round(float(mc.pD.sum()), 2)}}
print(json.dumps(R["niveau_rang_elo_par_edition"]), json.dumps(R["q5_nuls"]), json.dumps(R["q1_points"]["mali_VND"]), json.dumps(R["q1_points"]["robustesse_can"]), json.dumps(R["q2_titres"]["titres_attendus_robustesse"]), MODCAN)
json.dump(R, open(f"{OUT}/resultats.json", "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps({k: R[k] for k in ("modele",)}, indent=1, default=str))
print(mali[["edition", "tour", "adversaire", "lieu", "score", "tab", "elo", "elo_adv", "pts", "pts_att", "pN", "p_qualif"]].round(2).to_string())
print(json.dumps({k: v for k, v in R["q1_points"].items() if k != "par_edition"}, indent=1))
print(pd.DataFrame(R["q1_points"]["par_edition"]).T[["matchs", "points", "points_attendus", "ecart", "p_aussi_bas_ou_moins"]])
print(json.dumps({k: v for k, v in R["q2_tours"].items() if k != "detail"}, indent=1))
print(pd.DataFrame([{k: t[k] for k in ("edition", "p_sortie_groupe", "p_titre_si_tableau", "p_titre")} for t in tt]).to_string())
for t in tt:
    print(t["edition"], [(c["tour"], c["adversaire"], c["joue"], c["p_qualif"]) for c in t["chemin"]])
print(json.dumps({k: v for k, v in R["q2_titres"].items() if k != "editions"}, indent=1))
print(json.dumps({k: v for k, v in R["q3_tab"].items() if k != "liste"}, indent=1))
print(pd.DataFrame(comp).to_string())
print(json.dumps(R["q5_nuls"], indent=1))

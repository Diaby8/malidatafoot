"""Construit le modèle xT, le valide, et l'applique au Mali (CAN 2023).
Usage : python3 -I scripts/build_xt.py <racine xt>
Entrées : cache/train_actions.parquet, cache/afcon_actions.parquet, cache/training_pool.json,
          dépôt malidatafoot (lecture seule) : entrepôt DuckDB (minutes, postes) et événements bruts de la CAN 2023.
Sorties : out/*.json"""
import json, os, sys, datetime
import numpy as np
import pandas as pd
import scipy.sparse as sp
import duckdb
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import roc_auc_score

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from xtlib import NX, NY, NZ, cell, tag_actions, match_counts, fit, grid, add_xt, possessions, SET_PIECE_PASSES, MIN_CARRY  # noqa

REPO = "/home/claude/repo/malidatafoot"
OUT = ROOT
SEED = 2026
B = 200
MIN_MIN = 180
MALI = "Mali"
MALI_MATCHES = [3920391, 3920404, 3920417, 3922244, 3922659]
QF_CIV = 3922659
rng = np.random.default_rng(SEED)


def r6(x): return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 6)
def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=1)
    print("wrote", name, flush=True)


# ---------------------------------------------------------------- données d'entraînement
pool = pd.DataFrame(json.load(open(os.path.join(ROOT, "cache/training_pool.json"))))
assert pool["match_id"].is_unique
tr = tag_actions(pd.read_parquet(os.path.join(ROOT, "cache/train_actions.parquet")))
assert set(tr["match_id"].unique()) == set(pool["match_id"]), "événements manquants"
C = match_counts(tr)
mids = C["mids"]; n = len(mids)
comp_of = pool.set_index("match_id").loc[mids, "competition"].to_numpy()
print("training matches", n, flush=True)

full = fit(C)
xt = full["xt"]

# ---------------------------------------------------------------- contrôles de cohérence
G = grid(xt)
zmax = int(np.argmax(xt)); cy_max, cx_max = divmod(zmax, NX)
central = G[4:8, :]                      # 4 bandes centrales (y 26,7 à 53,3)
col_mean = G.mean(axis=0)
inc_central = float(np.mean(np.diff(central, axis=1) > 0))
inc_cols = float(np.mean(np.diff(col_mean) > 0))
mirror_r = float(pearsonr(G.ravel(), G[::-1, :].ravel())[0])
Tm = full["m"][:, None] * full["T"]
spec = float(np.max(np.abs(np.linalg.eigvals(Tm))))
cell_counts = (full["S"] + full["M"])
own_half = G[:, :8]

# variante g = taux de buts réel
emp = fit(C, g_mode="goals")
# variante conduites : toutes les conduites (pas de longueur minimale)
tr0 = tag_actions(pd.read_parquet(os.path.join(ROOT, "cache/train_actions.parquet"),
                                  columns=None), min_carry=0.0)
full0 = fit(match_counts(tr0)); del tr0

moves = tr[tr["is_move"]]
n_info = {
    "matchs": int(n),
    "competitions_saisons": int(pool.groupby(["competition", "season"]).ngroups),
    "matchs_par_competition": pool["competition"].value_counts().to_dict(),
    "periode_saisons": [str(pool["season"].min()), str(pool["season"].max())],
    "passes_jeu_courant": int((moves["type"] == "Pass").sum()),
    "passes_reussies": int(((moves["type"] == "Pass") & moves["is_success"]).sum()),
    "conduites": int((moves["type"] == "Carry").sum()),
    "deplacements_total": int(len(moves)),
    "deplacements_reussis": int(moves["is_success"].sum()),
    "tirs_jeu_courant": int(tr["is_shot"].sum()),
    "buts_jeu_courant": int(tr["is_goal"].sum()),
    "xg_tirs_jeu_courant": round(float(tr.loc[tr["is_shot"], "xg"].sum()), 2),
    "actions_ecartees": {
        "passes_coups_de_pied_arretes": int(((tr["type"] == "Pass") & tr["sub_type"].isin(SET_PIECE_PASSES)).sum()),
        "tirs_hors_jeu_courant (penaltys, coups francs directs, corners directs)": int(((tr["type"] == "Shot") & ~tr["is_shot"]).sum()),
        f"conduites_de_moins_de_{MIN_CARRY}_unites": int(((tr["type"] == "Carry") & ~tr["is_move"]).sum()),
    },
    "actions_par_case_min": int(cell_counts.min()),
    "actions_par_case_mediane": int(np.median(cell_counts)),
    "tirs_par_case_min": int(full["S"].min()),
}
print(n_info, flush=True)

# ---------------------------------------------------------------- validation : matchs mis de côté
perm = rng.permutation(n)
test_idx = np.sort(perm[: n // 5]); train_idx = np.sort(perm[n // 5:])
w_tr = np.zeros(n); w_tr[train_idx] = 1
fit_tr = fit(C, weights=w_tr)
test_mids = set(mids[test_idx])


def eval_possessions(d, xtv):
    pp = possessions(add_xt(d, xtv))
    pp = pp[pp["n_moves"] > 0]
    res = {"possessions": int(len(pp)), "part_avec_tir": round(float(pp["shot"].mean()), 4),
           "part_avec_but": round(float(pp["goal"].mean()), 4)}
    for target in ("shot", "goal"):
        y = pp[target].to_numpy()
        res[f"auc_{target}"] = {k: round(float(roc_auc_score(y, pp[k])), 4)
                                for k in ("xt_added", "xt_pos", "progress", "n_moves")}
    # calibration grossière : part de possessions avec tir par décile de xT ajouté
    q = pd.qcut(pp["xt_added"].rank(method="first"), 10, labels=False)
    res["part_tir_par_decile_xt"] = [round(float(v), 4) for v in pp.groupby(q)["shot"].mean()]
    return res, pp


test_df = tr[tr["match_id"].isin(test_mids)]
val_test, pp_test = eval_possessions(test_df, fit_tr["xt"])
# niveau équipe-match : xT créé vs xG (hors penalty) du match, sur les matchs mis de côté
tm = add_xt(test_df, fit_tr["xt"])
tm_ok = tm[tm["is_move"] & tm["is_success"]]
team_xt = tm_ok.groupby(["match_id", "team"])["xt_added"].sum()
sh = test_df[(test_df["type"] == "Shot") & (test_df["sub_type"] != "Penalty")]
team_xg = sh.groupby(["match_id", "team"])["xg"].sum()
tt = pd.concat([team_xt.rename("xt"), team_xg.rename("xg")], axis=1).fillna(0)
val_team = {"equipes_matchs": int(len(tt)),
            "spearman_xt_vs_xg_sans_penalty": round(float(spearmanr(tt["xt"], tt["xg"])[0]), 4),
            "pearson_xt_vs_xg_sans_penalty": round(float(pearsonr(tt["xt"], tt["xg"])[0]), 4)}

# hors domaine : CAN 2023 (jamais dans l'entraînement)
af = tag_actions(pd.read_parquet(os.path.join(ROOT, "cache/afcon_actions.parquet")))
val_afcon, _ = eval_possessions(af, xt)

# ---------------------------------------------------------------- stabilité
halves = []
for k in range(20):
    p = rng.permutation(n); a = np.zeros(n); a[p[: n // 2]] = 1
    xa = fit(C, weights=a)["xt"]; xb = fit(C, weights=1 - a)["xt"]
    halves.append((pearsonr(xa, xb)[0], spearmanr(xa, xb)[0], np.max(np.abs(xa - xb)), np.max(xa), np.max(xb)))
halves = np.array(halves)
liga = (comp_of == "La Liga").astype(float)
x_liga = fit(C, weights=liga)["xt"]; x_noliga = fit(C, weights=1 - liga)["xt"]
clubs = np.isin(comp_of, ["FIFA World Cup", "UEFA Euro", "Copa America"])
x_sel = fit(C, weights=clubs.astype(float))["xt"]

boot = np.zeros((B, NZ))
for b in range(B):
    w = rng.multinomial(n, np.ones(n) / n).astype(float)
    boot[b] = fit(C, weights=w)["xt"]
lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
rel_w = (hi - lo) / xt

# ---------------------------------------------------------------- CAN 2023 : joueurs et équipes
con = duckdb.connect(os.path.join(REPO, "data/warehouse.duckdb"), read_only=True)
pt = con.execute("select player_id, player, team, position, minutes, matches, starts from gold.player_tournament").df()
pos = con.execute("select * from gold.player_positions").df()
names = con.execute("select player_id, display_name from silver.players").df()
mlen = con.execute("select match_id, last_period from silver.match_lengths").df()
smatches = con.execute("select * from silver.matches").df()
con.close()


def role(position):   # copie de malidata/profils.py (rôles fins de la page)
    if not position: return None
    if position == "Goalkeeper": return "GAR"
    if "Center Back" in position: return "DC"
    if "Back" in position: return "LAT"
    if "Defensive Midfield" in position: return "MDF"
    if "Attacking Midfield" in position or position.endswith("Wing"): return "MOF"
    if "Midfield" in position: return "MIL"
    return "ATT"


ROLE_FR = {"DC": "défenseurs centraux", "LAT": "latéraux", "MDF": "milieux défensifs", "MIL": "milieux centraux",
           "MOF": "milieux offensifs et ailiers", "ATT": "attaquants", "GAR": "gardiens"}
pos["role"] = pos["position"].map(role)
pr = pos.groupby(["player_id", "role"])["n"].sum().reset_index()
pr["part"] = pr["n"] / pr.groupby("player_id")["n"].transform("sum")
principal = pr.sort_values(["n", "role"], ascending=[False, True]).drop_duplicates("player_id")[["player_id", "role", "part"]]

afx = add_xt(af, xt)
cred = afx[afx["is_move"] & afx["is_success"]].copy()
cred["is_pass"] = cred["type"] == "Pass"
cred["pos"] = cred["xt_added"].clip(lower=0)
agg = cred.groupby("player_id").agg(xt=("xt_added", "sum"), xt_pos=("pos", "sum"), actions=("xt_added", "size"),
                                    xt_pass=("xt_added", lambda s: s[cred.loc[s.index, "is_pass"]].sum()),
                                    xt_carry=("xt_added", lambda s: s[~cred.loc[s.index, "is_pass"]].sum()),
                                    n_pass=("is_pass", "sum")).reset_index()
pl = pt.merge(agg, on="player_id", how="left").merge(principal, on="player_id", how="left").merge(names, on="player_id", how="left")
for c in ("xt", "xt_pos", "xt_pass", "xt_carry", "actions", "n_pass"): pl[c] = pl[c].fillna(0)
pl["n_carry"] = pl["actions"] - pl["n_pass"]
pl["xt_p90"] = pl["xt"] / pl["minutes"] * 90
pl["xt_pass_p90"] = pl["xt_pass"] / pl["minutes"] * 90
pl["xt_carry_p90"] = pl["xt_carry"] / pl["minutes"] * 90
elig = (pl["minutes"] >= MIN_MIN) & (pl["position"] != "Goalkeeper")
pl["eligible"] = elig
pl["role_net"] = pl["part"] >= 0.5
pl["xt_p90_r"] = pl["xt_p90"].round(6)
pl["rang"] = np.nan; pl.loc[elig, "rang"] = pl.loc[elig, "xt_p90_r"].rank(ascending=False, method="min")
n_elig = int(elig.sum())
pl["rang_poste"] = np.nan; pl["effectif_poste"] = np.nan
for r_, grp in pl[elig & pl["role_net"]].groupby("role"):
    pl.loc[grp.index, "rang_poste"] = grp["xt_p90_r"].rank(ascending=False, method="min")
    pl.loc[grp.index, "effectif_poste"] = len(grp)
for k in ("xt_pass_p90", "xt_carry_p90"):
    pl["rang_" + k] = np.nan; pl.loc[elig, "rang_" + k] = pl.loc[elig, k].round(6).rank(ascending=False, method="min")

# bootstrap des rangs (matrice joueurs x cases : +1 à l'arrivée, -1 au départ)
pid_index = {p: i for i, p in enumerate(pl["player_id"])}
# deux joueurs entrés dans le temps additionnel (0 minute au chrono) ne sont pas dans gold.player_tournament : 8 actions, comptées pour l'équipe seulement
cp = cred[cred["player_id"].isin(pid_index)]
rows = cp["player_id"].map(pid_index).to_numpy()
A = sp.csr_matrix((np.r_[np.ones(len(cp)), -np.ones(len(cp))],
                   (np.r_[rows, rows], np.r_[cp["z_end"].to_numpy(), cp["z"].to_numpy()])), shape=(len(pl), NZ))
assert np.allclose(A @ xt, pl["xt"].to_numpy())
mins = pl["minutes"].to_numpy(); el = elig.to_numpy()
boot_p90 = (A @ boot.T).T / mins * 90           # B x joueurs
boot_rank = np.full_like(boot_p90, np.nan)
for b in range(B):
    v = boot_p90[b, el]; boot_rank[b, el] = pd.Series(v).rank(ascending=False, method="min").to_numpy()

# équipes
team_min = {}
for mid in afx["match_id"].unique():
    lp = int(mlen.loc[mlen["match_id"] == mid, "last_period"].iloc[0]); team_min[mid] = 120 if lp >= 3 else 90
tmatch = cred.groupby(["team", "match_id"]).agg(xt=("xt_added", "sum"), xt_pos=("pos", "sum")).reset_index()
opp = {}
for r in smatches.itertuples():
    opp[(r.match_id, r.home_team)] = r.away_team; opp[(r.match_id, r.away_team)] = r.home_team
tmatch["minutes"] = tmatch["match_id"].map(team_min)
tmatch["opp"] = [opp[(m, t)] for m, t in zip(tmatch["match_id"], tmatch["team"])]
conc = tmatch[["match_id", "team", "xt"]].rename(columns={"team": "opp", "xt": "xt_concede"})
tmatch = tmatch.merge(conc, on=["match_id", "opp"], how="left")
teams = tmatch.groupby("team").agg(matchs=("match_id", "nunique"), minutes=("minutes", "sum"), xt=("xt", "sum"),
                                   xt_pos=("xt_pos", "sum"), xt_concede=("xt_concede", "sum")).reset_index()
teams["xt_p90"] = teams["xt"] / teams["minutes"] * 90
teams["xt_pos_p90"] = teams["xt_pos"] / teams["minutes"] * 90
teams["xt_concede_p90"] = teams["xt_concede"] / teams["minutes"] * 90
teams["rang"] = teams["xt_p90"].round(6).rank(ascending=False, method="min").astype(int)
teams["rang_positif"] = teams["xt_pos_p90"].round(6).rank(ascending=False, method="min").astype(int)
teams["rang_concede"] = teams["xt_concede_p90"].round(6).rank(ascending=True, method="min").astype(int)
assert len(teams) == 24
# bootstrap du rang du Mali
tl = list(teams["team"]); tix = {t: i for i, t in enumerate(tl)}
trows = cred["team"].map(tix).to_numpy()
AT = sp.csr_matrix((np.r_[np.ones(len(cred)), -np.ones(len(cred))],
                    (np.r_[trows, trows], np.r_[cred["z_end"].to_numpy(), cred["z"].to_numpy()])), shape=(24, NZ))
tb = (AT @ boot.T).T / teams["minutes"].to_numpy() * 90
mali_rank_boot = np.array([pd.Series(r).rank(ascending=False, method="min").iloc[tix[MALI]] for r in tb])
# bruit du petit nombre de matchs : on retire au hasard, pour chaque équipe, ses matchs avec remise
rs_rank = []
tm_by_team = {t: g[["xt", "minutes"]].to_numpy() for t, g in tmatch.groupby("team")}
for b in range(2000):
    v = {}
    for t, arr in tm_by_team.items():
        k = rng.integers(0, len(arr), len(arr)); v[t] = arr[k, 0].sum() / arr[k, 1].sum() * 90
    rs_rank.append(int(pd.Series(v).rank(ascending=False, method="min")[MALI]))
rs_rank = np.array(rs_rank)
# stabilité des joueurs sur un tournoi : matchs alternés (1er, 3e, 5e... contre 2e, 4e...) de chaque joueur
pmm = cp.groupby(["player_id", "match_id"])["xt_added"].sum().reset_index()
con2 = duckdb.connect(os.path.join(REPO, "data/warehouse.duckdb"), read_only=True)
pmin = con2.execute("select m.player_id, m.match_id, m.minutes, s.match_date from silver.player_match_minutes m join silver.matches s using (match_id) where m.minutes > 0").df()
con2.close()
pmin = pmin.merge(pmm, on=["player_id", "match_id"], how="left").fillna({"xt_added": 0}).sort_values(["player_id", "match_date", "match_id"])
pmin["half"] = pmin.groupby("player_id").cumcount() % 2
hh = pmin.groupby(["player_id", "half"]).agg(xt=("xt_added", "sum"), mn=("minutes", "sum")).reset_index()
hh = hh.pivot(index="player_id", columns="half", values=["xt", "mn"]).dropna()
gk = set(pt.loc[pt["position"] == "Goalkeeper", "player_id"])
hh = hh[(hh[("mn", 0)] >= 90) & (hh[("mn", 1)] >= 90) & ~hh.index.isin(gk)]
split_rho = float(spearmanr(hh[("xt", 0)] / hh[("mn", 0)], hh[("xt", 1)] / hh[("mn", 1)])[0])
# rang du Mali avec le modèle des matchs de sélections et le modèle sans La Liga
def team_rank(xv):
    v = (AT @ xv) / teams["minutes"].to_numpy() * 90
    return int(pd.Series(v).rank(ascending=False, method="min").iloc[tix[MALI]])

# ---------------------------------------------------------------- sorties
meta_common = {"source": "Hudl StatsBomb Open Data (licence non commerciale, attribution « Hudl StatsBomb »)",
               "genere_le": datetime.date.today().isoformat()}

dump("xt_grid.json", {
    **meta_common,
    "description": "Expected Threat (xT, Karun Singh 2019) : probabilité qu'une possession qui passe par la case finisse en but dans les prochaines actions.",
    "grille": {"nx": NX, "ny": NY, "terrain": [120, 80], "case_x": 120 / NX, "case_y": 80 / NY,
               "orientation": "l'équipe qui attaque va vers x = 120 ; valeurs[cy][cx], cy = 0 en y = 0 (côté gauche de l'attaquant dans les coordonnées StatsBomb), cx = 0 près de son propre but",
               "indice_case": "z = cy * 16 + cx, cx = floor(x / 7.5), cy = floor(y / 6.667), bornés"},
    "valeurs": [[r6(v) for v in row] for row in G],
    "ic95_bas": [[r6(v) for v in row] for row in grid(lo)],
    "ic95_haut": [[r6(v) for v in row] for row in grid(hi)],
    "composantes": {"s_tir": [[r6(v) for v in row] for row in grid(full["s"])],
                    "m_deplacement": [[r6(v) for v in row] for row in grid(full["m"])],
                    "g_but_si_tir": [[r6(v) for v in row] for row in grid(full["g"])]},
    "methode": {
        "actions_de_depart": "passes de jeu courant (hors touches, coups francs, six mètres, corners, engagements, dégagements pour blessure) et conduites d'au moins 3 unités (~2,7 m) ; tirs de jeu courant",
        "reussite": "passe sans 'outcome' StatsBomb (= réussie) ; une conduite est toujours réussie",
        "g": "moyenne du xG StatsBomb des tirs de jeu courant de la case (choix : moins bruité que le taux de buts réel ; variante taux réel fournie dans validation.json)",
        "iteration": "xT(z) = s(z) g(z) + m(z) Σ T(z→z') xT(z'), départ à 0, arrêt quand l'écart max < 1e-7",
        "iterations": full["iterations"], "ecart_final": full["deltas"][-1], "converge": bool(full["converged"]),
        "rayon_spectral_mT": round(spec, 4)},
    "entrainement": n_info,
    "controles": {
        "max": r6(xt.max()), "case_max": {"cx": cx_max, "cy": cy_max, "x": [cx_max * 7.5, (cx_max + 1) * 7.5], "y": [round(cy_max * 80 / 12, 2), round((cy_max + 1) * 80 / 12, 2)]},
        "min": r6(xt.min()), "mediane": r6(np.median(xt)),
        "propre_moitie_max": r6(own_half.max()),
        "part_hausses_vers_le_but_bandes_centrales": round(inc_central, 4),
        "part_hausses_vers_le_but_moyenne_des_colonnes": round(inc_cols, 4),
        "symetrie_gauche_droite_pearson": round(mirror_r, 4),
        "colonnes_moyennes": [r6(v) for v in col_mean]},
})

dump("validation.json", {
    **meta_common,
    "matchs_mis_de_cote": {"principe": "20 % des matchs d'entraînement tirés au hasard (graine 2026) ; modèle refait sur les 80 % restants, puis évalué sur les possessions des matchs mis de côté",
                           "matchs_test": int(len(test_idx)), "matchs_apprentissage": int(len(train_idx)),
                           "possessions": val_test,
                           "niveau_equipe_match": val_team,
                           "lecture": "AUC : probabilité qu'une possession avec tir (ou but) ait plus de xT ajouté qu'une possession sans. 0,5 = hasard, 1 = parfait. 'progress' = mètres gagnés vers le but par les passes et conduites réussies, 'n_moves' = nombre de passes et conduites : deux repères naïfs."},
    "can_2023_hors_domaine": {"principe": "les 52 matchs de la CAN 2023 ne sont pas dans l'entraînement ; modèle complet", **val_afcon},
    "stabilite": {
        "moities": {"tirages": 20, "pearson_moyen": round(float(halves[:, 0].mean()), 4), "pearson_min": round(float(halves[:, 0].min()), 4),
                    "spearman_moyen": round(float(halves[:, 1].mean()), 4), "ecart_max_case_moyen": round(float(halves[:, 2].mean()), 4),
                    "max_grille_moitie_a_b": [round(float(halves[:, 3].mean()), 4), round(float(halves[:, 4].mean()), 4)]},
        "bootstrap": {"tirages": B, "unite": "match", "largeur_relative_ic95_mediane": round(float(np.median(rel_w)), 4),
                      "largeur_relative_ic95_max": round(float(np.max(rel_w)), 4),
                      "ic95_case_max": [r6(lo[zmax]), r6(hi[zmax])]},
        "sensibilite_echantillon": {
            "la_liga_seule_vs_reste_pearson": round(float(pearsonr(x_liga, x_noliga)[0]), 4),
            "la_liga_seule_max": r6(x_liga.max()), "sans_la_liga_max": r6(x_noliga.max()),
            "selections_seules_vs_complet_pearson": round(float(pearsonr(x_sel, xt)[0]), 4),
            "selections_seules_matchs": int(clubs.sum()), "selections_seules_max": r6(x_sel.max()),
            "rang_mali_modele_selections_seules": team_rank(x_sel), "rang_mali_modele_sans_la_liga": team_rank(x_noliga)},
        "sensibilite_methode": {
            "g_taux_de_buts_reel_vs_xg_pearson": round(float(pearsonr(emp["xt"], xt)[0]), 4), "g_taux_de_buts_reel_max": r6(emp["xt"].max()),
            "toutes_conduites_vs_conduites_3u_pearson": round(float(pearsonr(full0["xt"], xt)[0]), 4), "toutes_conduites_max": r6(full0["xt"].max()),
            "rang_mali_g_taux_reel": team_rank(emp["xt"])},
    },
})

# joueurs du Mali
def player_rec(r):
    i = pid_index[r.player_id]
    rec = {"player_id": int(r.player_id), "joueur": r.display_name or r.player, "nom_complet": r.player,
           "poste_principal": r.position, "role": r.role, "role_fr": ROLE_FR.get(r.role), "part_actions_dans_le_role": r6(r.part),
           "minutes": round(float(r.minutes), 1), "matchs": int(r.matches), "titularisations": int(r.starts),
           "xt_ajoute": r6(r.xt), "xt_ajoute_positif_seul": r6(r.xt_pos), "xt_p90": r6(r.xt_p90),
           "passes": {"n": int(r.n_pass), "xt": r6(r.xt_pass), "xt_p90": r6(r.xt_pass_p90), "rang": None if np.isnan(r.rang_xt_pass_p90) else int(r.rang_xt_pass_p90)},
           "conduites": {"n": int(r.n_carry), "xt": r6(r.xt_carry), "xt_p90": r6(r.xt_carry_p90), "rang": None if np.isnan(r.rang_xt_carry_p90) else int(r.rang_xt_carry_p90)},
           "eligible": bool(r.eligible)}
    if r.eligible:
        br = boot_rank[:, i]
        rec.update({"rang": int(r.rang), "sur": n_elig,
                    "rang_poste": None if np.isnan(r.rang_poste) else int(r.rang_poste),
                    "effectif_poste": None if np.isnan(r.effectif_poste) else int(r.effectif_poste),
                    "rang_bootstrap_ic90": [int(np.percentile(br, 5)), int(np.percentile(br, 95))],
                    "rang_bootstrap_median": float(np.median(br))})
        if not r.role_net: rec["note_poste"] = "pas de rôle net (moins de 50 % des actions dans un même rôle) : pas de rang au poste"
    else:
        rec["note"] = "gardien : hors classement" if r.position == "Goalkeeper" else f"moins de {MIN_MIN} minutes : hors classement"
    return rec

mali = pl[pl["team"] == MALI].sort_values(["eligible", "xt_p90"], ascending=[False, False])
top_all = pl[elig].sort_values("rang").head(15)
dump("mali_players.json", {
    **meta_common,
    "definition": "xT ajouté = xT(case d'arrivée) − xT(case de départ) pour chaque passe réussie de jeu courant et chaque conduite d'au moins 3 unités ; crédité au joueur qui fait l'action. Les passes ratées ne retirent rien (choix de Karun Singh).",
    "minutes": "chrono du match (90 ou 120 par match), table gold.player_tournament du pipeline",
    "classement": f"tous les joueurs de champ de la CAN 2023 avec au moins {MIN_MIN} minutes ({n_elig} joueurs), par xT ajouté par 90 minutes ; rang 1 = le plus haut ; ex aequo au même rang",
    "poste": "rôle fin de la page (malidata/profils.py) : rôle où le joueur a fait au moins 50 % de ses actions",
    "effectifs_par_role": {k: int(v) for k, v in pl[elig & pl["role_net"]]["role"].value_counts().items()},
    "stabilite_sur_le_tournoi": {"principe": "matchs de chaque joueur coupés en deux (1er, 3e, 5e… contre 2e, 4e…), au moins 90 minutes de chaque côté, gardiens exclus ; corrélation de rang du xT ajouté par 90 entre les deux moitiés",
                                 "joueurs": int(len(hh)), "spearman": round(split_rho, 4)},
    "rang_bootstrap": f"intervalle à 90 % du rang sur {B} grilles xT refaites par bootstrap des matchs d'entraînement (incertitude du modèle seulement, pas du petit nombre de matchs)",
    "joueurs": [player_rec(r) for r in mali.itertuples()],
    "top15_can_2023": [{"rang": int(r.rang), "joueur": r.display_name or r.player, "equipe": r.team, "role": r.role,
                        "minutes": round(float(r.minutes), 1), "xt_p90": r6(r.xt_p90)} for r in top_all.itertuples()],
})

mali_tm = tmatch[tmatch["team"] == MALI].sort_values("match_id")
dump("teams.json", {
    **meta_common,
    "definition": "xT généré = somme du xT ajouté par les passes réussies et conduites de l'équipe ; par 90 minutes de match (90 ou 120 selon prolongation). xT concédé = xT généré par l'adversaire.",
    "equipes": [{"rang": int(r.rang), "equipe": r.team, "matchs": int(r.matchs), "minutes": int(r.minutes),
                 "xt": r6(r.xt), "xt_p90": r6(r.xt_p90), "xt_positif_p90": r6(r.xt_pos_p90),
                 "rang_positif": int(r.rang_positif),
                 "xt_concede_p90": r6(r.xt_concede_p90), "rang_concede": int(r.rang_concede)}
                for r in teams.sort_values("rang").itertuples()],
    "mali": {"rang": int(teams.loc[teams.team == MALI, "rang"].iloc[0]), "sur": 24,
             "rang_bootstrap_modele_ic90": [int(np.percentile(mali_rank_boot, 5)), int(np.percentile(mali_rank_boot, 95))],
             "rang_reechantillonnage_matchs_ic90": [int(np.percentile(rs_rank, 5)), int(np.percentile(rs_rank, 95))],
             "lecture_incertitude": "le modèle est très stable (bootstrap de la grille) ; l'incertitude vient surtout du petit nombre de matchs (rééchantillonnage des matchs de chaque équipe, 2000 tirages)",
             "rang_positif": int(teams.loc[teams.team == MALI, "rang_positif"].iloc[0]),
             "rang_concede": int(teams.loc[teams.team == MALI, "rang_concede"].iloc[0]),
             "par_match": [{"match_id": int(r.match_id), "adversaire": r.opp, "minutes": int(r.minutes), "xt": r6(r.xt), "xt_concede": r6(r.xt_concede)}
                           for r in mali_tm.itertuples()]},
})

# ---------------------------------------------------------------- possession la plus menaçante du Mali
mp = cred[(cred["team"] == MALI) & (cred["possession_team"] == MALI)]
poss = mp.groupby(["match_id", "possession"]).agg(xt=("xt_added", "sum"), n=("xt_added", "size")).reset_index().sort_values("xt", ascending=False)
matches_info = {r.match_id: r for r in smatches.itertuples()}
ON_BALL = {"Pass", "Carry", "Shot", "Dribble", "Ball Receipt*", "Miscontrol", "Dispossessed", "Duel", "Foul Won",
           "Clearance", "Interception", "Ball Recovery", "Goal Keeper", "Block", "Foul Committed", "Pressure", "Dribbled Past"}


def export_poss(mid, pnum):
    ev = json.load(open(os.path.join(REPO, f"data/bronze/events/{mid}.json"), encoding="utf-8"))
    sel = [e for e in ev if e["possession"] == pnum and e["type"]["name"] in ON_BALL]
    xmap = {(r.idx): r for r in afx[(afx["match_id"] == mid) & (afx["possession"] == pnum)].itertuples()}
    def secs(e): h, m, s = e["timestamp"].split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
    t0 = secs(sel[0])
    disp = dict(zip(names["player_id"], names["display_name"]))
    seq = []
    for e in sel:
        t = e["type"]["name"]; d = {"index": e["index"], "type": t, "periode": e["period"], "timestamp": e["timestamp"],
                                   "minute": e["minute"], "seconde": e["second"], "t_relatif_s": round(secs(e) - t0, 3),
                                   "duree_s": e.get("duration"), "equipe": e["team"]["name"],
                                   "joueur": disp.get((e.get("player") or {}).get("id"), (e.get("player") or {}).get("name")),
                                   "player_id": (e.get("player") or {}).get("id"), "location": e.get("location")}
        if t == "Pass":
            p = e["pass"]; d.update({"end_location": p["end_location"], "receveur": disp.get((p.get("recipient") or {}).get("id"), (p.get("recipient") or {}).get("name")),
                                     "hauteur": (p.get("height") or {}).get("name"), "resultat": (p.get("outcome") or {}).get("name", "réussie"),
                                     "type_passe": (p.get("type") or {}).get("name"), "centre": p.get("cross", False)})
        elif t == "Carry": d["end_location"] = e["carry"]["end_location"]
        elif t == "Shot":
            s = e["shot"]; d.update({"end_location": s["end_location"], "xg": s.get("statsbomb_xg"), "resultat": s["outcome"]["name"],
                                     "surface": (s.get("body_part") or {}).get("name"), "type_tir": s["type"]["name"]})
        elif t == "Dribble": d["resultat"] = e["dribble"]["outcome"]["name"]
        r = xmap.get(e["index"])
        if r is not None and r.is_move and r.is_success and e["team"]["name"] == MALI:
            d.update({"credite": True, "xt_depart": r6(r.xt_start), "xt_arrivee": r6(r.xt_end), "xt_ajoute": r6(r.xt_added)})
        elif t in ("Pass", "Carry"):
            d["credite"] = False
            d["raison_non_credite"] = ("coup de pied arrêté" if t == "Pass" and d.get("type_passe") in SET_PIECE_PASSES else
                                       "passe ratée" if t == "Pass" and d.get("resultat") != "réussie" else
                                       "conduite de moins de 3 unités" if t == "Carry" else "action adverse")
        seq.append(d)
    m = matches_info[mid]
    shots = [s for s in seq if s["type"] == "Shot"]
    names_in = []
    for s in seq:
        if s["equipe"] == MALI and s["joueur"] and s["type"] in ("Pass", "Carry", "Shot", "Dribble") and s["joueur"] not in names_in: names_in.append(s["joueur"])
    row = poss[(poss.match_id == mid) & (poss.possession == pnum)].iloc[0]
    rank = int((poss["xt"] > row.xt).sum() + 1)
    return {"match_id": int(mid), "match": f"{m.home_team} {m.home_score}-{m.away_score} {m.away_team}", "date": str(m.match_date)[:10], "phase": m.stage,
            "possession": int(pnum), "rang_parmi_possessions_du_mali": rank, "possessions_du_mali": int(len(poss)),
            "xt_ajoute_total": r6(row.xt), "passes_et_conduites_creditees": int(row.n),
            "debut": {"periode": sel[0]["period"], "timestamp": sel[0]["timestamp"], "minute": sel[0]["minute"], "seconde": sel[0]["second"]},
            "duree_s": round(secs(sel[-1]) + (sel[-1].get("duration") or 0) - t0, 2),
            "debut_de_possession": sel[0]["play_pattern"]["name"],
            "joueurs_du_mali": names_in,
            "fin": shots[-1] if shots else {"type": sel[-1]["type"]["name"] if isinstance(sel[-1]["type"], dict) else seq[-1]["type"]},
            "sequence": seq}

top = poss.iloc[0]
res = {**meta_common, "definition": "possession du Mali dont la somme du xT ajouté (passes réussies et conduites) est la plus élevée sur les 5 matchs",
       "animation": "garder les événements de l'équipe du Mali (Pass, Ball Receipt*, Carry, Dribble, Shot) pour la trajectoire du ballon ; t_relatif_s = secondes depuis le premier événement de la possession (horodatage StatsBomb dans la période) ; duree_s = durée de l'action",
       "coordonnees": "StatsBomb 120 x 80 ; pour une passe ou une conduite, location = départ, end_location = arrivée ; chaque événement est orienté dans le sens d'attaque de l'équipe qui agit (les actions adverses sont donc en miroir : x' = 120 − x, y' = 80 − y pour les ramener au repère du Mali)",
       "top5": [{"match_id": int(r.match_id), "adversaire": opp[(r.match_id, MALI)], "possession": int(r.possession), "xt_ajoute": r6(r.xt), "actions": int(r.n)} for r in poss.head(5).itertuples()],
       "meilleure": export_poss(int(top.match_id), int(top.possession))}
if int(top.match_id) == QF_CIV:
    alt = poss[poss.match_id != QF_CIV].iloc[0]
    res["meilleure_hors_quart_de_finale"] = export_poss(int(alt.match_id), int(alt.possession))
dump("top_possession.json", res)
print("done")

"""Expected Threat (Karun Singh, 2019) : grille 16 x 12, itération sur les valeurs.
Conventions : coordonnées StatsBomb (120 x 80, l'équipe qui agit attaque toujours vers x = 120).
Cellule z = cy * NX + cx  (cx : 0..15 le long du terrain, cy : 0..11 en largeur)."""
import numpy as np
import pandas as pd
import scipy.sparse as sp

NX, NY = 16, 12
L, W = 120.0, 80.0
NZ = NX * NY
SET_PIECE_PASSES = {"Throw-in", "Free Kick", "Goal Kick", "Corner", "Kick Off"}
MIN_CARRY = 3.0          # longueur minimale d'une conduite (unités StatsBomb, ~2,7 m), comme socceraction (3 m)

def cell(x, y):
    cx = np.clip((np.asarray(x, float) / (L / NX)).astype(int), 0, NX - 1)
    cy = np.clip((np.asarray(y, float) / (W / NY)).astype(int), 0, NY - 1)
    return cy * NX + cx

def tag_actions(df, min_carry=MIN_CARRY):
    """Ajoute is_move, is_success, is_shot, z, z_end."""
    d = df.copy()
    for c in d.columns:
        if isinstance(d[c].dtype, pd.CategoricalDtype): d[c] = d[c].astype(object)
    is_pass = (d["type"] == "Pass") & ~d["sub_type"].isin(SET_PIECE_PASSES) & (d["outcome"].fillna("") != "Injury Clearance")
    clen = np.hypot(d["ex"] - d["x"], d["ey"] - d["y"])
    is_carry = (d["type"] == "Carry") & (clen >= min_carry)
    d["is_move"] = is_pass | is_carry
    d["is_success"] = (is_pass & d["outcome"].isna()) | is_carry
    d["is_shot"] = (d["type"] == "Shot") & (d["sub_type"] == "Open Play")
    d["is_goal"] = d["is_shot"] & (d["outcome"] == "Goal")
    d["z"] = cell(d["x"], d["y"])
    d["z_end"] = -1
    m = d["ex"].notna()
    d.loc[m, "z_end"] = cell(d.loc[m, "ex"], d.loc[m, "ey"])
    return d

def match_counts(d):
    """Comptes par match : S, M, G, XG (n_matches x 192) et T (n_matches x 192*192), creux."""
    mids = np.sort(d["match_id"].unique()); pos = {m: i for i, m in enumerate(mids)}
    r = d["match_id"].map(pos).to_numpy()
    def mat(mask, col, vals=None, ncol=NZ):
        v = np.ones(mask.sum()) if vals is None else vals[mask]
        return sp.csr_matrix((v, (r[mask], col[mask])), shape=(len(mids), ncol))
    z = d["z"].to_numpy(); ze = d["z_end"].to_numpy()
    sh = d["is_shot"].to_numpy(); mv = d["is_move"].to_numpy(); ok = (d["is_move"] & d["is_success"]).to_numpy()
    gl = d["is_goal"].to_numpy(); xg = d["xg"].fillna(0).to_numpy(float)
    return {"mids": mids, "S": mat(sh, z), "M": mat(mv, z), "G": mat(gl, z), "XG": mat(sh, z, xg),
            "T": mat(ok, z * NZ + np.where(ok, ze, 0), ncol=NZ * NZ)}

def fit(C, weights=None, g_mode="xg", tol=1e-7, max_iter=500):
    n = len(C["mids"])
    w = np.ones(n) if weights is None else np.asarray(weights, float)
    S = w @ C["S"]; M = w @ C["M"]; G = w @ C["G"]; XG = w @ C["XG"]
    T = (w @ C["T"]).reshape(NZ, NZ)
    tot = S + M
    with np.errstate(invalid="ignore", divide="ignore"):
        s = np.where(tot > 0, S / tot, 0.0); m = np.where(tot > 0, M / tot, 0.0)
        g = np.where(S > 0, (XG if g_mode == "xg" else G) / S, 0.0)
        Tn = np.where(M[:, None] > 0, T / M[:, None], 0.0)
    xt = np.zeros(NZ); hist = []
    for it in range(max_iter):
        new = s * g + m * (Tn @ xt)
        delta = float(np.max(np.abs(new - xt))); hist.append(delta); xt = new
        if delta < tol: break
    return {"xt": xt, "s": s, "m": m, "g": g, "T": Tn, "S": S, "M": M, "G": G, "XG": XG,
            "iterations": len(hist), "deltas": hist, "converged": hist[-1] < tol}

def grid(v):
    """Vecteur 192 -> tableau [12 lignes (y)][16 colonnes (x)]."""
    return np.asarray(v).reshape(NY, NX)

def add_xt(d, xt):
    d = d.copy()
    ok = d["is_move"] & d["is_success"]
    d["xt_start"] = np.where(ok, xt[d["z"].to_numpy()], np.nan)
    d["xt_end"] = np.where(ok, xt[np.clip(d["z_end"].to_numpy(), 0, NZ - 1)], np.nan)
    d["xt_added"] = d["xt_end"] - d["xt_start"]
    return d

def possessions(d):
    """Une ligne par possession : xT ajouté par l'équipe en possession, tir / but (hors penalty) dans la possession."""
    own = d[d["team"] == d["possession_team"]].copy()
    ok = own["is_move"] & own["is_success"]
    own["xt_pos"] = own["xt_added"].where(own["xt_added"] > 0, 0.0).fillna(0.0)
    own["progress"] = ((own["ex"] - own["x"]) * ok).fillna(0.0)
    own["shot"] = (own["type"] == "Shot") & (own["sub_type"] != "Penalty")
    own["goal"] = own["shot"] & (own["outcome"] == "Goal")
    own["xt_added0"] = own["xt_added"].fillna(0.0)
    g = own.groupby(["match_id", "possession"])
    out = g.agg(team=("possession_team", "first"), play_pattern=("play_pattern", "first"),
                xt_added=("xt_added0", "sum"), xt_pos=("xt_pos", "sum"), n_moves=("is_move", "sum"),
                progress=("progress", "sum"), shot=("shot", "any"), goal=("goal", "any")).reset_index()
    return out

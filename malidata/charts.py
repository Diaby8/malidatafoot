"""Graphiques d'analyse, aux couleurs de la page (jaune or, vert, rouge)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.patches import Arc, Circle, Rectangle  # noqa: E402

from .config import ROOT, Config, get_logger  # noqa: E402

log = get_logger("charts")

OR, OR_P, VERT, VERT_D, ROUGE, BLANC = "#F6C41C", "#FCE38A", "#0B7A3B", "#064A25", "#D4252A", "#FFFFFF"
FONTS = ROOT / "assets" / "fonts"
F_IMP = fm.FontProperties(fname=str(FONTS / "BarlowCondensed-BlackItalic.ttf"))
F_NUM = fm.FontProperties(fname=str(FONTS / "BarlowCondensed-ExtraBold.ttf"))
F_TXT = fm.FontProperties(fname=str(FONTS / "Montserrat-SemiBold.ttf"))
F_BLD = fm.FontProperties(fname=str(FONTS / "Montserrat-ExtraBold.ttf"))


def fr(value: float, nd: int = 2) -> str:
    return f"{value:.{nd}f}".replace(".", ",")


def short_names(players: list[str]) -> dict[str, str]:
    """Nom de famille seul, avec l'initiale du prénom quand deux joueurs le partagent."""
    last = [p.split()[-1] for p in players]
    return {p: (f"{p[0]}. {p.split()[-1]}" if last.count(p.split()[-1]) > 1 else p.split()[-1]) for p in players}


def canvas(info: str, title: str, box: str, source: str):
    """Fond, bloc titre (ligne rouge, titre, cartouche vert) et pied de page communs."""
    fig = plt.figure(figsize=(10.8, 10.8), dpi=150, facecolor=OR)
    fig.text(0.06, 0.945, info, color=ROUGE, fontproperties=F_BLD, fontsize=13)
    fig.text(0.06, 0.868, title, color=VERT_D, fontproperties=F_IMP, fontsize=58)
    t = fig.text(0.072, 0.822, box, color=OR_P, fontproperties=F_IMP, fontsize=27,
                 bbox=dict(facecolor=VERT, edgecolor="none", pad=7))
    t.set_va("center")
    fig.text(0.06, 0.035, "MaliDataFoot", color=VERT_D, fontproperties=F_BLD, fontsize=13)
    fig.text(0.94, 0.035, source, color=VERT_D, alpha=0.75, fontproperties=F_TXT, fontsize=10, ha="right")
    return fig


def draw_half_pitch(ax) -> None:
    """Moitié de terrain offensive, vue de derrière l'attaquant (but en haut)."""
    lw, c = 2.2, OR_P
    ax.add_patch(Rectangle((0, 60), 80, 60, fill=False, ec=c, lw=lw))
    ax.add_patch(Rectangle((18, 102), 44, 18, fill=False, ec=c, lw=lw))
    ax.add_patch(Rectangle((30, 114), 20, 6, fill=False, ec=c, lw=lw))
    ax.add_patch(Rectangle((36, 120), 8, 1.6, fill=False, ec=c, lw=lw))
    ax.add_patch(Arc((40, 108), 20, 20, theta1=217, theta2=323, ec=c, lw=lw))
    ax.add_patch(Arc((40, 60), 20, 20, theta1=0, theta2=180, ec=c, lw=lw))
    ax.add_patch(Circle((40, 108), 0.5, color=c))
    ax.set_xlim(-2, 82), ax.set_ylim(58, 123), ax.set_aspect("equal"), ax.axis("off")


def draw_pitch(ax) -> None:
    lw, c = 2.0, OR_P
    ax.add_patch(Rectangle((0, 0), 120, 80, fill=False, ec=c, lw=lw))
    ax.plot([60, 60], [0, 80], color=c, lw=lw)
    ax.add_patch(Circle((60, 40), 10, fill=False, ec=c, lw=lw))
    for x0, sign in ((0, 1), (120, -1)):
        ax.add_patch(Rectangle((x0, 18), sign * 18, 44, fill=False, ec=c, lw=lw))
        ax.add_patch(Rectangle((x0, 30), sign * 6, 20, fill=False, ec=c, lw=lw))
    ax.set_xlim(-2, 122), ax.set_ylim(82, -2), ax.set_aspect("equal"), ax.axis("off")


def shot_map(d: dict, out: Path) -> None:
    shots, tot = d["tirs"], d["totaux"]
    fig = canvas("CAN 2023 | 5 MATCHS | TOUS LES TIRS DU MALI", "LES TIRS DES AIGLES",
                 f"{tot['tirs']} TIRS | {fr(tot['xg'])} BUTS ATTENDUS | {sum(s['is_goal'] for s in shots)} BUTS SUR TIR",
                 "Données : StatsBomb Open Data")
    ax = fig.add_axes([0.06, 0.08, 0.88, 0.70])
    draw_half_pitch(ax)
    for s in sorted(shots, key=lambda s: s["is_goal"]):
        size = 90 + 2200 * s["xg"]
        if s["is_goal"]:
            ax.scatter(s["y"], s["x"], s=size, color=BLANC, edgecolor=VERT_D, linewidth=3.2, zorder=5)
            ax.annotate(f"{s['player'].split()[-1]} {s['minute'] + 1}'", (s["y"], s["x"]), xytext=(0, -22),
                        textcoords="offset points", ha="center", va="top", color=VERT_D, fontproperties=F_BLD, fontsize=10, zorder=6)
        else:
            ax.scatter(s["y"], s["x"], s=size, color=VERT, alpha=0.55, edgecolor=VERT_D, linewidth=1.2, zorder=4)
    ax.text(1, 61.5, "Taille du point = probabilité de but du tir (xG).  Blanc = but.",
            color=VERT_D, fontproperties=F_TXT, fontsize=11, va="bottom")
    fig.savefig(out, facecolor=OR), plt.close(fig)


def xg_by_match(d: dict, out: Path) -> None:
    ms, tot = d["matches"], d["totaux"]
    fig = canvas("CAN 2023 | BUTS ATTENDUS (xG) PAR MATCH", "CRÉÉ VS CONCÉDÉ",
                 f"{fr(tot['xg'])} xG POUR | {fr(tot['xg_contre'])} xG CONTRE", "Données : StatsBomb Open Data")
    ax = fig.add_axes([0.30, 0.10, 0.62, 0.66], facecolor=OR)
    mx = max(max(m["xg"], m["xg_against"]) for m in ms)
    for i, m in enumerate(ms):
        y = len(ms) - 1 - i
        ax.barh(y + 0.19, m["xg"], height=0.34, color=VERT, zorder=3)
        ax.barh(y - 0.19, m["xg_against"], height=0.34, color=ROUGE, zorder=3)
        ax.text(m["xg"] + mx * 0.02, y + 0.19, fr(m["xg"]), va="center", color=VERT_D, fontproperties=F_NUM, fontsize=26)
        ax.text(m["xg_against"] + mx * 0.02, y - 0.19, fr(m["xg_against"]), va="center", color=ROUGE, fontproperties=F_NUM, fontsize=26)
        ax.text(-mx * 0.05, y + 0.12, m["opponent"].upper(), ha="right", va="center", color=VERT_D, fontproperties=F_IMP, fontsize=27)
        ax.text(-mx * 0.05, y - 0.24, f"Score {m['goals_for']}-{m['goals_against']}", ha="right", va="center", color=VERT_D,
                fontproperties=F_TXT, fontsize=12)
    ax.set_xlim(0, mx * 1.22), ax.set_ylim(-0.6, len(ms) - 0.4), ax.axis("off")
    for x, label, color in ((0.30, "Mali", VERT), (0.41, "Adversaire", ROUGE)):
        fig.patches.append(Rectangle((x, 0.772), 0.016, 0.016, transform=fig.transFigure, color=color))
        fig.text(x + 0.022, 0.774, label, color=color, fontproperties=F_BLD, fontsize=13)
    fig.savefig(out, facecolor=OR), plt.close(fig)


def xg_timeline(d: dict, out: Path) -> None:
    last, ch, ends = d["matches"][-1], d["xg_chrono"], d["periodes_fin"]
    fig = canvas(f"CAN 2023 | QUART DE FINALE | MALI {last['goals_for']}-{last['goals_against']} {last['opponent'].upper()}",
                 "LE FIL DU QUART", f"{fr(last['xg'])} xG CONTRE {fr(last['xg_against'])} | ET L'ÉLIMINATION",
                 "Données : StatsBomb Open Data")
    ax = fig.add_axes([0.09, 0.11, 0.85, 0.63], facecolor=OR)
    end = ends[-1]
    for camp, color in (("equipe", VERT), ("adversaire", ROUGE)):
        xs, ys, cum = [0], [0], 0.0
        for s in (s for s in ch if s["camp"] == camp):
            cum += s["xg"]
            xs.append(s["minute_ecoulee"]), ys.append(cum)
            if s["is_goal"]:
                ax.scatter(s["minute_ecoulee"], cum, s=260, color=BLANC, edgecolor=color, linewidth=3.5, zorder=6)
                ax.annotate(f"But {s['player'].split()[-1]} ({s['minute']}')", (s["minute_ecoulee"], cum), xytext=(-8, 12),
                            textcoords="offset points", ha="right", color=color, fontproperties=F_BLD, fontsize=11)
            elif s["shot_type"] == "Penalty":
                ax.annotate(f"Penalty manqué ({s['minute']}')", (s["minute_ecoulee"], cum), xytext=(8, -4),
                            textcoords="offset points", color=color, fontproperties=F_BLD, fontsize=11, va="top")
        xs.append(end), ys.append(cum)
        ax.step(xs, ys, where="post", color=color, lw=4.5, zorder=4)
        ax.text(end + 1.5, cum, fr(cum), color=color, fontproperties=F_NUM, fontsize=30, va="center")
    top = ax.get_ylim()[1]
    for x, label in zip(ends[:-1], ("Mi-temps", "90 min", "105 min")):
        ax.axvline(x, color=OR_P, lw=1.8, zorder=1)
        ax.text(x, top * 1.01, label, ha="center", va="bottom", color=VERT_D, fontproperties=F_TXT, fontsize=9)
    for e in (e for e in d["expulsions"] if e["minute_ecoulee"] < end - 5):  # les rouges de toute fin de match ne pèsent pas sur le jeu
        ax.axvline(e["minute_ecoulee"], color=ROUGE, lw=1.8, ls=(0, (4, 3)), zorder=1)
        ax.text(e["minute_ecoulee"] + 1, top * 0.93, f"Rouge {e['player'].split()[-1]} ({e['minute']}')", color=ROUGE,
                fontproperties=F_BLD, fontsize=9.5, rotation=90, va="top")
    ax.set_xlim(0, end + 12), ax.set_ylim(0, top)
    ax.set_xticks([])
    ax.tick_params(colors=VERT_D, labelsize=11, length=0)
    for lab in ax.get_yticklabels():
        lab.set_fontproperties(F_TXT)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(VERT_D)
    ax.set_xlabel("Temps de jeu réel, arrêts de jeu et prolongation compris", color=VERT_D, fontproperties=F_TXT, fontsize=11, labelpad=10)
    ax.set_ylabel("Buts attendus cumulés", color=VERT_D, fontproperties=F_TXT, fontsize=11)
    fig.savefig(out, facecolor=OR), plt.close(fig)


def pass_network(d: dict, out: Path) -> None:
    net, last = d["reseau_passes"], d["matches"][-1]
    fig = canvas(f"CAN 2023 | MALI - {last['opponent'].upper()} | ONZE DE DÉPART",
                 "QUI JOUE AVEC QUI", f"LIAISONS DE PASSES JUSQU'À LA {int(net['until_min'])}e MINUTE",
                 "Données : StatsBomb Open Data")
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.70])
    draw_pitch(ax)
    pos = {n["player_id"]: n for n in net["nodes"]}
    names = short_names([n["player"] for n in net["nodes"]])
    mx = max(e["n"] for e in net["edges"])
    for e in net["edges"]:
        a, b = pos[e["a"]], pos[e["b"]]
        ax.plot([a["x"], b["x"]], [a["y"], b["y"]], color=VERT_D, lw=1 + 9 * e["n"] / mx, alpha=0.25 + 0.6 * e["n"] / mx, zorder=2, solid_capstyle="round")
    for n in net["nodes"]:
        ax.scatter(n["x"], n["y"], s=250 + 16 * n["passes"], color=BLANC, edgecolor=VERT_D, linewidth=3, zorder=4)
        ax.text(n["x"], n["y"] + 5.4, names[n["player"]], ha="center", va="top", color=VERT_D, fontproperties=F_BLD, fontsize=10, zorder=5)
    ax.annotate("", xy=(78, 85.5), xytext=(42, 85.5), arrowprops=dict(arrowstyle="-|>", color=VERT_D, lw=2.5), annotation_clip=False)
    ax.text(60, 88.5, "Sens de l'attaque", ha="center", color=VERT_D, fontproperties=F_TXT, fontsize=10)
    ax.set_ylim(91, -2)
    fig.savefig(out, facecolor=OR), plt.close(fig)


def score_ranking(d: dict, out: Path, min_minutes: int) -> None:
    sc = d["scores"]
    fig = canvas(f"CAN 2023 | MALIENS À {min_minutes} MIN ET PLUS | NOTE SUR 100", "MALI PLAYER SCORE",
                 "PRODUCTION | CRÉATION | PROGRESSION | DÉFENSE | TEMPS DE JEU", "Calcul : MaliDataFoot, données StatsBomb Open Data")
    ax = fig.add_axes([0.33, 0.07, 0.56, 0.70], facecolor=OR)
    for i, p in enumerate(sc):
        y = len(sc) - 1 - i
        color = VERT if i < 3 else OR_P
        ax.barh(y, p["score"], height=0.62, color=color, zorder=3)
        ax.text(p["score"] + 1.2, y, fr(p["score"], 1), va="center", color=VERT_D, fontproperties=F_NUM, fontsize=24)
        ax.text(-2, y + 0.1, p["player"], ha="right", va="center", color=VERT_D, fontproperties=F_BLD, fontsize=13)
        ax.text(-2, y - 0.25, f"{p['pos_group']} | {p['rang_poste']}e sur {p['effectif_poste']} au poste", ha="right", va="center",
                color=VERT_D, alpha=0.8, fontproperties=F_TXT, fontsize=8.5)
    ax.set_xlim(0, 100), ax.set_ylim(-0.6, len(sc) - 0.4), ax.axis("off")
    fig.savefig(out, facecolor=OR), plt.close(fig)


def run(cfg: Config) -> dict:
    out = cfg.path("outputs") / "graphiques"
    out.mkdir(parents=True, exist_ok=True)
    d = json.loads((cfg.path("outputs") / "resultats.json").read_text(encoding="utf-8"))
    shot_map(d, out / "1_tirs_des_aigles.png")
    xg_by_match(d, out / "2_xg_par_match.png")
    xg_timeline(d, out / "3_fil_du_quart.png")
    pass_network(d, out / "4_reseau_de_passes.png")
    score_ranking(d, out / "5_mali_player_score.png", cfg.min_minutes)
    log.info("graphiques : 5 fichiers dans %s", out.relative_to(ROOT))
    return {"charts": 5}

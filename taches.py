"""Toutes les commandes du projet, sur Windows, macOS et Linux.

    python taches.py installer      dépendances Python, JavaScript et navigateur de rendu
    python taches.py donnees        pipeline complet (bronze → silver → gold → profils → contrôles → export) + exports des visuels
    python taches.py tests          tests du pipeline
    python taches.py fiche          fiche joueur, versions X et TikTok
    python taches.py duel           duel, versions X et TikTok
    python taches.py grille         grille numérotée des variantes (32 cases)
    python taches.py bannieres      les 16 bannières X de la nouvelle DA + leurs planches
    python taches.py video          vidéo de lancement complète (≈ 5 min de rendu)
    python taches.py video --controle   seulement quelques images de la vidéo, pour vérifier
    python taches.py tout           donnees, tests, fiche, duel, grille, bannieres

Les visuels se fabriquent depuis le dossier visuels/ (ils y trouvent logos, photos et polices) ;
tout ce qui est produit va dans livrables/, qui n'est pas suivi par git.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
VIS = RACINE / "visuels"
LIV = RACINE / "livrables"
PY = sys.executable
NPM = "npm.cmd" if os.name == "nt" else "npm"
NPX = "npx.cmd" if os.name == "nt" else "npx"


def lance(*cmd, ou=VIS):
    print("›", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], cwd=ou, check=True)


def capture(html, png, w=1080, h=1350, echelle=2):
    lance("node", "shotu.mjs", html, png, w, h, echelle)


def installer():
    lance(PY, "-m", "pip", "install", "-r", "requirements.txt", ou=RACINE)
    lance(NPM, "install")
    if not os.environ.get("CHROMIUM_PATH"):
        lance(NPX, "playwright", "install", "chromium")
    if not shutil.which("ffmpeg"):
        print("⚠ ffmpeg introuvable : il n'est utile que pour la vidéo (voir README).")


def donnees():
    lance(PY, "-m", "malidata", "run", ou=RACINE)
    lance(PY, "duel_export.py", "Lassine Sinayoko", "Victor Osimhen", "../outputs/duel_v2.json")
    lance(PY, "vitrine_export.py")


def tests():
    lance(PY, "-m", "pytest", "-q", ou=RACINE)


def fiche():
    (LIV).mkdir(exist_ok=True)
    for fmt, h in (("x", 1350), ("tiktok", 1920)):
        lance(PY, "variantes.py", "fiche", "A", f"_fiche_{fmt}.html", fmt)
        capture(f"_fiche_{fmt}.html", LIV / f"fiche-joueur-{fmt}.png", 1080, h)


def duel():
    LIV.mkdir(exist_ok=True)
    for fmt, h in (("x", 1350), ("tiktok", 1920)):
        lance(PY, "duel_v2.py", "../outputs/duel_v2.json", f"_duel_{fmt}.html", fmt, "B")
        capture(f"_duel_{fmt}.html", LIV / f"duel-{fmt}.png", 1080, h)


def grille():
    lance(PY, "grille.py", LIV / "grille")


def bannieres():
    from PIL import Image, ImageDraw
    sys.path.insert(0, str(VIS))
    from polices import police

    dos = LIV / "bannieres"
    dos.mkdir(parents=True, exist_ok=True)
    lance(PY, "reel_cartes.py")
    ordre = [1, 13, 2, 3, 4, 14, 5, 7, 6, 8, 9, 16, 10, 15, 11, 12]  # numéros de la planche du 8 octobre 2026
    for i, k in enumerate(ordre, 1):
        lance(PY, "banniere_reel.py", k, f"_banniere_{k}.html")
        capture(f"_banniere_{k}.html", dos / f"{i:02d}.png", 1500, 500, 2)
    # planches de choix : chaque bannière avec son numéro
    for n, (a, b) in enumerate(((0, 9), (9, 16)), 1):
        pas = 413 + 78
        S = Image.new("RGB", (1280, 20 + (b - a) * pas), "#0E1A13")
        d = ImageDraw.Draw(S)
        for j, i in enumerate(range(a, b)):
            y = 20 + j * pas
            d.text((20, y + 6), str(i + 1), font=police(40, True), fill="#F6C41C")
            S.paste(Image.open(dos / f"{i + 1:02d}.png").convert("RGB").resize((1240, 413), Image.LANCZOS), (20, y + 60))
        S.save(dos / f"planche-{n}.png")


def video(controle=False):
    dos = LIV / "video"
    dos.mkdir(parents=True, exist_ok=True)
    lance(PY, "build_vitv.py")
    lance(PY, "scenes_md2.py")
    if controle:
        lance("node", "render2.mjs", 0, 0, 60, dos / "controle", "1.2,5,9,14,19,23.5,29,36.8")
        return
    lance(PY, "sfx_md2.py")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg est nécessaire pour assembler la vidéo (voir README).")
    images = VIS / "_images"
    shutil.rmtree(images, ignore_errors=True)
    total = round(37.45 * 60)
    bornes = [round(total * i / 4) for i in range(5)]
    lots = [subprocess.Popen(["node", "render2.mjs", str(bornes[i]), str(bornes[i + 1]), "60", str(images)], cwd=VIS) for i in range(4)]
    if any(p.wait() for p in lots):
        sys.exit("le rendu d'un lot a échoué")
    sortie = dos / "MaliDataFoot-video-de-lancement-tiktok.mp4"
    lance("ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", images / "f_%05d.jpg", "-i", "sfx_md2.wav",
          "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", sortie)
    shutil.copy(VIS / "sfx_md2.wav", dos / "MaliDataFoot-video-de-lancement-effets-sonores.wav")
    print("vidéo :", sortie)


def tout():
    donnees(); tests(); fiche(); duel(); grille(); bannieres()


if __name__ == "__main__":
    taches = dict(installer=installer, donnees=donnees, tests=tests, fiche=fiche, duel=duel, grille=grille,
                  bannieres=bannieres, video=video, tout=tout)
    if len(sys.argv) < 2 or sys.argv[1] not in taches:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "video":
        video("--controle" in sys.argv)
    else:
        taches[sys.argv[1]]()

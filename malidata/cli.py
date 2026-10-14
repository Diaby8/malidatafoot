"""Point d'entrée : `python -m malidata run` enchaîne toutes les étapes dans l'ordre."""
from __future__ import annotations

import argparse
import time

from . import aigles, analyses, charts, elo, export, gold, ingest, profils, quality, silver, simulation
from .config import get_logger, load_config

log = get_logger("pipeline")
STEPS = {
    "ingest": lambda cfg, a: ingest.run(cfg, force=a.force),
    "silver": lambda cfg, a: silver.run(cfg),
    "aigles": lambda cfg, a: aigles.run(cfg, force=a.force),
    "elo": lambda cfg, a: elo.run(cfg),
    "analyses": lambda cfg, a: analyses.run(cfg),
    "simulation": lambda cfg, a: simulation.run(cfg),
    "gold": lambda cfg, a: gold.run(cfg),
    "profils": lambda cfg, a: profils.run(cfg),
    "quality": lambda cfg, a: quality.run(cfg),
    "export": lambda cfg, a: export.run(cfg),
    "charts": lambda cfg, a: charts.run(cfg),
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="malidata", description="Pipeline de données football MaliDataFoot")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="exécute le pipeline")
    run.add_argument("--only", nargs="+", choices=list(STEPS), help="n'exécuter que ces étapes")
    run.add_argument("--force", action="store_true", help="retélécharger les fichiers bruts")
    run.add_argument("--config", help="chemin d'un autre fichier de configuration")
    args = parser.parse_args()

    cfg = load_config(args.config)
    t0 = time.time()
    for name in args.only or list(STEPS):
        t = time.time()
        STEPS[name](cfg, args)
        log.info("étape %-8s terminée en %.1f s", name, time.time() - t)
    log.info("pipeline terminé en %.1f s", time.time() - t0)


if __name__ == "__main__":
    main()

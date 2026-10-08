"""Étape 1 — BRONZE : collecte des fichiers bruts, sans les modifier.

Chaque fichier est téléchargé une seule fois (reprise possible), puis inscrit dans un
manifeste avec sa taille, son empreinte et sa date de collecte : on sait toujours
d'où vient une donnée et si elle a changé à la source.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .config import Config, get_logger

log = get_logger("ingest")


def _download(url: str, dest: Path, retries: int = 4) -> bytes:
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            json.loads(data)  # refuse un fichier tronqué ou une page d'erreur
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(data)
            tmp.replace(dest)  # écriture atomique : jamais de fichier à moitié écrit
            return data
        except Exception as exc:  # noqa: BLE001
            if attempt == retries:
                raise RuntimeError(f"échec du téléchargement de {url}") from exc
            time.sleep(1.5 * attempt)
    raise AssertionError("unreachable")


def run(cfg: Config, force: bool = False) -> dict:
    bronze = cfg.path("bronze")
    manifest_path = bronze / "_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    def fetch(rel: str) -> None:
        dest = bronze / rel
        if dest.exists() and rel in manifest and not force:
            return
        data = _download(f"{cfg.base_url}/{rel}", dest)
        manifest[rel] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    fetch("competitions.json")
    matches_rel = f"matches/{cfg.competition_id}/{cfg.season_id}.json"
    fetch(matches_rel)
    match_ids = [m["match_id"] for m in json.loads((bronze / matches_rel).read_text())]

    rels = [f"{kind}/{mid}.json" for mid in match_ids for kind in ("events", "lineups")]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, rels))

    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    total = sum(v["bytes"] for v in manifest.values())
    log.info("bronze : %d fichiers, %.1f Mo, %d matchs", len(manifest), total / 1e6, len(match_ids))
    return {"files": len(manifest), "bytes": total, "matches": len(match_ids)}

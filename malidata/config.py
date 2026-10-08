from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    raw: dict

    @property
    def base_url(self) -> str:
        return self.raw["source"]["base_url"]

    @property
    def competition_id(self) -> int:
        return int(self.raw["source"]["competition_id"])

    @property
    def season_id(self) -> int:
        return int(self.raw["source"]["season_id"])

    @property
    def team(self) -> str:
        return self.raw["team_focus"]

    @property
    def min_minutes(self) -> int:
        return int(self.raw["min_minutes"])

    def path(self, key: str) -> Path:
        p = ROOT / self.raw["paths"][key]
        if p.suffix == "":
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
        return p


def load_config(path: str | Path | None = None) -> Config:
    with open(path or ROOT / "config.yaml", encoding="utf-8") as f:
        return Config(yaml.safe_load(f))


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S")
    return logging.getLogger(name)

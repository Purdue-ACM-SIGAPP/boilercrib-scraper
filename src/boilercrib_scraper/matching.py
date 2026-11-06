import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SEED_PATH = DATA_DIR / "seed_buildings.json"
ALIASES_PATH = DATA_DIR / "aliases.json"

# Words that vary between sources without changing which building is meant
FILLER_WORDS = {"hall", "halls", "residences", "and", "the"}
SUGGESTION_CUTOFF = 80


@dataclass(frozen=True)
class SeedBuilding:
    id: str
    name: str
    acronym: str | None
    building_type: str


@dataclass
class MatchReport:
    matched: dict[str, list[SeedBuilding]] = field(default_factory=dict)
    unmatched: list[str] = field(default_factory=list)
    suggestions: dict[str, list[str]] = field(default_factory=dict)


def normalize(name: str) -> str:
    text = name.lower().replace("&", " and ")
    text = re.sub(r"\(ur apts\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return " ".join(w for w in text.split() if w not in FILLER_WORDS)


def load_seed(path: Path = SEED_PATH) -> list[SeedBuilding]:
    raw = cast(
        list[dict[str, str | None]], json.loads(path.read_text(encoding="utf-8"))
    )

    return [
        SeedBuilding(
            id=str(b["id"]),
            name=str(b["name"]),
            acronym=b.get("acronym"),
            building_type=str(b["buildingType"]),
        )
        for b in raw
    ]


def load_aliases(path: Path = ALIASES_PATH) -> dict[str, list[str]]:
    raw = cast(dict[str, list[str]], json.loads(path.read_text(encoding="utf-8")))

    return {normalize(k): v for k, v in raw.items()}


class Matcher:
    def __init__(
        self,
        seed: list[SeedBuilding] | None = None,
        aliases: dict[str, list[str]] | None = None,
    ) -> None:
        self.seed: list[SeedBuilding] = seed if seed is not None else load_seed()
        self.aliases: dict[str, list[str]] = (
            aliases if aliases is not None else load_aliases()
        )
        self._by_name: dict[str, SeedBuilding] = {b.name: b for b in self.seed}

        unknown = {n for names in self.aliases.values() for n in names} - set(
            self._by_name
        )

        if unknown:
            raise ValueError(
                f"aliases.json points at seed names that don't exist: {sorted(unknown)}"
            )

    def _candidates(self, building_type: str | None) -> list[SeedBuilding]:
        return [
            b
            for b in self.seed
            if building_type is None or b.building_type == building_type
        ]

    def match(
        self, raw_name: str, building_type: str | None = "Housing"
    ) -> list[SeedBuilding]:
        key = normalize(raw_name)
        candidates = self._candidates(building_type)

        if key in self.aliases:
            allowed = {b.name for b in candidates}

            return [self._by_name[n] for n in self.aliases[key] if n in allowed]

        return [b for b in candidates if normalize(b.name) == key]

    def report(
        self, raw_names: list[str], building_type: str | None = "Housing"
    ) -> MatchReport:
        result = MatchReport()
        choices = {b.name: normalize(b.name) for b in self._candidates(building_type)}

        for raw in dict.fromkeys(raw_names):
            found = self.match(raw, building_type)

            if found:
                result.matched[raw] = found
                continue

            result.unmatched.append(raw)

            close = process.extract(
                normalize(raw),
                choices,
                scorer=fuzz.WRatio,
                score_cutoff=SUGGESTION_CUTOFF,
                limit=3,
            )

            if close:
                result.suggestions[raw] = [name for _, _, name in close]

        return result

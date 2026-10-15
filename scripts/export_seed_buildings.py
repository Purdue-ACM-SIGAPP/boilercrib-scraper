# Run whenever the backend's seed buildings change.
# Usage:
# curl -sSL -o /tmp/seed.js https://raw.githubusercontent.com/Purdue-ACM-SIGAPP/boilercrib-backend/main/seed/seed.js
# uv run python scripts/export_seed_buildings.py /tmp/seed.js


import json
import re
import sys
from pathlib import Path
from typing import cast

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "seed_buildings.json"
KEEP = ("id", "name", "acronym", "buildingType")


def extract_buildings(seed_js: str) -> list[dict[str, str | None]]:
    start = seed_js.index("db.building.insertMany(") + len("db.building.insertMany(")
    end = seed_js.index("]);", start) + 1

    block = seed_js[start:end]
    block = re.sub(r'ObjectId\("([0-9a-f]+)"\)', r'"\1"', block)

    raw = cast(list[dict[str, object]], json.loads(block))

    buildings: list[dict[str, str | None]] = []

    for b in raw:
        b["id"] = b.pop("_id")
        buildings.append(
            {k: (str(b[k]) if b.get(k) is not None else None) for k in KEEP}
        )

    return buildings


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    buildings = extract_buildings(Path(sys.argv[1]).read_text(encoding="utf-8"))

    _ = OUTPUT.write_text(json.dumps(buildings, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(buildings)} buildings to {OUTPUT}")


if __name__ == "__main__":
    main()

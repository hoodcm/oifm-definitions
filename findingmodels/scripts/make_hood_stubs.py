# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "findingmodel",
# ]
# ///
"""Convert Hood CXR findings taxonomy CSV into OIFM finding model stubs.

Usage:
    python3 findingmodels/scripts/make_hood_stubs.py <csv_path>
"""

import csv
import json
import sys
from pathlib import Path

from findingmodel import FindingInfo
from findingmodel.common import model_file_name
from findingmodel.finding_model import FindingModelFull, _random_digits, ID_LENGTH
from findingmodel.tools.create_stub import create_model_stub_from_info
from findingmodel.tools.index_codes import add_standard_codes_to_model

SOURCE = "HOOD"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "hood"

# Track IDs within this run to prevent self-collision.
# The HOOD source prefix guarantees no collision with other sources (GMTS, MSFT, etc.)
_used_oifm: set[str] = set()
_used_oifma: set[str] = set()


def _gen_oifm_id() -> str:
    while True:
        candidate = f"OIFM_{SOURCE}_{_random_digits(ID_LENGTH)}"
        if candidate not in _used_oifm:
            _used_oifm.add(candidate)
            return candidate


def _gen_oifma_id() -> str:
    while True:
        candidate = f"OIFMA_{SOURCE}_{_random_digits(ID_LENGTH)}"
        if candidate not in _used_oifma:
            _used_oifma.add(candidate)
            return candidate


def add_ids(stub):
    """Convert FindingModelBase -> FindingModelFull with locally-generated IDs."""
    data = stub.model_dump()
    data["oifm_id"] = _gen_oifm_id()
    for attr in data.get("attributes", []):
        attr["oifma_id"] = _gen_oifma_id()
    return FindingModelFull.model_validate(data)


def parse_synonyms(raw: str) -> list[str] | None:
    if not raw or not raw.strip():
        return None
    parts = [s.strip() for s in raw.split(",") if s.strip()]
    return parts if parts else None


def ensure_name_length(name: str, synonyms: list[str] | None, category: str) -> tuple[str, list[str] | None]:
    """Ensure name >= 5 chars. Swap with a longer synonym, or prefix with category."""
    if len(name) >= 5:
        return name, synonyms

    # Try swapping with a longer synonym
    if synonyms:
        for i, syn in enumerate(synonyms):
            if len(syn) >= 5:
                new_synonyms = [name] + [s for j, s in enumerate(synonyms) if j != i]
                print(f"  swap: '{name}' -> '{syn}'")
                return syn, new_synonyms

    # Fall back: prefix with category
    expanded = f"{category} {name}"
    print(f"  expand: '{name}' -> '{expanded}'")
    return expanded, synonyms


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 findingmodels/scripts/make_hood_stubs.py <csv_path>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    created = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fid = row["id"].strip()
            name = row["name"].strip()
            category = row["category"].strip()
            synonyms = parse_synonyms(row.get("synonyms", ""))

            name, synonyms = ensure_name_length(name, synonyms, category)

            description = f"{name} on chest radiograph."
            info = FindingInfo(name=name, description=description, synonyms=synonyms)

            stub = create_model_stub_from_info(info, tags=[category, "CXR"])
            model = add_ids(stub)
            add_standard_codes_to_model(model)

            filename = model_file_name(model.name)
            output_path = OUTPUT_DIR / filename

            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(model.model_dump(exclude_none=True, mode="json"), out, indent=2)
                out.write("\n")

            print(f"  {fid} -> {model.oifm_id} {filename}")
            created += 1

    print(f"\nDone: {created} finding models written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

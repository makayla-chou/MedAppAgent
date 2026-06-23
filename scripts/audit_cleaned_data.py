from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import DATA_DIR, DEFAULT_SCHOOLS_FILE
from repositories.school_repository import DEFAULT_AAMC_RESIDENCY_FILE
from services.aamc_data_service import TABLE_FILES


CLEANED_ROOT = DATA_DIR / "cleaned"
INVENTORY_FILE = DATA_DIR / "metadata" / "medappagent_data_inventory.csv"

REPORT_CONTEXT_TABLES = {
    "acceptance_grid",
    "applicant_state",
    "major",
    "matriculant_state",
    "yearly",
    "state_outcomes",
    "undergraduate_demographics",
    "socioeconomic_access_summary",
    "medical_pipeline",
}


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _read_inventory() -> dict[str, dict[str, str]]:
    if not INVENTORY_FILE.exists():
        return {}

    with INVENTORY_FILE.open(newline="", encoding="utf-8-sig") as file:
        return {
            row["file"]: row
            for row in csv.DictReader(file)
            if row.get("file")
        }


def _registered_paths() -> dict[str, list[str]]:
    registered: dict[str, list[str]] = {}
    for table_name, paths in TABLE_FILES.items():
        for path in paths:
            registered.setdefault(_relative(path), []).append(table_name)
    return registered


def _runtime_paths() -> dict[str, str]:
    return {
        _relative(DEFAULT_SCHOOLS_FILE): "ranking school catalog",
        _relative(DEFAULT_AAMC_RESIDENCY_FILE): "ranking residency merge",
    }


def _usage_status(
    path: str,
    table_names: list[str],
    runtime_paths: dict[str, str],
) -> str:
    if path in runtime_paths:
        return runtime_paths[path]

    report_tables = sorted(
        table_name
        for table_name in table_names
        if table_name in REPORT_CONTEXT_TABLES
    )
    if report_tables:
        return "report and agent context: " + ", ".join(report_tables)

    if table_names:
        return "registered only: " + ", ".join(sorted(table_names))

    return "not wired"


def main() -> None:
    inventory = _read_inventory()
    registered = _registered_paths()
    runtime_paths = _runtime_paths()

    print(
        "path,registered_tables,usage_status,recommended_tier,"
        "ranking_use,recommended_use"
    )

    for path in sorted(CLEANED_ROOT.rglob("*.csv")):
        relative_path = _relative(path)
        table_names = registered.get(relative_path, [])
        inventory_key = relative_path.removeprefix("data/")
        inventory_row = inventory.get(
            inventory_key,
            inventory.get(Path(relative_path).name, {}),
        )
        print(
            ",".join(
                csv_escape(value)
                for value in (
                    relative_path,
                    ";".join(sorted(table_names)),
                    _usage_status(relative_path, table_names, runtime_paths),
                    inventory_row.get("recommended_tier", ""),
                    inventory_row.get("ranking_use", ""),
                    inventory_row.get("recommended_use", ""),
                )
            )
        )


def csv_escape(value: str) -> str:
    output = value.replace('"', '""')
    if any(character in output for character in ",\"\n"):
        return f'"{output}"'
    return output


if __name__ == "__main__":
    main()

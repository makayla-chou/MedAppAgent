import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from config import OUTPUT_DIR
from models.agent_reports import AgentReports


REPORT_FILENAMES = {
    "ranked_schools_csv": "ranked_schools.csv",
    "ranked_schools_text": "ranked_schools.txt",
    "profile_report": "profile_report.txt",
    "school_fit_report": "school_fit_report.txt",
    "critic_report": "critic_report.txt",
    "final_report": "final_report.md",
    "run_metadata": "run_metadata.json",
    "profile_snapshot": "profile_snapshot.json",
}


def make_safe_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip().lower())
    return cleaned.strip("_") or "student"


def create_report_run_id() -> str:
    """
    Create a sortable, collision-resistant identifier for one report run.

    Example:
        20260622t224501123456z_a1b2c3d4
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dt%H%M%S%fz")
    random_suffix = uuid4().hex[:8]
    return f"{timestamp}_{random_suffix}"


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _validate_directory(path: Path, description: str) -> None:
    """
    Refuse to use a symlink or ordinary file where a report directory belongs.
    """
    if not path.exists() and not path.is_symlink():
        return

    if path.is_symlink():
        raise ValueError(
            f"Refusing to use symlinked {description}: {path}"
        )

    if not path.is_dir():
        raise ValueError(
            f"{description.capitalize()} exists but is not a directory: {path}"
        )


def _prepare_owner_folder(
    output_root_path: Path,
    student_name: str,
    report_owner_id: str | None,
) -> Path:
    if report_owner_id is not None:
        owner_value = str(report_owner_id).strip()
        if not owner_value:
            raise ValueError("report_owner_id cannot be blank.")
        owner_folder_name = make_safe_name(owner_value)
    else:
        owner_folder_name = make_safe_name(student_name)

    owner_folder = output_root_path / owner_folder_name
    _validate_directory(owner_folder, "report owner folder")
    owner_folder.mkdir(parents=True, exist_ok=True)
    return owner_folder


def save_report_bundle(
    student_name: str,
    ranked_schools: pd.DataFrame,
    ranked_schools_text: str,
    agent_reports: AgentReports,
    final_report: str,
    report_run_id: str,
    generated_at_utc: str,
    profile_snapshot: dict[str, Any],
    output_root: str | Path = OUTPUT_DIR,
    report_owner_id: str | None = None,
) -> dict[str, Path]:
    """
    Save one immutable report run.

    Folder layout:
        outputs/<owner>/<run_id>/<report files>

    The authenticated Supabase user ID is used as <owner> when supplied.
    Local command-line runs fall back to the student's safe name.

    Every run is written into a fresh temporary directory and then moved into
    place atomically. Previous run folders are preserved.
    """
    if not isinstance(profile_snapshot, dict):
        raise ValueError("profile_snapshot must be a dictionary.")

    snapshot_json = json.dumps(
        profile_snapshot,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

    output_root_path = Path(output_root).expanduser()
    _validate_directory(output_root_path, "output root")
    output_root_path.mkdir(parents=True, exist_ok=True)

    owner_folder = _prepare_owner_folder(
        output_root_path=output_root_path,
        student_name=student_name,
        report_owner_id=report_owner_id,
    )

    safe_run_id = make_safe_name(report_run_id)
    if safe_run_id != report_run_id:
        raise ValueError(
            "report_run_id contains unsupported characters."
        )

    run_folder = owner_folder / report_run_id

    if run_folder.exists() or run_folder.is_symlink():
        raise FileExistsError(
            f"Report run folder already exists: {run_folder}"
        )

    temporary_folder = Path(
        tempfile.mkdtemp(
            prefix=f".{report_run_id}_",
            dir=owner_folder,
        )
    )

    temporary_paths = {
        key: temporary_folder / filename
        for key, filename in REPORT_FILENAMES.items()
    }

    metadata = {
        "run_id": report_run_id,
        "generated_at_utc": generated_at_utc,
        "student_name": student_name,
        "profile_snapshot_file": REPORT_FILENAMES["profile_snapshot"],
    }

    try:
        ranked_schools.to_csv(
            temporary_paths["ranked_schools_csv"],
            index=False,
        )
        save_text(
            temporary_paths["ranked_schools_text"],
            ranked_schools_text,
        )
        save_text(
            temporary_paths["profile_report"],
            agent_reports.profile_report,
        )
        save_text(
            temporary_paths["school_fit_report"],
            agent_reports.school_fit_report,
        )
        save_text(
            temporary_paths["critic_report"],
            agent_reports.critic_report,
        )
        save_text(
            temporary_paths["final_report"],
            final_report,
        )
        save_text(
            temporary_paths["run_metadata"],
            json.dumps(metadata, indent=2),
        )
        save_text(
            temporary_paths["profile_snapshot"],
            snapshot_json,
        )

        temporary_folder.replace(run_folder)

    except Exception:
        shutil.rmtree(temporary_folder, ignore_errors=True)
        raise

    return {
        key: run_folder / filename
        for key, filename in REPORT_FILENAMES.items()
    }

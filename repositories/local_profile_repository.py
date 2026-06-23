import json
from pathlib import Path
from typing import Any

from config import PROFILE_DIR


def get_available_profiles(profile_folder: Path = PROFILE_DIR) -> list[str]:
    profile_folder.mkdir(parents=True, exist_ok=True)
    return sorted(path.stem for path in profile_folder.glob("*.json"))


def resolve_profile_path(
    profile_name: str | Path,
    profile_folder: Path = PROFILE_DIR,
) -> Path:
    given_path = Path(profile_name)

    if given_path.exists():
        return given_path

    return profile_folder / f"{given_path.stem}.json"


def load_student_profile(
    profile_name: str | Path,
    profile_folder: Path = PROFILE_DIR,
) -> dict[str, Any]:
    profile_path = resolve_profile_path(profile_name, profile_folder)

    if not profile_path.exists():
        raise FileNotFoundError(f"Student profile not found: {profile_path}")

    with profile_path.open("r", encoding="utf-8") as file:
        student_profile = json.load(file)

    if not isinstance(student_profile, dict):
        raise ValueError("The student profile must contain a JSON object.")

    return student_profile


def save_student_profile(
    student_profile: dict[str, Any],
    profile_name: str,
    profile_folder: Path = PROFILE_DIR,
) -> Path:
    if not isinstance(student_profile, dict):
        raise ValueError("student_profile must be a dictionary.")

    profile_folder.mkdir(parents=True, exist_ok=True)
    profile_path = profile_folder / f"{Path(profile_name).stem}.json"

    with profile_path.open("w", encoding="utf-8") as file:
        json.dump(student_profile, file, indent=4, ensure_ascii=False)

    return profile_path


def update_student_profile(
    profile_name: str,
    updated_profile: dict[str, Any],
    profile_folder: Path = PROFILE_DIR,
) -> Path:
    profile_path = profile_folder / f"{Path(profile_name).stem}.json"

    if not profile_path.exists():
        raise FileNotFoundError(f"Cannot update missing profile: {profile_path}")

    return save_student_profile(updated_profile, profile_path.stem, profile_folder)


def delete_student_profile(
    profile_name: str,
    profile_folder: Path = PROFILE_DIR,
) -> None:
    profile_path = profile_folder / f"{Path(profile_name).stem}.json"

    if not profile_path.exists():
        raise FileNotFoundError(f"Student profile not found: {profile_path}")

    profile_path.unlink()

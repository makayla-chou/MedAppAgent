from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_DIR = DATA_DIR / "student_profiles"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_SCHOOLS_FILE = DATA_DIR / "cleaned" / "final_med_school_data.csv"

# These scales make score differences interpretable instead of assigning
# unrelated point bonuses. A difference of 0.20 GPA points or 5 MCAT points
# is treated as roughly one comparison unit.
GPA_COMPARISON_SCALE = 0.20
MCAT_COMPARISON_SCALE = 5.0
ACADEMIC_GPA_WEIGHT = 0.45
ACADEMIC_MCAT_WEIGHT = 0.55

PROFILE_AGENT_MODEL = os.getenv("PROFILE_AGENT_MODEL", "gpt-4.1-mini")
SCHOOL_FIT_AGENT_MODEL = os.getenv("SCHOOL_FIT_AGENT_MODEL", "gpt-4.1-mini")
CRITIC_AGENT_MODEL = os.getenv("CRITIC_AGENT_MODEL", "gpt-4.1-mini")
FOLLOWUP_AGENT_MODEL = os.getenv("FOLLOWUP_AGENT_MODEL", "gpt-4.1-mini")

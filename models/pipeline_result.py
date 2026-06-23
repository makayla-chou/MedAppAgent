from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class PipelineResult:
    final_report_path: Path
    final_report: str
    ranked_schools: pd.DataFrame
    warnings: list[str]
    run_id: str
    generated_at_utc: str
    student_name: str

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class RankingOutput:
    ranked_schools: pd.DataFrame
    data_warnings: list[str]
    ranking_basis: str
    school_views: dict[str, pd.DataFrame] = field(default_factory=dict)

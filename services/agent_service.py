from typing import Any

import pandas as pd

from agents.critic_agent import critic_agent
from agents.profile_agent import profile_agent
from agents.school_fit_agent import school_fit_agent
from models.agent_reports import AgentReports
from models.validation import ValidationIssue
from reports.report_formatter import (
    format_data_warnings,
    format_validation_issues,
    prepare_ranked_schools_for_agents,
)
from services.profile_service import profile_to_text


def run_agents(
    profile: dict[str, Any],
    ranked_schools: pd.DataFrame,
    aamc_context: str,
    profile_issues: list[ValidationIssue],
    data_warnings: list[str],
    ranking_basis: str,
) -> AgentReports:
    applicant_profile = profile_to_text(profile)
    schools_table = prepare_ranked_schools_for_agents(ranked_schools)

    data_context = (
        "AAMC STATISTICAL CONTEXT:\n"
        f"{aamc_context}\n\n"
        "RANKING BASIS:\n"
        f"{ranking_basis}\n\n"
        "APPLICANT-PROFILE VALIDATION:\n"
        f"{format_validation_issues(profile_issues)}\n\n"
        "SCHOOL-DATASET WARNINGS:\n"
        f"{format_data_warnings(data_warnings)}"
    )

    profile_context = (
        "APPLICANT PROFILE:\n"
        f"{applicant_profile}\n\n"
        f"{data_context}"
    )

    profile_report = profile_agent(profile_context)

    school_fit_report = school_fit_agent(
        applicant_profile=applicant_profile,
        schools_table=schools_table,
        data_context=data_context,
    )

    critic_report = critic_agent(
        applicant_profile=applicant_profile,
        schools_table=schools_table,
        school_fit_report=school_fit_report,
        data_context=data_context,
    )

    return AgentReports(
        profile_report=profile_report,
        school_fit_report=school_fit_report,
        critic_report=critic_report,
    )

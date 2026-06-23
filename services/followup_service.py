from typing import Any

import pandas as pd

from agents.followup_agent import followup_agent
from reports.report_formatter import prepare_ranked_schools_for_agents
from services.aamc_data_service import get_context_for_profile
from services.profile_service import profile_to_text


MAX_FOLLOWUP_QUESTION_CHARS = 1500


def _build_followup_context(
    profile: dict[str, Any],
    final_report: str,
    ranked_schools: pd.DataFrame,
) -> str:
    applicant_profile = profile_to_text(profile)
    schools_table = prepare_ranked_schools_for_agents(ranked_schools)
    aamc_context = get_context_for_profile(profile)

    return (
        "APPLICANT PROFILE:\n"
        f"{applicant_profile}\n\n"
        "AAMC AND DATA CONTEXT:\n"
        f"{aamc_context}\n\n"
        "RANKED SCHOOL DATA:\n"
        f"{schools_table}\n\n"
        "FINAL REPORT:\n"
        f"{final_report}"
    )


def answer_followup_question(
    profile: dict[str, Any],
    final_report: str,
    ranked_schools: pd.DataFrame,
    question: str,
) -> str:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Enter a follow-up question first.")

    if len(cleaned_question) > MAX_FOLLOWUP_QUESTION_CHARS:
        raise ValueError(
            "Follow-up question is too long. Please keep it under "
            f"{MAX_FOLLOWUP_QUESTION_CHARS} characters."
        )

    if not isinstance(profile, dict) or not profile:
        raise ValueError("A saved applicant profile is required.")

    if not final_report.strip():
        raise ValueError("Generate a report before asking follow-up questions.")

    if ranked_schools.empty:
        raise ValueError("Ranked school data is required for follow-up questions.")

    context = _build_followup_context(
        profile=profile,
        final_report=final_report,
        ranked_schools=ranked_schools,
    )

    return followup_agent(
        context=context,
        question=cleaned_question,
    )

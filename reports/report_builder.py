from datetime import datetime

from models.agent_reports import AgentReports
from models.validation import ValidationIssue
from reports.report_formatter import (
    format_data_warnings,
    format_validation_issues,
    ranking_summary_to_markdown,
    school_views_to_markdown,
)


def build_final_report(
    student_name: str,
    ranked_schools,
    agent_reports: AgentReports,
    aamc_context: str,
    profile_issues: list[ValidationIssue],
    data_warnings: list[str],
    ranking_basis: str,
    school_views: dict,
) -> str:
    generated_on = datetime.now().strftime("%Y-%m-%d")
    ranking_summary = ranking_summary_to_markdown(ranked_schools)
    school_view_sections = school_views_to_markdown(school_views)

    return f"""# MedAppAgent Advising Report

**Applicant:** {student_name}  
**Generated on:** {generated_on}

## 1. How This Report Was Built

{ranking_basis}

The system keeps academic comparison separate from personal preference fit. Academic scores are comparison indexes based on distance from reported school averages; they are not acceptance probabilities.

## 2. Data Quality and Validation

### Applicant-profile checks

{format_validation_issues(profile_issues)}

### School-dataset checks

{format_data_warnings(data_warnings)}

## 3. Official AAMC Aggregate Context

{aamc_context}

## 4. Applicant Profile Analysis

{agent_reports.profile_report}

## 5. Planning List

This is a combined planning order, not a universal best-school ranking. Schools are grouped by eligibility and then ordered using the factors described above.

{ranking_summary}

## 6. Independent School Views

Each view answers a different planning question and has its own `view_rank`. Ranks should not be compared across views.

{school_view_sections}

## 7. School Fit Interpretation

{agent_reports.school_fit_report}

## 8. Critic Review

{agent_reports.critic_report}

## 9. Important Limitations

- This is a planning aid, not a prediction of admission.
- Reported school averages do not define an acceptance threshold.
- Public-school residency policies, mission fit, curriculum, prerequisites, and cycle-specific deadlines must be verified from official sources.
- A missing MCAT prevents a complete academic competitiveness assessment.
"""

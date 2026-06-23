import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DEFAULT_SCHOOLS_FILE, OUTPUT_DIR
from models.agent_reports import AgentReports
from models.pipeline_result import PipelineResult
from repositories.school_repository import load_schools
from reports.report_builder import build_final_report
from reports.report_formatter import prepare_ranked_schools_for_agents
from services.aamc_data_service import get_context_for_profile
from services.profile_service import (
    get_student_name,
    load_and_validate_profile,
    validate_profile_data,
)
from services.ranking_service import rank_schools
from services.report_service import (
    create_report_run_id,
    save_report_bundle,
)


def generate_report_for_profile(
    student_data: dict[str, Any],
    schools_file: str | Path = DEFAULT_SCHOOLS_FILE,
    output_root: str | Path = OUTPUT_DIR,
    top_n: int = 25,
    use_agents: bool = True,
    report_owner_id: str | None = None,
    selected_school_names: list[str] | None = None,
) -> PipelineResult:
    profile_issues = validate_profile_data(student_data)
    student_name = get_student_name(student_data)

    report_run_id = create_report_run_id()
    generated_at_utc = datetime.now(timezone.utc).isoformat()

    schools = load_schools(schools_file)
    if selected_school_names:
        selected_names = {
            str(name).strip() for name in selected_school_names if str(name).strip()
        }
        schools = schools[schools["school_name"].isin(selected_names)].copy()
        if schools.empty:
            raise ValueError("None of the selected schools were found.")
        top_n = min(top_n, len(schools))

    ranking_output = rank_schools(
        student=student_data,
        schools=schools,
        top_n=top_n,
    )

    aamc_context = get_context_for_profile(student_data)
    if use_agents:
        from services.agent_service import run_agents

        agent_reports = run_agents(
            profile=student_data,
            ranked_schools=ranking_output.ranked_schools,
            aamc_context=aamc_context,
            profile_issues=profile_issues,
            data_warnings=ranking_output.data_warnings,
            ranking_basis=ranking_output.ranking_basis,
        )
    else:
        skipped = "Agent execution was skipped for this local test run."
        agent_reports = AgentReports(
            profile_report=skipped,
            school_fit_report=skipped,
            critic_report=skipped,
        )

    report_body = build_final_report(
        student_name=student_name,
        ranked_schools=ranking_output.ranked_schools,
        agent_reports=agent_reports,
        aamc_context=aamc_context,
        profile_issues=profile_issues,
        data_warnings=ranking_output.data_warnings,
        ranking_basis=ranking_output.ranking_basis,
        school_views=ranking_output.school_views,
    )

    final_report = (
        f"> Report run ID: `{report_run_id}`\n"
        f"> Generated at: `{generated_at_utc}`\n\n"
        f"{report_body}"
    )

    ranked_text = prepare_ranked_schools_for_agents(
        ranking_output.ranked_schools
    )
    paths = save_report_bundle(
        student_name=student_name,
        ranked_schools=ranking_output.ranked_schools,
        ranked_schools_text=ranked_text,
        agent_reports=agent_reports,
        final_report=final_report,
        report_run_id=report_run_id,
        generated_at_utc=generated_at_utc,
        profile_snapshot=student_data,
        output_root=output_root,
        report_owner_id=report_owner_id,
    )

    return PipelineResult(
        final_report_path=paths["final_report"],
        final_report=final_report,
        ranked_schools=ranking_output.ranked_schools,
        warnings=ranking_output.data_warnings,
        run_id=report_run_id,
        generated_at_utc=generated_at_utc,
        student_name=student_name,
    )


def generate_report(
    profile_file: str | Path,
    schools_file: str | Path = DEFAULT_SCHOOLS_FILE,
    output_root: str | Path = OUTPUT_DIR,
    top_n: int = 25,
    use_agents: bool = True,
    report_owner_id: str | None = None,
) -> PipelineResult:
    student_data, _ = load_and_validate_profile(profile_file)
    return generate_report_for_profile(
        student_data=student_data,
        schools_file=schools_file,
        output_root=output_root,
        top_n=top_n,
        use_agents=use_agents,
        report_owner_id=report_owner_id,
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MedAppAgent for a student JSON profile."
    )
    parser.add_argument("profile", help="Path or saved profile name.")
    parser.add_argument(
        "--schools",
        default=str(DEFAULT_SCHOOLS_FILE),
        help="Path to the medical-school CSV.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_DIR),
        help="Folder where reports will be saved.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=25,
        help="Number of ranked schools to send to the agents.",
    )
    parser.add_argument(
        "--skip-agents",
        action="store_true",
        help="Build a local test report without calling the OpenAI API.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = generate_report(
        profile_file=args.profile,
        schools_file=args.schools,
        output_root=args.output,
        top_n=args.top,
        use_agents=not args.skip_agents,
    )
    print(f"Final report: {result.final_report_path}")


if __name__ == "__main__":
    main()

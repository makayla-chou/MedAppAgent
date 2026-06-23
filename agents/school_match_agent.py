"""Optional future school-list strategy agent.

This agent is intentionally not called by the default pipeline. The profile,
school-fit, and critic agents remain the active three-agent workflow.
"""

from dotenv import load_dotenv
from openai import OpenAI

from config import SCHOOL_FIT_AGENT_MODEL

load_dotenv()


def school_strategy_agent(
    applicant_profile: str,
    ranked_schools_table: str,
    school_fit_report: str,
    data_context: str,
) -> str:
    prompt = f"""
Review the supplied school list as a whole. Focus on geographic coverage,
residency context, degree-type coverage, missing data, and overreliance on
provisional rankings. Do not invent school facts or use safety-school language.

Applicant profile:
{applicant_profile}

Data context:
{data_context}

Ranked schools:
{ranked_schools_table}

School fit report:
{school_fit_report}
"""
    client = OpenAI()
    response = client.responses.create(model=SCHOOL_FIT_AGENT_MODEL, input=prompt)
    return response.output_text

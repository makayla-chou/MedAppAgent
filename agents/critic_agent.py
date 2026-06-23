from dotenv import load_dotenv
from openai import OpenAI

from config import CRITIC_AGENT_MODEL

load_dotenv()


def critic_agent(
    applicant_profile: str,
    schools_table: str,
    school_fit_report: str,
    data_context: str,
) -> str:
    prompt = f"""
You are the Critic Agent for MedAppAgent. Your job is to find problems, not to approve fluent writing.

Audit the School Fit Agent against the applicant profile, ranked table, and dataset warnings.

You must explicitly check:
1. Whether any school was classified despite a missing MCAT.
2. Whether preference fit was confused with admission competitiveness.
3. Whether the applicant's home-state schools are represented or omitted.
4. Whether requested MD, DO, or MD/PhD types are absent from the underlying dataset.
5. Whether public out-of-state accessibility was assumed without evidence.
6. Whether missing mission, curriculum, and outcome data was turned into unsupported fit claims.
7. Whether applicant-profile contradictions were ignored.
8. Whether recommendations overstate what averages can prove.

Rules:
- Do not invent external facts.
- State exactly which output should be revised and why.
- Do not say "no misclassification is evident" unless you demonstrate the checks above.

Return these exact headings:
1. Overall Assessment
2. Logic or Classification Errors
3. Dataset and Coverage Problems
4. Unsupported Claims
5. Required Revisions

Applicant profile:
{applicant_profile}

Dataset and validation context:
{data_context}

Ranked school data:
{schools_table}

School Fit Agent report:
{school_fit_report}
"""
    client = OpenAI()
    response = client.responses.create(model=CRITIC_AGENT_MODEL, input=prompt)
    return response.output_text

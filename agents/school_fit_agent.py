from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


client = OpenAI()


def school_fit_agent(applicant_profile: str, schools_table: str) -> str:
    """
    Evaluates medical school fit using applicant profile data and a school database.
    """

    prompt = f"""
You are the School Fit Agent for MedAppAgent.

Your job is to evaluate medical school fit using the applicant profile and the school data provided.

Classify each school as one of:
- High Reach
- Reach
- Target-ish
- Safer
- Remove / Low Priority

Important rules:
- Be realistic.
- Do not guarantee acceptance.
- Do not invent facts outside the provided school table.
- If school data is marked Unknown, say that it needs verification.
- Pay attention to GPA, MCAT, residency, mission fit, and program type.
- A school should not be called "Safer" just because mission fit is good.
- Explain each classification briefly.

Return your answer as a markdown table with these columns:
School | Classification | Reasoning | Concern | Recommended Action

Applicant profile:
{applicant_profile}

School data:
{schools_table}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text
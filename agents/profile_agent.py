#Read applicant_profile.txt and create a structured summary:
# - stats
# - interests
# - strengths
# - risks
# - advising priorities


from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def profile_agent(applicant_profile: str) -> str:
    """
    Reads an applicant profile and creates a structured medical school application summary.
    """

    prompt = f"""
You are the Profile Agent for MedAppAgent.

Your job is to read a medical school applicant profile and create a structured summary.

Return your answer using these exact headings:

1. Applicant Snapshot
2. Core Strengths
3. Risk Factors
4. Advising Priorities
5. Missing Information

Rules:
- Be realistic.
- Do not guarantee acceptance.
- Do not invent information.
- If something is missing, say it is missing.
- Keep the response concise but useful.

Applicant profile:
{applicant_profile}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

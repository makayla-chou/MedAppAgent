from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


client = OpenAI()


def critic_agent(applicant_profile: str, schools_table: str, school_fit_report: str) -> str:
    """
    Reviews the School Fit Agent's recommendations for realism, unsupported claims,
    overconfidence, and missing verification.
    """

    prompt = f"""
You are the Critic Agent for MedAppAgent.

Your job is to review the School Fit Agent's recommendations.

You are not giving a new full school list.
You are checking whether the advice is realistic, cautious, and supported by the provided data.

Check for:
1. Overconfidence
2. Unsupported claims
3. Misclassification of schools
4. Ignoring MCAT/GPA risk
5. Ignoring state residency
6. Ignoring unknown or unverified school data
7. Ethical concerns, such as implying guaranteed acceptance

Rules:
- Do not invent facts outside the applicant profile and school table.
- If school data is unknown, say it needs verification.
- Be specific about what should be revised.
- Keep the tone professional and realistic.

Return your answer using these exact headings:

1. Overall Assessment
2. Major Flags
3. Classification Concerns
4. Missing Data to Verify
5. Recommended Revisions

Applicant profile:
{applicant_profile}

School data:
{schools_table}

School Fit Agent report:
{school_fit_report}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text
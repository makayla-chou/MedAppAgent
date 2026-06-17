from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def school_match_agent(applicant_profile: str, schools_table: str) -> str:
    """
    Uses the applicant profile and medical school data to recommend school matches.
    """

    prompt = f"""
You are a medical school application school-matching agent.

Your job is to use the applicant profile and the medical school dataset to recommend schools.

Important rules:
- Use the provided medical school data.
- Do not invent schools.
- Do not invent MCAT, GPA, deadline, or admissions data.
- If a school is missing important data, say that clearly.
- Group schools into Reach, Target, and Safer categories.
- Explain why each school fits or does not fit.
- Be realistic and blunt.

Applicant profile:
{applicant_profile}

Medical school data:
{schools_table}

Return your answer in this format:

# School Match Report

## Strongest Matches
List the best-fit schools and explain why.

## Reach Schools
List reach schools and explain why they are reaches.

## Target Schools
List target schools and explain why they are reasonable.

## Safer Schools
List safer schools and explain why.

## Schools to Be Careful With
List schools that may not be worth applying to and explain why.

## Final Recommendation
Give a short overall strategy.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful medical school admissions strategy assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
from dotenv import load_dotenv
from openai import OpenAI

from config import SCHOOL_FIT_AGENT_MODEL


load_dotenv()


def school_fit_agent(
    applicant_profile: str,
    schools_table: str,
    data_context: str,
) -> str:
    prompt = f"""
You are the School Fit Agent for MedAppAgent.

The supplied Python system separately calculates:
- eligibility status,
- academic comparison,
- basic preference match,
- residency context,
- data completeness.

Interpret those fields without recalculating, replacing, or renaming them.

Eligibility rules:
- Use only these exact statuses:
  - Eligible
  - Verify Eligibility
  - Not Eligible
  - Insufficient Data
- Copy eligibility_status exactly from the ranked-school data.
- Do not convert "Verify Eligibility" or "Insufficient Data" into "Eligible."
- A public out-of-state school with unverified accessibility must remain
  "Verify Eligibility."
- "Not Eligible" requires an explicit program-type mismatch or failure to
  meet a listed minimum requirement in the supplied data.
- "Insufficient Data" means eligibility-critical information is missing.
- Preference conflicts and dealbreakers affect preference scoring and
  advising, but do not independently prove formal ineligibility.

Other critical rules:
- If academic_category is "Insufficient Data", do not call the school a
  target, reach, likely acceptance, or safety.
- academic_score is a comparison index based on distance from reported
  school averages, not an admission probability.
- basic_preference_score is a weighted score using only degree type,
  state-border proximity, preferred region, setting, and explicit
  dealbreaker penalties when those data are available.
- geographic_proximity_hops is a state-border approximation, not mileage
  or travel time.
- preference_components, preference_component_weights, and
  preference_penalty explain the score. Do not recalculate or expand it.
- basic_preference_score is not a complete personal-fit score, school-fit
  score, or admission probability.
- Do not infer school mission, curriculum, service programs, acceptance
  rates, or residency policies when those fields are absent.
- Never call a medical school a safety.

Return a markdown table with:
School | Eligibility | Academic Assessment | Basic Preference Match | Residency Context | Main Evidence | Main Limitation | Recommended Action | Verification Needed

Recommended Action must be one of:
- Prioritize
- Consider
- Consider after MCAT
- Apply only if strongly interested
- Remove or verify first

Applicant profile:
{applicant_profile}

Dataset and ranking limitations:
{data_context}

Ranked school data:
{schools_table}
"""
    client = OpenAI()
    response = client.responses.create(
        model=SCHOOL_FIT_AGENT_MODEL,
        input=prompt,
    )
    return response.output_text

from datetime import datetime


def build_final_report(
    applicant_profile: str,
    profile_report: str,
    school_fit_report: str,
    critic_report: str,
    match_report: str
) -> str:
    current_date = datetime.now().strftime("%Y-%m-%d")

    final_report = f"""
# MedAppAgent Final Advising Report

**Generated on:** {current_date}

---

## 1. Project Purpose

MedAppAgent is a multi-agent AI system designed to help medical school applicants organize their application profile, evaluate school fit, and receive realistic advising feedback.

This report was generated using three agents:

1. **Profile Agent** - summarizes the applicant's strengths, risks, and advising priorities.
2. **School Fit Agent** - evaluates school fit using applicant data and a school database.
3. **Critic Agent** - reviews school fit recommendations for overconfidence, unsupported claims, and missing verification.

---

## 2. Applicant Profile Used

{applicant_profile}

---

## 3. Profile Agent Report

{profile_report}

---

## 4. School Fit Agent Report

{school_fit_report}

---

## 5. Critic Agent Report

{critic_report}

---

---

## 6. Match Agent Report

{match_report}

---

## 7. System Notes

This report is intended as a structured advising aid, not a replacement for official medical school admissions data or professional advising.

School-specific data should be verified using official sources such as AAMC MSAR and official medical school admissions pages.

The system should not guarantee acceptance or make unsupported claims about admissions outcomes.

---

## 8. Next Development Steps

Future versions of MedAppAgent could add:

- An Activity Review Agent
- A Secondary Essay Review Agent
- A Deadline and Timeline Agent
- Verified source links for each school
- A Streamlit web interface
- Export to PDF
"""

    return final_report.strip()
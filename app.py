import json
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import ClientOptions, create_client

from config import DEFAULT_SCHOOLS_FILE
from main import generate_report_for_profile
from repositories.school_repository import load_schools
from repositories.supabase_profile_repository import (
    load_profile_from_supabase,
    save_profile_to_supabase,
)
from repositories.supabase_report_repository import (
    list_reports_for_user,
    load_report_from_supabase,
    save_report_to_supabase,
)
from services.followup_service import answer_followup_question
from validation.profile_validator import validate_student_profile


load_dotenv()


def load_streamlit_secrets_into_environment() -> None:
    for key in (
        "SUPABASE_URL",
        "SUPABASE_PUBLISHABLE_KEY",
        "OPENAI_API_KEY",
        "PROFILE_AGENT_MODEL",
        "SCHOOL_FIT_AGENT_MODEL",
        "CRITIC_AGENT_MODEL",
        "FOLLOWUP_AGENT_MODEL",
    ):
        if os.getenv(key):
            continue
        try:
            value = st.secrets.get(key)
        except Exception:
            value = None
        if value:
            os.environ[key] = str(value)


load_streamlit_secrets_into_environment()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

MAJOR_GROUPS = [
    "Biological Sciences",
    "Physical Sciences",
    "Social Sciences",
    "Humanities",
    "Math and Statistics",
    "Specialized Health Sciences",
    "Other",
]

ADVISOR_GOALS = [
    "Build my first school list",
    "Review my existing school list",
    "Identify risky choices",
    "Find more in-state or regional schools",
    "Explain my competitiveness",
    "Improve my application narrative",
]

HARD_DEALBREAKERS = [
    "Strong in-state preference",
    "Rural location",
    "Large city",
]

MAJOR_CONCERNS = [
    "Very high tuition",
    "Religious affiliation",
    "Mandatory research requirement",
    "Far from family",
]


@st.cache_data
def load_school_catalog() -> pd.DataFrame:
    schools = load_schools(DEFAULT_SCHOOLS_FILE)
    columns = [
        column
        for column in (
            "school_name",
            "school_state_code",
            "school_degree_type",
            "school_region",
            "school_setting",
            "school_gpa",
            "school_mcat",
            "is_public_bool",
        )
        if column in schools.columns
    ]
    return schools[columns].drop_duplicates(subset=["school_name"]).copy()


def nested_get(data: dict, *keys, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def option_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


def create_authenticated_client(access_token: str):
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(
            headers={"Authorization": f"Bearer {access_token}"}
        ),
    )


def show_auth_page() -> None:
    st.title("MedAppAgent")
    login_tab, signup_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", use_container_width=True)

        if submitted:
            try:
                auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                response = auth_client.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password,
                })
                if not response.user or not response.session:
                    st.error("Login failed.")
                    return

                st.session_state["user_id"] = response.user.id
                st.session_state["user_email"] = response.user.email
                st.session_state["access_token"] = response.session.access_token
                st.session_state["refresh_token"] = response.session.refresh_token
                st.rerun()
            except Exception as error:
                st.error(f"Login failed: {error}")

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Create account", use_container_width=True)

        if submitted:
            try:
                auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                response = auth_client.auth.sign_up({
                    "email": email.strip(),
                    "password": password,
                })
                if response.session and response.user:
                    st.session_state["user_id"] = response.user.id
                    st.session_state["user_email"] = response.user.email
                    st.session_state["access_token"] = response.session.access_token
                    st.session_state["refresh_token"] = response.session.refresh_token
                    st.rerun()
                else:
                    st.success("Account created. Check your email if confirmation is enabled.")
            except Exception as error:
                st.error(f"Account creation failed: {error}")


def build_profile_form(existing: dict) -> dict | None:
    basic = existing.get("basic_information", {})
    academics = existing.get("academics", {})
    hours = existing.get("experience_hours", {})
    descriptions = existing.get("experience_descriptions", {})
    achievements = existing.get("achievements", {})
    goals = existing.get("goals", {})
    preferences = existing.get("school_preferences", {})
    sections = academics.get("mcat_sections", {})
    major_aliases = {
        "biology": "Biological Sciences",
        "biological sciences": "Biological Sciences",
        "neuroscience": "Biological Sciences",
        "public health": "Specialized Health Sciences",
    }
    existing_major_group = basic.get("major_group")
    if existing_major_group not in MAJOR_GROUPS:
        existing_major_group = major_aliases.get(
            str(basic.get("major", "")).strip().casefold(),
            "Other",
        )

    if "profile_mcat_taken" not in st.session_state:
        st.session_state["profile_mcat_taken"] = bool(
            academics.get("mcat_taken", False)
        )

    st.subheader("MCAT Status")
    mcat_taken = st.checkbox(
        "I have taken the MCAT and want to enter my scores",
        key="profile_mcat_taken",
    )
    if not mcat_taken:
        st.caption(
            "MCAT score fields will appear after this is checked. Reports can still be generated without an MCAT."
        )

    with st.form("student_profile_form"):
        st.header("1. Basics")
        name = st.text_input(
            "Name",
            value=basic.get("name", ""),
        )
        state_residency = st.selectbox(
            "State of legal residency",
            STATES,
            index=option_index(STATES, basic.get("state_residency"), 0),
        )
        citizenship_options = [
            "U.S. citizen", "Permanent resident", "DACA",
            "International student", "Other",
        ]
        citizenship_status = st.selectbox(
            "Citizenship status",
            citizenship_options,
            index=option_index(
                citizenship_options,
                basic.get("citizenship_status", "U.S. citizen"),
            ),
        )
        undergraduate_school = st.text_input(
            "Undergraduate institution",
            value=basic.get("undergraduate_school", ""),
        )
        major_group = st.selectbox(
            "AAMC major group",
            MAJOR_GROUPS,
            index=option_index(MAJOR_GROUPS, existing_major_group),
        )
        major = st.text_input(
            "Specific major",
            value=basic.get("major", ""),
        )
        application_year = st.number_input(
            "Application cycle",
            min_value=2026,
            max_value=2035,
            value=int(basic.get("application_year", 2027)),
            step=1,
        )

        st.header("2. Academic Profile")
        overall_gpa = st.number_input(
            "Cumulative GPA",
            min_value=0.0,
            max_value=4.0,
            value=float(academics.get("overall_gpa") or 3.5),
            step=0.01,
        )
        science_gpa = st.number_input(
            "Science GPA",
            min_value=0.0,
            max_value=4.0,
            value=float(academics.get("science_gpa") or 3.5),
            step=0.01,
        )

        if mcat_taken:
            mcat_total = st.number_input(
                "MCAT total score",
                min_value=472,
                max_value=528,
                value=int(academics.get("mcat_total") or 500),
                step=1,
            )
            col1, col2 = st.columns(2)
            with col1:
                chem_physics = st.number_input(
                    "Chem/Physics", 118, 132,
                    value=int(sections.get("chem_physics") or 125),
                )
                bio_biochem = st.number_input(
                    "Bio/Biochem", 118, 132,
                    value=int(sections.get("bio_biochem") or 125),
                )
            with col2:
                cars = st.number_input(
                    "CARS", 118, 132,
                    value=int(sections.get("cars") or 125),
                )
                psych_social = st.number_input(
                    "Psych/Soc", 118, 132,
                    value=int(sections.get("psych_social") or 125),
                )
        else:
            mcat_total = None
            chem_physics = cars = bio_biochem = psych_social = None

        academic_context = st.text_area(
            "Optional academic context",
            value=academics.get("academic_context", ""),
            max_chars=1500,
        )

        st.header("3. Experience Hours")
        col1, col2 = st.columns(2)
        with col1:
            clinical_hours = st.number_input(
                "Clinical hours", min_value=0,
                value=int(hours.get("clinical", 0)), step=10,
            )
            research_hours = st.number_input(
                "Research hours", min_value=0,
                value=int(hours.get("research", 0)), step=10,
            )
            leadership_hours = st.number_input(
                "Leadership hours", min_value=0,
                value=int(hours.get("leadership", 0)), step=10,
            )
        with col2:
            shadowing_hours = st.number_input(
                "Shadowing hours", min_value=0,
                value=int(hours.get("shadowing", 0)), step=10,
            )
            nonclinical_hours = st.number_input(
                "Nonclinical volunteering hours", min_value=0,
                value=int(hours.get("nonclinical_volunteering", 0)), step=10,
            )
            teaching_hours = st.number_input(
                "Teaching or tutoring hours", min_value=0,
                value=int(hours.get("teaching", 0)), step=10,
            )

        st.header("4. Important Experiences")
        clinical_description = st.text_area(
            "Most important clinical experience",
            value=descriptions.get("clinical", ""),
            max_chars=2000,
        )
        research_description = st.text_area(
            "Research experience",
            value=descriptions.get("research", ""),
            max_chars=2000,
        )
        service_description = st.text_area(
            "Most important service experience",
            value=descriptions.get("service", ""),
            max_chars=2000,
        )

        st.header("5. Achievements and Goals")
        research_options = [
            "No formal research output", "Internal presentation",
            "Poster presentation", "Conference presentation", "Abstract",
            "Publication submitted", "Publication accepted", "Publication published",
        ]
        research_outputs = st.multiselect(
            "Research outcomes",
            research_options,
            default=[
                value for value in achievements.get("research_outputs", [])
                if value in research_options
            ],
        )
        awards = st.text_area(
            "Awards and honors, one per line",
            value="\n".join(achievements.get("awards", [])),
            max_chars=1500,
        )
        career_options = [
            "Primary care", "Pediatrics", "Psychiatry", "Surgery",
            "Emergency medicine", "Public health", "Health equity",
            "Academic medicine", "Rural medicine", "Underserved communities",
            "Medical research", "Undecided",
        ]
        career_interests = st.multiselect(
            "Medical interests",
            career_options,
            default=[
                value for value in goals.get("career_interests", [])
                if value in career_options
            ],
        )
        populations_of_interest = st.text_area(
            "Populations or health issues of interest",
            value=goals.get("populations_of_interest", ""),
            max_chars=1000,
        )
        advising_goals = st.multiselect(
            "What do you want the advisor to help with?",
            ADVISOR_GOALS,
            default=[
                value for value in goals.get("advising_goals", [])
                if value in ADVISOR_GOALS
            ],
        )

        st.header("6. School Preferences")
        school_types = st.multiselect(
            "Programs you are willing to consider",
            ["MD", "DO", "MD/PhD"],
            default=preferences.get("school_types", ["MD"]),
        )
        region_options = [
            "Northeast", "Mid-Atlantic", "Southeast", "Midwest",
            "Southwest", "West Coast", "No geographic preference",
        ]
        preferred_regions = st.multiselect(
            "Preferred regions",
            region_options,
            default=[
                value for value in preferences.get("preferred_regions", [])
                if value in region_options
            ],
        )
        setting_options = ["No preference", "Urban", "Suburban", "Rural", "Town"]
        setting_preference = st.selectbox(
            "Preferred setting",
            setting_options,
            index=option_index(
                setting_options,
                preferences.get("setting_preference", "No preference"),
            ),
        )
        dealbreakers = st.multiselect(
            "Hard dealbreakers that should exclude or strongly deprioritize schools",
            HARD_DEALBREAKERS,
            default=[
                value for value in preferences.get("dealbreakers", [])
                if value in HARD_DEALBREAKERS
            ],
        )
        major_concerns = st.multiselect(
            "Concerns to flag for review, but not automatically exclude",
            MAJOR_CONCERNS,
            default=[
                value for value in preferences.get("major_concerns", [])
                if value in MAJOR_CONCERNS
            ]
            + [
                value for value in preferences.get("dealbreakers", [])
                if value in MAJOR_CONCERNS
            ],
        )
        additional_context = st.text_area(
            "Anything else the advisor should consider?",
            value=existing.get("additional_context", ""),
            max_chars=1500,
        )

        submitted = st.form_submit_button(
            "Save Student Profile",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    return {
        "basic_information": {
            "name": name.strip(),
            "state_residency": state_residency,
            "citizenship_status": citizenship_status,
            "undergraduate_school": undergraduate_school.strip(),
            "major_group": major_group,
            "major": major.strip(),
            "application_year": int(application_year),
        },
        "academics": {
            "overall_gpa": float(overall_gpa),
            "science_gpa": float(science_gpa),
            "mcat_taken": bool(mcat_taken),
            "mcat_total": int(mcat_total) if mcat_total is not None else None,
            "mcat_sections": {
                "chem_physics": int(chem_physics) if chem_physics is not None else None,
                "cars": int(cars) if cars is not None else None,
                "bio_biochem": int(bio_biochem) if bio_biochem is not None else None,
                "psych_social": int(psych_social) if psych_social is not None else None,
            },
            "academic_context": academic_context.strip(),
        },
        "experience_hours": {
            "clinical": int(clinical_hours),
            "shadowing": int(shadowing_hours),
            "research": int(research_hours),
            "nonclinical_volunteering": int(nonclinical_hours),
            "leadership": int(leadership_hours),
            "teaching": int(teaching_hours),
        },
        "experience_descriptions": {
            "clinical": clinical_description.strip(),
            "research": research_description.strip(),
            "service": service_description.strip(),
        },
        "achievements": {
            "research_outputs": research_outputs,
            "awards": [line.strip() for line in awards.splitlines() if line.strip()],
        },
        "goals": {
            "career_interests": career_interests,
            "populations_of_interest": populations_of_interest.strip(),
            "advising_goals": advising_goals,
        },
        "school_preferences": {
            "school_types": school_types,
            "preferred_regions": preferred_regions,
            "setting_preference": setting_preference,
            "dealbreakers": dealbreakers,
            "major_concerns": major_concerns,
        },
        "additional_context": additional_context.strip(),
    }


def show_followup_panel() -> None:
    report_state = st.session_state.get("latest_report")
    if not report_state:
        return

    if st.session_state.pop("clear_followup_question", False):
        st.session_state["followup_question"] = ""

    st.header("Ask a Follow-up Question")
    st.caption(
        "Ask about the generated report, ranked schools, profile, or data limitations."
    )

    question = st.text_area(
        "Follow-up question",
        key="followup_question",
        max_chars=1500,
        placeholder="Example: Which five schools should I verify before applying?",
    )

    if st.button("Ask Follow-up", type="secondary", use_container_width=True):
        try:
            with st.spinner("Answering follow-up question..."):
                answer = answer_followup_question(
                    profile=report_state["profile"],
                    final_report=report_state["final_report"],
                    ranked_schools=report_state["ranked_schools"],
                    question=question,
                )
        except Exception as error:
            st.error(f"Could not answer follow-up question: {error}")
        else:
            st.session_state.setdefault("followup_history", []).append(
                {
                    "question": question.strip(),
                    "answer": answer,
                }
            )
            st.session_state["clear_followup_question"] = True
            st.rerun()

    for item in reversed(st.session_state.get("followup_history", [])):
        with st.expander(item["question"], expanded=True):
            st.markdown(item["answer"])


def _set_latest_report_from_saved_row(row: dict) -> None:
    ranked_records = row.get("ranked_schools") or []
    ranked_schools = pd.DataFrame(ranked_records)

    st.session_state["latest_report"] = {
        "profile": row.get("profile_snapshot") or {},
        "final_report": row.get("final_report", ""),
        "ranked_schools": ranked_schools,
        "run_id": row.get("run_id", ""),
    }
    st.session_state["followup_history"] = []


def _numeric_column(dataframe: pd.DataFrame, column: str) -> pd.Series:
    if column not in dataframe.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(dataframe[column], errors="coerce")


def _format_metric_value(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.1f}"


def _to_float(value) -> float | None:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(number):
        return None
    return float(number)


def _profile_academic_values(profile: dict) -> dict[str, float | None]:
    academics = profile.get("academics", {}) if isinstance(profile, dict) else {}
    return {
        "overall_gpa": _to_float(academics.get("overall_gpa")),
        "science_gpa": _to_float(academics.get("science_gpa")),
        "mcat_total": _to_float(academics.get("mcat_total")),
    }


def _comparison_dataframe(
    profile: dict,
    ranked_schools: pd.DataFrame,
) -> pd.DataFrame:
    applicant = _profile_academic_values(profile)
    columns = [
        column
        for column in (
            "rank",
            "school_name",
            "school_state_code",
            "school_gpa",
            "school_mcat",
            "gpa_difference",
            "mcat_difference",
            "academic_category",
            "academic_score",
            "basic_preference_score",
            "eligibility_status",
        )
        if column in ranked_schools.columns
    ]
    if not columns:
        return pd.DataFrame()

    comparison = ranked_schools[columns].copy()
    for column in (
        "school_gpa",
        "school_mcat",
        "gpa_difference",
        "mcat_difference",
        "academic_score",
        "basic_preference_score",
    ):
        if column in comparison.columns:
            comparison[column] = pd.to_numeric(
                comparison[column],
                errors="coerce",
            )

    if "gpa_difference" not in comparison.columns:
        comparison["gpa_difference"] = pd.NA
    if applicant["overall_gpa"] is not None and "school_gpa" in comparison.columns:
        comparison["gpa_difference"] = comparison["gpa_difference"].fillna(
            round(applicant["overall_gpa"], 2) - comparison["school_gpa"]
        )

    if "mcat_difference" not in comparison.columns:
        comparison["mcat_difference"] = pd.NA
    if applicant["mcat_total"] is not None and "school_mcat" in comparison.columns:
        comparison["mcat_difference"] = comparison["mcat_difference"].fillna(
            round(applicant["mcat_total"], 1) - comparison["school_mcat"]
        )

    return comparison


def _comparison_summary_text(
    comparison: pd.DataFrame,
    column: str,
    unit: str,
) -> str:
    if column not in comparison.columns:
        return "Not enough data"

    values = pd.to_numeric(comparison[column], errors="coerce").dropna()
    if values.empty:
        return "Not enough data"

    above = int((values >= 0).sum())
    total = len(values)
    average = values.mean()
    return f"{above}/{total} schools, avg {average:+.1f} {unit}"


def show_applicant_comparison_dashboard(
    profile: dict,
    ranked_schools: pd.DataFrame,
) -> None:
    applicant = _profile_academic_values(profile)
    comparison = _comparison_dataframe(profile, ranked_schools)
    if comparison.empty:
        return

    st.subheader("Applicant Comparison Dashboard")

    school_gpa = _numeric_column(comparison, "school_gpa")
    school_mcat = _numeric_column(comparison, "school_mcat")

    metric_columns = st.columns(5)
    metric_columns[0].metric(
        "Applicant GPA",
        _format_metric_value(applicant["overall_gpa"]),
    )
    metric_columns[1].metric(
        "Science GPA",
        _format_metric_value(applicant["science_gpa"]),
    )
    metric_columns[2].metric(
        "MCAT",
        "N/A"
        if applicant["mcat_total"] is None
        else f"{applicant['mcat_total']:.0f}",
    )
    metric_columns[3].metric(
        "Median school GPA",
        _format_metric_value(school_gpa.median()),
    )
    metric_columns[4].metric(
        "Median school MCAT",
        "N/A" if school_mcat.dropna().empty else f"{school_mcat.median():.0f}",
    )

    st.caption(
        "GPA and MCAT comparisons use each school's reported average, not an admission probability."
    )

    academic_tab, map_tab, closest_tab = st.tabs(
        ["Academic Compare", "Fit Map", "Closest Schools"]
    )

    with academic_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "GPA at or above school average",
                _comparison_summary_text(comparison, "gpa_difference", "GPA"),
            )
            if (
                applicant["overall_gpa"] is not None
                and "school_gpa" in comparison.columns
            ):
                gpa_chart = comparison[
                    ["school_name", "school_gpa"]
                ].dropna().head(12)
                if not gpa_chart.empty:
                    gpa_chart = gpa_chart.rename(
                        columns={
                            "school_name": "school",
                            "school_gpa": "School average GPA",
                        }
                    )
                    gpa_chart["Applicant GPA"] = applicant["overall_gpa"]
                    st.bar_chart(
                        gpa_chart.set_index("school"),
                        horizontal=True,
                        x_label="GPA",
                        y_label="School",
                    )
        with col2:
            st.metric(
                "MCAT at or above school average",
                _comparison_summary_text(comparison, "mcat_difference", "MCAT"),
            )
            if (
                applicant["mcat_total"] is not None
                and "school_mcat" in comparison.columns
            ):
                mcat_chart = comparison[
                    ["school_name", "school_mcat"]
                ].dropna().head(12)
                if not mcat_chart.empty:
                    mcat_chart = mcat_chart.rename(
                        columns={
                            "school_name": "school",
                            "school_mcat": "School average MCAT",
                        }
                    )
                    mcat_chart["Applicant MCAT"] = applicant["mcat_total"]
                    st.bar_chart(
                        mcat_chart.set_index("school"),
                        horizontal=True,
                        x_label="MCAT",
                        y_label="School",
                    )

    with map_tab:
        map_columns = {
            "school_name",
            "academic_score",
            "basic_preference_score",
        }
        if map_columns.issubset(comparison.columns):
            fit_map = comparison[
                [
                    "school_name",
                    "academic_score",
                    "basic_preference_score",
                ]
            ].copy()
            fit_map["academic_score"] = pd.to_numeric(
                fit_map["academic_score"],
                errors="coerce",
            )
            fit_map["basic_preference_score"] = pd.to_numeric(
                fit_map["basic_preference_score"],
                errors="coerce",
            )
            fit_map = fit_map.dropna()
            if not fit_map.empty:
                st.scatter_chart(
                    fit_map,
                    x="academic_score",
                    y="basic_preference_score",
                    x_label="Academic comparison score",
                    y_label="Basic preference score",
                )

        if "academic_category" in comparison.columns:
            category_summary = (
                comparison["academic_category"]
                .fillna("Unknown")
                .value_counts()
            )
            if not category_summary.empty:
                st.caption("Academic category mix")
                st.bar_chart(category_summary)

    with closest_tab:
        closeness = comparison.copy()
        if "gpa_difference" in closeness.columns:
            closeness["gpa_gap"] = pd.to_numeric(
                closeness["gpa_difference"],
                errors="coerce",
            ).abs()
        else:
            closeness["gpa_gap"] = pd.NA

        if "mcat_difference" in closeness.columns:
            closeness["mcat_gap"] = (
                pd.to_numeric(
                    closeness["mcat_difference"],
                    errors="coerce",
                ).abs()
                / 10
            )
        else:
            closeness["mcat_gap"] = pd.NA

        closeness["academic_distance"] = closeness[
            ["gpa_gap", "mcat_gap"]
        ].mean(axis=1, skipna=True)
        closest = closeness.dropna(subset=["academic_distance"]).sort_values(
            "academic_distance"
        )

        visible_columns = [
            column
            for column in (
                "rank",
                "school_name",
                "school_state_code",
                "school_gpa",
                "gpa_difference",
                "school_mcat",
                "mcat_difference",
                "academic_category",
                "basic_preference_score",
                "eligibility_status",
            )
            if column in closest.columns
        ]
        if visible_columns:
            st.dataframe(
                closest[visible_columns].head(15),
                use_container_width=True,
                hide_index=True,
            )


def _show_score_bar_chart(
    ranked_schools: pd.DataFrame,
    score_column: str,
    label: str,
) -> None:
    required_columns = {"rank", "school_name", score_column}
    if not required_columns.issubset(ranked_schools.columns):
        return

    chart_data = ranked_schools[
        ["rank", "school_name", score_column]
    ].copy()
    chart_data[score_column] = pd.to_numeric(
        chart_data[score_column],
        errors="coerce",
    )
    chart_data = chart_data.dropna(subset=[score_column]).head(15)
    if chart_data.empty:
        return

    chart_data["school"] = (
        chart_data["rank"].astype(str) + ". " + chart_data["school_name"]
    )
    st.bar_chart(
        chart_data.set_index("school")[[score_column]],
        horizontal=True,
        x_label=label,
        y_label="School",
    )


def show_report_visuals(profile: dict, ranked_schools: pd.DataFrame) -> None:
    if ranked_schools.empty:
        return

    if profile:
        show_applicant_comparison_dashboard(profile, ranked_schools)

    st.subheader("Report Visuals")

    eligible_count = (
        ranked_schools["eligibility_status"].eq("Eligible").sum()
        if "eligibility_status" in ranked_schools.columns
        else None
    )
    academic_scores = _numeric_column(ranked_schools, "academic_score")
    preference_scores = _numeric_column(
        ranked_schools,
        "basic_preference_score",
    )
    completeness_scores = _numeric_column(
        ranked_schools,
        "data_completeness_score",
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric("Schools shown", len(ranked_schools))
    metric_columns[1].metric(
        "Eligible",
        "N/A" if eligible_count is None else int(eligible_count),
    )
    metric_columns[2].metric(
        "Avg academic score",
        _format_metric_value(academic_scores.mean()),
    )
    metric_columns[3].metric(
        "Avg preference score",
        _format_metric_value(preference_scores.mean()),
    )

    score_tab, category_tab, table_tab = st.tabs(
        ["Scores", "Breakdowns", "Ranked Table"]
    )

    with score_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Academic comparison")
            _show_score_bar_chart(
                ranked_schools,
                "academic_score",
                "Academic score",
            )
        with col2:
            st.caption("Basic preference fit")
            _show_score_bar_chart(
                ranked_schools,
                "basic_preference_score",
                "Preference score",
            )

        scatter_columns = {
            "school_name",
            "academic_score",
            "basic_preference_score",
        }
        if scatter_columns.issubset(ranked_schools.columns):
            scatter_data = ranked_schools[
                ["school_name", "academic_score", "basic_preference_score"]
            ].copy()
            scatter_data["academic_score"] = pd.to_numeric(
                scatter_data["academic_score"],
                errors="coerce",
            )
            scatter_data["basic_preference_score"] = pd.to_numeric(
                scatter_data["basic_preference_score"],
                errors="coerce",
            )
            scatter_data = scatter_data.dropna()
            if not scatter_data.empty:
                st.caption("Academic score vs. preference score")
                st.scatter_chart(
                    scatter_data,
                    x="academic_score",
                    y="basic_preference_score",
                    x_label="Academic score",
                    y_label="Preference score",
                )

    with category_tab:
        col1, col2 = st.columns(2)
        with col1:
            if "eligibility_status" in ranked_schools.columns:
                st.caption("Eligibility status")
                st.bar_chart(
                    ranked_schools["eligibility_status"]
                    .fillna("Unknown")
                    .value_counts()
                )
        with col2:
            if "academic_category" in ranked_schools.columns:
                st.caption("Academic category")
                st.bar_chart(
                    ranked_schools["academic_category"]
                    .fillna("Unknown")
                    .value_counts()
                )

        if not completeness_scores.dropna().empty:
            st.caption("Data completeness")
            st.bar_chart(
                pd.DataFrame(
                    {
                        "school": ranked_schools.get(
                            "school_name",
                            pd.Series(dtype="object"),
                        ),
                        "data_completeness_score": completeness_scores,
                    }
                )
                .dropna()
                .head(15)
                .set_index("school")
            )

    with table_tab:
        display_columns = [
            "rank",
            "school_name",
            "school_state_code",
            "school_degree_type",
            "eligibility_status",
            "academic_category",
            "academic_score",
            "basic_preference_category",
            "basic_preference_score",
            "residency_context",
            "data_completeness_score",
        ]
        visible_columns = [
            column for column in display_columns if column in ranked_schools.columns
        ]
        if visible_columns:
            st.dataframe(
                ranked_schools[visible_columns],
                use_container_width=True,
                hide_index=True,
            )


def show_school_list_summary(selected_schools: pd.DataFrame) -> None:
    if selected_schools.empty:
        return

    metric_columns = st.columns(4)
    metric_columns[0].metric("Schools in list", len(selected_schools))
    if "school_state_code" in selected_schools.columns:
        metric_columns[1].metric(
            "States",
            selected_schools["school_state_code"].dropna().nunique(),
        )
    if "school_gpa" in selected_schools.columns:
        metric_columns[2].metric(
            "Median GPA",
            _format_metric_value(_numeric_column(selected_schools, "school_gpa").median()),
        )
    if "school_mcat" in selected_schools.columns:
        mcat_values = _numeric_column(selected_schools, "school_mcat").dropna()
        metric_columns[3].metric(
            "Median MCAT",
            "N/A" if mcat_values.empty else f"{mcat_values.median():.0f}",
        )

    chart_columns = st.columns(2)
    with chart_columns[0]:
        if "school_state_code" in selected_schools.columns:
            st.caption("Schools by state")
            st.bar_chart(
                selected_schools["school_state_code"]
                .fillna("Unknown")
                .value_counts()
            )
    with chart_columns[1]:
        if "school_degree_type" in selected_schools.columns:
            st.caption("Programs by degree type")
            st.bar_chart(
                selected_schools["school_degree_type"]
                .fillna("Unknown")
                .value_counts()
            )

    display_columns = [
        column
        for column in (
            "school_name",
            "school_state_code",
            "school_degree_type",
            "school_region",
            "school_setting",
            "school_gpa",
            "school_mcat",
        )
        if column in selected_schools.columns
    ]
    st.dataframe(
        selected_schools[display_columns],
        use_container_width=True,
        hide_index=True,
    )


def generate_and_store_report(
    *,
    profile: dict,
    top_n: int,
    supabase_client,
    user_id: str,
    selected_school_names: list[str] | None = None,
) -> None:
    try:
        with st.spinner("Generating rankings and agent reports..."):
            result = generate_report_for_profile(
                profile,
                top_n=top_n,
                report_owner_id=user_id,
                selected_school_names=selected_school_names,
            )
    except Exception as error:
        st.exception(error)
        return

    st.session_state["latest_report"] = {
        "profile": profile,
        "final_report": result.final_report,
        "ranked_schools": result.ranked_schools,
        "run_id": result.run_id,
    }
    st.session_state["followup_history"] = []
    cloud_saved = False

    try:
        save_report_to_supabase(
            supabase_client=supabase_client,
            user_id=user_id,
            run_id=result.run_id,
            generated_at_utc=result.generated_at_utc,
            student_name=result.student_name,
            final_report=result.final_report,
            ranked_schools=result.ranked_schools,
            warnings=result.warnings,
            profile_snapshot=profile,
        )
        cloud_saved = True
    except Exception as error:
        st.error(
            "The report was generated locally, but it could not be "
            f"saved to Supabase: {error}"
        )

    if cloud_saved:
        st.success(
            "Report saved locally and to Supabase. "
            f"Run ID: {result.run_id}"
        )
    else:
        st.warning(f"Local report path: {result.final_report_path}")


def show_school_list_panel(
    *,
    profile: dict,
    top_n: int,
    supabase_client,
    user_id: str,
) -> None:
    st.header("School List")

    catalog = load_school_catalog()
    if catalog.empty:
        st.warning("No school catalog data is available.")
        return

    if "school_list_selection" not in st.session_state:
        st.session_state["school_list_selection"] = []

    school_names = catalog["school_name"].dropna().sort_values().tolist()
    selected_names = st.multiselect(
        "My schools",
        school_names,
        default=[
            name
            for name in st.session_state["school_list_selection"]
            if name in school_names
        ],
        placeholder="Search for schools to add",
    )
    st.session_state["school_list_selection"] = selected_names

    selected_schools = catalog[
        catalog["school_name"].isin(selected_names)
    ].copy()
    show_school_list_summary(selected_schools)

    button_columns = st.columns(2)
    with button_columns[0]:
        generate_disabled = not selected_names
        if st.button(
            "Generate Report from School List",
            type="primary",
            use_container_width=True,
            disabled=generate_disabled,
        ):
            generate_and_store_report(
                profile=profile,
                top_n=max(1, len(selected_names)),
                supabase_client=supabase_client,
                user_id=user_id,
                selected_school_names=selected_names,
            )
    with button_columns[1]:
        if st.button(
            "Clear School List",
            use_container_width=True,
            disabled=not selected_names,
        ):
            st.session_state["school_list_selection"] = []
            st.rerun()


def show_saved_reports_panel(supabase_client, user_id: str) -> None:
    st.header("Saved Reports")

    try:
        reports = list_reports_for_user(
            supabase_client=supabase_client,
            user_id=user_id,
        )
    except Exception as error:
        st.warning(f"Could not load saved reports: {error}")
        return

    if not reports:
        st.caption("No saved reports yet.")
        return

    labels = []
    reports_by_label = {}
    for report in reports:
        generated_at = str(report.get("generated_at_utc", "Unknown date"))
        student_name = str(report.get("student_name", "student"))
        run_id = str(report.get("run_id", ""))
        label = f"{generated_at} | {student_name} | {run_id}"
        labels.append(label)
        reports_by_label[label] = report

    selected_label = st.selectbox(
        "Open a previous report",
        labels,
        key="saved_report_picker",
    )

    if st.button("Load Saved Report", use_container_width=True):
        selected_report = reports_by_label[selected_label]
        try:
            row = load_report_from_supabase(
                supabase_client=supabase_client,
                user_id=user_id,
                run_id=selected_report["run_id"],
            )
        except Exception as error:
            st.error(f"Could not load the saved report: {error}")
            return

        if not row:
            st.error("Saved report was not found.")
            return

        _set_latest_report_from_saved_row(row)
        st.success("Saved report loaded.")


def show_current_report_panel() -> None:
    report_state = st.session_state.get("latest_report")
    if not report_state:
        return

    run_id = report_state.get("run_id", "report")
    final_report = report_state.get("final_report", "")
    profile = report_state.get("profile", {})
    ranked_schools = report_state.get("ranked_schools", pd.DataFrame())

    st.header("Current Report")
    if run_id:
        st.caption(f"Run ID: {run_id}")

    show_followup_panel()
    if isinstance(ranked_schools, pd.DataFrame):
        show_report_visuals(profile, ranked_schools)

    st.markdown(final_report)
    st.download_button(
        "Download final report",
        data=final_report,
        file_name=f"final_report_{run_id}.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(
        page_title="Medical School Application Advisor",
        page_icon="🩺",
        layout="wide",
    )

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials are missing. Copy .env.example to .env and fill it in.")
        st.stop()

    if "user_id" not in st.session_state:
        show_auth_page()
        st.stop()

    with st.sidebar:
        st.write(f"Signed in as: {st.session_state.get('user_email', '')}")
        top_n = st.slider("Schools to analyze", min_value=5, max_value=50, value=25)
        if st.button("Log out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("Medical School Application Advisor")
    st.caption("Save your profile, then generate an advising report grounded in the local school dataset.")

    supabase_client = create_authenticated_client(st.session_state["access_token"])

    if "current_profile" not in st.session_state:
        try:
            row = load_profile_from_supabase(
                supabase_client,
                st.session_state["user_id"],
            )
            st.session_state["current_profile"] = (
                row.get("profile_data", {}) if row else {}
            )
        except Exception as error:
            st.warning(f"Could not load the saved profile: {error}")
            st.session_state["current_profile"] = {}

    profile_tab, school_list_tab, reports_tab = st.tabs(
        ["Profile", "School List", "Reports"]
    )

    with profile_tab:
        saved_profile = build_profile_form(st.session_state["current_profile"])

        if saved_profile is not None:
            issues = validate_student_profile(saved_profile)
            errors = [issue for issue in issues if issue.severity == "error"]
            if errors:
                for issue in errors:
                    st.error(f"{issue.field}: {issue.message}")
            else:
                try:
                    save_profile_to_supabase(
                        supabase_client,
                        st.session_state["user_id"],
                        saved_profile,
                    )
                    st.session_state["current_profile"] = saved_profile
                    st.success("Profile saved.")
                    for issue in issues:
                        if issue.severity == "warning":
                            st.warning(f"{issue.field}: {issue.message}")
                except Exception as error:
                    st.error(f"Could not save the profile: {error}")

        current_profile = st.session_state.get("current_profile", {})
        if current_profile:
            with st.expander("Profile preview"):
                st.json(current_profile)
                st.download_button(
                    "Download profile JSON",
                    data=json.dumps(current_profile, indent=2),
                    file_name="student_profile.json",
                    mime="application/json",
                )

    current_profile = st.session_state.get("current_profile", {})
    if not current_profile:
        with school_list_tab:
            st.info("Save a profile before building a school list.")
        with reports_tab:
            st.info("Save a profile before generating reports.")
        return

    user_id = str(st.session_state["user_id"])
    with school_list_tab:
        show_school_list_panel(
            profile=current_profile,
            top_n=top_n,
            supabase_client=supabase_client,
            user_id=user_id,
        )

    with reports_tab:
        show_saved_reports_panel(
            supabase_client=supabase_client,
            user_id=user_id,
        )

        if st.button(
            "Generate Advising Report",
            type="primary",
            use_container_width=True,
        ):
            generate_and_store_report(
                profile=current_profile,
                top_n=top_n,
                supabase_client=supabase_client,
                user_id=user_id,
            )

        show_current_report_panel()


if __name__ == "__main__":
    main()

import json
import os

import streamlit as st
from dotenv import load_dotenv
from supabase import ClientOptions, create_client

from main import generate_report_for_profile
from repositories.supabase_profile_repository import (
    load_profile_from_supabase,
    save_profile_to_supabase,
)
from repositories.supabase_report_repository import save_report_to_supabase
from validation.profile_validator import validate_student_profile


load_dotenv()

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

        if st.button("Generate Advising Report", type="primary", use_container_width=True):
            try:
                with st.spinner("Generating rankings and agent reports..."):
                    result = generate_report_for_profile(
                        current_profile,
                        top_n=top_n,
                        report_owner_id=str(st.session_state["user_id"]),
                    )
            except Exception as error:
                st.exception(error)
            else:
                cloud_saved = False

                try:
                    save_report_to_supabase(
                        supabase_client=supabase_client,
                        user_id=str(st.session_state["user_id"]),
                        run_id=result.run_id,
                        generated_at_utc=result.generated_at_utc,
                        student_name=result.student_name,
                        final_report=result.final_report,
                        ranked_schools=result.ranked_schools,
                        warnings=result.warnings,
                        profile_snapshot=current_profile,
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
                    st.warning(
                        f"Local report path: {result.final_report_path}"
                    )

                st.markdown(result.final_report)
                st.download_button(
                    "Download final report",
                    data=result.final_report,
                    file_name=f"final_report_{result.run_id}.md",
                    mime="text/markdown",
                )


if __name__ == "__main__":
    main()

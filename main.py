import pandas as pd


from agents.profile_agent import profile_agent
from agents.school_fit_agent import school_fit_agent
from agents.critic_agent import critic_agent
from agents.school_match_agent import school_match_agent
from report_builder import build_final_report


def read_text_file(filename: str) -> str:
    """
    Reads a text file and returns its contents as a string.
    """

    with open(filename, "r") as file:
        return file.read()


def read_csv_as_text(filename: str) -> str:
    """
    Reads a CSV file and converts it into a readable text table.
    """

    df = pd.read_csv(filename)
    return df.to_string(index=False)


def save_output(filename: str, content: str) -> None:
    """
    Saves agent output to a file.
    """

    with open(filename, "w") as file:
        file.write(content)


def main():
    applicant_profile = read_text_file("data/applicant_profile.txt")
    schools_table = read_csv_as_text("data/merged_med_school_data.csv")

    profile_report = profile_agent(applicant_profile)
    school_fit_report = school_fit_agent(applicant_profile, schools_table)
    critic_report = critic_agent(applicant_profile, schools_table, school_fit_report)
    match_report = school_match_agent(applicant_profile, schools_table)
    final_report = build_final_report(
        applicant_profile=applicant_profile,
        profile_report=profile_report,
        school_fit_report=school_fit_report,
        critic_report=critic_report,
        match_report=match_report
    )

    print("\n===== PROFILE AGENT REPORT =====\n")
    print(profile_report)

    print("\n===== SCHOOL FIT AGENT REPORT =====\n")
    print(school_fit_report)

    print("\n===== CRITIC AGENT REPORT =====\n")
    print(critic_report)

    print("\n===== MATCH AGENT REPORT =====\n")
    print(match_report)

    print("\n===== FINAL REPORT CREATED =====\n")
    print("Saved to outputs/final_report.md")

    save_output("outputs/profile_report.txt", profile_report)
    save_output("outputs/school_fit_report.txt", school_fit_report)
    save_output("outputs/critic_report.txt", critic_report)
    save_output("outputs/match_report.txt", match_report)
    save_output("outputs/final_report.md", final_report)


if __name__ == "__main__":
    main()
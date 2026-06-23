from dataclasses import dataclass


@dataclass
class AgentReports:
    profile_report: str
    school_fit_report: str
    critic_report: str

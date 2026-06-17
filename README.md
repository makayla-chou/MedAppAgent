# Medical School Application Agent

This project is an agentic AI system designed to help medical school applicants analyze their profile, compare themselves to medical school data, and generate a realistic application strategy.

The system uses multiple specialized agents that work together to review an applicant profile, evaluate school fit, critique recommendations, and generate a final report. The agents are grounded in structured medical school data from CSV files rather than relying only on general model knowledge.

## Project Overview

The goal of this project is to demonstrate how agentic AI can be used to support pre-medical advising. The system takes in an applicant profile and a cleaned medical school dataset, then produces a written report with school recommendations and application strategy feedback.

The project currently includes:

- A profile agent that summarizes the applicant’s strengths and weaknesses
- A school fit agent that compares the applicant to medical school data
- A critic agent that reviews the school recommendations for realism
- A school match agent that recommends reach, target, and safer schools
- A report builder that combines all agent outputs into one final Markdown report


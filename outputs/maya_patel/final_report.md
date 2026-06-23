# MedAppAgent Final Advising Report

**Generated on:** 2026-06-19

---

## 1. Project Purpose

MedAppAgent is a multi-agent AI system designed to help medical school applicants organize their application profile, evaluate school fit, and receive realistic advising feedback.

This report was generated using three agents:

1. **Profile Agent** - summarizes the applicant's strengths, risks, and advising priorities.
2. **School Fit Agent** - evaluates school fit using applicant data and a school database.
3. **Critic Agent** - reviews school fit recommendations for overconfidence, unsupported claims, and missing verification.

---

## 2. Applicant Profile Used

{
  "basic_information": {
    "name": "Maya Patel",
    "state_residency": "New Jersey",
    "citizenship_status": "U.S. citizen",
    "undergraduate_school": "Rutgers University",
    "major": "Public Health",
    "application_year": 2027
  },
  "academics": {
    "overall_gpa": 3.88,
    "science_gpa": 3.82,
    "mcat_taken": true,
    "mcat_total": 517,
    "mcat_sections": {
      "chem_physics": 129,
      "cars": 128,
      "bio_biochem": 130,
      "psych_social": 130
    },
    "academic_context": "I maintained a strong academic record throughout college while completing an honors thesis and working part time. My grades were consistent, with my strongest performance in biology, biochemistry, and public health courses."
  },
  "experience_hours": {
    "clinical": 260,
    "shadowing": 55,
    "research": 1100,
    "nonclinical_volunteering": 180,
    "leadership": 240,
    "teaching": 90
  },
  "experience_descriptions": {
    "clinical": "I volunteered in an outpatient oncology clinic, where I escorted patients, prepared exam rooms, coordinated translated materials, and supported staff during patient check-in. I learned how continuity, clear communication, and emotional support affect the experience of patients receiving long-term treatment.",
    "research": "I completed an honors thesis examining differences in cancer screening access across income and insurance groups. I cleaned survey data, conducted statistical analyses in R, reviewed public health literature, and presented the findings at a regional undergraduate research conference. A manuscript based on the project is in preparation.",
    "service": "I volunteered with a refugee resettlement organization, helping newly arrived families navigate healthcare appointments, public transportation, and school enrollment. I also developed a simple resource guide describing local clinics and low-cost health services."
  },
  "achievements": {
    "research_outputs": [
      "Conference presentation",
      "Poster presentation",
      "Internal presentation"
    ],
    "awards": [
      "Rutgers Honors College Scholar",
      "Public Health Research Award, 2026",
      "Dean's List, 2023\u20132026"
    ]
  },
  "goals": {
    "career_interests": [
      "Internal medicine",
      "Public health",
      "Health equity",
      "Academic medicine"
    ],
    "populations_of_interest": "I am interested in caring for immigrant, refugee, and low-income communities that face barriers to preventive care and cancer screening."
  },
  "school_preferences": {
    "school_types": [
      "MD"
    ],
    "preferred_regions": [
      "Northeast",
      "Mid-Atlantic"
    ],
    "setting_preference": "Urban",
    "dealbreakers": [
      "Rural location",
      "Very high tuition"
    ]
  },
  "additional_context": "I prefer schools with strong public health partnerships, research opportunities, and access to diverse patient populations."
}

---

## 3. Profile Agent Report

1. Applicant Snapshot  
- Name: Maya Patel  
- State Residency: New Jersey  
- Citizenship: U.S. citizen  
- Undergraduate Institution: Rutgers University  
- Major: Public Health  
- Application Year: 2027  

2. Core Strengths  
- Strong academic performance: Overall GPA 3.88, Science GPA 3.82  
- High MCAT: 517 with balanced, strong section scores (129-130 range)  
- Extensive research experience (1100 hours) including an honors thesis and multiple presentations  
- Clinical exposure in oncology outpatient setting with patient-support roles  
- Significant volunteer service focused on vulnerable populations (refugees, immigrants)  
- Leadership and teaching experiences totaling over 300 hours  
- Recognized with multiple academic and research awards  
- Clear career focus on internal medicine, public health, health equity, and academic medicine  
- Preference for urban MD programs with public health and research emphasis aligns with applicant profile  

3. Risk Factors  
- Clinical hours are somewhat limited (260 hours) compared to some applicants—may want to broaden clinical experience or further highlight clinical competencies  
- Shadowing hours (55) are moderate; additional shadowing could solidify clinical exposure  
- No explicit mention of paid healthcare employment or scribing, which can sometimes strengthen clinical realism  
- No mention of letters of recommendation strength or interview skills (missing information)  

4. Advising Priorities  
- Consider applying broadly within Northeast and Mid-Atlantic urban MD programs that focus on public health and research to maximize fit and chance  
- Emphasize research achievements, patient-centered clinical experiences, and community service in essays and interviews to showcase well-roundedness  
- Pursue additional clinical experience or seek strong clinical letters to balance research-heavy profile  
- Develop compelling personal statement linking public health, health equity, and clinical goals  
- Prepare to discuss leadership and teamwork examples, especially in cross-cultural contexts  
- Research financial aid and scholarships due to sensitivity to high tuition  

5. Missing Information  
- Details on letters of recommendation (number, source, strength)  
- Interview readiness or planned preparation  
- Any MCAT retakes or plans for additional attempts if needed  
- Specific target schools or list of applied schools  
- Additional extracurriculars or hobbies beyond those listed  
- Experiences related to paid healthcare work or other healthcare exposure  
- Any challenges or gaps in education or timeline

---

## 4. School Fit Agent Report

| School                                                          | Classification | Reasoning                                                                                                                                                                                                                         | Concern                                            | Recommended Action                                         |
|-----------------------------------------------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|------------------------------------------------------------|
| Cooper Medical School of Rowan University                        | Target-ish     | Close in-state residency (NJ), urban setting, MD program; average GPA (3.79) and MCAT (512) slightly below applicant's scores (3.88 GPA, 517 MCAT), making it a reasonable match with good geographical fit.                        | Slightly lower average GPA and MCAT                  | Include as a target; prepare strong application emphasizing local ties and mission fit.             |
| Hackensack Meridian School of Medicine                          | Target-ish     | In-state, suburban setting in NJ, MD program; average GPA (3.8) and MCAT (514) close to applicant’s scores. The suburban setting may be less preferred but still fits mid-Atlantic region preference.                            | Slightly suburban setting, not urban as preferred    | Apply as a target school; highlight relevant experience and fit with mission.                      |
| Rutgers New Jersey Medical School                               | Reach          | In-state NJ with urban setting, MD program. Average GPA (3.7) lower than applicant’s but average MCAT (515) close. School has competitive metrics and is public, but slightly higher MCAT expectations.                            | Slightly competitive for GPA and MCAT                 | Apply with strong emphasis on academic achievements and research experience; consider as reach.    |
| Rutgers, Robert Wood Johnson Medical School                     | Reach          | In-state NJ, urban, MD. GPA average (3.7) lower than applicant; MCAT average (514) slightly lower than applicant’s 517. Competitive but applicant strong in GPA and MCAT.                                                        | Competitive GPA and MCAT averages                      | Apply; emphasize experience and mission alignment; treat as reach.                              |
| University of Pennsylvania Perelman School of Medicine         | High Reach    | Very high average GPA (3.97) and MCAT (521), very competitive private urban school in mid-Atlantic. Applicant’s scores excellent but just below average at this level.                                                        | Very competitive admissions metrics                  | Apply if feeling ambitious; consider as high reach.                                              |
| Georgetown University School of Medicine                        | Reach          | Private, urban mid-Atlantic school with average GPA (3.76) and MCAT (513) below applicant’s metrics. Applicant’s scores above average making it competitive, but private status can be selective.                              | Possibly competitive private school                    | Apply as reach with focus on mission fit and urban environment.                                  |
| George Washington University School of Medicine & Health Sciences | Reach          | Private urban mid-Atlantic school, average GPA 3.88 and MCAT 515, closely matching applicant’s metrics. Good geographic and urban fit.                                                                                     | Competitive private school admissions                  | Apply as reach; highlight strong clinical and research experience.                             |
| University of Maryland School of Medicine                       | Target-ish     | State public school in Maryland (mid-Atlantic), average GPA 3.84, MCAT 512 close to applicant’s scores. Urban setting matches applicant preference, and region is preferred.                                                 | Slightly competitive but good fit                      | Apply as target, emphasize public health and local residency.                                  |
| Thomas Jefferson Sidney Kimmel Medical College                 | Target-ish     | Private urban mid-Atlantic school, average GPA 3.80 and MCAT 513 close; applicant’s stats slightly higher. Mission and setting appropriate, competitive but within range.                                                    | Competitive private school                              | Apply as target; highlight relevant experiences and local mission fit.                        |
| Drexel University College of Medicine                           | Target-ish     | Private urban mid-Atlantic school in Philadelphia, average GPA 3.76 and MCAT 512 slightly below applicant. Slightly competitive but urban setting and region good.                                                        | Private school competitiveness                         | Apply as target with focus on applicant’s strengths; emphasize urban and public health interest. |
| Temple University Lewis Katz School of Medicine                | Target-ish     | Public urban school in Philadelphia with average GPA 3.70 and MCAT 510 slightly below applicant but within range. Urban location and region strong fit, public tuition may be favorable.                                     | Slightly lower averages but within range               | Apply as target; stress local connection and urban underserved care interest.                   |
| University of Pittsburgh School of Medicine                    | Reach          | Public urban mid-Atlantic school with average GPA 3.91 and MCAT 516, very competitive but applicant GPA (3.88) and MCAT (517) nearly matches. Strong urban setting, competitive admissions.                                | Highly competitive admissions                         | Apply as reach if competitive applicant; highlight strong research and clinical experience.    |
| Tufts University School of Medicine                             | Reach          | Private, urban Northeast school with average GPA 3.82 and MCAT 514 slightly below applicant; competitive admissions with good geographic fit.                                                                               | Competitive private school                             | Apply as reach; highlight mission fit and public health interests.                            |
| Boston University School of Medicine                           | Reach          | Private urban Northeast school with average GPA 3.76 and MCAT 517 close match for applicant. Urban and regional fit good, competitive admissions.                                                                            | Competitive private school                             | Apply as reach; focus on strong academic and research profile.                               |
| Harvard Medical School                                          | High Reach    | Top-tier private Northeast urban school with average GPA 3.9 and MCAT 520.5, extremely competitive with applicant stats slightly below average for Harvard.                                                                   | Extremely competitive admissions                       | Apply only if willing to accept risk; consider as high reach.                                 |
| University of Rochester School of Medicine and Dentistry       | Target-ish     | Private urban Northeast school with GPA 3.6 and MCAT 517. MCAT fits well but GPA is lower than applicant’s. Fits applicant's MCAT but slightly lower GPA average, urban setting good.                                        | Lower average GPA but good MCAT                         | Consider target-ish; verify fit with mission and preference.                                  |
| Albany Medical College                                         | Target-ish     | Private urban Northeast school with avg GPA 3.80 and MCAT 512, competitive but suitable region and setting. Applicant surpasses averages with strong application.                                                            | Competitive private setting                            | Apply as target-ish; highlight experiences relevant to mission and local health equity.       |
| University of Massachusetts T.H. Chan School of Medicine       | Target-ish     | Public urban Northeast school with average GPA 3.76 and MCAT 511, below applicant's scores but reasonable target. Urban and regional fit good, public tuition likely favorable.                                              | Lower averages but within reach                        | Apply as target; emphasize public health focus and urban/underserved mission.                 |
| Cooper Medical School of Rowan University                       | Target-ish     | Public urban mid-Atlantic school with avg GPA 3.79 and MCAT 512, slightly below applicant but good fit in terms of residency and mission.                                                                                     | None significant                                      | Apply as target with strong local mission emphasis.                                          |
| University of North Carolina at Chapel Hill School of Medicine | Target-ish     | Public suburban Southeast school with GPA 3.79 and MCAT 512, applicant slightly exceeds averages. Urban preference somewhat unmet but geographic and mission fit is moderate.                                               | Suburban setting, Southeast region                     | Apply as target if willing to consider Southeast; emphasize mission and research interest.     |
| University of California, Davis, School of Medicine            | Target-ish     | Public urban West school with avg GPA 3.72 and MCAT 509, lower averages but within range. Urban setting aligns; region less preferred.                                                                                      | Out-of-preferred region                               | Apply as target-ish; consider mission fit and research interest.                              |
| University of California, San Francisco, School of Medicine    | High Reach    | Elite public urban West Coast school with avg GPA 3.87 and MCAT 517, very competitive. Applicant matches averages well but school highly competitive and less preferred West Coast location.                                  | Highly competitive, geographic preference             | Apply only if very ambitious; consider high reach.                                           |
| University of California, Los Angeles David Geffen School of Medicine | High Reach    | Top public urban West Coast school with avg GPA 3.81 and MCAT 516, competitive admissions. Urban but located outside preferred Northeast/Mid-Atlantic region.                                                               | Location outside preferred region                      | Apply only if willing to expand region; consider high reach.                                |
| University of Michigan Medical School                          | Target-ish     | Public urban Midwest school with avg GPA 3.85 and MCAT 516, good academic fit but outside preferred region.                                                                                                                   | Location outside preferred region                      | Apply target-ish with strong academic advantages; mention public health research interest.     |
| University of Washington School of Medicine                    | Target-ish     | Public urban West school with avg GPA 3.7 and MCAT 511, lower averages but competitive and urban setting good. Geographical region less preferred but strong research and clinical opportunities.                              | Location outside preferred region                      | Apply as target-ish if applicant is open to West region.                                    |
| University of Alabama at Birmingham Marnix E. Heersink School of Medicine | Safer          | Public urban Southeast school with avg GPA 3.87 and MCAT 509. Applicant exceeds or matches well. Urban setting reasonable but in Southeast.                                                                              | Location outside preferred region, lower MCAT average | Consider as safer option if expanding region; highlight clinical and research experience.       |
| Frederick P. Whiddon College of Medicine at University of South Alabama | Safer          | Public urban Southeast school with avg GPA 3.85 and MCAT 508. Applicant stronger on scores, location urban but in Southeast.                                                                                                  | Location outside preferred region                      | Include as safer; good academic fit; consider if open to Southeast.                           |
| University of Kentucky College of Medicine                     | Safer          | Public urban Southeast school with avg GPA 3.84 and MCAT 508, good academic fit for applicant but outside preferred region.                                                                                                  | Location outside preferred region                      | Consider safer if willing to expand region; good urban setting and public program.             |
| University of South Carolina Kay and C. Edward Floyd, M.D. School of Medicine | Safer          | Public urban Southeast school with avg GPA 3.77 and MCAT 508. Applicant surpasses averages but location outside preferred region.                                                                                             | Location outside preferred region                      | Include as safer if open to Southeast; emphasize mission fit and clinical interests.            |
| Medical College of Georgia at Augusta University               | Safer          | Public urban Southeast school with avg GPA 3.80 and MCAT 512. Applicant meets or exceeds averages; location out of preferred regions but good fit academically.                                                               | Location outside preferred region                      | Consider safer if expanding geographic options; urban setting fits preferences.                |
| University of Pittsburgh School of Medicine                    | Reach          | Public urban Mid-Atlantic school, average GPA 3.91 and MCAT 516, close match but competitive. Good geographic and urban fit.                                                                                                | Competitive admissions metrics                         | Apply as reach emphasizing research and public health interests.                             |

**Notes:**
- Schools marked as “High Reach” have very competitive metrics significantly above applicant’s averages or top-tier reputations.
- “Reach” schools have metrics close to applicant but more competitive admission or some significant selectivity.
- “Target-ish” schools have metrics similar or slightly below applicant, good fit but not guaranteed acceptance.
- “Safer” schools show applicant exceeds average academic metrics, but some have geographical or other fit issues.
- Schools with “NR” (Not reported) MCAT minimum need verification before applying.
- Applicant prefers Northeast/Mid-Atlantic region and urban settings, MD programs only, and schools with good public health and research opportunities.
- Schools with unknown or missing data are not included due to lack of verification.

---

## 5. Critic Agent Report

1. Overall Assessment  
The School Fit Agent's recommendations for Maya Patel generally align well with her strong academic profile, state residency, and stated preferences. The classifications reflect a cautious and realistic approach, appropriately distinguishing between “High Reach,” “Reach,” “Target-ish,” and “Safer” schools based on average GPA/MCAT metrics and institutional selectivity. Recommendations emphasize geographical fit (favoring Northeast and Mid-Atlantic) and urban settings, consistent with the applicant’s expressed preferences. The advice includes nuanced mentions of school competitiveness, mission fit, and applicant advantages, which is prudent and avoids overconfidence or guarantees of admission.

2. Major Flags  
- No explicit guarantees or ethical concerns implying guaranteed acceptance are present.  
- The agent correctly identifies more competitive “High Reach” schools without overstating chances.  
- The suggested broadening of region in some “Safer” options (e.g., Southeast or West coast schools) is flagged with reminders about geographic preference, which is appropriate.  
- The agent notes when MCAT minimums or other data are “Not reported” (NR) or need verification where relevant.  

3. Classification Concerns  
- No major misclassifications were flagged. The classifications are consistent with provided data on average GPA and MCAT.  
- Some “Target-ish” schools have slightly lower averages but appear reasonable choices given applicant's scores and preferences.  
- “High Reach” schools have appropriately high expected academic metrics or prestige relative to applicant stats.  
- The “Safer” category includes schools where applicant exceeds metrics, even if outside preferred geographic region, which is acceptable so long as the applicant is informed.  

4. Missing Data to Verify  
- Several schools have “NR” (Not Reported) MCAT minimum or average GPAs that should be verified before finalizing applications; the agent correctly points this out in general but no specific schools here flagged for correction.  
- Some schools with no provided data in the table (e.g., Alice L. Walton School of Medicine, Charles R. Drew University, Methodist University Cape Fear Valley Health School of Medicine, Thomas F. Frist, Jr. College of Medicine at Belmont University) are excluded appropriately due to lack of verified data.  
- The report should continuously confirm any school with incomplete or missing data before recommendation refinement.  

5. Recommended Revisions  
- While geographic preferences are noted, the agent might more explicitly caution including out-of-region schools only if the applicant is open to relocation or less regional alignment. For example, schools in the Southeast and West appear as “Safer” though they fall outside the stated “Northeast, Mid-Atlantic” preference.  
- For schools classified as “Target-ish” but located in suburban areas (e.g., Hackensack Meridian, UNC Chapel Hill), the agent should ensure the applicant understands these settings differ slightly from her preference for urban environments.  
- Explicitly state that inclusion of highly competitive private schools (e.g., Harvard, UPenn, Columbia) should only be if applicant accepts high risk of rejection given intense selectivity. This is implied but could be more prominent to avoid any perceived overconfidence.  
- For any school with reported MCAT minimums or percentile-based minimums, if applicant's MCAT is near but not clearly above the threshold, suggest verifying school policies about minimums for in-state versus out-of-state applicants as this can affect chances and applicant is New Jersey resident.  
- Emphasize that while applicant’s strong academic profile supports broad target/reach list, she should pair application volume with genuine interest and preparedness for varied levels of competitiveness and mission alignment.  

In summary, the School Fit Agent’s recommendations are balanced, data-supported, and aligned with the applicant’s profile and stated preferences. Minor clarifications on regional flexibility, setting nuances, and high competition disclaimers would improve transparency and applicant decision-making.

---

---

## 6. Match Agent Report

# School Match Report

## Strongest Matches
1. **Rutgers New Jersey Medical School (NJ)**
   - Public, urban, in-state (New Jersey) school.
   - Average GPA 3.70, average MCAT 515; Maya’s 3.88 GPA and 517 MCAT are above average.
   - Strong public health environment in NJ, aligns with Maya’s background and goals.
   - Urban setting fits preference.
   - Deadline December 1, 2026, so on time for 2027 cycle.
   
2. **Rutgers Robert Wood Johnson Medical School (NJ)**
   - Public, urban, in-state school in New Brunswick, NJ.
   - Average GPA 3.70, average MCAT 514; Maya’s stats exceed these.
   - Strong research and public health connections.
   - Urban setting, matches preference.
   - Deadline December 1, 2026.
   
3. **Cooper Medical School of Rowan University (NJ)**
   - Public, urban, in-state school in Camden, NJ.
   - Average GPA 3.79, average MCAT 512; Maya’s stats are above average.
   - Urban setting and strong public health focus.
   - Deadline November 16, 2026.
   
4. **University of Maryland School of Medicine (MD)**
   - Public, urban, Mid-Atlantic school.
   - Average GPA 3.84, average MCAT 512; Maya’s stats are slightly above average.
   - Urban setting, strong research and public health opportunities.
   - Deadline November 2, 2026.
   - Maryland is neighboring state, reasonable for regional preference.
   
5. **Geisel School of Medicine at Dartmouth (NH)**
   - Private, urban, Northeast school.
   - Average GPA 3.77, average MCAT 516; Maya’s stats slightly above average.
   - Strong research and public health reputation.
   - Urban setting is a bit town-like but close enough.
   - Deadline November 2, 2026.
   
6. **Boston University School of Medicine (MA)**
   - Private, urban, Northeast school.
   - Average GPA 3.76, average MCAT 517; Maya’s stats slightly above average.
   - Urban setting, strong public health and research.
   - Deadline November 2, 2026.
   
7. **Tufts University School of Medicine (MA)**
   - Private, urban, Northeast school.
   - Average GPA 3.82, average MCAT 514; Maya’s stats are above average.
   - Urban setting, strong public health and research.
   - Deadline November 2, 2026.
   
8. **University of Pittsburgh School of Medicine (PA)**
   - Public, urban, Mid-Atlantic school.
   - Average GPA 3.91, average MCAT 516; Maya’s GPA slightly below average but MCAT on par.
   - Urban setting, strong research and public health.
   - Deadline October 15, 2026.
   
9. **University of Virginia School of Medicine (VA)**
   - Public, urban, Mid-Atlantic school.
   - Average GPA 3.85, average MCAT 518; Maya’s stats very close.
   - Urban setting, strong research and public health.
   - Deadline November 2, 2026.
   
10. **Virginia Commonwealth University School of Medicine (VA)**
    - Public, urban, Mid-Atlantic school.
    - Average GPA 3.70, average MCAT 512; Maya’s stats above average.
    - Urban setting, good public health opportunities.
    - Deadline October 15, 2026.

## Reach Schools
1. **Columbia University Vagelos College of Physicians and Surgeons (NY)**
   - Private, urban, Northeast.
   - Average GPA 3.85, average MCAT 521; Maya’s MCAT 517 is slightly below average.
   - Very competitive, Ivy-level school.
   - Deadline October 15, 2026.
   - Fits region and urban preference, strong research and public health.
   
2. **NYU Grossman School of Medicine (NY)**
   - Private, urban, Northeast.
   - Average GPA 3.98, average MCAT 523; Maya’s stats are below average.
   - Extremely competitive.
   - Deadline October 15, 2026.
   
3. **Yale School of Medicine (CT)**
   - Private, urban, Northeast.
   - Average GPA 3.94, average MCAT 521; Maya’s stats below average.
   - Very competitive.
   - Deadline October 15, 2026.
   
4. **Perelman School of Medicine at the University of Pennsylvania (PA)**
   - Private, urban, Mid-Atlantic.
   - Average GPA 3.97, average MCAT 521; Maya’s stats below average.
   - Extremely competitive.
   - Deadline October 15, 2026.
   
5. **Washington University in St. Louis School of Medicine (MO)**
   - Private, urban, Midwest (not preferred region).
   - Average GPA 3.88, average MCAT 519.5; Maya’s stats slightly below MCAT.
   - Very competitive.
   - Deadline October 15, 2026.
   
6. **Northwestern University Feinberg School of Medicine (IL)**
   - Private, urban, Midwest (not preferred region).
   - Average GPA 3.93, average MCAT 521; Maya’s stats below average.
   - Very competitive.
   - Deadline November 2, 2026.
   
7. **Icahn School of Medicine at Mount Sinai (NY)**
   - Private, urban, Northeast.
   - Average GPA 3.81, average MCAT 519; Maya’s MCAT slightly below average.
   - Competitive.
   - Deadline October 1, 2026.

## Target Schools
1. **Hackensack Meridian School of Medicine (NJ)**
   - Private, suburban, Mid-Atlantic.
   - Average GPA 3.80, average MCAT 514; Maya’s stats slightly above.
   - Fits region and near urban setting.
   - Deadline December 1, 2026.
   
2. **University of Rochester School of Medicine and Dentistry (NY)**
   - Private, urban, Northeast.
   - Average GPA 3.60, average MCAT 517; Maya’s GPA well above average.
   - Urban setting.
   - Deadline October 15, 2026.
   
3. **Albany Medical College (NY)**
   - Private, urban, Northeast.
   - Average GPA 3.80, average MCAT 512; Maya’s stats above average.
   - Urban setting.
   - Deadline November 2, 2026.
   
4. **University of Massachusetts T.H. Chan School of Medicine (MA)**
   - Public, urban, Northeast.
   - Average GPA 3.76, average MCAT 511; Maya’s stats above average.
   - Urban setting.
   - Deadline October 15, 2026.
   
5. **University of Connecticut School of Medicine (CT)**
   - Public, suburban, Northeast.
   - Average GPA 3.76, average MCAT 513; Maya’s stats above average.
   - Suburban, but close to urban areas.
   - Deadline November 16, 2026.
   
6. **University of Pennsylvania (Perelman) is a reach but University of Pittsburgh is a target**
   - University of Pittsburgh has slightly lower GPA average and Maya’s stats fit better.
   
7. **Drexel University College of Medicine (PA)**
   - Private, urban, Mid-Atlantic.
   - Average GPA 3.76, average MCAT 512; Maya’s stats above average.
   - Urban setting.
   - Deadline December 1, 2026.
   
8. **Sidney Kimmel Medical College at Thomas Jefferson University (PA)**
   - Private, urban, Mid-Atlantic.
   - Average GPA 3.80, average MCAT 513; Maya’s stats above average.
   - Urban setting.
   - Deadline November 16, 2026.

## Safer Schools
1. **University of New Mexico School of Medicine (NM)**
   - Public, urban, Southwest (not preferred region).
   - Average GPA 3.75, average MCAT 507; Maya’s stats well above.
   - Urban setting.
   - Deadline November 2, 2026.
   
2. **University of Kentucky College of Medicine (KY)**
   - Public, urban, Southeast (not preferred region).
   - Average GPA 3.84, average MCAT 508; Maya’s stats well above.
   - Urban setting.
   - Deadline November 2, 2026.
   
3. **Medical University of South Carolina College of Medicine (SC)**
   - Public, urban, Southeast (not preferred region).
   - Average GPA 3.85, average MCAT 511.2; Maya’s stats above.
   - Urban setting.
   - Deadline November 2, 2026.
   
4. **Indiana University School of Medicine (IN)**
   - Public, urban, Midwest (not preferred region).
   - Average GPA 3.85, average MCAT 512; Maya’s stats above.
   - Urban setting.
   - Deadline November 16, 2026.
   
5. **University of Iowa Carver College of Medicine (IA)**
   - Public, urban, Midwest (not preferred region).
   - Average GPA 3.81, average MCAT 514; Maya’s stats above.
   - Urban setting.
   - Deadline November 2, 2026.
   
6. **University of South Carolina School of Medicine – Columbia (SC)**
   - Public, urban, Southeast (not preferred region).
   - Average GPA 3.77, average MCAT 508; Maya’s stats well above.
   - Urban setting.
   - Deadline November 2, 2026.

## Schools to Be Careful With
1. **Schools with missing data (e.g., Alice L. Walton School of Medicine, Charles R. Drew University of Medicine and Science College of Medicine, Methodist University Cape Fear Valley Health School of Medicine, Roseman University College of Medicine, Thomas F. Frist, Jr. College of Medicine at Belmont University)**
   - Lack of GPA and MCAT data makes it hard to assess fit.
   - Applying here is risky without more info.
   
2. **Schools with rural or town settings (dealbreaker)**
   - Geisel School of Medicine at Dartmouth is in a town setting, which Maya dislikes.
   - University of South Dakota Sanford School of Medicine (town).
   - University of Massachusetts (Worcester) is urban but more suburban/town-like.
   - These may not fit Maya’s preference.
   
3. **Schools with very high tuition (dealbreaker)**
   - Private schools tend to have higher tuition; Maya should be cautious with private schools outside NJ and nearby states.
   - Examples: Harvard Medical School, Columbia, NYU Grossman, Perelman, Yale.
   - These are also reach schools, so applying to many may not be cost-effective.
   
4. **Schools outside preferred regions**
   - Many strong schools are outside Northeast or Mid-Atlantic (e.g., Michigan, Illinois, California).
   - Maya prefers Northeast and Mid-Atlantic, so applying broadly outside these regions may reduce chances and increase costs.
   
5. **Howard University College of Medicine (DC)**
   - MCAT average 507, GPA 3.61, but Maya’s stats are much higher.
   - May be a mismatch in mission and competitiveness.
   
6. **Schools with minimum MCAT higher than Maya’s score**
   - None explicitly listed with minimum MCAT above 517, but some have average MCAT higher than 517 (e.g., Columbia, Yale, Perelman, NYU Grossman).
   - These are reach schools but not safe.

## Final Recommendation
Maya has a strong GPA (3.88) and excellent MCAT (517) with rich research, clinical, and public health experience, and clear regional and setting preferences (Northeast/Mid-Atlantic, urban, MD schools, no rural, no very high tuition).

- **Apply broadly within NJ public schools (Rutgers NJMS, RWJMS, Cooper) as strong targets/likely admits.**
- **Add solid public, urban Mid-Atlantic and Northeast public schools with good public health/research (UMD, Pitt, UVA, VCU, UConn, UMass, Drexel, Sidney Kimmel) as targets.**
- **Include a few private Northeast urban schools with strong public health/research but be mindful of high tuition and competitiveness (Boston University, Tufts, Albany).**
- **Include a few reach schools with very high prestige and stats slightly above Maya’s (Columbia, Yale, Perelman, NYU Grossman) but limit these to a few due to competitiveness and cost.**
- **Avoid rural or town schools and those with missing data or outside preferred regions unless Maya is willing to expand preferences.**
- **Avoid applying to schools with very high tuition unless financial aid is assured.**

This balanced strategy maximizes Maya’s chances by focusing on schools where her stats and profile fit well, with a few reach options for ambition, and avoids schools that do not align with her preferences or are unrealistic.

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
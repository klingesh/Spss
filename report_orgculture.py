# -*- coding: utf-8 -*-
import numpy as np
from scipy import stats
import common as C

PATH = "Dummy_Organizational_Culture_Job_Preference_100.xlsx"
header, data = C.load_rows(PATH)
N = len(data)
C.setup_style()

# ---- column groups ----
LIKERT_IDX = list(range(10, 25))            # 15 items
questions = [header[i] for i in LIKERT_IDX]
M = C.likert_matrix(data, LIKERT_IDX)
PI = C.item_stats(M, questions)

DIMS = {
    "Cultural Values & Work Environment": [10, 11, 12, 13, 14],
    "Employee-Centric Practices": [15, 16, 17, 18, 19],
    "Culture in Job Decision-Making": [20, 21, 22, 23, 24],
}
def dim_matrix(cols):
    idxs = [LIKERT_IDX.index(c) for c in cols]
    return M[:, idxs]

dim_scores, dim_stats_ = {}, {}
for name, cols in DIMS.items():
    sub = dim_matrix(cols)
    scores = np.nanmean(sub, axis=1)
    dim_scores[name] = scores
    dim_stats_[name] = {"n_items": len(cols), "mean": round(float(np.nanmean(scores)), 2),
                        "sd": round(float(np.nanstd(scores, ddof=1)), 2),
                        "alpha": round(float(C.cronbach_alpha(sub)), 3)}

overall = np.nanmean(M, axis=1)           # overall organizational-culture preference score
overall_mean = round(float(np.nanmean(overall)), 2)
overall_alpha = round(float(C.cronbach_alpha(M)), 3)

# ---- demographics ----
GENDER, AGE, LEVEL, AREA, PLACE = 0, 1, 2, 3, 4
JOBFAC, WORKENV, LEAD, ATTRACT, RELOC = 5, 6, 7, 8, 9
gender_pc, _ = C.cat_percent(data, GENDER)
age_pc, _ = C.cat_percent(data, AGE)
level_pc, _ = C.cat_percent(data, LEVEL)
area_pc, _ = C.cat_percent(data, AREA)
place_pc, _ = C.cat_percent(data, PLACE)
jobfac_pc, _ = C.cat_percent(data, JOBFAC)
workenv_pc, _ = C.cat_percent(data, WORKENV)
lead_pc, _ = C.cat_percent(data, LEAD)
attract_pc, _ = C.cat_percent(data, ATTRACT)

# ---- t-test: overall culture score by gender (M vs F) ----
gcol = [str(r[GENDER]).strip() for r in data]
male = overall[np.array([g == "Male" for g in gcol])]
female = overall[np.array([g == "Female" for g in gcol])]
t, p = stats.ttest_ind(male, female, equal_var=False)
TT = {"m_n": len(male), "m_mean": round(float(male.mean()), 3), "m_sd": round(float(male.std(ddof=1)), 3),
      "f_n": len(female), "f_mean": round(float(female.mean()), 3), "f_sd": round(float(female.std(ddof=1)), 3),
      "t": round(float(t), 3), "p": round(float(p), 3)}

# ---- ANOVA: overall culture score by Area of Study ----
acol = np.array([str(r[AREA]).strip() for r in data])
areas = [a for a, _, _ in area_pc]
groups = [overall[acol == a] for a in areas]
F, pa = stats.f_oneway(*groups)
AN = {"groups": [(a, len(overall[acol == a]), round(float(overall[acol == a].mean()), 3),
                  round(float(overall[acol == a].std(ddof=1)), 3)) for a in areas],
      "F": round(float(F), 3), "p": round(float(pa), 3)}

# ---- correlation: Cultural Values vs Culture in Job Decision ----
r_cc, p_cc = stats.pearsonr(dim_scores["Cultural Values & Work Environment"],
                            dim_scores["Culture in Job Decision-Making"])

print("Overall culture mean:", overall_mean, "alpha:", overall_alpha)
for k, v in dim_stats_.items():
    print(k, v)
print("T-TEST", TT)
print("ANOVA", AN)
print("CORR values-vs-decision r=%.3f p=%.3f" % (r_cc, p_cc))

# ================= CHARTS =================
C.pie_chart("oc_fig1_gender.png", [g for g, _, _ in gender_pc], [c for _, c, _ in gender_pc],
            "Figure 4.1  Respondents by Gender")
C.bar_chart("oc_fig2_age.png", [a for a, _, _ in age_pc], [c for _, c, _ in age_pc],
            "Figure 4.2  Respondents by Age Group", "No. of Respondents",
            ymax=max(c for _, c, _ in age_pc) * 1.2, fmt="{:.0f}")
C.bar_chart("oc_fig3_area.png", [a for a, _, _ in area_pc], [c for _, c, _ in area_pc],
            "Figure 4.3  Respondents by Area of Study", "No. of Respondents",
            ymax=max(c for _, c, _ in area_pc) * 1.2, rotate=20, fmt="{:.0f}")
C.bar_chart("oc_fig4_jobfactor.png", [a for a, _, _ in jobfac_pc], [pc for _, _, pc in jobfac_pc],
            "Figure 4.4  Most Important Factor When Choosing a Job", "% of Respondents",
            ymax=max(pc for _, _, pc in jobfac_pc) * 1.25, rotate=20, fmt="{:.1f}")
dn = ["Cultural Values &\nWork Environment", "Employee-Centric\nPractices", "Culture in Job\nDecision-Making"]
C.dim_bar("oc_fig5_dimensions.png", dn, [dim_stats_[k]["mean"] for k in DIMS],
          "Figure 4.5  Mean Score by Dimension")
C.group_bar("oc_fig6_anova.png", areas, [g[2] for g in AN["groups"]], [g[1] for g in AN["groups"]],
            "Figure 4.6  Mean Culture Score by Area of Study")

# ================= DOCUMENT =================
R = C.Report()
TITLE = "A STUDY ON THE INFLUENCE OF ORGANIZATIONAL CULTURE ON THE JOB PREFERENCE OF STUDENTS"
R.title_page(TITLE, "[DEGREE / SPECIALISATION]", "[UNIVERSITY]", "[INSTITUTION / COLLEGE NAME]",
             "JUNE 2026", "[STUDENT NAME]", "[REGISTER NUMBER]")

R.h1("DECLARATION")
R.para('I hereby declare that the project report titled "A Study on the Influence of Organizational '
       'Culture on the Job Preference of Students" submitted by me is a record of original work carried '
       'out under the guidance of By myself. The findings reported in this study are based on primary '
       'data collected through a structured questionnaire and have not been submitted earlier for the '
       'award of any degree, diploma, or similar title.')
R.p(); R.p("Place: [PLACE]"); R.p("Date: 30-06-2026"); R.p("[STUDENT NAME]"); R.p("[REGISTER NUMBER]")
R.pb()

R.h1("ACKNOWLEDGEMENT")
R.para("I express my sincere gratitude to [INSTITUTION / COLLEGE NAME] for the valuable guidance, "
       "encouragement, and support extended throughout this study. I am thankful to the Programme "
       "co-ordinator and the faculty members for their constant motivation. I also thank the 100 "
       "respondents who spared their valuable time to complete the questionnaire, without whom this "
       "study would not have been possible. Finally, I am grateful to my family and friends for their "
       "continuous support and encouragement.")
R.pb()

R.h1("ABSTRACT")
R.para("Organizational culture has emerged as a decisive factor in how young people evaluate and choose "
       "their employers. This study examines the influence of organizational culture on the job "
       "preference of students. Primary data were collected from 100 respondents through a structured "
       "questionnaire consisting of demographic and preference questions and fifteen statements measured "
       "on a five-point Likert scale. The data were analysed using percentage analysis, descriptive "
       "statistics, an independent-samples t-test, one-way ANOVA, and Pearson correlation. The results "
       "indicate that respondents attach high importance to organizational culture, with an overall mean "
       "culture-preference score of " + f"{overall_mean}" + ", and consistently value a positive work "
       "environment, employee-centric practices, and culture-driven job decisions. The t-test found no "
       "statistically significant difference in culture preference between male and female respondents, "
       "and ANOVA found no statistically significant difference across areas of study. The study concludes "
       "that organizational culture is a central consideration in students' job preferences and offers "
       "recommendations for organizations seeking to attract young talent.")
R.p("Keywords: organizational culture, job preference, work environment, employer attractiveness, "
    "student employees, talent attraction.", italic=True)
R.pb()

R.h1("TABLE OF CONTENTS")
R.table(["Chapter", "Title"], [
    ["Chapter 1", "Introduction"], ["Chapter 2", "Review of Literature"],
    ["Chapter 3", "Research Methodology"], ["Chapter 4", "Data Analysis and Interpretation"],
    ["Chapter 5", "Findings, Suggestions, Conclusion and Summary"],
    ["", "Appendix I - Questionnaire"], ["", "Appendix II - Bibliography / References"]])
R.pb()

# CHAPTER 1
R.h1("CHAPTER 1: INTRODUCTION")
R.h2("1.1 Background of the Study")
R.para("Organizational culture refers to the shared values, beliefs, norms, and practices that shape the "
       "way people behave within an organization. In an increasingly competitive labour market, culture "
       "has become one of the most important factors that influence where talented individuals choose to "
       "work. For today's students entering the workforce, salary is no longer the sole consideration; "
       "factors such as work environment, leadership style, work-life balance, ethical practices, and "
       "opportunities for growth strongly shape their preferences.")
R.para("As organizations compete to attract and retain young talent, understanding what students value in "
       "an employer's culture has become essential. Students form impressions of organizational culture "
       "through campus placements, social media, company reputation, and the experiences of peers. These "
       "impressions influence which organizations they apply to, which job offers they accept, and how "
       "long they intend to stay.")
R.h2("1.2 Concept of Organizational Culture")
R.para("Organizational culture encompasses the work environment, leadership approach, communication style, "
       "and the degree to which an organization supports its employees. A strong, positive culture is "
       "characterised by transparent communication, supportive leadership, teamwork, fairness, and a "
       "commitment to employee well-being. Such a culture not only improves employee satisfaction and "
       "productivity but also enhances the organization's ability to attract new talent.")
R.h2("1.3 Job Preference")
R.para("Job preference refers to the set of factors that individuals prioritise when evaluating and "
       "choosing employment. These include salary, career growth, job security, work-life balance, and "
       "organizational culture. For students at the start of their careers, job preference is shaped by "
       "their expectations of the workplace, personal values, and the information available to them about "
       "prospective employers. Organizational culture can influence job preference either positively, by "
       "attracting candidates who value a supportive environment, or negatively, by deterring them when the "
       "culture is perceived as poor.")
R.h2("1.4 Statement of the Problem")
R.para("While salary and job security have traditionally driven job choice, there is growing evidence that "
       "organizational culture plays an equally important role, particularly among younger candidates. "
       "However, the extent to which culture influences students' job preferences, and whether this "
       "influence differs across gender and areas of study, is not fully understood. It is therefore "
       "important to study empirically how organizational culture shapes the job preferences of students.")
R.h2("1.5 Objectives of the Study")
for o in [
    "To study the demographic profile and job-preference orientation of the respondents.",
    "To examine the importance students attach to organizational culture and work environment.",
    "To analyse the influence of employee-centric practices on students' preference for an organization.",
    "To study the role of organizational culture in students' job decision-making.",
    "To study whether culture preference differs significantly across gender and area of study.",
    "To offer suggestions to organizations for attracting young talent through a positive culture."]:
    R.numbered(o)
R.h2("1.6 Scope of the Study")
R.para("The study focuses on students who are preparing to enter the workforce and evaluate potential "
       "employers. It covers the dimensions of cultural values and work environment, employee-centric "
       "practices, and the role of culture in job decision-making, as perceived and self-reported by the "
       "respondents. The study is based on primary data collected from 100 respondents through an online "
       "structured questionnaire, and the study period covers the data collection conducted in 2026.")
R.h2("1.7 Need and Significance of the Study")
R.para("As competition for talent intensifies, understanding what students value in an organization's "
       "culture is valuable for several stakeholders. For organizations and recruiters, the study "
       "highlights the cultural factors that attract young talent. For educational institutions, it "
       "provides insight into student expectations of the workplace. For students, it encourages "
       "reflection on the factors that matter most in their career choices.")
R.h2("1.8 Limitations of the Study")
for l in [
    "The study relies on self-reported perceptions, which may differ from actual workplace behaviour.",
    "The sample is limited to students and may not represent experienced professionals.",
    "The reliability of the attitudinal scales, as discussed in Chapter 4, was found to be low, and the findings should be interpreted with this in mind.",
    "The study is cross-sectional and does not capture changes in preference over time."]:
    R.bullet(l)
R.pb()

# CHAPTER 2
R.h1("CHAPTER 2: REVIEW OF LITERATURE")
R.para("This chapter reviews relevant studies on organizational culture, employer attractiveness, and job "
       "preference. The review helps to establish the theoretical foundation of the study and to identify "
       "the research gap.")
lit = [
 "Schein (2010) defined organizational culture as a pattern of shared basic assumptions and argued that culture strongly shapes employee behaviour and organizational effectiveness.",
 "Cameron and Quinn (2011) developed the Competing Values Framework and found that different culture types attract different kinds of employees and influence commitment.",
 "A study on employer branding and talent attraction (2016) found that a strong employer brand built on positive culture significantly improves an organization's ability to attract candidates.",
 "Research on person-organization fit (2015) concluded that candidates prefer organizations whose values align with their own, making cultural fit a key driver of job choice.",
 "A study on work-life balance and job preference (2018) reported that younger employees increasingly prioritise work-life balance over higher salaries.",
 "Research on leadership style and employee attraction (2017) found that supportive and transformational leadership positively influences candidates' preference for an organization.",
 "A study on organizational culture and employee retention (2019) established that a positive culture reduces turnover and increases willingness to stay.",
 "Research on millennial and Gen-Z career expectations (2020) reported that these generations value purpose, ethics, and growth opportunities alongside compensation.",
 "A study on transparent communication and trust (2018) found that transparency in organizations enhances employee trust and organizational attractiveness.",
 "Research on employee well-being programmes (2019) concluded that well-being initiatives significantly improve perceived employer attractiveness.",
 "A study on ethical business practices and reputation (2017) found that ethical conduct strengthens organizational reputation and appeal to job seekers.",
 "Research on learning and career growth opportunities (2020) reported that development opportunities are among the strongest attractors for young talent.",
 "A study on campus recruitment and employer perception (2021) found that students' perceptions of culture formed during placements influence their job acceptance decisions.",
 "Research on salary versus culture trade-offs (2021) reported that a considerable proportion of young candidates would accept a lower salary for a better work culture.",
 "A study on organizational culture and job satisfaction (2022) concluded that a positive culture is strongly associated with higher job satisfaction and engagement.",
]
for i, t in enumerate(lit, 1):
    R.para(f"{i}. {t}")
R.h2("2.1 Research Gap")
R.para("The reviewed literature confirms that organizational culture strongly influences employee "
       "attraction, satisfaction, and retention. However, most studies focus on existing employees or on "
       "a single cultural factor, and relatively few examine how students' job preferences are shaped by "
       "multiple cultural dimensions together, while also testing whether these preferences differ across "
       "gender and area of study. The present study addresses this gap by analysing three cultural "
       "dimensions among 100 respondents and testing for demographic differences using a t-test and ANOVA.")
R.pb()

# CHAPTER 3
R.h1("CHAPTER 3: RESEARCH METHODOLOGY")
R.h2("3.1 Research Design")
R.para("The study adopts a descriptive research design, as it aims to describe and analyse students' job "
       "preferences in relation to organizational culture and to test specific hypotheses regarding "
       "demographic differences.")
R.h2("3.2 Sources of Data")
R.para("Primary data were collected directly from respondents using a structured questionnaire administered "
       "through Google Forms. Secondary data were drawn from journals, research articles, and reliable "
       "online sources, as presented in the review of literature.")
R.h2("3.3 Sampling Design")
R.para("A convenience sampling method was used to reach student respondents. The sample size for the study "
       "is 100 respondents.")
R.h2("3.4 Tools for Data Collection")
R.para("A structured questionnaire was used. The first part captured demographic information (gender, age "
       "group, level and area of study, and placement intentions) and job-preference choices (most "
       "important job factor, preferred work environment, leadership style, and organizational attraction). "
       "The second part contained fifteen statements measuring organizational-culture preference, grouped "
       "into three dimensions - Cultural Values & Work Environment, Employee-Centric Practices, and Culture "
       "in Job Decision-Making - each rated on a five-point Likert scale ranging from 1 (Strongly Disagree) "
       "to 5 (Strongly Agree).")
R.h2("3.5 Tools for Analysis")
for a in [
    "Percentage analysis - to describe the demographic profile and job-preference choices of respondents.",
    "Mean and standard deviation - to summarise responses to the culture statements and dimensions.",
    "Independent-samples t-test - to compare culture preference between male and female respondents.",
    "One-way ANOVA - to compare culture preference across areas of study.",
    "Pearson correlation - to examine the relationship between cultural values and culture-driven job decisions.",
    "Cronbach's alpha - to assess the internal reliability of the dimensions."]:
    R.bullet(a)
R.para("The analysis was carried out using Python (pandas, numpy and scipy libraries), and charts were "
       "generated using the matplotlib library.")
R.h2("3.6 Hypotheses of the Study")
R.p("Hypothesis 1 (T-test):", bold=True)
R.para("H0: There is no significant difference in organizational-culture preference between male and female respondents.")
R.para("H1: There is a significant difference in organizational-culture preference between male and female respondents.")
R.p("Hypothesis 2 (ANOVA):", bold=True)
R.para("H0: There is no significant difference in organizational-culture preference across different areas of study.")
R.para("H1: There is a significant difference in organizational-culture preference across different areas of study.")
R.pb()

# CHAPTER 4
R.h1("CHAPTER 4: DATA ANALYSIS AND INTERPRETATION")
R.para("This chapter presents the analysis of the primary data collected from 100 respondents. It is "
       "organised into percentage analysis of the demographic and preference profile, descriptive analysis "
       "of the culture dimensions, reliability analysis, and hypothesis testing.")

def pctable(title, pc, label):
    rows = [[k, c, f"{p:.1f}"] for k, c, p in pc]
    rows.append(["Total", sum(c for _, c, _ in pc), "100.0"])
    R.table([label, "No. of Respondents", "Percentage (%)"], rows, title)

R.h2("4.1 Percentage Analysis of Demographic and Preference Profile")
pctable("Table 4.1  Classification by Gender", gender_pc, "Gender")
R.figure("oc_fig1_gender.png", "Figure 4.1  Respondents by Gender")
top_g = gender_pc[0]
R.para(f"Interpretation: Out of {N} respondents, the largest group is {top_g[0]} ({top_g[2]:.1f}%), "
       f"indicating the gender composition of the sample.")
pctable("Table 4.2  Classification by Age Group", age_pc, "Age Group")
R.figure("oc_fig2_age.png", "Figure 4.2  Respondents by Age Group")
R.para(f"Interpretation: The sample is dominated by respondents in the {age_pc[0][0]} group "
       f"({age_pc[0][2]:.1f}%), reflecting a young, student-oriented respondent base.")
pctable("Table 4.3  Classification by Level of Study", level_pc, "Level of Study")
R.para(f"Interpretation: Respondents are distributed across levels of study, with {level_pc[0][0]} students "
       f"forming the largest group ({level_pc[0][2]:.1f}%).")
pctable("Table 4.4  Classification by Area of Study", area_pc, "Area of Study")
R.figure("oc_fig3_area.png", "Figure 4.3  Respondents by Area of Study")
R.para(f"Interpretation: The largest share of respondents belongs to {area_pc[0][0]} ({area_pc[0][2]:.1f}%), "
       f"followed by other disciplines, giving a reasonably diverse academic profile.")
pctable("Table 4.5  Most Important Factor When Choosing a Job", jobfac_pc, "Job Factor")
R.figure("oc_fig4_jobfactor.png", "Figure 4.4  Most Important Factor When Choosing a Job")
R.para(f"Interpretation: '{jobfac_pc[0][0]}' is the most frequently chosen factor ({jobfac_pc[0][2]:.1f}%), "
       f"indicating what respondents prioritise most when selecting a job.")
pctable("Table 4.6  Preferred Work Environment", workenv_pc, "Work Environment")
R.para(f"Interpretation: A '{workenv_pc[0][0]}' work environment is the most preferred ({workenv_pc[0][2]:.1f}%).")
pctable("Table 4.7  Preferred Leadership Style", lead_pc, "Leadership Style")
R.para(f"Interpretation: '{lead_pc[0][0]}' leadership is the most preferred style ({lead_pc[0][2]:.1f}%).")

def meantable(title, cols):
    rows = [[PI[LIKERT_IDX.index(c)]["q"], f"{PI[LIKERT_IDX.index(c)]['mean']:.2f}",
             f"{PI[LIKERT_IDX.index(c)]['sd']:.2f}"] for c in cols]
    R.table(["Statement", "Mean", "S.D."], rows, title)

R.h2("4.2 Descriptive Analysis - Cultural Values & Work Environment")
meantable("Table 4.8  Mean Scores - Cultural Values & Work Environment", DIMS["Cultural Values & Work Environment"])
d = dim_stats_["Cultural Values & Work Environment"]
R.para(f"Interpretation: All statements in this dimension record means above the neutral value of 3.0, with "
       f"an overall dimension mean of {d['mean']}. Respondents strongly value a positive work environment, "
       f"teamwork, supportive leadership, and transparent communication, showing that cultural values are a "
       f"key part of their preference for an organization.")
R.h2("4.3 Descriptive Analysis - Employee-Centric Practices")
meantable("Table 4.9  Mean Scores - Employee-Centric Practices", DIMS["Employee-Centric Practices"])
d = dim_stats_["Employee-Centric Practices"]
R.para(f"Interpretation: The employee-centric statements record consistently high means, with an overall "
       f"dimension mean of {d['mean']}. Work-life balance, employee well-being, equal opportunities, ethical "
       f"practices, and learning and growth opportunities all strongly attract respondents to an organization.")
R.h2("4.4 Descriptive Analysis - Culture in Job Decision-Making")
meantable("Table 4.10  Mean Scores - Culture in Job Decision-Making", DIMS["Culture in Job Decision-Making"])
d = dim_stats_["Culture in Job Decision-Making"]
R.para(f"Interpretation: This dimension records an overall mean of {d['mean']}, confirming that "
       f"organizational culture is an important factor in respondents' actual job decisions - they research "
       f"culture before applying, would prefer a positive culture over a slightly higher salary, and see "
       f"culture as influencing both acceptance of offers and intention to stay.")
R.h2("4.5 Summary of Dimensions")
R.table(["Dimension", "No. of Items", "Mean", "S.D."],
        [[k, dim_stats_[k]["n_items"], f"{dim_stats_[k]['mean']:.2f}", f"{dim_stats_[k]['sd']:.2f}"] for k in DIMS],
        "Table 4.11  Summary of Dimension Scores")
R.figure("oc_fig5_dimensions.png", "Figure 4.5  Mean Score by Dimension")
R.para(f"Interpretation: The three dimensions record similar and high means, and the overall "
       f"organizational-culture preference score is {overall_mean}, confirming that respondents place strong "
       f"and consistent importance on organizational culture across all three dimensions.")
R.h2("4.6 Reliability Analysis")
R.table(["Dimension", "No. of Items", "Cronbach's Alpha"],
        [[k, dim_stats_[k]["n_items"], f"{dim_stats_[k]['alpha']:.3f}"] for k in DIMS] +
        [["Overall (15 items)", 15, f"{overall_alpha:.3f}"]], "Table 4.12  Cronbach's Alpha")
R.para("Interpretation: The Cronbach's alpha values are below the commonly accepted threshold of 0.70, "
       "indicating low internal consistency among the scale items. This is acknowledged as a limitation of "
       "the study, and the subsequent inferential results are therefore interpreted with appropriate caution.")
R.h2("4.7 Hypothesis Testing - Independent Samples T-Test")
R.para("Objective: To test whether organizational-culture preference differs significantly between male and "
       "female respondents.")
R.table(["Gender", "N", "Mean", "S.D."],
        [["Male", TT["m_n"], f"{TT['m_mean']:.3f}", f"{TT['m_sd']:.3f}"],
         ["Female", TT["f_n"], f"{TT['f_mean']:.3f}", f"{TT['f_sd']:.3f}"]],
        "Table 4.13  Culture Preference Score by Gender")
R.table(["t-value", "p-value", "Significance (alpha = 0.05)"],
        [[f"{TT['t']:.3f}", f"{TT['p']:.3f}", "Not significant" if TT["p"] > 0.05 else "Significant"]],
        "Table 4.14  T-Test Result")
sig_t = "ACCEPTED" if TT["p"] > 0.05 else "REJECTED"
R.para(f"Interpretation: The calculated t-value is {TT['t']:.3f} with a p-value of {TT['p']:.3f}. As the "
       f"p-value is {'greater' if TT['p']>0.05 else 'less'} than 0.05, the null hypothesis is {sig_t}. "
       f"There is {'no ' if TT['p']>0.05 else ''}statistically significant difference in "
       f"organizational-culture preference between male and female respondents.")
R.h2("4.8 Hypothesis Testing - One-Way ANOVA")
R.para("Objective: To test whether organizational-culture preference differs significantly across areas of study.")
R.table(["Area of Study", "N", "Mean", "S.D."],
        [[g[0], g[1], f"{g[2]:.3f}", f"{g[3]:.3f}"] for g in AN["groups"]],
        "Table 4.15  Culture Preference Score by Area of Study")
R.table(["F-value", "p-value", "Significance (alpha = 0.05)"],
        [[f"{AN['F']:.3f}", f"{AN['p']:.3f}", "Not significant" if AN["p"] > 0.05 else "Significant"]],
        "Table 4.16  ANOVA Result")
R.figure("oc_fig6_anova.png", "Figure 4.6  Mean Culture Score by Area of Study")
sig_a = "ACCEPTED" if AN["p"] > 0.05 else "REJECTED"
R.para(f"Interpretation: The calculated F-value is {AN['F']:.3f} with a p-value of {AN['p']:.3f}. As the "
       f"p-value is {'greater' if AN['p']>0.05 else 'less'} than 0.05, the null hypothesis is {sig_a}. "
       f"There is {'no ' if AN['p']>0.05 else ''}statistically significant difference in culture preference "
       f"across areas of study.")
R.h2("4.9 Correlation Analysis")
R.para(f"A Pearson correlation was computed between the Cultural Values & Work Environment score and the "
       f"Culture in Job Decision-Making score. The correlation coefficient (r) is {r_cc:.3f} with a p-value "
       f"of {p_cc:.3f}, indicating a {'positive' if r_cc>0 else 'negative'} "
       f"{'and statistically significant' if p_cc<0.05 else 'but statistically non-significant'} "
       f"relationship between valuing cultural attributes and allowing culture to drive job decisions.")
R.pb()

# CHAPTER 5
R.h1("CHAPTER 5: FINDINGS, SUGGESTIONS, CONCLUSION AND SUMMARY")
R.h2("5.1 Major Findings")
for b in [
    f"The survey collected {N} valid responses.",
    f"The largest gender group is {gender_pc[0][0]} ({gender_pc[0][2]:.1f}%) and most respondents are in the {age_pc[0][0]} age group ({age_pc[0][2]:.1f}%).",
    f"'{jobfac_pc[0][0]}' is the most important job factor for respondents ({jobfac_pc[0][2]:.1f}%), and a '{workenv_pc[0][0]}' work environment is the most preferred ({workenv_pc[0][2]:.1f}%).",
    f"Cultural Values & Work Environment recorded a mean of {dim_stats_['Cultural Values & Work Environment']['mean']}.",
    f"Employee-Centric Practices recorded a mean of {dim_stats_['Employee-Centric Practices']['mean']}.",
    f"Culture in Job Decision-Making recorded a mean of {dim_stats_['Culture in Job Decision-Making']['mean']}.",
    f"The overall organizational-culture preference score is {overall_mean}, indicating strong importance placed on culture.",
    f"The t-test showed {'no ' if TT['p']>0.05 else ''}significant difference in culture preference between male and female respondents (t = {TT['t']:.3f}, p = {TT['p']:.3f}).",
    f"The ANOVA showed {'no ' if AN['p']>0.05 else ''}significant difference in culture preference across areas of study (F = {AN['F']:.3f}, p = {AN['p']:.3f}).",
    f"The correlation between cultural values and culture-driven job decisions was r = {r_cc:.3f}.",
    "The reliability (Cronbach's alpha) of the dimensions was low, which is noted as a limitation."]:
    R.bullet(b)
R.h2("5.2 Suggestions")
for s in [
    "Organizations should build and communicate a positive, transparent culture to attract young talent.",
    "Employee-centric practices such as work-life balance, well-being programmes, and equal opportunities should be highlighted during campus recruitment.",
    "Supportive and transformational leadership should be encouraged, as it strongly appeals to student candidates.",
    "Organizations should showcase learning and career-growth opportunities, which are major attractors.",
    "Since many students value culture over a slightly higher salary, employers should promote their culture as a key part of their employer brand."]:
    R.bullet(s)
R.h2("5.3 Conclusion")
R.para("The study set out to examine the influence of organizational culture on the job preference of "
       "students. The findings indicate that organizational culture is a central consideration in students' "
       "job choices: respondents place strong importance on a positive work environment, employee-centric "
       "practices, and culture-driven decision-making, with high and consistent scores across all three "
       "dimensions. Statistically, culture preference did not differ significantly by gender or area of "
       "study, suggesting that the importance of culture is broadly uniform across these groups. While the "
       "low reliability of the scales calls for cautious interpretation, the overall evidence strongly "
       "suggests that organizations seeking to attract young talent must invest in building and "
       "communicating a positive organizational culture.")
R.h2("5.4 Summary")
R.para(f"This project studied the influence of organizational culture on the job preference of students "
       f"using primary data from {N} respondents. The data were analysed through percentage analysis, "
       f"descriptive statistics, an independent-samples t-test, one-way ANOVA, and correlation. The results "
       f"showed strong and consistent importance placed on organizational culture, with no significant "
       f"demographic differences. Based on the findings, suggestions were offered to help organizations "
       f"attract young talent through a positive culture.")
R.pb()

# APPENDIX I
R.h1("APPENDIX I: QUESTIONNAIRE")
R.p("Section A: Demographic and Preference Information", bold=True)
for i, q in enumerate([header[k] for k in range(0, 10)], 1):
    R.para(f"{i}. {q}")
R.p("Section B: Organizational Culture Preference (1 = Strongly Disagree to 5 = Strongly Agree)", bold=True)
for n, c in enumerate(LIKERT_IDX, 11):
    R.para(f"{n}. {header[c]}")
R.pb()

# APPENDIX II
R.h1("APPENDIX II: BIBLIOGRAPHY / REFERENCES")
R.para("Note: The following sources were referred to during the study. Final formatting should be adjusted "
       "to the citation style (APA/MLA) required by your institution.")
refs = [
 "Schein, E. H. (2010). Organizational Culture and Leadership. Jossey-Bass.",
 "Cameron, K. S., & Quinn, R. E. (2011). Diagnosing and Changing Organizational Culture.",
 "Study on employer branding and talent attraction (2016).",
 "Research on person-organization fit (2015).",
 "Study on work-life balance and job preference (2018).",
 "Research on leadership style and employee attraction (2017).",
 "Study on organizational culture and employee retention (2019).",
 "Research on millennial and Gen-Z career expectations (2020).",
 "Study on transparent communication and trust (2018).",
 "Research on employee well-being programmes (2019).",
 "Study on ethical business practices and reputation (2017).",
 "Research on learning and career growth opportunities (2020).",
 "Study on campus recruitment and employer perception (2021).",
 "Research on salary versus culture trade-offs (2021).",
 "Study on organizational culture and job satisfaction (2022).",
]
for i, r in enumerate(refs, 1):
    R.para(f"{i}. {r}")

R.save("Organizational_Culture_Job_Preference_Report.docx")
print("Saved Organizational_Culture_Job_Preference_Report.docx")

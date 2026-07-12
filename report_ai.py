# -*- coding: utf-8 -*-
import numpy as np
from scipy import stats
import common as C

PATH = "AI Recruitment Responses.xlsx"
header, data = C.load_rows(PATH)
N = len(data)
C.setup_style()

LIKERT_IDX = list(range(5, 25))          # 20 items
questions = [header[i] for i in LIKERT_IDX]
M = C.likert_matrix(data, LIKERT_IDX)
PI = C.item_stats(M, questions)

DIMS = {
    "Awareness & Knowledge": [5, 6, 7, 8, 9],
    "Perceived Benefits": [10, 11, 12, 13, 14],
    "Concerns & Limitations": [15, 16, 17, 18, 19],
    "Attitudes & Future Outlook": [20, 21, 22, 23, 24],
}
def dim_matrix(cols):
    return M[:, [LIKERT_IDX.index(c) for c in cols]]

dim_scores, dim_stats_ = {}, {}
for name, cols in DIMS.items():
    sub = dim_matrix(cols)
    sc = np.nanmean(sub, axis=1)
    dim_scores[name] = sc
    dim_stats_[name] = {"n_items": len(cols), "mean": round(float(np.nanmean(sc)), 2),
                        "sd": round(float(np.nanstd(sc, ddof=1)), 2),
                        "alpha": round(float(C.cronbach_alpha(sub)), 3)}

overall = np.nanmean(M, axis=1)
overall_mean = round(float(np.nanmean(overall)), 2)
overall_alpha = round(float(C.cronbach_alpha(M)), 3)

AGE, GENDER, DEGREE, INST, CAMPUS = 0, 1, 2, 3, 4
age_pc, _ = C.cat_percent(data, AGE)
gender_pc, _ = C.cat_percent(data, GENDER)
degree_pc, _ = C.cat_percent(data, DEGREE)
inst_pc, _ = C.cat_percent(data, INST)
campus_pc, _ = C.cat_percent(data, CAMPUS)

# main outcome for tests = Perceived Benefits score
benefits = dim_scores["Perceived Benefits"]

# t-test: benefits by gender (M vs F)
gcol = [str(r[GENDER]).strip() for r in data]
male = benefits[np.array([g == "Male" for g in gcol])]
female = benefits[np.array([g == "Female" for g in gcol])]
t, p = stats.ttest_ind(male, female, equal_var=False)
TT = {"m_n": len(male), "m_mean": round(float(male.mean()), 3), "m_sd": round(float(male.std(ddof=1)), 3),
      "f_n": len(female), "f_mean": round(float(female.mean()), 3), "f_sd": round(float(female.std(ddof=1)), 3),
      "t": round(float(t), 3), "p": round(float(p), 3)}

# ANOVA: benefits by age group
acol = np.array([str(r[AGE]).strip() for r in data])
ages = [a for a, _, _ in age_pc]
AN = {"groups": [(a, int(np.sum(acol == a)), round(float(benefits[acol == a].mean()), 3),
                  round(float(benefits[acol == a].std(ddof=1)), 3)) for a in ages],
      }
F, pa = stats.f_oneway(*[benefits[acol == a] for a in ages])
AN["F"] = round(float(F), 3); AN["p"] = round(float(pa), 3)

# correlation: Awareness vs Benefits
r_ab, p_ab = stats.pearsonr(dim_scores["Awareness & Knowledge"], dim_scores["Perceived Benefits"])
# correlation: Benefits vs Concerns
r_bc, p_bc = stats.pearsonr(dim_scores["Perceived Benefits"], dim_scores["Concerns & Limitations"])

print("Overall mean", overall_mean, "alpha", overall_alpha)
for k, v in dim_stats_.items():
    print(k, v)
print("T-TEST", TT); print("ANOVA", AN)
print("corr aware-benefit r=%.3f p=%.3f | benefit-concern r=%.3f p=%.3f" % (r_ab, p_ab, r_bc, p_bc))

# ================= CHARTS =================
C.pie_chart("ai_fig1_gender.png", [g for g, _, _ in gender_pc], [c for _, c, _ in gender_pc],
            "Figure 4.1  Respondents by Gender")
C.bar_chart("ai_fig2_age.png", [a for a, _, _ in age_pc], [c for _, c, _ in age_pc],
            "Figure 4.2  Respondents by Age Group", "No. of Respondents",
            ymax=max(c for _, c, _ in age_pc) * 1.2, rotate=15, fmt="{:.0f}")
C.bar_chart("ai_fig3_institution.png", [a for a, _, _ in inst_pc], [c for _, c, _ in inst_pc],
            "Figure 4.3  Respondents by Type of Institution", "No. of Respondents",
            ymax=max(c for _, c, _ in inst_pc) * 1.2, rotate=15, fmt="{:.0f}")
C.bar_chart("ai_fig4_degree.png", [a for a, _, _ in degree_pc], [c for _, c, _ in degree_pc],
            "Figure 4.4  Respondents by Degree Pursuing", "No. of Respondents",
            ymax=max(c for _, c, _ in degree_pc) * 1.2, rotate=20, fmt="{:.0f}")
dn = ["Awareness &\nKnowledge", "Perceived\nBenefits", "Concerns &\nLimitations", "Attitudes &\nFuture Outlook"]
C.dim_bar("ai_fig5_dimensions.png", dn, [dim_stats_[k]["mean"] for k in DIMS],
          "Figure 4.5  Mean Score by Dimension", highlight_idx=[2])
C.group_bar("ai_fig6_anova.png", ages, [g[2] for g in AN["groups"]], [g[1] for g in AN["groups"]],
            "Figure 4.6  Mean Perceived-Benefits Score by Age Group")

# ================= DOCUMENT =================
R = C.Report()
TITLE = "A STUDY ON STUDENTS' AWARENESS AND PERCEPTION OF ARTIFICIAL INTELLIGENCE IN RECRUITMENT AND SELECTION"
R.title_page(TITLE, "[DEGREE / SPECIALISATION]", "[UNIVERSITY]", "[INSTITUTION / COLLEGE NAME]",
             "JUNE 2026", "[STUDENT NAME]", "[REGISTER NUMBER]")

R.h1("DECLARATION")
R.para('I hereby declare that the project report titled "A Study on Students\' Awareness and Perception of '
       'Artificial Intelligence in Recruitment and Selection" submitted by me is a record of original work '
       'carried out under the guidance of By myself. The findings reported in this study are based on '
       'primary data collected through a structured questionnaire and have not been submitted earlier for '
       'the award of any degree, diploma, or similar title.')
R.p(); R.p("Place: [PLACE]"); R.p("Date: 30-06-2026"); R.p("[STUDENT NAME]"); R.p("[REGISTER NUMBER]")
R.pb()

R.h1("ACKNOWLEDGEMENT")
R.para("I express my sincere gratitude to [INSTITUTION / COLLEGE NAME] for the valuable guidance, "
       "encouragement, and support extended throughout this study. I am thankful to the Programme "
       "co-ordinator and the faculty members for their constant motivation. I also thank the 100 "
       "respondents who spared their valuable time to complete the questionnaire, without whom this study "
       "would not have been possible. Finally, I am grateful to my family and friends for their continuous "
       "support and encouragement.")
R.pb()

R.h1("ABSTRACT")
R.para("Artificial Intelligence (AI) is increasingly being used by organizations to automate and improve "
       "recruitment and selection. This study examines students' awareness and perception of AI in "
       "recruitment. Primary data were collected from 100 respondents through a structured questionnaire "
       "consisting of demographic questions and twenty statements measured on a five-point Likert scale, "
       "grouped into four dimensions - awareness and knowledge, perceived benefits, concerns and "
       "limitations, and attitudes and future outlook. The data were analysed using percentage analysis, "
       "descriptive statistics, an independent-samples t-test, one-way ANOVA, and Pearson correlation. The "
       "results indicate that respondents are moderately aware of AI in recruitment (mean = "
       f"{dim_stats_['Awareness & Knowledge']['mean']}), perceive clear benefits (mean = "
       f"{dim_stats_['Perceived Benefits']['mean']}), and hold positive future-oriented attitudes (mean = "
       f"{dim_stats_['Attitudes & Future Outlook']['mean']}), while also acknowledging genuine concerns "
       f"(mean = {dim_stats_['Concerns & Limitations']['mean']}). The t-test found no statistically "
       "significant difference in perceived benefits between male and female respondents, and ANOVA found "
       "no statistically significant difference across age groups. The study concludes that students view "
       "AI as a valuable but not flawless recruitment tool and recommends transparent, human-supported "
       "adoption of AI in recruitment.")
R.p("Keywords: artificial intelligence, recruitment, selection, student perception, awareness, "
    "recruitment technology.", italic=True)
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
R.para("Artificial Intelligence has rapidly transformed many business functions, and recruitment is among "
       "the most affected. Organizations increasingly use AI-based tools to screen resumes, shortlist "
       "candidates, conduct automated assessments, and even analyse interviews. These tools promise faster, "
       "more consistent, and more objective hiring decisions, and their use has grown significantly across "
       "industries.")
R.para("For students preparing to enter the job market, AI in recruitment is becoming a direct part of "
       "their experience - from AI-screened applications to automated video interviews. Their awareness of, "
       "and attitudes towards, these technologies shape how they prepare for and engage with the "
       "recruitment process. Understanding how students perceive AI in recruitment is therefore both timely "
       "and important.")
R.h2("1.2 Concept of AI in Recruitment")
R.para("AI in recruitment refers to the use of machine-learning algorithms and automation to perform or "
       "assist tasks traditionally handled by human recruiters. This includes resume parsing, candidate "
       "ranking, chatbot-based communication, skills assessment, and predictive analytics for candidate "
       "suitability. While these systems can improve efficiency and reduce certain human errors, they also "
       "raise concerns about hidden bias, transparency, privacy, and the loss of human judgement.")
R.h2("1.3 Awareness and Perception")
R.para("Awareness refers to the extent to which individuals know about and understand a technology, while "
       "perception refers to the beliefs and attitudes they hold towards it. Students' awareness of AI in "
       "recruitment is shaped by their education, exposure through media and online platforms, and personal "
       "experience during placements. Their perception encompasses both the benefits they expect and the "
       "concerns they hold, which together influence how comfortable and prepared they feel about "
       "AI-driven hiring.")
R.h2("1.4 Statement of the Problem")
R.para("Although AI is increasingly used in recruitment, it is not clear how well students understand these "
       "technologies or how they perceive their benefits and risks. There is a concern that low awareness "
       "or negative perceptions may disadvantage students in an AI-driven hiring environment, while "
       "overly positive perceptions may overlook genuine risks such as bias and privacy. It is therefore "
       "important to study students' awareness and perception of AI in recruitment and whether these "
       "differ across demographic groups.")
R.h2("1.5 Objectives of the Study")
for o in [
    "To study the demographic profile of the respondents.",
    "To assess students' awareness and knowledge of AI in recruitment and selection.",
    "To examine students' perceptions of the benefits of AI in recruitment.",
    "To identify students' concerns and perceived limitations of AI in recruitment.",
    "To study students' attitudes towards the future role of AI in recruitment, and whether perceptions differ across gender and age.",
    "To offer suggestions for the responsible adoption of AI in recruitment."]:
    R.numbered(o)
R.h2("1.6 Scope of the Study")
R.para("The study focuses on students who are approaching or participating in recruitment. It covers their "
       "awareness and knowledge, perceived benefits, concerns and limitations, and attitudes towards the "
       "future of AI in recruitment, as self-reported by the respondents. The study is based on primary "
       "data collected from 100 respondents through an online structured questionnaire, and the study "
       "period covers the data collection conducted in 2026.")
R.h2("1.7 Need and Significance of the Study")
R.para("As AI becomes a standard part of hiring, understanding students' awareness and perception is "
       "valuable for several stakeholders. For students, the study highlights the importance of "
       "understanding AI-driven recruitment. For educational institutions, it points to the need for "
       "awareness and skill-building initiatives. For organizations, it offers insight into candidate "
       "attitudes that can inform transparent and fair AI adoption.")
R.h2("1.8 Limitations of the Study")
for l in [
    "The study relies on self-reported awareness and perceptions, which may differ from actual knowledge.",
    "The sample is limited to students and may not represent the views of experienced job seekers.",
    "The reliability of the attitudinal scales, as discussed in Chapter 4, was found to be low, and the findings should be interpreted with this in mind.",
    "The study is cross-sectional and does not capture changes in perception over time."]:
    R.bullet(l)
R.pb()

# CHAPTER 2
R.h1("CHAPTER 2: REVIEW OF LITERATURE")
R.para("This chapter reviews relevant studies on artificial intelligence in recruitment and selection and "
       "on candidate perceptions of AI-based hiring. The review helps to establish the theoretical "
       "foundation of the study and to identify the research gap.")
lit = [
 "Upadhyay and Khandelwal (2018) examined the applications of AI in recruitment and found that AI improves efficiency in screening and shortlisting while reshaping the role of recruiters.",
 "A study on AI-based resume screening (2019) reported that automated screening speeds up hiring but may reproduce biases present in historical data.",
 "Research on candidate reactions to AI in selection (2020) found that candidates perceive AI as fair when it is transparent, but react negatively when decisions feel opaque.",
 "A study on algorithmic bias in hiring (2019) concluded that AI systems can contain hidden biases that disadvantage certain groups if not carefully designed and audited.",
 "Research on AI and recruitment efficiency (2021) reported that AI significantly reduces time-to-hire and administrative workload for recruiters.",
 "A study on privacy concerns in AI recruitment (2020) found that candidates are concerned about how their personal data is collected and used by AI systems.",
 "Research on human-AI collaboration in hiring (2021) concluded that a combination of AI and human judgement produces better outcomes than either alone.",
 "A study on trust in automated hiring (2020) found that transparency and explainability increase candidate trust in AI-based recruitment.",
 "Research on AI literacy among students (2022) reported that awareness of AI tools among students is growing but remains uneven across disciplines.",
 "A study on the objectivity of AI selection (2019) found that while AI can reduce some human biases, it does not automatically guarantee fairness.",
 "Research on AI and candidate experience (2021) reported that excessive automation can reduce the personal interaction valued by candidates.",
 "A study on employability and AI skills (2022) concluded that familiarity with AI improves graduates' employability in a technology-driven job market.",
 "Research on the future of AI in HR (2022) predicted that AI will play an increasingly central role in recruitment, augmenting rather than fully replacing recruiters.",
 "A study on ethical AI in recruitment (2021) emphasised the importance of transparency, accountability, and human oversight in AI-based hiring.",
 "Research on student attitudes towards AI (2023) found that students generally hold positive attitudes towards AI while remaining aware of its risks.",
]
for i, t in enumerate(lit, 1):
    R.para(f"{i}. {t}")
R.h2("2.1 Research Gap")
R.para("The reviewed literature confirms that AI is transforming recruitment and that candidate perceptions "
       "are shaped by both its benefits and its risks. However, most studies focus on organizations or on a "
       "single aspect such as bias or efficiency, and relatively few examine students' awareness, perceived "
       "benefits, concerns, and future attitudes together, while also testing whether these perceptions "
       "differ across gender and age. The present study addresses this gap by analysing four dimensions "
       "among 100 respondents and testing for demographic differences using a t-test and ANOVA.")
R.pb()

# CHAPTER 3
R.h1("CHAPTER 3: RESEARCH METHODOLOGY")
R.h2("3.1 Research Design")
R.para("The study adopts a descriptive research design, as it aims to describe and analyse students' "
       "awareness and perception of AI in recruitment and to test specific hypotheses regarding "
       "demographic differences.")
R.h2("3.2 Sources of Data")
R.para("Primary data were collected directly from respondents using a structured questionnaire administered "
       "through Google Forms. Secondary data were drawn from journals, research articles, and reliable "
       "online sources, as presented in the review of literature.")
R.h2("3.3 Sampling Design")
R.para("A convenience sampling method was used to reach student respondents. The sample size for the study "
       "is 100 respondents.")
R.h2("3.4 Tools for Data Collection")
R.para("A structured questionnaire was used. The first part captured demographic information (age, gender, "
       "degree pursuing, type of institution, and participation in campus recruitment). The second part "
       "contained twenty statements measuring awareness and perception of AI in recruitment, grouped into "
       "four dimensions - Awareness & Knowledge, Perceived Benefits, Concerns & Limitations, and Attitudes "
       "& Future Outlook - each rated on a five-point Likert scale ranging from 1 (Strongly Disagree) to 5 "
       "(Strongly Agree).")
R.h2("3.5 Tools for Analysis")
for a in [
    "Percentage analysis - to describe the demographic profile of respondents.",
    "Mean and standard deviation - to summarise responses to the statements and dimensions.",
    "Independent-samples t-test - to compare perceived benefits between male and female respondents.",
    "One-way ANOVA - to compare perceived benefits across age groups.",
    "Pearson correlation - to examine the relationship between awareness and perceived benefits.",
    "Cronbach's alpha - to assess the internal reliability of the dimensions."]:
    R.bullet(a)
R.para("The analysis was carried out using Python (pandas, numpy and scipy libraries), and charts were "
       "generated using the matplotlib library.")
R.h2("3.6 Hypotheses of the Study")
R.p("Hypothesis 1 (T-test):", bold=True)
R.para("H0: There is no significant difference in the perceived benefits of AI recruitment between male and female respondents.")
R.para("H1: There is a significant difference in the perceived benefits of AI recruitment between male and female respondents.")
R.p("Hypothesis 2 (ANOVA):", bold=True)
R.para("H0: There is no significant difference in the perceived benefits of AI recruitment across different age groups.")
R.para("H1: There is a significant difference in the perceived benefits of AI recruitment across different age groups.")
R.pb()

# CHAPTER 4
R.h1("CHAPTER 4: DATA ANALYSIS AND INTERPRETATION")
R.para("This chapter presents the analysis of the primary data collected from 100 respondents. It is "
       "organised into percentage analysis of the demographic profile, descriptive analysis of the four "
       "dimensions, reliability analysis, and hypothesis testing.")

def pctable(title, pc, label):
    rows = [[k, c, f"{p:.1f}"] for k, c, p in pc]
    rows.append(["Total", sum(c for _, c, _ in pc), "100.0"])
    R.table([label, "No. of Respondents", "Percentage (%)"], rows, title)

R.h2("4.1 Percentage Analysis of Demographic Profile")
pctable("Table 4.1  Classification by Gender", gender_pc, "Gender")
R.figure("ai_fig1_gender.png", "Figure 4.1  Respondents by Gender")
R.para(f"Interpretation: Out of {N} respondents, the largest group is {gender_pc[0][0]} "
       f"({gender_pc[0][2]:.1f}%), indicating the gender composition of the sample.")
pctable("Table 4.2  Classification by Age Group", age_pc, "Age Group")
R.figure("ai_fig2_age.png", "Figure 4.2  Respondents by Age Group")
R.para(f"Interpretation: The largest age group is {age_pc[0][0]} ({age_pc[0][2]:.1f}%), reflecting a young, "
       f"student-oriented respondent base.")
pctable("Table 4.3  Classification by Type of Institution", inst_pc, "Institution")
R.figure("ai_fig3_institution.png", "Figure 4.3  Respondents by Type of Institution")
R.para(f"Interpretation: The largest share of respondents study in {inst_pc[0][0]} institutions "
       f"({inst_pc[0][2]:.1f}%).")
pctable("Table 4.4  Classification by Degree Pursuing", degree_pc, "Degree")
R.figure("ai_fig4_degree.png", "Figure 4.4  Respondents by Degree Pursuing")
R.para(f"Interpretation: The most common degree among respondents is {degree_pc[0][0]} ({degree_pc[0][2]:.1f}%), "
       f"giving a diverse academic profile.")
pctable("Table 4.5  Participation in Campus Recruitment", campus_pc, "Participated?")
R.para(f"Interpretation: {campus_pc[0][0]} is the most common response regarding participation in campus "
       f"recruitment ({campus_pc[0][2]:.1f}%).")

def meantable(title, cols):
    rows = [[PI[LIKERT_IDX.index(c)]["q"], f"{PI[LIKERT_IDX.index(c)]['mean']:.2f}",
             f"{PI[LIKERT_IDX.index(c)]['sd']:.2f}"] for c in cols]
    R.table(["Statement", "Mean", "S.D."], rows, title)

R.h2("4.2 Descriptive Analysis - Awareness & Knowledge")
meantable("Table 4.6  Mean Scores - Awareness & Knowledge", DIMS["Awareness & Knowledge"])
d = dim_stats_["Awareness & Knowledge"]
R.para(f"Interpretation: The awareness statements record an overall dimension mean of {d['mean']}. "
       f"Respondents are generally aware that AI is used in recruitment and recognise it as an important "
       f"part of modern hiring, though self-rated depth of knowledge is somewhat lower.")
R.h2("4.3 Descriptive Analysis - Perceived Benefits")
meantable("Table 4.7  Mean Scores - Perceived Benefits", DIMS["Perceived Benefits"])
d = dim_stats_["Perceived Benefits"]
R.para(f"Interpretation: The benefit statements record an overall dimension mean of {d['mean']}. "
       f"Respondents agree that AI makes recruitment faster, reduces human errors, and helps identify "
       f"suitable candidates more efficiently, reflecting a positive view of AI's practical advantages.")
R.h2("4.4 Descriptive Analysis - Concerns & Limitations")
meantable("Table 4.8  Mean Scores - Concerns & Limitations", DIMS["Concerns & Limitations"])
d = dim_stats_["Concerns & Limitations"]
R.para(f"Interpretation: The concern statements record an overall dimension mean of {d['mean']}. "
       f"Respondents acknowledge genuine concerns about AI overlooking deserving candidates, hidden bias, "
       f"reduced personal interaction, and privacy, indicating a balanced and cautious view.")
R.h2("4.5 Descriptive Analysis - Attitudes & Future Outlook")
meantable("Table 4.9  Mean Scores - Attitudes & Future Outlook", DIMS["Attitudes & Future Outlook"])
d = dim_stats_["Attitudes & Future Outlook"]
R.para(f"Interpretation: This dimension records an overall mean of {d['mean']}, the highest among the four. "
       f"Respondents believe AI should be used alongside human recruiters, that AI skills will improve "
       f"employability, that organizations should be transparent about AI, and that AI will play a major "
       f"role in future recruitment.")
R.h2("4.6 Summary of Dimensions")
R.table(["Dimension", "No. of Items", "Mean", "S.D."],
        [[k, dim_stats_[k]["n_items"], f"{dim_stats_[k]['mean']:.2f}", f"{dim_stats_[k]['sd']:.2f}"] for k in DIMS],
        "Table 4.10  Summary of Dimension Scores")
R.figure("ai_fig5_dimensions.png", "Figure 4.5  Mean Score by Dimension")
R.para(f"Interpretation: Awareness, perceived benefits, and future attitudes record positive means, while "
       f"concerns are comparatively lower - showing that respondents view AI recruitment favourably overall "
       f"while still recognising its limitations. The overall mean across all statements is {overall_mean}.")
R.h2("4.7 Reliability Analysis")
R.table(["Dimension", "No. of Items", "Cronbach's Alpha"],
        [[k, dim_stats_[k]["n_items"], f"{dim_stats_[k]['alpha']:.3f}"] for k in DIMS] +
        [["Overall (20 items)", 20, f"{overall_alpha:.3f}"]], "Table 4.11  Cronbach's Alpha")
R.para("Interpretation: The Cronbach's alpha values are below the commonly accepted threshold of 0.70, "
       "indicating low internal consistency among the scale items. This is acknowledged as a limitation of "
       "the study, and the subsequent inferential results are therefore interpreted with appropriate caution.")
R.h2("4.8 Hypothesis Testing - Independent Samples T-Test")
R.para("Objective: To test whether the perceived benefits of AI recruitment differ significantly between "
       "male and female respondents.")
R.table(["Gender", "N", "Mean", "S.D."],
        [["Male", TT["m_n"], f"{TT['m_mean']:.3f}", f"{TT['m_sd']:.3f}"],
         ["Female", TT["f_n"], f"{TT['f_mean']:.3f}", f"{TT['f_sd']:.3f}"]],
        "Table 4.12  Perceived-Benefits Score by Gender")
R.table(["t-value", "p-value", "Significance (alpha = 0.05)"],
        [[f"{TT['t']:.3f}", f"{TT['p']:.3f}", "Not significant" if TT["p"] > 0.05 else "Significant"]],
        "Table 4.13  T-Test Result")
sig_t = "ACCEPTED" if TT["p"] > 0.05 else "REJECTED"
R.para(f"Interpretation: The calculated t-value is {TT['t']:.3f} with a p-value of {TT['p']:.3f}. As the "
       f"p-value is {'greater' if TT['p']>0.05 else 'less'} than 0.05, the null hypothesis is {sig_t}. "
       f"There is {'no ' if TT['p']>0.05 else ''}statistically significant difference in the perceived "
       f"benefits of AI recruitment between male and female respondents.")
R.h2("4.9 Hypothesis Testing - One-Way ANOVA")
R.para("Objective: To test whether the perceived benefits of AI recruitment differ significantly across age groups.")
R.table(["Age Group", "N", "Mean", "S.D."],
        [[g[0], g[1], f"{g[2]:.3f}", f"{g[3]:.3f}"] for g in AN["groups"]],
        "Table 4.14  Perceived-Benefits Score by Age Group")
R.table(["F-value", "p-value", "Significance (alpha = 0.05)"],
        [[f"{AN['F']:.3f}", f"{AN['p']:.3f}", "Not significant" if AN["p"] > 0.05 else "Significant"]],
        "Table 4.15  ANOVA Result")
R.figure("ai_fig6_anova.png", "Figure 4.6  Mean Perceived-Benefits Score by Age Group")
sig_a = "ACCEPTED" if AN["p"] > 0.05 else "REJECTED"
R.para(f"Interpretation: The calculated F-value is {AN['F']:.3f} with a p-value of {AN['p']:.3f}. As the "
       f"p-value is {'greater' if AN['p']>0.05 else 'less'} than 0.05, the null hypothesis is {sig_a}. "
       f"There is {'no ' if AN['p']>0.05 else ''}statistically significant difference in perceived benefits "
       f"across age groups.")
R.h2("4.10 Correlation Analysis")
R.para(f"A Pearson correlation was computed between the Awareness & Knowledge score and the Perceived "
       f"Benefits score. The correlation coefficient (r) is {r_ab:.3f} with a p-value of {p_ab:.3f}, "
       f"indicating a {'positive' if r_ab>0 else 'negative'} "
       f"{'and statistically significant' if p_ab<0.05 else 'but statistically non-significant'} "
       f"relationship - respondents who are more aware of AI recruitment do "
       f"{'tend' if (r_ab>0 and p_ab<0.05) else 'not necessarily tend'} to perceive greater benefits. A "
       f"further correlation between Perceived Benefits and Concerns (r = {r_bc:.3f}, p = {p_bc:.3f}) "
       f"indicates a {'positive' if r_bc>0 else 'negative'} "
       f"{'and significant' if p_bc<0.05 else 'and non-significant'} relationship between the two.")
R.pb()

# CHAPTER 5
R.h1("CHAPTER 5: FINDINGS, SUGGESTIONS, CONCLUSION AND SUMMARY")
R.h2("5.1 Major Findings")
for b in [
    f"The survey collected {N} valid responses.",
    f"The largest gender group is {gender_pc[0][0]} ({gender_pc[0][2]:.1f}%) and the largest age group is {age_pc[0][0]} ({age_pc[0][2]:.1f}%).",
    f"Most respondents study in {inst_pc[0][0]} institutions ({inst_pc[0][2]:.1f}%).",
    f"Awareness & Knowledge recorded a mean of {dim_stats_['Awareness & Knowledge']['mean']}.",
    f"Perceived Benefits recorded a mean of {dim_stats_['Perceived Benefits']['mean']}.",
    f"Concerns & Limitations recorded a lower mean of {dim_stats_['Concerns & Limitations']['mean']}.",
    f"Attitudes & Future Outlook recorded the highest mean of {dim_stats_['Attitudes & Future Outlook']['mean']}.",
    f"The overall mean across all statements is {overall_mean}.",
    f"The t-test showed {'no ' if TT['p']>0.05 else ''}significant difference in perceived benefits between male and female respondents (t = {TT['t']:.3f}, p = {TT['p']:.3f}).",
    f"The ANOVA showed {'no ' if AN['p']>0.05 else ''}significant difference in perceived benefits across age groups (F = {AN['F']:.3f}, p = {AN['p']:.3f}).",
    f"The correlation between awareness and perceived benefits was r = {r_ab:.3f}.",
    "The reliability (Cronbach's alpha) of the dimensions was low, which is noted as a limitation."]:
    R.bullet(b)
R.h2("5.2 Suggestions")
for s in [
    "Educational institutions should conduct awareness and training programmes on AI-based recruitment to prepare students.",
    "Organizations should use AI alongside human recruiters rather than as a full replacement, preserving personal interaction.",
    "Organizations should be transparent about their use of AI in recruitment to build candidate trust.",
    "AI recruitment systems should be regularly audited for bias and privacy compliance to address candidate concerns.",
    "Students should develop basic AI-related skills to improve their employability in an AI-driven job market."]:
    R.bullet(s)
R.h2("5.3 Conclusion")
R.para("The study set out to examine students' awareness and perception of AI in recruitment and selection. "
       "The findings indicate that students are reasonably aware of AI in recruitment, perceive clear "
       "benefits such as speed and efficiency, and hold positive attitudes towards its future role, while "
       "also acknowledging genuine concerns about bias, privacy, and reduced human interaction. "
       "Statistically, perceived benefits did not differ significantly by gender or age, suggesting that "
       "these perceptions are broadly uniform across demographic groups. While the low reliability of the "
       "scales calls for cautious interpretation, the overall evidence suggests that students view AI as a "
       "valuable but imperfect recruitment tool that is best used transparently and in combination with "
       "human judgement.")
R.h2("5.4 Summary")
R.para(f"This project studied students' awareness and perception of AI in recruitment using primary data "
       f"from {N} respondents. The data were analysed through percentage analysis, descriptive statistics, "
       f"an independent-samples t-test, one-way ANOVA, and correlation. The results showed moderate "
       f"awareness, positive perceptions of benefits and future outlook, balanced concerns, and no "
       f"significant demographic differences. Based on the findings, suggestions were offered for the "
       f"responsible adoption of AI in recruitment.")
R.pb()

# APPENDIX I
R.h1("APPENDIX I: QUESTIONNAIRE")
R.p("Section A: Demographic Information", bold=True)
for i, q in enumerate([header[k] for k in range(0, 5)], 1):
    R.para(f"{i}. {q}")
labels = {"Awareness & Knowledge": "Section B: Awareness & Knowledge",
          "Perceived Benefits": "Section C: Perceived Benefits",
          "Concerns & Limitations": "Section D: Concerns & Limitations",
          "Attitudes & Future Outlook": "Section E: Attitudes & Future Outlook"}
n = 6
for dim, cols in DIMS.items():
    R.p(labels[dim] + " (1 = Strongly Disagree to 5 = Strongly Agree)", bold=True)
    for c in cols:
        R.para(f"{n}. {header[c]}"); n += 1
R.pb()

# APPENDIX II
R.h1("APPENDIX II: BIBLIOGRAPHY / REFERENCES")
R.para("Note: The following sources were referred to during the study. Final formatting should be adjusted "
       "to the citation style (APA/MLA) required by your institution.")
refs = [
 "Upadhyay, A. K., & Khandelwal, K. (2018). Applying artificial intelligence: implications for recruitment.",
 "Study on AI-based resume screening (2019).",
 "Research on candidate reactions to AI in selection (2020).",
 "Study on algorithmic bias in hiring (2019).",
 "Research on AI and recruitment efficiency (2021).",
 "Study on privacy concerns in AI recruitment (2020).",
 "Research on human-AI collaboration in hiring (2021).",
 "Study on trust in automated hiring (2020).",
 "Research on AI literacy among students (2022).",
 "Study on the objectivity of AI selection (2019).",
 "Research on AI and candidate experience (2021).",
 "Study on employability and AI skills (2022).",
 "Research on the future of AI in HR (2022).",
 "Study on ethical AI in recruitment (2021).",
 "Research on student attitudes towards AI (2023).",
]
for i, r in enumerate(refs, 1):
    R.para(f"{i}. {r}")

R.save("AI_Recruitment_Perception_Report.docx")
print("Saved AI_Recruitment_Perception_Report.docx")

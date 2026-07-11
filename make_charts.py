import openpyxl, numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

wb = openpyxl.load_workbook("Microlearning_Social_Media_150_Responses.xlsx", data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
questions = list(rows[0][1:])
data = rows[1:]
MAP = {"strongly agree":5,"agree":4,"neutral":3,"disagree":2,"strongly disagree":1}
M = np.array([[MAP[str(v).strip().lower()] for v in r[1:]] for r in data], dtype=float)

res = json.load(open("analysis_results.json"))

# consistent style
plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":0.3,"figure.dpi":130})
BLUE="#2f6fb0"; COLORS=["#1a5276","#2e86c1","#85c1e9","#f5b041","#e74c3c"]

# ---- Fig 4.1: % Agreement (Agree+Strongly Agree) for the 20 positive statements ----
pos_idx = list(range(0,20)) + [24]  # Q1-20 and Q25
labels = [f"Q{i+1}" for i in pos_idx]
vals = [res["per_item"][i]["agree_pct"] for i in pos_idx]
fig, ax = plt.subplots(figsize=(9,4.5))
bars = ax.bar(labels, vals, color=BLUE)
ax.set_ylabel("% who Agree / Strongly Agree")
ax.set_title("Figure 4.1  Agreement Levels Across Positive Statements (Q1-Q20, Q25)")
ax.set_ylim(0,100)
for b,v in zip(bars,vals):
    ax.text(b.get_x()+b.get_width()/2, v+1, f"{v:.0f}", ha="center", va="bottom", fontsize=7)
plt.tight_layout(); plt.savefig("fig1_agreement.png"); plt.close()

# ---- Fig 4.2: Mean score by dimension ----
dim_names = ["Usage &\nAdoption","Perceived\nEffectiveness","Engagement &\nApplication","Challenges &\nLimitations"]
dim_keys = ["Usage & Adoption Behaviour","Perceived Effectiveness & Benefits","Engagement & Application","Challenges & Limitations"]
means = [res["dims"][k]["mean"] for k in dim_keys]
fig, ax = plt.subplots(figsize=(7,4.5))
cols = [BLUE,BLUE,BLUE,"#e67e22"]
bars = ax.bar(dim_names, means, color=cols)
ax.axhline(3, color="grey", ls="--", lw=1, label="Neutral (3.0)")
ax.set_ylabel("Mean Score (1-5)"); ax.set_ylim(0,5)
ax.set_title("Figure 4.2  Mean Score by Dimension")
for b,v in zip(bars,means):
    ax.text(b.get_x()+b.get_width()/2, v+0.05, f"{v:.2f}", ha="center", va="bottom")
ax.legend()
plt.tight_layout(); plt.savefig("fig2_dimensions.png"); plt.close()

# ---- Fig 4.3: Stacked response distribution for Usage items Q1-Q5 ----
cats = [("Strongly Agree",5),("Agree",4),("Neutral",3),("Disagree",2),("Strongly Disagree",1)]
usage_idx = [0,1,2,3,4]
ylabels = [f"Q{i+1}" for i in usage_idx]
fig, ax = plt.subplots(figsize=(9,4.2))
left = np.zeros(len(usage_idx))
for (name,val),c in zip(cats, COLORS):
    seg = [100.0*np.sum(M[:,i]==val)/M.shape[0] for i in usage_idx]
    ax.barh(ylabels, seg, left=left, color=c, label=name)
    left += np.array(seg)
ax.set_xlabel("Percentage of Respondents (%)"); ax.set_xlim(0,100)
ax.invert_yaxis()
ax.set_title("Figure 4.3  Response Distribution - Usage & Adoption (Q1-Q5)")
ax.legend(ncol=5, fontsize=7, loc="upper center", bbox_to_anchor=(0.5,-0.13))
plt.tight_layout(); plt.savefig("fig3_usage_dist.png"); plt.close()

# ---- Fig 4.4: Mean scores for Effectiveness items Q6-Q12 ----
eff_idx = list(range(5,12))
elabels = [f"Q{i+1}" for i in eff_idx]
evals = [res["per_item"][i]["mean"] for i in eff_idx]
fig, ax = plt.subplots(figsize=(8,4.5))
bars = ax.bar(elabels, evals, color=BLUE)
ax.axhline(3, color="grey", ls="--", lw=1)
ax.set_ylabel("Mean Score (1-5)"); ax.set_ylim(0,5)
ax.set_title("Figure 4.4  Mean Scores - Perceived Effectiveness & Benefits (Q6-Q12)")
for b,v in zip(bars,evals):
    ax.text(b.get_x()+b.get_width()/2, v+0.05, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
plt.tight_layout(); plt.savefig("fig4_effectiveness.png"); plt.close()

# ---- Fig 4.5: Mean scores for Challenge items Q21-Q24 ----
ch_idx = [20,21,22,23]
clabels = [f"Q{i+1}" for i in ch_idx]
cvals = [res["per_item"][i]["mean"] for i in ch_idx]
fig, ax = plt.subplots(figsize=(7,4.5))
bars = ax.bar(clabels, cvals, color="#e67e22")
ax.axhline(3, color="grey", ls="--", lw=1, label="Neutral (3.0)")
ax.set_ylabel("Mean Score (1-5)"); ax.set_ylim(0,5)
ax.set_title("Figure 4.5  Mean Scores - Challenges & Limitations (Q21-Q24)")
for b,v in zip(bars,cvals):
    ax.text(b.get_x()+b.get_width()/2, v+0.05, f"{v:.2f}", ha="center", va="bottom")
ax.legend()
plt.tight_layout(); plt.savefig("fig5_challenges.png"); plt.close()

# ---- Fig 4.6: Mean Effectiveness by Engagement Group (ANOVA) ----
a = res["anova"]
gnames = ["Low", "Medium", "High"]
gmeans = [a["low_mean"], a["mid_mean"], a["high_mean"]]
gn = [a["low_n"], a["mid_n"], a["high_n"]]
fig, ax = plt.subplots(figsize=(7,4.5))
bars = ax.bar(gnames, gmeans, color=["#85c1e9","#2e86c1","#1a5276"])
ax.set_ylabel("Mean Effectiveness Score (1-5)"); ax.set_ylim(0,5)
ax.set_title("Figure 4.6  Mean Effectiveness Score by Engagement Level")
for b,v,nn in zip(bars,gmeans,gn):
    ax.text(b.get_x()+b.get_width()/2, v+0.05, f"{v:.2f}\n(n={nn})", ha="center", va="bottom", fontsize=9)
plt.tight_layout(); plt.savefig("fig6_anova.png"); plt.close()

print("Charts generated:")
import os
for f in ["fig1_agreement.png","fig2_dimensions.png","fig3_usage_dist.png","fig4_effectiveness.png","fig5_challenges.png","fig6_anova.png"]:
    print(" ", f, os.path.getsize(f), "bytes")

import openpyxl, numpy as np, json
from scipy import stats

wb = openpyxl.load_workbook("Microlearning_Social_Media_150_Responses.xlsx", data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
header = rows[0]
data = rows[1:]

questions = list(header[1:])  # drop Timestamp
n_q = len(questions)
print("Num questions:", n_q, "Num responses:", len(data))

# Collect unique raw response values
uniq = set()
for r in data:
    for v in r[1:]:
        uniq.add(str(v).strip())
print("Unique raw values:", sorted(uniq))

MAP = {
    "strongly agree": 5,
    "agree": 4,
    "neutral": 3,
    "disagree": 2,
    "strongly disagree": 1,
}
def to_score(v):
    if v is None: return None
    return MAP.get(str(v).strip().lower())

# Build numeric matrix [respondent][question]
M = []
for r in data:
    row = [to_score(v) for v in r[1:]]
    M.append(row)
M = np.array([[np.nan if x is None else x for x in row] for row in M], dtype=float)
print("Matrix shape:", M.shape)
print("Any NaN:", np.isnan(M).sum())

# Per-statement mean, sd, and % distribution
CATS = [("Strongly Agree",5),("Agree",4),("Neutral",3),("Disagree",2),("Strongly Disagree",1)]
per_item = []
for i,q in enumerate(questions):
    col = M[:,i]
    col = col[~np.isnan(col)]
    mean = col.mean(); sd = col.std(ddof=1)
    dist = {name: round(100.0*np.sum(col==val)/len(col),1) for name,val in CATS}
    agree_pct = round(100.0*np.sum(col>=4)/len(col),1)
    per_item.append({"idx":i+1,"q":q,"mean":round(mean,2),"sd":round(sd,2),"dist":dist,"agree_pct":agree_pct,"n":len(col)})

print("\n=== PER ITEM ===")
for it in per_item:
    print(f"Q{it['idx']:2d} mean={it['mean']:.2f} sd={it['sd']:.2f} agree%={it['agree_pct']:.1f}  {it['q'][:60]}")

# Dimensions (1-indexed question numbers)
dims = {
    "Usage & Adoption Behaviour": [1,2,3,4,5],
    "Perceived Effectiveness & Benefits": [6,7,8,9,10,11,12],
    "Engagement & Application": [13,14,15,16,17,18,19,20],
    "Challenges & Limitations": [21,22,23,24],
}
overall_item = 25

def cronbach_alpha(mat):
    # mat: rows=respondents, cols=items
    mat = mat[~np.isnan(mat).any(axis=1)]
    k = mat.shape[1]
    item_var = mat.var(axis=0, ddof=1).sum()
    total_var = mat.sum(axis=1).var(ddof=1)
    return (k/(k-1))*(1 - item_var/total_var)

print("\n=== DIMENSIONS ===")
dim_scores = {}
dim_stats = {}
for name, qs in dims.items():
    idx = [q-1 for q in qs]
    sub = M[:, idx]
    scores = np.nanmean(sub, axis=1)
    dim_scores[name] = scores
    alpha = cronbach_alpha(sub)
    dim_stats[name] = {"n_items":len(qs),"mean":round(np.nanmean(scores),2),"sd":round(np.nanstd(scores,ddof=1),2),"alpha":round(alpha,3)}
    print(f"{name}: items={len(qs)} mean={dim_stats[name]['mean']} sd={dim_stats[name]['sd']} alpha={alpha:.3f}")

overall_mean = round(np.nanmean(M[:,overall_item-1]),2)
print("Overall effectiveness (Q25) mean:", overall_mean)

# Effectiveness score (main outcome) = Perceived Effectiveness dimension
eff = dim_scores["Perceived Effectiveness & Benefits"]
eng = dim_scores["Engagement & Application"]
usage = dim_scores["Usage & Adoption Behaviour"]

# T-TEST: frequent vs infrequent learners (median split on Q1)
q1 = M[:,0]
med = np.nanmedian(q1)
print("\nQ1 median:", med, "distribution:", {v:int(np.sum(q1==v)) for v in [1,2,3,4,5]})
# frequent = Q1 >=4 (agree/strongly agree), infrequent = Q1 <=3
freq_mask = q1>=4
infreq_mask = q1<=3
g_freq = eff[freq_mask]; g_infreq = eff[infreq_mask]
t,p = stats.ttest_ind(g_freq, g_infreq, equal_var=False)
print("\n=== T-TEST (Effectiveness: frequent vs infrequent learners) ===")
print(f"Frequent n={freq_mask.sum()} mean={g_freq.mean():.3f} sd={g_freq.std(ddof=1):.3f}")
print(f"Infrequent n={infreq_mask.sum()} mean={g_infreq.mean():.3f} sd={g_infreq.std(ddof=1):.3f}")
print(f"t={t:.3f} p={p:.3f}")

# ANOVA: Effectiveness across engagement level groups (tertiles of engagement)
lo, hi = np.nanpercentile(eng, [33.333, 66.667])
print("\nEngagement tertile cuts:", round(lo,3), round(hi,3))
grp_low = eff[eng<=lo]
grp_mid = eff[(eng>lo)&(eng<=hi)]
grp_high = eff[eng>hi]
F,pa = stats.f_oneway(grp_low, grp_mid, grp_high)
print("=== ANOVA (Effectiveness across engagement groups) ===")
for nm,g in [("Low",grp_low),("Medium",grp_mid),("High",grp_high)]:
    print(f"{nm} n={len(g)} mean={g.mean():.3f} sd={g.std(ddof=1):.3f}")
print(f"F={F:.3f} p={pa:.3f}")

# Correlation: Engagement vs Effectiveness
r,pc = stats.pearsonr(eng, eff)
print(f"\n=== CORRELATION Engagement vs Effectiveness: r={r:.3f} p={pc:.3f} ===")
r2,pc2 = stats.pearsonr(usage, eff)
print(f"=== CORRELATION Usage vs Effectiveness: r={r2:.3f} p={pc2:.3f} ===")

# Save everything
out = {
    "n": len(data),
    "questions": questions,
    "per_item": per_item,
    "dims": {k:v for k,v in dim_stats.items()},
    "dim_qs": dims,
    "overall_mean": overall_mean,
    "ttest": {"freq_n":int(freq_mask.sum()),"freq_mean":round(float(g_freq.mean()),3),"freq_sd":round(float(g_freq.std(ddof=1)),3),
              "infreq_n":int(infreq_mask.sum()),"infreq_mean":round(float(g_infreq.mean()),3),"infreq_sd":round(float(g_infreq.std(ddof=1)),3),
              "t":round(float(t),3),"p":round(float(p),3)},
    "anova": {"low_n":len(grp_low),"low_mean":round(float(grp_low.mean()),3),"low_sd":round(float(grp_low.std(ddof=1)),3),
              "mid_n":len(grp_mid),"mid_mean":round(float(grp_mid.mean()),3),"mid_sd":round(float(grp_mid.std(ddof=1)),3),
              "high_n":len(grp_high),"high_mean":round(float(grp_high.mean()),3),"high_sd":round(float(grp_high.std(ddof=1)),3),
              "F":round(float(F),3),"p":round(float(pa),3)},
    "corr_eng_eff": {"r":round(float(r),3),"p":round(float(pc),3)},
    "corr_usage_eff": {"r":round(float(r2),3),"p":round(float(pc2),3)},
}
with open("analysis_results.json","w") as f:
    json.dump(out,f,indent=2)
print("\nSaved analysis_results.json")

# Understanding Bias Metrics in Veritas

> **A non-technical guide to the bias metrics Veritas uses and what they mean.**

## The Three Metrics

Veritas uses three complementary metrics to measure bias. Each captures a different aspect of fairness.

---

## 1. Disparate Impact Ratio (DIR)

### What It Is
DIR compares the positive outcome rate between two groups.

**Formula (simplified):**
```
DIR = (% hired in minority group) / (% hired in majority group)

Example:
- 50% of women are hired
- 70% of men are hired
- DIR = 50/70 = 0.71
```

### What It Means
- **DIR = 1.0**: Perfect parity (both groups hired at same rate) ✅
- **DIR = 0.8**: At the "threshold" (acceptable in many jurisdictions)
- **DIR < 0.8**: **HIGH BIAS** (minority group hired significantly less) ⚠️
- **DIR > 1.2**: Reverse bias (minority group favored)

### Real-World Example: Hiring

Imagine a tech company hiring engineers:

| Group | Applicants | Hired | Rate |
|-------|-----------|-------|------|
| Women | 100 | 30 | 30% |
| Men | 100 | 50 | 50% |

**DIR = 30% ÷ 50% = 0.60**

This is severely biased! Only 60% of women hired vs men. The company is systematically hiring fewer women.

### Why It Matters
- Defined in **U.S. employment law** (4/5 rule: minority outcomes should be ≥80% of majority)
- Simple, actionable metric
- Easy to explain to non-technical stakeholders

### When It Fails
- Doesn't show **why** bias exists (just that it does)
- Sensitive to sample size (small groups can create extreme ratios)
- Doesn't account for qualification differences

---

## 2. Demographic Parity Difference (DPD)

### What It Is
DPD measures the **absolute percentage-point difference** in outcomes between groups.

**Formula (simplified):**
```
DPD = (% positive outcome in group A) - (% positive outcome in group B)

Example:
- 50% of women approved for loans
- 60% of men approved for loans
- DPD = 50% - 60% = -10 percentage points
```

### What It Means
- **DPD = 0**: Perfect fairness (outcomes identical)
- **|DPD| < 0.10 (10 pp)**: Acceptable (small difference)
- **|DPD| > 0.10 (10 pp)**: **MEDIUM BIAS** (different at >10 pp level) ⚠️
- **|DPD| > 0.20 (20 pp)**: Severe bias

### Real-World Example: Loan Approval

| Group | Applicants | Approved | Rate |
|-------|-----------|----------|------|
| Minority | 1000 | 400 | 40% |
| Majority | 1000 | 600 | 60% |

**DPD = 40% - 60% = -20 percentage points**

Minority group approved **20 percentage points less**. This is significant bias.

### Why It Matters
- Easier to interpret than ratios (people understand percentages)
- Directly answers: "How many more people from group X are rejected?"
- Non-discriminatory if motivated by job-relevant qualifications

### When It Fails
- Can mask extreme bias when base rates are small
- Example: 5% vs 10% has |DPD| = 5 pp (seems small) but DIR = 0.5 (severe!)

---

## 3. Equalized Odds Difference (EOD)

### What It Is
EOD measures whether model **errors are distributed equally** across groups.

**Concept:**
- **False Positive Rate (FPR)**: "Of people who shouldn't have been hired, how many were?"
- **False Negative Rate (FNR)**: "Of people who should have been hired, how many weren't?"

For fairness, both rates should be similar across groups.

### What It Means
- **EOD ≈ 0**: Equal error rates across groups ✅
- **|EOD| > 0.10**: Significant difference in errors ⚠️
- Higher EOD = model fails differently for different groups

### Real-World Example: Hiring Decisions

Imagine a hiring algorithm:

**Women:** 
- Should hire 100, actually hired 80 (missed 20%)
- Shouldn't hire 100, but hired 10 anyway (10% false positives)

**Men:**
- Should hire 100, actually hired 90 (missed 10%)
- Shouldn't hire 100, but hired 5 anyway (5% false positives)

**Issue:** Algorithm misses more qualified women (20% false negative) than men (10%). It's harder to get hired as a woman!

### Why It Matters
- Focuses on **error rates**, not just outcomes
- Accounts for whether bias comes from misclassifications
- Legally recognized in some jurisdictions

### When It Fails
- Complex to explain to non-technical stakeholders
- Can conflict with other fairness metrics
- Requires knowing who truly "should" have been hired (ground truth)

---

## Comparing the Metrics

| Metric | Asks | Example | Threshold | Strength | Weakness |
|--------|------|---------|-----------|----------|----------|
| **DIR** | "Do groups have equal positive outcome rates?" | Hiring rate: 50% women vs 60% men | < 0.80 = bias | Simple, legal standard | Ignores why bias exists |
| **DPD** | "What's the percentage-point difference in outcomes?" | 50% approval vs 60% approval = 10 pp diff | > 0.10 = bias | Intuitive, interpretable | Can mask extreme disparities |
| **EOD** | "Do groups have equal error rates?" | Women missed 20%, men missed 10% | > 0.10 = bias | Focuses on fairness | Complex, requires ground truth |

---

## How Veritas Uses These Metrics

### Severity Levels

Veritas assigns a severity level based on the **worst** finding:

```
IF   Disparate Impact Ratio < 0.80
THEN Severity = "HIGH BIAS" ⚠️ (4/5 rule violation)

ELSE IF |Demographic Parity Difference| > 0.10
THEN Severity = "MEDIUM BIAS" ⚠️ (significant group difference)

ELSE
THEN Severity = "LOW BIAS" ✅ (acceptable fairness)
```

### Example Analysis Output

**Dataset:** 500 hiring records, gender + race tracked

**Finding: Gender Bias (MEDIUM)**
- 65% of women hired
- 50% of men hired
- DPD = +15 pp (women favored)
- DIR = 0.77 (but men slightly favored overall?)
- EOD = 0.08 (similar error rates) ✅

**Interpretation:** Women slightly favored in hiring, but EOD suggests the algorithm is relatively fair in its error rates.

---

## Real-World Scenarios

### Scenario 1: Hiring Algorithm (Tech Company)

**Data:** 1000 applications (60% women, 40% men)

| Metric | Women | Men | Finding |
|--------|-------|-----|---------|
| Hire Rate | 35% | 25% | Women hired more often |
| DPD | - | - | +10 pp (women favored) |
| DIR | - | - | 1.40 (women favorable) |
| EOD | - | - | 0.12 (small error difference) |

**Verdict:** ✅ **No bias** (women actually favored; algorithm working as intended if diversity is a goal)

---

### Scenario 2: Loan Approval (Financial Institution)

**Data:** 2000 loan applications (60% majority race, 40% minority race)

| Metric | Majority | Minority | Finding |
|--------|----------|----------|---------|
| Approval Rate | 65% | 45% | Minority approved less |
| DPD | - | - | -20 pp (severe difference) |
| DIR | - | - | 0.69 (severe bias) |
| EOD | - | - | 0.08 (similar error rates) |

**Verdict:** ⚠️ **HIGH BIAS** (systematically denying minority applicants; likely violates Fair Lending laws)

**Root Cause Ideas:**
- Minority applicants have lower credit scores? (may be justified)
- Minority applicants in different geographic areas? (may be proxy discrimination)
- Algorithm trained on biased historical data? (need retraining)

---

### Scenario 3: Healthcare Diagnosis (Hospital)

**Data:** 5000 patient records (ages 30-80)

| Metric | Young (30-50) | Old (50+) | Finding |
|--------|---------------|-----------|---------|
| Diagnosis Rate | 12% | 8% | Younger patients diagnosed more |
| DPD | - | - | -4 pp (modest difference) |
| DIR | - | - | 0.67 (significant difference) |
| EOD | - | - | 0.05 (small error difference) |

**Verdict:** ⚠️ **MEDIUM BIAS** (young patients diagnosed at higher rate; could indicate missed cases in elderly)

**Root Cause Ideas:**
- Elderly present with atypical symptoms? (legitimate reason)
- Diagnostic criteria age-biased? (may need updates)
- Data collection method differs by age? (methodology issue)

---

## Common Questions

### Q: If my DIR is 0.75, am I breaking the law?

**A:** Possibly. The "4/5 rule" is a guideline in U.S. employment law—if protected groups are selected at rates below 80% of others, it raises a red flag. But it's not a bright-line rule; you can have legitimate reasons (e.g., job-related differences). Consult legal counsel.

### Q: Which metric should I trust most?

**A:** Use all three together:
- **DIR**: Quick, actionable, legal benchmark
- **DPD**: Easy to explain; shows magnitude
- **EOD**: Deeper fairness check; shows if errors are equal

If all three align (all show bias), you have strong evidence. If they conflict, investigate why.

### Q: What if I only care about overall accuracy, not fairness?

**A:** Your model might have high accuracy but severe bias. Example:
- Overall accuracy: 90% ✅
- But: 95% accurate for men, 70% accurate for women ⚠️

Veritas helps catch this.

### Q: Can bias ever be OK?

**A:** Sometimes, if motivated by job-relevant factors:
- Different hiring rates across genders = *might* reflect qualification differences
- Different loan approval rates = *might* reflect creditworthiness differences

**But:** You need evidence it's job-related, not proxy discrimination. Veritas flags bias; you investigate the reason.

### Q: My dataset is small (N=100). Can I trust the metrics?

**A:** Small datasets produce high-variance metrics. DIR in particular can swing wildly with N=100. Consider:
- Confidence intervals (not shown by Veritas, but mathematically available)
- Collecting more data before drawing conclusions
- Using Veritas for screening, not final decisions

### Q: What if my group sizes are very different (10 people vs 1000)?

**A:** Metrics become unreliable for small groups. Example:
- 5 out of 10 minority candidates hired (50%)
- 400 out of 1000 majority candidates hired (40%)
- DIR = 1.25 (looks favorable!)
- But sample size difference makes this unreliable

**Solution:** Use stratified analysis or set minimum group sizes before computing metrics.

---

## Next Steps

### If Veritas Flags Bias:

1. **Understand the severity** (HIGH/MEDIUM/LOW)
2. **Read the AI explanation** (Gemini identifies likely root causes)
3. **Investigate the data:**
   - Are protected groups truly comparable? (same education, experience, etc.)
   - Are outcomes job-related? (or proxy discrimination?)
   - Is the data collection method biased? (how were they selected for the dataset?)
4. **Take action:**
   - Retrain model on more balanced data
   - Add fairness constraints to model
   - Change decision process (add human review, etc.)
   - Document legitimate business reasons (if any)

### If Veritas Finds No Bias:

- Good, but don't be complacent
- Retest periodically (bias can emerge over time)
- Continue monitoring before deployment
- Consider other fairness dimensions not covered (intersectionality, etc.)

---

## Resources

- **Fairlearn (library used):** https://fairlearn.org/
- **4/5 Rule (employment law):** https://www.eeoc.gov/facts-about-equal-employment-opportunity
- **Algorithmic Bias (academic):** https://arxiv.org/abs/1908.04913
- **Responsible AI (Microsoft):** https://www.microsoft.com/en-us/ai/responsible-ai

---

## Glossary

- **Disparate Impact**: Situation where neutral policy has discriminatory effect
- **Protected Attribute**: Characteristic (gender, race, etc.) that cannot legally be used for discrimination
- **Positive Outcome Rate**: Percentage of group receiving favorable decision (hired, approved, etc.)
- **False Positive Rate (FPR)**: % of people incorrectly given positive outcome
- **False Negative Rate (FNR)**: % of people incorrectly given negative outcome
- **Base Rate**: Overall percentage with positive outcome (across all groups)
- **Fairness**: No group has systematically worse outcomes than others (fairness definition varies)
- **Bias**: Systematic difference in treatment/outcomes between protected groups

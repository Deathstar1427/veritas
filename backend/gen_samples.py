import pandas as pd
import numpy as np
import os

np.random.seed(42)
out = os.path.join(os.path.dirname(__file__), "sample_datasets")
os.makedirs(out, exist_ok=True)
n = 500

# HIRING (with bias: Male hired 68%, Female hired 45%)
data = {
    "gender": np.random.choice(["Male", "Female"], n, p=[0.5, 0.5]),
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n),
    "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n),
    "years_experience": np.random.randint(0, 20, n),
    "education_level": np.random.choice(["HS", "Bachelor", "Master", "PhD"], n),
    "interview_score": np.random.randint(40, 100, n),
}
df = pd.DataFrame(data)
hired = []
for i in df.index:
    if df.loc[i, "gender"] == "Female":
        hired.append(1 if np.random.random() < 0.45 else 0)
    else:
        hired.append(1 if np.random.random() < 0.68 else 0)
df["hired"] = hired
df.to_csv(os.path.join(out, "hiring_sample.csv"), index=False)
print(f"Hiring: {len(df)} rows")

# LOAN (with bias: Urban 80%, Rural 55%)
np.random.seed(43)
data2 = {
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n),
    "gender": np.random.choice(["Male", "Female"], n, p=[0.5, 0.5]),
    "income": np.random.randint(20000, 150000, n),
    "credit_score": np.random.randint(300, 850, n),
    "loan_amount": np.random.randint(5000, 500000, n),
    "zip_region": np.random.choice(["Urban", "Suburban", "Rural"], n),
}
df2 = pd.DataFrame(data2)
approved = []
for i in df2.index:
    if df2.loc[i, "zip_region"] == "Urban":
        approved.append(1 if np.random.random() < 0.80 else 0)
    else:
        approved.append(1 if np.random.random() < 0.55 else 0)
df2["approved"] = approved
df2.to_csv(os.path.join(out, "loan_sample.csv"), index=False)
print(f"Loan: {len(df2)} rows")

# HEALTHCARE (with bias: Black/Hispanic 35%, White/Asian 65%)
np.random.seed(44)
data3 = {
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n),
    "gender": np.random.choice(["Male", "Female"], n, p=[0.5, 0.5]),
    "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n),
    "symptom_severity": np.random.randint(1, 10, n),
}
df3 = pd.DataFrame(data3)
diag = []
for i in df3.index:
    if df3.loc[i, "ethnicity"] in ["Black", "Hispanic"]:
        diag.append(1 if np.random.random() < 0.35 else 0)
    else:
        diag.append(1 if np.random.random() < 0.65 else 0)
df3["diagnosis_positive"] = diag
df3.to_csv(os.path.join(out, "healthcare_sample.csv"), index=False)
print(f"Healthcare: {len(df3)} rows")

print("All samples generated!")

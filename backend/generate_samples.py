import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Create sample_data directory if not exists
os.makedirs("sample_data", exist_ok=True)

# ====================
# HIRING DATASET
# ====================
n_rows = 500
data_hiring = {
    "gender": np.random.choice(["Male", "Female"], n_rows, p=[0.5, 0.5]),
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n_rows),
    "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n_rows),
    "years_experience": np.random.randint(0, 20, n_rows),
    "education_level": np.random.choice(["HS", "Bachelor", "Master", "PhD"], n_rows),
    "interview_score": np.random.randint(40, 100, n_rows),
}
df_hiring = pd.DataFrame(data_hiring)

# Bake in bias: Women hired at 45% vs Men at 68%
df_hiring["hired"] = (df_hiring["interview_score"] > 65).astype(int)
for idx in df_hiring.index:
    if df_hiring.loc[idx, "gender"] == "Female":
        if np.random.random() < 0.45:
            df_hiring.loc[idx, "hired"] = 1
        else:
            df_hiring.loc[idx, "hired"] = 0
    else:
        if np.random.random() < 0.68:
            df_hiring.loc[idx, "hired"] = 1
        else:
            df_hiring.loc[idx, "hired"] = 0

df_hiring.to_csv("sample_data/hiring.csv", index=False)
male_rate = df_hiring[df_hiring["gender"] == "Male"]["hired"].mean()
female_rate = df_hiring[df_hiring["gender"] == "Female"]["hired"].mean()
print("Hiring dataset created: {} rows".format(len(df_hiring)))
print("  Male hired rate: {:.1%}".format(male_rate))
print("  Female hired rate: {:.1%}".format(female_rate))

# ====================
# LOAN DATASET
# ====================
data_loan = {
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n_rows),
    "gender": np.random.choice(["Male", "Female"], n_rows, p=[0.5, 0.5]),
    "income": np.random.randint(20000, 150000, n_rows),
    "credit_score": np.random.randint(300, 850, n_rows),
    "loan_amount": np.random.randint(5000, 500000, n_rows),
    "zip_region": np.random.choice(["Urban", "Suburban", "Rural"], n_rows),
}
df_loan = pd.DataFrame(data_loan)

# Bake in bias: Urban approved 80% vs Rural approved 55%
df_loan["approved"] = 0
for idx in df_loan.index:
    if df_loan.loc[idx, "zip_region"] == "Urban":
        df_loan.loc[idx, "approved"] = 1 if np.random.random() < 0.80 else 0
    else:
        df_loan.loc[idx, "approved"] = 1 if np.random.random() < 0.55 else 0

df_loan.to_csv("sample_data/loan.csv", index=False)
urban_rate = df_loan[df_loan["zip_region"] == "Urban"]["approved"].mean()
rural_rate = df_loan[df_loan["zip_region"] == "Rural"]["approved"].mean()
print("Loan dataset created: {} rows".format(len(df_loan)))
print("  Urban approved rate: {:.1%}".format(urban_rate))
print("  Rural approved rate: {:.1%}".format(rural_rate))

# ====================
# HEALTHCARE DATASET
# ====================
data_healthcare = {
    "age_group": np.random.choice(["18-30", "31-45", "46-60", "60+"], n_rows),
    "gender": np.random.choice(["Male", "Female"], n_rows, p=[0.5, 0.5]),
    "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n_rows),
    "symptom_severity": np.random.randint(1, 10, n_rows),
}
df_healthcare = pd.DataFrame(data_healthcare)

# Bake in bias: Certain ethnicities diagnosed positive 35% vs others 65%
df_healthcare["diagnosis_positive"] = 0
for idx in df_healthcare.index:
    if df_healthcare.loc[idx, "ethnicity"] in ["Black", "Hispanic"]:
        df_healthcare.loc[idx, "diagnosis_positive"] = (
            1 if np.random.random() < 0.35 else 0
        )
    else:
        df_healthcare.loc[idx, "diagnosis_positive"] = (
            1 if np.random.random() < 0.65 else 0
        )

df_healthcare.to_csv("sample_data/healthcare.csv", index=False)
white_asian_rate = df_healthcare[df_healthcare["ethnicity"].isin(["White", "Asian"])][
    "diagnosis_positive"
].mean()
black_hispanic_rate = df_healthcare[
    df_healthcare["ethnicity"].isin(["Black", "Hispanic"])
]["diagnosis_positive"].mean()
print("Healthcare dataset created: {} rows".format(len(df_healthcare)))
print("  White/Asian diagnosis rate: {:.1%}".format(white_asian_rate))
print("  Black/Hispanic diagnosis rate: {:.1%}".format(black_hispanic_rate))

# ====================
# EDUCATION DATASET
# ====================
data_education = {
    "age_group": np.random.choice(["13-15", "16-18", "19-21"], n_rows),
    "gender": np.random.choice(["Male", "Female"], n_rows, p=[0.5, 0.5]),
    "socioeconomic_group": np.random.choice(["Low", "Medium", "High"], n_rows),
    "attendance": np.random.randint(70, 100, n_rows),
    "test_score": np.random.randint(40, 100, n_rows),
}
df_education = pd.DataFrame(data_education)

# Bake in bias: Low SES students pass at 40% vs High SES at 72%
df_education["passed"] = 0
for idx in df_education.index:
    if df_education.loc[idx, "socioeconomic_group"] == "Low":
        df_education.loc[idx, "passed"] = 1 if np.random.random() < 0.40 else 0
    elif df_education.loc[idx, "socioeconomic_group"] == "Medium":
        df_education.loc[idx, "passed"] = 1 if np.random.random() < 0.56 else 0
    else:
        df_education.loc[idx, "passed"] = 1 if np.random.random() < 0.72 else 0

df_education.to_csv("sample_data/education.csv", index=False)
low_rate = df_education[df_education["socioeconomic_group"] == "Low"]["passed"].mean()
high_rate = df_education[df_education["socioeconomic_group"] == "High"]["passed"].mean()
print("Education dataset created: {} rows".format(len(df_education)))
print("  Low SES pass rate: {:.1%}".format(low_rate))
print("  High SES pass rate: {:.1%}".format(high_rate))

print("\nAll 4 sample datasets created successfully!")

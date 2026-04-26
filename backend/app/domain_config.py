# For each domain, we define:
# - protected_attributes: columns to check for bias
# - outcome_column: the decision being made (hired, approved, etc.)
# - positive_outcome: what counts as a "good" result

DOMAIN_CONFIG = {
    "hiring": {
        "protected_attributes": ["gender", "age_group", "ethnicity"],
        "outcome_column": "hired",
        "positive_outcome": 1,
        "description": "Job hiring decisions",
    },
    "loan": {
        "protected_attributes": ["gender", "age_group", "zip_region"],
        "outcome_column": "approved",
        "positive_outcome": 1,
        "description": "Loan approval decisions",
    },
    "healthcare": {
        "protected_attributes": ["gender", "age_group", "ethnicity"],
        "outcome_column": "diagnosis_positive",
        "positive_outcome": 1,
        "description": "Healthcare diagnosis decisions",
    },
    "education": {
        "protected_attributes": ["gender", "socioeconomic_group", "region"],
        "outcome_column": "passed",
        "positive_outcome": 1,
        "description": "Student scoring decisions",
    },
}

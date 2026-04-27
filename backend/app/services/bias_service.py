import pandas as pd
from fairlearn.metrics import (
    demographic_parity_difference,
)
from app.domain_config import DOMAIN_CONFIG


def _select_qualified_mask(
    df: pd.DataFrame,
    outcome_col: str,
    protected_attrs: list[str],
) -> pd.Series:
    """
    Build a boolean mask for "qualified" applicants used for EOD.

    Priority:
    1) Use credit_score >= 650 when credit_score exists and is numeric.
    2) Otherwise use top 40% by the first numeric feature column available.
       (excluding outcome/protected attributes/prediction)
    """
    if (
        "credit_score" in df.columns
        and pd.api.types.is_numeric_dtype(df["credit_score"])
    ):
        return df["credit_score"].fillna(float("-inf")) >= 650

    excluded = set(protected_attrs + [outcome_col, "prediction"])
    numeric_cols = [
        col
        for col in df.columns
        if col not in excluded and pd.api.types.is_numeric_dtype(df[col])
    ]

    if not numeric_cols:
        # Last-resort fallback so EOD still works if all useful numeric
        # predictors are missing from the uploaded CSV.
        numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    if not numeric_cols:
        # If no numeric column exists at all, treat everyone as qualified.
        return pd.Series([True] * len(df), index=df.index)

    ranking_col = numeric_cols[0]
    threshold = df[ranking_col].quantile(0.6)
    return df[ranking_col].fillna(float("-inf")) >= threshold


def _compute_equalized_odds_difference(
    y_true: pd.Series,
    sensitive: pd.Series,
    qualified_mask: pd.Series,
    positive_outcome: int,
) -> tuple[float | None, dict[str, float | None]]:
    """
    EOD definition used by product requirement:
      max(TPR per group) - min(TPR per group)

    where:
      TPR(group) = approved==1 among qualified in group / qualified in group
    """
    tpr_by_group: dict[str, float | None] = {}

    groups = sensitive.unique().tolist()
    for group in groups:
        group_mask = sensitive == group
        qualified_group_mask = group_mask & qualified_mask
        denominator = int(qualified_group_mask.sum())

        if denominator == 0:
            tpr_by_group[str(group)] = None
            continue

        numerator = int((y_true[qualified_group_mask] == positive_outcome).sum())
        tpr_by_group[str(group)] = numerator / denominator

    valid_tprs = [value for value in tpr_by_group.values() if value is not None]
    if len(valid_tprs) < 2:
        return None, tpr_by_group

    eod = max(valid_tprs) - min(valid_tprs)
    return eod, tpr_by_group


def detect_bias(df: pd.DataFrame, domain: str) -> dict:
    """
    Takes a dataframe and domain name.
    Returns bias metrics for each protected attribute.

    Think of this as the maths guy in the kitchen —
    he reads the data and flags where things are unfair.
    """
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        raise ValueError(f"Unknown domain: {domain}")

    outcome_col = config["outcome_column"]
    protected_attrs = config["protected_attributes"]
    positive_outcome = config.get("positive_outcome", 1)

    # Validate columns exist before proceeding
    if outcome_col not in df.columns:
        raise ValueError(
            f"CSV must have an '{outcome_col}' column for the {domain} domain. "
            f"Available columns: {', '.join(df.columns)}"
        )

    # Check which protected attributes actually exist in the uploaded CSV
    available_attrs = [col for col in protected_attrs if col in df.columns]

    if not available_attrs:
        raise ValueError(
            f"CSV must have at least one of these columns: {', '.join(protected_attrs)}. "
            f"Available columns: {', '.join(df.columns)}"
        )

    y_true = df[outcome_col]
    qualified_mask = _select_qualified_mask(df, outcome_col, protected_attrs)

    # If there's a prediction column use it, otherwise use outcome as proxy
    y_pred = df["prediction"] if "prediction" in df.columns else y_true

    results = {}

    for attr in available_attrs:
        sensitive = df[attr]
        groups = sensitive.unique().tolist()

        # Demographic Parity Difference
        # "Are different groups getting positive outcomes at the same rate?"
        try:
            dpd = demographic_parity_difference(
                y_true=y_true, y_pred=y_pred, sensitive_features=sensitive
            )
        except Exception:
            dpd = None

        # Equalized Odds Difference
        # Product requirement:
        #   EOD = max(TPR per group) - min(TPR per group)
        #   TPR(group) = approved=1 among qualified in group / qualified in group
        try:
            eod, eod_tpr_by_group = _compute_equalized_odds_difference(
                y_true=y_true,
                sensitive=sensitive,
                qualified_mask=qualified_mask,
                positive_outcome=positive_outcome,
            )
        except Exception:
            eod = None
            eod_tpr_by_group = {}

        # Group-level selection rates
        # "What % of each group got a positive outcome?"
        group_rates = {}
        rates_list = []
        for group in groups:
            mask = sensitive == group
            rate = float(y_pred[mask].mean()) if mask.sum() > 0 else 0
            group_rates[str(group)] = round(rate * 100, 2)
            rates_list.append(rate)

        # Disparate Impact Ratio
        # min(rate1/rate2, rate2/rate1) — threshold 0.8 indicates bias
        dir_value = None
        if len(rates_list) >= 2:
            max_rate = max(rates_list)
            if min(rates_list) > 0 and max_rate > 0:
                dir_value = min(rates_list) / max_rate

        # Bias severity label per master plan
        # disparate_impact_ratio < 0.8 → high
        # demographic_parity_difference > 0.1 → medium
        # else → low
        if dir_value is not None and dir_value < 0.8:
            severity = "High"
        elif dpd is not None and abs(dpd) > 0.1:
            severity = "Medium"
        else:
            severity = "Low"

        results[attr] = {
            "groups": [str(g) for g in groups],
            "demographic_parity_difference": round(dpd, 4) if dpd is not None else None,
            "equalized_odds_difference": round(eod, 4) if eod is not None else None,
            "equalized_odds_tpr_by_group": {
                group: round(value, 4) if value is not None else None
                for group, value in eod_tpr_by_group.items()
            },
            "disparate_impact_ratio": round(dir_value, 4)
            if dir_value is not None
            else None,
            "group_selection_rates": group_rates,
            "bias_severity": severity,
        }

    return {
        "domain": domain,
        "total_records": len(df),
        "outcome_column": outcome_col,
        "attributes_analyzed": available_attrs,
        "bias_metrics": results,
    }


def detect_proxy_columns(
    df: pd.DataFrame,
    protected_attr: str,
    outcome_col: str,
    protected_attrs: list[str],
) -> list[dict]:
    """
    Detect columns that may be proxies for a protected attribute.
    Returns the top 3 columns most correlated with the protected attribute.
    """
    proxies = {}
    for col in df.columns:
        if col in protected_attrs or col == outcome_col:
            continue
        try:
            # Encode categorical columns as numeric codes
            a = (
                pd.Categorical(df[col]).codes
                if df[col].dtype == object
                else df[col]
            )
            b = (
                pd.Categorical(df[protected_attr]).codes
                if df[protected_attr].dtype == object
                else df[protected_attr]
            )
            corr = abs(pd.Series(a).corr(pd.Series(b)))
            if not pd.isna(corr):
                proxies[col] = round(float(corr), 3)
        except Exception:
            continue
    top = sorted(proxies.items(), key=lambda x: x[1], reverse=True)[:3]
    return [{"column": col, "correlation": corr} for col, corr in top]

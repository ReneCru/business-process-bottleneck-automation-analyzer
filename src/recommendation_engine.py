from pathlib import Path
from typing import List

import pandas as pd


STEP_ROI_INPUT_PATH = Path("data/processed/automation_roi_results.csv")
PROCESS_ROI_INPUT_PATH = Path("reports/automation_roi_summary_by_process.csv")

STEP_RECOMMENDATIONS_OUTPUT_PATH = Path("reports/automation_recommendations_by_step.csv")
PROCESS_RECOMMENDATIONS_OUTPUT_PATH = Path("reports/automation_recommendations_by_process.csv")
EXECUTIVE_ACTION_PLAN_OUTPUT_PATH = Path("reports/executive_action_plan.csv")


REQUIRED_PROCESS_COLUMNS = [
    "process_id",
    "process_name",
    "process_category",
    "department",
    "monthly_volume",
    "total_labor_hours_before",
    "total_labor_hours_after",
    "monthly_labor_hours_saved",
    "annual_labor_hours_saved",
    "monthly_labor_cost_before_usd",
    "monthly_labor_cost_after_usd",
    "monthly_labor_cost_savings_usd",
    "annual_labor_cost_savings_usd",
    "automation_setup_cost_usd",
    "annual_waiting_hours_reduced",
    "max_bottleneck_score",
    "annual_net_benefit_usd",
    "roi_pct",
    "payback_months",
    "roi_classification",
]


REQUIRED_STEP_COLUMNS = [
    "process_id",
    "process_name",
    "process_category",
    "department",
    "step_id",
    "step_order",
    "step_name",
    "owner_role",
    "system_used",
    "monthly_volume",
    "automation_feasibility",
    "automation_complexity",
    "bottleneck_score",
    "bottleneck_severity",
    "labor_cost_before_usd",
    "labor_cost_after_usd",
    "monthly_labor_cost_savings_usd",
    "annual_labor_cost_savings_usd",
    "automation_setup_cost_usd",
    "annual_net_benefit_usd",
    "roi_pct",
    "payback_months",
    "monthly_labor_hours_saved",
    "annual_labor_hours_saved",
    "annual_waiting_hours_reduced",
    "roi_classification",
]


def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Loads a CSV file and validates that it exists.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}. "
            "Run the previous project scripts before running the recommendation engine."
        )

    return pd.read_csv(file_path)


def validate_columns(df: pd.DataFrame, required_columns: List[str], dataset_name: str) -> None:
    """
    Validates that all required columns exist.
    """
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in {dataset_name}: {missing_columns}"
        )


def min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Normalizes a numeric series between 0 and 1.

    Higher values become better scores.
    """
    numeric_series = pd.to_numeric(series, errors="coerce")

    if numeric_series.isna().all():
        return pd.Series([0] * len(series), index=series.index)

    numeric_series = numeric_series.fillna(numeric_series.median())

    min_value = numeric_series.min()
    max_value = numeric_series.max()

    if max_value == min_value:
        return pd.Series([1] * len(series), index=series.index)

    return (numeric_series - min_value) / (max_value - min_value)


def inverse_min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Normalizes a numeric series where lower values are better.

    Used for payback months.
    """
    numeric_series = pd.to_numeric(series, errors="coerce")

    if numeric_series.isna().all():
        return pd.Series([0] * len(series), index=series.index)

    fill_value = numeric_series.max() + 12
    numeric_series = numeric_series.fillna(fill_value)

    normalized = min_max_normalize(numeric_series)

    return 1 - normalized


def calculate_automation_priority_score(df: pd.DataFrame, score_level: str) -> pd.DataFrame:
    """
    Calculates automation priority score.

    This score combines financial value, operational pain, payback speed,
    and cycle-time improvement potential.
    """
    df = df.copy()

    if score_level == "process":
        bottleneck_column = "max_bottleneck_score"
    else:
        bottleneck_column = "bottleneck_score"

    df["normalized_annual_net_benefit"] = min_max_normalize(
        df["annual_net_benefit_usd"]
    )
    df["normalized_bottleneck_score"] = min_max_normalize(df[bottleneck_column])
    df["normalized_roi"] = min_max_normalize(df["roi_pct"])
    df["normalized_payback_speed"] = inverse_min_max_normalize(df["payback_months"])
    df["normalized_waiting_reduction"] = min_max_normalize(
        df["annual_waiting_hours_reduced"]
    )

    df["automation_priority_score"] = (
        df["normalized_annual_net_benefit"] * 0.30
        + df["normalized_bottleneck_score"] * 0.25
        + df["normalized_roi"] * 0.20
        + df["normalized_payback_speed"] * 0.15
        + df["normalized_waiting_reduction"] * 0.10
    )

    df["automation_priority_rank"] = (
        df["automation_priority_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    return df.sort_values(by="automation_priority_rank").reset_index(drop=True)


def classify_process_recommendation(row: pd.Series) -> str:
    """
    Classifies process-level automation recommendation.
    """
    roi_pct = row["roi_pct"]
    payback_months = row["payback_months"]
    annual_net_benefit = row["annual_net_benefit_usd"]
    bottleneck_score = row["max_bottleneck_score"]

    if pd.isna(payback_months) or annual_net_benefit <= 0 or roi_pct <= 0:
        return "Do Not Automate Yet"

    if roi_pct >= 200 and payback_months <= 6 and bottleneck_score >= 0.45:
        return "Automate Now"

    if roi_pct >= 75 and payback_months <= 12:
        return "Pilot Automation"

    if bottleneck_score >= 0.45 and roi_pct < 75:
        return "Improve Process First"

    if roi_pct > 0 and payback_months <= 24:
        return "Backlog Candidate"

    return "Monitor Only"


def classify_step_recommendation(row: pd.Series) -> str:
    """
    Classifies step-level automation recommendation.
    """
    roi_pct = row["roi_pct"]
    payback_months = row["payback_months"]
    annual_net_benefit = row["annual_net_benefit_usd"]
    bottleneck_score = row["bottleneck_score"]
    feasibility = row["automation_feasibility"]
    complexity = row["automation_complexity"]

    if pd.isna(payback_months) or annual_net_benefit <= 0 or roi_pct <= 0:
        return "Do Not Automate Yet"

    if (
        feasibility == "High"
        and complexity in ["Low", "Medium"]
        and roi_pct >= 150
        and payback_months <= 8
    ):
        return "Automate This Step"

    if complexity == "High" and roi_pct >= 150 and payback_months <= 12:
        return "Technical Feasibility Study"

    if feasibility == "Medium" and roi_pct >= 75 and payback_months <= 12:
        return "Pilot This Step"

    if bottleneck_score >= 0.45 and feasibility == "Low":
        return "Redesign Before Automation"

    if roi_pct > 0 and payback_months <= 24:
        return "Backlog Candidate"

    return "Monitor Only"


def assign_implementation_phase(recommendation: str) -> str:
    """
    Assigns implementation phase based on recommendation.
    """
    phase_mapping = {
        "Improve Process First": "Phase 0 - Process Cleanup",
        "Redesign Before Automation": "Phase 0 - Process Cleanup",
        "Automate Now": "Phase 1 - Immediate Automation",
        "Automate This Step": "Phase 1 - Immediate Automation",
        "Pilot Automation": "Phase 2 - Pilot",
        "Pilot This Step": "Phase 2 - Pilot",
        "Technical Feasibility Study": "Phase 2 - Technical Assessment",
        "Backlog Candidate": "Phase 3 - Backlog",
        "Do Not Automate Yet": "Hold",
        "Monitor Only": "Hold",
    }

    return phase_mapping.get(recommendation, "Hold")


def build_process_rationale(row: pd.Series) -> str:
    """
    Builds a business rationale for the process-level recommendation.
    """
    recommendation = row["recommendation"]

    if recommendation == "Automate Now":
        return (
            "High financial return, short payback period, and significant operational bottleneck. "
            "This process should be prioritized for automation."
        )

    if recommendation == "Pilot Automation":
        return (
            "Positive ROI and acceptable payback period. Start with a controlled pilot before scaling."
        )

    if recommendation == "Improve Process First":
        return (
            "Operational bottleneck is significant, but the financial case is not strong enough yet. "
            "Standardize and simplify the process before automation."
        )

    if recommendation == "Backlog Candidate":
        return (
            "The process has positive financial value but is not the highest priority. "
            "Keep it in the automation backlog."
        )

    if recommendation == "Do Not Automate Yet":
        return (
            "The automation case does not currently generate enough financial value. "
            "Do not invest until the process volume, cost, or design changes."
        )

    return (
        "No immediate action required. Continue monitoring process performance."
    )


def build_step_rationale(row: pd.Series) -> str:
    """
    Builds a business rationale for the step-level recommendation.
    """
    recommendation = row["recommendation"]

    if recommendation == "Automate This Step":
        return (
            "This step has strong automation feasibility, manageable complexity, "
            "and a favorable financial case."
        )

    if recommendation == "Technical Feasibility Study":
        return (
            "The financial case is attractive, but technical complexity is high. "
            "Validate integration, data quality, and system constraints first."
        )

    if recommendation == "Pilot This Step":
        return (
            "This step has moderate feasibility and positive ROI. "
            "Test automation in a limited scope before full deployment."
        )

    if recommendation == "Redesign Before Automation":
        return (
            "This step is a bottleneck but has low automation feasibility. "
            "Improve rules, ownership, handoffs, and standard work before automating."
        )

    if recommendation == "Backlog Candidate":
        return (
            "This step may create value later but is not an immediate priority."
        )

    if recommendation == "Do Not Automate Yet":
        return (
            "The financial case is too weak to justify automation at this time."
        )

    return "Monitor this step and reassess if volume, cost, or process pain increases."


def add_process_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds process-level recommendations, phases, and rationale.
    """
    df = df.copy()

    df["recommendation"] = df.apply(classify_process_recommendation, axis=1)
    df["implementation_phase"] = df["recommendation"].apply(assign_implementation_phase)
    df["business_rationale"] = df.apply(build_process_rationale, axis=1)

    return df


def add_step_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds step-level recommendations, phases, and rationale.
    """
    df = df.copy()

    df["recommendation"] = df.apply(classify_step_recommendation, axis=1)
    df["implementation_phase"] = df["recommendation"].apply(assign_implementation_phase)
    df["business_rationale"] = df.apply(build_step_rationale, axis=1)

    return df


def build_executive_action_plan(process_recommendations: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a concise executive action plan from process-level recommendations.
    """
    selected_columns = [
        "automation_priority_rank",
        "process_name",
        "process_category",
        "department",
        "recommendation",
        "implementation_phase",
        "monthly_labor_cost_before_usd",
        "monthly_labor_cost_after_usd",
        "monthly_labor_cost_savings_usd",
        "annual_labor_cost_savings_usd",
        "automation_setup_cost_usd",
        "annual_net_benefit_usd",
        "roi_pct",
        "payback_months",
        "annual_labor_hours_saved",
        "annual_waiting_hours_reduced",
        "automation_priority_score",
        "business_rationale",
    ]

    action_plan = process_recommendations[selected_columns].copy()

    return action_plan.sort_values(
        by=["automation_priority_rank", "payback_months"]
    ).reset_index(drop=True)


def save_recommendation_outputs(
    process_recommendations: pd.DataFrame,
    step_recommendations: pd.DataFrame,
    executive_action_plan: pd.DataFrame,
) -> None:
    """
    Saves recommendation outputs.
    """
    PROCESS_RECOMMENDATIONS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    STEP_RECOMMENDATIONS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXECUTIVE_ACTION_PLAN_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    process_recommendations.to_csv(PROCESS_RECOMMENDATIONS_OUTPUT_PATH, index=False)
    step_recommendations.to_csv(STEP_RECOMMENDATIONS_OUTPUT_PATH, index=False)
    executive_action_plan.to_csv(EXECUTIVE_ACTION_PLAN_OUTPUT_PATH, index=False)


def print_recommendation_summary(
    process_recommendations: pd.DataFrame,
    executive_action_plan: pd.DataFrame,
) -> None:
    """
    Prints a concise recommendation summary in the terminal.
    """
    top_recommendation = executive_action_plan.iloc[0]

    recommendation_counts = (
        process_recommendations["recommendation"]
        .value_counts()
        .to_dict()
    )

    print("\nAutomation Recommendation Engine")
    print("--------------------------------")
    print("Process recommendation counts:")

    for recommendation, count in recommendation_counts.items():
        print(f"- {recommendation}: {count}")

    print("\nTop recommended action:")
    print(f"- Process: {top_recommendation['process_name']}")
    print(f"- Department: {top_recommendation['department']}")
    print(f"- Recommendation: {top_recommendation['recommendation']}")
    print(f"- Phase: {top_recommendation['implementation_phase']}")
    print(
        f"- Annual savings: "
        f"${top_recommendation['annual_labor_cost_savings_usd']:,.2f}"
    )
    print(
        f"- Automation setup cost: "
        f"${top_recommendation['automation_setup_cost_usd']:,.2f}"
    )
    print(f"- ROI: {top_recommendation['roi_pct']:,.2f}%")
    print(f"- Payback: {top_recommendation['payback_months']:,.2f} months")
    print(
        f"- Priority score: "
        f"{top_recommendation['automation_priority_score']:.2f}"
    )
    print(f"- Rationale: {top_recommendation['business_rationale']}")

    print("\nFiles created:")
    print(f"- {PROCESS_RECOMMENDATIONS_OUTPUT_PATH}")
    print(f"- {STEP_RECOMMENDATIONS_OUTPUT_PATH}")
    print(f"- {EXECUTIVE_ACTION_PLAN_OUTPUT_PATH}")


def main() -> None:
    """
    Main execution function.
    """
    step_roi = load_csv(STEP_ROI_INPUT_PATH)
    process_roi = load_csv(PROCESS_ROI_INPUT_PATH)

    validate_columns(
        df=step_roi,
        required_columns=REQUIRED_STEP_COLUMNS,
        dataset_name="step ROI results",
    )

    validate_columns(
        df=process_roi,
        required_columns=REQUIRED_PROCESS_COLUMNS,
        dataset_name="process ROI summary",
    )

    process_recommendations = calculate_automation_priority_score(
        df=process_roi,
        score_level="process",
    )
    process_recommendations = add_process_recommendations(process_recommendations)

    step_recommendations = calculate_automation_priority_score(
        df=step_roi,
        score_level="step",
    )
    step_recommendations = add_step_recommendations(step_recommendations)

    executive_action_plan = build_executive_action_plan(process_recommendations)

    save_recommendation_outputs(
        process_recommendations=process_recommendations,
        step_recommendations=step_recommendations,
        executive_action_plan=executive_action_plan,
    )

    print_recommendation_summary(
        process_recommendations=process_recommendations,
        executive_action_plan=executive_action_plan,
    )


if __name__ == "__main__":
    main()
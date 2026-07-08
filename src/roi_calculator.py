from pathlib import Path
from typing import List

import pandas as pd


INPUT_PATH = Path("data/processed/bottleneck_analysis_results.csv")
STEP_ROI_OUTPUT_PATH = Path("data/processed/automation_roi_results.csv")
PROCESS_ROI_OUTPUT_PATH = Path("reports/automation_roi_summary_by_process.csv")
EXECUTIVE_ROI_OUTPUT_PATH = Path("reports/executive_roi_summary.csv")


REQUIRED_COLUMNS = [
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
    "manual_time_minutes_per_case",
    "waiting_time_hours_per_case",
    "error_rate",
    "rework_time_minutes_per_error",
    "cost_per_hour_usd",
    "automation_feasibility",
    "automation_complexity",
    "automation_time_reduction_pct",
    "automation_error_reduction_pct",
    "automation_waiting_time_reduction_pct",
    "automation_setup_cost_usd",
    "manual_hours_before",
    "rework_hours_before",
    "total_labor_hours_before",
    "labor_cost_before_usd",
    "waiting_hours_total",
    "cycle_time_before_per_case_hours",
    "bottleneck_score",
    "bottleneck_rank",
    "bottleneck_severity",
]


def load_bottleneck_analysis(file_path: Path = INPUT_PATH) -> pd.DataFrame:
    """
    Loads the bottleneck analysis results created by bottleneck_analyzer.py.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}. "
            "Run src/bottleneck_analyzer.py before running the ROI calculator."
        )

    return pd.read_csv(file_path)


def validate_roi_columns(df: pd.DataFrame) -> None:
    """
    Validates that all columns required for ROI calculation exist.
    """
    missing_columns: List[str] = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns for ROI calculation: {missing_columns}")


def calculate_future_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates future-state operational metrics after automation.

    The calculation is conservative:
    - Automation reduces manual time.
    - Automation reduces error rate.
    - Automation reduces waiting time.
    - Rework time per error remains the same.
    """
    df = df.copy()

    df["manual_time_minutes_after"] = (
        df["manual_time_minutes_per_case"]
        * (1 - df["automation_time_reduction_pct"])
    )

    df["error_rate_after"] = (
        df["error_rate"] * (1 - df["automation_error_reduction_pct"])
    )

    df["waiting_time_hours_after"] = (
        df["waiting_time_hours_per_case"]
        * (1 - df["automation_waiting_time_reduction_pct"])
    )

    df["manual_hours_after"] = (
        df["monthly_volume"] * df["manual_time_minutes_after"] / 60
    )

    df["rework_hours_after"] = (
        df["monthly_volume"]
        * df["error_rate_after"]
        * df["rework_time_minutes_per_error"]
        / 60
    )

    df["total_labor_hours_after"] = (
        df["manual_hours_after"] + df["rework_hours_after"]
    )

    df["labor_cost_after_usd"] = (
        df["total_labor_hours_after"] * df["cost_per_hour_usd"]
    )

    df["waiting_hours_after_total"] = (
        df["monthly_volume"] * df["waiting_time_hours_after"]
    )

    df["expected_rework_time_after_per_case_hours"] = (
        df["error_rate_after"] * df["rework_time_minutes_per_error"] / 60
    )

    df["cycle_time_after_per_case_hours"] = (
        df["manual_time_minutes_after"] / 60
        + df["waiting_time_hours_after"]
        + df["expected_rework_time_after_per_case_hours"]
    )

    return df


def calculate_savings_and_roi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates labor savings, annual savings, ROI, and payback period.
    """
    df = df.copy()

    df["monthly_labor_hours_saved"] = (
        df["total_labor_hours_before"] - df["total_labor_hours_after"]
    )

    df["annual_labor_hours_saved"] = df["monthly_labor_hours_saved"] * 12

    df["monthly_labor_cost_savings_usd"] = (
        df["labor_cost_before_usd"] - df["labor_cost_after_usd"]
    )

    df["annual_labor_cost_savings_usd"] = (
        df["monthly_labor_cost_savings_usd"] * 12
    )

    df["monthly_waiting_hours_reduced"] = (
        df["waiting_hours_total"] - df["waiting_hours_after_total"]
    )

    df["annual_waiting_hours_reduced"] = (
        df["monthly_waiting_hours_reduced"] * 12
    )

    df["cycle_time_reduction_hours_per_case"] = (
        df["cycle_time_before_per_case_hours"]
        - df["cycle_time_after_per_case_hours"]
    )

    df["cycle_time_reduction_pct"] = (
        df["cycle_time_reduction_hours_per_case"]
        / df["cycle_time_before_per_case_hours"]
    )

    df["annual_net_benefit_usd"] = (
        df["annual_labor_cost_savings_usd"] - df["automation_setup_cost_usd"]
    )

    df["roi_pct"] = (
        df["annual_net_benefit_usd"] / df["automation_setup_cost_usd"] * 100
    )

    df["payback_months"] = df.apply(
        lambda row: (
            row["automation_setup_cost_usd"]
            / row["monthly_labor_cost_savings_usd"]
            if row["monthly_labor_cost_savings_usd"] > 0
            else None
        ),
        axis=1,
    )

    return df


def classify_roi_case(roi_pct: float, payback_months: float) -> str:
    """
    Classifies the automation case based on ROI and payback period.
    """
    if roi_pct >= 200 and payback_months <= 6:
        return "Strong Business Case"

    if roi_pct >= 75 and payback_months <= 12:
        return "Moderate Business Case"

    if roi_pct > 0 and payback_months <= 24:
        return "Long-Term Business Case"

    return "Weak Business Case"


def add_roi_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds ROI classification to each process step.
    """
    df = df.copy()

    df["roi_classification"] = df.apply(
        lambda row: classify_roi_case(
            roi_pct=row["roi_pct"],
            payback_months=row["payback_months"],
        ),
        axis=1,
    )

    return df


def build_process_roi_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates ROI results at process level.
    """
    process_summary = (
        df.groupby(
            [
                "process_id",
                "process_name",
                "process_category",
                "department",
            ],
            as_index=False,
        )
        .agg(
            monthly_volume=("monthly_volume", "max"),
            total_labor_hours_before=("total_labor_hours_before", "sum"),
            total_labor_hours_after=("total_labor_hours_after", "sum"),
            monthly_labor_hours_saved=("monthly_labor_hours_saved", "sum"),
            annual_labor_hours_saved=("annual_labor_hours_saved", "sum"),
            monthly_labor_cost_before_usd=("labor_cost_before_usd", "sum"),
            monthly_labor_cost_after_usd=("labor_cost_after_usd", "sum"),
            monthly_labor_cost_savings_usd=(
                "monthly_labor_cost_savings_usd",
                "sum",
            ),
            annual_labor_cost_savings_usd=(
                "annual_labor_cost_savings_usd",
                "sum",
            ),
            automation_setup_cost_usd=("automation_setup_cost_usd", "sum"),
            annual_waiting_hours_reduced=("annual_waiting_hours_reduced", "sum"),
            avg_cycle_time_before_per_case_hours=(
                "cycle_time_before_per_case_hours",
                "sum",
            ),
            avg_cycle_time_after_per_case_hours=(
                "cycle_time_after_per_case_hours",
                "sum",
            ),
            max_bottleneck_score=("bottleneck_score", "max"),
        )
        .reset_index(drop=True)
    )

    process_summary["annual_net_benefit_usd"] = (
        process_summary["annual_labor_cost_savings_usd"]
        - process_summary["automation_setup_cost_usd"]
    )

    process_summary["roi_pct"] = (
        process_summary["annual_net_benefit_usd"]
        / process_summary["automation_setup_cost_usd"]
        * 100
    )

    process_summary["payback_months"] = process_summary.apply(
        lambda row: (
            row["automation_setup_cost_usd"]
            / row["monthly_labor_cost_savings_usd"]
            if row["monthly_labor_cost_savings_usd"] > 0
            else None
        ),
        axis=1,
    )

    process_summary["cycle_time_reduction_hours_per_case"] = (
        process_summary["avg_cycle_time_before_per_case_hours"]
        - process_summary["avg_cycle_time_after_per_case_hours"]
    )

    process_summary["cycle_time_reduction_pct"] = (
        process_summary["cycle_time_reduction_hours_per_case"]
        / process_summary["avg_cycle_time_before_per_case_hours"]
    )

    process_summary["roi_classification"] = process_summary.apply(
        lambda row: classify_roi_case(
            roi_pct=row["roi_pct"],
            payback_months=row["payback_months"],
        ),
        axis=1,
    )

    process_summary["automation_priority_rank"] = (
        process_summary["annual_net_benefit_usd"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    return process_summary.sort_values(
        by=["automation_priority_rank", "payback_months"]
    ).reset_index(drop=True)


def build_executive_summary(process_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a one-row executive summary for the full business case.
    """
    total_before = process_summary["monthly_labor_cost_before_usd"].sum()
    total_after = process_summary["monthly_labor_cost_after_usd"].sum()
    monthly_savings = process_summary["monthly_labor_cost_savings_usd"].sum()
    annual_savings = process_summary["annual_labor_cost_savings_usd"].sum()
    automation_cost = process_summary["automation_setup_cost_usd"].sum()
    annual_net_benefit = annual_savings - automation_cost

    roi_pct = (
        annual_net_benefit / automation_cost * 100
        if automation_cost > 0
        else None
    )

    payback_months = (
        automation_cost / monthly_savings
        if monthly_savings > 0
        else None
    )

    return pd.DataFrame(
        [
            {
                "monthly_labor_cost_before_usd": total_before,
                "monthly_labor_cost_after_usd": total_after,
                "monthly_labor_cost_savings_usd": monthly_savings,
                "annual_labor_cost_savings_usd": annual_savings,
                "automation_setup_cost_usd": automation_cost,
                "annual_net_benefit_usd": annual_net_benefit,
                "roi_pct": roi_pct,
                "payback_months": payback_months,
                "annual_labor_hours_saved": process_summary[
                    "annual_labor_hours_saved"
                ].sum(),
                "annual_waiting_hours_reduced": process_summary[
                    "annual_waiting_hours_reduced"
                ].sum(),
                "processes_analyzed": process_summary["process_id"].nunique(),
            }
        ]
    )


def save_roi_outputs(
    step_roi: pd.DataFrame,
    process_roi_summary: pd.DataFrame,
    executive_summary: pd.DataFrame,
) -> None:
    """
    Saves ROI outputs to processed data and reports folders.
    """
    STEP_ROI_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESS_ROI_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXECUTIVE_ROI_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    step_roi.to_csv(STEP_ROI_OUTPUT_PATH, index=False)
    process_roi_summary.to_csv(PROCESS_ROI_OUTPUT_PATH, index=False)
    executive_summary.to_csv(EXECUTIVE_ROI_OUTPUT_PATH, index=False)


def print_roi_summary(
    process_roi_summary: pd.DataFrame,
    executive_summary: pd.DataFrame,
) -> None:
    """
    Prints a concise ROI summary in the terminal.
    """
    summary = executive_summary.iloc[0]
    top_process = process_roi_summary.iloc[0]

    print("\nAutomation ROI Analysis")
    print("-----------------------")
    print(
        f"Monthly labor cost before automation: "
        f"${summary['monthly_labor_cost_before_usd']:,.2f}"
    )
    print(
        f"Monthly labor cost after automation: "
        f"${summary['monthly_labor_cost_after_usd']:,.2f}"
    )
    print(
        f"Estimated monthly labor cost savings: "
        f"${summary['monthly_labor_cost_savings_usd']:,.2f}"
    )
    print(
        f"Estimated annual labor cost savings: "
        f"${summary['annual_labor_cost_savings_usd']:,.2f}"
    )
    print(
        f"Estimated automation setup cost: "
        f"${summary['automation_setup_cost_usd']:,.2f}"
    )
    print(f"Estimated ROI: {summary['roi_pct']:,.2f}%")
    print(f"Estimated payback period: {summary['payback_months']:,.2f} months")
    print(
        f"Estimated annual labor hours saved: "
        f"{summary['annual_labor_hours_saved']:,.2f}"
    )
    print(
        f"Estimated annual waiting hours reduced: "
        f"{summary['annual_waiting_hours_reduced']:,.2f}"
    )

    print("\nHighest-value automation opportunity:")
    print(f"- Process: {top_process['process_name']}")
    print(f"- Department: {top_process['department']}")
    print(
        f"- Annual savings: "
        f"${top_process['annual_labor_cost_savings_usd']:,.2f}"
    )
    print(
        f"- Automation setup cost: "
        f"${top_process['automation_setup_cost_usd']:,.2f}"
    )
    print(f"- ROI: {top_process['roi_pct']:,.2f}%")
    print(f"- Payback: {top_process['payback_months']:,.2f} months")
    print(f"- Classification: {top_process['roi_classification']}")

    print("\nFiles created:")
    print(f"- {STEP_ROI_OUTPUT_PATH}")
    print(f"- {PROCESS_ROI_OUTPUT_PATH}")
    print(f"- {EXECUTIVE_ROI_OUTPUT_PATH}")


def main() -> None:
    """
    Main execution function.
    """
    df = load_bottleneck_analysis()
    validate_roi_columns(df)

    step_roi = calculate_future_state_metrics(df)
    step_roi = calculate_savings_and_roi(step_roi)
    step_roi = add_roi_classification(step_roi)

    process_roi_summary = build_process_roi_summary(step_roi)
    executive_summary = build_executive_summary(process_roi_summary)

    save_roi_outputs(
        step_roi=step_roi,
        process_roi_summary=process_roi_summary,
        executive_summary=executive_summary,
    )

    print_roi_summary(
        process_roi_summary=process_roi_summary,
        executive_summary=executive_summary,
    )


if __name__ == "__main__":
    main()
from pathlib import Path
from typing import List

import pandas as pd


INPUT_PATH = Path("data/processed/business_process_data_clean.csv")
STEP_ANALYSIS_OUTPUT_PATH = Path("data/processed/bottleneck_analysis_results.csv")
PROCESS_SUMMARY_OUTPUT_PATH = Path("reports/bottleneck_summary_by_process.csv")
TOP_BOTTLENECKS_OUTPUT_PATH = Path("reports/top_bottlenecks.csv")


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
]


def load_clean_data(file_path: Path = INPUT_PATH) -> pd.DataFrame:
    """
    Loads the clean business process dataset created by ingest_data.py.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Clean input file not found: {file_path}. "
            "Run src/ingest_data.py before running this analyzer."
        )

    return pd.read_csv(file_path)


def validate_analysis_columns(df: pd.DataFrame) -> None:
    """
    Validates that all columns required for bottleneck analysis exist.
    """
    missing_columns: List[str] = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns for analysis: {missing_columns}")


def min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Normalizes a numeric series between 0 and 1.

    If all values are the same, returns 0 to avoid division by zero.
    """
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series([0] * len(series), index=series.index)

    return (series - min_value) / (max_value - min_value)


def calculate_current_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates current-state operational and cost metrics before automation.
    """
    df = df.copy()

    df["manual_hours_before"] = (
        df["monthly_volume"] * df["manual_time_minutes_per_case"] / 60
    )

    df["rework_hours_before"] = (
        df["monthly_volume"]
        * df["error_rate"]
        * df["rework_time_minutes_per_error"]
        / 60
    )

    df["total_labor_hours_before"] = (
        df["manual_hours_before"] + df["rework_hours_before"]
    )

    df["labor_cost_before_usd"] = (
        df["total_labor_hours_before"] * df["cost_per_hour_usd"]
    )

    df["waiting_hours_total"] = (
        df["monthly_volume"] * df["waiting_time_hours_per_case"]
    )

    df["expected_rework_time_per_case_hours"] = (
        df["error_rate"] * df["rework_time_minutes_per_error"] / 60
    )

    df["cycle_time_before_per_case_hours"] = (
        df["manual_time_minutes_per_case"] / 60
        + df["waiting_time_hours_per_case"]
        + df["expected_rework_time_per_case_hours"]
    )

    return df


def calculate_bottleneck_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a weighted bottleneck score.

    The score is not a financial metric. It is a prioritization index
    that combines cost, waiting time, rework, and error rate.
    """
    df = df.copy()

    df["normalized_labor_cost"] = min_max_normalize(df["labor_cost_before_usd"])
    df["normalized_waiting_hours"] = min_max_normalize(df["waiting_hours_total"])
    df["normalized_rework_hours"] = min_max_normalize(df["rework_hours_before"])
    df["normalized_error_rate"] = min_max_normalize(df["error_rate"])

    df["bottleneck_score"] = (
        df["normalized_labor_cost"] * 0.35
        + df["normalized_waiting_hours"] * 0.30
        + df["normalized_rework_hours"] * 0.20
        + df["normalized_error_rate"] * 0.15
    )

    df["bottleneck_rank"] = df["bottleneck_score"].rank(
        method="dense", ascending=False
    ).astype(int)

    return df.sort_values(by="bottleneck_rank").reset_index(drop=True)


def classify_bottleneck_severity(score: float) -> str:
    """
    Classifies bottleneck severity based on the weighted score.
    """
    if score >= 0.70:
        return "Critical"

    if score >= 0.45:
        return "High"

    if score >= 0.25:
        return "Medium"

    return "Low"


def add_bottleneck_severity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds severity labels to each process step.
    """
    df = df.copy()

    df["bottleneck_severity"] = df["bottleneck_score"].apply(
        classify_bottleneck_severity
    )

    return df


def build_process_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates bottleneck results at process level.
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
            total_manual_hours_before=("manual_hours_before", "sum"),
            total_rework_hours_before=("rework_hours_before", "sum"),
            total_labor_hours_before=("total_labor_hours_before", "sum"),
            total_labor_cost_before_usd=("labor_cost_before_usd", "sum"),
            total_waiting_hours=("waiting_hours_total", "sum"),
            avg_cycle_time_before_per_case_hours=(
                "cycle_time_before_per_case_hours",
                "sum",
            ),
            avg_error_rate=("error_rate", "mean"),
            max_bottleneck_score=("bottleneck_score", "max"),
        )
        .sort_values(by="max_bottleneck_score", ascending=False)
        .reset_index(drop=True)
    )

    process_summary["process_bottleneck_rank"] = (
        process_summary["max_bottleneck_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    return process_summary


def save_analysis_outputs(
    step_analysis: pd.DataFrame,
    process_summary: pd.DataFrame,
    top_bottlenecks: pd.DataFrame,
) -> None:
    """
    Saves bottleneck analysis outputs.
    """
    STEP_ANALYSIS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESS_SUMMARY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOP_BOTTLENECKS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    step_analysis.to_csv(STEP_ANALYSIS_OUTPUT_PATH, index=False)
    process_summary.to_csv(PROCESS_SUMMARY_OUTPUT_PATH, index=False)
    top_bottlenecks.to_csv(TOP_BOTTLENECKS_OUTPUT_PATH, index=False)


def print_executive_summary(
    step_analysis: pd.DataFrame,
    process_summary: pd.DataFrame,
    top_bottlenecks: pd.DataFrame,
) -> None:
    """
    Prints a concise executive summary in the terminal.
    """
    total_labor_cost = step_analysis["labor_cost_before_usd"].sum()
    total_labor_hours = step_analysis["total_labor_hours_before"].sum()
    total_waiting_hours = step_analysis["waiting_hours_total"].sum()

    worst_process = process_summary.iloc[0]
    worst_step = top_bottlenecks.iloc[0]

    print("\nBusiness Process Bottleneck Analysis")
    print("------------------------------------")
    print(f"Total monthly labor hours before automation: {total_labor_hours:,.2f}")
    print(f"Total monthly labor cost before automation: ${total_labor_cost:,.2f}")
    print(f"Total monthly waiting hours across all process steps: {total_waiting_hours:,.2f}")

    print("\nHighest-risk process:")
    print(f"- {worst_process['process_name']}")
    print(f"- Department: {worst_process['department']}")
    print(
        f"- Monthly labor cost before automation: "
        f"${worst_process['total_labor_cost_before_usd']:,.2f}"
    )
    print(f"- Process bottleneck rank: {worst_process['process_bottleneck_rank']}")

    print("\nTop bottleneck step:")
    print(f"- Process: {worst_step['process_name']}")
    print(f"- Step: {worst_step['step_name']}")
    print(f"- Owner role: {worst_step['owner_role']}")
    print(f"- Severity: {worst_step['bottleneck_severity']}")
    print(f"- Bottleneck score: {worst_step['bottleneck_score']:.2f}")
    print(f"- Monthly labor cost before automation: ${worst_step['labor_cost_before_usd']:,.2f}")
    print(f"- Monthly waiting hours: {worst_step['waiting_hours_total']:,.2f}")

    print("\nFiles created:")
    print(f"- {STEP_ANALYSIS_OUTPUT_PATH}")
    print(f"- {PROCESS_SUMMARY_OUTPUT_PATH}")
    print(f"- {TOP_BOTTLENECKS_OUTPUT_PATH}")


def main() -> None:
    """
    Main execution function.
    """
    df = load_clean_data()
    validate_analysis_columns(df)

    step_analysis = calculate_current_state_metrics(df)
    step_analysis = calculate_bottleneck_score(step_analysis)
    step_analysis = add_bottleneck_severity(step_analysis)

    process_summary = build_process_summary(step_analysis)
    top_bottlenecks = step_analysis.head(10)

    save_analysis_outputs(
        step_analysis=step_analysis,
        process_summary=process_summary,
        top_bottlenecks=top_bottlenecks,
    )

    print_executive_summary(
        step_analysis=step_analysis,
        process_summary=process_summary,
        top_bottlenecks=top_bottlenecks,
    )


if __name__ == "__main__":
    main()
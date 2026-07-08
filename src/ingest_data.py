from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


RAW_DATA_PATH = Path("data/raw/business_process_data.csv")
PROCESSED_DATA_PATH = Path("data/processed/business_process_data_clean.csv")
VALIDATION_REPORT_PATH = Path("reports/data_validation_summary.csv")


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
]


NUMERIC_COLUMNS = [
    "step_order",
    "monthly_volume",
    "manual_time_minutes_per_case",
    "waiting_time_hours_per_case",
    "error_rate",
    "rework_time_minutes_per_error",
    "cost_per_hour_usd",
    "automation_time_reduction_pct",
    "automation_error_reduction_pct",
    "automation_waiting_time_reduction_pct",
    "automation_setup_cost_usd",
]


PERCENTAGE_COLUMNS = [
    "error_rate",
    "automation_time_reduction_pct",
    "automation_error_reduction_pct",
    "automation_waiting_time_reduction_pct",
]


POSITIVE_VALUE_COLUMNS = [
    "monthly_volume",
    "manual_time_minutes_per_case",
    "waiting_time_hours_per_case",
    "rework_time_minutes_per_error",
    "cost_per_hour_usd",
    "automation_setup_cost_usd",
]


ALLOWED_AUTOMATION_FEASIBILITY = ["High", "Medium", "Low"]
ALLOWED_AUTOMATION_COMPLEXITY = ["High", "Medium", "Low"]


def load_business_process_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads business process data from a CSV or Excel file.

    In a real implementation, this function can be reused to load client data
    exported from Excel, ERP systems, ticketing tools, or workflow platforms.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    if file_path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")


def validate_required_columns(df: pd.DataFrame) -> List[str]:
    """
    Validates that all required columns exist in the dataset.
    """
    errors = []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    return errors


def convert_numeric_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Converts numeric columns to numeric data types.

    Invalid values are converted to NaN so they can be detected during validation.
    """
    errors = []
    df = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            original_null_count = df[column].isna().sum()
            df[column] = pd.to_numeric(df[column], errors="coerce")
            new_null_count = df[column].isna().sum()

            if new_null_count > original_null_count:
                errors.append(
                    f"Column '{column}' contains values that could not be converted to numbers."
                )

    return df, errors


def validate_missing_values(df: pd.DataFrame) -> List[str]:
    """
    Detects missing values in required columns.
    """
    errors = []

    for column in REQUIRED_COLUMNS:
        if column in df.columns:
            missing_count = df[column].isna().sum()

            if missing_count > 0:
                errors.append(f"Column '{column}' has {missing_count} missing values.")

    return errors


def validate_positive_values(df: pd.DataFrame) -> List[str]:
    """
    Validates that operational and cost values are not negative or zero where needed.
    """
    errors = []

    for column in POSITIVE_VALUE_COLUMNS:
        if column in df.columns:
            invalid_count = (df[column] <= 0).sum()

            if invalid_count > 0:
                errors.append(
                    f"Column '{column}' has {invalid_count} values less than or equal to zero."
                )

    return errors


def validate_percentage_values(df: pd.DataFrame) -> List[str]:
    """
    Validates that percentage columns are between 0 and 1.

    Example:
    - 0.08 means 8%
    - 0.75 means 75%
    """
    errors = []

    for column in PERCENTAGE_COLUMNS:
        if column in df.columns:
            invalid_count = ((df[column] < 0) | (df[column] > 1)).sum()

            if invalid_count > 0:
                errors.append(
                    f"Column '{column}' has {invalid_count} values outside the 0 to 1 range."
                )

    return errors


def validate_allowed_categories(df: pd.DataFrame) -> List[str]:
    """
    Validates allowed values for automation feasibility and complexity.
    """
    errors = []

    if "automation_feasibility" in df.columns:
        invalid_feasibility = ~df["automation_feasibility"].isin(
            ALLOWED_AUTOMATION_FEASIBILITY
        )

        invalid_count = invalid_feasibility.sum()

        if invalid_count > 0:
            errors.append(
                f"'automation_feasibility' has {invalid_count} invalid values. "
                f"Allowed values: {ALLOWED_AUTOMATION_FEASIBILITY}"
            )

    if "automation_complexity" in df.columns:
        invalid_complexity = ~df["automation_complexity"].isin(
            ALLOWED_AUTOMATION_COMPLEXITY
        )

        invalid_count = invalid_complexity.sum()

        if invalid_count > 0:
            errors.append(
                f"'automation_complexity' has {invalid_count} invalid values. "
                f"Allowed values: {ALLOWED_AUTOMATION_COMPLEXITY}"
            )

    return errors


def validate_duplicate_ids(df: pd.DataFrame) -> List[str]:
    """
    Validates that step_id is unique.

    Each row represents one process step, so step_id should not be duplicated.
    """
    errors = []

    if "step_id" in df.columns:
        duplicate_count = df["step_id"].duplicated().sum()

        if duplicate_count > 0:
            errors.append(f"Found {duplicate_count} duplicated step_id values.")

    return errors


def clean_business_process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset after validation.

    This function standardizes text fields and sorts process steps.
    """
    df = df.copy()

    text_columns = [
        "process_id",
        "process_name",
        "process_category",
        "department",
        "step_id",
        "step_name",
        "owner_role",
        "system_used",
        "automation_feasibility",
        "automation_complexity",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip()

    df = df.sort_values(by=["process_id", "step_order"]).reset_index(drop=True)

    return df


def run_data_validation(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Runs all data validation checks.
    """
    validation_results = {
        "required_columns": validate_required_columns(df),
        "missing_values": [],
        "positive_values": [],
        "percentage_values": [],
        "allowed_categories": [],
        "duplicate_ids": [],
        "numeric_conversion": [],
    }

    if validation_results["required_columns"]:
        return validation_results

    df, numeric_errors = convert_numeric_columns(df)

    validation_results["numeric_conversion"] = numeric_errors
    validation_results["missing_values"] = validate_missing_values(df)
    validation_results["positive_values"] = validate_positive_values(df)
    validation_results["percentage_values"] = validate_percentage_values(df)
    validation_results["allowed_categories"] = validate_allowed_categories(df)
    validation_results["duplicate_ids"] = validate_duplicate_ids(df)

    return validation_results


def flatten_validation_results(validation_results: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Converts validation results into a DataFrame that can be exported as a report.
    """
    rows = []

    for validation_area, messages in validation_results.items():
        if messages:
            for message in messages:
                rows.append(
                    {
                        "validation_area": validation_area,
                        "status": "Failed",
                        "message": message,
                    }
                )
        else:
            rows.append(
                {
                    "validation_area": validation_area,
                    "status": "Passed",
                    "message": "No issues found.",
                }
            )

    return pd.DataFrame(rows)


def has_validation_errors(validation_results: Dict[str, List[str]]) -> bool:
    """
    Returns True if at least one validation error was found.
    """
    return any(len(messages) > 0 for messages in validation_results.values())


def save_outputs(clean_df: pd.DataFrame, validation_report: pd.DataFrame) -> None:
    """
    Saves the clean dataset and the validation report.
    """
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(PROCESSED_DATA_PATH, index=False)
    validation_report.to_csv(VALIDATION_REPORT_PATH, index=False)


def main() -> None:
    """
    Main execution function.
    """
    df = load_business_process_data()
    validation_results = run_data_validation(df)
    validation_report = flatten_validation_results(validation_results)

    if has_validation_errors(validation_results):
        VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        validation_report.to_csv(VALIDATION_REPORT_PATH, index=False)

        print("Data validation failed.")
        print(f"Validation report saved to: {VALIDATION_REPORT_PATH}")
        print("Fix the source data before running the analysis.")
        return

    df, _ = convert_numeric_columns(df)
    clean_df = clean_business_process_data(df)

    save_outputs(clean_df, validation_report)

    print("Data validation passed successfully.")
    print(f"Clean dataset saved to: {PROCESSED_DATA_PATH}")
    print(f"Validation report saved to: {VALIDATION_REPORT_PATH}")
    print(f"Rows processed: {len(clean_df)}")


if __name__ == "__main__":
    main()
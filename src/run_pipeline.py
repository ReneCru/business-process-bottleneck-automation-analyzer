import subprocess
import sys
from pathlib import Path


PIPELINE_STEPS = [
    {
        "name": "Generate synthetic business process data",
        "script": "src/generate_sample_data.py",
    },
    {
        "name": "Validate and clean business process data",
        "script": "src/ingest_data.py",
    },
    {
        "name": "Analyze business process bottlenecks",
        "script": "src/bottleneck_analyzer.py",
    },
    {
        "name": "Calculate automation ROI",
        "script": "src/roi_calculator.py",
    },
    {
        "name": "Generate automation recommendations",
        "script": "src/recommendation_engine.py",
    },
]


def run_script(script_path: str) -> None:
    """
    Runs a Python script as part of the project pipeline.

    If one script fails, the pipeline stops immediately to avoid creating
    incorrect reports from incomplete or invalid data.
    """
    path = Path(script_path)

    if not path.exists():
        raise FileNotFoundError(f"Pipeline script not found: {script_path}")

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Pipeline failed while running: {script_path}")


def run_pipeline() -> None:
    """
    Runs the full business process bottleneck and automation analysis pipeline.
    """
    print("\nBusiness Process Bottleneck & Automation Analyzer")
    print("Pipeline Execution")
    print("-------------------------------------------------")

    for step_number, step in enumerate(PIPELINE_STEPS, start=1):
        print(f"\nStep {step_number}: {step['name']}")
        print(f"Running: {step['script']}")

        run_script(step["script"])

    print("\nPipeline completed successfully.")
    print("\nGenerated outputs:")
    print("- data/raw/business_process_data.csv")
    print("- data/processed/business_process_data_clean.csv")
    print("- data/processed/bottleneck_analysis_results.csv")
    print("- data/processed/automation_roi_results.csv")
    print("- reports/data_validation_summary.csv")
    print("- reports/bottleneck_summary_by_process.csv")
    print("- reports/top_bottlenecks.csv")
    print("- reports/automation_roi_summary_by_process.csv")
    print("- reports/executive_roi_summary.csv")
    print("- reports/automation_recommendations_by_process.csv")
    print("- reports/automation_recommendations_by_step.csv")
    print("- reports/executive_action_plan.csv")


def main() -> None:
    """
    Main execution function.
    """
    run_pipeline()


if __name__ == "__main__":
    main()
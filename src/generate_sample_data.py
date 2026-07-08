import os
import random
from datetime import datetime

import pandas as pd


RANDOM_SEED = 42
OUTPUT_PATH = "data/raw/business_process_data.csv"


def get_reduction_ranges(automation_feasibility: str) -> dict:
    """
    Returns realistic improvement ranges based on automation feasibility.

    High feasibility means the task is repetitive, rule-based, and easier to automate.
    Medium feasibility means partial automation is possible.
    Low feasibility means the process may require judgment, exceptions, or human approval.
    """
    ranges = {
        "High": {
            "time_reduction": (0.55, 0.80),
            "error_reduction": (0.50, 0.75),
            "waiting_reduction": (0.35, 0.65),
        },
        "Medium": {
            "time_reduction": (0.30, 0.55),
            "error_reduction": (0.25, 0.50),
            "waiting_reduction": (0.15, 0.40),
        },
        "Low": {
            "time_reduction": (0.10, 0.30),
            "error_reduction": (0.05, 0.25),
            "waiting_reduction": (0.05, 0.20),
        },
    }

    return ranges[automation_feasibility]


def estimate_automation_cost(automation_complexity: str, monthly_volume: int) -> float:
    """
    Estimates automation setup cost based on complexity and monthly process volume.

    This is a synthetic estimate for portfolio/demo purposes.
    In a real business implementation, this cost would come from vendor quotes,
    internal development estimates, or consulting scope.
    """
    base_cost_by_complexity = {
        "Low": 2500,
        "Medium": 7500,
        "High": 15000,
    }

    volume_multiplier = 1 + (monthly_volume / 5000)
    estimated_cost = base_cost_by_complexity[automation_complexity] * volume_multiplier

    return round(estimated_cost, 2)


def build_process_templates() -> list:
    """
    Creates realistic business process templates.

    Each process contains operational steps that commonly appear in small,
    mid-sized, or corporate business environments.
    """
    return [
        {
            "process_name": "Invoice Approval",
            "process_category": "Finance",
            "department": "Accounts Payable",
            "monthly_volume_range": (300, 900),
            "hourly_cost_range": (18, 32),
            "steps": [
                ("Invoice Received", "AP Clerk", "Email / ERP", "High", "Low", 5, 12, 4, 18, 0.03, 0.08, 10, 25),
                ("Data Validation", "AP Analyst", "Excel / ERP", "High", "Medium", 10, 25, 8, 36, 0.05, 0.12, 15, 35),
                ("Manager Approval", "Finance Manager", "Email / ERP", "Medium", "Medium", 8, 20, 24, 72, 0.02, 0.06, 10, 25),
                ("Payment Scheduling", "AP Analyst", "ERP", "Medium", "Low", 6, 15, 8, 24, 0.02, 0.05, 10, 20),
            ],
        },
        {
            "process_name": "Purchase Requisition Review",
            "process_category": "Procurement",
            "department": "Supply Chain",
            "monthly_volume_range": (150, 500),
            "hourly_cost_range": (20, 38),
            "steps": [
                ("Request Intake", "Buyer", "Email / ERP", "High", "Low", 8, 18, 4, 20, 0.04, 0.10, 10, 30),
                ("Budget Check", "Procurement Analyst", "Excel / ERP", "High", "Medium", 10, 28, 12, 48, 0.05, 0.14, 15, 40),
                ("Supplier Review", "Buyer", "ERP / Supplier Portal", "Medium", "Medium", 15, 35, 12, 60, 0.04, 0.10, 20, 45),
                ("Approval Routing", "Purchasing Manager", "Email / ERP", "Medium", "Medium", 8, 22, 24, 96, 0.03, 0.08, 15, 35),
            ],
        },
        {
            "process_name": "Customer Support Ticket Resolution",
            "process_category": "Customer Service",
            "department": "Support",
            "monthly_volume_range": (500, 1500),
            "hourly_cost_range": (15, 28),
            "steps": [
                ("Ticket Classification", "Support Agent", "CRM", "High", "Low", 4, 12, 1, 8, 0.05, 0.15, 5, 20),
                ("Initial Response", "Support Agent", "CRM / Email", "High", "Low", 5, 15, 2, 12, 0.04, 0.12, 5, 20),
                ("Escalation Review", "Support Lead", "CRM", "Medium", "Medium", 10, 25, 8, 36, 0.03, 0.08, 10, 30),
                ("Case Closure", "Support Agent", "CRM", "High", "Low", 3, 10, 1, 8, 0.02, 0.07, 5, 15),
            ],
        },
        {
            "process_name": "Employee Onboarding",
            "process_category": "Human Resources",
            "department": "HR",
            "monthly_volume_range": (20, 120),
            "hourly_cost_range": (18, 35),
            "steps": [
                ("Document Collection", "HR Coordinator", "Email / Forms", "High", "Low", 15, 45, 12, 48, 0.06, 0.18, 20, 50),
                ("Employee Data Entry", "HR Coordinator", "HRIS", "High", "Medium", 20, 60, 8, 24, 0.08, 0.20, 30, 75),
                ("Access Request", "IT Support", "Ticketing System", "Medium", "Medium", 10, 30, 24, 96, 0.04, 0.12, 15, 45),
                ("Policy Acknowledgment", "HR Coordinator", "HRIS / Forms", "High", "Low", 8, 20, 8, 24, 0.03, 0.08, 10, 25),
            ],
        },
        {
            "process_name": "Document Control Renewal",
            "process_category": "Compliance",
            "department": "Quality",
            "monthly_volume_range": (80, 300),
            "hourly_cost_range": (22, 40),
            "steps": [
                ("Document Expiration Review", "Document Controller", "Excel / ERP", "High", "Low", 10, 30, 8, 36, 0.05, 0.14, 15, 40),
                ("Owner Follow-up", "Document Controller", "Email", "Medium", "Medium", 8, 25, 24, 120, 0.03, 0.10, 10, 35),
                ("Revision Validation", "Quality Analyst", "QMS", "Medium", "Medium", 20, 50, 24, 96, 0.04, 0.12, 20, 60),
                ("Final Release", "Quality Manager", "QMS", "Low", "High", 15, 40, 12, 72, 0.02, 0.07, 15, 45),
            ],
        },
        {
            "process_name": "Sales Order Entry",
            "process_category": "Sales Operations",
            "department": "Sales",
            "monthly_volume_range": (250, 1000),
            "hourly_cost_range": (17, 30),
            "steps": [
                ("Order Intake", "Sales Coordinator", "Email / CRM", "High", "Low", 6, 18, 2, 12, 0.04, 0.12, 10, 25),
                ("Customer Data Check", "Sales Coordinator", "CRM / ERP", "High", "Medium", 8, 22, 4, 24, 0.05, 0.15, 15, 35),
                ("Pricing Validation", "Sales Analyst", "Excel / ERP", "Medium", "Medium", 12, 30, 8, 48, 0.04, 0.10, 15, 40),
                ("Order Confirmation", "Sales Coordinator", "CRM / Email", "High", "Low", 5, 15, 2, 12, 0.02, 0.06, 5, 20),
            ],
        },
    ]


def generate_business_process_data() -> pd.DataFrame:
    """
    Generates synthetic business process data at process-step level.

    The generated dataset is designed to support:
    - bottleneck analysis
    - labor cost analysis
    - cycle time analysis
    - rework cost analysis
    - automation opportunity ranking
    - ROI calculation
    """
    random.seed(RANDOM_SEED)

    rows = []
    process_templates = build_process_templates()

    for process_index, process in enumerate(process_templates, start=1):
        monthly_volume = random.randint(*process["monthly_volume_range"])
        hourly_cost = round(random.uniform(*process["hourly_cost_range"]), 2)

        for step_index, step in enumerate(process["steps"], start=1):
            (
                step_name,
                owner_role,
                system_used,
                automation_feasibility,
                automation_complexity,
                manual_time_min,
                manual_time_max,
                waiting_time_min,
                waiting_time_max,
                error_rate_min,
                error_rate_max,
                rework_time_min,
                rework_time_max,
            ) = step

            reduction_ranges = get_reduction_ranges(automation_feasibility)

            automation_time_reduction_pct = round(
                random.uniform(*reduction_ranges["time_reduction"]), 4
            )
            automation_error_reduction_pct = round(
                random.uniform(*reduction_ranges["error_reduction"]), 4
            )
            automation_waiting_time_reduction_pct = round(
                random.uniform(*reduction_ranges["waiting_reduction"]), 4
            )

            automation_setup_cost = estimate_automation_cost(
                automation_complexity=automation_complexity,
                monthly_volume=monthly_volume,
            )

            rows.append(
                {
                    "process_id": f"P{process_index:03d}",
                    "process_name": process["process_name"],
                    "process_category": process["process_category"],
                    "department": process["department"],
                    "step_id": f"P{process_index:03d}-S{step_index:02d}",
                    "step_order": step_index,
                    "step_name": step_name,
                    "owner_role": owner_role,
                    "system_used": system_used,
                    "monthly_volume": monthly_volume,
                    "manual_time_minutes_per_case": random.randint(
                        manual_time_min, manual_time_max
                    ),
                    "waiting_time_hours_per_case": round(
                        random.uniform(waiting_time_min, waiting_time_max), 2
                    ),
                    "error_rate": round(random.uniform(error_rate_min, error_rate_max), 4),
                    "rework_time_minutes_per_error": random.randint(
                        rework_time_min, rework_time_max
                    ),
                    "cost_per_hour_usd": hourly_cost,
                    "automation_feasibility": automation_feasibility,
                    "automation_complexity": automation_complexity,
                    "automation_time_reduction_pct": automation_time_reduction_pct,
                    "automation_error_reduction_pct": automation_error_reduction_pct,
                    "automation_waiting_time_reduction_pct": automation_waiting_time_reduction_pct,
                    "automation_setup_cost_usd": automation_setup_cost,
                    "data_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    return pd.DataFrame(rows)


def save_dataset(df: pd.DataFrame, output_path: str) -> None:
    """
    Saves the generated dataset into the raw data folder.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


def main() -> None:
    """
    Main execution function.
    """
    df = generate_business_process_data()
    save_dataset(df, OUTPUT_PATH)

    print("Synthetic business process dataset created successfully.")
    print(f"Rows generated: {len(df)}")
    print(f"File saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
# Data Dictionary

This document explains the main input and output fields used in the Business Process Bottleneck & Automation Analyzer.

## 1. Input Data Fields

| Column | Description | Example |
|---|---|---|
| process_id | Unique process identifier | P001 |
| process_name | Name of the business process | Invoice Approval |
| process_category | Business category | Finance |
| department | Department responsible for the process | Accounts Payable |
| step_id | Unique process step identifier | P001-S01 |
| step_order | Order of the step inside the process | 1 |
| step_name | Name of the process step | Data Validation |
| owner_role | Role responsible for the step | AP Analyst |
| system_used | Main system or tool used | Excel / ERP |
| monthly_volume | Number of cases processed per month | 500 |
| manual_time_minutes_per_case | Manual work time required per case | 15 |
| waiting_time_hours_per_case | Average waiting time per case | 24 |
| error_rate | Percentage of cases with errors, expressed as decimal | 0.08 |
| rework_time_minutes_per_error | Time required to correct each error | 30 |
| cost_per_hour_usd | Labor cost per hour in USD | 25 |
| automation_feasibility | Estimated automation feasibility | High |
| automation_complexity | Estimated implementation complexity | Medium |
| automation_time_reduction_pct | Expected manual time reduction after automation | 0.60 |
| automation_error_reduction_pct | Expected error reduction after automation | 0.50 |
| automation_waiting_time_reduction_pct | Expected waiting time reduction after automation | 0.35 |
| automation_setup_cost_usd | Estimated implementation cost | 10000 |

## 2. Current-State Calculated Fields

| Column | Description |
|---|---|
| manual_hours_before | Monthly manual labor hours before automation |
| rework_hours_before | Monthly rework hours before automation |
| total_labor_hours_before | Manual hours plus rework hours before automation |
| labor_cost_before_usd | Monthly labor cost before automation |
| waiting_hours_total | Total monthly waiting hours |
| expected_rework_time_per_case_hours | Expected rework time per case |
| cycle_time_before_per_case_hours | Estimated cycle time before automation |
| bottleneck_score | Weighted score used to identify process bottlenecks |
| bottleneck_rank | Ranking based on bottleneck score |
| bottleneck_severity | Severity classification: Low, Medium, High, or Critical |

## 3. Future-State Calculated Fields

| Column | Description |
|---|---|
| manual_time_minutes_after | Estimated manual time per case after automation |
| error_rate_after | Estimated error rate after automation |
| waiting_time_hours_after | Estimated waiting time after automation |
| manual_hours_after | Monthly manual labor hours after automation |
| rework_hours_after | Monthly rework hours after automation |
| total_labor_hours_after | Manual hours plus rework hours after automation |
| labor_cost_after_usd | Monthly labor cost after automation |
| waiting_hours_after_total | Total monthly waiting hours after automation |
| cycle_time_after_per_case_hours | Estimated cycle time after automation |

## 4. Savings and ROI Fields

| Column | Description |
|---|---|
| monthly_labor_hours_saved | Monthly labor hours saved |
| annual_labor_hours_saved | Annual labor hours saved |
| monthly_labor_cost_savings_usd | Monthly labor cost savings |
| annual_labor_cost_savings_usd | Annual labor cost savings |
| monthly_waiting_hours_reduced | Monthly waiting hours reduced |
| annual_waiting_hours_reduced | Annual waiting hours reduced |
| cycle_time_reduction_hours_per_case | Cycle time reduction per case |
| cycle_time_reduction_pct | Percentage reduction in cycle time |
| annual_net_benefit_usd | Annual savings minus automation setup cost |
| roi_pct | Return on investment percentage |
| payback_months | Number of months required to recover investment |
| roi_classification | Business case classification |

## 5. Recommendation Fields

| Column | Description |
|---|---|
| automation_priority_score | Weighted score used to prioritize automation opportunities |
| automation_priority_rank | Priority ranking |
| recommendation | Recommended action |
| implementation_phase | Suggested implementation phase |
| business_rationale | Explanation of the recommendation |

## 6. Important Data Notes

Percentage fields must be entered as decimals.

Correct:

```text
0.08 = 8%
0.50 = 50%
0.75 = 75%
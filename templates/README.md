# Business Process Input Template

This folder contains a public demo input template for the Business Process Bottleneck & Automation Analyzer.

## Purpose

The template shows the type of information required to analyze a business process, identify bottlenecks, estimate automation savings, and calculate ROI.

## Important

This template uses sample data only.

Do not include:

- Real company data
- Real employee names
- Real customer information
- Real supplier information
- Confidential financial data
- Internal ERP exports
- Private business process documentation

## Required Fields

| Field | Description |
|---|---|
| process_id | Unique process identifier |
| process_name | Name of the business process |
| process_category | Finance, Procurement, HR, Quality, Sales, etc. |
| department | Department responsible for the process |
| step_id | Unique step identifier |
| step_order | Order of the step in the process |
| step_name | Name of the process step |
| owner_role | Role responsible for the step |
| system_used | System or tool used |
| monthly_volume | Number of cases processed per month |
| manual_time_minutes_per_case | Manual work time required per case |
| waiting_time_hours_per_case | Average waiting time per case |
| error_rate | Error rate as decimal |
| rework_time_minutes_per_error | Time required to correct each error |
| cost_per_hour_usd | Labor cost per hour |
| automation_feasibility | High, Medium, or Low |
| automation_complexity | High, Medium, or Low |
| automation_time_reduction_pct | Expected manual time reduction |
| automation_error_reduction_pct | Expected error reduction |
| automation_waiting_time_reduction_pct | Expected waiting time reduction |
| automation_setup_cost_usd | Estimated automation implementation cost |

## Percentage Format

Use decimal format.

Correct:

```text
0.08 = 8%
0.50 = 50%
0.75 = 75%
```

## Real Implementation Note

For real business use, assumptions should be validated with process owners, historical data, time studies, ERP exports, workflow logs, and automation cost estimates.

## Percentage Format

Use decimal format.

Correct:

```text
0.08 = 8%
0.50 = 50%
0.75 = 75%
```

Incorrect:

```text
8 = 800%
50 = 5000%
75 = 7500%
```

## Real Implementation Note

For real business use, assumptions should be validated with process owners, historical data, time studies, ERP exports, workflow logs, and automation cost estimates.


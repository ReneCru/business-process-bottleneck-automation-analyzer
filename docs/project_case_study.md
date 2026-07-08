# Project Case Study — Business Process Bottleneck & Automation Analyzer

## 1. Project Overview

The Business Process Bottleneck & Automation Analyzer is a Python-based business analytics project designed to identify operational bottlenecks, estimate automation savings, calculate ROI, and generate executive-level automation recommendations.

The project uses synthetic business process data to simulate common workflows such as invoice approval, purchase requisition review, customer support ticket resolution, employee onboarding, document control renewal, and sales order entry.

The goal is to demonstrate how business process data can be converted into structured automation decisions.

## 2. Business Problem

Many organizations lose time and money through manual workflows, approval delays, process errors, rework, and disconnected systems.

Common issues include:

- Excessive manual data entry
- Long approval waiting times
- High error and rework rates
- Lack of visibility into process cost
- No clear ROI before investing in automation
- Poor prioritization of automation opportunities

Without structured analysis, businesses may automate low-impact processes while ignoring higher-value opportunities.

## 3. Project Objective

The objective of this project is to build a scalable and modular analytics tool that can answer:

- Which processes create the biggest bottlenecks?
- Which process steps consume the most labor hours?
- What is the current cost of manual work?
- What is the estimated cost after automation?
- How much time and money could be saved?
- What is the expected ROI?
- What is the estimated payback period?
- Which processes should be automated first?

## 4. Solution Approach

The project follows a structured pipeline:

```text
1. Generate synthetic process data
2. Validate and clean input data
3. Calculate current-state process metrics
4. Identify bottlenecks
5. Estimate future-state automation impact
6. Calculate savings, ROI, and payback period
7. Generate automation recommendations
8. Display results in a Streamlit dashboard
```

## 5. Technical Architecture

The project is organized into modular Python scripts:

src/generate_sample_data.py
    Generates realistic synthetic business process data.

src/ingest_data.py
    Validates and cleans the input dataset.

src/bottleneck_analyzer.py
    Calculates current-state operational metrics and bottleneck scores.

src/roi_calculator.py
    Calculates before-vs-after automation costs, savings, ROI, and payback.

src/recommendation_engine.py
    Generates process and step-level automation recommendations.

src/run_pipeline.py
    Runs the full analysis pipeline with one command.

src/app.py
    Displays results in an interactive Streamlit dashboard.

## 6. Key Business Metrics

The project calculates the following metrics:

Manual labor hours before automation
Rework hours before automation
Total labor cost before automation
Waiting hours
Cycle time before automation
Manual labor hours after automation
Rework hours after automation
Total labor cost after automation
Monthly savings
Annual savings
ROI percentage
Payback period
Bottleneck severity
Automation priority score

## 7. Key Business Formulas
Manual Labor Hours Before Automation
manual_hours_before = monthly_volume × manual_time_minutes_per_case / 60
Rework Hours Before Automation
rework_hours_before = monthly_volume × error_rate × rework_time_minutes_per_error / 60
Labor Cost Before Automation
labor_cost_before = (manual_hours_before + rework_hours_before) × cost_per_hour
Labor Cost After Automation
labor_cost_after = (manual_hours_after + rework_hours_after) × cost_per_hour
Monthly Savings
monthly_savings = labor_cost_before - labor_cost_after
Annual Savings
annual_savings = monthly_savings × 12
ROI
roi_pct = ((annual_savings - automation_setup_cost) / automation_setup_cost) × 100
Payback Period
payback_months = automation_setup_cost / monthly_savings

## 8. Important Methodology Decision

Waiting time is treated as an operational cycle-time metric, not as direct labor cost savings.

This is intentional.

For example, if an approval waits 48 hours, it does not mean someone worked for 48 hours. It means the process was delayed for 48 hours.

Therefore, waiting-time reduction is reported separately as an operational improvement metric instead of being converted directly into payroll savings.

## 9. Recommendation Logic

The recommendation engine evaluates automation opportunities using:

Annual net benefit
Bottleneck severity
ROI
Payback speed
Waiting-time reduction
Automation feasibility
Automation complexity

The tool generates recommendations such as:

Automate Now
Pilot Automation
Improve Process First
Backlog Candidate
Do Not Automate Yet
Monitor Only

## 10. Dashboard Outputs

The Streamlit dashboard includes:

Executive KPI summary
Monthly cost before vs. after automation
ROI by process
Payback period vs. annual savings
Top bottleneck steps
Executive action plan
Step-level automation recommendations
Downloadable CSV reports
Methodology explanation

## 11. Business Value

This project demonstrates how data analytics can support business process improvement and automation strategy.

Potential business value includes:

Identifying high-cost manual processes
Reducing operational waste
Prioritizing automation investments
Supporting ROI-based decisions
Improving process visibility
Creating executive-ready recommendations
Supporting digital transformation initiatives

## 12. Real-World Implementation Requirements

To implement this in a real company, the synthetic dataset would need to be replaced with validated process data.

A real implementation would require:

Process owner interviews
Historical transaction volume
Manual time studies
Error and rework measurement
Labor cost validation
Automation cost estimates
Data security controls
Pilot testing
Post-implementation savings tracking

## 13. Limitations

This public version uses synthetic data and estimated assumptions.

The results should not be interpreted as guaranteed savings.

A production version would require additional controls, including real data validation, security, client-specific assumptions, configurable scoring, and implementation tracking.

## 14. Skills Demonstrated

This project demonstrates:

Python programming
Pandas data processing
Streamlit dashboard development
Plotly visualization
Business process analysis
Bottleneck identification
ROI analysis
Automation opportunity assessment
Data validation
Executive reporting
Modular project architecture
GitHub documentation
Business case development

## 15. Portfolio Positioning

This project is relevant for roles such as:

Business Analyst
Operations Analyst
Process Improvement Analyst
PMO Analyst
Project Manager
Automation Analyst
Supply Chain Analyst
Digital Transformation Analyst

The project shows the ability to connect business operations, financial analysis, automation strategy, and Python-based analytics into a practical decision-support tool.
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st


EXECUTIVE_ROI_PATH = Path("reports/executive_roi_summary.csv")
PROCESS_ROI_PATH = Path("reports/automation_roi_summary_by_process.csv")
BOTTLENECKS_PATH = Path("reports/top_bottlenecks.csv")
ACTION_PLAN_PATH = Path("reports/executive_action_plan.csv")
STEP_RECOMMENDATIONS_PATH = Path("reports/automation_recommendations_by_step.csv")


REQUIRED_FILES = {
    "Executive ROI Summary": EXECUTIVE_ROI_PATH,
    "Process ROI Summary": PROCESS_ROI_PATH,
    "Top Bottlenecks": BOTTLENECKS_PATH,
    "Executive Action Plan": ACTION_PLAN_PATH,
    "Step Recommendations": STEP_RECOMMENDATIONS_PATH,
}


def configure_page() -> None:
    """
    Configures the Streamlit page.
    """
    st.set_page_config(
        page_title="Business Process Bottleneck & Automation Analyzer",
        page_icon="📊",
        layout="wide",
    )


def check_required_files() -> bool:
    """
    Checks whether all required report files exist.
    """
    missing_files = {
        name: path for name, path in REQUIRED_FILES.items() if not path.exists()
    }

    if missing_files:
        st.error("Some required files are missing.")

        st.write("Run the project pipeline before opening the dashboard:")

        st.code(
            """
python src/generate_sample_data.py
python src/ingest_data.py
python src/bottleneck_analyzer.py
python src/roi_calculator.py
python src/recommendation_engine.py
            """,
            language="bash",
        )

        st.write("Missing files:")

        for name, path in missing_files.items():
            st.write(f"- {name}: `{path}`")

        return False

    return True


@st.cache_data
def load_data() -> Dict[str, pd.DataFrame]:
    """
    Loads all dashboard datasets.
    """
    return {
        "executive_roi": pd.read_csv(EXECUTIVE_ROI_PATH),
        "process_roi": pd.read_csv(PROCESS_ROI_PATH),
        "top_bottlenecks": pd.read_csv(BOTTLENECKS_PATH),
        "action_plan": pd.read_csv(ACTION_PLAN_PATH),
        "step_recommendations": pd.read_csv(STEP_RECOMMENDATIONS_PATH),
    }


def format_currency(value: float) -> str:
    """
    Formats a number as USD currency.
    """
    return f"${value:,.2f}"


def format_number(value: float) -> str:
    """
    Formats a number with two decimals.
    """
    return f"{value:,.2f}"


def format_percentage(value: float) -> str:
    """
    Formats a number as percentage.
    """
    return f"{value:,.2f}%"


def calculate_cost_reduction_pct(summary_row: pd.Series) -> float:
    """
    Calculates monthly cost reduction percentage.
    """
    before_cost = summary_row["monthly_labor_cost_before_usd"]
    monthly_savings = summary_row["monthly_labor_cost_savings_usd"]

    if before_cost == 0:
        return 0

    return monthly_savings / before_cost * 100


def render_header() -> None:
    """
    Renders dashboard header.
    """
    st.title("Business Process Bottleneck & Automation Analyzer")

    st.write(
        """
        This dashboard identifies business process bottlenecks, estimates automation
        savings, calculates ROI, and recommends which processes should be automated first.
        """
    )


def render_executive_kpis(executive_roi: pd.DataFrame) -> None:
    """
    Renders executive KPI cards.
    """
    summary = executive_roi.iloc[0]

    monthly_cost_reduction_pct = calculate_cost_reduction_pct(summary)

    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Monthly Cost Before",
        format_currency(summary["monthly_labor_cost_before_usd"]),
    )

    col2.metric(
        "Monthly Cost After",
        format_currency(summary["monthly_labor_cost_after_usd"]),
    )

    col3.metric(
        "Monthly Savings",
        format_currency(summary["monthly_labor_cost_savings_usd"]),
        delta=f"{monthly_cost_reduction_pct:,.2f}% reduction",
    )

    col4.metric(
        "Annual Savings",
        format_currency(summary["annual_labor_cost_savings_usd"]),
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Automation Setup Cost",
        format_currency(summary["automation_setup_cost_usd"]),
    )

    col6.metric(
        "ROI",
        format_percentage(summary["roi_pct"]),
    )

    col7.metric(
        "Payback Period",
        f"{summary['payback_months']:,.2f} months",
    )

    col8.metric(
        "Processes Analyzed",
        int(summary["processes_analyzed"]),
    )

    col9, col10 = st.columns(2)

    col9.metric(
        "Annual Labor Hours Saved",
        format_number(summary["annual_labor_hours_saved"]),
    )

    col10.metric(
        "Annual Waiting Hours Reduced",
        format_number(summary["annual_waiting_hours_reduced"]),
    )


def render_before_after_chart(process_roi: pd.DataFrame) -> None:
    """
    Renders before vs after monthly labor cost by process.
    """
    st.subheader("Monthly Labor Cost Before vs. After Automation")

    chart_data = process_roi[
        [
            "process_name",
            "monthly_labor_cost_before_usd",
            "monthly_labor_cost_after_usd",
        ]
    ].copy()

    chart_data = chart_data.melt(
        id_vars="process_name",
        value_vars=[
            "monthly_labor_cost_before_usd",
            "monthly_labor_cost_after_usd",
        ],
        var_name="cost_type",
        value_name="monthly_cost_usd",
    )

    chart_data["cost_type"] = chart_data["cost_type"].replace(
        {
            "monthly_labor_cost_before_usd": "Before Automation",
            "monthly_labor_cost_after_usd": "After Automation",
        }
    )

    fig = px.bar(
        chart_data,
        x="process_name",
        y="monthly_cost_usd",
        color="cost_type",
        barmode="group",
        labels={
            "process_name": "Process",
            "monthly_cost_usd": "Monthly Labor Cost USD",
            "cost_type": "Cost Type",
        },
    )

    fig.update_layout(xaxis_tickangle=-35)

    st.plotly_chart(fig, use_container_width=True)


def render_roi_chart(process_roi: pd.DataFrame) -> None:
    """
    Renders ROI by process.
    """
    st.subheader("ROI by Process")

    chart_data = process_roi.sort_values(by="roi_pct", ascending=False)

    fig = px.bar(
        chart_data,
        x="process_name",
        y="roi_pct",
        text="roi_pct",
        labels={
            "process_name": "Process",
            "roi_pct": "ROI %",
        },
    )

    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(xaxis_tickangle=-35)

    st.plotly_chart(fig, use_container_width=True)


def render_payback_vs_savings_chart(process_roi: pd.DataFrame) -> None:
    """
    Renders payback period compared with annual savings.
    """
    st.subheader("Payback Period vs. Annual Savings")

    fig = px.scatter(
        process_roi,
        x="payback_months",
        y="annual_labor_cost_savings_usd",
        size="automation_setup_cost_usd",
        hover_name="process_name",
        hover_data=[
            "department",
            "roi_pct",
            "annual_net_benefit_usd",
            "automation_setup_cost_usd",
        ],
        labels={
            "payback_months": "Payback Period Months",
            "annual_labor_cost_savings_usd": "Annual Labor Cost Savings USD",
            "automation_setup_cost_usd": "Automation Setup Cost USD",
        },
    )

    st.plotly_chart(fig, use_container_width=True)


def render_bottleneck_chart(top_bottlenecks: pd.DataFrame) -> None:
    """
    Renders top bottleneck steps.
    """
    st.subheader("Top Bottleneck Steps")

    chart_data = top_bottlenecks.sort_values(
        by="bottleneck_score",
        ascending=True,
    )

    fig = px.bar(
        chart_data,
        x="bottleneck_score",
        y="step_name",
        orientation="h",
        hover_data=[
            "process_name",
            "owner_role",
            "bottleneck_severity",
            "labor_cost_before_usd",
            "waiting_hours_total",
        ],
        labels={
            "bottleneck_score": "Bottleneck Score",
            "step_name": "Process Step",
        },
    )

    st.plotly_chart(fig, use_container_width=True)


def render_recommendation_counts(action_plan: pd.DataFrame) -> None:
    """
    Renders recommendation count chart.
    """
    st.subheader("Recommendation Mix")

    recommendation_counts = (
        action_plan["recommendation"]
        .value_counts()
        .reset_index()
    )

    recommendation_counts.columns = ["recommendation", "count"]

    fig = px.pie(
        recommendation_counts,
        names="recommendation",
        values="count",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_action_plan_table(action_plan: pd.DataFrame) -> None:
    """
    Renders the executive action plan.
    """
    st.subheader("Executive Action Plan")

    display_columns = [
        "automation_priority_rank",
        "process_name",
        "department",
        "recommendation",
        "implementation_phase",
        "monthly_labor_cost_before_usd",
        "monthly_labor_cost_after_usd",
        "monthly_labor_cost_savings_usd",
        "annual_labor_cost_savings_usd",
        "automation_setup_cost_usd",
        "roi_pct",
        "payback_months",
        "business_rationale",
    ]

    table = action_plan[display_columns].copy()

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


def render_step_recommendations_table(step_recommendations: pd.DataFrame) -> None:
    """
    Renders step-level recommendations.
    """
    st.subheader("Step-Level Automation Recommendations")

    display_columns = [
        "automation_priority_rank",
        "process_name",
        "step_name",
        "owner_role",
        "system_used",
        "automation_feasibility",
        "automation_complexity",
        "recommendation",
        "implementation_phase",
        "annual_labor_cost_savings_usd",
        "automation_setup_cost_usd",
        "roi_pct",
        "payback_months",
        "business_rationale",
    ]

    table = step_recommendations[display_columns].copy()

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


def convert_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """
    Converts a DataFrame into CSV bytes for Streamlit downloads.
    """
    return df.to_csv(index=False).encode("utf-8")


def render_download_section(data: Dict[str, pd.DataFrame]) -> None:
    """
    Renders report download buttons.
    """
    st.subheader("Download Reports")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        label="Download Executive Action Plan",
        data=convert_dataframe_to_csv(data["action_plan"]),
        file_name="executive_action_plan.csv",
        mime="text/csv",
    )

    col2.download_button(
        label="Download Process ROI Summary",
        data=convert_dataframe_to_csv(data["process_roi"]),
        file_name="automation_roi_summary_by_process.csv",
        mime="text/csv",
    )

    col3.download_button(
        label="Download Step Recommendations",
        data=convert_dataframe_to_csv(data["step_recommendations"]),
        file_name="automation_recommendations_by_step.csv",
        mime="text/csv",
    )


def render_methodology_section() -> None:
    """
    Renders methodology notes.
    """
    with st.expander("Methodology"):
        st.write(
            """
            The analyzer separates direct labor cost from waiting time.
            Labor savings are calculated from reductions in manual work and rework.
            Waiting-time reduction is used as an operational improvement metric,
            but it is not directly converted into payroll savings.
            """
        )

        st.write("Key formulas:")

        st.code(
            """
manual_hours_before = monthly_volume * manual_time_minutes_per_case / 60

rework_hours_before = monthly_volume * error_rate * rework_time_minutes_per_error / 60

labor_cost_before = (manual_hours_before + rework_hours_before) * cost_per_hour

manual_time_after = manual_time_before * (1 - automation_time_reduction_pct)

error_rate_after = error_rate_before * (1 - automation_error_reduction_pct)

labor_cost_after = (manual_hours_after + rework_hours_after) * cost_per_hour

monthly_savings = labor_cost_before - labor_cost_after

annual_savings = monthly_savings * 12

roi_pct = (annual_savings - automation_setup_cost) / automation_setup_cost * 100

payback_months = automation_setup_cost / monthly_savings
            """,
            language="text",
        )


def main() -> None:
    """
    Main Streamlit app function.
    """
    configure_page()
    render_header()

    if not check_required_files():
        return

    data = load_data()

    executive_roi = data["executive_roi"]
    process_roi = data["process_roi"]
    top_bottlenecks = data["top_bottlenecks"]
    action_plan = data["action_plan"]
    step_recommendations = data["step_recommendations"]

    render_executive_kpis(executive_roi)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        render_roi_chart(process_roi)

    with col2:
        render_recommendation_counts(action_plan)

    render_before_after_chart(process_roi)
    render_payback_vs_savings_chart(process_roi)
    render_bottleneck_chart(top_bottlenecks)

    st.divider()

    render_action_plan_table(action_plan)
    render_step_recommendations_table(step_recommendations)

    st.divider()

    render_download_section(data)
    render_methodology_section()


if __name__ == "__main__":
    main()
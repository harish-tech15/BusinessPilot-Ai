
import os
import json
import sqlite3
import html
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# BUSINESSPILOT AI - ENTERPRISE DASHBOARD
# =========================================================

BASE_DIR = "/content/BusinessPilot-AI"

DATA_FILE = os.path.join(BASE_DIR, "dashboard_data.json")
CSV_FILE = os.path.join(BASE_DIR, "sample_data", "sales_data.csv")
DB_FILE = os.path.join(BASE_DIR, "database", "businesspilot.db")
PDF_FILE = os.path.join(BASE_DIR, "reports", "BusinessPilot_Executive_Report.pdf")

st.set_page_config(
    page_title="BusinessPilot AI | Enterprise Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ANIMATED ENTERPRISE THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(31,111,235,0.12), transparent 28%),
        radial-gradient(circle at 90% 20%, rgba(0,212,170,0.08), transparent 25%),
        #080e1b;
    color: #e8eefc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101a2d, #0a1221);
    border-right: 1px solid rgba(100,150,220,0.18);
}

[data-testid="stHeader"] {
    background: rgba(8,14,27,0.75);
}

h1, h2, h3 {
    color: #edf4ff !important;
}

p, label, span {
    color: #c5d2e8;
}

.hero {
    padding: 28px;
    border: 1px solid rgba(100,160,255,0.25);
    border-radius: 20px;
    background: linear-gradient(120deg, rgba(25,50,91,0.85), rgba(12,25,45,0.88));
    box-shadow: 0 12px 45px rgba(0,0,0,0.25);
    animation: fadeIn 0.8s ease;
    margin-bottom: 22px;
}

.hero-title {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
}

.hero-subtitle {
    color: #a9c5ed;
    font-size: 13px;
    margin-top: 7px;
}

.kpi-card {
    padding: 20px;
    min-height: 125px;
    border-radius: 16px;
    border: 1px solid rgba(120,160,220,0.2);
    background: linear-gradient(145deg, #14243d, #0e192c);
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    transition: all 0.25s ease;
    animation: fadeIn 0.7s ease;
}

.kpi-card:hover {
    transform: translateY(-5px);
    border-color: #3d8bfd;
    box-shadow: 0 12px 30px rgba(30,120,255,0.15);
}

.kpi-label {
    font-size: 12px;
    color: #9eb5d8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    font-size: 27px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 12px;
}

.kpi-caption {
    font-size: 11px;
    color: #7f9fc8;
    margin-top: 5px;
}

.section-card {
    background: rgba(17,30,50,0.82);
    border: 1px solid rgba(110,150,210,0.17);
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 15px;
}

.agent-card {
    background: linear-gradient(120deg, #14243a, #101b2d);
    border: 1px solid rgba(100,150,220,0.18);
    border-radius: 13px;
    padding: 15px;
    margin-bottom: 10px;
    transition: 0.2s ease;
}

.agent-card:hover {
    border-color: #3d8bfd;
    transform: translateX(3px);
}

.login-wrapper {
    max-width: 480px;
    margin: 8vh auto;
    padding: 32px;
    background: linear-gradient(145deg, #152640, #0c1728);
    border: 1px solid rgba(100,160,255,0.3);
    border-radius: 22px;
    box-shadow: 0 20px 70px rgba(0,0,0,0.4);
    animation: fadeIn 1s ease;
}

.login-brand {
    text-align: center;
    font-size: 31px;
    font-weight: 800;
    color: #ffffff;
}

.login-caption {
    text-align: center;
    color: #9eb5d8;
    font-size: 13px;
    margin-bottom: 25px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(90,150,255,0.35);
    background: linear-gradient(100deg, #1769d2, #2454a8);
    color: white;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: #80b5ff;
    transform: translateY(-2px);
    color: white;
}

div[data-testid="stMetric"] {
    background: #122139;
    border: 1px solid rgba(100,150,220,0.17);
    border-radius: 12px;
    padding: 12px;
}

hr {
    border-color: rgba(130,160,210,0.18);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD PROJECT DATA
# =========================================================

@st.cache_data
def load_dashboard_data():

    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_sales_data():

    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()

    df = pd.read_csv(CSV_FILE)

    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(
            df["Order_Date"], errors="coerce"
        )

    return df


def get_db_connection():

    return sqlite3.connect(DB_FILE, timeout=15)


def get_approval_records():

    if not os.path.exists(DB_FILE):
        return pd.DataFrame()

    try:
        with get_db_connection() as conn:
            return pd.read_sql_query(
                """
                SELECT request_id, action, reason, status, created_at
                FROM approval_requests
                ORDER BY id DESC
                """,
                conn
            )
    except Exception:
        return pd.DataFrame()


def record_decision(request_id, decision):

    if decision not in ["approved", "rejected"]:
        return False

    try:
        with get_db_connection() as conn:

            cursor = conn.execute(
                """
                UPDATE approval_requests
                SET status = ?
                WHERE request_id = ?
                  AND status = 'pending'
                """,
                (decision, request_id)
            )

            if cursor.rowcount == 0:
                return False

            conn.execute(
                """
                INSERT INTO audit_logs
                (run_id, agent_name, event, details)
                VALUES (?, ?, ?, ?)
                """,
                (
                    st.session_state.get("execution_id", "dashboard"),
                    "human_approval_manager",
                    "APPROVAL_" + decision.upper(),
                    json.dumps({
                        "request_id": request_id,
                        "decision": decision
                    })
                )
            )

            conn.commit()

        return True

    except Exception as error:
        st.error(f"Approval update failed: {error}")
        return False


# =========================================================
# AUTHENTICATION - DEVELOPMENT PROTOTYPE
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "execution_id" not in st.session_state:
    st.session_state.execution_id = "Not loaded"

if not st.session_state.authenticated:

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    st.markdown(
        '<div class="login-brand">🚀 BusinessPilot AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-caption">AUTONOMOUS BUSINESS INTELLIGENCE PLATFORM</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    with st.form("login_form"):

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        submitted = st.form_submit_button(
            "ACCESS COMMAND CENTER",
            use_container_width=True
        )

        if submitted:

            expected_user = os.getenv(
                "BUSINESSPILOT_USERNAME", "admin"
            )

            expected_password = os.getenv(
                "BUSINESSPILOT_PASSWORD", "ChangeMe123!"
            )

            if username == expected_user and password == expected_password:

                st.session_state.authenticated = True
                st.rerun()

            else:
                st.error("Invalid username or password.")

    st.markdown(
        '<div class="login-caption">Secure access prototype · Authorized users only</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# =========================================================
# AUTHENTICATED APPLICATION
# =========================================================

data = load_dashboard_data()
sales = load_sales_data()

st.session_state.execution_id = data.get(
    "execution_id", "Not available"
)

agents = data.get("agents", {})

agent_names = {
    "data_analyst": "Data Analyst",
    "finance_analyst": "Finance Analyst",
    "researcher": "Researcher",
    "strategist": "Strategist",
    "quality_controller": "Quality Controller"
}

# Read independently verified metrics
quality = agents.get("quality_controller") or {}
metrics = quality.get("independent_metrics", {})

revenue = float(metrics.get("total_revenue", 0))
cost = float(metrics.get("total_cost", 0))
profit = float(metrics.get("total_profit", 0))
margin = float(metrics.get("profit_margin", 0))

if not metrics and not sales.empty:
    revenue = float(sales["Revenue"].sum())
    cost = float(sales["Cost"].sum())
    profit = float(sales["Profit"].sum())
    margin = profit / revenue * 100 if revenue else 0


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🚀 BusinessPilot AI")
    st.caption("ENTERPRISE COMMAND CENTER")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Business Analytics",
            "AI Agent Monitor",
            "Human Approval Center",
            "Executive Reports",
            "System Information"
        ]
    )

    st.markdown("---")

    st.markdown("**Workflow Status**")
    st.success(data.get("workflow_status", "Unknown"))

    st.caption(
        "Execution: " + str(data.get("execution_id", "N/A"))
    )

    st.markdown("---")

    if st.button("LOG OUT", use_container_width=True):

        st.session_state.authenticated = False
        st.rerun()

    st.caption("BusinessPilot AI · Prototype v0.1")


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">BusinessPilot AI</div>
    <div class="hero-subtitle">
        AUTONOMOUS MULTI-AGENT BUSINESS OPERATIONS PLATFORM
        · ENTERPRISE ANALYTICS COMMAND CENTER
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    st.subheader("Executive Overview")

    st.caption(
        "Business performance indicators from the current analysis run."
    )

    kpis = [
        ("TOTAL REVENUE", f"₹{revenue / 1e7:.2f} Cr", "Sales performance"),
        ("TOTAL PROFIT", f"₹{profit / 1e7:.2f} Cr", "Calculated profit"),
        ("OPERATING COST", f"₹{cost / 1e7:.2f} Cr", "Recorded costs"),
        ("PROFIT MARGIN", f"{margin:.2f}%", "Profit / revenue")
    ]

    cols = st.columns(4)

    for col, (label, value, caption) in zip(cols, kpis):

        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### Business Performance")

    if not sales.empty:

        left, right = st.columns(2)

        with left:

            region_data = (
                sales.groupby("Region", as_index=False)
                .agg(Revenue=("Revenue", "sum"))
            )

            fig = px.bar(
                region_data,
                x="Region",
                y="Revenue",
                title="Revenue by Region",
                template="plotly_dark",
                color="Revenue",
                color_continuous_scale="Blues"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:

            product_data = (
                sales.groupby("Product", as_index=False)
                .agg(Revenue=("Revenue", "sum"))
            )

            fig = px.pie(
                product_data,
                names="Product",
                values="Revenue",
                title="Product Revenue Distribution",
                template="plotly_dark",
                hole=0.55
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Sales dataset is not available.")

    st.markdown("### AI Workforce")

    cols = st.columns(5)

    for col, (key, name) in zip(cols, agent_names.items()):

        result = agents.get(key)

        with col:
            if result:
                st.success(name)
                st.caption("Output available")
            else:
                st.warning(name)
                st.caption("Output unavailable")


# =========================================================
# BUSINESS ANALYTICS
# =========================================================

elif page == "Business Analytics":

    st.subheader("Business Analytics")

    if sales.empty:

        st.warning("Sales dataset is unavailable.")

    else:

        selected_regions = st.multiselect(
            "Select Regions",
            sorted(sales["Region"].dropna().unique()),
            default=sorted(sales["Region"].dropna().unique())
        )

        filtered = sales[
            sales["Region"].isin(selected_regions)
        ].copy()

        a, b, c = st.columns(3)

        a.metric("Orders", f"{len(filtered):,}")
        b.metric("Revenue", f"₹{filtered['Revenue'].sum()/1e7:.2f} Cr")
        c.metric("Profit", f"₹{filtered['Profit'].sum()/1e7:.2f} Cr")

        region_summary = (
            filtered.groupby("Region", as_index=False)
            .agg(
                Revenue=("Revenue", "sum"),
                Profit=("Profit", "sum"),
                Orders=("Order_ID", "count")
            )
        )

        fig = px.bar(
            region_summary,
            x="Region",
            y=["Revenue", "Profit"],
            barmode="group",
            title="Regional Revenue and Profit",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        product_summary = (
            filtered.groupby("Product", as_index=False)
            .agg(
                Revenue=("Revenue", "sum"),
                Profit=("Profit", "sum"),
                Cost=("Cost", "sum")
            )
        )

        product_summary["Profit Margin %"] = (
            product_summary["Profit"] /
            product_summary["Revenue"] * 100
        )

        st.markdown("### Product Performance")
        st.dataframe(
            product_summary,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Sales Trend")

        if "Order_Date" in filtered.columns:

            trend = (
                filtered.dropna(subset=["Order_Date"])
                .groupby(
                    filtered["Order_Date"].dt.to_period("M")
                )["Revenue"]
                .sum()
                .reset_index()
            )

            trend["Month"] = trend["Order_Date"].astype(str)

            fig = px.line(
                trend,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue Trend",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "Download filtered sales CSV",
            filtered.to_csv(index=False).encode("utf-8"),
            file_name="BusinessPilot_Filtered_Sales.csv",
            mime="text/csv"
        )


# =========================================================
# AI AGENT MONITOR
# =========================================================

elif page == "AI Agent Monitor":

    st.subheader("AI Agent Activity Monitor")

    st.caption("Outputs captured from the latest completed workflow.")

    for key, name in agent_names.items():

        result = agents.get(key)

        with st.expander(f"🤖 {name}", expanded=True):

            if result:

                st.success("Agent output available")

                if key == "quality_controller":

                    content = result.get("review", "")

                else:

                    content = result.get("finding", "")

                st.write(content)

                if key == "quality_controller":

                    st.markdown("**Independent Metrics**")
                    st.json(result.get("independent_metrics", {}))

                    st.markdown("**Validation Issues**")
                    st.write(result.get("issues", []))

                if key == "strategist":

                    st.markdown("**Strategic Priorities**")
                    st.write(
                        result.get("strategic_priorities", [])
                    )

            else:
                st.warning("No output found for this agent.")

    st.markdown("### Execution Details")
    st.code(data.get("execution_id", "N/A"))


# =========================================================
# HUMAN APPROVAL CENTER
# =========================================================

elif page == "Human Approval Center":

    st.subheader("Human Approval Center")

    st.warning(
        "Approvals record human decisions only. "
        "They do not automatically execute external business actions."
    )

    approvals = get_approval_records()

    if approvals.empty:

        st.info("No approval requests found.")

    else:

        total = len(approvals)
        pending = int((approvals["status"] == "pending").sum())
        approved = int((approvals["status"] == "approved").sum())
        rejected = int((approvals["status"] == "rejected").sum())

        a, b, c, d = st.columns(4)

        a.metric("Total Requests", total)
        b.metric("Pending", pending)
        c.metric("Approved", approved)
        d.metric("Rejected", rejected)

        st.markdown("---")

        for _, request in approvals.iterrows():

            with st.container():

                st.markdown(
                    f"### {html.escape(str(request['action']))}"
                )

                st.caption(
                    "Request ID: " +
                    str(request["request_id"])
                )

                st.write(request["reason"])

                status = str(request["status"]).lower()

                if status == "pending":

                    left, right = st.columns(2)

                    with left:

                        if st.button(
                            "APPROVE",
                            key="approve_" + str(request["request_id"])
                        ):

                            if record_decision(
                                request["request_id"], "approved"
                            ):
                                st.success("Approval recorded.")
                                st.rerun()

                    with right:

                        if st.button(
                            "REJECT",
                            key="reject_" + str(request["request_id"])
                        ):

                            if record_decision(
                                request["request_id"], "rejected"
                            ):
                                st.warning("Rejection recorded.")
                                st.rerun()

                elif status == "approved":

                    st.success("APPROVED")

                elif status == "rejected":

                    st.error("REJECTED")

                st.divider()

        st.markdown("### Approval History")
        st.dataframe(
            approvals,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# EXECUTIVE REPORTS
# =========================================================

elif page == "Executive Reports":

    st.subheader("Executive Reports")

    st.write(
        "Access the executive PDF generated by the BusinessPilot workflow."
    )

    if os.path.exists(PDF_FILE):

        with open(PDF_FILE, "rb") as file:

            pdf_bytes = file.read()

        st.success("Executive PDF report available.")

        st.download_button(
            "📄 DOWNLOAD EXECUTIVE PDF",
            data=pdf_bytes,
            file_name="BusinessPilot_Executive_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.caption(
            f"Report size: {len(pdf_bytes)/1024:.2f} KB"
        )

    else:

        st.warning(
            "PDF report not found. Generate the report from the Colab workflow."
        )


# =========================================================
# SYSTEM INFORMATION
# =========================================================

elif page == "System Information":

    st.subheader("System Information")

    st.markdown("### Platform Components")

    components = {
        "Orchestration": "LangGraph",
        "LLM": "Gemini",
        "External Research": "Tavily",
        "Data Analysis": "Pandas / NumPy",
        "Visualization": "Plotly",
        "Database": "SQLite",
        "Interface": "Streamlit",
        "Reporting": "ReportLab"
    }

    st.table(
        pd.DataFrame(
            list(components.items()),
            columns=["Component", "Technology"]
        )
    )

    st.markdown("### Current Execution")

    st.json({
        "execution_id": data.get("execution_id"),
        "workflow_status": data.get("workflow_status"),
        "agent_count": len(agents),
        "dataset_rows": len(sales),
        "database_available": os.path.exists(DB_FILE),
        "report_available": os.path.exists(PDF_FILE)
    })

    st.markdown("### Data Disclaimer")

    st.info(
        "This version uses synthetic demonstration data. "
        "The dashboard is a development prototype, not a production "
        "enterprise security or financial auditing system."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "BusinessPilot AI | Enterprise Multi-Agent Business Intelligence "
    "| Development Prototype v0.1"
)

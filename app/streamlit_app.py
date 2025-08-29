# app/streamlit_app.py
import os
import urllib.parse
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import plotly.express as px

# Load .env (try parent folder first, then current)
if os.path.exists('../.env'):
    load_dotenv('../.env')
else:
    load_dotenv()

# Build DB connection safely (handles special characters in password)
user = os.getenv("MYSQL_USER")
_password_raw = os.getenv("MYSQL_PASSWORD") or ""
password = urllib.parse.quote_plus(_password_raw)
host = os.getenv("MYSQL_HOST", "127.0.0.1")
port = os.getenv("MYSQL_PORT", "3306")
db = os.getenv("MYSQL_DB", "crm_db")

# If user provided a full DATABASE_URL in .env, prefer it; otherwise build one
DATABASE_URL = os.getenv("DATABASE_URL") or f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

# Create engine
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    st.error("Failed to create DB engine. Check your DATABASE_URL / .env. Error: " + str(e))
    st.stop()

st.set_page_config(layout="wide", page_title="CRM Analytics Dashboard")

# Load tables (cached)
@st.cache_data(ttl=60)
def load_tables():
    with engine.connect() as conn:
        leads = pd.read_sql(
            text(
                "SELECT l.*, s.name as source_name, u.name as owner_name "
                "FROM leads l "
                "LEFT JOIN sources s ON l.source_id = s.id "
                "LEFT JOIN users u ON l.owner_id = u.id"
            ),
            conn,
        )
        opps = pd.read_sql(
            text(
                "SELECT o.*, s.name as stage_name, u.name as owner_name "
                "FROM opportunities o "
                "LEFT JOIN stages s ON o.stage_id = s.id "
                "LEFT JOIN users u ON o.owner_id = u.id"
            ),
            conn,
        )
        activities = pd.read_sql(
            text(
                "SELECT a.*, u.name as user_name FROM activities a "
                "LEFT JOIN users u ON a.user_id = u.id"
            ),
            conn,
        )
        sources = pd.read_sql(text("SELECT * FROM sources"), conn)
        users = pd.read_sql(text("SELECT * FROM users"), conn)
        stages = pd.read_sql(text("SELECT * FROM stages ORDER BY stage_order"), conn)

    # ensure datetime types if present
    for df, col in [(leads, "created_at"), (opps, "created_at"), (activities, "created_at")]:
        if col in df.columns and not df.empty:
            df[col] = pd.to_datetime(df[col])

    return leads, opps, activities, sources, users, stages


# Try to load tables, show friendly error if DB is unreachable or query fails
try:
    leads, opps, activities, sources, users, stages = load_tables()
except Exception as e:
    st.error("Error loading data from the database. Check DB, tables and .env. Error: " + str(e))
    st.stop()

# Sidebar filters (guard empty users/sources)
st.sidebar.header("Filters")
owner_opts = ["All"] + (users["name"].tolist() if not users.empty else [])
owner_filter = st.sidebar.selectbox("Owner", owner_opts)
date_min = st.sidebar.date_input("From", value=(datetime.now() - timedelta(days=90)).date())
date_max = st.sidebar.date_input("To", value=datetime.now().date())

source_opts = ["All"] + (sources["name"].tolist() if not sources.empty else [])
source_filter = st.sidebar.selectbox("Source", source_opts)

def filter_df(df, date_col="created_at"):
    # If df is empty or doesn't have the date column, return it as-is
    if df is None or df.empty or date_col not in df.columns:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    res = df.copy()
    res[date_col] = pd.to_datetime(res[date_col])
    mask = (res[date_col] >= pd.to_datetime(date_min)) & (
        res[date_col] <= pd.to_datetime(date_max) + pd.Timedelta(days=1)
    )
    res = res.loc[mask]
    if owner_filter != "All" and "owner_name" in res.columns:
        res = res[res["owner_name"] == owner_filter]
    if source_filter != "All" and "source_name" in res.columns:
        res = res[res["source_name"] == source_filter]
    return res

f_leads = filter_df(leads)
f_opps = filter_df(opps)
f_activities = filter_df(activities)

# KPI tiles
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("New leads", int(f_leads.shape[0]) if not f_leads.empty else 0)
col2.metric("Opportunities", int(f_opps.shape[0]) if not f_opps.empty else 0)
won = f_opps[f_opps["status"] == "WON"].shape[0] if "status" in f_opps.columns else 0
col3.metric("Won", int(won))
pipeline_value = float(f_opps[f_opps["status"] != "LOST"]["value"].sum()) if "value" in f_opps.columns else 0.0
col4.metric("Pipeline value", f"${pipeline_value:,.0f}")
conv_rate = (f_opps.shape[0] / f_leads.shape[0] * 100) if (not f_leads.empty and f_leads.shape[0] > 0) else 0
col5.metric("Conversion % (opps/leads)", f"{conv_rate:.1f}%")

# Time series — New leads (weekly)
st.markdown("### Time series — New leads (weekly)")
if not f_leads.empty:
    ts = f_leads.set_index("created_at").resample("W-MON").size().reset_index(name="count")
    fig = px.line(ts, x="created_at", y="count", title="New leads per week")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No leads in this period.")

# Funnel-style: lead -> opportunity -> won
st.markdown("### Funnel / conversion")
total_leads = f_leads.shape[0] if not f_leads.empty else 0
total_opps = f_opps.shape[0] if not f_opps.empty else 0
total_won = f_opps[f_opps["status"] == "WON"].shape[0] if "status" in f_opps.columns else 0
funnel_df = pd.DataFrame({"stage": ["Leads", "Opportunities", "Won"], "count": [total_leads, total_opps, total_won]})
fig2 = px.bar(funnel_df, x="stage", y="count", title="Simple funnel")
st.plotly_chart(fig2, use_container_width=True)

# Pipeline by stage
st.markdown("### Pipeline value by stage")
if "stage_name" in f_opps.columns and "value" in f_opps.columns and not f_opps.empty:
    pipeline = f_opps.groupby("stage_name")["value"].sum().reset_index().sort_values("value", ascending=False)
    if pipeline.shape[0]:
        fig3 = px.bar(pipeline, x="stage_name", y="value", title="Pipeline value by stage")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No opportunities to show pipeline")
else:
    st.info("No opportunities to show pipeline")

# Top sources by conversion
st.markdown("### Top sources by conversion")
if "source_id" in leads.columns and "id" in sources.columns and not f_opps.empty and not f_leads.empty:
    # leads_with_opps: join opps' lead_id to filtered leads' id and their source_name
    if "lead_id" in f_opps.columns and "id" in f_leads.columns and "source_name" in f_leads.columns:
        leads_with_opps = f_opps[["lead_id"]].merge(f_leads[["id", "source_name"]], left_on="lead_id", right_on="id", how="inner")
        if leads_with_opps.shape[0]:
            src = leads_with_opps.groupby("source_name").size().reset_index(name="opps").sort_values("opps", ascending=False)
            st.table(src.head(10))
        else:
            st.info("No conversions (opportunities linked to leads) in this period")
    else:
        st.info("No conversions (opportunities linked to leads) in this period")
else:
    st.info("No source data or no conversions to compute.")

# Recent activities table
st.markdown("### Recent activities")
if not f_activities.empty:
    st.dataframe(f_activities.sort_values("created_at", ascending=False).head(25))
else:
    st.info("No activities in this period.")

# CRUD: add new lead
st.sidebar.markdown("---")
st.sidebar.header("Add new lead")
# Only show form if we have users and sources; otherwise disable
if users.empty or sources.empty:
    st.sidebar.info("Add Lead disabled until `users` and `sources` tables have rows.")
else:
    with st.sidebar.form(key="add_lead"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        owner = st.selectbox("Owner", users["name"].tolist())
        source = st.selectbox("Source", sources["name"].tolist())
        score = st.slider("Lead score", 0, 100, 50)
        submitted = st.form_submit_button("Create lead")
        if submitted:
            owner_id = int(users[users["name"] == owner]["id"].iloc[0])
            source_id = int(sources[sources["name"] == source]["id"].iloc[0])
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """INSERT INTO leads (name,email,phone,owner_id,source_id,lead_score,created_at,updated_at)
                           VALUES (:n,:e,:p,:o,:s,:score,NOW(),NOW())"""
                    ),
                    {"n": name, "e": email, "p": phone, "o": owner_id, "s": source_id, "score": score},
                )
            st.sidebar.success("Lead created. Refresh page to see.")

# Convert lead to opportunity
st.markdown("### Convert a lead to opportunity")
if f_leads.empty or stages.empty or users.empty:
    st.info("Conversion disabled: ensure leads, stages and users exist.")
else:
    with st.form("convert"):
        lead_choice = st.selectbox(
            "Lead",
            f_leads[["id", "name"]]
            .astype(str)
            .apply(lambda r: f"{r['id']} — {r['name']}", axis=1)
            .tolist(),
        )
        lead_id = int(lead_choice.split(" — ")[0])
        value = st.number_input("Opportunity value", min_value=0.0, step=100.0, value=5000.0)
        owner_sel = st.selectbox("Owner for opportunity", users["name"].tolist())
        stage_sel = st.selectbox("Initial stage", stages["name"].tolist())
        do_convert = st.form_submit_button("Convert lead")
        if do_convert:
            owner_id = int(users[users["name"] == owner_sel]["id"].iloc[0])
            stage_id = int(stages[stages["name"] == stage_sel]["id"].iloc[0])
            with engine.begin() as conn:
                # mark lead converted
                conn.execute(text("UPDATE leads SET status='CONVERTED', converted_at=NOW() WHERE id=:lid"), {"lid": lead_id})
                # create opportunity
                conn.execute(
                    text(
                        """INSERT INTO opportunities (lead_id, owner_id, stage_id, value, created_at, updated_at, stage_entered_at)
                           VALUES (:lid, :owner, :stage, :val, NOW(), NOW(), NOW())"""
                    ),
                    {"lid": lead_id, "owner": owner_id, "stage": stage_id, "val": value},
                )
                # reliably fetch last insert id in MySQL
                opp_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
                conn.execute(
                    text("INSERT INTO opportunity_stage_history (opportunity_id, stage_id, entered_at) VALUES (:opp,:stage,NOW())"),
                    {"opp": opp_id, "stage": stage_id},
                )
            st.success(f"Lead {lead_id} converted into opportunity {opp_id}. Refresh to see changes.")

# Export CSV of filtered leads or opportunities
st.markdown("### Export data")
export_choice = st.selectbox("Export", ["Leads (filtered)", "Opportunities (filtered)"])
if st.button("Download CSV"):
    if export_choice.startswith("Leads"):
        csv = f_leads.to_csv(index=False).encode("utf-8")
        st.download_button("Download Leads CSV", csv, file_name="leads_filtered.csv", mime="text/csv")
    else:
        csv = f_opps.to_csv(index=False).encode("utf-8")
        st.download_button("Download Opps CSV", csv, file_name="opps_filtered.csv", mime="text/csv")

st.markdown("---")
st.markdown("Built for an analytics-first BA workflow: SQL → pandas → dashboard. Use this to answer business questions like: How is pipeline trend vs. target? Which source gives highest win rate?")

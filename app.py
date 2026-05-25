import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BAOAN Churn Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F8F9FB; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
 
    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        border-left: 4px solid transparent;
    }
    .kpi-label { font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 700; margin-bottom: 2px; }
    .kpi-sub   { font-size: 12px; color: #9CA3AF; }
 
    /* Insight / callout boxes */
    .insight-danger {
        background: #FEF2F2; border-left: 4px solid #EF4444;
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 8px;
        font-size: 14px; color: #7F1D1D;
    }
    .insight-warning {
        background: #FFFBEB; border-left: 4px solid #F59E0B;
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 8px;
        font-size: 14px; color: #78350F;
    }
    .insight-info {
        background: #EFF6FF; border-left: 4px solid #3B82F6;
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 8px;
        font-size: 14px; color: #1E3A5F;
    }
    .insight-success {
        background: #F0FDF4; border-left: 4px solid #22C55E;
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 8px;
        font-size: 14px; color: #14532D;
    }
 
    /* Section headers */
    .section-header {
        font-size: 16px; font-weight: 700; color: #111827;
        margin-bottom: 4px; margin-top: 8px;
    }
    .section-sub { font-size: 13px; color: #6B7280; margin-bottom: 14px; }
 
    /* Action recommendation cards */
    .rec-card {
        background: white; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #F3F4F6;
    }
    .rec-title { font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 4px; }
    .rec-body  { font-size: 13px; color: #6B7280; }
 
    /* Sidebar */
    [data-testid="stSidebar"] { background: #1F2937; }
    [data-testid="stSidebar"] * { color: #F9FAFB !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label { color: #D1D5DB !important; font-size: 13px; }
 
    /* Divider */
    hr { border: none; border-top: 1px solid #E5E7EB; margin: 1.5rem 0; }
 
    /* Hide default Streamlit header/footer */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Data loading / generation ─────────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    """Load real data from upload, or generate realistic synthetic data."""
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            # Normalise the target column
            if "Attrition_Flag" in df.columns:
                if df["Attrition_Flag"].dtype == object:
                    df["Attrition_Flag"] = df["Attrition_Flag"].str.lower().str.contains("attrited").astype(int)
            return df
        except Exception:
            st.warning("Could not read file — showing demo data instead.")
 
    # ── Synthetic demo data matching the real dataset structure ──
    rng = np.random.default_rng(42)
    n = 10_127
 
    income_cats  = ["Less Than $40K", "$40K - $60K", "$60K - $80K", "$80K - $120K", "$120K +"]
    card_cats    = ["Blue", "Silver", "Gold", "Platinum"]
    edu_cats     = ["Uneducated", "High School", "College", "Graduate", "Post-Graduate", "Doctorate"]
    marital_cats = ["Single", "Married", "Divorced"]
    gender_cats  = ["M", "F"]
 
    income  = rng.choice(income_cats,  n, p=[0.35, 0.18, 0.22, 0.18, 0.07])
    card    = rng.choice(card_cats,    n, p=[0.93, 0.05, 0.015, 0.005])
    edu     = rng.choice(edu_cats,     n)
    marital = rng.choice(marital_cats, n, p=[0.47, 0.46, 0.07])
    gender  = rng.choice(gender_cats,  n)
 
    months_inactive  = rng.integers(0, 7, n)
    contacts         = rng.integers(0, 7, n)
    total_trans_ct   = rng.integers(10, 140, n)
    total_trans_amt  = rng.integers(500, 18_000, n).astype(float)
    customer_age     = rng.integers(26, 74, n)
    months_on_book   = rng.integers(13, 56, n)
    credit_limit     = rng.uniform(1_438, 34_516, n).round(1)
    revolving_bal    = rng.integers(0, 2_518, n)
    dependent_cnt    = rng.integers(0, 6, n)
 
    # Churn probability influenced by key drivers
    churn_prob = (
        0.05
        + 0.07 * (months_inactive >= 3)
        + 0.06 * (contacts >= 3)
        + 0.08 * (total_trans_ct < 40)
        + 0.04 * (revolving_bal == 0)
        + 0.03 * (income == "Less Than $40K")
        + 0.05 * (card == "Platinum")
    )
    churn_prob = np.clip(churn_prob + rng.normal(0, 0.03, n), 0, 1)
    attrition = (rng.random(n) < churn_prob).astype(int)
 
    return pd.DataFrame({
        "Attrition_Flag":        attrition,
        "Customer_Age":          customer_age,
        "Gender":                gender,
        "Dependent_count":       dependent_cnt,
        "Education_Level":       edu,
        "Marital_Status":        marital,
        "Income_Category":       income,
        "Card_Category":         card,
        "Months_on_book":        months_on_book,
        "Total_Trans_Ct":        total_trans_ct,
        "Total_Trans_Amt":       total_trans_amt,
        "Months_Inactive_12_mon": months_inactive,
        "Contacts_Count_12_mon": contacts,
        "Credit_Limit":          credit_limit,
        "Total_Revolving_Bal":   revolving_bal,
    })
 
 
# ── Risk scoring ──────────────────────────────────────────────────────────────
def add_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    score = pd.Series(0.0, index=df.index)
    if "Months_Inactive_12_mon" in df.columns:
        score += df["Months_Inactive_12_mon"].clip(0, 6) * 15
    if "Contacts_Count_12_mon" in df.columns:
        score += (df["Contacts_Count_12_mon"] >= 3).astype(int) * 20
    if "Total_Trans_Ct" in df.columns:
        score += ((df["Total_Trans_Ct"] < 40) * 25).astype(int)
    if "Total_Revolving_Bal" in df.columns:
        score += ((df["Total_Revolving_Bal"] == 0) * 15).astype(int)
    if "Total_Trans_Amt" in df.columns:
        q25 = df["Total_Trans_Amt"].quantile(0.25)
        score += ((df["Total_Trans_Amt"] < q25) * 10).astype(int)
 
    df["Risk_Score"] = score.clip(0, 100)
    df["Risk_Category"] = pd.cut(
        df["Risk_Score"],
        bins=[-1, 29, 59, 101],
        labels=["Low Risk 🟢", "Medium Risk 🟡", "High Risk 🔴"],
    )
    return df
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
COLOUR_CHURNED = "#EF4444"
COLOUR_ACTIVE  = "#22C55E"
COLOUR_NEUTRAL = "#3B82F6"
COLOUR_WARN    = "#F59E0B"
 
def churn_rate(df):
    return df["Attrition_Flag"].mean() * 100
 
def kpi_html(label, value, sub, border_color="#3B82F6"):
    return f"""
    <div class="kpi-card" style="border-left-color:{border_color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{border_color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""
 
def insight(text, kind="info"):
    return f'<div class="insight-{kind}">{text}</div>'
 
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Upload your data")
    uploaded = st.file_uploader("Excel (.xlsx) file", type=["xlsx"])
    st.markdown("---")
    st.markdown("## 🎛️ Filters")
    st.caption("Narrow down the customer segment you want to analyse.")
 
df_raw = load_data(uploaded)
df_raw = add_risk_score(df_raw)
 
# Build sidebar filters after data is loaded
with st.sidebar:
    gender_opts   = sorted(df_raw["Gender"].unique())          if "Gender"           in df_raw.columns else []
    income_opts   = sorted(df_raw["Income_Category"].unique()) if "Income_Category"  in df_raw.columns else []
    card_opts     = sorted(df_raw["Card_Category"].unique())   if "Card_Category"    in df_raw.columns else []
    marital_opts  = sorted(df_raw["Marital_Status"].unique())  if "Marital_Status"   in df_raw.columns else []
 
    sel_gender  = st.multiselect("Gender",         gender_opts,  default=gender_opts)
    sel_income  = st.multiselect("Income level",   income_opts,  default=income_opts)
    sel_card    = st.multiselect("Card type",      card_opts,    default=card_opts)
    sel_marital = st.multiselect("Marital status", marital_opts, default=marital_opts)
 
    age_min = int(df_raw["Customer_Age"].min()) if "Customer_Age" in df_raw.columns else 18
    age_max = int(df_raw["Customer_Age"].max()) if "Customer_Age" in df_raw.columns else 75
    age_range = st.slider("Age range", age_min, age_max, (age_min, age_max))
 
    risk_filter = st.multiselect(
        "Risk category",
        ["Low Risk 🟢", "Medium Risk 🟡", "High Risk 🔴"],
        default=["Low Risk 🟢", "Medium Risk 🟡", "High Risk 🔴"],
    )
    st.markdown("---")
    st.caption("BAOAN Customer Intelligence · v2.0")
 
# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_gender  and "Gender"           in df.columns: df = df[df["Gender"].isin(sel_gender)]
if sel_income  and "Income_Category"  in df.columns: df = df[df["Income_Category"].isin(sel_income)]
if sel_card    and "Card_Category"    in df.columns: df = df[df["Card_Category"].isin(sel_card)]
if sel_marital and "Marital_Status"   in df.columns: df = df[df["Marital_Status"].isin(sel_marital)]
if "Customer_Age" in df.columns:
    df = df[(df["Customer_Age"] >= age_range[0]) & (df["Customer_Age"] <= age_range[1])]
if risk_filter and "Risk_Category" in df.columns:
    df = df[df["Risk_Category"].isin(risk_filter)]
 
# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("# 📊 BAOAN Customer Churn Dashboard")
st.markdown(
    f"Analysing **{len(df):,}** customers after filters "
    f"({len(df_raw) - len(df):,} filtered out)"
)
st.markdown("---")
 
# ── KPI row ───────────────────────────────────────────────────────────────────
total      = len(df)
churned    = int(df["Attrition_Flag"].sum())
active     = total - churned
rate       = churn_rate(df)
high_risk  = int((df["Risk_Category"] == "High Risk 🔴").sum())
 
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.markdown(kpi_html("Total customers",   f"{total:,}",    "In selected segment", "#3B82F6"), unsafe_allow_html=True)
with k2: st.markdown(kpi_html("Churned",           f"{churned:,}",  "Lost customers",      "#EF4444"), unsafe_allow_html=True)
with k3: st.markdown(kpi_html("Churn rate",        f"{rate:.1f}%",  "Of selected segment", "#EF4444" if rate > 15 else "#F59E0B"), unsafe_allow_html=True)
with k4: st.markdown(kpi_html("Still active",      f"{active:,}",   f"{100-rate:.1f}% retained", "#22C55E"), unsafe_allow_html=True)
with k5: st.markdown(kpi_html("High-risk customers", f"{high_risk:,}", "Need immediate action", "#F59E0B"), unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── Plain-English Insights ────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 What the data is telling you</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Plain-English takeaways — no statistics degree needed.</div>', unsafe_allow_html=True)
 
col_ins1, col_ins2 = st.columns(2)
 
with col_ins1:
    # Inactivity insight
    if "Months_Inactive_12_mon" in df.columns:
        inactive_3plus = df[df["Months_Inactive_12_mon"] >= 3]
        if len(inactive_3plus) > 0:
            rate_inactive = churn_rate(inactive_3plus)
            st.markdown(
                insight(f"<b>⚠️ Inactivity is the #1 red flag.</b> Customers inactive for 3+ months "
                        f"churn at <b>{rate_inactive:.0f}%</b> — {rate_inactive/rate:.1f}× the average. "
                        f"That's <b>{len(inactive_3plus):,} customers</b> to watch.", "danger"),
                unsafe_allow_html=True,
            )
 
    # Transaction count insight
    if "Total_Trans_Ct" in df.columns:
        low_tx = df[df["Total_Trans_Ct"] < 40]
        if len(low_tx) > 0:
            st.markdown(
                insight(f"<b>📉 Low transaction count = early leaver.</b> "
                        f"{len(low_tx):,} customers made fewer than 40 transactions. "
                        f"Their churn rate is <b>{churn_rate(low_tx):.0f}%</b>. "
                        "Declining activity usually comes before cancellation.", "warning"),
                unsafe_allow_html=True,
            )
 
with col_ins2:
    # Contacts insight
    if "Contacts_Count_12_mon" in df.columns:
        high_contact = df[df["Contacts_Count_12_mon"] >= 3]
        if len(high_contact) > 0:
            st.markdown(
                insight(f"<b>📞 Frequent support contacts signal frustration.</b> "
                        f"{len(high_contact):,} customers contacted support 3+ times. "
                        f"Their churn rate: <b>{churn_rate(high_contact):.0f}%</b>. "
                        "These are likely unresolved issues, not happy engagement.", "danger"),
                unsafe_allow_html=True,
            )
 
    # Zero revolving balance
    if "Total_Revolving_Bal" in df.columns:
        zero_bal = df[df["Total_Revolving_Bal"] == 0]
        if len(zero_bal) > 0:
            st.markdown(
                insight(f"<b>💳 Zero revolving balance = disengaged.</b> "
                        f"{len(zero_bal):,} customers carry no revolving balance — "
                        f"churn rate of <b>{churn_rate(zero_bal):.0f}%</b>. "
                        "They're likely not using the card at all.", "warning"),
                unsafe_allow_html=True,
            )
 
st.markdown("---")
 
# ── Behaviour charts ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Customer behaviour insights</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">What separates customers who stay from those who leave.</div>', unsafe_allow_html=True)
 
b1, b2, b3 = st.columns(3)
 
with b1:
    if "Months_Inactive_12_mon" in df.columns:
        grp = (df.groupby("Months_Inactive_12_mon")["Attrition_Flag"]
                 .agg(churn_count="sum", total="count")
                 .reset_index())
        grp["churn_rate"] = grp["churn_count"] / grp["total"] * 100
        fig = px.bar(
            grp, x="Months_Inactive_12_mon", y="churn_rate",
            color="churn_rate",
            color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
            labels={"Months_Inactive_12_mon": "Months inactive", "churn_rate": "Churn rate (%)"},
            title="Churn rate by inactivity",
        )
        fig.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            title_font_size=13, margin=dict(t=40, b=10, l=10, r=10),
            height=280,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📌 More months inactive = higher churn rate. Act before 2 months.")
 
with b2:
    if "Contacts_Count_12_mon" in df.columns:
        grp2 = (df.groupby("Contacts_Count_12_mon")["Attrition_Flag"]
                  .agg(churn_count="sum", total="count")
                  .reset_index())
        grp2["churn_rate"] = grp2["churn_count"] / grp2["total"] * 100
        fig2 = px.bar(
            grp2, x="Contacts_Count_12_mon", y="churn_rate",
            color="churn_rate",
            color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
            labels={"Contacts_Count_12_mon": "Support contacts", "churn_rate": "Churn rate (%)"},
            title="Churn rate by support contacts",
        )
        fig2.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            title_font_size=13, margin=dict(t=40, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("📌 3+ contacts = frustration. Investigate recurring issues.")
 
with b3:
    if "Total_Trans_Ct" in df.columns:
        df["Trans_Bucket"] = pd.cut(
            df["Total_Trans_Ct"],
            bins=[0, 30, 50, 70, 100, 200],
            labels=["<30", "30–50", "50–70", "70–100", "100+"],
        )
        grp3 = (df.groupby("Trans_Bucket", observed=True)["Attrition_Flag"]
                  .mean().reset_index())
        grp3["churn_rate"] = grp3["Attrition_Flag"] * 100
        fig3 = px.bar(
            grp3, x="Trans_Bucket", y="churn_rate",
            color="churn_rate",
            color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
            labels={"Trans_Bucket": "Transaction count", "churn_rate": "Churn rate (%)"},
            title="Churn rate by transaction volume",
        )
        fig3.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            title_font_size=13, margin=dict(t=40, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("📌 Fewer than 30 transactions — highest churn. Reward them first.")
 
st.markdown("---")
 
# ── Profile charts ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">👥 Customer profile insights</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Which customer types are most at risk?</div>', unsafe_allow_html=True)
 
p1, p2 = st.columns(2)
 
with p1:
    if "Income_Category" in df.columns:
        income_order = ["Less Than $40K", "$40K - $60K", "$60K - $80K", "$80K - $120K", "$120K +"]
        inc_grp = (df.groupby("Income_Category")["Attrition_Flag"]
                     .mean().reset_index())
        inc_grp["churn_rate"] = inc_grp["Attrition_Flag"] * 100
        inc_grp["Income_Category"] = pd.Categorical(inc_grp["Income_Category"], categories=income_order, ordered=True)
        inc_grp = inc_grp.sort_values("Income_Category")
        fig_inc = px.bar(
            inc_grp, y="Income_Category", x="churn_rate",
            orientation="h",
            color="churn_rate",
            color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
            labels={"Income_Category": "", "churn_rate": "Churn rate (%)"},
            title="Churn rate by income level",
            text=inc_grp["churn_rate"].round(1).astype(str) + "%",
        )
        fig_inc.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            title_font_size=13, margin=dict(t=40, b=10, l=10, r=80),
            height=280,
        )
        fig_inc.update_traces(textposition="outside")
        st.plotly_chart(fig_inc, use_container_width=True)
        st.caption("📌 Lower-income customers churn more — value perception may be lower.")
 
with p2:
    if "Card_Category" in df.columns:
        card_grp = (df.groupby("Card_Category")["Attrition_Flag"]
                      .mean().reset_index())
        card_grp["churn_rate"] = card_grp["Attrition_Flag"] * 100
        card_grp = card_grp.sort_values("churn_rate", ascending=True)
        fig_card = px.bar(
            card_grp, y="Card_Category", x="churn_rate",
            orientation="h",
            color="churn_rate",
            color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
            labels={"Card_Category": "", "churn_rate": "Churn rate (%)"},
            title="Churn rate by card type",
            text=card_grp["churn_rate"].round(1).astype(str) + "%",
        )
        fig_card.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            title_font_size=13, margin=dict(t=40, b=10, l=10, r=80),
            height=280,
        )
        fig_card.update_traces(textposition="outside")
        st.plotly_chart(fig_card, use_container_width=True)
        st.caption("📌 Platinum holders churn most — they may not be getting value from premium benefits.")
 
st.markdown("---")
 
# ── Risk segmentation ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚦 Customer risk segmentation</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Every customer scored by their likelihood to leave.</div>', unsafe_allow_html=True)
 
r1, r2 = st.columns([1, 2])
 
with r1:
    risk_counts = df["Risk_Category"].value_counts().reset_index()
    risk_counts.columns = ["Risk Category", "Count"]
    colour_map = {
        "High Risk 🔴": "#EF4444",
        "Medium Risk 🟡": "#F59E0B",
        "Low Risk 🟢": "#22C55E",
    }
    fig_risk = px.pie(
        risk_counts, names="Risk Category", values="Count",
        color="Risk Category",
        color_discrete_map=colour_map,
        title="Risk distribution",
        hole=0.55,
    )
    fig_risk.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        title_font_size=13, margin=dict(t=40, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
        height=300,
    )
    fig_risk.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_risk, use_container_width=True)
 
with r2:
    for cat, col in [("High Risk 🔴", "#EF4444"), ("Medium Risk 🟡", "#F59E0B"), ("Low Risk 🟢", "#22C55E")]:
        seg = df[df["Risk_Category"] == cat]
        if len(seg) == 0:
            continue
        pct = len(seg) / len(df) * 100
        cr  = churn_rate(seg)
        labels = {"High Risk 🔴": "Need immediate outreach — retention offers or personal calls.",
                  "Medium Risk 🟡": "Show warning signs. Good target for re-engagement campaigns.",
                  "Low Risk 🟢": "Healthy and engaged. Maintain with loyalty rewards."}
        st.markdown(f"""
        <div style="background:white; border-radius:10px; padding:14px 18px; margin-bottom:10px;
                    border-left:4px solid {col}; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <div style="font-weight:700; font-size:15px; color:{col};">{cat}</div>
            <div style="font-size:22px; font-weight:700; color:#111827; margin:4px 0;">
                {len(seg):,} customers
                <span style="font-size:13px;font-weight:400;color:#6B7280;">
                  ({pct:.0f}% of segment · {cr:.0f}% churn rate)
                </span>
            </div>
            <div style="font-size:13px;color:#6B7280;">{labels[cat]}</div>
        </div>""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── Action recommendations ────────────────────────────────────────────────────
st.markdown('<div class="section-header">✅ Recommended actions</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Prioritised steps you can take right now to reduce churn.</div>', unsafe_allow_html=True)
 
actions = [
    ("🔴", "#FEF2F2", "#7F1D1D",
     f"Contact your {int((df['Risk_Category']=='High Risk 🔴').sum()):,} high-risk customers immediately",
     "Personalised retention offers — fee waivers, credit limit increases, or a proactive call — can recover 15–25% of at-risk customers before they leave."),
    ("🟡", "#FFFBEB", "#78350F",
     "Send a re-engagement campaign to inactive customers",
     f"{int((df.get('Months_Inactive_12_mon', pd.Series([])) >= 2).sum()) if 'Months_Inactive_12_mon' in df.columns else 'Many'} customers have been inactive for 2+ months. A personalised email with a compelling reason to transact (cashback, reward bonus) is your fastest win."),
    ("🟢", "#F0FDF4", "#14532D",
     "Launch a loyalty rewards programme for declining spenders",
     "Customers whose transaction amounts are dropping are early leavers. Reward-linked spending targets can reverse the decline before they churn."),
    ("🔵", "#EFF6FF", "#1E3A5F",
     "Fix the Platinum card value proposition",
     "Platinum holders have the highest churn rate of any card tier. Audit what benefits they're actually using vs what they're paying for, and close the gap."),
    ("🟠", "#FFF7ED", "#7C2D12",
     "Resolve root causes behind repeat support contacts",
     "Customers who called 3+ times have a significantly higher churn rate. Investigate whether there is a recurring issue — billing errors, feature gaps, or poor first-contact resolution — and fix it."),
]
 
for emoji, bg, text_col, title, body in actions:
    st.markdown(f"""
    <div style="background:{bg}; border-radius:10px; padding:14px 18px; margin-bottom:10px;
                box-shadow:0 1px 2px rgba(0,0,0,0.05);">
        <div style="font-size:15px; font-weight:600; color:{text_col}; margin-bottom:4px;">{emoji} {title}</div>
        <div style="font-size:13px; color:{text_col}; opacity:.85;">{body}</div>
    </div>""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── High-risk customer table ──────────────────────────────────────────────────
st.markdown('<div class="section-header">🔎 High-risk customer list</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Download or filter the exact customers who need attention.</div>', unsafe_allow_html=True)
 
high_risk_df = df[df["Risk_Category"] == "High Risk 🔴"].copy()
 
col_search, col_sort, col_dl = st.columns([2, 2, 1])
with col_sort:
    sort_by = st.selectbox(
        "Sort by",
        ["Risk_Score", "Months_Inactive_12_mon", "Total_Trans_Ct", "Contacts_Count_12_mon"],
        format_func=lambda x: {
            "Risk_Score": "Risk score (highest first)",
            "Months_Inactive_12_mon": "Months inactive",
            "Total_Trans_Ct": "Transaction count (lowest first)",
            "Contacts_Count_12_mon": "Support contacts",
        }.get(x, x),
    )
    asc = sort_by == "Total_Trans_Ct"
    high_risk_df = high_risk_df.sort_values(sort_by, ascending=asc)
 
with col_dl:
    st.markdown("<br>", unsafe_allow_html=True)
    csv = high_risk_df.to_csv(index=False).encode()
    st.download_button("⬇️ Export CSV", csv, "high_risk_customers.csv", "text/csv")
 
display_cols = [c for c in [
    "Customer_Age", "Gender", "Income_Category", "Card_Category",
    "Months_Inactive_12_mon", "Contacts_Count_12_mon",
    "Total_Trans_Ct", "Total_Trans_Amt", "Risk_Score",
] if c in high_risk_df.columns]
 
st.dataframe(
    high_risk_df[display_cols].head(200),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Risk_Score":               st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100),
        "Total_Trans_Amt":          st.column_config.NumberColumn("Transaction $", format="$%.0f"),
        "Months_Inactive_12_mon":   st.column_config.NumberColumn("Months inactive"),
        "Contacts_Count_12_mon":    st.column_config.NumberColumn("Support contacts"),
        "Total_Trans_Ct":           st.column_config.NumberColumn("Transaction count"),
    },
)
 
st.caption(f"Showing up to 200 of {len(high_risk_df):,} high-risk customers. Export CSV to see all.")

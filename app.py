import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Universal Customer Churn Dashboard", layout="wide")

st.title("Customer Churn Insights Dashboard")
st.write("Upload any customer churn dataset and select the important columns.")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Select Columns")

    columns = list(df.columns)

    churn_col = st.selectbox("Select churn/target column", columns)

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    spend_col = st.selectbox("Select spend/amount column (optional)", ["None"] + numeric_cols)
    activity_col = st.selectbox("Select activity/usage column (optional)", ["None"] + numeric_cols)
    tenure_col = st.selectbox("Select tenure/months column (optional)", ["None"] + numeric_cols)
    support_col = st.selectbox("Select support/contact column (optional)", ["None"] + numeric_cols)

    st.subheader("Business KPIs")

    total_customers = len(df)
    churned = df[churn_col].sum() if df[churn_col].dtype != "object" else df[churn_col].value_counts().min()
    churn_rate = round((churned / total_customers) * 100, 2)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Customers", total_customers)
    k2.metric("Estimated Churned Customers", int(churned))
    k3.metric("Churn Rate", f"{churn_rate}%")

    st.subheader("Churn Distribution")

    churn_counts = df[churn_col].value_counts().reset_index()
    churn_counts.columns = ["Churn Status", "Count"]

    fig = px.pie(
        churn_counts,
        names="Churn Status",
        values="Count",
        title="Customer Churn Distribution"
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Customer Behaviour Insights")

    col1, col2 = st.columns(2)

    with col1:
        if activity_col != "None":
            fig = px.box(
                df,
                x=churn_col,
                y=activity_col,
                title=f"{activity_col} by Churn Status"
            )
            st.plotly_chart(fig, width="stretch")

    with col2:
        if spend_col != "None":
            fig = px.box(
                df,
                x=churn_col,
                y=spend_col,
                title=f"{spend_col} by Churn Status"
            )
            st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        if tenure_col != "None":
            fig = px.histogram(
                df,
                x=tenure_col,
                color=churn_col,
                barmode="group",
                title=f"Churn by {tenure_col}"
            )
            st.plotly_chart(fig, width="stretch")

    with col4:
        if support_col != "None":
            fig = px.histogram(
                df,
                x=support_col,
                color=churn_col,
                barmode="group",
                title=f"Churn by {support_col}"
            )
            st.plotly_chart(fig, width="stretch")

    st.subheader("Categorical Churn Insights")

    for cat_col in categorical_cols[:4]:
        if cat_col != churn_col:
            cat_churn = df.groupby(cat_col)[churn_col].count().reset_index()
            cat_churn.columns = [cat_col, "Count"]

            fig = px.bar(
                cat_churn,
                x=cat_col,
                y="Count",
                title=f"Customer Count by {cat_col}"
            )
            st.plotly_chart(fig, width="stretch")

    st.subheader("Business Insights & Recommendations")

    st.info("""
    Key Insights:
    - The dashboard adapts to different customer churn datasets.
    - Churn behaviour can be compared across usage, spend, tenure, and support activity.
    - Customers with low activity, low spend, or high support contact may require attention.

    Recommendations:
    - Target high-risk customers with retention offers.
    - Re-engage inactive customers through campaigns.
    - Monitor support-heavy customers for dissatisfaction.
    - Use churn insights to prioritise customer retention strategies.
    """)

else:
    st.info("Upload a customer churn dataset to begin.")

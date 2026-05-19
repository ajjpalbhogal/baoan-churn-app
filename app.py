import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Universal Customer Churn Dashboard",
    layout="wide"
)

st.title("Customer Churn Insights Dashboard")

st.write(
    "Upload any customer churn dataset and generate insights automatically."
)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # Load dataset
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Preview
    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # Column selection
    st.subheader("Select Important Columns")

    columns = df.columns.tolist()

    churn_col = st.selectbox(
        "Select churn column",
        columns
    )

    numeric_cols = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    spend_col = st.selectbox(
        "Select spend column",
        ["None"] + numeric_cols
    )

    activity_col = st.selectbox(
        "Select activity/usage column",
        ["None"] + numeric_cols
    )

    tenure_col = st.selectbox(
        "Select tenure/months column",
        ["None"] + numeric_cols
    )

    support_col = st.selectbox(
        "Select support/contact column",
        ["None"] + numeric_cols
    )

    # KPIs
    st.subheader("Business KPIs")

    total_customers = len(df)

    churn_counts = df[churn_col].value_counts()

    churned = churn_counts.iloc[-1]

    churn_rate = round(
        (churned / total_customers) * 100,
        2
    )

    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Total Customers",
        total_customers
    )

    k2.metric(
        "Estimated Churned Customers",
        int(churned)
    )

    k3.metric(
        "Churn Rate",
        f"{churn_rate}%"
    )

    # Pie chart
    st.subheader("Churn Distribution")

    churn_df = churn_counts.reset_index()
    churn_df.columns = ["Churn Status", "Count"]

    fig = px.pie(
        churn_df,
        names="Churn Status",
        values="Count",
        title="Customer Churn Distribution"
    )

    st.plotly_chart(fig, width="stretch")

    # Behaviour insights
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

    # Recommendations
    st.subheader("Business Insights & Recommendations")

    st.info("""
    Key Insights:
    - Churn behaviour varies across customer activity and spending.
    - Customers with low activity may require retention efforts.
    - High support interaction may indicate dissatisfaction.

    Recommendations:
    - Target high-risk customers with retention offers.
    - Re-engage inactive customers.
    - Monitor customer support patterns closely.
    """)

else:
    st.info(
        "Please upload a CSV or Excel customer churn dataset."
    )

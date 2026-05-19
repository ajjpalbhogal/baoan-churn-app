import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BAOAN Churn Dashboard", layout="wide")

st.title("BAOAN Customer Churn Prediction Dashboard")

uploaded_file = st.file_uploader("Upload Customer Dataset", type=["csv", "xlsx"])

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Information")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", int(df.isnull().sum().sum()))

    if "Attrition_Flag" in df.columns:
        churned = df[df["Attrition_Flag"] == 1].shape[0]
        active = df[df["Attrition_Flag"] == 0].shape[0]
        churn_rate = round((churned / len(df)) * 100, 2)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Customers", len(df))
        k2.metric("Churned Customers", churned)
        k3.metric("Churn Rate", f"{churn_rate}%")
        k4.metric("Active Customers", active)

    st.subheader("Customer Behaviour Insights")

    col1, col2 = st.columns(2)

    with col1:
        if "Months_Inactive_12_mon" in df.columns and "Attrition_Flag" in df.columns:
            fig = px.histogram(df, x="Months_Inactive_12_mon", color="Attrition_Flag",
                               barmode="group", title="Churn by Months Inactive")
            st.plotly_chart(fig, width="stretch")

    with col2:
        if "Total_Trans_Ct" in df.columns and "Attrition_Flag" in df.columns:
            fig = px.box(df, x="Attrition_Flag", y="Total_Trans_Ct",
                         title="Transaction Count by Churn Status")
            st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        if "Total_Trans_Amt" in df.columns and "Attrition_Flag" in df.columns:
            fig = px.box(df, x="Attrition_Flag", y="Total_Trans_Amt",
                         title="Transaction Amount by Churn Status")
            st.plotly_chart(fig, width="stretch")

    with col4:
        if "Contacts_Count_12_mon" in df.columns and "Attrition_Flag" in df.columns:
            fig = px.histogram(df, x="Contacts_Count_12_mon", color="Attrition_Flag",
                               barmode="group", title="Churn by Customer Contact Count")
            st.plotly_chart(fig, width="stretch")

    st.subheader("Customer Profile Insights")

    col5, col6 = st.columns(2)

    with col5:
        if "Income_Category" in df.columns and "Attrition_Flag" in df.columns:
            income_churn = df.groupby("Income_Category")["Attrition_Flag"].mean().reset_index()
            income_churn["Churn Rate %"] = income_churn["Attrition_Flag"] * 100
            fig = px.bar(income_churn, x="Income_Category", y="Churn Rate %",
                         title="Churn Rate by Income Category")
            st.plotly_chart(fig, width="stretch")

    with col6:
        if "Card_Category" in df.columns and "Attrition_Flag" in df.columns:
            card_churn = df.groupby("Card_Category")["Attrition_Flag"].mean().reset_index()
            card_churn["Churn Rate %"] = card_churn["Attrition_Flag"] * 100
            fig = px.bar(card_churn, x="Card_Category", y="Churn Rate %",
                         title="Churn Rate by Card Category")
            st.plotly_chart(fig, width="stretch")

    st.subheader("Customer Risk Segmentation")

    if "Months_Inactive_12_mon" in df.columns and "Total_Trans_Ct" in df.columns:
        df["Risk_Category"] = "Low Risk"

        df.loc[
            (df["Months_Inactive_12_mon"] >= 3) &
            (df["Total_Trans_Ct"] < df["Total_Trans_Ct"].median()),
            "Risk_Category"
        ] = "High Risk"

        df.loc[
            (df["Months_Inactive_12_mon"] >= 2) &
            (df["Risk_Category"] != "High Risk"),
            "Risk_Category"
        ] = "Medium Risk"

        risk_counts = df["Risk_Category"].value_counts().reset_index()
        risk_counts.columns = ["Risk Category", "Count"]

        fig = px.bar(risk_counts, x="Risk Category", y="Count",
                     title="Customer Risk Categories")
        st.plotly_chart(fig, width="stretch")

        st.subheader("High Risk Customers")
        st.dataframe(df[df["Risk_Category"] == "High Risk"].head(20))

    st.subheader("Business Insights & Recommendations")

    st.info("""
    Key Insights:
    - Inactive customers show higher churn risk.
    - Customers with lower transaction counts need early attention.
    - High contact frequency may indicate dissatisfaction or service issues.

    Recommendations:
    - Target high-risk customers with retention offers.
    - Send re-engagement campaigns to inactive customers.
    - Provide loyalty rewards to customers with declining transaction activity.
    - Use customer risk categories for proactive support campaigns.
    """)

else:
    st.info("Please upload a CSV or Excel customer dataset to generate the dashboard.")

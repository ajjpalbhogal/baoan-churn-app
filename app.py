import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BAOAN Churn Dashboard", layout="wide")

st.title("BAOAN Customer Churn Prediction Dashboard")

uploaded_file = st.file_uploader(
    "Upload Customer Dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Information")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", int(df.isnull().sum().sum()))

    if "Attrition_Flag" in df.columns:

        churn_counts = (
            df["Attrition_Flag"]
            .value_counts()
            .reset_index()
        )

        churn_counts.columns = ["Status", "Count"]

        fig = px.pie(
            churn_counts,
            names="Status",
            values="Count",
            title="Customer Churn Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.success("Dashboard Generated Successfully")
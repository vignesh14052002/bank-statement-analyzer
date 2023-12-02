from dotenv import find_dotenv, load_dotenv

# Load .env file
load_dotenv(find_dotenv())

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.Visualize import plot_balance_trend, plot_monthly_spending, plot_portfolio
from utils.Analysis import filter_particulars, statement_info, particulars_filter_map


MERGED_STATEMENT_path = "./db/statement/merged_statement.csv"
mergedDF = pd.read_csv(MERGED_STATEMENT_path)


def main():
    st.title("Finance Dashboard")

    # Plot balance trend
    st.subheader("Balance Trend")
    st.pyplot(plot_balance_trend(mergedDF))

    # Plot monthly spending
    st.subheader("Monthly Spending")
    selected_particular = st.selectbox(
        "Select Particular", list(particulars_filter_map.keys())
    )
    selected_df = filter_particulars(
        mergedDF, particulars_filter_map[selected_particular]
    )
    st.pyplot(plot_monthly_spending(selected_df))

    # Plot portfolio
    st.subheader("Portfolio")
    mergedDF["DATE"] = pd.to_datetime(mergedDF["DATE"]).dt.date

    selected_date = st.slider(
        "Select Date range",
        mergedDF["DATE"].min(),
        mergedDF["DATE"].max(),
        mergedDF["DATE"].max(),
    )
    sliced_df = mergedDF[mergedDF["DATE"] <= selected_date]
    st.pyplot(plot_portfolio(sliced_df))


if __name__ == "__main__":
    main()

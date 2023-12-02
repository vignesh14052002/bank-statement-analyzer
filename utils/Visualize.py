import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.Analysis import get_portfolio


def merge_dataframes(df_list):
    df = pd.concat(df_list, ignore_index=True)
    df = df.sort_values(by="DATE")
    df["NET_AMOUNT"] = -df["WITHDRAWALS"] + df["DEPOSIT"]
    # Start and initial Balance
    df["NET_AMOUNT"].iloc[0] += df["BALANCE"].iloc[0]
    # Recalculate Net Balance
    df["BALANCE"] = df["NET_AMOUNT"].cumsum()

    return df


def plot_balance_trend(df):
    """
    Plots the balance trend from a merged DataFrame with 'DATE', 'BALANCE', and 'STATEMENT_TYPE' columns.

    Args:
        df (DataFrame): Merged DataFrame with 'DATE', 'BALANCE', and 'STATEMENT_TYPE' columns.

    Returns:
        None
    """
    df["DATE"] = pd.to_datetime(df["DATE"])

    # Sort the DataFrame by 'DATE'
    df.sort_values(by="DATE", inplace=True)

    # Create a plot for each statement type
    plt.figure(figsize=(10, 6))
    statement_types = df["STATEMENT_TYPE"].unique()
    for statement_type in statement_types:
        statement_df = df[df["STATEMENT_TYPE"] == statement_type]
        statement_df["BALANCE"] = statement_df["NET_AMOUNT"].cumsum()
        plt.plot(statement_df["DATE"], statement_df["BALANCE"], label=statement_type)

    # Plot the total balance
    plt.plot(df["DATE"], df["BALANCE"], label="Total Balance", color="black")
    plt.xlabel("Date")
    plt.ylabel("Balance")
    plt.title("Date vs. Balance")
    plt.grid(True)
    plt.legend()
    handle_sensitive_data_in_plot()
    return plt.gcf()


def plot_monthly_spending(df):
    df["DATE"] = pd.to_datetime(df["DATE"])
    df_group = df.groupby(df["DATE"].dt.strftime("%Y-%m"))
    net_df = df_group["WITHDRAWALS"].sum() - df_group["DEPOSIT"].sum()
    plt.figure(figsize=(10, 6))
    net_df.plot(kind="bar", color="skyblue")
    plt.xlabel("Month")
    plt.ylabel("Amount Spent (in currency)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    handle_sensitive_data_in_plot()
    return plt.gcf()


def plot_portfolio(mergedDF):
    [portfolio, portfolio_labels] = get_portfolio(mergedDF)
    portfolio = list(map(lambda x: x if x >= 0 else -x, portfolio))
    plt.cla()
    plt.pie(portfolio, labels=portfolio_labels, autopct="%1.1f%%")
    plt.title("Portfolio")
    plt.legend(portfolio)
    handle_sensitive_data_in_plot(plot_type="pie")
    return plt.gcf()


def handle_sensitive_data_in_plot(plot_type="bar"):
    if os.environ.get("DISPLAY_SENSITIVE_DATA") == "true":
        return
    # Hide sensitive data
    plt.yticks([])
    if plot_type == "pie":
        plt.legend([])

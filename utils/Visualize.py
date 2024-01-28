import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.Analysis import get_portfolio, particulars_filter_map
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), override=True)


def merge_dataframes(df_list):
    df = pd.concat(df_list, ignore_index=True)
    df = df.sort_values(by="DATE")
    df["WITHDRAWALS"] = df["WITHDRAWALS"].astype(
        float
    )  # Convert "withdrawals" column to float
    df["DEPOSIT"] = df["DEPOSIT"].astype(float)  # Convert "deposit" column to float
    df["NET_AMOUNT"] = -df["WITHDRAWALS"] + df["DEPOSIT"]
    # Start and initial Balance
    df["NET_AMOUNT"].iloc[0] += df["BALANCE"].iloc[0]
    # Recalculate Net Balance
    df["BALANCE"] = df["NET_AMOUNT"].cumsum()

    return df


def plot_balance_trend(df):
    df["DATE"] = pd.to_datetime(df["DATE"])

    # Sort the DataFrame by 'DATE'
    df.sort_values(by="DATE", inplace=True)

    # Create a plot for each statement type
    plt.figure(figsize=(10, 6))
    statement_types = df["STATEMENT_TYPE"].unique()
    for statement_type in statement_types:
        statement_df = df[df["STATEMENT_TYPE"] == statement_type]
        statement_df["BALANCE"] = statement_df["NET_AMOUNT"].cumsum()
        plt.plot(
            statement_df["DATE"],
            statement_df["BALANCE"],
            label=_get_balance_trend_plot_label(statement_df, statement_type),
        )

    ignored_filters = ["angel_one", "mutual_fund", "FD", "bonds"]
    filter_str = "|".join(map(lambda x: particulars_filter_map[x], ignored_filters))
    filtered_df = df[
        ~df["PARTICULARS"].str.contains(filter_str, regex=True, case=False)
    ]
    for filter in ignored_filters:
        _df = df[
            df["PARTICULARS"].str.contains(
                particulars_filter_map[filter], regex=True, case=False
            )
        ]
        _df["BALANCE"] = -_df["NET_AMOUNT"].cumsum()
        plt.plot(
            _df["DATE"],
            _df["BALANCE"],
            label=_get_balance_trend_plot_label(_df, filter),
        )

    filtered_df["BALANCE"] = filtered_df["NET_AMOUNT"].cumsum()
    plt.plot(
        filtered_df["DATE"],
        filtered_df["BALANCE"],
        label=_get_balance_trend_plot_label(filtered_df, "Net Worth"),
        color="black",
    )
    plt.xlabel("Date")
    plt.ylabel("Money (in Rupees)")
    plt.title("Date vs. Money (in Rupees)")
    plt.grid(True)
    plt.legend()
    handle_sensitive_data_in_plot()
    return plt.gcf()


def _get_balance_trend_plot_label(df, label):
    if os.environ.get("DISPLAY_SENSITIVE_DATA") == "true":
        return f"{label.ljust(10)} : {int(df['BALANCE'].iloc[-1])}"
    return label


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
    if os.getenv("DISPLAY_SENSITIVE_DATA") == "true":
        return
    # Hide sensitive data.
    plt.yticks([])
    if plot_type == "pie":
        plt.legend([])

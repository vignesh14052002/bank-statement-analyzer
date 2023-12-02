import re
import pandas as pd
import os
import json

current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
particulars_filter_map_path = os.path.join(
    parent_directory, "db", "statement", "particulars_filter_map.json"
)

with open(particulars_filter_map_path) as f:
    particulars_filter_map = json.load(f)


def filter_particulars(df, filter_str, column="PARTICULARS"):
    if filter_str is "None":
        # return entries that doesn't match any of those particulars_filter_map
        for key in particulars_filter_map:
            if not particulars_filter_map[key]:
                continue
            df = df[
                ~df[column].str.contains(
                    particulars_filter_map[key], regex=True, case=False
                )
            ]
        return df
    return df[df[column].str.contains(filter_str, regex=True, case=False)]


def statement_info(df):
    total_withdrawals = df["WITHDRAWALS"].sum()
    total_deposits = df["DEPOSIT"].sum()
    print("Total Withdrawals", total_withdrawals)
    print("Total Deposits", total_deposits)
    print("Net Withdrawal", total_withdrawals - total_deposits)


def __get_net_amount(df):
    series = df["NET_AMOUNT"].cumsum()
    if series.empty:
        return 0
    return series.iloc[-1]


def get_portfolio(mergedDF):
    portfolio_labels = [
        "Indian_Bank_savings",
        "ICICI_Bank_savings",
        "Indian_Bank_FD",
        "Stocks",
        "Mutual_Fund",
    ]
    statement_names = ["Indian Bank", "ICICI Bank"]
    portfolio = []
    for name in statement_names:
        portfolio.append(__get_net_amount(mergedDF[mergedDF["STATEMENT_TYPE"] == name]))

    fd_filtered = filter_particulars(mergedDF, particulars_filter_map["FD"])
    FD = -__get_net_amount(fd_filtered[(fd_filtered["WITHDRAWALS"] > 0)])
    portfolio.append(FD)
    angel_one = -__get_net_amount(
        filter_particulars(mergedDF, particulars_filter_map["angel_one"])
    )
    portfolio.append(angel_one)
    mutual_fund = -__get_net_amount(
        filter_particulars(mergedDF, particulars_filter_map["mutual_fund"])
    )
    portfolio.append(mutual_fund)
    return [portfolio, portfolio_labels]


def get_total_savings_percentage(mergedDF):
    [portfolio, portfolio_labels] = get_portfolio(mergedDF)
    total_net_worth = sum(portfolio)
    salary_df = filter_particulars(mergedDF, particulars_filter_map["soliton"])
    if salary_df.empty:
        return 0
    total_salary_received = salary_df["DEPOSIT"].sum()
    total_savings_percentage = (total_net_worth / total_salary_received) * 100
    return total_savings_percentage

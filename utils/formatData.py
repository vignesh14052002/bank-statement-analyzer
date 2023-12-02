import tabula
import os
import pandas as pd
import numpy as np


def clean_IndianBank_Data(df):
    df = df.dropna()
    cols = ["WITHDRAWALS", "DEPOSIT", "BALANCE"]
    df = df[df["WITHDRAWALS"] != "WITHDRAWALS"]
    for col in cols:
        df[col] = df[col].replace("-", "0")
        df[col] = df[col].replace("CR", "", regex=True)
        df[col] = pd.to_numeric(df[col])
    print("Data cleaned")
    return df


class DataFormatter:
    columns = {
        "IndianBank_Savings": [
            "DATE",
            "PARTICULARS",
            "WITHDRAWALS",
            "DEPOSIT",
            "BALANCE",
        ],
        "ICICI_Bank_Savings": ["Date", "Description", "Amount", "Type"],
        "ICICI_Credit_Card": ["Date", "Particulars", "Points", "Amount"],
    }

    def __init__(self, df, df_type="ICICI_Bank_Savings"):
        self.df = df
        self.df_type = df_type

    def convert_to_standard_dataframe(self):
        """
        IndianBank is set as standard

        Output Columns : DATE , PARTICULARS , WITHDRAWALS ,	DEPOSIT , BALANCE
        """
        self.check_missing_columns()
        df = pd.DataFrame()
        # Convert 'Date' column to datetime
        if "Date" in self.df.columns:
            self.df["Date"] = pd.to_datetime(self.df["Date"], format="%d-%m-%Y")
        elif "DATE" in self.df.columns:
            self.df["DATE"] = pd.to_datetime(self.df["DATE"], format="%d-%m-%Y")
        # Sort DataFrame by date in ascending order
        self.df = self.df.sort_values(by="Date")
        if self.df_type == "ICICI_Bank_Savings":
            df["DATE"] = self.df["Date"]
            df["PARTICULARS"] = self.df["Description"]
            df["WITHDRAWALS"] = np.where(self.df["Type"] == "DR", self.df["Amount"], 0)
            df["DEPOSIT"] = np.where(self.df["Type"] == "DR", 0, self.df["Amount"])
            self.df["NET_AMOUNT"] = self.df["Amount"] = np.where(
                self.df["Type"] == "DR", -self.df["Amount"], self.df["Amount"]
            )
            df["BALANCE"] = self.df["NET_AMOUNT"].cumsum()
            return df
        elif self.df_type == "ICICI_Credit_Card":
            df["DATE"] = self.df["Date"]
            df["PARTICULARS"] = self.df["Particulars"]
            self.df["Amount"] = self.df["Amount"].apply(lambda x: x.replace(",", ""))
            self.df["NET_AMOUNT"] = self.df["Amount"].apply(
                lambda x: float(x.split(" ")[0]) if "CR" in x else -float(x)
            )
            df["WITHDRAWALS"] = np.where(
                self.df["NET_AMOUNT"] < 0, -self.df["NET_AMOUNT"], 0
            )
            df["DEPOSIT"] = np.where(
                self.df["NET_AMOUNT"] < 0, 0, self.df["NET_AMOUNT"]
            )
            df["BALANCE"] = self.df["NET_AMOUNT"].cumsum()
            return df

    def check_missing_columns(self):
        # Check if all columns exist
        missing_columns = [
            col
            for col in DataFormatter.columns[self.df_type]
            if col not in self.df.columns
        ]
        if missing_columns:
            # Raise an exception with a message indicating the missing columns
            raise Exception(f"Missing columns: {', '.join(missing_columns)}")
        return len(missing_columns) == 0

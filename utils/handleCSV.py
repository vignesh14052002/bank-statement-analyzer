import tabula
import os
import pandas as pd


def combine_csv_files(directory):
    combined_df = pd.DataFrame()
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".csv"):
                file_path = os.path.join(root, filename)
                df = pd.read_csv(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def convert_pdf_to_csv(file_path, output_path):
    tabula.convert_into(file_path, output_path, output_format="csv", pages="all")


def convert_dir_pdf_to_csv(directory, output_file_path):
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".pdf"):
                file_path = os.path.join(root, filename)
                output_path = output_file_path + os.path.splitext(filename)[0] + ".csv"
                tabula.convert_into(
                    file_path, output_path, output_format="csv", pages="all"
                )

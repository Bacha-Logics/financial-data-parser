# financial_data_parser.py

import pandas as pd
import openpyxl
import numpy as np
import sqlite3
import re
from datetime import datetime, timedelta
from decimal import Decimal


class ExcelProcessor:
    def __init__(self):
        self.workbooks = {}

    def load_files(self, file_paths):
        for path in file_paths:
            self.workbooks[path] = pd.read_excel(path, sheet_name=None, engine="openpyxl")

    def get_sheet_info(self):
        for filename, sheets in self.workbooks.items():
            print(f"\nFile: {filename}")
            for sheet_name, df in sheets.items():
                print(f"  Sheet: {sheet_name}")
                print(f"    Dimensions: {df.shape}")
                print(f"    Columns: {list(df.columns)}")

    def extract_data(self, filename, sheet_name):
        return self.workbooks[filename][sheet_name]

    def preview_data(self, filename, sheet_name, rows=5):
        print(self.workbooks[filename][sheet_name].head(rows))


class DataTypeDetector:
    def detect_column_type(self, column_data):
        data = column_data.dropna().astype(str).tolist()
        if all(self.is_date(val) for val in data[:5]):
            return 'date'
        elif all(self.is_number(val) for val in data[:5]):
            return 'number'
        else:
            return 'string'

    def is_date(self, value):
        formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y", "%b %Y", "%B %Y"]
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except:
                continue
        if value.isdigit():
            try:
                base_date = datetime(1899, 12, 30)
                date = base_date + timedelta(days=int(value))
                return True
            except:
                return False
        return False

    def is_number(self, value):
        try:
            self.parse_number(value)
            return True
        except:
            return False

    def parse_number(self, value):
        value = value.replace(',', '').replace('(', '-').replace(')', '').strip()
        multiplier = 1
        if value.endswith('K'):
            multiplier = 1_000
            value = value[:-1]
        elif value.endswith('M'):
            multiplier = 1_000_000
            value = value[:-1]
        elif value.endswith('B'):
            multiplier = 1_000_000_000
            value = value[:-1]
        return float(value) * multiplier


class FormatParser:
    def parse_amount(self, value):
        if isinstance(value, (int, float)):
            return value
        if pd.isna(value):
            return np.nan
        value = str(value).replace('₹', '').replace('$', '').replace('€', '')
        value = value.replace('(', '-').replace(')', '').replace(',', '').strip()
        try:
            if value.endswith('K'):
                return float(value[:-1]) * 1_000
            elif value.endswith('M'):
                return float(value[:-1]) * 1_000_000
            elif value.endswith('B'):
                return float(value[:-1]) * 1_000_000_000
            elif value.endswith('-'):
                return -float(value[:-1])
            return float(value)
        except:
            return np.nan

    def parse_date(self, value):
        if isinstance(value, (int, float)) and 10000 < value < 60000:
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        value = str(value).strip()
        formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y", "%b %Y", "%B %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except:
                continue
        return np.nan


class FinancialDataStore:
    def __init__(self):
        self.data = {}
        self.indexes = {}
        self.metadata = {}

    def add_dataset(self, name, df, column_types):
        self.data[name] = df
        self.metadata[name] = column_types
        self.indexes[name] = {}

    def create_indexes(self, name, columns):
        df = self.data[name]
        for col in columns:
            self.indexes[name][col] = {}
            for idx, val in df[col].items():
                self.indexes[name][col].setdefault(val, []).append(idx)

    def query_by_criteria(self, name, column, value):
        if column in self.indexes[name]:
            rows = self.indexes[name][column].get(value, [])
            return self.data[name].loc[rows]
        return pd.DataFrame()

    def aggregate_data(self, name, group_by, measures):
        df = self.data[name]
        return df.groupby(group_by)[measures].sum()


# === Example usage ===
if __name__ == "__main__":
    # Phase 1: Load files
    processor = ExcelProcessor()
    processor.load_files(["KH_Bank.XLSX", "Customer_Ledger_Entries_FULL.xlsx"])
    processor.get_sheet_info()

    # Preview a sheet
    processor.preview_data("KH_Bank.XLSX", list(processor.workbooks["KH_Bank.XLSX"].keys())[0])

    # Phase 2 & 3: Detect types and parse
    detector = DataTypeDetector()
    parser = FormatParser()

    sheet_name = list(processor.workbooks["KH_Bank.XLSX"].keys())[0]
    df = processor.extract_data("KH_Bank.XLSX", sheet_name)

    column_types = {}
    for col in df.columns:
        col_type = detector.detect_column_type(df[col])
        column_types[col] = col_type
        if col_type == 'number':
            df[col] = df[col].apply(parser.parse_amount)
        elif col_type == 'date':
            df[col] = df[col].apply(parser.parse_date)

    print("\nDetected Column Types:")
    print(column_types)

    # Phase 4: Store and Query
    store = FinancialDataStore()
    store.add_dataset("bank_data", df, column_types)
    store.create_indexes("bank_data", [col for col, typ in column_types.items() if typ == "string"])

    # Sample Query
    some_value = df.iloc[0][list(df.columns)[0]]  # Get a sample value to query
    result = store.query_by_criteria("bank_data", list(df.columns)[0], some_value)
    print("\nQuery Result:")
    print(result.head())


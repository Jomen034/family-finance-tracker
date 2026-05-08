# services/sheets_service.py

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import uuid

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

client = gspread.authorize(creds)

SPREADSHEET_NAME = st.secrets["sheets"]["spreadsheet_name"]

spreadsheet = client.open(SPREADSHEET_NAME)

transactions_sheet = spreadsheet.worksheet("transactions")
transaction_names_sheet = spreadsheet.worksheet(
    "master_transaction_names"
)
budget_sheet = spreadsheet.worksheet("budgeting")


def get_transactions():
    data = transactions_sheet.get_all_records()

    if not data:
        return pd.DataFrame(
            columns=[
                "id",
                "date",
                "transaction_name",
                "category",
                "amount",
                "description",
                "created_at",
            ]
        )

    return pd.DataFrame(data)


def add_transaction(data):

    row = [
        str(uuid.uuid4()),
        data["date"],
        data["transaction_name"],
        data["category"],
        data["amount"],
        data["description"],
        data["created_at"],
    ]

    transactions_sheet.append_row(row)


def update_transaction(transaction_id, updated_data):

    records = transactions_sheet.get_all_records()

    for idx, record in enumerate(records, start=2):

        if record["id"] == transaction_id:

            transactions_sheet.update(
                f"B{idx}:F{idx}",
                [
                    [
                        updated_data["date"],
                        updated_data["transaction_name"],
                        updated_data["category"],
                        updated_data["amount"],
                        updated_data["description"],
                    ]
                ],
            )

            break


def get_transaction_names():

    data = transaction_names_sheet.get_all_records()

    return pd.DataFrame(data)


def get_budget_data():

    data = budget_sheet.get_all_records()

    return pd.DataFrame(data)


def update_budget_data(category, monthly_budget):

    records = budget_sheet.get_all_records()

    found = False

    for idx, record in enumerate(records, start=2):

        if record["category"] == category:

            budget_sheet.update(
                f"B{idx}",
                monthly_budget,
            )

            found = True

    if not found:

        budget_sheet.append_row(
            [
                category,
                monthly_budget,
            ]
        )

# services/sheets_service.py

import uuid

import gspread
import pandas as pd
import streamlit as st

from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# =========================
# GOOGLE AUTH
# =========================

creds_dict = st.secrets[
    "gcp_service_account"
]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES,
)

client = gspread.authorize(creds)

# =========================
# SPREADSHEET
# =========================

SPREADSHEET_NAME = st.secrets[
    "sheets"
]["spreadsheet_name"]

spreadsheet = client.open(
    SPREADSHEET_NAME
)

transactions_sheet = spreadsheet.worksheet(
    "transactions"
)

transaction_names_sheet = spreadsheet.worksheet(
    "master_transaction_names"
)

budget_sheet = spreadsheet.worksheet(
    "budgeting"
)

# =========================
# TRANSACTIONS
# =========================


@st.cache_data(ttl=30)
def get_transactions():

    data = transactions_sheet.get_all_records()

    expected_columns = [
        "id",
        "date",
        "name",
        "category",
        "amount",
        "description",
        "created_at",
    ]

    if not data:
        return pd.DataFrame(
            columns=expected_columns
        )

    df = pd.DataFrame(data)

    # CLEAN COLUMN NAMES
    df.columns = df.columns.str.strip()

    missing_cols = [
        col
        for col in expected_columns
        if col not in df.columns
    ]

    if missing_cols:
        raise Exception(
            f"Missing columns in transactions sheet: {missing_cols}"
        )

    # CLEAN AMOUNT
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(
            "Rp",
            "",
            regex=False,
        )
        .str.replace(
            ".",
            "",
            regex=False,
        )
        .str.replace(
            ",",
            "",
            regex=False,
        )
        .str.strip()
    )

    # TO NUMERIC
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    ).fillna(0)

    # DATE PARSING
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    return df


def add_transaction(data):

    required_keys = [
        "date",
        "name",
        "category",
        "amount",
        "description",
        "created_at",
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in data
    ]

    if missing_keys:
        raise Exception(
            f"Missing keys in add_transaction(): {missing_keys}"
        )

    row = [
        str(uuid.uuid4()),
        data["date"],
        data["name"],
        data["category"],
        int(data["amount"]),
        data["description"],
        data["created_at"],
    ]

    transactions_sheet.append_row(row)

    # CLEAR CACHE
    st.cache_data.clear()


def update_transaction(
    transaction_id,
    updated_data,
):

    required_keys = [
        "date",
        "name",
        "category",
        "amount",
        "description",
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in updated_data
    ]

    if missing_keys:
        raise Exception(
            f"Missing keys in update_transaction(): {missing_keys}"
        )

    records = transactions_sheet.get_all_records()

    for idx, record in enumerate(
        records,
        start=2,
    ):

        if record["id"] == transaction_id:

            transactions_sheet.update(
                f"B{idx}:F{idx}",
                [[
                    updated_data["date"],
                    updated_data["name"],
                    updated_data["category"],
                    int(updated_data["amount"]),
                    updated_data["description"],
                ]]
            )

            break

    # CLEAR CACHE
    st.cache_data.clear()


# =========================
# MASTER TRANSACTION NAMES
# =========================


@st.cache_data(ttl=30)
def get_transaction_names():

    data = transaction_names_sheet.get_all_records()

    expected_columns = [
        "id",
        "name",
        "category",
    ]

    if not data:
        return pd.DataFrame(
            columns=expected_columns
        )

    df = pd.DataFrame(data)

    df.columns = df.columns.str.strip()

    missing_cols = [
        col
        for col in expected_columns
        if col not in df.columns
    ]

    if missing_cols:
        raise Exception(
            f"Missing columns in master_transaction_names sheet: {missing_cols}"
        )

    return df


# =========================
# BUDGET
# =========================


@st.cache_data(ttl=30)
def get_budget_data():

    data = budget_sheet.get_all_records()

    expected_columns = [
        "name",
        "monthly_budget",
    ]

    if not data:
        return pd.DataFrame(
            columns=expected_columns
        )

    df = pd.DataFrame(data)

    df.columns = df.columns.str.strip()

    missing_cols = [
        col
        for col in expected_columns
        if col not in df.columns
    ]

    if missing_cols:
        raise Exception(
            f"Missing columns in budgeting sheet: {missing_cols}"
        )

    df["monthly_budget"] = pd.to_numeric(
        df["monthly_budget"],
        errors="coerce",
    ).fillna(0)

    return df


def update_budget_data(
    name,
    monthly_budget,
):

    records = budget_sheet.get_all_records()

    found = False

    for idx, record in enumerate(
        records,
        start=2,
    ):

        if record["name"] == name:

            budget_sheet.update(
                f"B{idx}",
                [[int(monthly_budget)]],
            )

            found = True
            break

    if not found:

        budget_sheet.append_row([
            name,
            int(monthly_budget),
        ])

    # CLEAR CACHE
    st.cache_data.clear()
"""Thin wrapper around gspread: one place that knows how to talk to the Sheet.

Every other service module reads/writes through here so caching and
credential handling only exist in one spot.
"""
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


@st.cache_resource
def _get_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_resource
def _get_spreadsheet():
    return _get_client().open_by_url(st.secrets["sheet"]["url"])


def get_worksheet(name: str):
    return _get_spreadsheet().worksheet(name)


@st.cache_data(ttl=30, show_spinner=False)
def read_table(name: str) -> pd.DataFrame:
    """Read a whole tab as a DataFrame. Cached for 30s so navigating between
    pages doesn't re-fetch the Sheet on every click; cleared automatically
    after any write (see clear_cache below)."""
    ws = get_worksheet(name)
    records = ws.get_all_records()
    return pd.DataFrame(records)


def clear_cache():
    read_table.clear()


def next_empty_row(sheet_name: str) -> int:
    ws = get_worksheet(sheet_name)
    return len(ws.get_all_values()) + 1


def find_row_by_id(sheet_name: str, id_col_name: str, id_value: str):
    """Returns the 1-indexed sheet row number for a given key value, or None."""
    ws = get_worksheet(sheet_name)
    header = ws.row_values(1)
    if id_col_name not in header:
        return None
    col_idx = header.index(id_col_name) + 1
    col_values = ws.col_values(col_idx)
    for i, v in enumerate(col_values[1:], start=2):
        if v == id_value:
            return i
    return None


def truthy(value) -> bool:
    """Google Sheets checkbox cells come back as real bools via gspread,
    but plain TRUE/FALSE text cells come back as strings - handle both."""
    if isinstance(value, bool):
        return value
    return str(value).strip().upper() in ("TRUE", "1", "YES")

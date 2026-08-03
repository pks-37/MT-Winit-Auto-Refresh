import os
import json
import sys
from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# -------------------------------------------------------
# Google Client
# -------------------------------------------------------

def get_client():

    # 1. Streamlit Secrets
    if "GOOGLE_CREDENTIALS" in st.secrets:
	print(type(st.secrets["GOOGLE_CREDENTIALS"]))

        creds = Credentials.from_service_account_info(
            json.loads(st.secrets["GOOGLE_CREDENTIALS"]),
            scopes=SCOPES
        )

    # 2. Environment Variable (Railway etc.)
    elif os.getenv("GOOGLE_CREDENTIALS"):

        creds = Credentials.from_service_account_info(
            json.loads(os.environ["GOOGLE_CREDENTIALS"]),
            scopes=SCOPES
        )

    # 3. Local credentials.json
    else:

        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent

        credentials_file = base_path / "credentials.json"

        creds = Credentials.from_service_account_file(
            credentials_file,
            scopes=SCOPES
        )

    return gspread.authorize(creds)


# -------------------------------------------------------
# Upload Function
# -------------------------------------------------------

def upload_dataframe(worksheet_name, df):

    client = get_client()

    spreadsheet = client.open("SFA Backend")
    worksheet = spreadsheet.worksheet(worksheet_name)

    worksheet.clear()

    worksheet.update(
        [df.columns.tolist()],
        "A1",
        value_input_option="USER_ENTERED"
    )

    rows = []

    for row in df.fillna("").values.tolist():

        new_row = []

        for value in row:

            if isinstance(value, pd.Timestamp):
                new_row.append(value.strftime("%m/%d/%Y"))
            else:
                new_row.append(value)

        rows.append(new_row)

    chunk_size = 5000
    total = len(rows)

    for i in range(0, total, chunk_size):

        worksheet.update(
            rows[i:i + chunk_size],
            f"A{i + 2}",
            value_input_option="USER_ENTERED"
        )

        print(f"Uploaded {min(i + chunk_size, total)}/{total} rows")

    print(f"✅ {worksheet_name} uploaded successfully!")
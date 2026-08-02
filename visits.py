import requests
import pandas as pd

from config import BASE_URL, HEADERS, LOGIN_USER
from google_sheets import upload_dataframe

def get_visits(start_date, end_date):

    url = f"{BASE_URL}/api/store-visits"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "loginUserCode": LOGIN_USER
    }

    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()

    return pd.DataFrame(response.json()["data"])


def clean_visits(df):

    # Remove unwanted rows
    df = df[df["teamLeaderName"] != "Vacant RTM South"]
    df = df[df["teamLeaderName"] != "Demo"]
    df = df[df["chainName"] != "GT"]
    df = df[df["chainName"] != "CPC"]

    # Convert date
    df["visitDate"] = pd.to_datetime(df["visitDate"])

    # Convert duration to HH:MM:SS
    df["durationSeconds"] = pd.to_timedelta(
        df["durationSeconds"],
        unit="s"
    ).astype(str)

    # Sort
    df = df.sort_values(
        by=[
            "visitDate",
            "chainName",
            "storeName",
            "durationSeconds"
        ],
        kind="stable"
    )


    # Rename columns
    df = df.rename(columns={
        "teamLeaderCode": "TL Code",
        "teamLeaderName": "TL Name",
        "userName": "Field User",
        "userCode": "Field User Code",
        "storeCode": "Store Code",
        "storeName": "Store Name",
        "chainName": "Chain Name",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "visitDate": "Date",
        "arrivalTime": "Check-in",
        "departureTime": "Check-out",
        "durationSeconds": "Total Time Spent",
        "visitPurpose": "Reason"
    })

    # Keep only required columns
    df = df[
        [
            "TL Code",
            "TL Name",
            "Field User",
            "Field User Code",
            "Store Code",
            "Store Name",
            "Chain Name",
            "Latitude",
            "Longitude",
            "Date",
            "Check-in",
            "Check-out",
            "Total Time Spent",
            "Reason"
        ]
    ]

    return df


def upload_visits(df):

    upload_dataframe("Visits_Clean", df)

def run_visits(start_date="2026-07-01", end_date="2026-07-31"):

    df = get_visits(start_date, end_date)
    df = clean_visits(df)
    upload_visits(df)


if __name__ == "__main__":
    run_visits()
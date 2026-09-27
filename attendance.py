import requests
import pandas as pd

from config import BASE_URL, LOGIN_USER, get_auth_headers
from google_sheets import upload_dataframe

def get_attendance(start_date, end_date):

    url = f"{BASE_URL}/api/user-wise-attendance"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "loginUserCode": LOGIN_USER
    }

    response = requests.get(url, params=params, headers=get_auth_headers())
    response.raise_for_status()

    return pd.DataFrame(response.json()["data"])


def clean_attendance(df):

    # Remove unwanted TL Names
    unwanted_tls = [
        "Gayathri K",
        "Admin",
        "Demo",
        "Dharmendra Singh Nahar",
        "N/A",
        "Test Team Leader",
        "Test User",
        "test_12",
        "Vacant Mumbai RTM",
        "Vacant RTM South"
    ]

    df = df[~df["tlName"].isin(unwanted_tls)]

    # Remove Demo Field User
    df = df[df["userName"] != "Demo"]

    # Convert & Sort Date
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

    df = df.sort_values(
        by=["date", "tlName", "userName"],
        kind="stable"
    )


    # Rename Columns
    df = df.rename(columns={
        "tlCode": "TL Code",
        "tlName": "TL Name",
        "userCode": "Field User Code",
        "userName": "Field User Name",
        "date": "Date",
        "isAutoEod": "EOD Type",
        "attendance": "Attendance",
        "profilePic": "Profile Image"
    })

    # Convert EOD Type
    df["EOD Type"] = df["EOD Type"].map({
        True: "Auto",
        False: "Manual"
    })

    # Serial Number
    df.insert(0, "S.No", range(1, len(df) + 1))

    # Final Columns
    df = df[
        [
            "S.No",
            "TL Code",
            "TL Name",
            "Field User Code",
            "Field User Name",
            "Date",
            "EOD Type",
            "Attendance",
            "Profile Image"
        ]
    ]

    return df


def upload_attendance(df):

    upload_dataframe("Attendance_Clean", df)

def run_attendance(start_date, end_date):

    df = get_attendance(start_date, end_date)
    df = clean_attendance(df)
    upload_attendance(df)


if __name__ == "__main__":
    run_attendance()
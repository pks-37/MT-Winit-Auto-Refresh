import requests
import pandas as pd

from config import BASE_URL, HEADERS, LOGIN_USER
from google_sheets import upload_dataframe


def get_sales(start_date, end_date):

    url = f"{BASE_URL}/api/daily-stock-sales/all"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "loginUserCode": LOGIN_USER
    }

    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()

    return pd.DataFrame(response.json()["transactions"])


def clean_sales(df):

    # Remove unwanted columns
    df = df.drop(columns=[
        "productCategory",
        "productCode",
        "storeCode",
        "cityCode",
        "regionCode"
    ])

    # Remove unwanted rows
    df = df[df["tlName"] != "Vacant RTM South"]
    df = df[df["chainName"] != "GT"]

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Sort
    df = df.sort_values(
    	by=[
        	"date",
        	"chainName",
        	"storeName",
        	"fieldUserName",
        	"productName"
    ],
    ascending=True,
    kind="stable"
)


    # Round Sale Value
    df["secondarySalesRevenue"] = (
        df["secondarySalesRevenue"]
        .round()
        .astype(int)
    )

    # Rename columns
    df = df.rename(columns={
        "date": "Date",
        "tlCode": "TL Code",
        "tlName": "TL Name",
        "fieldUserCode": "Emp ID",
        "fieldUserName": "OGP Name",
        "chainName": "Chain",
        "storeName": "Store Name",
        "productName": "Product Name",
        "openingStocks": "SOH Qty",
        "secondarySales": "Sale Qty",
        "secondarySalesRevenue": "Sale Val"
    })

    # Reorder columns
    df = df[
        [
            "Date",
            "TL Code",
            "TL Name",
            "Emp ID",
            "OGP Name",
            "Chain",
            "Store Name",
            "Product Name",
            "SOH Qty",
            "Sale Qty",
            "Sale Val"
        ]
    ]


    return df


def upload_sales(df):

    upload_dataframe("Sales_Clean", df)

def run_sales(start_date="2026-07-01", end_date="2026-07-31"):

    df = get_sales(start_date, end_date)
    df = clean_sales(df)
    upload_sales(df)


if __name__ == "__main__":
    run_sales()
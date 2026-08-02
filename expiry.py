import requests
import pandas as pd

from config import BASE_URL, HEADERS, LOGIN_USER
from google_sheets import upload_dataframe

session = requests.Session()


def get_expiry(start_date, end_date):

    # -----------------------------
    # Get all visits
    # -----------------------------

    url = f"{BASE_URL}/api/expiry/visits"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "loginUserCode": LOGIN_USER,
        "page": 1,
        "limit": 100000
    }

    response = session.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=(10,60)
    )

    response.raise_for_status()

    visits = response.json()["data"]

    rows = []

    total = len(visits)

    print(f"Found {total} visits")

    # -----------------------------
    # Loop through each visit
    # -----------------------------

    for i, visit in enumerate(visits, start=1):

        product_url = f"{BASE_URL}/api/expiry/products"

        product_params = {
            "visitedDate": visit["visitedDate"],
            "customerCode": visit["customerCode"],
            "fieldUserCode": visit["fieldUserCode"],
            "loginUserCode": LOGIN_USER
        }

        success = False

        for attempt in range(3):

            try:

                r = session.get(
                    product_url,
                    params=product_params,
                    headers=HEADERS,
                    timeout=(10,60)
                )

                r.raise_for_status()

                products = r.json().get("data", [])

                success = True

                break

            except requests.exceptions.RequestException:

                print(
                    f"\nRetry {attempt + 1}/3 : "
                    f"{visit['customerName']}"
                )

        if not success:

            print(
                f"\nSkipped : "
                f"{visit['customerName']}"
            )

            continue

        for product in products:

            rows.append({

                "Date": visit["visitedDate"],

                "TL Code": visit["tlCode"].strip(),

                "TL Name": visit["tlName"].strip(),

                "Field User Code": visit["fieldUserCode"],

                "Field User Name": visit["fieldUserName"],

                "Customer Name": visit["customerName"],

                "Chain Name": visit["chainName"],

                "ItemName": product["productName"],

                "ExpiryDate": product["expiryDate"],

                "ExpiryQty": product["quantity"]

            })

        print(
            f"\rProcessing {i}/{total}",
            end="",
            flush=True
        )

    print("\nFinished fetching expiry data.")

    return pd.DataFrame(rows)

def clean_expiry(df):

    # -----------------------------------
    # Remove GT
    # -----------------------------------

    df = df[df["Chain Name"] != "GT"]

    # -----------------------------------
    # Remove blank expiry dates
    # -----------------------------------

    df = df[df["ExpiryDate"].notna()]

    # -----------------------------------
    # Convert dates
    # -----------------------------------

    df["Date"] = pd.to_datetime(df["Date"])

    df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"])

    # -----------------------------------
    # Sort exactly like VBA
    # Customer Name
    # → Expiry Date
    # → Expiry Qty (Descending)
    # -----------------------------------

    df = df.sort_values(

        by=[
            "Customer Name",
            "ExpiryDate",
            "ExpiryQty"
        ],

        ascending=[
            True,
            True,
            False
        ],

        kind="stable"

    )

 
    # -----------------------------------
    # Final column order
    # -----------------------------------

    df = df[
        [
            "Date",
            "TL Code",
            "TL Name",
            "Field User Code",
            "Field User Name",
            "Customer Name",
            "Chain Name",
            "ItemName",
            "ExpiryDate",
            "ExpiryQty"
        ]
    ]

    return df

def upload_expiry(df):

    upload_dataframe("Aging_Clean", df)

def run_expiry(start_date="2026-07-01", end_date="2026-07-31"):

    print("=" * 50)
    print("        FARMLEY AGING REFRESH")
    print("=" * 50)

    df = get_expiry(start_date, end_date)

    print(f"\nFetched {len(df)} product rows")

    df = clean_expiry(df)

    print(f"Rows after cleaning : {len(df)}")

    upload_expiry(df)

    print("\n" + "=" * 50)
    print("           DONE ✓")
    print("=" * 50)


if __name__ == "__main__":
    run_expiry()
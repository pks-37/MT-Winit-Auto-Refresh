import json
import os

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://farmley-prod-v1-reports.winitsoftware.com"
SFA_URL = "https://farmley-prod-v1.winitsoftware.com/login"

LOGIN_USER = os.getenv("FARMLEY_LOGIN_USER")
PASSWORD = os.getenv("FARMLEY_PASSWORD")

SESSION_FILE = "farmley_session.json"


# ============================================================
# LOAD SAVED REPORTS COOKIE
# ============================================================

def load_saved_reports_cookie():

    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        for cookie in state.get("cookies", []):

            if (
                cookie.get("name") == "farmley_reports_session"
                and "farmley-prod-v1-reports.winitsoftware.com"
                in cookie.get("domain", "")
            ):
                return cookie.get("value")

    except Exception:
        return None

    return None


# ============================================================
# CREATE FRESH REPORTS SESSION AUTOMATICALLY
# ============================================================

def create_reports_session():

    print("Creating fresh Farmley Reports session...")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        context = browser.new_context()

        page = context.new_page()

        # ----------------------------------------------------
        # 1. Open SFA login
        # ----------------------------------------------------

        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("Farmley SFA opened.")

        # ----------------------------------------------------
        # 2. Login automatically
        # ----------------------------------------------------

        page.locator("input").nth(0).fill(LOGIN_USER)

        page.locator("input").nth(1).fill(PASSWORD)

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print("SFA login submitted.")

        # ----------------------------------------------------
        # 3. Wait for SFA dashboard
        # ----------------------------------------------------

        page.wait_for_timeout(5000)

        print("SFA dashboard loaded.")

        # ----------------------------------------------------
        # 4. Open Reports Dashboard
        # ----------------------------------------------------

        page.goto(
            BASE_URL,
            wait_until="networkidle",
            timeout=60000
        )

        print("Reports Dashboard opened.")

        # ----------------------------------------------------
        # 5. Allow Reports application to create cookie
        # ----------------------------------------------------

        page.wait_for_timeout(5000)

        # ----------------------------------------------------
        # 6. Save complete browser session
        # ----------------------------------------------------

        context.storage_state(
            path=SESSION_FILE
        )

        # ----------------------------------------------------
        # 7. Find Reports session cookie
        # ----------------------------------------------------

        cookies = context.cookies()

        reports_cookie = None

        for cookie in cookies:

            if cookie.get("name") == "farmley_reports_session":

                reports_cookie = cookie.get("value")

                break

        browser.close()

        # ----------------------------------------------------
        # 8. Validate cookie
        # ----------------------------------------------------

        if not reports_cookie:

            raise Exception(
                "Reports session cookie was not created."
            )

        print("Fresh Reports session saved.")

        return reports_cookie


# ============================================================
# GET AUTH HEADERS
# ============================================================

def get_auth_headers():

    # --------------------------------------------------------
    # First try existing saved session
    # --------------------------------------------------------

    cookie = load_saved_reports_cookie()

    if cookie:

        print("Using saved Reports session.")

        return {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0",
            "Cookie": f"farmley_reports_session={cookie}"
        }

    # --------------------------------------------------------
    # Saved session unavailable → create automatically
    # --------------------------------------------------------

    print("Saved Reports session unavailable.")

    cookie = create_reports_session()

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"farmley_reports_session={cookie}"
    }
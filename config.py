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

# Used on Vercel
REPORTS_COOKIE = os.getenv("FARMLEY_REPORTS_COOKIE")

# Used locally
SESSION_FILE = "farmley_session.json"


# ============================================================
# LOAD SAVED REPORTS COOKIE
# ============================================================

def load_saved_reports_cookie():

    # Vercel / Environment Variable
    if REPORTS_COOKIE:
        print("Using Reports cookie from environment variable.")
        return REPORTS_COOKIE

    # Local PC / saved session file
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
# CREATE FRESH REPORTS SESSION
# ============================================================

def create_reports_session():

    print("Creating fresh Farmley Reports session...")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()
        page = context.new_page()

        # Open SFA
        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("Farmley SFA opened.")

        # Login
        page.locator("input").nth(0).fill(LOGIN_USER)
        page.locator("input").nth(1).fill(PASSWORD)

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print("SFA login submitted.")

        # Wait for dashboard
        page.wait_for_timeout(5000)

        print("SFA dashboard loaded.")

        # Open Reports
        page.goto(
            BASE_URL,
            wait_until="networkidle",
            timeout=60000
        )

        print("Reports Dashboard opened.")

        # Allow cookie creation
        page.wait_for_timeout(5000)

        # Save local session
        context.storage_state(
            path=SESSION_FILE
        )

        # Find Reports cookie
        cookies = context.cookies()

        reports_cookie = None

        for cookie in cookies:

            if cookie.get("name") == "farmley_reports_session":

                reports_cookie = cookie.get("value")
                break

        browser.close()

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
    # 1. Vercel / Environment Variable
    # --------------------------------------------------------
    cookie = os.getenv("FARMLEY_REPORTS_COOKIE")

    if cookie:
        print("Using FARMLEY_REPORTS_COOKIE from environment.")
        return {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0",
            "Cookie": f"farmley_reports_session={cookie}"
        }

    # --------------------------------------------------------
    # 2. Local saved session
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
    # 3. Local machine only → create fresh session
    # --------------------------------------------------------
    print("Saved Reports session unavailable.")
    print("Creating fresh Reports session...")

    cookie = create_reports_session()

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"farmley_reports_session={cookie}"
    }
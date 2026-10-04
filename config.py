import json
import os

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://farmley-prod-v1-reports.winitsoftware.com"
SFA_URL = "https://farmley-prod-v1.winitsoftware.com/login"

LOGIN_USER = os.getenv("FARMLEY_LOGIN_USER")
PASSWORD = os.getenv("FARMLEY_PASSWORD")

# Used locally only
SESSION_FILE = "farmley_session.json"

# Cache fresh cookie during one request
_FRESH_COOKIE = None


# ============================================================
# CREATE FRESH REPORTS SESSION
# ============================================================

def create_reports_session():

    print("========================================")
    print("CREATING FRESH FARMLEY REPORTS SESSION")
    print("========================================")

    if not LOGIN_USER or not PASSWORD:
        raise Exception(
            "FARMLEY_LOGIN_USER or FARMLEY_PASSWORD is missing."
        )

    with sync_playwright() as p:

        # Vercel must run headless
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context()

        page = context.new_page()

        # ----------------------------------------------------
        # 1. Open SFA Login
        # ----------------------------------------------------

        print("Opening SFA login...")

        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("SFA login page opened.")

        # ----------------------------------------------------
        # 2. Login
        # ----------------------------------------------------

        page.locator("input").nth(0).fill(LOGIN_USER)
        page.locator("input").nth(1).fill(PASSWORD)

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print("Login submitted.")

        # ----------------------------------------------------
        # 3. Wait for SFA authentication
        # ----------------------------------------------------

        page.wait_for_timeout(5000)

        print("SFA authentication completed.")

        # ----------------------------------------------------
        # 4. Open Reports Dashboard
        # ----------------------------------------------------

        print("Opening Reports Dashboard...")

        page.goto(
            BASE_URL,
            wait_until="networkidle",
            timeout=60000
        )

        print("Reports Dashboard opened.")

        # Give Reports application time to create cookie
        page.wait_for_timeout(5000)

        # ----------------------------------------------------
        # 5. Extract fresh Reports cookie
        # ----------------------------------------------------

        cookies = context.cookies()

        reports_cookie = None

        for cookie in cookies:

            if cookie.get("name") == "farmley_reports_session":

                reports_cookie = cookie.get("value")

                break

        browser.close()

        # ----------------------------------------------------
        # 6. Validate
        # ----------------------------------------------------

        if not reports_cookie:

            raise Exception(
                "Reports session cookie was not created after login."
            )

        print("========================================")
        print("FRESH REPORTS COOKIE CREATED")
        print("========================================")

        return reports_cookie


# ============================================================
# GET AUTH HEADERS
# ============================================================

def get_auth_headers():

    global _FRESH_COOKIE

    # --------------------------------------------------------
    # IMPORTANT:
    # Create the cookie ONLY ONCE per Refresh Reports request.
    #
    # Sales → get_auth_headers()
    # Visits → get_auth_headers()
    # Attendance → get_auth_headers()
    # Aging → get_auth_headers()
    #
    # All four will reuse the same fresh cookie.
    # --------------------------------------------------------

    if _FRESH_COOKIE:

        print("Using freshly generated Reports session.")

        cookie = _FRESH_COOKIE

    else:

        print("No fresh session exists.")
        print("Logging into Winit to create a fresh Reports session...")

        cookie = create_reports_session()

        _FRESH_COOKIE = cookie

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"farmley_reports_session={cookie}"
    }
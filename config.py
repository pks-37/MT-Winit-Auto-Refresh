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

# Vercel environment variable
REPORTS_COOKIE = os.getenv("FARMLEY_REPORTS_COOKIE")

# Local session file
SESSION_FILE = "farmley_session.json"


# ============================================================
# LOAD SAVED REPORTS COOKIE
# ============================================================

def load_saved_reports_cookie():

    # Vercel / Environment Variable
    if REPORTS_COOKIE:
        print(
            "Using Reports cookie from environment variable.",
            flush=True
        )
        return REPORTS_COOKIE

    # Local PC / saved session file
    if not os.path.exists(SESSION_FILE):
        return None

    try:

        with open(
            SESSION_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            state = json.load(f)

        for cookie in state.get("cookies", []):

            if (
                cookie.get("name") == "farmley_reports_session"
                and
                "farmley-prod-v1-reports.winitsoftware.com"
                in cookie.get("domain", "")
            ):
                return cookie.get("value")

    except Exception as e:

        print(
            "Could not load saved Reports session:",
            str(e),
            flush=True
        )

    return None


# ============================================================
# CREATE FRESH REPORTS SESSION
# ============================================================

def create_reports_session():

    print(
        "Creating fresh Farmley Reports session...",
        flush=True
    )

    if not LOGIN_USER or not PASSWORD:
        raise Exception(
            "FARMLEY_LOGIN_USER or FARMLEY_PASSWORD is missing."
        )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context()

        page = context.new_page()

        # ----------------------------------------------------
        # OPEN SFA
        # ----------------------------------------------------

        print(
            "Opening SFA login...",
            flush=True
        )

        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print(
            "Farmley SFA opened.",
            flush=True
        )

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        page.locator("input").nth(0).fill(
            LOGIN_USER
        )

        page.locator("input").nth(1).fill(
            PASSWORD
        )

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print(
            "SFA login submitted.",
            flush=True
        )

        # ----------------------------------------------------
        # WAIT FOR SFA
        # ----------------------------------------------------

        page.wait_for_timeout(5000)

        print(
            "SFA authentication wait completed.",
            flush=True
        )

        print(
            "Current SFA URL:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # OPEN REPORTS
        # ----------------------------------------------------

        print(
            "Opening Reports Dashboard...",
            flush=True
        )

        page.goto(
            BASE_URL,
            wait_until="networkidle",
            timeout=60000
        )

        print(
            "Reports Dashboard opened.",
            flush=True
        )

        # Allow Reports application to create cookie
        page.wait_for_timeout(5000)

        print(
            "Reports URL:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # SAVE LOCAL SESSION
        # ----------------------------------------------------

        try:

            context.storage_state(
                path=SESSION_FILE
            )

        except Exception as e:

            print(
                "Could not save local session:",
                str(e),
                flush=True
            )

        # ----------------------------------------------------
        # FIND REPORTS COOKIE
        # ----------------------------------------------------

        cookies = context.cookies()

        print(
            "COOKIE NAMES:",
            json.dumps([
                {
                    "name": c.get("name"),
                    "domain": c.get("domain")
                }
                for c in cookies
            ]),
            flush=True
        )

        reports_cookie = None

        for cookie in cookies:

            if cookie.get("name") == "farmley_reports_session":

                reports_cookie = cookie.get("value")

                break

        browser.close()

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        if not reports_cookie:

            raise Exception(
                "Reports session cookie was not created."
            )

        print(
            "Fresh Reports session created successfully.",
            flush=True
        )

        return reports_cookie


# ============================================================
# GET AUTH HEADERS
# ============================================================

def get_auth_headers():

    # --------------------------------------------------------
    # 1. VERCEL ENVIRONMENT COOKIE
    # --------------------------------------------------------

    cookie = os.getenv(
        "FARMLEY_REPORTS_COOKIE"
    )

    if cookie:

        print(
            "Using FARMLEY_REPORTS_COOKIE from environment.",
            flush=True
        )

        return {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0",
            "Cookie": (
                f"farmley_reports_session={cookie}"
            )
        }

    # --------------------------------------------------------
    # 2. LOCAL SAVED SESSION
    # --------------------------------------------------------

    cookie = load_saved_reports_cookie()

    if cookie:

        print(
            "Using saved Reports session.",
            flush=True
        )

        return {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0",
            "Cookie": (
                f"farmley_reports_session={cookie}"
            )
        }

    # --------------------------------------------------------
    # 3. CREATE FRESH SESSION
    # --------------------------------------------------------

    print(
        "No saved Reports session available.",
        flush=True
    )

    print(
        "Creating fresh Reports session...",
        flush=True
    )

    cookie = create_reports_session()

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": (
            f"farmley_reports_session={cookie}"
        )
    }
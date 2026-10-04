import os
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://farmley-prod-v1-reports.winitsoftware.com"
SFA_URL = "https://farmley-prod-v1.winitsoftware.com/login"

LOGIN_USER = os.getenv("FARMLEY_LOGIN_USER")
PASSWORD = os.getenv("FARMLEY_PASSWORD")

_FRESH_COOKIE = None


# ============================================================
# CREATE FRESH REPORTS SESSION
# ============================================================

def create_reports_session():

    print("========================================", flush=True)
    print("CREATING FRESH WINIT REPORTS SESSION", flush=True)
    print("========================================", flush=True)

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

        print("Opening SFA login...", flush=True)

        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("SFA login opened.", flush=True)

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        inputs = page.locator("input")

        print(
            "Input count:",
            inputs.count(),
            flush=True
        )

        inputs.nth(0).fill(LOGIN_USER)
        inputs.nth(1).fill(PASSWORD)

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print("Login submitted.", flush=True)

        # Wait for SFA authentication
        page.wait_for_url(
            lambda url: "/login" not in url,
            timeout=30000
        )

        page.wait_for_timeout(3000)

        print(
            "SFA LOGIN SUCCESS:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # FIND NEW REPORTS
        # ----------------------------------------------------

        print("Finding New Reports...", flush=True)

        reports_link = page.get_by_text(
            "New Reports",
            exact=True
        )

        print(
            "New Reports elements:",
            reports_link.count(),
            flush=True
        )

        if reports_link.count() == 0:
            raise Exception(
                "New Reports link not found after SFA login."
            )

        # ----------------------------------------------------
        # CLICK NEW REPORTS
        # ----------------------------------------------------

        print("Clicking New Reports...", flush=True)

        reports_link.first.click()

        # Wait for Reports application
        page.wait_for_url(
            lambda url: "farmley-prod-v1-reports.winitsoftware.com"
            in url,
            timeout=60000
        )

        page.wait_for_timeout(5000)

        print(
            "Reports loaded:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # CAPTURE REPORTS COOKIE
        # ----------------------------------------------------

        cookies = context.cookies()

        reports_cookie = None

        for cookie in cookies:

            if (
                cookie.get("name")
                == "farmley_reports_session"
            ):

                reports_cookie = cookie.get("value")

                print(
                    "Reports cookie found.",
                    flush=True
                )

                print(
                    "Cookie domain:",
                    cookie.get("domain"),
                    flush=True
                )

                break

        browser.close()

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        if not reports_cookie:

            raise Exception(
                "Reports page opened successfully, "
                "but farmley_reports_session cookie was not found."
            )

        print("========================================", flush=True)
        print("FRESH REPORTS COOKIE CAPTURED", flush=True)
        print("========================================", flush=True)

        return reports_cookie


# ============================================================
# GET AUTH HEADERS
# ============================================================

def get_auth_headers():

    global _FRESH_COOKIE

    if _FRESH_COOKIE:

        print(
            "Using existing fresh Reports session.",
            flush=True
        )

        cookie = _FRESH_COOKIE

    else:

        print(
            "Creating fresh Reports authentication...",
            flush=True
        )

        cookie = create_reports_session()

        _FRESH_COOKIE = cookie

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"farmley_reports_session={cookie}"
    }
import os
import json

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"

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
    print("CREATING FRESH FARMLEY REPORTS SESSION", flush=True)
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
        # OPEN SFA LOGIN
        # ----------------------------------------------------

        print("Opening SFA login...", flush=True)

        page.goto(
            SFA_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("SFA login page opened.", flush=True)

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        page.locator("input").nth(0).fill(LOGIN_USER)
        page.locator("input").nth(1).fill(PASSWORD)

        page.get_by_role(
            "button",
            name="Sign In"
        ).click()

        print("Login submitted.", flush=True)

        # Give the authentication process time to complete
        page.wait_for_timeout(8000)

        print(
            "Current URL after login:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # INSPECT AUTHENTICATION ON SFA DOMAIN
        # ----------------------------------------------------

        sfa_cookies = context.cookies()

        print(
            "SFA COOKIES:",
            json.dumps([
                {
                    "name": c.get("name"),
                    "domain": c.get("domain"),
                    "path": c.get("path")
                }
                for c in sfa_cookies
            ]),
            flush=True
        )

        sfa_storage = page.evaluate(
            """() => ({
                localStorage: Object.keys(localStorage),
                sessionStorage: Object.keys(sessionStorage)
            })"""
        )

        print(
            "SFA STORAGE:",
            json.dumps(sfa_storage),
            flush=True
        )

        # ----------------------------------------------------
        # CAPTURE SFA STORAGE
        # ----------------------------------------------------

        try:

            sfa_storage = page.evaluate(
                """() => ({
                    localStorage: Object.keys(localStorage),
                    sessionStorage: Object.keys(sessionStorage)
                })"""
            )

            print(
                "SFA STORAGE:",
                json.dumps(sfa_storage),
                flush=True
            )

        except Exception as e:

            print(
                "Could not read SFA storage:",
                str(e),
                flush=True
            )

        # ----------------------------------------------------
        # OPEN REPORTS
        # ----------------------------------------------------

        print("Opening Reports Dashboard...", flush=True)

        page.goto(
            BASE_URL,
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_timeout(8000)

        print(
            "Reports Dashboard opened.",
            flush=True
        )

        print(
            "Reports URL:",
            page.url,
            flush=True
        )

        # ----------------------------------------------------
        # CAPTURE ALL COOKIES
        # ----------------------------------------------------

        cookies = context.cookies()

        print(
            "DEBUG COOKIES:",
            json.dumps([
                {
                    "name": c.get("name"),
                    "domain": c.get("domain"),
                    "path": c.get("path")
                }
                for c in cookies
            ]),
            flush=True
        )

        # ----------------------------------------------------
        # CAPTURE REPORTS STORAGE
        # ----------------------------------------------------

        try:

            reports_storage = page.evaluate(
                """() => ({
                    localStorage: Object.keys(localStorage),
                    sessionStorage: Object.keys(sessionStorage)
                })"""
            )

            print(
                "REPORTS STORAGE:",
                json.dumps(reports_storage),
                flush=True
            )

        except Exception as e:

            print(
                "Could not read Reports storage:",
                str(e),
                flush=True
            )

        # ----------------------------------------------------
        # BUILD COOKIE HEADER FROM WHATEVER EXISTS
        # ----------------------------------------------------

        cookie_header = "; ".join(
            f"{c['name']}={c['value']}"
            for c in cookies
        )

        browser.close()

        if not cookie_header:

            try:
                final_storage = page.evaluate(
                    """() => ({
                        localStorage: Object.keys(localStorage),
                        sessionStorage: Object.keys(sessionStorage)
                    })"""
                )
            except Exception:
                final_storage = {
                    "localStorage": "UNAVAILABLE",
                    "sessionStorage": "UNAVAILABLE"
                }

            raise Exception(
                "NO COOKIES | "
                f"SFA URL: {SFA_URL} | "
                f"REPORTS URL: {page.url} | "
                f"STORAGE: {json.dumps(final_storage)}"
            )

        print(
            "Authentication cookies captured successfully.",
            flush=True
        )

        return cookie_header


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
            "No fresh session exists.",
            flush=True
        )

        print(
            "Creating fresh Winit authentication session...",
            flush=True
        )

        cookie = create_reports_session()

        _FRESH_COOKIE = cookie

    return {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
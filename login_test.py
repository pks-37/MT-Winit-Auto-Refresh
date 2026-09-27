from playwright.sync_api import sync_playwright
from config import LOGIN_USER, PASSWORD

SFA_URL = "https://farmley-prod-v1.winitsoftware.com/login"
REPORTS_URL = "https://farmley-prod-v1-reports.winitsoftware.com/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 1. Open SFA login
    page.goto(SFA_URL, wait_until="networkidle")

    print("SFA login page opened.")

    # 2. Login automatically
    page.locator("input").nth(0).fill(LOGIN_USER)
    page.locator("input").nth(1).fill(PASSWORD)
    page.get_by_role("button", name="Sign In").click()

    print("Login submitted.")

    # 3. Wait for SFA dashboard
    page.wait_for_timeout(5000)

    print("SFA dashboard loaded.")

    # 4. Open Reports Dashboard
    page.goto(REPORTS_URL, wait_until="networkidle")

    print("Reports Dashboard opened.")

    # 5. Give the Reports application time to create its session
    page.wait_for_timeout(5000)

    # 6. Save complete browser session
    context.storage_state(path="farmley_session.json")

    print("SESSION SAVED!")

    # Keep browser open briefly so we can see what happened
    page.wait_for_timeout(3000)

    browser.close()
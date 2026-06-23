from playwright.sync_api import sync_playwright
import re

URL = "https://students-residents.aamc.org/applying-medical-school-amcas/amcas-program-participating-medical-schools-and-deadlines"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(5000)

    text = page.locator("body").inner_text()

    start_marker = "School Name\nState\nApplication Deadline\nCriminal Background Check"
    start = text.find(start_marker)

    if start == -1:
        print("Could not find table header.")
        browser.close()
        exit()

    table_text = text[start + len(start_marker):]

    end = table_text.find("Viewing 10 of 149")
    table_text = table_text[:end]

    print("\n========== ONLY TABLE ROWS ==========\n")
    print(table_text.strip())
    print("\n========== END ==========\n")

    browser.close()
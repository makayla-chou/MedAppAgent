from playwright.sync_api import sync_playwright
from pathlib import Path
import pandas as pd
import re
import time

URL = "https://students-residents.aamc.org/applying-medical-school-amcas/amcas-program-participating-medical-schools-and-deadlines"
OUTPUT_FILE = "data/amcas_medical_schools_deadlines.csv"

STATES = [
    "Alabama", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin"
]

DATE_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}"


def parse_row(row):
    row = row.strip()

    date_match = re.search(DATE_PATTERN, row)
    if not date_match:
        return None

    deadline = date_match.group(0)

    before_date = row[:date_match.start()]
    after_date = row[date_match.end():]

    if after_date.endswith("Yes"):
        criminal_background_check = "Yes"
    elif after_date.endswith("No"):
        criminal_background_check = "No"
    else:
        criminal_background_check = ""

    state = ""
    school_name = before_date

    for possible_state in sorted(STATES, key=len, reverse=True):
        if before_date.endswith(possible_state):
            state = possible_state
            school_name = before_date[:-len(possible_state)]
            break

    return {
        "school_name": school_name.strip(),
        "state": state.strip(),
        "application_deadline": deadline.strip(),
        "criminal_background_check": criminal_background_check.strip()
    }


def get_table_rows_from_page(page):
    text = page.locator("body").inner_text()

    start_marker = "School Name\nState\nApplication Deadline\nCriminal Background Check"

    start = text.find(start_marker)
    if start == -1:
        print("Could not find table header.")
        return []

    table_text = text[start + len(start_marker):]

    # Stop before the next "Viewing..." text.
    end_match = re.search(r"Viewing \d+ of \d+", table_text)
    if end_match:
        table_text = table_text[:end_match.start()]

    raw_rows = [
        line.strip()
        for line in table_text.split("\n")
        if line.strip()
    ]

    parsed_rows = []

    for row in raw_rows:
        parsed = parse_row(row)

        if parsed:
            parsed_rows.append(parsed)
        else:
            print("Could not parse:", row)

    return parsed_rows


def click_next_page(page):
    """
    Clicks the pagination next button/link if available.
    Returns True if it clicked successfully, False if no next page exists.
    """
    current_text = page.locator("body").inner_text()

    # Try obvious next button/link labels first.
    next_candidates = [
        page.get_by_role("link", name="Next"),
        page.get_by_role("button", name="Next"),
        page.locator("a[aria-label='Next']"),
        page.locator("button[aria-label='Next']"),
        page.locator("text=Next"),
    ]

    for candidate in next_candidates:
        try:
            if candidate.count() > 0 and candidate.first.is_visible():
                candidate.first.click()
                page.wait_for_timeout(1500)

                new_text = page.locator("body").inner_text()

                if new_text != current_text:
                    return True
        except Exception:
            pass

    return False


def click_page_number(page, page_number):
    """
    Clicks a page number directly.
    Returns True if successful.
    """
    old_text = page.locator("body").inner_text()

    try:
        page.get_by_text(str(page_number), exact=True).click()
        page.wait_for_timeout(1500)

        new_text = page.locator("body").inner_text()
        return new_text != old_text

    except Exception:
        return False


def scrape_all_pages():
    Path("data").mkdir(exist_ok=True)

    all_rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        # Scrape page 1 first.
        page_num = 1

        while True:
            print(f"\nScraping visible page {page_num}...")

            rows = get_table_rows_from_page(page)
            print(f"Rows found on page {page_num}: {len(rows)}")

            all_rows.extend(rows)

            # Try clicking next.
            clicked = click_next_page(page)

            if not clicked:
                print("No next page found. Stopping.")
                break

            page_num += 1

            # Safety stop so it does not loop forever.
            if page_num > 20:
                print("Safety stop reached.")
                break

            time.sleep(0.3)

        browser.close()

    df = pd.DataFrame(all_rows)

    df = df.drop_duplicates()

    df["application_deadline_date"] = pd.to_datetime(
        df["application_deadline"],
        errors="coerce"
    ).dt.date

    df = df.sort_values(["state", "school_name"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    print(df.head(20))


if __name__ == "__main__":
    scrape_all_pages()
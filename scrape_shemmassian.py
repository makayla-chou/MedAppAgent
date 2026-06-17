import pandas as pd
from pathlib import Path

URL = "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school"
OUTPUT_FILE = "data/shemmassian_med_school_stats.csv"


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).replace("\xa0", " ").strip()


def scrape_shemmassian():
    Path("data").mkdir(exist_ok=True)

    tables = pd.read_html(URL)

    print(f"Found {len(tables)} tables")

    for i, table in enumerate(tables):
        print(f"\nTable {i}")
        print(table.head())
        print(table.shape)

    df = tables[0]

    df.columns = [
        str(col).lower().strip().replace(" ", "_")
        for col in df.columns
    ]

    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # Find the school-name column
    school_col = None

    for col in df.columns:
        if "school" in col:
            school_col = col
            break

    if school_col is None:
        raise ValueError("Could not find the medical school name column.")

    # If school name ends in *, mark as public
    df["is_public"] = df[school_col].str.endswith("*")

    # Remove the * from the school name
    df[school_col] = (
        df[school_col]
        .str.replace(r"\*$", "", regex=True)
        .str.strip()
    )

    df = df.drop_duplicates()

    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    print(df.head(20))


if __name__ == "__main__":
    scrape_shemmassian()
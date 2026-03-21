"""
US Universities Crawler
Uses the College Scorecard API (data.ed.gov) to fetch data on all US institutions.

Usage:
  1. Copy .env.example to .env and add your API key from https://api.data.gov/signup/
  2. pip install -r requirements.txt
  3. python crawler.py
"""

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
PER_PAGE = 100
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "universities.csv"

FIELDS = [
    "id",
    "school.name",
    "school.city",
    "school.state",
    "school.zip",
    "school.school_url",
    "school.ownership",
    "school.carnegie_basic",
    "school.locale",
    "latest.admissions.admission_rate.overall",
    "latest.admissions.sat_scores.average.overall",
    "latest.admissions.act_scores.midpoint.cumulative",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.cost.avg_net_price.public",
    "latest.cost.avg_net_price.private",
    "latest.cost.attendance.academic_year",
    "latest.completion.completion_rate_4yr_150nt",
    "latest.student.size",
    "latest.student.retention_rate.four_year.full_time",
    "latest.earnings.10_yrs_after_entry.median",
    "latest.earnings.6_yrs_after_entry.median",
    "latest.aid.median_debt.completers.overall",
]

COLUMN_RENAME = {
    "id": "id",
    "school.name": "name",
    "school.city": "city",
    "school.state": "state",
    "school.zip": "zip",
    "school.school_url": "website",
    "school.ownership": "ownership",
    "school.carnegie_basic": "carnegie_type",
    "school.locale": "locale",
    "latest.admissions.admission_rate.overall": "admission_rate",
    "latest.admissions.sat_scores.average.overall": "sat_avg",
    "latest.admissions.act_scores.midpoint.cumulative": "act_midpoint",
    "latest.cost.tuition.in_state": "tuition_in_state",
    "latest.cost.tuition.out_of_state": "tuition_out_of_state",
    "latest.cost.avg_net_price.public": "avg_net_price_public",
    "latest.cost.avg_net_price.private": "avg_net_price_private",
    "latest.cost.attendance.academic_year": "cost_of_attendance",
    "latest.completion.completion_rate_4yr_150nt": "graduation_rate_4yr",
    "latest.student.size": "enrollment",
    "latest.student.retention_rate.four_year.full_time": "retention_rate",
    "latest.earnings.10_yrs_after_entry.median": "median_earnings_10yr",
    "latest.earnings.6_yrs_after_entry.median": "median_earnings_6yr",
    "latest.aid.median_debt.completers.overall": "median_debt",
}

OWNERSHIP_LABELS = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}


def fetch_page(page: int, session: requests.Session) -> dict:
    params = {
        "api_key": API_KEY,
        "fields": ",".join(FIELDS),
        "per_page": PER_PAGE,
        "page": page,
    }
    resp = session.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all() -> list[dict]:
    session = requests.Session()

    # First request to get total count
    print("Fetching total record count...")
    data = fetch_page(0, session)
    total = data["metadata"]["total"]
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    print(f"Found {total:,} institutions across {total_pages} pages.\n")

    records = list(data["results"])

    for page in tqdm(range(1, total_pages), desc="Fetching pages", unit="page"):
        try:
            data = fetch_page(page, session)
            records.extend(data["results"])
        except requests.HTTPError as e:
            print(f"\nHTTP error on page {page}: {e}. Retrying once...")
            time.sleep(2)
            data = fetch_page(page, session)
            records.extend(data["results"])

    return records


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)

    # Rename columns
    df = df.rename(columns=COLUMN_RENAME)

    # Map ownership codes to readable labels
    if "ownership" in df.columns:
        df["ownership"] = df["ownership"].map(OWNERSHIP_LABELS).fillna(df["ownership"])

    # Round float columns
    float_cols = ["admission_rate", "graduation_rate_4yr", "retention_rate"]
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].round(4)

    # Sort by name
    df = df.sort_values("name", ignore_index=True)

    return df


def main():
    if not API_KEY:
        print("Error: COLLEGE_SCORECARD_API_KEY not set.")
        print("1. Get a free key at https://api.data.gov/signup/")
        print("2. Create a .env file with: COLLEGE_SCORECARD_API_KEY=your_key_here")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    records = fetch_all()
    df = build_dataframe(records)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nDone! {len(df):,} records saved to {OUTPUT_FILE}")
    print(f"\nSample (5 rows):\n{df[['name', 'state', 'tuition_in_state', 'admission_rate', 'graduation_rate_4yr']].dropna(subset=['tuition_in_state']).head()}")


if __name__ == "__main__":
    main()

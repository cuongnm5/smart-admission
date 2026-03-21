"""
Academic Programs Crawler — College Scorecard API
Fetches program percentage fields for all US institutions.

Output: output/programs.csv
  - id: Scorecard institution ID (joins to universities.csv)
  - programs_offered: comma-separated list of programs with any enrollment
  - top_programs: top 3 programs by enrollment percentage
  - prog_*: raw percentage for each program area
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
OUTPUT_FILE = OUTPUT_DIR / "programs.csv"

# All available program_percentage fields in College Scorecard
# Maps API field suffix → human-readable label
PROGRAM_FIELDS = {
    "agriculture":                   "Agriculture",
    "resources":                     "Natural Resources",
    "architecture":                  "Architecture",
    "ethnic_cultural_gender":        "Ethnic/Cultural/Gender Studies",
    "communication":                 "Communication",
    "communications_technology":     "Communications Technology",
    "computer":                      "Computer Science",
    "personal_culinary":             "Culinary/Personal Services",
    "education":                     "Education",
    "engineering":                   "Engineering",
    "engineering_technology":        "Engineering Technology",
    "language":                      "Foreign Languages",
    "family_consumer_science":       "Family & Consumer Science",
    "legal":                         "Legal Studies",
    "english":                       "English",
    "humanities":                    "Liberal Arts/Humanities",
    "library":                       "Library Science",
    "biological":                    "Biological Sciences",
    "mathematics":                   "Mathematics & Statistics",
    "military":                      "Military Studies",
    "multidiscipline":               "Multidisciplinary Studies",
    "parks_recreation_fitness":      "Parks, Recreation & Fitness",
    "philosophy_religious":          "Philosophy & Religious Studies",
    "theology_religious_vocation":   "Theology",
    "physical_science":              "Physical Sciences",
    "science_technology":            "Science Technology",
    "psychology":                    "Psychology",
    "security_law_enforcement":      "Security & Law Enforcement",
    "public_administration_social_service": "Public Administration",
    "social_science":                "Social Sciences",
    "construction":                  "Construction Trades",
    "mechanic_repair_technology":    "Mechanic & Repair",
    "precision_production":          "Precision Production",
    "transportation":                "Transportation",
    "visual_performing":             "Visual & Performing Arts",
    "health":                        "Health Professions",
    "business_marketing":            "Business & Marketing",
    "history":                       "History",
}

API_FIELDS = ["id"] + [f"latest.academics.program_percentage.{k}" for k in PROGRAM_FIELDS]


def fetch_page(page: int, session: requests.Session) -> dict:
    params = {
        "api_key": API_KEY,
        "fields": ",".join(API_FIELDS),
        "per_page": PER_PAGE,
        "page": page,
    }
    resp = session.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def process_record(raw: dict) -> dict:
    record = {"id": raw.get("id")}

    # Extract program percentages
    prog_values = {}
    for key, label in PROGRAM_FIELDS.items():
        api_key = f"latest.academics.program_percentage.{key}"
        val = raw.get(api_key)
        try:
            val = float(val) if val is not None else None
        except (TypeError, ValueError):
            val = None
        record[f"prog_{key}"] = val
        if val and val > 0:
            prog_values[label] = val

    # programs_offered: all with any enrollment
    record["programs_offered"] = ", ".join(sorted(prog_values.keys())) if prog_values else None

    # top_programs: top 3 by percentage
    top3 = sorted(prog_values.items(), key=lambda x: x[1], reverse=True)[:3]
    record["top_programs"] = ", ".join(f"{name} ({pct:.0%})" for name, pct in top3) if top3 else None

    return record


def main():
    if not API_KEY:
        print("Error: COLLEGE_SCORECARD_API_KEY not set in .env")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    session = requests.Session()

    print("Fetching total record count...")
    data = fetch_page(0, session)
    total = data["metadata"]["total"]
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    print(f"Found {total:,} institutions across {total_pages} pages.\n")

    records = [process_record(r) for r in data["results"]]

    for page in tqdm(range(1, total_pages), desc="Fetching program data", unit="page"):
        try:
            data = fetch_page(page, session)
            records.extend(process_record(r) for r in data["results"])
        except requests.HTTPError as e:
            print(f"\nHTTP error on page {page}: {e}. Retrying...")
            time.sleep(2)
            data = fetch_page(page, session)
            records.extend(process_record(r) for r in data["results"])

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_FILE, index=False)

    has_programs = df["programs_offered"].notna().sum()
    print(f"\nDone! {len(df):,} records → {OUTPUT_FILE}")
    print(f"Schools with program data: {has_programs:,}")
    print(f"\nSample:\n{df[['id','top_programs']].dropna().head(5).to_string(index=False)}")


if __name__ == "__main__":
    main()

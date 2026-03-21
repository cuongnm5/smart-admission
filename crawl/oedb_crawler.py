"""
OEDB.org Crawler
Scrapes two datasets from oedb.org:

1. Program Rankings (14 disciplines) → output/oedb_rankings.csv
   - Uses requests + BeautifulSoup (static HTML)
   - Fields: rank, school, metrics (grad rate, retention, acceptance, etc.), address, description

2. School Directory (~3,500 schools) → output/oedb_schools.csv
   - Uses Playwright (Algolia JS-rendered pages)
   - Fields: name, type, location, degree levels, tuition

Usage:
  python oedb_crawler.py
"""

import time
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

OUTPUT_DIR = Path("output")
RANKINGS_FILE = OUTPUT_DIR / "oedb_rankings.csv"
SCHOOLS_FILE = OUTPUT_DIR / "oedb_schools.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

RANKING_PAGES = {
    "Accounting":            "https://www.oedb.org/rankings/online-accounting-programs/",
    "Business Administration": "https://www.oedb.org/rankings/online-business-administration-programs/",
    "Computer Science":      "https://www.oedb.org/rankings/online-computer-science-programs/",
    "Criminal Justice":      "https://www.oedb.org/rankings/online-criminal-justice-programs/",
    "Education":             "https://www.oedb.org/rankings/online-education-programs/",
    "Engineering":           "https://www.oedb.org/rankings/online-engineering-programs/",
    "Graphic Design":        "https://www.oedb.org/rankings/online-graphic-design-programs/",
    "IT":                    "https://www.oedb.org/rankings/online-it-programs/",
    "Marketing":             "https://www.oedb.org/rankings/online-marketing-programs/",
    "MBA":                   "https://www.oedb.org/rankings/online-mba-programs/",
    "Nursing":               "https://www.oedb.org/rankings/online-nursing-programs/",
    "Paralegal":             "https://www.oedb.org/rankings/online-paralegal-programs/",
    "PhD":                   "https://www.oedb.org/rankings/online-phd-programs/",
    "Psychology":            "https://www.oedb.org/rankings/online-psychology-programs/",
}

US_STATES = [
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new-hampshire", "new-jersey", "new-mexico", "new-york",
    "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode-island", "south-carolina", "south-dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west-virginia", "wisconsin", "wyoming", "district-of-columbia",
]


# ─── PART 1: Rankings ────────────────────────────────────────────────────────

def parse_ranking_row(row, discipline: str) -> dict:
    tds = row.find_all("td")
    if len(tds) < 9:
        return {}

    def text(td):
        return td.get_text(strip=True) if td else None

    name_td = tds[1]
    name_a = name_td.find("a")
    school_name = name_a.get_text(strip=True) if name_a else text(name_td)
    school_url = name_a.get("href") if name_a else None

    desc_td = row.find("td", class_="item-desc")
    description = desc_td.get_text(separator=" ", strip=True) if desc_td else None

    addr = row.find("div", {"itemprop": "address"})
    street = addr.find("div", {"itemprop": "streetAddress"}).get_text(strip=True) if addr and addr.find("div", {"itemprop": "streetAddress"}) else None
    city = addr.find("span", {"itemprop": "addressLocality"}).get_text(strip=True) if addr and addr.find("span", {"itemprop": "addressLocality"}) else None
    state = addr.find("span", {"itemprop": "addressRegion"}).get_text(strip=True) if addr and addr.find("span", {"itemprop": "addressRegion"}) else None
    zipcode = addr.find("span", {"itemprop": "postalCode"}).get_text(strip=True) if addr and addr.find("span", {"itemprop": "postalCode"}) else None

    buttons = row.find("td", class_="action-buttons")
    website = None
    program_page = None
    if buttons:
        links = buttons.find_all("a")
        if len(links) >= 1:
            website = links[0].get("href")
        if len(links) >= 2:
            program_page = links[1].get("href")

    logo_img = row.find("img", {"itemprop": "logo"})
    logo = logo_img.get("data-src") or logo_img.get("src") if logo_img else None

    return {
        "discipline": discipline,
        "rank": text(tds[0]),
        "school_name": school_name,
        "school_url": school_url,
        "student_faculty_ratio": text(tds[2]),
        "grad_rate": text(tds[3]),
        "retention_rate": text(tds[4]),
        "accept_rate": text(tds[5]),
        "enroll_rate": text(tds[6]),
        "aid_rate": text(tds[7]),
        "default_rate": text(tds[8]),
        "description": description,
        "street_address": street,
        "city": city,
        "state": state,
        "zip": zipcode,
        "website": website,
        "program_page": program_page,
        "logo_url": logo,
    }


def scrape_rankings() -> pd.DataFrame:
    print("\n=== Scraping Rankings (14 disciplines) ===")
    records = []

    for discipline, url in tqdm(RANKING_PAGES.items(), desc="Ranking pages"):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            tbody = soup.find("tbody", class_="rankings-table")
            if not tbody:
                print(f"  [!] No table found for {discipline}")
                continue

            for row in tbody.find_all("tr"):
                record = parse_ranking_row(row, discipline)
                if record:
                    records.append(record)

            time.sleep(0.5)
        except Exception as e:
            print(f"  [!] Error scraping {discipline}: {e}")

    df = pd.DataFrame(records)
    print(f"  → {len(df):,} ranking entries across {df['discipline'].nunique()} disciplines")
    return df


# ─── PART 2: School Directory (Playwright) ───────────────────────────────────

def parse_school_items(soup: BeautifulSoup) -> list[dict]:
    records = []
    # Items are wrapped in .ais-hits--item divs (Algolia rendered)
    containers = soup.find_all("div", class_="ais-hits--item")
    items_to_parse = [c.find("div", class_="data-item") or c for c in containers] if containers else soup.find_all("div", class_="data-item")
    for item in items_to_parse:
        name_span = item.find("span", {"itemprop": "name"})
        name = name_span.get_text(strip=True) if name_span else None

        url_a = item.find("a", {"itemprop": "url"})
        url = url_a.get("href") if url_a else None

        degrees_span = item.find("span", {"itemprop": "itemOffered"})
        degrees = degrees_span.get_text(strip=True) if degrees_span else None

        city_span = item.find("span", {"itemprop": "addressLocality"})
        city = city_span.get_text(strip=True).rstrip(",").strip() if city_span else None

        state_span = item.find("span", {"itemprop": "addressRegion"})
        state = state_span.get_text(strip=True) if state_span else None

        table_div = item.find("div", class_="data-header__table")
        tuition = None
        school_type = None
        if table_div:
            dls = table_div.find_all("dl")
            for dl in dls:
                dt = dl.find("dt")
                dd = dl.find("dd")
                if dt and dd:
                    label = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if "Tuition" in label:
                        tuition = value
                    elif "School Type" in label or "Type" in label:
                        school_type = value

        if name:
            records.append({
                "name": name,
                "url": url,
                "city": city,
                "state": state,
                "degree_levels": degrees,
                "tuition": tuition,
                "school_type": school_type,
            })
    return records


def scroll_and_collect(page, url: str, label: str) -> list[dict]:
    """Load a page, scroll until all Algolia results are loaded, parse all items."""
    from playwright.sync_api import TimeoutError as PWTimeout
    try:
        page.goto(url, timeout=30000)
        # Wait for first batch of results
        page.wait_for_selector(".ais-hits--item", timeout=15000)
    except PWTimeout:
        print(f"  [!] Timeout waiting for results on {label}")
        return []

    # Infinite scroll: keep scrolling until item count stabilises
    prev_count = 0
    stale_rounds = 0
    while stale_rounds < 3:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2500)
        count = page.locator(".ais-hits--item").count()
        if count == prev_count:
            stale_rounds += 1
        else:
            stale_rounds = 0
        prev_count = count

    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    return parse_school_items(soup)


def scrape_directory() -> pd.DataFrame:
    print("\n=== Scraping School Directory (Playwright + infinite scroll) ===")
    from playwright.sync_api import sync_playwright

    records = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Scrape the main accreditation page (all schools) first
        print("  Scraping main accreditation page...")
        items = scroll_and_collect(page, "https://www.oedb.org/accreditation/", "accreditation")
        records.extend(items)
        print(f"  → {len(items)} items from main page")

        # Also scrape each state page to catch any state-specific listings
        for state in tqdm(US_STATES, desc="State pages"):
            url = f"https://www.oedb.org/{state}/"
            items = scroll_and_collect(page, url, state)
            records.extend(items)

        browser.close()

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(subset=["name", "city", "state"])
        df = df.sort_values("name", ignore_index=True)
    print(f"  → {len(df):,} unique schools in directory")
    return df


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Part 1: Rankings
    df_rankings = scrape_rankings()
    df_rankings.to_csv(RANKINGS_FILE, index=False)
    print(f"  Saved → {RANKINGS_FILE}")

    # Part 2: School Directory
    df_schools = scrape_directory()
    df_schools.to_csv(SCHOOLS_FILE, index=False)
    print(f"  Saved → {SCHOOLS_FILE}")

    # Summary
    print("\n=== Done ===")
    print(f"  Rankings:  {len(df_rankings):,} rows  → {RANKINGS_FILE}")
    print(f"  Directory: {len(df_schools):,} rows  → {SCHOOLS_FILE}")

    if not df_rankings.empty:
        print(f"\nRankings sample:\n{df_rankings[['discipline','rank','school_name','grad_rate','accept_rate']].head()}")

    if not df_schools.empty:
        print(f"\nDirectory sample:\n{df_schools[['name','city','state','school_type','tuition']].head()}")


if __name__ == "__main__":
    main()

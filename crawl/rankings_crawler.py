"""
Rankings Crawler
Fetches university rankings from two sources:

1. Washington Monthly (2024) — direct Excel download
   → output/rankings_wm.csv

2. US News Best Colleges — Playwright scraper
   → output/rankings_usnews.csv
"""

import re
import io
import time
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

OUTPUT_DIR = Path("output")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def normalize(name) -> str:
    if pd.isna(name): return ""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


# ─── Washington Monthly ───────────────────────────────────────────────────────

WM_URLS = {
    "main":       "https://washingtonmonthly.com/wp-content/uploads/2024/08/Main-Rankings-2024.xlsx",
    "bang4buck":  "https://washingtonmonthly.com/wp-content/uploads/2024/08/Best-Bang-for-the-Buck-Rankings-2024.xlsx",
}

# Category keywords that appear in the sheet names/columns
WM_CATEGORY_MAP = {
    "national": "National Universities",
    "liberal":  "Liberal Arts Colleges",
    "master":   "Master's Universities",
    "bachelor": "Bachelor's Colleges",
    "regional": "Regional Colleges",
}

def detect_category(sheet_name: str) -> str:
    s = sheet_name.lower()
    for kw, label in WM_CATEGORY_MAP.items():
        if kw in s:
            return label
    return sheet_name


def clean_wm_rank(val) -> int | None:
    try:
        return int(str(val).strip().lstrip("#").split("-")[0])
    except Exception:
        return None


def parse_wm_sheet(xls, sheet_name: str, category: str, source: str) -> pd.DataFrame:
    """
    WM Excel sheets have:
      Row 0: group header (Social Mobility, Research, etc.)
      Row 1: column names
      Row 2+: data  (col 0 = rank, col 1 = school name with state in parens)
    """
    df = xls.parse(sheet_name, header=1).dropna(how="all")
    if df.empty:
        return pd.DataFrame()

    # Rename positional columns 0→rank, 1→school
    cols = list(df.columns)
    col_rename = {}
    if len(cols) > 0: col_rename[cols[0]] = "_rank"
    if len(cols) > 1: col_rename[cols[1]] = "_school"
    df = df.rename(columns=col_rename)

    # Normalise column names for the enrichment map
    df.columns = [re.sub(r"[^a-z0-9_]", "_", str(c).strip().lower()) for c in df.columns]

    records = []
    for _, row in df.iterrows():
        school_raw = str(row.get("_school", "")).strip()
        if not school_raw or school_raw.lower() in ("nan", "school", "institution", "name", "college"):
            continue

        # Strip trailing "(ST)" state abbreviation
        school_clean = re.sub(r"\s*\([A-Z]{2}\)\s*$", "", school_raw).strip()

        rec = {
            "school_name": school_clean,
            "wm_source":   source,
            "wm_category": category,
            "wm_rank":     clean_wm_rank(row.get("_rank")),
        }

        # Optional enrichment: map output col → keywords to search in column names
        col_map = {
            "wm_social_mobility_rank": ["social_mobility", "mobility_rank", "social_rank"],
            "wm_research_rank":        ["research_rank", "research"],
            "wm_service_rank":         ["service_rank", "service"],
            "wm_grad_rate_8yr":        ["8_year", "graduation_rate", "grad_rate"],
            "wm_pell_graduates":       ["number_of_pell", "pell_grad"],
            "wm_net_price":            ["net_price", "price_of_attendance"],
            "wm_earnings_rank":        ["earnings_performance", "earnings_rank", "median_earnings"],
        }
        for out_col, keywords in col_map.items():
            matched = next((c for c in df.columns if any(k in c for k in keywords) and c not in ("_rank","_school")), None)
            if matched:
                rec[out_col] = row.get(matched)

        records.append(rec)

    return pd.DataFrame(records)


def scrape_washington_monthly() -> pd.DataFrame:
    print("\n=== Washington Monthly Rankings (Excel download) ===")
    all_frames = []

    for source_key, url in WM_URLS.items():
        print(f"  Downloading {source_key}...")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            xls = pd.ExcelFile(io.BytesIO(resp.content))
            print(f"  Sheets: {xls.sheet_names}")

            for sheet in xls.sheet_names:
                try:
                    category = detect_category(sheet)
                    df_parsed = parse_wm_sheet(xls, sheet, category, source_key)
                    if not df_parsed.empty:
                        all_frames.append(df_parsed)
                        print(f"    Sheet '{sheet}' ({category}): {len(df_parsed)} schools")
                except Exception as e:
                    print(f"    [!] Error parsing sheet '{sheet}': {e}")

        except Exception as e:
            print(f"  [!] Error downloading {source_key}: {e}")

    if not all_frames:
        return pd.DataFrame()

    df = pd.concat(all_frames, ignore_index=True)
    df["_key"] = df["school_name"].apply(normalize)

    # Keep best (lowest) rank per school across duplicate sheets
    df = df.sort_values("wm_rank", na_position="last").drop_duplicates(subset=["_key", "wm_category"])
    print(f"  → {len(df):,} total WM ranking entries")
    return df


# ─── US News ─────────────────────────────────────────────────────────────────

USNEWS_CATEGORIES = [
    ("national-universities",      "https://www.usnews.com/best-colleges/rankings/national-universities"),
    ("national-liberal-arts",      "https://www.usnews.com/best-colleges/rankings/national-liberal-arts-colleges"),
    ("regional-universities-north","https://www.usnews.com/best-colleges/rankings/regional-universities-north"),
    ("regional-universities-south","https://www.usnews.com/best-colleges/rankings/regional-universities-south"),
    ("regional-universities-midwest","https://www.usnews.com/best-colleges/rankings/regional-universities-midwest"),
    ("regional-universities-west", "https://www.usnews.com/best-colleges/rankings/regional-universities-west"),
]


def scrape_usnews() -> pd.DataFrame:
    print("\n=== US News Rankings (Playwright, HTTP/1.1) ===")
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    from bs4 import BeautifulSoup

    records = []

    with sync_playwright() as p:
        # --disable-http2 forces HTTP/1.1, bypassing ERR_HTTP2_PROTOCOL_ERROR blocks
        browser = p.chromium.launch(headless=True, args=["--disable-http2"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        for category, url in tqdm(USNEWS_CATEGORIES, desc="US News categories"):
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                # Try to wait for ranking list
                try:
                    page.wait_for_selector("[class*='RankingItem'], [class*='ranking-item'], [data-testid*='ranking'], li[class*='college'], [class*='SearchResultsCard']", timeout=12000)
                except PWTimeout:
                    pass  # try parsing anyway

                # Scroll to load more results
                for _ in range(6):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1500)

                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                # Try multiple selector patterns US News uses
                selectors = [
                    ("[class*='RankingItem']", "rank-number", "heading"),
                    ("li[class*='college']", "[class*='rank']", "h3"),
                    ("[class*='SearchResultsCard']", "[class*='rank']", "h3"),
                    ("[data-testid='ranking-item']", "[data-testid='rank']", "[data-testid='school-name']"),
                ]

                found = []
                for container_sel, rank_sel, name_sel in selectors:
                    items = soup.select(container_sel)
                    if not items:
                        continue
                    for item in items:
                        rank_el = item.select_one(rank_sel) if rank_sel else None
                        name_el = item.select_one(name_sel) if name_sel else None
                        rank_text = rank_el.get_text(strip=True) if rank_el else None
                        name_text = name_el.get_text(strip=True) if name_el else None
                        if name_text:
                            try:
                                rank_num = int(re.search(r"\d+", rank_text or "").group()) if rank_text else None
                            except Exception:
                                rank_num = None
                            found.append({"school_name": name_text, "usnews_rank": rank_num, "usnews_category": category})
                    if found:
                        break

                # Fallback: look for embedded JSON
                if not found:
                    scripts = soup.find_all("script", type=["application/json", "application/ld+json"])
                    for script in scripts:
                        try:
                            import json
                            data = json.loads(script.string or "")
                            # Try to find itemListElement (schema.org)
                            items = data.get("itemListElement") or (data if isinstance(data, list) else [])
                            for item in items[:200]:
                                name = item.get("name") or (item.get("item", {}) or {}).get("name")
                                pos = item.get("position")
                                if name:
                                    found.append({"school_name": name, "usnews_rank": pos, "usnews_category": category})
                            if found:
                                break
                        except Exception:
                            pass

                if found:
                    records.extend(found)
                    print(f"  {category}: {len(found)} schools")
                else:
                    print(f"  [!] {category}: No results found (site may have blocked)")

                time.sleep(1.5)

            except Exception as e:
                print(f"  [!] Error on {category}: {e}")

        browser.close()

    if not records:
        print("  [!] US News scraping returned no results (likely blocked).")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["_key"] = df["school_name"].apply(normalize)
    df = df.drop_duplicates(subset=["_key"])
    print(f"  → {len(df):,} total US News ranking entries")
    return df


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df_wm = scrape_washington_monthly()
    if not df_wm.empty:
        df_wm.drop(columns=["_key"], errors="ignore").to_csv(OUTPUT_DIR / "rankings_wm.csv", index=False)
        print(f"  Saved → output/rankings_wm.csv ({len(df_wm):,} rows)")

    df_usnews = scrape_usnews()
    if not df_usnews.empty:
        df_usnews.drop(columns=["_key"], errors="ignore").to_csv(OUTPUT_DIR / "rankings_usnews.csv", index=False)
        print(f"  Saved → output/rankings_usnews.csv ({len(df_usnews):,} rows)")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()

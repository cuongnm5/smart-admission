"""
Merges all crawled datasets into one master CSV for analysis.

Sources:
  - output/universities.csv      (College Scorecard, DoE API — 6,429 schools)
  - output/oedb_schools.csv      (OEDB school directory — 928 schools)
  - output/oedb_rankings.csv     (OEDB discipline rankings — 305 entries, 14 disciplines)
  - output/programs.csv          (College Scorecard academic programs — 6,429 schools)
  - output/rankings_wm.csv       (Washington Monthly rankings — ~2,888 entries)

Output:
  - output/universities_master.csv
"""

import re
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("output")


def normalize_name(name) -> str:
    if pd.isna(name): return ""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def load_sources():
    scorecard   = pd.read_csv(OUTPUT_DIR / "universities.csv")
    oedb_schools  = pd.read_csv(OUTPUT_DIR / "oedb_schools.csv")
    oedb_rankings = pd.read_csv(OUTPUT_DIR / "oedb_rankings.csv")
    programs      = pd.read_csv(OUTPUT_DIR / "programs.csv")
    wm            = pd.read_csv(OUTPUT_DIR / "rankings_wm.csv")
    return scorecard, oedb_schools, oedb_rankings, programs, wm


def enrich_from_oedb_schools(base: pd.DataFrame, oedb: pd.DataFrame) -> pd.DataFrame:
    oedb_clean = oedb.rename(columns={
        "url":          "oedb_url",
        "degree_levels": "oedb_degree_levels",
        "tuition":      "oedb_tuition",
        "school_type":  "oedb_school_type",
    })[["name", "oedb_url", "oedb_degree_levels", "oedb_tuition", "oedb_school_type"]]
    oedb_clean["_key"] = oedb_clean["name"].apply(normalize_name)
    oedb_clean = oedb_clean.drop(columns=["name"]).drop_duplicates(subset=["_key"])
    base["_key"] = base["name"].apply(normalize_name)
    return base.merge(oedb_clean, on="_key", how="left")


def enrich_from_oedb_rankings(base: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    rankings["_key"] = rankings["school_name"].apply(normalize_name)

    pivot = rankings.pivot_table(index="_key", columns="discipline", values="rank", aggfunc="first")
    pivot.columns = [f"oedb_rank_{c.lower().replace(' ', '_')}" for c in pivot.columns]
    pivot = pivot.reset_index()

    def disciplines_list(key):
        ranked = rankings[rankings["_key"] == key]
        return ", ".join(sorted(ranked["discipline"].tolist())) if not ranked.empty else None

    def best_rank(key):
        ranked = rankings[rankings["_key"] == key]["rank"]
        if ranked.empty: return None
        try: return int(ranked.astype(int).min())
        except: return None

    pivot["oedb_disciplines_ranked"] = pivot["_key"].apply(disciplines_list)
    pivot["oedb_best_rank"] = pivot["_key"].apply(best_rank)

    first = (rankings.sort_values("rank").drop_duplicates(subset=["_key"])
             [["_key", "student_faculty_ratio", "description", "logo_url"]]
             .rename(columns={"student_faculty_ratio": "oedb_student_faculty_ratio",
                              "description": "oedb_description", "logo_url": "oedb_logo_url"}))
    pivot = pivot.merge(first, on="_key", how="left")
    return base.merge(pivot, on="_key", how="left")


def enrich_from_programs(base: pd.DataFrame, programs: pd.DataFrame) -> pd.DataFrame:
    """Join program data by Scorecard ID (exact match)."""
    prog_cols = ["id", "programs_offered", "top_programs"] + \
                [c for c in programs.columns if c.startswith("prog_")]
    programs_clean = programs[prog_cols].drop_duplicates(subset=["id"])
    # Convert id to same type
    base["id"] = pd.to_numeric(base["id"], errors="coerce")
    programs_clean = programs_clean.copy()
    programs_clean["id"] = pd.to_numeric(programs_clean["id"], errors="coerce")
    return base.merge(programs_clean, on="id", how="left")


def enrich_from_washington_monthly(base: pd.DataFrame, wm: pd.DataFrame) -> pd.DataFrame:
    """
    Washington Monthly has two types of rankings:
    - Main: national/liberal arts/bachelor's/master's → wm_rank, wm_category + sub-ranks
    - Best Bang for Buck: regional → wm_bang_for_buck_rank, wm_bang_region
    """
    wm["_key"] = wm["school_name"].apply(normalize_name)

    # Split into main rankings vs bang-for-buck
    main_sources = wm[wm["wm_source"] == "main"].copy()
    b4b_sources  = wm[wm["wm_source"] == "bang4buck"].copy()

    # ── Main rankings ────────────────────────────────────────────────────────
    # One row per school (keep the lowest rank if duplicated)
    main_clean = (
        main_sources
        .sort_values("wm_rank", na_position="last")
        .drop_duplicates(subset=["_key"])
        [["_key", "wm_rank", "wm_category",
          "wm_social_mobility_rank", "wm_research_rank", "wm_service_rank",
          "wm_grad_rate_8yr", "wm_pell_graduates", "wm_net_price"]]
    )

    # ── Best Bang for Buck ───────────────────────────────────────────────────
    b4b_base_cols = ["_key", "wm_rank", "wm_category"]
    b4b_opt_cols  = [c for c in ["wm_earnings_rank", "wm_net_price"] if c in b4b_sources.columns]
    b4b_clean = (
        b4b_sources
        .sort_values("wm_rank", na_position="last")
        .drop_duplicates(subset=["_key"])
        [b4b_base_cols + b4b_opt_cols]
        .rename(columns={
            "wm_rank":     "wm_bang_for_buck_rank",
            "wm_category": "wm_bang_region",
            "wm_net_price":"wm_b4b_net_price",
        })
    )

    merged = base.merge(main_clean, on="_key", how="left")
    merged = merged.merge(b4b_clean, on="_key", how="left")
    return merged


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    priority = [
        "name", "city", "state", "zip", "ownership", "carnegie_type",
        # Programs
        "programs_offered", "top_programs",
        # Admissions
        "admission_rate", "sat_avg", "act_midpoint",
        # Cost
        "tuition_in_state", "tuition_out_of_state", "cost_of_attendance",
        "avg_net_price_public", "avg_net_price_private",
        # Outcomes
        "graduation_rate_4yr", "retention_rate", "enrollment",
        "median_earnings_6yr", "median_earnings_10yr", "median_debt",
        # Washington Monthly rankings
        "wm_rank", "wm_category",
        "wm_social_mobility_rank", "wm_research_rank", "wm_service_rank",
        "wm_grad_rate_8yr", "wm_pell_graduates",
        "wm_bang_for_buck_rank", "wm_bang_region", "wm_earnings_rank",
        # OEDB program rankings
        "oedb_disciplines_ranked", "oedb_best_rank", "oedb_student_faculty_ratio",
        # OEDB school info
        "oedb_school_type", "oedb_degree_levels", "oedb_tuition",
        # Links
        "website", "oedb_url",
        "oedb_description",
    ]
    oedb_rank_cols = sorted([c for c in df.columns if c.startswith("oedb_rank_")])
    prog_raw_cols  = sorted([c for c in df.columns if c.startswith("prog_")])
    rest = [c for c in df.columns
            if c not in priority and c not in oedb_rank_cols and c not in prog_raw_cols
            and not c.startswith("_")]

    ordered = (
        [c for c in priority if c in df.columns]
        + oedb_rank_cols
        + [c for c in rest if c in df.columns]
        + prog_raw_cols   # raw percentages last (still accessible, not cluttering view)
    )
    return df[ordered]


def main():
    print("Loading datasets...")
    scorecard, oedb_schools, oedb_rankings, programs, wm = load_sources()
    print(f"  Scorecard:          {len(scorecard):,} rows")
    print(f"  OEDB schools:       {len(oedb_schools):,} rows")
    print(f"  OEDB rankings:      {len(oedb_rankings):,} rows ({oedb_rankings['discipline'].nunique()} disciplines)")
    print(f"  Programs:           {len(programs):,} rows ({programs['programs_offered'].notna().sum():,} with data)")
    print(f"  Washington Monthly: {len(wm):,} rows")

    print("\nMerging OEDB school directory...")
    master = enrich_from_oedb_schools(scorecard, oedb_schools)
    print(f"  Matched {master['oedb_url'].notna().sum():,} schools")

    print("Merging OEDB program rankings...")
    master = enrich_from_oedb_rankings(master, oedb_rankings)
    print(f"  Matched {master['oedb_disciplines_ranked'].notna().sum():,} schools")

    print("Merging academic programs...")
    master = enrich_from_programs(master, programs)
    print(f"  Matched {master['programs_offered'].notna().sum():,} schools")

    print("Merging Washington Monthly rankings...")
    master = enrich_from_washington_monthly(master, wm)
    print(f"  Main rankings: {master['wm_rank'].notna().sum():,} schools")
    print(f"  Bang for Buck: {master['wm_bang_for_buck_rank'].notna().sum():,} schools")

    print("Reordering columns...")
    master = reorder_columns(master)

    out_path = OUTPUT_DIR / "universities_master.csv"
    master.to_csv(out_path, index=False)

    print(f"\n=== Done ===")
    print(f"  Output:  {out_path}")
    print(f"  Rows:    {len(master):,}")
    print(f"  Cols:    {len(master.columns)}")

    # Spot-check famous schools
    check = master[master["name"].str.contains("Massachusetts Institute|Harvard|Stanford|MIT", case=False, na=False)]
    if not check.empty:
        cols = ["name", "wm_rank", "wm_category", "oedb_best_rank", "top_programs"]
        cols = [c for c in cols if c in master.columns]
        print(f"\nSpot-check (MIT/Harvard/Stanford):\n{check[cols].to_string(index=False)}")


if __name__ == "__main__":
    main()

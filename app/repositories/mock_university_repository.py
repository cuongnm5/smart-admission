from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List, Sequence

from app.domain.models import UniversityProfile
from app.repositories.base import UniversityRepository

# Maps common student major names to the broad categories used in the data.
# Keys are lowercase; values are lists of data-category substrings to match against.
_MAJOR_ALIASES: dict[str, list[str]] = {
    "information technology": ["computer science", "engineering technology", "science technology"],
    "software engineering": ["computer science", "engineering"],
    "computer engineering": ["computer science", "engineering"],
    "data science": ["computer science", "mathematics & statistics"],
    "artificial intelligence": ["computer science"],
    "machine learning": ["computer science"],
    "cybersecurity": ["computer science", "security & law enforcement"],
    "network engineering": ["computer science", "engineering technology"],
    "electrical engineering": ["engineering"],
    "mechanical engineering": ["engineering"],
    "civil engineering": ["engineering"],
    "biomedical engineering": ["engineering", "biological sciences"],
    "chemical engineering": ["engineering", "physical sciences"],
    "industrial engineering": ["engineering"],
    "business administration": ["business & marketing"],
    "marketing": ["business & marketing"],
    "finance": ["business & marketing"],
    "accounting": ["business & marketing"],
    "economics": ["business & marketing", "social sciences"],
    "medicine": ["health professions", "biological sciences"],
    "nursing": ["health professions"],
    "pharmacy": ["health professions"],
    "public health": ["health professions", "public administration"],
    "biology": ["biological sciences"],
    "biochemistry": ["biological sciences", "physical sciences"],
    "chemistry": ["physical sciences"],
    "physics": ["physical sciences"],
    "mathematics": ["mathematics & statistics"],
    "statistics": ["mathematics & statistics"],
    "law": ["legal studies", "security & law enforcement"],
    "psychology": ["psychology"],
    "sociology": ["social sciences"],
    "political science": ["social sciences", "public administration"],
    "international relations": ["social sciences", "public administration"],
    "communication": ["communication"],
    "journalism": ["communication"],
    "architecture": ["architecture"],
    "design": ["visual & performing arts", "architecture"],
    "education": ["education"],
    "environmental science": ["natural resources", "biological sciences"],
    "agriculture": ["agriculture"],
}


def _candidate_categories(intended_major: str) -> list[str]:
    """Return the list of data categories to search for the given major."""
    key = intended_major.strip().lower()
    # 1. Direct alias lookup
    if key in _MAJOR_ALIASES:
        return _MAJOR_ALIASES[key]
    # 2. Partial alias lookup (student major contains an alias key or vice-versa)
    for alias_key, categories in _MAJOR_ALIASES.items():
        if alias_key in key or key in alias_key:
            return categories
    # 3. Word-token overlap fallback against alias keys
    key_tokens = set(key.split())
    best: list[str] = []
    best_overlap = 0
    for alias_key, categories in _MAJOR_ALIASES.items():
        overlap = len(key_tokens & set(alias_key.split()))
        if overlap > best_overlap:
            best_overlap = overlap
            best = categories
    if best:
        return best
    # 4. Use the major itself as-is (original behaviour)
    return [key]


class MockUniversityRepository(UniversityRepository):
    def __init__(self, data_file: Path | None = None) -> None:
        if data_file is not None:
            self._data_file = data_file
        else:
            data_dir = Path(__file__).resolve().parents[1] / "data"
            csv_file = data_dir / "universities_master.csv"
            preferred = data_dir / "clean_universities.jsonl"
            legacy = data_dir / "universities.json"
            # Prefer CSV (has proper university names), fall back to JSONL/JSON
            self._data_file = csv_file if csv_file.exists() else (preferred if preferred.exists() else legacy)
        self._universities = self._load_data()

    def _load_data(self) -> List[UniversityProfile]:
        if self._data_file.suffix == ".csv":
            return self._load_csv()

        if self._data_file.suffix == ".jsonl":
            raw: List[dict] = []
            with self._data_file.open("r", encoding="utf-8") as file:
                for index, line in enumerate(file, start=1):
                    payload = line.strip()
                    if not payload:
                        continue
                    item = json.loads(payload)
                    item.setdefault("_row_index", index)
                    raw.append(item)

            cs_rows = [
                item for item in raw
                if "computer science" in str(item.get("programs_offered", "")).lower()
            ]
            cs_rows_sorted = sorted(cs_rows, key=lambda x: float(x.get("tution_out_of_state") or 0.0))

            if cs_rows_sorted:
                cheapest = cs_rows_sorted[0]
                most_expensive = cs_rows_sorted[-1]
                median = cs_rows_sorted[len(cs_rows_sorted) // 2]
                cheapest["university_id"] = "uta"
                median["university_id"] = "asu"
                most_expensive["university_id"] = "uiuc"

            for item in raw:
                index = int(item.pop("_row_index", 0) or 0)
                item.setdefault("university_id", f"jsonl-{index:04d}")
                item.setdefault("name", f"University {index}")
            return [UniversityProfile.model_validate(item) for item in raw]

        with self._data_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        return [UniversityProfile.model_validate(item) for item in raw]

    def _load_csv(self) -> List[UniversityProfile]:
        universities: List[UniversityProfile] = []
        with self._data_file.open("r", encoding="utf-8") as file:
            for index, row in enumerate(csv.DictReader(file), start=1):
                # Skip rows without the minimum required numeric fields
                try:
                    admission_rate = float(row.get("admission_rate") or 0)
                    sat_avg = float(row.get("sat_avg") or 0)
                    tuition_out = float(row.get("tuition_out_of_state") or 0)
                    tuition_in = float(row.get("tuition_in_state") or 0)
                except (ValueError, TypeError):
                    continue
                if not (0 < admission_rate <= 1 and sat_avg > 0 and tuition_out > 0):
                    continue

                name = row.get("name", "").strip()
                if not name:
                    continue

                university_id = (
                    name.lower()
                    .replace(" ", "_")
                    .replace("&", "and")
                    .replace(",", "")
                    .replace("'", "")
                    .replace("/", "_")
                    .replace("-", "_")
                    [:60]
                )

                item = {
                    "university_id": university_id,
                    "name": name,
                    "admissio_rate": admission_rate,
                    "sat_avg": sat_avg,
                    "tution_in_state": tuition_in,
                    "tution_out_of_state": tuition_out,
                    "programs_offered": row.get("programs_offered", ""),
                    "top_programs": row.get("top_programs", ""),
                    "city": row.get("city", "").strip(),
                    "state": row.get("state", "").strip(),
                }
                # Load subject-specific rankings from oedb_rank_* columns
                for col in (
                    "oedb_rank_accounting", "oedb_rank_business_administration",
                    "oedb_rank_computer_science", "oedb_rank_criminal_justice",
                    "oedb_rank_education", "oedb_rank_engineering",
                    "oedb_rank_graphic_design", "oedb_rank_it", "oedb_rank_marketing",
                    "oedb_rank_mba", "oedb_rank_nursing", "oedb_rank_paralegal",
                    "oedb_rank_phd", "oedb_rank_psychology",
                ):
                    val = row.get(col, "").strip()
                    if val:
                        try:
                            item[col] = int(float(val))
                        except (ValueError, TypeError):
                            pass
                try:
                    universities.append(UniversityProfile.model_validate(item))
                except Exception:
                    continue
        return universities

    def list_universities(self) -> Sequence[UniversityProfile]:
        return self._universities

    def find_by_major_and_international(self, intended_major: str) -> Sequence[UniversityProfile]:
        categories = _candidate_categories(intended_major)
        return [
            university
            for university in self._universities
            if university.accepts_international_students
            and any(
                cat in program or program in cat
                for program in (m.strip().lower() for m in university.majors)
                for cat in categories
            )
        ]

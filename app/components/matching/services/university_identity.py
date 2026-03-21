from __future__ import annotations

import hashlib

from app.domain.models import UniversityProfile


def build_university_id(university: UniversityProfile) -> str:
    payload = "|".join(
        [
            f"{university.admissio_rate:.6f}",
            f"{university.sat_avg:.2f}",
            f"{university.tution_in_state:.2f}",
            f"{university.tution_out_of_state:.2f}",
            university.programs_offered,
            university.top_programs,
        ]
    )
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"uni-{digest}"

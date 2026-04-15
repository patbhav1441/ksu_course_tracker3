"""Normalize professor rating data into the app's expected schema.

Recommended flow:
1. Run an external collector or use a legally obtained dataset export.
2. Save the raw file locally.
3. Use this script to transform the file into professors.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAW_FILE = Path(__file__).resolve().parents[1] / "data" / "raw_professors.json"
OUTFILE = Path(__file__).resolve().parents[1] / "data" / "demo_data" / "professors_normalized.json"


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    professor_id = str(record.get("id") or record.get("tid") or record.get("professor_id") or "unknown")
    return {
        "professor_id": professor_id,
        "name": record.get("name") or " ".join(filter(None, [record.get("tFname"), record.get("tLname")])).strip() or "Unknown",
        "department": record.get("department") or record.get("tDept") or "Unknown",
        "overall_rating": record.get("overall_rating") or record.get("rating") or "N/A",
        "difficulty": record.get("difficulty") or record.get("avgDifficulty") or "N/A",
        "num_ratings": record.get("num_ratings") or record.get("tNumRatings") or 0,
        "reviews": record.get("reviews") or record.get("comments") or [],
    }


def main() -> None:
    raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    normalized = {}
    for record in raw:
        item = normalize_record(record)
        normalized[item["professor_id"]] = item
    OUTFILE.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    print(f"Wrote {len(normalized)} normalized professor profiles to {OUTFILE}")


if __name__ == "__main__":
    main()

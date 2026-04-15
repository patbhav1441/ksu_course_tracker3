from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DEMO_DIR = DATA_DIR / "demo_data"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_program_shape(programs: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for name, payload in programs.items():
        requirements = []
        for req in payload.get("requirements", []):
            requirements.append(
                {
                    "course_code": str(req.get("course_code", "")).strip(),
                    "title": str(req.get("title", "")).strip() or "Unknown",
                    "credits": int(req.get("credits") or 0),
                    "recommended_term": str(req.get("recommended_term", "Not mapped")).strip(),
                }
            )
        normalized[name] = {
            "name": payload.get("name", name),
            "college": payload.get("college", "Kennesaw State University"),
            "description": payload.get("description", ""),
            "requirements": [req for req in requirements if req["course_code"]],
            "source_url": payload.get("source_url"),
        }
    return normalized


def _ensure_course_shape(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for course in courses:
        normalized.append(
            {
                "course_code": str(course.get("course_code", "")).strip(),
                "title": str(course.get("title", "Unknown")).strip(),
                "credits": int(course.get("credits") or 0),
                "prerequisites": [str(x).strip() for x in course.get("prerequisites", []) if str(x).strip()],
                "corequisites": [str(x).strip() for x in course.get("corequisites", []) if str(x).strip()],
            }
        )
    return [course for course in normalized if course["course_code"]]


def _ensure_section_shape(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for section in sections:
        normalized.append(
            {
                "term": str(section.get("term", "")).strip(),
                "course_code": str(section.get("course_code", "")).strip(),
                "section": str(section.get("section", "")).strip(),
                "title": str(section.get("title", "Unknown")).strip(),
                "professor_id": str(section.get("professor_id", "")).strip() or None,
                "professor_name": str(section.get("professor_name", "TBA")).strip(),
                "campus": str(section.get("campus", "TBA")).strip(),
                "modality": str(section.get("modality", "TBA")).strip(),
                "days": str(section.get("days", "TBA")).strip(),
                "time": str(section.get("time", "TBA")).strip(),
                "seats_available": int(section.get("seats_available") or 0),
                "crn": str(section.get("crn", "N/A")).strip(),
            }
        )
    return [section for section in normalized if section["course_code"] and section["term"]]


def _ensure_professor_shape(professors: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, payload in professors.items():
        pid = str(payload.get("professor_id") or key).strip()
        normalized[pid] = {
            "professor_id": pid,
            "name": str(payload.get("name", "Unknown")).strip(),
            "department": str(payload.get("department", "Unknown")).strip(),
            "overall_rating": float(payload.get("overall_rating") or 0),
            "difficulty": float(payload.get("difficulty") or 0),
            "num_ratings": int(payload.get("num_ratings") or 0),
            "reviews": [str(x).strip() for x in payload.get("reviews", []) if str(x).strip()],
        }
    return normalized


@lru_cache(maxsize=1)
def load_repository() -> dict[str, Any]:
    programs = _ensure_program_shape(_read_json(DEMO_DIR / "programs.json"))
    courses = _ensure_course_shape(_read_json(DEMO_DIR / "courses.json"))
    sections = _ensure_section_shape(_read_json(DEMO_DIR / "sections.json"))
    professors = _ensure_professor_shape(_read_json(DEMO_DIR / "professors.json"))
    return {
        "programs": programs,
        "courses": courses,
        "sections": sections,
        "professors": professors,
    }

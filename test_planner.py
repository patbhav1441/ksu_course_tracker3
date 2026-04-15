from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_TERM_SEQUENCE = [
    "Spring 2026",
    "Summer 2026",
    "Fall 2026",
    "Spring 2027",
    "Summer 2027",
    "Fall 2027",
]

SUMMER_MAX_CREDITS = 6
REGULAR_MAX_CREDITS = 15


@dataclass(slots=True)
class RecommendedSection:
    course_code: str
    section: dict[str, Any]
    professor: dict[str, Any] | None
    score: float
    reasons: list[str]


@dataclass(slots=True)
class RecommendationContext:
    score: float
    reasons: list[str]
    best_section: RecommendedSection | None


PREFERENCE_PRESETS = {
    "Balanced": {"rating": 0.45, "difficulty": 0.15, "confidence": 0.15, "availability": 0.15, "modality": 0.10},
    "Best professors": {"rating": 0.60, "difficulty": 0.10, "confidence": 0.20, "availability": 0.05, "modality": 0.05},
    "Easier semester": {"rating": 0.35, "difficulty": 0.30, "confidence": 0.10, "availability": 0.15, "modality": 0.10},
    "Open seats first": {"rating": 0.25, "difficulty": 0.10, "confidence": 0.10, "availability": 0.45, "modality": 0.10},
}


def build_course_lookup(courses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {course["course_code"]: course for course in courses}



def _normalize_set(values: list[str] | None) -> set[str]:
    return {value.strip() for value in values or [] if value and value.strip()}



def compute_remaining_requirements(program: dict[str, Any], completed_courses: list[str]) -> list[str]:
    completed = _normalize_set(completed_courses)
    required = [req["course_code"] for req in program.get("requirements", []) if req.get("course_code")]
    return [course_code for course_code in required if course_code not in completed]



def prereqs_satisfied(course: dict[str, Any], completed_courses: set[str]) -> bool:
    return _normalize_set(course.get("prerequisites")).issubset(completed_courses)



def coreqs_satisfied_or_planned(course: dict[str, Any], completed_courses: set[str], planned_courses: set[str]) -> bool:
    return _normalize_set(course.get("corequisites")).issubset(completed_courses | planned_courses)



def course_unlock_count(course_code: str, remaining_requirements: list[str], course_lookup: dict[str, dict[str, Any]]) -> int:
    unlocks = 0
    for other_code in remaining_requirements:
        if other_code == course_code:
            continue
        other = course_lookup.get(other_code, {})
        prereqs = _normalize_set(other.get("prerequisites"))
        if course_code in prereqs:
            unlocks += 1
    return unlocks



def infer_term_offerings(sections: list[dict[str, Any]]) -> dict[str, set[str]]:
    offerings: dict[str, set[str]] = {}
    for section in sections:
        offerings.setdefault(section["course_code"], set()).add(section["term"])
    return offerings



def professor_signal_summary(profile: dict[str, Any]) -> dict[str, str | list[str]]:
    reviews = [str(review).strip() for review in profile.get("reviews", []) if str(review).strip()][:15]
    joined = " ".join(reviews).lower()

    def seen(*keywords: str) -> bool:
        return any(keyword in joined for keyword in keywords)

    attendance = "Limited review signal"
    if seen("attendance", "mandatory", "participation", "required in class"):
        attendance = "Usually required or checked" if not seen("optional", "not mandatory") else "Often optional"

    homework = "Limited review signal"
    if seen("homework", "assignment", "assignments", "labs", "project", "projects"):
        homework = "Moderate to heavy workload" if seen("a lot", "heavy", "tons", "every week", "frequent") else "Regular coursework mentioned"

    grading = "Limited review signal"
    if seen("strict", "hard grader", "fair", "rubric", "curve", "partial credit"):
        if seen("strict", "hard grader"):
            grading = "Strict grading shows up often"
        elif seen("fair", "partial credit", "rubric", "transparent"):
            grading = "Fair and structured grading"
        else:
            grading = "Grading style appears in reviews"

    exam_style = "Limited review signal"
    if seen("exam", "quiz", "quizzes", "test", "tests"):
        exam_style = "Exams are a recurring theme"
        if seen("study guide", "straightforward", "predictable", "project based", "coding"):
            exam_style = "Assessments have recognizable patterns"

    return {
        "attendance": attendance,
        "homework": homework,
        "grading": grading,
        "exam_style": exam_style,
        "highlights": reviews[:5],
    }



def professor_score(profile: dict[str, Any], preference_profile: str = "Balanced") -> float:
    weights = PREFERENCE_PRESETS.get(preference_profile, PREFERENCE_PRESETS["Balanced"])
    overall = float(profile.get("overall_rating") or 0)
    difficulty = float(profile.get("difficulty") or 0)
    count = int(profile.get("num_ratings") or 0)
    rating_component = (overall / 5.0) * weights["rating"] * 100
    ease_component = (max(0.0, 5.0 - difficulty) / 5.0) * weights["difficulty"] * 100
    confidence_component = (min(count, 50) / 50.0) * weights["confidence"] * 100
    return round(rating_component + ease_component + confidence_component, 3)



def rank_sections_for_course(
    course_code: str,
    term: str,
    sections: list[dict[str, Any]],
    professors: dict[str, dict[str, Any]],
    only_open: bool = False,
    preference_profile: str = "Balanced",
) -> list[RecommendedSection]:
    weights = PREFERENCE_PRESETS.get(preference_profile, PREFERENCE_PRESETS["Balanced"])
    ranked: list[RecommendedSection] = []
    for section in sections:
        if section.get("term") != term or section.get("course_code") != course_code:
            continue
        seats = int(section.get("seats_available") or 0)
        if only_open and seats <= 0:
            continue

        reasons: list[str] = []
        score = 0.0
        professor = professors.get(section.get("professor_id") or "")

        if professor:
            score += professor_score(professor, preference_profile=preference_profile)
            reasons.append(f"Professor rating {professor.get('overall_rating', 0):.1f}")
            reasons.append(f"Difficulty {professor.get('difficulty', 0):.1f}")
            reasons.append(f"{professor.get('num_ratings', 0)} ratings")
        else:
            reasons.append("Professor data unavailable")

        availability_component = (min(max(seats, 0), 30) / 30.0) * weights["availability"] * 100
        score += availability_component
        reasons.append(f"{seats} seats open" if seats > 0 else "Currently full")

        modality = str(section.get("modality") or "")
        if "online" in modality.lower():
            score += weights["modality"] * 100
            reasons.append("Online flexibility bonus")

        if seats <= 0:
            score -= 10

        ranked.append(RecommendedSection(course_code=course_code, section=section, professor=professor, score=round(score, 3), reasons=reasons))

    ranked.sort(key=lambda item: (item.score, int(item.section.get("seats_available") or 0)), reverse=True)
    return ranked



def _course_recommendation_context(
    course_code: str,
    remaining_requirements: list[str],
    course_lookup: dict[str, dict[str, Any]],
    preferred_term: str | None,
    sections: list[dict[str, Any]] | None,
    professors: dict[str, dict[str, Any]] | None,
    only_open_sections: bool,
    preference_profile: str,
) -> RecommendationContext:
    reasons: list[str] = []
    score = 0.0
    course = course_lookup.get(course_code, {})
    credits = int(course.get("credits") or 0)
    unlocks = course_unlock_count(course_code, remaining_requirements, course_lookup)
    score += unlocks * 12
    reasons.append(f"Unlocks {unlocks} later requirement(s)")

    if credits >= 4:
        score += 3
        reasons.append("High credit milestone course")

    best_section: RecommendedSection | None = None
    if preferred_term and sections is not None and professors is not None:
        ranked = rank_sections_for_course(
            course_code,
            preferred_term,
            sections,
            professors,
            only_open=only_open_sections,
            preference_profile=preference_profile,
        )
        if ranked:
            best_section = ranked[0]
            score += best_section.score * 0.45
            reasons.extend(best_section.reasons[:3])
        elif only_open_sections:
            score -= 100
            reasons.append("No open sections this term")

    return RecommendationContext(score=round(score, 3), reasons=reasons, best_section=best_section)



def recommend_next_term(
    remaining_requirements: list[str],
    course_lookup: dict[str, dict[str, Any]],
    completed_courses: list[str],
    target_credits: int = 12,
    preferred_term: str | None = None,
    sections: list[dict[str, Any]] | None = None,
    professors: dict[str, dict[str, Any]] | None = None,
    only_open_sections: bool = False,
    preference_profile: str = "Balanced",
) -> list[str]:
    completed = _normalize_set(completed_courses)
    planned: list[str] = []
    planned_set: set[str] = set()
    total_credits = 0
    remaining_pending = list(remaining_requirements)

    for _ in range(len(remaining_pending) + 2):
        eligible: list[str] = []
        for course_code in remaining_pending:
            course = course_lookup.get(course_code)
            if not course:
                continue
            if not prereqs_satisfied(course, completed):
                continue
            if not coreqs_satisfied_or_planned(course, completed, planned_set | {course_code}):
                continue
            if preferred_term and sections is not None:
                has_term_match = any(s.get("term") == preferred_term and s.get("course_code") == course_code for s in sections)
                if not has_term_match:
                    continue
            eligible.append(course_code)

        if not eligible:
            break

        scored = []
        for course_code in eligible:
            context = _course_recommendation_context(
                course_code=course_code,
                remaining_requirements=remaining_requirements,
                course_lookup=course_lookup,
                preferred_term=preferred_term,
                sections=sections,
                professors=professors,
                only_open_sections=only_open_sections,
                preference_profile=preference_profile,
            )
            scored.append((course_code, context.score))

        progress_made = False
        for course_code, _ in sorted(scored, key=lambda item: item[1], reverse=True):
            if course_code in planned_set:
                continue
            course = course_lookup.get(course_code, {})
            credits = int(course.get("credits") or 0)
            if total_credits + credits > target_credits:
                continue
            if not prereqs_satisfied(course, completed):
                continue
            if not coreqs_satisfied_or_planned(course, completed, planned_set | {course_code}):
                continue
            planned.append(course_code)
            planned_set.add(course_code)
            total_credits += credits
            remaining_pending.remove(course_code)
            progress_made = True
        if not progress_made:
            break

    return planned



def build_full_path(
    remaining_requirements: list[str],
    course_lookup: dict[str, dict[str, Any]],
    completed_courses: list[str],
    starting_term: str,
    term_sequence: list[str] | None = None,
) -> dict[str, list[str]]:
    sequence = term_sequence or DEFAULT_TERM_SEQUENCE
    if starting_term not in sequence:
        sequence = [starting_term] + [term for term in sequence if term != starting_term]
    else:
        sequence = sequence[sequence.index(starting_term):]

    completed = _normalize_set(completed_courses)
    remaining = [course for course in remaining_requirements if course not in completed]
    path: dict[str, list[str]] = {}

    for term in sequence:
        max_credits = SUMMER_MAX_CREDITS if "Summer" in term else REGULAR_MAX_CREDITS
        term_plan = recommend_next_term(
            remaining_requirements=remaining,
            course_lookup=course_lookup,
            completed_courses=sorted(completed),
            target_credits=max_credits,
            preferred_term=None,
        )
        if term_plan:
            path[term] = term_plan
            for course_code in term_plan:
                completed.add(course_code)
                if course_code in remaining:
                    remaining.remove(course_code)
        if not remaining:
            break

    return path



def recommend_sections_for_courses(
    selected_courses: list[str],
    selected_term: str,
    sections: list[dict[str, Any]],
    professors: dict[str, dict[str, Any]],
    only_open: bool = False,
    preference_profile: str = "Balanced",
) -> dict[str, list[RecommendedSection]]:
    return {
        course_code: rank_sections_for_course(
            course_code,
            selected_term,
            sections,
            professors,
            only_open=only_open,
            preference_profile=preference_profile,
        )
        for course_code in selected_courses
    }



def build_course_recommendation_rows(
    next_term_plan: list[str],
    course_lookup: dict[str, dict[str, Any]],
    selected_term: str,
    sections: list[dict[str, Any]],
    professors: dict[str, dict[str, Any]],
    only_open: bool = False,
    preference_profile: str = "Balanced",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ranked_sections = recommend_sections_for_courses(
        next_term_plan,
        selected_term,
        sections,
        professors,
        only_open=only_open,
        preference_profile=preference_profile,
    )
    for course_code in next_term_plan:
        course = course_lookup.get(course_code, {})
        ranked = ranked_sections.get(course_code, [])
        top = ranked[0] if ranked else None
        rows.append(
            {
                "course_code": course_code,
                "title": course.get("title", "Unknown"),
                "credits": int(course.get("credits") or 0),
                "best_professor": (top.professor or {}).get("name", "No professor data") if top else "No section data",
                "rating": round(float((top.professor or {}).get("overall_rating") or 0), 2) if top else "N/A",
                "difficulty": round(float((top.professor or {}).get("difficulty") or 0), 2) if top else "N/A",
                "section": top.section.get("section", "N/A") if top else "N/A",
                "crn": top.section.get("crn", "N/A") if top else "N/A",
                "modality": top.section.get("modality", "N/A") if top else "N/A",
                "time": f"{top.section.get('days', 'TBA')} {top.section.get('time', 'TBA')}" if top else "N/A",
                "seats_available": top.section.get("seats_available", "N/A") if top else "N/A",
                "fit_score": top.score if top else 0.0,
            }
        )
    return rows



def build_manual_schedule_rows(
    selected_courses: list[str],
    selected_term: str,
    course_lookup: dict[str, dict[str, Any]],
    sections: list[dict[str, Any]],
    professors: dict[str, dict[str, Any]],
    preference_profile: str = "Balanced",
    only_open: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ranked = recommend_sections_for_courses(
        selected_courses,
        selected_term,
        sections,
        professors,
        only_open=only_open,
        preference_profile=preference_profile,
    )
    for course_code in selected_courses:
        for rec in ranked.get(course_code, [])[:5]:
            rows.append(
                {
                    "course_code": course_code,
                    "title": course_lookup.get(course_code, {}).get("title", "Unknown"),
                    "section": rec.section.get("section", "N/A"),
                    "crn": rec.section.get("crn", "N/A"),
                    "professor": (rec.professor or {}).get("name", rec.section.get("professor_name", "TBA")),
                    "rating": (rec.professor or {}).get("overall_rating", "N/A"),
                    "difficulty": (rec.professor or {}).get("difficulty", "N/A"),
                    "campus": rec.section.get("campus", "TBA"),
                    "modality": rec.section.get("modality", "TBA"),
                    "days": rec.section.get("days", "TBA"),
                    "time": rec.section.get("time", "TBA"),
                    "seats_available": rec.section.get("seats_available", 0),
                    "fit_score": rec.score,
                    "why": " | ".join(rec.reasons[:4]),
                }
            )
    return rows

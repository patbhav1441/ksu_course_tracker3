from __future__ import annotations

from io import StringIO

import pandas as pd
import streamlit as st


def render_header(hero_title: str, hero_subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-overlay">
                <span class="hero-badge">Kennesaw State planning showcase</span>
                <h1>{hero_title}</h1>
                <p>{hero_subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_program_summary(program: dict, remaining: list[str], completed_courses: list[str], total_credits_remaining: int) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-kicker">Program snapshot</div>
            <h3>{program.get('name', 'Unknown program')}</h3>
            <p class="muted-copy">{program.get('description', 'No description available.')}</p>
            <div class="stat-grid">
                <div><span class="stat-label">College</span><span class="stat-value">{program.get('college', 'KSU')}</span></div>
                <div><span class="stat-label">Completed</span><span class="stat-value">{len(completed_courses)}</span></div>
                <div><span class="stat-label">Remaining courses</span><span class="stat-value">{len(remaining)}</span></div>
                <div><span class="stat-label">Remaining credits</span><span class="stat-value">{total_credits_remaining}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_course_card(requirement: dict, course: dict | None, taken: bool = False, term_offerings: list[str] | None = None) -> None:
    course = course or {}
    prereqs = ", ".join(course.get("prerequisites", [])) or "None"
    coreqs = ", ".join(course.get("corequisites", [])) or "None"
    terms = ", ".join(term_offerings or []) or "No section data"
    credits = course.get("credits") or requirement.get("credits") or "N/A"
    recommended_term = requirement.get("recommended_term", "Not mapped")
    classes = "course-card course-card-complete" if taken else "course-card"
    st.markdown(
        f"""
        <div class="{classes}">
            <div class="course-card-top">
                <div>
                    <div class="course-code">{requirement.get('course_code', 'Unknown')}</div>
                    <div class="course-title">{course.get('title') or requirement.get('title', 'Unknown')}</div>
                </div>
            </div>
            <div class="course-meta-grid">
                <span><strong>Credits</strong><br>{credits}</span>
                <span><strong>Suggested term</strong><br>{recommended_term}</span>
                <span><strong>Prereqs</strong><br>{prereqs}</span>
                <span><strong>Coreqs</strong><br>{coreqs}</span>
                <span><strong>Offered in data</strong><br>{terms}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_schedule_table(sections: list[dict], caption: str | None = None, csv_name: str | None = None) -> None:
    if caption:
        st.caption(caption)
    if not sections:
        st.info("No sections matched the current filters.")
        return
    df = pd.DataFrame(sections)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if csv_name:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button("Download CSV", csv_buffer.getvalue(), file_name=csv_name, mime="text/csv")



def render_professor_card(profile: dict, summary: dict, section: dict) -> None:
    review_html = "".join(f"<li>{review}</li>" for review in summary.get("highlights", []))
    st.markdown(
        f"""
        <div class="glass-card professor-card">
            <div class="professor-header">
                <div>
                    <h3>{profile.get('name', 'Unknown')}</h3>
                    <p>{profile.get('department', 'Unknown')}</p>
                </div>
                <div class="prof-chip-wrap">
                    <span class="prof-chip">Rating {profile.get('overall_rating', 'N/A')}</span>
                    <span class="prof-chip">Difficulty {profile.get('difficulty', 'N/A')}</span>
                    <span class="prof-chip">{profile.get('num_ratings', 0)} ratings</span>
                </div>
            </div>
            <div class="course-meta-grid">
                <span><strong>Course</strong><br>{section.get('course_code')} {section.get('section')}</span>
                <span><strong>CRN</strong><br>{section.get('crn', 'N/A')}</span>
                <span><strong>Time</strong><br>{section.get('days', 'TBA')} {section.get('time', 'TBA')}</span>
                <span><strong>Modality</strong><br>{section.get('modality', 'N/A')}</span>
            </div>
            <div class="signal-grid">
                <div><strong>Attendance</strong><br>{summary['attendance']}</div>
                <div><strong>Homework</strong><br>{summary['homework']}</div>
                <div><strong>Grading</strong><br>{summary['grading']}</div>
                <div><strong>Exam style</strong><br>{summary['exam_style']}</div>
            </div>
            <div>
                <strong>Representative reviews</strong>
                <ul>{review_html or '<li>No review text available</li>'}</ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_plan_table(rows: list[dict], title: str, csv_name: str | None = None) -> None:
    st.markdown(f"### {title}")
    if not rows:
        st.info("No courses planned for this term.")
        return
    render_schedule_table(rows, csv_name=csv_name)

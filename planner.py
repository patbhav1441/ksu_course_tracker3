# KSU PathPilot

KSU PathPilot is a Streamlit based KSU themed course planning showcase app.

## What it does

- lets students choose a KSU major or minor
- tracks completed courses
- shows remaining requirements
- checks prerequisites and corequisites before making recommendations
- recommends the next semester based on requirement order, section availability, and professor quality
- lets students manually pick courses for a term and rank sections by professor quality, difficulty, open seats, and modality
- shows CRN, section, meeting time, campus, and delivery format
- summarizes professor review signals such as attendance, homework, grading, and exam style

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app from that repo.
3. Set the entrypoint to `app.py`.
4. Deploy.

## Production notes

This repo is built as a frontend first showcase. The data refresh layer should remain separate.

Recommended production data flow:

1. fetch official KSU catalog rules
2. fetch KSU academic map sequencing
3. fetch KSU schedule sections by term
4. normalize professor intelligence from a separately maintained dataset
5. validate schemas
6. publish clean snapshots to the app

## Files

- `app.py` main Streamlit app
- `ksu_app/services/data_loader.py` data loading and normalization
- `ksu_app/services/planner.py` prerequisite aware planning and section ranking
- `ksu_app/components/renderers.py` UI rendering helpers
- `ksu_app/theme/styles.py` KSU themed styles
- `scripts/` offline ETL starter scripts

## Current truth

The application logic is stronger than a prototype, but the included data is still demo data rather than the full KSU catalog and live schedule.

"""Example ETL for KSU Schedule of Classes.

KSU class availability is term-sensitive and the HTML structure can change.
This script is written as a maintainable starting point, not a guaranteed parser
for every future term without selector updates.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUTFILE = Path(__file__).resolve().parents[1] / "data" / "demo_data" / "sections_live.json"
SEARCH_URL = "https://owlexpress.kennesaw.edu/prodban/bwckschd.p_disp_dyn_sched"


def fetch_term_page() -> str:
    response = requests.get(SEARCH_URL, timeout=30)
    response.raise_for_status()
    return response.text


def parse_term_options(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    terms = []
    for option in soup.select("select[name='p_term'] option"):
        value = option.get("value", "").strip()
        label = option.get_text(" ", strip=True)
        if value and label and value != "%":
            terms.append({"term_code": value, "term_label": label})
    return terms


def main() -> None:
    html = fetch_term_page()
    terms = parse_term_options(html)
    OUTFILE.write_text(json.dumps({"terms": terms}, indent=2), encoding="utf-8")
    print(f"Saved {len(terms)} term options to {OUTFILE}")


if __name__ == "__main__":
    main()

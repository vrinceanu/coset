"""
Scrapes TSU undergraduate program data from catalog.tsu.edu for COSET departments.
Outputs: catalog_programs.json

Two table layouts exist on program pages:
  Layout A (single requirements table): table[0] = all requirements, table[1] = degree plan
  Layout B (split tables): table[0] = summary, table[1..n-1] = sections, table[n] = degree plan
The degree plan table is always identified by its first row being "First Year".
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://catalog.tsu.edu"

DEPARTMENT_URLS = {
    "Biology": "/undergraduate/schools-colleges/science-engineering-technology/biology/",
    "Chemistry": "/undergraduate/schools-colleges/science-engineering-technology/chemistry/",
    "Computer Science": "/undergraduate/schools-colleges/science-engineering-technology/computer-science/",
    "Engineering": "/undergraduate/schools-colleges/science-engineering-technology/engineering/",
    "Environmental and Interdisciplinary Sciences": "/undergraduate/schools-colleges/science-engineering-technology/environmental-interdisciplinary-sciences/",
    "Industrial Technologies": "/undergraduate/schools-colleges/science-engineering-technology/industrial-technologies/",
    "Mathematics": "/undergraduate/schools-colleges/science-engineering-technology/mathematics/",
    "Physics": "/undergraduate/schools-colleges/science-engineering-technology/physics/",
    "Transportation Studies": "/undergraduate/schools-colleges/science-engineering-technology/transportation-studies/",
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (research scraper)"})


def get_soup(url: str) -> BeautifulSoup:
    full = url if url.startswith("http") else BASE_URL + url
    resp = SESSION.get(full, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def clean(el) -> str:
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).replace("\xa0", " ").split())


# ── Patterns ──────────────────────────────────────────────────────────────────

MAJOR_PAT = re.compile(r"major\s+req|major\s*\(|program\s+req|required\s+courses?", re.I)
OTHER_PAT = re.compile(r"other\s+req|supporting|cognate|general\s+ed|core\s+curr", re.I)
ELEC_PAT = re.compile(r"elective|free\s+elec", re.I)
SECTION_HOURS_RE = re.compile(r"\((\d+)\s*hours?\)", re.I)
CODE_RE = re.compile(r"^([A-Z]{2,6})\s+(\d+[A-Z]?)$")
YEAR_RE = re.compile(r"^(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+year$", re.I)
SEM_RE = re.compile(
    r"^((first|second|third|fourth|fifth|sixth|seventh|eighth)\s+semester|"
    r"fall\s*\d*|spring\s*\d*|summer\s*\d*)$",
    re.I,
)


def is_course_code(text: str) -> bool:
    return bool(CODE_RE.match(text.strip()))


# ── Name / degree helpers ─────────────────────────────────────────────────────

def extract_program_name(soup: BeautifulSoup) -> str:
    title_tag = soup.find("title")
    if title_tag:
        txt = clean(title_tag)
        for sep in [" < ", " | ", " - "]:
            if sep in txt:
                return txt.split(sep)[0].strip()
        return txt
    h1s = soup.find_all("h1")
    return clean(h1s[-1]) if h1s else ""


def extract_degree_conferred(name: str, url: str) -> str:
    n, u = name.lower(), url.lower()
    if "minor" in n or "minor" in u:
        return "Minor"
    if "certificate" in n:
        return "Certificate"
    if "bachelor of arts" in n or (re.search(r"-ba[-/]", u) and "ms" not in n):
        return "Bachelor of Arts"
    if "bachelor of technology" in n:
        return "Bachelor of Technology"
    if "accelerated" in n and "master" in n:
        return "Bachelor of Science / Master of Science (Accelerated)"
    return "Bachelor of Science"


def infer_focus(name: str, url: str) -> str:
    n, u = name.lower(), url.lower()
    if "minor" in u or ("minor" in n and not re.search(r"(with|without)\s+minor", n)):
        return "minor"
    if "certificate" in n:
        return "certificate"
    return "major"


# ── Description ───────────────────────────────────────────────────────────────

def extract_dept_description(dept_soup: BeautifulSoup) -> str:
    for p in dept_soup.find_all("p"):
        t = clean(p)
        if len(t) > 80 and not re.match(r"[A-Z]{2,6}\s+\d", t):
            return t
    return ""


# ── Credit hours ──────────────────────────────────────────────────────────────

def extract_credit_hours(soup: BeautifulSoup) -> str:
    body = soup.get_text(" ").replace("\xa0", " ")
    for pat in [
        r"total\s+hours?[\s:]+(\d+)",
        r"(\d+)\s+(?:semester\s+)?credit\s+hours?\s+(?:required|total|minimum)",
        r"minimum\s+of\s+(\d+)\s+(?:semester\s+)?(?:credit\s+)?hours?",
        r"(\d+)\s+total\s+(?:credit\s+)?hours?",
    ]:
        m = re.search(pat, body, re.I)
        if m:
            return m.group(1)
    return ""


# ── Table classification ──────────────────────────────────────────────────────

def table_has_courses(tbl) -> bool:
    for tr in tbl.find_all("tr"):
        cells = [clean(c) for c in tr.find_all(["td", "th"])]
        if len(cells) >= 2 and is_course_code(cells[0]):
            return True
    return False


def table_is_degree_plan(tbl) -> bool:
    rows = tbl.find_all("tr")
    if not rows:
        return False
    first_cells = [clean(c) for c in rows[0].find_all(["td", "th"])]
    return bool(first_cells and YEAR_RE.match(first_cells[0]))


def bucket_for_table(tbl) -> str | None:
    """Determine major/other/electives from the table's preceding sibling."""
    prev = tbl.find_previous_sibling(["h1", "h2", "h3", "h4", "p"])
    prev_text = clean(prev) if prev else ""
    if MAJOR_PAT.search(prev_text):
        return "major"
    if OTHER_PAT.search(prev_text) or "general education" in prev_text.lower():
        return "other"
    if ELEC_PAT.search(prev_text):
        return "electives"
    return None


# ── Requirements parsing ──────────────────────────────────────────────────────

def parse_course_rows(tbl, default_bucket: str, buckets: dict) -> None:
    """Read all course rows from a single table into buckets."""
    current = default_bucket
    for tr in tbl.find_all("tr"):
        cells = [clean(c) for c in tr.find_all(["td", "th"])]
        if not cells:
            continue
        first = cells[0]
        if not first or first.lower() in ("code", "title", "hours"):
            continue

        # Section-header row (no course code, 1-2 cells)
        if len(cells) <= 2 and not is_course_code(first):
            if MAJOR_PAT.search(first):
                current = "major"
            elif OTHER_PAT.search(first) or "general education" in first.lower():
                current = "other"
            elif ELEC_PAT.search(first):
                current = "electives"
            m = SECTION_HOURS_RE.search(first)
            if m:
                buckets[current]["total_hours"] = m.group(1)
            buckets[current]["notes"].append(first)
            continue

        # Course row
        if len(cells) >= 2 and is_course_code(first):
            hours = cells[2] if len(cells) > 2 else ""
            buckets[current]["courses"].append({
                "code": first,
                "name": cells[1],
                "credit_hours": hours if re.match(r"^\d+$", hours) else "",
            })


def parse_requirements(soup: BeautifulSoup) -> dict:
    buckets: dict = {
        "major": {"courses": [], "notes": [], "total_hours": ""},
        "other": {"courses": [], "notes": [], "total_hours": ""},
        "electives": {"courses": [], "notes": [], "total_hours": ""},
    }

    tables = soup.find_all("table")
    req_tables = [t for t in tables if not table_is_degree_plan(t)]
    course_tables = [t for t in req_tables if table_has_courses(t)]

    if len(course_tables) == 1:
        # Layout A: single table holds all requirements with section-header rows
        parse_course_rows(course_tables[0], "major", buckets)
    else:
        # Layout B: each table is a separate section; classify by preceding sibling
        for tbl in course_tables:
            bkt = bucket_for_table(tbl) or "major"
            parse_course_rows(tbl, bkt, buckets)

    for bk in buckets.values():
        bk["notes"] = " | ".join(bk["notes"])

    return buckets


# ── Degree plan parsing ───────────────────────────────────────────────────────

def parse_degree_plan(soup: BeautifulSoup) -> list:
    tables = soup.find_all("table")
    plan_table = next((t for t in tables if table_is_degree_plan(t)), None)
    if not plan_table:
        return []

    plan = []
    current_semester = None
    year_label = ""

    for tr in plan_table.find_all("tr"):
        cells = [clean(c) for c in tr.find_all(["td", "th"])]
        if not cells:
            continue
        first = cells[0]
        if not first:
            continue

        if len(cells) == 1 and YEAR_RE.match(first):
            year_label = first
            continue

        if SEM_RE.match(first) and not is_course_code(first):
            if current_semester:
                plan.append(current_semester)
            label = f"{year_label} — {first}" if year_label else first
            current_semester = {"semester": label, "courses": []}
            continue

        if len(cells) >= 2 and is_course_code(first):
            hours = cells[2] if len(cells) > 2 else ""
            entry = {
                "code": first,
                "name": cells[1],
                "credit_hours": hours if re.match(r"^\d", hours) else "",
            }
            if current_semester is None:
                current_semester = {"semester": year_label or "Unknown", "courses": []}
            current_semester["courses"].append(entry)

    if current_semester:
        plan.append(current_semester)

    return plan


# ── Department link discovery ─────────────────────────────────────────────────

def find_program_links(soup: BeautifulSoup, dept_path: str) -> list[tuple[str, str]]:
    seen: set[str] = set()
    links: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        label = clean(a)
        if not href.startswith(dept_path) or href == dept_path:
            continue
        if href.endswith(".pdf") or "#" in href:
            continue
        if any(x in href for x in ["/courses/", "/faculty/"]):
            continue
        if href not in seen:
            seen.add(href)
            links.append((label, href))
    return links


# ── Single program scraper ────────────────────────────────────────────────────

def scrape_program_page(url: str, department: str, dept_description: str) -> dict:
    soup = get_soup(url)
    name = extract_program_name(soup)
    reqs = parse_requirements(soup)
    degree_plan = parse_degree_plan(soup)
    return {
        "name": name,
        "degree_conferred": extract_degree_conferred(name, url),
        "department": department,
        "focus": infer_focus(name, url),
        "level": "undergraduate",
        "description": dept_description,
        "major_requirements": {
            "courses": reqs["major"]["courses"],
            "notes": reqs["major"]["notes"],
            "total_hours": reqs["major"]["total_hours"],
        },
        "other_requirements": {
            "courses": reqs["other"]["courses"],
            "notes": reqs["other"]["notes"],
            "total_hours": reqs["other"]["total_hours"],
        },
        "electives": {
            "courses": reqs["electives"]["courses"],
            "notes": reqs["electives"]["notes"],
            "total_hours": reqs["electives"]["total_hours"],
        },
        "credit_hours": extract_credit_hours(soup),
        "degree_plan": degree_plan,
        "source_url": (url if url.startswith("http") else BASE_URL + url),
    }


# ── Department scraper ────────────────────────────────────────────────────────

def scrape_department(dept_name: str, dept_path: str) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"Department: {dept_name}")
    dept_soup = get_soup(dept_path)
    dept_description = extract_dept_description(dept_soup)

    links = find_program_links(dept_soup, dept_path)
    print(f"  {len(links)} program(s) found")

    programs = []
    for label, href in links:
        print(f"  Scraping: {href.split('/')[-2]}")
        try:
            prog = scrape_program_page(href, dept_name, dept_description)
            major_n = len(prog["major_requirements"]["courses"])
            other_n = len(prog["other_requirements"]["courses"])
            plan_n = len(prog["degree_plan"])
            print(f"    OK [{prog['focus']}] {prog['credit_hours']} cr | "
                  f"major={major_n} other={other_n} plan={plan_n} sem")
            programs.append(prog)
        except Exception as exc:
            print(f"    ERROR: {exc}")
        time.sleep(0.5)

    return programs


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    all_programs = []
    for dept_name, dept_path in DEPARTMENT_URLS.items():
        try:
            progs = scrape_department(dept_name, dept_path)
            all_programs.extend(progs)
        except Exception as exc:
            print(f"ERROR scraping {dept_name}: {exc}")
        time.sleep(1)

    output_path = "catalog_programs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_programs, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Done. {len(all_programs)} programs saved to {output_path}")
    by_dept: dict[str, list] = {}
    for p in all_programs:
        by_dept.setdefault(p["department"], []).append(
            f"{p['name'][:45]} [{p['focus']}]"
        )
    for dept, entries in by_dept.items():
        print(f"\n  {dept} ({len(entries)}):")
        for e in entries:
            print(f"    {e}")


if __name__ == "__main__":
    main()

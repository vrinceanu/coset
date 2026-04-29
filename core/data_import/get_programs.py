import json, re, time, requests
from bs4 import BeautifulSoup

BASE_URL = "https://catalog.tsu.edu"

DEPARTMENT_URLS = {
    "BIOL": "/undergraduate/schools-colleges/science-engineering-technology/biology/",
    "CHEM": "/undergraduate/schools-colleges/science-engineering-technology/chemistry/",
    "COMP": "/undergraduate/schools-colleges/science-engineering-technology/computer-science/",
    "ENG": "/undergraduate/schools-colleges/science-engineering-technology/engineering/",
    "EIS": "/undergraduate/schools-colleges/science-engineering-technology/environmental-interdisciplinary-sciences/",
    "ITEC": "/undergraduate/schools-colleges/science-engineering-technology/industrial-technologies/",
    "MATH": "/undergraduate/schools-colleges/science-engineering-technology/mathematics/",
    "PHYS": "/undergraduate/schools-colleges/science-engineering-technology/physics/",
    "TS": "/undergraduate/schools-colleges/science-engineering-technology/transportation-studies/",
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

def scrape_department(dept_name: str, dept_path: str) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"Department: {dept_name}")
    dept_soup = get_soup(dept_path)
    for t in dept_soup.find_all("p"):
        tt = clean(t)
        if len(tt) > 80:
            description = tt
            break                
 #   print(description)

    container = dept_soup.find('div', id="programstextcontainer")
    programs = []
    if container:
        progs = container.find_all('a', href=True)
        for p in progs:
            name = p.get_text()
            url = p.get('href')
            prog_soup = get_soup(BASE_URL+url)
            th = prog_soup.find('td', string="Total Hours")
            ts = th.find_next_sibling()
            crh = ts.text
            if name[-19:] == "Bachelor of Science":
                degree = "BS"
            elif name[-5:] == "Minor":
                degree = "MINOR"
            elif name[:11] == "Accelerated":
                degree = "4+1"
            elif name[-11:] == "Certificate":
                degree = "CERT"
            else:
                degree = "OTHER"
            
            programs.append({
                'name':name, 
                'url':url,
                'department': dept_name,
                'credit_hours': crh,
                'degree_conferred': degree
                })

    return programs

def main():
    all_programs = []
    for dept_name, dept_path in DEPARTMENT_URLS.items():
        try:
            progs = scrape_department(dept_name, dept_path)
            all_programs.extend(progs)
        except Exception as exc:
            print(f"ERROR scraping {dept_name}: {exc}")
        time.sleep(1)
    output_path = "programs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_programs, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()


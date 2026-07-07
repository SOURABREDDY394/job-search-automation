"""
SimplyHired Scraper
====================
SimplyHired is a large job aggregator (like Indeed).
It has remote + intern/junior filters in the URL.
No API — we scrape the search results page.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Search URLs targeting remote intern/junior tech roles
SEARCH_QUERIES = [
    ("AI intern remote", "ai-intern-remote"),
    ("junior software engineer remote", "junior-software-engineer-remote"),
    ("junior full stack developer remote", "junior-full-stack-developer-remote"),
    ("python intern remote", "python-intern-remote"),
    ("junior backend developer remote", "junior-backend-developer-remote"),
    ("junior react developer remote", "junior-react-developer-remote"),
    ("machine learning intern remote", "machine-learning-intern-remote"),
    ("junior web developer remote", "junior-web-developer-remote"),
    ("entry level software engineer remote", "entry-level-software-engineer-remote"),
    ("junior AI engineer remote", "junior-ai-engineer-remote"),
]


def search_simplyhired(keywords, min_hourly=10):
    """
    Search SimplyHired for remote intern/junior tech jobs.
    Returns list of job dicts.
    """
    jobs = []
    seen_titles = set()

    print("  [SimplyHired] Searching remote intern/junior jobs...")

    for query_text, query_slug in SEARCH_QUERIES:
        try:
            # SimplyHired URL format
            url = f"https://www.simplyhired.com/search?q={requests.utils.quote(query_text)}&l=remote&t=internship"

            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                # Try alternate URL format
                url = f"https://www.simplyhired.com/search?q={requests.utils.quote(query_text)}&fdb=7&fjt=internship"
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    continue

            soup = BeautifulSoup(response.text, "html.parser")

            # SimplyHired job cards
            job_cards = soup.find_all("article", class_="SerpJob")
            if not job_cards:
                job_cards = soup.find_all("div", {"data-testid": "searchSerpJob"})
            if not job_cards:
                job_cards = soup.find_all("li", class_="css-0")
            if not job_cards:
                # Try finding any job-like links
                job_cards = soup.find_all("article")

            for card in job_cards:
                try:
                    # Title
                    title_tag = card.find("a", {"data-testid": "searchSerpJobTitle"})
                    if not title_tag:
                        title_tag = card.find("a", class_="SerpJob-titleCard")
                    if not title_tag:
                        title_tag = card.find("h2")
                        if title_tag:
                            title_tag = title_tag.find("a")
                    if not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)

                    # Skip if already seen or senior
                    title_lower = title.lower()
                    if title_lower in seen_titles:
                        continue
                    seen_titles.add(title_lower)

                    if any(t in title_lower for t in ["senior", "sr.", "lead", "principal", "staff", "director"]):
                        continue

                    # Company
                    company_tag = card.find("span", {"data-testid": "companyName"})
                    if not company_tag:
                        company_tag = card.find("span", class_="SerpJob-companyName")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"

                    # Location
                    location_tag = card.find("span", {"data-testid": "searchSerpJobLocation"})
                    if not location_tag:
                        location_tag = card.find("span", class_="SerpJob-location")
                    location = location_tag.get_text(strip=True) if location_tag else "Remote"

                    # Salary
                    salary_tag = card.find("span", {"data-testid": "searchSerpJobSalary"})
                    if not salary_tag:
                        salary_tag = card.find("span", class_="SerpJob-metaInfoSalary")
                    salary_text = salary_tag.get_text(strip=True) if salary_tag else "Not specified"

                    # Link
                    href = title_tag.get("href", "")
                    link = f"https://www.simplyhired.com{href}" if href.startswith("/") else href

                    # Parse salary
                    salary_monthly = parse_simplyhired_salary(salary_text)

                    # Tags
                    found_techs = []
                    tech_terms = [
                        "python", "react", "javascript", "ai", "machine learning",
                        "full stack", "backend", "frontend", "software", "developer",
                        "engineer", "web", "aws", "docker", "api", "data",
                    ]
                    for t in tech_terms:
                        if t in title_lower:
                            found_techs.append(t)

                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": salary_text,
                        "salary_monthly_usd": salary_monthly,
                        "type": "Internship/Junior",
                        "location": location,
                        "source": "SimplyHired",
                        "link": link,
                        "tags": ", ".join(found_techs) if found_techs else query_text,
                        "date_posted": "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            time.sleep(2)  # Rate limiting

        except requests.RequestException:
            continue

    print(f"  [SimplyHired] Found {len(jobs)} intern/junior tech jobs")
    return jobs


def parse_simplyhired_salary(salary_text):
    """Parse SimplyHired salary into monthly USD."""
    if not salary_text or salary_text == "Not specified":
        return 0

    cleaned = salary_text.replace(",", "").replace("$", "").lower()

    # Find numbers
    numbers = re.findall(r"([\d.]+)", cleaned)
    if not numbers:
        return 0

    amount = float(numbers[0])

    # Determine period
    if "hour" in cleaned or "/hr" in cleaned:
        return int(amount * 160)
    elif "year" in cleaned or "annual" in cleaned or amount > 30000:
        return int(amount // 12)
    elif "month" in cleaned or (1000 <= amount <= 30000):
        return int(amount)
    elif "week" in cleaned:
        return int(amount * 4)
    elif amount > 50000:
        return int(amount // 12)

    return int(amount)

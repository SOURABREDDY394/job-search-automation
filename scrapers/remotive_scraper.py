"""
Remotive Scraper
================
Remotive is a curated remote job board focused on tech.
They have a public API. Companies here are remote-first
and often hire globally (including from India).
"""

import requests
from datetime import datetime
import re


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}

# Remotive job categories relevant to our search
CATEGORIES = [
    "software-dev",
    "data",
    "machine-learning",
]


def search_remotive(keywords, min_hourly=10):
    """
    Search Remotive for remote tech internships/junior roles.
    Uses their public API.
    """
    jobs = []
    seen_ids = set()

    for category in CATEGORIES:
        try:
            url = f"https://remotive.com/api/remote-jobs?category={category}&limit=100"
            response = requests.get(url, headers=HEADERS, timeout=15)

            if response.status_code != 200:
                print(f"  [Remotive] HTTP {response.status_code} for category '{category}'")
                continue

            data = response.json()
            job_listings = data.get("jobs", [])

            for job in job_listings:
                try:
                    job_id = job.get("id", "")
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = job.get("title", "")
                    company = job.get("company_name", "N/A")
                    description = job.get("description", "").lower()
                    candidate_location = job.get("candidate_required_location", "Worldwide")
                    job_type = job.get("job_type", "")
                    url_link = job.get("url", "")
                    pub_date = job.get("publication_date", "")
                    salary_text = job.get("salary", "Not specified") or "Not specified"
                    tags = job.get("tags", [])

                    title_lower = title.lower()
                    all_text = f"{title_lower} {description} {' '.join(tags).lower()}"

                    # Check for intern/junior/entry level roles
                    is_entry_level = any(term in all_text for term in [
                        "intern", "internship", "junior", "entry level",
                        "entry-level", "jr.", "jr ", "graduate",
                        "associate", "trainee", "early career",
                    ])

                    # Check tech keyword match
                    matches_tech = any(
                        kw.lower().replace(" intern", "").replace(" internship", "") in all_text
                        for kw in keywords
                    )

                    if not (is_entry_level and matches_tech):
                        # Also include if title directly matches
                        if not any(kw.lower() in title_lower for kw in keywords):
                            continue

                    # Parse salary
                    salary_monthly_usd = parse_salary(salary_text)

                    # Check if location allows India/worldwide
                    location_ok = is_location_ok(candidate_location)
                    if not location_ok:
                        continue

                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": salary_text,
                        "salary_monthly_usd": salary_monthly_usd,
                        "type": detect_pay_type(salary_text, job_type),
                        "location": candidate_location,
                        "source": "Remotive",
                        "link": url_link,
                        "tags": ", ".join(tags) if tags else category,
                        "date_posted": pub_date[:10] if pub_date else "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            print(f"  [Remotive] Category '{category}': {len(job_listings)} total, scanning...")

        except requests.RequestException as e:
            print(f"  [Remotive] Network error for '{category}': {e}")

    print(f"  [Remotive] Total matched: {len(jobs)}")
    return jobs


def is_location_ok(location):
    """Check if the job allows hiring from India/worldwide."""
    if not location:
        return True
    loc_lower = location.lower()
    # Accept if worldwide, anywhere, or specifically includes Asia/India
    ok_terms = [
        "worldwide", "anywhere", "global", "india",
        "asia", "remote", "earth", "international",
    ]
    # Reject if restricted to specific western countries only
    reject_exclusive = ["us only", "usa only", "uk only", "eu only", "europe only"]

    if any(term in loc_lower for term in reject_exclusive):
        return False
    if any(term in loc_lower for term in ok_terms):
        return True
    # If it just lists countries, check if it's too restrictive
    # Be lenient - include unless explicitly restricted
    return True


def parse_salary(salary_text):
    """Parse salary text into monthly USD amount."""
    if not salary_text or salary_text == "Not specified":
        return 0

    cleaned = salary_text.replace(",", "").replace("$", "").replace("€", "").replace("£", "")

    # Try to find numbers
    numbers = re.findall(r"(\d+)", cleaned)
    if not numbers:
        return 0

    amount = int(numbers[0])

    # Guess if annual or monthly or hourly
    lower = salary_text.lower()
    if "hour" in lower or "/hr" in lower:
        return amount * 160  # hourly to monthly
    elif "year" in lower or "annual" in lower or amount > 30000:
        return amount // 12  # annual to monthly
    elif "month" in lower or (amount >= 1000 and amount <= 30000):
        return amount
    else:
        # If number is large, assume annual
        if amount > 50000:
            return amount // 12
        return amount


def detect_pay_type(salary_text, job_type):
    """Detect pay type from text."""
    if not salary_text or salary_text == "Not specified":
        return job_type if job_type else "Not specified"
    lower = salary_text.lower()
    if "hour" in lower:
        return "Hourly"
    elif "year" in lower or "annual" in lower:
        return "Annual"
    elif "month" in lower:
        return "Monthly"
    return job_type if job_type else "Not specified"

"""
Remotive Scraper - FIXED
=========================
Remotive has a free public API at:
  https://remotive.com/api/remote-jobs

Supports filtering by category. No auth needed.
Max 4 requests per day recommended, but we query once per category.
"""

import requests
from datetime import datetime
import re


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}

# ALL relevant categories on Remotive
CATEGORIES = [
    "software-dev",
    "data",
    "machine-learning",
    "devops",
    "product",
    "qa",
]

# Also search by keyword directly (gets more results)
KEYWORD_SEARCHES = [
    "intern",
    "internship",
    "AI intern",
    "python intern",
    "react intern",
    "full stack intern",
    "backend intern",
    "frontend intern",
    "software engineer intern",
    "machine learning intern",
    "data science intern",
    "web developer intern",
    "remote internship",
]


def search_remotive(keywords, min_hourly=10):
    """
    Search Remotive using their public API.
    Hits both category-based and keyword-based endpoints.
    """
    jobs = []
    seen_ids = set()

    # Method 1: Search by category (broader)
    for category in CATEGORIES:
        try:
            url = f"https://remotive.com/api/remote-jobs?category={category}&limit=100"
            response = requests.get(url, headers=HEADERS, timeout=15)

            if response.status_code != 200:
                continue

            data = response.json()
            job_listings = data.get("jobs", [])

            for job in job_listings:
                parsed = parse_remotive_job(job, seen_ids, keywords)
                if parsed:
                    jobs.append(parsed)
                    seen_ids.add(job.get("id", ""))

        except requests.RequestException:
            continue

    print(f"  [Remotive] Categories searched: {len(CATEGORIES)}")

    # Method 2: Search by keyword (more targeted)
    for kw in KEYWORD_SEARCHES:
        try:
            url = f"https://remotive.com/api/remote-jobs?search={requests.utils.quote(kw)}&limit=50"
            response = requests.get(url, headers=HEADERS, timeout=15)

            if response.status_code != 200:
                continue

            data = response.json()
            job_listings = data.get("jobs", [])

            for job in job_listings:
                parsed = parse_remotive_job(job, seen_ids, keywords)
                if parsed:
                    jobs.append(parsed)
                    seen_ids.add(job.get("id", ""))

        except requests.RequestException:
            continue

    print(f"  [Remotive] Total unique matched: {len(jobs)}")
    return jobs


def parse_remotive_job(job, seen_ids, keywords):
    """Parse a single Remotive job listing."""
    try:
        job_id = job.get("id", "")
        if job_id in seen_ids:
            return None

        title = job.get("title", "")
        company = job.get("company_name", "N/A")
        description = job.get("description", "").lower()
        candidate_location = job.get("candidate_required_location", "Worldwide")
        job_type = job.get("job_type", "")
        url_link = job.get("url", "")
        pub_date = job.get("publication_date", "")
        salary_text = job.get("salary", "") or "Not specified"
        tags = job.get("tags", [])
        category = job.get("category", "")

        title_lower = title.lower()
        all_text = f"{title_lower} {description} {' '.join(tags).lower()} {category.lower()}"

        # Check tech keyword match - be more lenient
        tech_terms = [
            "python", "javascript", "react", "node", "fastapi",
            "django", "flask", "ai", "machine learning", "ml",
            "llm", "data", "full stack", "fullstack", "backend",
            "frontend", "software", "developer", "engineer",
            "aws", "docker", "postgresql", "api", "web",
            "deep learning", "nlp", "rag", "vector",
        ]

        matches_tech = any(term in all_text for term in tech_terms)
        if not matches_tech:
            return None

        # Check location allows worldwide/India
        if not is_location_ok(candidate_location):
            return None

        # Parse salary
        salary_monthly_usd = parse_salary(salary_text)

        # Extract tech tags from description for better scoring
        found_techs = [t for t in tech_terms if t in all_text]

        return {
            "title": title,
            "company": company,
            "salary": salary_text,
            "salary_monthly_usd": salary_monthly_usd,
            "type": job_type if job_type else "full_time",
            "location": candidate_location if candidate_location else "Worldwide",
            "source": "Remotive",
            "link": url_link,
            "tags": ", ".join(found_techs[:10]),
            "date_posted": pub_date[:10] if pub_date else "Recent",
            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def is_location_ok(location):
    """Check if the job allows hiring from India/worldwide."""
    if not location:
        return True
    loc_lower = location.lower()
    ok_terms = ["worldwide", "anywhere", "global", "india", "asia", "remote", "international"]
    reject = ["us only", "usa only", "uk only", "eu only", "europe only", "canada only"]

    if any(r in loc_lower for r in reject):
        return False
    if any(t in loc_lower for t in ok_terms):
        return True
    # Be lenient — include unless explicitly restricted
    return True


def parse_salary(salary_text):
    """Parse salary text into monthly USD."""
    if not salary_text or salary_text == "Not specified":
        return 0
    cleaned = salary_text.replace(",", "").replace("$", "").replace("€", "").replace("£", "")
    numbers = re.findall(r"(\d+)", cleaned)
    if not numbers:
        return 0
    amount = int(numbers[0])
    lower = salary_text.lower()
    if "hour" in lower or "/hr" in lower:
        return amount * 160
    elif "year" in lower or "annual" in lower or amount > 30000:
        return amount // 12
    elif "month" in lower or (1000 <= amount <= 30000):
        return amount
    elif amount > 50000:
        return amount // 12
    return amount

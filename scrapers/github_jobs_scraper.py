"""
Hidden Gem Sources - Himalayas + Jobicy
========================================
These are legit job boards with free APIs that most people don't check.
Less competition = better chances.

Himalayas API: https://himalayas.app/jobs/api (no auth, pagination, keyword search)
Jobicy API: https://jobicy.com/api/v2/remote-jobs (no auth, tag filter)
"""

import requests
from datetime import datetime
import re
import time


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}


def search_github_awesome_remote(keywords, min_hourly=10):
    """Search hidden gem sources."""
    jobs = []
    jobs.extend(search_himalayas(keywords))
    jobs.extend(search_jobicy(keywords))
    return jobs


def search_himalayas(keywords):
    """
    Himalayas.app - Free JSON API with keyword search and pagination.
    No auth required. Supports: keyword, seniority, employment_type.
    """
    jobs = []
    seen_ids = set()
    print("  [Himalayas] Searching with keyword queries...")

    # Search with multiple relevant keywords
    search_terms = [
        "python developer",
        "AI engineer",
        "full stack",
        "backend developer",
        "react developer",
        "machine learning",
        "software engineer",
        "web developer",
        "junior developer",
        "intern",
    ]

    for term in search_terms:
        try:
            url = "https://himalayas.app/jobs/api"
            params = {
                "limit": 50,
                "offset": 0,
                "query": term,
            }

            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue

            data = response.json()
            job_listings = data.get("jobs", [])

            for item in job_listings:
                try:
                    job_id = item.get("id", item.get("slug", ""))
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = item.get("title", "")
                    company = item.get("companyName", item.get("company_name", ""))
                    description = item.get("description", "").lower()[:500]
                    categories = item.get("categories", [])
                    salary_min = item.get("minSalary", 0) or 0
                    salary_max = item.get("maxSalary", 0) or 0
                    location = item.get("location", "Remote")
                    seniority = item.get("seniority", "")
                    job_url = item.get("applicationLink", item.get("url", ""))
                    pub_date = item.get("pubDate", item.get("publishedAt", ""))
                    slug = item.get("slug", "")

                    if not title or not company:
                        continue

                    # Extract tech from title + description
                    all_text = f"{title.lower()} {description} {' '.join(categories).lower()}"
                    tech_terms = [
                        "python", "javascript", "react", "node", "fastapi",
                        "ai", "machine learning", "llm", "data", "full stack",
                        "backend", "frontend", "software", "developer", "engineer",
                        "aws", "docker", "api", "web", "deep learning",
                    ]
                    found_techs = [t for t in tech_terms if t in all_text]

                    # Must match at least 1 tech term
                    if not found_techs:
                        continue

                    # Parse salary
                    salary_text = "Not specified"
                    salary_monthly = 0
                    if salary_min and salary_min > 0:
                        salary_monthly = salary_min // 12
                        if salary_max:
                            salary_text = f"${salary_min:,}-${salary_max:,}/year"
                        else:
                            salary_text = f"${salary_min:,}/year"

                    # Build link
                    if not job_url:
                        job_url = f"https://himalayas.app/jobs/{slug}" if slug else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": salary_text,
                        "salary_monthly_usd": salary_monthly,
                        "type": seniority if seniority else "Remote",
                        "location": location if location else "Remote",
                        "source": "Himalayas",
                        "link": job_url,
                        "tags": ", ".join(found_techs),
                        "date_posted": pub_date[:10] if pub_date else "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            time.sleep(0.5)  # Be nice to the API

        except requests.RequestException:
            continue

    print(f"  [Himalayas] Found {len(jobs)} tech jobs")
    return jobs


def search_jobicy(keywords):
    """
    Jobicy.com - Free API, max 50 jobs per call.
    Endpoint: https://jobicy.com/api/v2/remote-jobs
    Params: count (1-50), tag (search keyword), geo (region)
    """
    jobs = []
    seen_ids = set()
    print("  [Jobicy] Searching with tag queries...")

    # Search multiple tags - focus on internships
    search_tags = [
        "intern",
        "internship",
        "trainee",
        "python-intern",
        "software-intern",
        "AI-intern",
        "data-intern",
        "web-intern",
        "react-intern",
        "backend-intern",
        "full-stack-intern",
        "machine-learning-intern",
    ]

    for tag in search_tags:
        try:
            url = "https://jobicy.com/api/v2/remote-jobs"
            params = {
                "count": 50,
                "tag": tag,
            }

            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue

            data = response.json()
            job_listings = data.get("jobs", [])

            for item in job_listings:
                try:
                    job_id = item.get("id", item.get("url", ""))
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = item.get("jobTitle", "")
                    company = item.get("companyName", "")
                    job_type = item.get("jobType", "")
                    location = item.get("jobGeo", "Remote")
                    url_link = item.get("url", "")
                    pub_date = item.get("pubDate", "")
                    industry = item.get("jobIndustry", [])
                    salary_min = item.get("annualSalaryMin", "")
                    salary_max = item.get("annualSalaryMax", "")
                    salary_currency = item.get("salaryCurrency", "USD")

                    if not title or not company:
                        continue

                    title_lower = title.lower()
                    all_text = f"{title_lower} {' '.join(industry).lower() if isinstance(industry, list) else str(industry).lower()}"

                    # Broad tech check
                    tech_terms = [
                        "python", "react", "ai", "machine learning",
                        "full stack", "backend", "frontend", "software",
                        "data", "developer", "engineer", "web", "devops",
                        "javascript", "node", "cloud",
                    ]
                    found_techs = [t for t in tech_terms if t in all_text]
                    if not found_techs:
                        continue

                    # Parse salary
                    salary_monthly = 0
                    salary_display = "Not specified"
                    if salary_min:
                        try:
                            min_sal = int(str(salary_min).replace(",", "").replace("$", ""))
                            max_sal = int(str(salary_max).replace(",", "").replace("$", "")) if salary_max else min_sal
                            salary_monthly = min_sal // 12
                            salary_display = f"${min_sal:,}-${max_sal:,}/year ({salary_currency})"
                        except (ValueError, TypeError):
                            pass

                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": salary_display,
                        "salary_monthly_usd": salary_monthly,
                        "type": job_type if job_type else "Remote",
                        "location": location if location else "Anywhere",
                        "source": "Jobicy",
                        "link": url_link,
                        "tags": ", ".join(found_techs),
                        "date_posted": pub_date[:10] if pub_date else "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            time.sleep(0.5)

        except requests.RequestException:
            continue

    print(f"  [Jobicy] Found {len(jobs)} tech jobs")
    return jobs

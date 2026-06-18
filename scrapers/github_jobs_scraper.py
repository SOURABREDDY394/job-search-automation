"""
GitHub/Dev Community Job Sources
==================================
Hidden gem sources that most people don't check:
1. GitHub repos that aggregate remote jobs
2. Dev.to job listings
3. Various curated remote job lists

These have LESS competition because casual applicants don't find them.
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
    """
    Search curated job sources from GitHub repos and dev communities.
    These are the hidden gems that don't show up on main job boards.
    """
    jobs = []

    # Source 1: Himalayas.app (remote job API - free, less known)
    jobs.extend(search_himalayas(keywords))

    # Source 2: Jobicy (remote jobs API)
    jobs.extend(search_jobicy(keywords))

    return jobs


def search_himalayas(keywords):
    """
    Himalayas.app - Remote job board with a clean API.
    Less known = less competition. Legit companies.
    """
    jobs = []
    print("  [Himalayas] Searching remote jobs API...")

    try:
        # Their API endpoint
        url = "https://himalayas.app/jobs/api"
        params = {
            "limit": 50,
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"  [Himalayas] HTTP {response.status_code}")
            return jobs

        data = response.json()
        job_listings = data.get("jobs", [])

        for item in job_listings:
            try:
                title = item.get("title", "")
                company = item.get("companyName", item.get("company_name", ""))
                description = item.get("description", "").lower()
                categories = item.get("categories", [])
                salary_min = item.get("minSalary", 0)
                salary_max = item.get("maxSalary", 0)
                location = item.get("location", "Remote")
                job_url = item.get("applicationLink", item.get("url", ""))
                pub_date = item.get("pubDate", item.get("publishedAt", ""))

                title_lower = title.lower()
                all_text = f"{title_lower} {description} {' '.join(categories).lower()}"

                # Check relevance to our keywords
                matches = any(
                    kw.lower().replace(" intern", "") in all_text
                    for kw in keywords
                )

                if not matches:
                    continue

                # Parse salary
                salary_text = "Not specified"
                salary_monthly = 0
                if salary_min and salary_min > 0:
                    salary_monthly = salary_min // 12
                    salary_text = f"${salary_min:,}-${salary_max:,}/year" if salary_max else f"${salary_min:,}/year"

                jobs.append({
                    "title": title,
                    "company": company if company else "Unknown",
                    "salary": salary_text,
                    "salary_monthly_usd": salary_monthly,
                    "type": "Remote",
                    "location": location,
                    "source": "Himalayas",
                    "link": job_url if job_url else f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    "tags": ", ".join(categories) if categories else "remote",
                    "date_posted": pub_date[:10] if pub_date else "Recent",
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            except Exception:
                continue

        print(f"  [Himalayas] Processed {len(job_listings)} listings, {len(jobs)} matched")

    except requests.RequestException as e:
        print(f"  [Himalayas] Error: {e}")

    return jobs


def search_jobicy(keywords):
    """
    Jobicy - Remote job board with RSS/API feed.
    Good for finding tech roles at remote-first companies.
    """
    jobs = []
    print("  [Jobicy] Searching remote jobs...")

    try:
        # Jobicy API
        url = "https://jobicy.com/api/v2/remote-jobs"
        params = {
            "count": 50,
            "tag": "python,javascript,ai,machine-learning,react",
            "geo": "anywhere",
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"  [Jobicy] HTTP {response.status_code}")
            return jobs

        data = response.json()
        job_listings = data.get("jobs", [])

        for item in job_listings:
            try:
                title = item.get("jobTitle", "")
                company = item.get("companyName", "")
                job_type = item.get("jobType", "")
                location = item.get("jobGeo", "Remote")
                url_link = item.get("url", "")
                pub_date = item.get("pubDate", "")
                salary_text = item.get("annualSalaryMin", "")
                salary_max = item.get("annualSalaryMax", "")

                title_lower = title.lower()

                # Check relevance
                matches = any(
                    kw.lower().replace(" intern", "") in title_lower
                    for kw in keywords
                )

                if not matches:
                    # Also check if title contains common tech terms
                    tech_check = any(t in title_lower for t in [
                        "python", "react", "ai", "machine learning",
                        "full stack", "backend", "frontend", "software",
                        "data", "developer", "engineer",
                    ])
                    if not tech_check:
                        continue

                # Parse salary
                salary_monthly = 0
                salary_display = "Not specified"
                if salary_text:
                    try:
                        min_sal = int(str(salary_text).replace(",", "").replace("$", ""))
                        max_sal = int(str(salary_max).replace(",", "").replace("$", "")) if salary_max else min_sal
                        salary_monthly = min_sal // 12
                        salary_display = f"${min_sal:,}-${max_sal:,}/year"
                    except (ValueError, TypeError):
                        pass

                jobs.append({
                    "title": title,
                    "company": company if company else "Unknown",
                    "salary": salary_display,
                    "salary_monthly_usd": salary_monthly,
                    "type": job_type if job_type else "Remote",
                    "location": location if location else "Anywhere",
                    "source": "Jobicy",
                    "link": url_link,
                    "tags": "remote",
                    "date_posted": pub_date[:10] if pub_date else "Recent",
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            except Exception:
                continue

        print(f"  [Jobicy] Processed {len(job_listings)} listings, {len(jobs)} matched")

    except requests.RequestException as e:
        print(f"  [Jobicy] Error: {e}")

    return jobs

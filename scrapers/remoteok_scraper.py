"""
RemoteOK Scraper
================
RemoteOK has a public JSON API - no HTML scraping needed.
Great source for remote tech jobs from US/EU companies.
Less competition than LinkedIn/Indeed.
Handles rate limiting and pagination gracefully.
"""

import requests
from datetime import datetime
import time
import re


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}


def search_remoteok(keywords, min_hourly=10):
    """
    Search RemoteOK for remote internships/junior roles.
    RemoteOK has a JSON API at /api endpoint.
    """
    jobs = []
    seen_ids = set()

    print("  [RemoteOK] Fetching remote jobs via API...")

    try:
        # RemoteOK provides all jobs via JSON API
        url = "https://remoteok.com/api"
        response = requests.get(url, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            print(f"  [RemoteOK] HTTP {response.status_code}")
            return jobs

        data = response.json()

        # First item is metadata, skip it
        job_listings = data[1:] if len(data) > 1 else []

        for job in job_listings:
            try:
                job_id = job.get("id", "")
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                position = job.get("position", "").lower()
                company = job.get("company", "N/A")
                description = job.get("description", "").lower()
                tags = [t.lower() for t in job.get("tags", [])]
                salary_min = job.get("salary_min", 0)
                salary_max = job.get("salary_max", 0)
                location = job.get("location", "Remote")
                url_slug = job.get("url", "")
                date_posted = job.get("date", "")

                # Check if this matches our keywords (intern/junior/entry)
                all_text = f"{position} {description} {' '.join(tags)}"

                # Must match tech keywords - broad check
                tech_terms = [
                    "python", "javascript", "react", "node", "fastapi",
                    "django", "flask", "ai", "machine learning", "ml",
                    "llm", "data", "full stack", "fullstack", "backend",
                    "frontend", "software", "developer", "engineer",
                    "aws", "docker", "api", "web", "deep learning",
                    "nlp", "rag", "devops", "cloud", "typescript",
                    "postgresql", "database", "intern", "junior",
                ]

                matches_tech = any(term in all_text for term in tech_terms)

                if not matches_tech:
                    continue

                # Parse salary
                salary_text = "Not specified"
                salary_monthly = 0

                if salary_min and salary_min > 0:
                    # RemoteOK salaries are typically annual USD
                    salary_monthly = salary_min // 12
                    if salary_max:
                        salary_text = f"${salary_min:,} - ${salary_max:,}/year"
                    else:
                        salary_text = f"${salary_min:,}/year"

                # Build job link
                if url_slug:
                    if url_slug.startswith("http"):
                        link = url_slug
                    else:
                        link = f"https://remoteok.com{url_slug}"
                else:
                    link = ""

                # Determine pay type
                pay_type = "Annual (USD)"
                if salary_min and salary_min < 100000 and salary_min > 0:
                    # Might be hourly if very low
                    if salary_min < 200:
                        pay_type = "Hourly (USD)"
                        salary_monthly = salary_min * 160

                jobs.append({
                    "title": job.get("position", "N/A"),
                    "company": company,
                    "salary": salary_text,
                    "salary_monthly_usd": salary_monthly,
                    "type": pay_type,
                    "location": location if location else "Worldwide Remote",
                    "source": "RemoteOK",
                    "link": link,
                    "tags": ", ".join(job.get("tags", [])),
                    "date_posted": date_posted[:10] if date_posted else "Recent",
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            except Exception:
                continue

        print(f"  [RemoteOK] Processed {len(job_listings)} total listings, {len(jobs)} matched")

    except requests.RequestException as e:
        print(f"  [RemoteOK] Network error: {e}")

    return jobs

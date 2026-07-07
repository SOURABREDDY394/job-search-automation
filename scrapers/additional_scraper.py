"""
Additional Sources - Specifically targeting intern/junior roles
===============================================================
These scrape pages that specifically list intern/junior/entry level positions.
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
    )
}


def search_additional_sources(keywords, min_hourly=10):
    """Search additional sources specifically for intern/junior roles."""
    jobs = []
    jobs.extend(search_remoteok_junior())
    jobs.extend(search_startup_jobs())
    return jobs


def search_remoteok_junior():
    """
    RemoteOK has tag-specific URLs for junior/intern jobs.
    Hit those directly instead of filtering the general feed.
    """
    jobs = []
    seen_ids = set()

    # RemoteOK tag-based URLs that target entry level
    tag_urls = [
        "https://remoteok.com/api?tag=junior",
        "https://remoteok.com/api?tag=intern",
        "https://remoteok.com/api?tag=entry",
        "https://remoteok.com/api?tag=python",
        "https://remoteok.com/api?tag=react",
        "https://remoteok.com/api?tag=ai",
        "https://remoteok.com/api?tag=fullstack",
        "https://remoteok.com/api?tag=machinelearning",
    ]

    print("  [RemoteOK-Tags] Searching junior/intern specific tags...")

    for url in tag_urls:
        try:
            response = requests.get(url, headers={
                "User-Agent": "JobSearchBot/1.0",
                "Accept": "application/json",
            }, timeout=15)

            if response.status_code != 200:
                continue

            data = response.json()
            listings = data[1:] if len(data) > 1 else []

            for job in listings:
                try:
                    job_id = job.get("id", "")
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    position = job.get("position", "").lower()
                    company = job.get("company", "N/A")
                    tags = [t.lower() for t in job.get("tags", [])]
                    salary_min = job.get("salary_min", 0)
                    salary_max = job.get("salary_max", 0)
                    location = job.get("location", "Remote")
                    url_slug = job.get("url", "")

                    # Skip senior roles
                    if any(term in position for term in ["senior", "sr.", "lead", "principal", "staff", "director"]):
                        continue

                    # Must be tech related
                    all_text = f"{position} {' '.join(tags)}"
                    tech_terms = [
                        "python", "javascript", "react", "node", "fastapi",
                        "ai", "machine learning", "ml", "llm", "data",
                        "full stack", "fullstack", "backend", "frontend",
                        "software", "developer", "engineer", "web",
                        "aws", "docker", "api", "deep learning",
                    ]
                    if not any(t in all_text for t in tech_terms):
                        continue

                    # Build link
                    if url_slug:
                        link = url_slug if url_slug.startswith("http") else f"https://remoteok.com{url_slug}"
                    else:
                        link = ""

                    # Salary
                    salary_text = "Not specified"
                    salary_monthly = 0
                    if salary_min and salary_min > 0:
                        salary_monthly = salary_min // 12
                        salary_text = f"${salary_min:,}-${salary_max:,}/year" if salary_max else f"${salary_min:,}/year"

                    found_techs = [t for t in tech_terms if t in all_text]

                    jobs.append({
                        "title": job.get("position", "N/A"),
                        "company": company,
                        "salary": salary_text,
                        "salary_monthly_usd": salary_monthly,
                        "type": "Remote",
                        "location": location if location else "Worldwide",
                        "source": "RemoteOK",
                        "link": link,
                        "tags": ", ".join(found_techs),
                        "date_posted": job.get("date", "")[:10] if job.get("date") else "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            time.sleep(1)

        except requests.RequestException:
            continue

    print(f"  [RemoteOK-Tags] Found {len(jobs)} junior/mid tech jobs")
    return jobs


def search_startup_jobs():
    """
    Search startup-focused job boards for entry-level roles.
    Uses public listings from various startup boards.
    """
    jobs = []

    print("  [Startups] Searching startup job boards...")

    # Try WorkAtAStartup direct search
    try:
        url = "https://www.workatastartup.com/companies?demographic=any&hasJobs=true&industry=B2B&interviewProcess=any&jobType=fulltime&layout=list-compact&numEmployees=1-10&query=&role=eng&sortBy=created_desc&tab=any&usVisaNotRequired=any"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Try to parse company listings
            company_cards = soup.find_all("div", class_="company-card")
            for card in company_cards[:20]:
                try:
                    name_tag = card.find("a", class_="company-name")
                    if name_tag:
                        company_name = name_tag.get_text(strip=True)
                        link = f"https://www.workatastartup.com{name_tag.get('href', '')}"
                        jobs.append({
                            "title": "Engineering Roles (YC Startup)",
                            "company": f"{company_name} (YC)",
                            "salary": "Not specified",
                            "salary_monthly_usd": 0,
                            "type": "Startup",
                            "location": "Remote",
                            "source": "YCombinator",
                            "link": link,
                            "tags": "yc, startup, engineering",
                            "date_posted": "Recent",
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                except Exception:
                    continue
    except Exception:
        pass

    print(f"  [Startups] Found {len(jobs)} startup positions")
    return jobs

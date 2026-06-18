"""
Y Combinator Work at a Startup Scraper
========================================
YC startups are some of the best places to intern:
- Fast hiring (small teams need help NOW)
- Cutting-edge AI/tech work
- Great learning opportunity
- Many hire remote globally

Uses the public YC job board API.
"""

import requests
from datetime import datetime
import re


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}

# Algolia search for YC jobs
YC_API_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/queries"
YC_APP_ID = "45BWZJ1SGC"
YC_API_KEY = "Zjk5ZmFjMzg2NmMxYTA1MjkzZDQ1MGUyMGI1YjdiMzAxMzU2NTQ0NTRjZTIyYjc5Mjg5N2RjMDk1NTFmMTYxYmZpbHRlcnM9bGVnYWN5X29wc19hbGxfdGV4dCUzQSUyMkhpcmluZyUyMg=="


def search_yc_startups(keywords, min_hourly=10):
    """
    Search Y Combinator's Work at a Startup board.
    These are legit, funded startups that often hire remote.
    """
    jobs = []

    print("  [YC] Searching Y Combinator startup jobs...")

    try:
        # Search YC job board via their Algolia-powered API
        # We'll use a simpler approach - scrape their job listings page
        url = "https://www.workatastartup.com/jobs"

        # Search for specific roles
        search_terms = [
            "intern",
            "junior ai",
            "junior full stack",
            "junior backend",
            "entry level",
            "ai engineer",
            "full stack",
            "python",
            "machine learning",
        ]

        for term in search_terms:
            api_url = f"https://www.workatastartup.com/companies/jobs?query={requests.utils.quote(term)}&remote=true"

            try:
                response = requests.get(api_url, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    continue

                # Try to parse as JSON (their API might return JSON)
                try:
                    data = response.json()
                    if isinstance(data, list):
                        for item in data:
                            job = parse_yc_job(item, term)
                            if job:
                                jobs.append(job)
                    elif isinstance(data, dict) and "jobs" in data:
                        for item in data["jobs"]:
                            job = parse_yc_job(item, term)
                            if job:
                                jobs.append(job)
                except (ValueError, KeyError):
                    pass

            except requests.RequestException:
                continue

        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in jobs:
            key = (job["title"].lower()[:40], job["company"].lower()[:20])
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        jobs = unique_jobs

        print(f"  [YC] Found {len(jobs)} YC startup positions")

    except Exception as e:
        print(f"  [YC] Error: {e}")

    return jobs


def parse_yc_job(item, search_term):
    """Parse a YC job listing into our standard format."""
    try:
        title = item.get("title", item.get("role", ""))
        company = item.get("company_name", item.get("company", {}).get("name", "Unknown"))
        location = item.get("location", "Remote")
        job_url = item.get("url", item.get("absolute_url", ""))

        if not title:
            return None

        # Get salary info
        min_salary = item.get("salary_min", 0)
        max_salary = item.get("salary_max", 0)
        salary_text = "Not specified"
        salary_monthly = 0

        if min_salary:
            salary_monthly = min_salary // 12
            salary_text = f"${min_salary:,}-${max_salary:,}/year" if max_salary else f"${min_salary:,}/year"

        # Build link
        if not job_url:
            company_slug = company.lower().replace(" ", "-")
            job_url = f"https://www.workatastartup.com/companies/{company_slug}"

        return {
            "title": title,
            "company": f"{company} (YC Startup)",
            "salary": salary_text,
            "salary_monthly_usd": salary_monthly,
            "type": "Startup",
            "location": location if location else "Remote",
            "source": "YCombinator",
            "link": job_url,
            "tags": f"yc, startup, {search_term}",
            "date_posted": "Recent",
            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


def search_wellfound(keywords, min_hourly=10):
    """
    Search Wellfound (formerly AngelList Talent) for startup jobs.
    Another great source for startup internships.
    """
    jobs = []
    print("  [Wellfound] Searching startup jobs...")

    try:
        # Wellfound doesn't have a public API, but we can try their listing pages
        for keyword in keywords[:5]:  # Limit to avoid rate limiting
            search_url = (
                f"https://wellfound.com/role/l/"
                f"?keywords={requests.utils.quote(keyword)}"
                f"&remote=true&jobType=internship"
            )

            try:
                response = requests.get(search_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
                    "Accept": "text/html",
                }, timeout=15)

                if response.status_code == 200:
                    # Parse what we can from the response
                    # Wellfound heavily uses JS rendering, so results may be limited
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Try to find job cards
                    cards = soup.find_all("div", attrs={"data-test": "StartupResult"})
                    for card in cards:
                        try:
                            title_tag = card.find("a", class_="job-title")
                            company_tag = card.find("a", class_="startup-link")

                            if title_tag:
                                jobs.append({
                                    "title": title_tag.get_text(strip=True),
                                    "company": company_tag.get_text(strip=True) if company_tag else "Startup",
                                    "salary": "Not specified",
                                    "salary_monthly_usd": 0,
                                    "type": "Startup",
                                    "location": "Remote",
                                    "source": "Wellfound",
                                    "link": f"https://wellfound.com{title_tag.get('href', '')}",
                                    "tags": f"startup, {keyword}",
                                    "date_posted": "Recent",
                                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                })
                        except Exception:
                            continue

            except requests.RequestException:
                continue

    except Exception as e:
        print(f"  [Wellfound] Error: {e}")

    print(f"  [Wellfound] Found {len(jobs)} startup positions")
    return jobs

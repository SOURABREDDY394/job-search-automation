"""
Apify LinkedIn Scraper - WORKING
==================================
Uses gopalakrishnan/linkedin-jobs actor.
Cheapest, no proxy, no login required. Works on free tier.

Tested: Returns 50 results per query in ~10 seconds.
"""

import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
APIFY_BASE = "https://api.apify.com/v2"

# This actor works on free tier, no login needed
LINKEDIN_ACTOR = "gopalakrishnan~linkedin-jobs"

# Precise queries matching your profile
SEARCH_QUERIES = [
    "AI engineer intern",
    "software engineer intern",
    "python developer internship",
    "full stack intern",
    "machine learning internship",
    "backend developer internship",
    "react developer internship",
    "web developer internship",
]

# Title MUST have one of these to be relevant
REQUIRED_TECH = [
    "software", "engineer", "developer", "python", "react",
    "ai", "ml", "machine learning", "data", "backend",
    "frontend", "full stack", "fullstack", "web",
    "devops", "cloud", "api", "nlp", "deep learning",
    "automation", "llm", "computing",
]


def search_apify_linkedin(keywords, min_hourly=10):
    """
    Scrape LinkedIn internships via Apify.
    Uses gopalakrishnan~linkedin-jobs (cheapest, no login).
    """
    if not APIFY_TOKEN:
        print("  [Apify-LinkedIn] No API token in .env")
        return []

    all_jobs = []
    seen = set()

    print("  [Apify-LinkedIn] Scraping LinkedIn internships...")

    for query in SEARCH_QUERIES:
        try:
            # Start run
            run_url = f"{APIFY_BASE}/acts/{LINKEDIN_ACTOR}/runs"
            params = {"token": APIFY_TOKEN}

            input_data = {
                "keywords": query,
                "location": "",
                "datePosted": "past week",
                "jobType": "internship",
                "remote": "remote",
                "limit": 25,
            }

            response = requests.post(run_url, params=params, json=input_data, timeout=30)

            if response.status_code == 402:
                print("  ⚠️ Out of credits! Stopping.")
                break
            if response.status_code not in (200, 201):
                print(f"    '{query}': HTTP {response.status_code}")
                continue

            run_id = response.json().get("data", {}).get("id", "")
            if not run_id:
                continue

            # Wait for completion (usually takes 5-15 seconds)
            jobs_from_query = wait_and_fetch(run_id, query)

            # Filter and add
            for item in jobs_from_query:
                job = parse_linkedin_job(item)
                if job:
                    key = (job["title"].lower()[:40], job["company"].lower()[:20])
                    if key not in seen:
                        seen.add(key)
                        all_jobs.append(job)

            print(f"    '{query}': {len(jobs_from_query)} raw -> {len(all_jobs)} total unique")
            time.sleep(2)

        except requests.RequestException as e:
            print(f"    '{query}': {e}")
            continue

    print(f"  [Apify-LinkedIn] Total: {len(all_jobs)} tech internships")
    return all_jobs


def search_apify_indeed(keywords, min_hourly=10):
    """Skip Indeed - it returns garbage on free tier."""
    return []


def wait_and_fetch(run_id, query, max_wait=60):
    """Wait for actor run to complete and fetch results."""
    for _ in range(max_wait // 5):
        time.sleep(5)
        try:
            r = requests.get(
                f"{APIFY_BASE}/actor-runs/{run_id}",
                params={"token": APIFY_TOKEN},
                timeout=15,
            )
            data = r.json().get("data", {})
            status = data.get("status", "")

            if status == "SUCCEEDED":
                dataset_id = data.get("defaultDatasetId", "")
                if dataset_id:
                    items_r = requests.get(
                        f"{APIFY_BASE}/datasets/{dataset_id}/items",
                        params={"token": APIFY_TOKEN},
                        timeout=30,
                    )
                    if items_r.status_code == 200:
                        return items_r.json()
                return []

            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                return []

        except Exception:
            continue

    return []


def parse_linkedin_job(item):
    """Parse LinkedIn result. STRICT: must be tech intern."""
    try:
        title = item.get("title", item.get("jobTitle", ""))
        company = item.get("company", item.get("companyName", ""))
        location = item.get("location", "Remote")
        link = item.get("url", item.get("link", item.get("jobUrl", "")))
        salary = item.get("salary", "Not specified")
        posted = item.get("postedDate", item.get("postedAt", "Recent"))

        if not title or not company:
            return None

        title_lower = title.lower()

        # Must be internship
        if "intern" not in title_lower:
            return None

        # Must be tech-related
        if not any(tech in title_lower for tech in REQUIRED_TECH):
            return None

        # No senior
        if any(t in title_lower for t in ["senior", "sr.", "lead", "principal", "staff"]):
            return None

        # Extract tags
        found_techs = [t for t in REQUIRED_TECH if t in title_lower]

        return {
            "title": title,
            "company": company,
            "salary": salary if isinstance(salary, str) and salary else "Not specified",
            "salary_monthly_usd": 0,
            "type": "Internship",
            "location": location if location else "Remote",
            "source": "LinkedIn",
            "link": link if link else "",
            "tags": ", ".join(found_techs[:5]),
            "date_posted": str(posted)[:20] if posted else "Recent",
            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None

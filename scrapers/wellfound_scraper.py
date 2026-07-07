"""
Wellfound (AngelList) Scraper
==============================
Wellfound uses GraphQL internally. We hit their /graphql endpoint
with job search queries. These are startup jobs — they hire fast.

No public API, but the GraphQL endpoint is accessible with the right headers.
"""

import requests
from datetime import datetime
import json
import time


GRAPHQL_URL = "https://wellfound.com/graphql"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://wellfound.com",
    "Referer": "https://wellfound.com/jobs",
    "X-Requested-With": "XMLHttpRequest",
    "apollographql-client-name": "talent-web",
}

# GraphQL query to search jobs
JOB_SEARCH_QUERY = """
query JobSearchResults($query: String, $page: Int, $remotePreference: RemotePreference) {
  talent {
    jobSearchResults(query: $query, page: $page, remotePreference: $remotePreference) {
      totalCount
      pageCount
      jobs {
        id
        title
        slug
        remote
        compensation
        jobType
        liveStartAt
        startup {
          name
          slug
          companySize
          highConcept
          logoUrl
        }
        roleLocation {
          location
        }
      }
    }
  }
}
"""


def search_wellfound(keywords, min_hourly=10):
    """
    Search Wellfound for startup intern/junior jobs.
    Uses their GraphQL endpoint.
    """
    jobs = []
    seen_ids = set()

    print("  [Wellfound] Searching startup jobs via GraphQL...")

    # Search terms specifically for entry-level
    search_terms = [
        "intern",
        "junior developer",
        "junior software engineer",
        "junior full stack",
        "junior backend",
        "AI intern",
        "python junior",
        "react junior",
        "entry level developer",
        "new grad engineer",
    ]

    for term in search_terms:
        try:
            payload = {
                "operationName": "JobSearchResults",
                "variables": {
                    "query": term,
                    "page": 1,
                    "remotePreference": "REMOTE_ONLY",
                },
                "query": JOB_SEARCH_QUERY,
            }

            response = requests.post(
                GRAPHQL_URL,
                json=payload,
                headers=HEADERS,
                timeout=15,
            )

            if response.status_code != 200:
                # Try alternative approach - scrape the search page
                continue

            data = response.json()

            # Navigate GraphQL response
            search_results = (
                data.get("data", {})
                .get("talent", {})
                .get("jobSearchResults", {})
            )

            if not search_results:
                continue

            job_listings = search_results.get("jobs", [])

            for job in job_listings:
                try:
                    job_id = job.get("id", "")
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = job.get("title", "")
                    slug = job.get("slug", "")
                    remote = job.get("remote", False)
                    compensation = job.get("compensation", "")
                    job_type = job.get("jobType", "")

                    startup = job.get("startup", {})
                    company = startup.get("name", "Unknown")
                    company_slug = startup.get("slug", "")
                    company_size = startup.get("companySize", "")
                    tagline = startup.get("highConcept", "")

                    location_data = job.get("roleLocation", {})
                    location = location_data.get("location", "Remote") if location_data else "Remote"

                    # Skip senior roles
                    title_lower = title.lower()
                    if any(term in title_lower for term in ["senior", "sr.", "lead", "principal", "staff", "director"]):
                        continue

                    # Parse compensation
                    salary_text = compensation if compensation else "Not specified"
                    salary_monthly = parse_wellfound_salary(compensation)

                    # Build link
                    link = f"https://wellfound.com/jobs/{slug}" if slug else f"https://wellfound.com/company/{company_slug}/jobs"

                    # Tags
                    tags_list = []
                    if company_size:
                        tags_list.append(f"size:{company_size}")
                    if tagline:
                        tags_list.append(tagline[:50])
                    tags_list.append("startup")

                    jobs.append({
                        "title": title,
                        "company": f"{company} (Startup)",
                        "salary": salary_text,
                        "salary_monthly_usd": salary_monthly,
                        "type": job_type if job_type else "Startup",
                        "location": location if location else "Remote",
                        "source": "Wellfound",
                        "link": link,
                        "tags": ", ".join(tags_list),
                        "date_posted": "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            time.sleep(1)  # Rate limit

        except requests.RequestException:
            continue

    # If GraphQL didn't work, try the HTML fallback
    if len(jobs) == 0:
        jobs = search_wellfound_html(keywords)

    print(f"  [Wellfound] Found {len(jobs)} startup jobs")
    return jobs


def search_wellfound_html(keywords):
    """
    Fallback: Try scraping Wellfound search pages directly.
    These URLs are publicly accessible.
    """
    jobs = []
    from bs4 import BeautifulSoup

    # Wellfound has these public-facing job listing pages
    urls = [
        "https://wellfound.com/role/remote-software-engineer-intern-jobs",
        "https://wellfound.com/role/remote-full-stack-developer-intern-jobs",
        "https://wellfound.com/role/remote-backend-developer-intern-jobs",
        "https://wellfound.com/role/remote-frontend-developer-intern-jobs",
        "https://wellfound.com/role/remote-machine-learning-engineer-intern-jobs",
        "https://wellfound.com/role/remote-junior-software-engineer-jobs",
        "https://wellfound.com/role/remote-junior-full-stack-developer-jobs",
    ]

    for url in urls:
        try:
            response = requests.get(url, headers={
                "User-Agent": HEADERS["User-Agent"],
                "Accept": "text/html,application/xhtml+xml",
            }, timeout=15)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to find job listings in script tags (Next.js data)
            scripts = soup.find_all("script", {"type": "application/json"})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Look for job data in the JSON
                    jobs_from_json = extract_jobs_from_json(data)
                    jobs.extend(jobs_from_json)
                except (json.JSONDecodeError, TypeError):
                    continue

            # Also try standard HTML parsing
            job_cards = soup.find_all("div", {"data-test": "JobSearchResult"})
            if not job_cards:
                job_cards = soup.find_all("a", href=lambda h: h and "/jobs/" in h if h else False)

            for card in job_cards[:20]:
                try:
                    title_text = card.get_text(strip=True)[:100]
                    href = card.get("href", "")
                    if title_text and href:
                        jobs.append({
                            "title": title_text,
                            "company": "Startup (Wellfound)",
                            "salary": "Not specified",
                            "salary_monthly_usd": 0,
                            "type": "Startup",
                            "location": "Remote",
                            "source": "Wellfound",
                            "link": f"https://wellfound.com{href}" if href.startswith("/") else href,
                            "tags": "startup, wellfound",
                            "date_posted": "Recent",
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                except Exception:
                    continue

            time.sleep(1)

        except requests.RequestException:
            continue

    return jobs


def extract_jobs_from_json(data, depth=0):
    """Recursively search JSON for job listings."""
    jobs = []
    if depth > 5:
        return jobs

    if isinstance(data, dict):
        # Check if this looks like a job object
        if "title" in data and ("startup" in data or "company" in data):
            title = data.get("title", "")
            company = data.get("startup", {}).get("name", "") if isinstance(data.get("startup"), dict) else data.get("company", "")
            if title and company:
                jobs.append({
                    "title": title,
                    "company": f"{company} (Startup)",
                    "salary": data.get("compensation", "Not specified"),
                    "salary_monthly_usd": 0,
                    "type": "Startup",
                    "location": "Remote",
                    "source": "Wellfound",
                    "link": f"https://wellfound.com/jobs/{data.get('slug', '')}",
                    "tags": "startup",
                    "date_posted": "Recent",
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        else:
            for value in data.values():
                jobs.extend(extract_jobs_from_json(value, depth + 1))
    elif isinstance(data, list):
        for item in data:
            jobs.extend(extract_jobs_from_json(item, depth + 1))

    return jobs


def parse_wellfound_salary(compensation):
    """Parse Wellfound compensation string."""
    if not compensation:
        return 0
    import re
    # Try to find dollar amounts like "$80k – $120k"
    numbers = re.findall(r"\$?(\d+)k?", compensation.lower())
    if numbers:
        amount = int(numbers[0])
        if amount < 500:  # Likely in thousands (e.g., 80 = $80k)
            amount *= 1000
        return amount // 12
    return 0

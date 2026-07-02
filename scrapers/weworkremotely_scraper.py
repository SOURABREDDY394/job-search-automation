"""
We Work Remotely Scraper
=========================
One of the best remote job boards. US/EU companies that actually
hire remote workers worldwide. Less spam than LinkedIn.
Scrapes their listing pages.
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

# WWR category URLs for programming/tech
CATEGORY_URLS = [
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs",
    "https://weworkremotely.com/categories/remote-back-end-programming-jobs",
    "https://weworkremotely.com/categories/remote-front-end-programming-jobs",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs",
]


def search_weworkremotely(keywords, min_hourly=10):
    """
    Search We Work Remotely for intern/junior remote tech roles.
    """
    jobs = []
    seen_links = set()

    for cat_url in CATEGORY_URLS:
        try:
            response = requests.get(cat_url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"  [WWR] HTTP {response.status_code} for {cat_url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # WWR job listing items
            job_sections = soup.find_all("li", class_="feature")
            job_sections += soup.find_all("li", class_="new")

            for item in job_sections:
                try:
                    # Find the job link
                    link_tag = item.find("a", href=True)
                    if not link_tag:
                        continue

                    href = link_tag.get("href", "")
                    if not href or href in seen_links:
                        continue
                    seen_links.add(href)

                    full_link = f"https://weworkremotely.com{href}" if href.startswith("/") else href

                    # Extract title
                    title_tag = item.find("span", class_="title")
                    title = title_tag.get_text(strip=True) if title_tag else ""

                    # Extract company
                    company_tag = item.find("span", class_="company")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"

                    # Extract region
                    region_tag = item.find("span", class_="region")
                    region = region_tag.get_text(strip=True) if region_tag else "Anywhere"

                    if not title:
                        continue

                    title_lower = title.lower()
                    all_text = f"{title_lower} {company.lower()}"

                    # Check if entry level / intern
                    is_entry = any(term in all_text for term in [
                        "intern", "junior", "jr", "entry",
                        "associate", "trainee", "graduate",
                        "early career", "new grad",
                    ])

                    # Check tech match
                    matches_tech = any(
                        kw.lower().replace(" intern", "") in all_text
                        for kw in keywords
                    )

                    # Include if entry level OR matches our tech keywords
                    # (many WWR jobs are open to all levels)
                    if not (is_entry or matches_tech):
                        continue

                    # Check if location is worldwide/open
                    if not is_location_worldwide(region):
                        continue

                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": "Not specified",  # WWR rarely shows salary in listings
                        "salary_monthly_usd": 0,
                        "type": "Full-time Remote",
                        "location": region if region else "Anywhere",
                        "source": "WeWorkRemotely",
                        "link": full_link,
                        "tags": extract_category(cat_url),
                        "date_posted": "Recent",
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                except Exception:
                    continue

            print(f"  [WWR] {extract_category(cat_url)}: {len(job_sections)} listings scanned")
            time.sleep(1)

        except requests.RequestException as e:
            print(f"  [WWR] Network error: {e}")

    print(f"  [WWR] Total matched: {len(jobs)}")
    return jobs


def is_location_worldwide(region):
    """Check if location allows global applicants."""
    if not region:
        return True
    lower = region.lower()
    ok_terms = ["anywhere", "worldwide", "global", "remote", "asia", "india", "international"]
    # Reject US-only or EU-only
    reject = ["us only", "usa only", "north america only", "europe only", "eu only", "uk only", "canada only"]

    if any(r in lower for r in reject):
        return False
    if any(t in lower for t in ok_terms):
        return True
    # Be lenient with unspecified
    return True


def extract_category(url):
    """Extract readable category from URL."""
    if "full-stack" in url:
        return "Full Stack"
    elif "back-end" in url:
        return "Backend"
    elif "front-end" in url:
        return "Frontend"
    elif "devops" in url:
        return "DevOps"
    return "Programming"

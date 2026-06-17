"""
Hacker News "Who is Hiring" Scraper
====================================
Every month, HN posts a "Who is Hiring" thread where real companies
post jobs directly. These are HIGH QUALITY leads with less competition
than job boards. Many are open to remote worldwide.

Uses the HN Algolia API to search recent hiring threads.
"""

import requests
from datetime import datetime, timedelta
import re
import html


HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "application/json",
}


def search_hn_hiring(keywords, min_hourly=10):
    """
    Search Hacker News "Who is Hiring" threads for matching remote jobs.
    Uses HN Algolia search API.
    """
    jobs = []

    print("  [HN] Searching recent 'Who is Hiring' posts...")

    try:
        # Search for recent "Who is Hiring" threads (monthly)
        # Get posts from last 60 days
        timestamp = int((datetime.now() - timedelta(days=60)).timestamp())

        # First, find the "Who is Hiring" thread
        search_url = (
            f"https://hn.algolia.com/api/v1/search?"
            f"query=Ask HN: Who is hiring&tags=story"
            f"&numericFilters=created_at_i>{timestamp}"
        )

        response = requests.get(search_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"  [HN] Failed to find hiring threads: HTTP {response.status_code}")
            return jobs

        threads = response.json().get("hits", [])

        # Find the most recent "Who is hiring" thread
        hiring_thread = None
        for thread in threads:
            title = thread.get("title", "").lower()
            if "who is hiring" in title and "freelancer" not in title:
                hiring_thread = thread
                break

        if not hiring_thread:
            print("  [HN] No recent 'Who is Hiring' thread found")
            return jobs

        thread_id = hiring_thread["objectID"]
        thread_title = hiring_thread.get("title", "")
        print(f"  [HN] Found thread: {thread_title}")

        # Now get all comments (job postings) from this thread
        comments_url = (
            f"https://hn.algolia.com/api/v1/search?"
            f"tags=comment,story_{thread_id}"
            f"&hitsPerPage=500"
        )

        response = requests.get(comments_url, headers=HEADERS, timeout=20)
        if response.status_code != 200:
            print(f"  [HN] Failed to get comments: HTTP {response.status_code}")
            return jobs

        comments = response.json().get("hits", [])
        print(f"  [HN] Processing {len(comments)} job posts...")

        for comment in comments:
            try:
                comment_text = comment.get("comment_text", "")
                if not comment_text:
                    continue

                # Clean HTML
                clean_text = clean_html(comment_text)
                text_lower = clean_text.lower()

                # Must mention REMOTE
                is_remote = any(term in text_lower for term in [
                    "remote", "work from home", "wfh",
                    "anywhere", "worldwide", "distributed",
                ])

                if not is_remote:
                    continue

                # Must match our tech keywords
                matches_tech = any(
                    kw.lower().replace(" intern", "") in text_lower
                    for kw in keywords
                )

                if not matches_tech:
                    continue

                # Check for intern/junior friendliness
                is_entry_friendly = any(term in text_lower for term in [
                    "intern", "junior", "entry", "new grad",
                    "early career", "0-2 year", "0-3 year",
                    "all levels", "any level", "fresh",
                ])

                # Extract company name (usually first line)
                lines = clean_text.strip().split("\n")
                first_line = lines[0] if lines else ""

                # Try to extract company and role from first line
                company = extract_company(first_line)
                title = extract_role(first_line, clean_text)

                # Extract salary if mentioned
                salary_info = extract_salary(clean_text)

                # HN link
                comment_id = comment.get("objectID", "")
                link = f"https://news.ycombinator.com/item?id={comment_id}"

                jobs.append({
                    "title": title,
                    "company": company,
                    "salary": salary_info.get("text", "Not specified"),
                    "salary_monthly_usd": salary_info.get("monthly", 0),
                    "type": salary_info.get("type", "Not specified"),
                    "location": "Remote",
                    "source": "HackerNews",
                    "link": link,
                    "tags": "entry-level" if is_entry_friendly else "all-levels",
                    "date_posted": hiring_thread.get("created_at", "")[:10],
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            except Exception:
                continue

        print(f"  [HN] Matched {len(jobs)} remote tech positions")

    except requests.RequestException as e:
        print(f"  [HN] Network error: {e}")

    return jobs


def clean_html(text):
    """Remove HTML tags and decode entities."""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "\n", text)
    # Clean up whitespace
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def extract_company(first_line):
    """Try to extract company name from the first line of HN post."""
    # HN hiring posts typically start with: "Company Name | Role | Location | ..."
    parts = re.split(r"[|/\-–—]", first_line)
    if parts:
        company = parts[0].strip()
        # Clean up
        company = re.sub(r"\(.*?\)", "", company).strip()
        if len(company) > 50:
            company = company[:50] + "..."
        return company if company else "Unknown"
    return "Unknown"


def extract_role(first_line, full_text):
    """Extract job role/title."""
    parts = re.split(r"[|/\-–—]", first_line)
    if len(parts) > 1:
        role = parts[1].strip()
        if len(role) > 60:
            role = role[:60] + "..."
        return role if role else "Software Engineer"

    # Try to find role keywords in text
    role_patterns = [
        r"((?:senior |junior |lead )?(?:software|ai|ml|full.?stack|backend|frontend|data|machine learning|deep learning) (?:engineer|developer|scientist|intern))",
    ]
    text_lower = full_text.lower()
    for pattern in role_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).title()

    return "Software/AI Role"


def extract_salary(text):
    """Extract salary information from job post text."""
    text_lower = text.lower()

    # Look for salary patterns
    # $XXX,XXX or $XXXk patterns
    salary_patterns = [
        r"\$(\d{2,3})k?\s*[-–to]+\s*\$?(\d{2,3})k?\s*(?:per\s+hour|/hr|hourly)",
        r"\$(\d{2,3})\s*[-–to/]+\s*\$?(\d{2,3})\s*(?:per\s+hour|/hr|hourly|/h)",
        r"\$(\d{2,3},?\d{3})\s*[-–to]+\s*\$?(\d{2,3},?\d{3})",
        r"\$(\d{2,3})k\s*[-–to]+\s*\$?(\d{2,3})k",
        r"(\d{2,3})k?\s*[-–to]+\s*(\d{2,3})k?\s*usd",
    ]

    for pattern in salary_patterns:
        match = re.search(pattern, text_lower)
        if match:
            low = match.group(1).replace(",", "")
            high = match.group(2).replace(",", "")
            try:
                low_num = int(low)
                high_num = int(high)

                # Determine if hourly or annual
                if "hour" in text_lower[match.start():match.end()+20]:
                    monthly = low_num * 160
                    return {
                        "text": f"${low_num}-${high_num}/hour",
                        "monthly": monthly,
                        "type": "Hourly",
                    }

                # If numbers have 'k' suffix or are small, multiply by 1000
                if low_num < 500:
                    low_num *= 1000
                    high_num *= 1000

                monthly = low_num // 12
                return {
                    "text": f"${low_num:,}-${high_num:,}/year",
                    "monthly": monthly,
                    "type": "Annual",
                }
            except ValueError:
                pass

    return {"text": "Not specified", "monthly": 0, "type": "Not specified"}

"""
GitHub Job List Scraper
========================
Scrapes the speedyapply/2026-AI-College-Jobs repo which maintains
a daily-updated list of 463+ international AI internships.

Companies include: Microsoft, NVIDIA, TikTok, Cloudflare, Mistral AI,
Perplexity, Snowflake, Bosch, Airbus, etc. from US/UK/Germany/
Singapore/Canada/Australia/India.

Source: https://github.com/speedyapply/2026-AI-College-Jobs
"""

import requests
import re
from datetime import datetime


RAW_URL = "https://raw.githubusercontent.com/speedyapply/2026-AI-College-Jobs/main/INTERN_INTL.md"

HEADERS = {
    "User-Agent": "JobSearchBot/1.0 (personal use)",
    "Accept": "text/plain",
}


def search_github_lists(keywords, min_hourly=10):
    """
    Fetch and parse the curated GitHub internship list.
    Returns jobs that match our tech criteria and are recent (<30 days old).
    """
    jobs = []

    print("  [GitHub-Lists] Fetching curated AI internship list...")

    try:
        response = requests.get(RAW_URL, headers=HEADERS, timeout=20)
        if response.status_code != 200:
            print(f"  [GitHub-Lists] HTTP {response.status_code}")
            return jobs

        content = response.text

        # Parse markdown table rows
        # Format: | Company | Position | Location | Apply Link | Age |
        lines = content.split("\n")

        for line in lines:
            if not line.startswith("|"):
                continue
            if "Company" in line or "---" in line:
                continue

            try:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) < 5:
                    continue

                company_col = cols[0]
                position = cols[1]
                location = cols[2]
                link_col = cols[3]
                age_col = cols[4]

                # Extract company name from markdown link
                company_match = re.search(r"\*\*(.+?)\*\*", company_col)
                company = company_match.group(1) if company_match else "Unknown"

                # Extract apply link
                link_match = re.search(r'href="(.+?)"', link_col)
                apply_link = link_match.group(1) if link_match else ""

                # Parse age (e.g., "7d", "14d")
                age_match = re.search(r"(\d+)d", age_col)
                age_days = int(age_match.group(1)) if age_match else 999

                # Only include recent jobs (< 60 days)
                if age_days > 60:
                    continue

                # Skip ONLY the biggest/most competitive companies
                big_companies = [
                    "nvidia", "microsoft", "meta", "google", "amazon", "apple",
                    "tiktok", "bytedance",
                    "citadel", "jane street", "optiver", "two sigma",
                    "goldman sachs", "morgan stanley", "jp morgan",
                ]
                if any(bc in company.lower() for bc in big_companies):
                    continue

                # Skip PhD-only roles
                position_lower = position.lower()
                if "phd" in position_lower and "bs" not in position_lower and "ms" not in position_lower:
                    continue

                # Skip senior roles
                if any(t in position_lower for t in ["senior", "sr.", "lead", "principal", "staff"]):
                    continue

                # Check if relevant to your skills
                relevant_terms = [
                    "ai", "machine learning", "ml", "data",
                    "software", "engineer", "developer",
                    "full stack", "backend", "frontend",
                    "python", "llm", "deep learning",
                    "nlp", "computer vision", "automation",
                    "intern", "research",
                ]
                if not any(t in position_lower for t in relevant_terms):
                    continue

                # Determine tags based on position
                found_tags = []
                for t in relevant_terms:
                    if t in position_lower:
                        found_tags.append(t)

                jobs.append({
                    "title": position.strip(),
                    "company": company,
                    "salary": "Not specified (FAANG-tier pay)",
                    "salary_monthly_usd": 0,
                    "type": "Internship",
                    "location": location.strip(),
                    "source": "GitHub-CuratedList",
                    "link": apply_link,
                    "tags": ", ".join(found_tags[:5]),
                    "date_posted": f"{age_days}d ago",
                    "date_found": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            except Exception:
                continue

        print(f"  [GitHub-Lists] Found {len(jobs)} relevant internships (< 60 days old)")

    except requests.RequestException as e:
        print(f"  [GitHub-Lists] Error: {e}")

    return jobs

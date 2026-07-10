"""
Job Search Automation - Personalized for Sourab
=================================================
Skills: Python, FastAPI, React, RAG, LLM, pgvector, Docker, AWS

Pipeline:
1. Search 7 sources (including hidden gems most people don't check)
2. Smart filter (scam detection, entry-level only, skill matching)
3. Duplicate tracking (only NEW jobs notified)
4. Desktop notifications
5. HTML dashboard with filters
6. CSV export

Sources:
- RemoteOK (API) - High volume remote jobs
- Remotive (API) - Curated remote tech
- WeWorkRemotely (scrape) - Premium remote board
- Hacker News (API) - Direct from hiring managers
- YC Startups (API) - Funded startups that hire fast
- Himalayas (API) - Less known, less competition
- Jobicy (API) - Global remote jobs

Usage:
    python job_search.py
"""

import pandas as pd
from datetime import datetime
import os

from config import (
    SEARCH_KEYWORDS,
    MIN_MONTHLY_USD,
    MIN_HOURLY_USD,
    INCLUDE_HOURLY,
    OUTPUT_FILE,
    LOG_FILE,
    DASHBOARD_FILE,
)
from scrapers.remoteok_scraper import search_remoteok
from scrapers.remotive_scraper import search_remotive
from scrapers.weworkremotely_scraper import search_weworkremotely
from scrapers.hn_scraper import search_hn_hiring
from scrapers.yc_scraper import search_yc_startups
from scrapers.github_jobs_scraper import search_github_awesome_remote
from scrapers.additional_scraper import search_additional_sources
from scrapers.wellfound_scraper import search_wellfound as search_wellfound_gql
from scrapers.simplyhired_scraper import search_simplyhired
from scrapers.github_list_scraper import search_github_lists
from scrapers.apify_scraper import search_apify_linkedin, search_apify_indeed
from filters import filter_jobs
from tracker import find_new_jobs, get_stats
from notifier import notify_new_jobs
from dashboard import generate_dashboard
from cold_email import generate_cold_emails, find_emails_from_hn_posts


def run_search():
    """Run the full personalized job search pipeline."""
    print("=" * 65)
    print("  🔍 JOB SEARCH - Personalized for Sourab")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: AI Engineer / Full Stack / Backend (Remote)")
    print(f"  Min Pay: ${MIN_MONTHLY_USD}/mo | ${MIN_HOURLY_USD}/hr")
    print(f"  Sources: 7 platforms (including hidden gems)")
    print("=" * 65)
    print()

    all_jobs = []

    # === SEARCH PHASE ===

    # 1. RemoteOK (JSON API)
    print("[1/7] RemoteOK (API)...")
    try:
        jobs = search_remoteok(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 2. Remotive (JSON API - curated)
    print("[2/7] Remotive (API)...")
    try:
        jobs = search_remotive(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 3. We Work Remotely (HTML)
    print("[3/7] WeWorkRemotely...")
    try:
        jobs = search_weworkremotely(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 4. Hacker News "Who is Hiring" (API - highest quality)
    print("[4/7] Hacker News 'Who is Hiring' (API)...")
    try:
        jobs = search_hn_hiring(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 5. YC Startups (fast hiring, funded)
    print("[5/7] Y Combinator Startups...")
    try:
        jobs = search_yc_startups(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ Skipped: {e}\n")

    # 6. Himalayas + Jobicy (hidden gems)
    print("[6/7] Hidden Gems (Himalayas + Jobicy)...")
    try:
        jobs = search_github_awesome_remote(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 7. Wellfound/AngelList (startups - GraphQL)
    print("[7/8] Wellfound (Startup Jobs)...")
    try:
        jobs = search_wellfound_gql(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 8. Additional sources (RemoteOK tag-based + startup boards)
    print("[8/9] Additional Sources (tag-specific + startups)...")
    try:
        jobs = search_additional_sources(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 9. SimplyHired (large aggregator)
    print("[9/10] SimplyHired (job aggregator)...")
    try:
        jobs = search_simplyhired(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 10. GitHub Curated List (NVIDIA, Microsoft, TikTok, Cloudflare, Mistral, etc.)
    print("[10/12] GitHub Curated List (Global Internships)...")
    try:
        jobs = search_github_lists(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 11. Apify - LinkedIn (real internships, bypasses anti-bot)
    print("[11/12] LinkedIn via Apify...")
    try:
        jobs = search_apify_linkedin(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # 12. Apify - Indeed (real internships)
    print("[12/12] Indeed via Apify...")
    try:
        jobs = search_apify_indeed(SEARCH_KEYWORDS, MIN_HOURLY_USD)
        all_jobs.extend(jobs)
        print(f"  ✓ {len(jobs)} jobs\n")
    except Exception as e:
        print(f"  ✗ {e}\n")

    # === FILTER PHASE ===
    print(f"{'─' * 50}")
    print(f"[Filter] Raw results: {len(all_jobs)}")
    all_jobs = remove_duplicates(all_jobs)
    print(f"[Filter] After dedup: {len(all_jobs)}")
    all_jobs = filter_jobs(all_jobs)
    print(f"[Filter] After smart filter: {len(all_jobs)}")
    print()

    # === TRACKING ===
    new_jobs = find_new_jobs(all_jobs)
    stats = get_stats()
    print(f"[Tracker] New this run: {len(new_jobs)}")
    print(f"[Tracker] All-time seen: {stats['total_seen']}")
    print()

    # === NOTIFICATIONS ===
    if new_jobs:
        notify_new_jobs(new_jobs, len(all_jobs))

    # === SAVE ===
    save_results(all_jobs)

    # === DASHBOARD ===
    generate_dashboard(all_jobs, new_count=len(new_jobs))

    # === COLD EMAILS ===
    print("\n[Cold Email] Generating personalized outreach emails...")
    try:
        generate_cold_emails(all_jobs)
        # Also find real emails from HN posts
        hn_emails = find_emails_from_hn_posts(all_jobs)
        if hn_emails:
            print(f"  📬 Found {len(hn_emails)} HN posts with direct email addresses")
            save_hn_emails(hn_emails)
    except Exception as e:
        print(f"  ✗ Cold email generation failed: {e}")

    # === SUMMARY ===
    print_summary(all_jobs, new_jobs)

    return all_jobs


def remove_duplicates(jobs):
    """Remove duplicate jobs."""
    seen = set()
    unique = []
    for job in jobs:
        key = (
            job["title"].lower().strip()[:50],
            job["company"].lower().strip()[:30],
        )
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


def save_hn_emails(hn_emails):
    """Save extracted HN emails to a file."""
    with open("hn_direct_emails.md", "w", encoding="utf-8") as f:
        f.write("# 🎯 Direct Emails from HN Hiring Posts\n\n")
        f.write("> These are REAL emails posted by hiring managers on Hacker News.\n")
        f.write("> Response rate is much higher than cold outreach.\n\n---\n\n")
        for item in hn_emails:
            f.write(f"## {item['company']} – {item['job_title']}\n")
            f.write(f"**Emails:** {', '.join(item['emails'])}\n")
            f.write(f"**Post:** {item['link']}\n\n---\n\n")
    print(f"  📬 Direct emails saved to: hn_direct_emails.md")


def save_results(jobs):
    """Save to CSV."""
    if not jobs:
        print("  No jobs found.\n")
        return

    df = pd.DataFrame(jobs)

    columns = [
        "title", "company", "salary", "salary_monthly_usd", "type",
        "location", "source", "link", "tags", "relevance_score",
        "skill_match_score", "is_entry_level", "is_startup",
        "date_posted", "date_found",
    ]
    columns = [c for c in columns if c in df.columns]
    df = df[columns]

    # Append to existing
    if os.path.exists(OUTPUT_FILE):
        try:
            existing = pd.read_csv(OUTPUT_FILE)
            df = pd.concat([existing, df]).drop_duplicates(
                subset=["title", "company", "source"], keep="last"
            )
        except (PermissionError, pd.errors.EmptyDataError):
            pass

    try:
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        print(f"  💾 Saved: {OUTPUT_FILE} ({len(df)} total)")
    except PermissionError:
        # File is open in another app (Excel, etc.)
        alt_file = "jobs_found_latest.csv"
        df.to_csv(alt_file, index=False, encoding="utf-8")
        print(f"  ⚠️  {OUTPUT_FILE} is locked (close Excel). Saved to: {alt_file}")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {len(jobs)} filtered | CSV: {len(df)}\n")


def print_summary(jobs, new_jobs):
    """Print results summary."""
    print()
    print("=" * 65)
    print("  RESULTS")
    print("=" * 65)

    if not jobs:
        print("\n  Nothing found. Try again later.")
        return

    print(f"\n  Total: {len(jobs)} | New: {len(new_jobs)}")

    # By source
    sources = {}
    for j in jobs:
        s = j["source"]
        sources[s] = sources.get(s, 0) + 1
    print(f"\n  Sources:")
    for s, c in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"    {s}: {c}")

    # Counts
    entry = sum(1 for j in jobs if j.get("is_entry_level"))
    startups = sum(1 for j in jobs if j.get("is_startup"))
    print(f"\n  🎯 Intern/Junior: {entry}")
    print(f"  🚀 Startups: {startups}")

    # Salary
    paid = [j for j in jobs if j.get("salary_monthly_usd", 0) > 0]
    if paid:
        avg = sum(j["salary_monthly_usd"] for j in paid) // len(paid)
        top = max(j["salary_monthly_usd"] for j in paid)
        print(f"\n  💰 Salary ({len(paid)} with data):")
        print(f"     Avg: ${avg:,}/mo (₹{avg*83:,}/mo)")
        print(f"     Top: ${top:,}/mo (₹{top*83:,}/mo)")

    # Top new jobs
    if new_jobs:
        print(f"\n  {'─' * 50}")
        print(f"  🆕 TOP NEW JOBS:\n")
        for i, job in enumerate(new_jobs[:15], 1):
            salary = job.get("salary", "")
            entry_tag = " 🎯" if job.get("is_entry_level") else ""
            startup_tag = " 🚀" if job.get("is_startup") else ""
            score = job.get("relevance_score", 0)
            skill = job.get("skill_match_score", 0)

            print(f"  {i:2}. {job['title']}{entry_tag}{startup_tag}")
            print(f"      {job['company']} | {salary}")
            print(f"      Score: {score}/100 | Skills match: {skill}%")
            if job.get("link"):
                print(f"      → {job['link']}")
            print()

    print("=" * 65)
    print(f"  📁 {OUTPUT_FILE} | 📊 {DASHBOARD_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    run_search()

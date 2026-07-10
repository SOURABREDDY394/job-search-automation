"""
Smart Job Filters - Personalized for Sourab's Profile
======================================================
1. Matches jobs to YOUR skills (Python, FastAPI, React, RAG, LLM, etc.)
2. Detects and removes SCAM postings
3. Prioritizes startups (they hire fast)
4. Filters for entry-level/intern only
5. Scores relevance based on skill match
"""

import re
from config import (
    ENTRY_LEVEL_TERMS,
    EXCLUDE_TERMS,
    SCAM_INDICATORS,
    STARTUP_SIGNALS,
    MY_SKILLS,
    SKIP_BIG_COMPANIES,
)


def filter_jobs(jobs):
    """
    Full filtering pipeline:
    1. Remove scams
    2. Remove senior roles
    3. Score by skill match
    4. Prioritize startups
    5. Sort by relevance
    """
    filtered = []
    scam_count = 0
    senior_count = 0

    for job in jobs:
        title = job.get("title", "").lower()
        company = job.get("company", "").lower()
        tags = job.get("tags", "").lower()
        link = job.get("link", "").lower()

        all_text = f"{title} {company} {tags}"

        # === SCAM CHECK ===
        # Skip scam check for curated sources (manually maintained, 100% legit)
        if job.get("source") not in ("GitHub-CuratedList",):
            if is_scam(all_text, link, job):
                scam_count += 1
                continue

        # === ONLY INTERNSHIPS — strict check ===
        # Must have "intern" or "internship" or "trainee" or "co-op" in the TITLE
        # NO EXCEPTIONS — you're a student, can't do full-time
        intern_terms = ["intern", "internship", "trainee", "co-op", "coop", "apprentice"]
        if not any(term in title for term in intern_terms):
            senior_count += 1
            continue

        # === MUST BE TECH ROLE (no marketing/design/sales garbage) ===
        tech_required = [
            "software", "engineer", "developer", "python", "react",
            "ai", "ml", "machine learning", "data science", "backend",
            "frontend", "full stack", "fullstack", "web", "devops",
            "cloud", "api", "nlp", "deep learning", "automation",
            "llm", "computer", "coding", "programming",
        ]
        # Check TITLE specifically — not just all_text
        if not any(term in title for term in tech_required):
            continue

        # === MUST BE RECENT (max 7 days old) ===
        # Removed: Apify already filters at source with "past week"
        # Don't waste scraped results by filtering again

        # === EXCLUDE SENIOR ROLES ===
        if any(term in title for term in EXCLUDE_TERMS):
            senior_count += 1
            continue

        # === QUALITY CHECK ===
        if len(job.get("title", "")) < 5:
            continue
        if job.get("company", "N/A") in ("N/A", "", "Unknown"):
            continue

        # === SCORING ===
        job["skill_match_score"] = calculate_skill_match(all_text)
        job["is_entry_level"] = any(term in all_text for term in ENTRY_LEVEL_TERMS)
        job["is_startup"] = is_startup(all_text)
        job["relevance_score"] = calculate_relevance(job)
        job["scam_safe"] = True

        filtered.append(job)

    # Sort: entry-level first, then by relevance score
    filtered.sort(
        key=lambda x: (
            x.get("is_entry_level", False),
            x.get("relevance_score", 0),
        ),
        reverse=True,
    )

    # Remove low-score jobs (except HN and curated lists which we trust)
    MIN_SCORE_THRESHOLD = 40
    before_count = len(filtered)
    filtered = [
        job for job in filtered
        if job.get("source") in ("HackerNews", "GitHub-CuratedList")
        or job.get("relevance_score", 0) >= MIN_SCORE_THRESHOLD
    ]
    low_score_removed = before_count - len(filtered)

    if scam_count > 0:
        print(f"  🚫 Removed {scam_count} suspected scam listings")
    if senior_count > 0:
        print(f"  ⏭️  Skipped {senior_count} senior/lead roles")
    if low_score_removed > 0:
        print(f"  📉 Removed {low_score_removed} low-relevance jobs (score < {MIN_SCORE_THRESHOLD})")

    return filtered


def is_too_old(date_posted):
    """
    Check if a job is older than 7 days.
    Returns True if too old.
    """
    if not date_posted or date_posted in ("Recent", ""):
        return False  # Unknown date = keep it

    date_lower = str(date_posted).lower()

    # Check relative dates like "2 weeks ago", "1 month ago"
    import re
    weeks_match = re.search(r"(\d+)\s*week", date_lower)
    months_match = re.search(r"(\d+)\s*month", date_lower)
    days_match = re.search(r"(\d+)\s*d", date_lower)

    if months_match:
        return True  # Anything in months is too old
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return weeks > 1  # More than 1 week = too old
    if days_match:
        days = int(days_match.group(1))
        return days > 7

    # Check absolute dates like "2026-06-15"
    try:
        from datetime import datetime, timedelta
        if re.match(r"\d{4}-\d{2}-\d{2}", date_lower):
            posted_date = datetime.strptime(date_lower[:10], "%Y-%m-%d")
            return (datetime.now() - posted_date).days > 7
    except (ValueError, TypeError):
        pass

    return False  # Can't parse = keep it


def is_scam(text, link, job):
    """
    Detect scam job postings using multiple signals.
    Returns True if likely a scam.
    """
    # Check scam keywords
    for indicator in SCAM_INDICATORS:
        if indicator in text:
            return True

    # Suspicious link patterns
    suspicious_domains = [
        "bit.ly", "tinyurl", "goo.gl",  # URL shorteners in job links
        "telegram.me", "t.me",  # Telegram-based "jobs"
        "wa.me",  # WhatsApp-based recruiting (red flag)
        "forms.gle",  # Google forms for "applications" (usually scam)
    ]
    if any(domain in link for domain in suspicious_domains):
        return True

    # No company name is suspicious
    company = job.get("company", "")
    if len(company) < 2 or company.lower() in ("n/a", "unknown", "hiring", "urgent"):
        return True

    # Title is all caps (spam signal)
    title = job.get("title", "")
    if title == title.upper() and len(title) > 10:
        return True

    # Extremely high salary for intern (likely scam)
    salary = job.get("salary_monthly_usd", 0)
    if salary > 25000 and "intern" in text:
        return True  # $25k/month for an intern? Scam.

    # Job description is too short (low effort posting)
    if len(text) < 30:
        return True

    return False


def is_startup(text):
    """Check if the job is at a startup (they hire faster)."""
    return any(signal in text for signal in STARTUP_SIGNALS)


def calculate_skill_match(text):
    """
    Score 0-100 based on how many of YOUR skills match the job.
    Higher = better fit for you specifically.
    """
    matched = 0
    matched_skills = []
    for skill in MY_SKILLS:
        if skill in text:
            matched += 1
            matched_skills.append(skill)

    # Use a lower threshold — a job mentioning 5+ of your skills is great
    if matched >= 8:
        score = 100
    elif matched >= 5:
        score = 80
    elif matched >= 3:
        score = 60
    elif matched >= 2:
        score = 40
    elif matched >= 1:
        score = 20
    else:
        score = 0

    return score


def calculate_relevance(job):
    """
    Overall relevance score 0-100.
    Combines: skill match + entry level + startup + salary + source quality.
    """
    score = 0
    title = job.get("title", "").lower()
    tags = job.get("tags", "").lower()
    all_text = f"{title} {tags}"

    # Skill match (0-40 points)
    skill_score = job.get("skill_match_score", 0)
    score += int(skill_score * 0.4)

    # Entry level bonus (+20)
    if job.get("is_entry_level"):
        score += 20

    # INTERN-SPECIFIC bonus (+15) — you're undergrad, internships are ideal
    title_lower = job.get("title", "").lower()
    if any(term in title_lower for term in ["intern", "internship", "trainee", "co-op", "apprentice"]):
        score += 15

    # Startup bonus (+15) - they hire fast
    if job.get("is_startup"):
        score += 15

    # Salary available (+10)
    if job.get("salary_monthly_usd", 0) > 0:
        score += 10

    # AI/ML keyword bonus (+10)
    ai_terms = ["ai", "machine learning", "llm", "rag", "nlp", "deep learning",
                "generative", "embeddings", "vector", "langchain", "openai"]
    if any(term in all_text for term in ai_terms):
        score += 10

    # Full stack / backend bonus (+5)
    if any(term in all_text for term in ["full stack", "fullstack", "backend", "fastapi", "python"]):
        score += 5

    # Source quality bonus
    source = job.get("source", "")
    source_bonus = {
        "HackerNews": 8,      # Highest quality, direct from hiring managers
        "Remotive": 10,       # Curated, legit companies - boost to pass threshold
        "Jobicy": 10,         # Good remote board - boost to pass threshold
        "Himalayas": 10,      # Hidden gem - boost to pass threshold
        "WeWorkRemotely": 8,  # Premium board
        "RemoteOK": 8,        # Good volume - boost
        "YCombinator": 12,    # Startups, fast hiring
    }
    score += source_bonus.get(source, 0)

    # Has a real link (+5)
    if job.get("link") and len(job.get("link", "")) > 10:
        score += 5

    # Penalty for missing company info (-5)
    if not job.get("company") or job.get("company") == "Unknown":
        score -= 5

    return min(score, 100)

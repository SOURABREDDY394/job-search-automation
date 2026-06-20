"""
Duplicate Tracker
==================
Keeps track of jobs already seen so you only get notified about NEW ones.
Uses a JSON file to persist seen job IDs between runs.
"""

import json
import os
from datetime import datetime

from config import HISTORY_FILE


def load_seen_jobs():
    """Load previously seen job IDs from file."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_seen_jobs(seen):
    """Save seen job IDs to file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, ensure_ascii=False)


def get_job_id(job):
    """Generate a unique ID for a job based on title + company + source."""
    title = job.get("title", "").lower().strip()[:50]
    company = job.get("company", "").lower().strip()[:30]
    source = job.get("source", "").lower()
    return f"{source}|{company}|{title}"


def find_new_jobs(jobs):
    """
    Compare jobs against history and return only NEW ones.
    Also updates the history file.
    """
    seen = load_seen_jobs()
    new_jobs = []

    for job in jobs:
        job_id = get_job_id(job)
        if job_id not in seen:
            new_jobs.append(job)
            seen[job_id] = {
                "title": job.get("title"),
                "company": job.get("company"),
                "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

    save_seen_jobs(seen)
    return new_jobs


def get_stats():
    """Get tracker statistics."""
    seen = load_seen_jobs()
    return {
        "total_seen": len(seen),
        "history_file": HISTORY_FILE,
    }

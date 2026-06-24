"""
Job Search Scheduler
====================
Runs the job search at regular intervals automatically.
Default: Every 6 hours.

Usage:
    python scheduler.py          # Run scheduler (auto-searches every 6 hours)
    python scheduler.py --now    # Run once immediately and exit
"""

import schedule
import time
import sys
from datetime import datetime

from config import SEARCH_INTERVAL_HOURS
from job_search import run_search


def scheduled_search():
    """Wrapper for scheduled execution."""
    print(f"\n{'*' * 65}")
    print(f"  Scheduled search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'*' * 65}\n")
    try:
        run_search()
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()
    print(f"\nNext search in {SEARCH_INTERVAL_HOURS} hours...\n")


def main():
    if "--now" in sys.argv:
        print("Running single search...\n")
        run_search()
        return

    print("=" * 65)
    print("  JOB SEARCH SCHEDULER - International Remote Internships")
    print(f"  Interval: Every {SEARCH_INTERVAL_HOURS} hours")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Press Ctrl+C to stop")
    print("=" * 65)

    # Run immediately on start
    scheduled_search()

    # Schedule recurring searches
    schedule.every(SEARCH_INTERVAL_HOURS).hours.do(scheduled_search)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped. Results saved in jobs_found.csv")


if __name__ == "__main__":
    main()

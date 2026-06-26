# 🔍 Job Search Automation - International Remote Internships

Automated job search that targets **international companies (US/UK/EU)** hiring remote interns globally. Way better pay and less competition than Internshala/Naukri.

## ✨ Features

- 🌍 **International sources** — RemoteOK, Remotive, WeWorkRemotely, Hacker News
- 🎯 **Smart filtering** — Only shows intern/junior roles, excludes senior positions
- 🆕 **Duplicate tracking** — Only notifies you about NEW jobs each run
- 🔔 **Desktop notifications** — Windows toast alerts for new matches
- 📊 **HTML Dashboard** — Beautiful filterable view of all jobs
- 💾 **CSV export** — Opens in Excel/Google Sheets
- ⏰ **Auto-run** — Windows Task Scheduler (every 6 hours + on login)
- 📧 **Email alerts** — Optional Gmail notifications (configure in config.py)

## 🚀 Setup

```bash
pip install -r requirements.txt
```

## 📖 Usage

```bash
# Run search once
python job_search.py

# Run on schedule (every 6 hours in terminal)
python scheduler.py

# Setup auto-run via Windows Task Scheduler
python setup_autorun.py

# Remove auto-run
python setup_autorun.py --remove
```

## 📁 Project Structure

```
automation/
├── job_search.py          # Main script - run this
├── scheduler.py           # Schedule repeated searches
├── setup_autorun.py       # Windows Task Scheduler setup
├── config.py              # All settings (keywords, salary, etc.)
├── filters.py             # Smart filtering (intern/junior only)
├── tracker.py             # Duplicate detection
├── notifier.py            # Desktop + email notifications
├── dashboard.py           # HTML dashboard generator
├── requirements.txt
├── .gitignore
├── README.md
└── scrapers/
    ├── __init__.py
    ├── remoteok_scraper.py       # RemoteOK JSON API
    ├── remotive_scraper.py       # Remotive JSON API
    ├── weworkremotely_scraper.py  # WWR HTML scraper
    └── hn_scraper.py             # Hacker News Algolia API
```

## 🎯 What It Searches For

| Category | Keywords |
|----------|----------|
| AI/ML | AI intern, ML intern, deep learning, NLP, LLM, generative AI, computer vision |
| Full Stack | Full stack intern, software engineer intern |
| Data | Data science intern |
| Web Dev | Python intern, backend intern, frontend intern |

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `SEARCH_KEYWORDS` | 14 keywords | Job titles to search |
| `MIN_MONTHLY_USD` | $250 | Min monthly pay (≈ ₹20k) |
| `MIN_HOURLY_USD` | $10 | Min hourly pay |
| `SEARCH_INTERVAL_HOURS` | 6 | Auto-search frequency |
| `ENABLE_DESKTOP_NOTIFICATIONS` | True | Windows toast alerts |
| `EMAIL_ENABLED` | False | Email notifications |

## 📊 Output Files

| File | Description |
|------|-------------|
| `jobs_found.csv` | All jobs (Excel/Sheets compatible) |
| `dashboard.html` | Visual dashboard (open in browser) |
| `seen_jobs.json` | Tracking history |
| `search_log.txt` | Search run log |

## 🔔 Notifications

**Desktop:** Automatic Windows toast notification when new jobs are found.

**Email (optional):** Set in `config.py`:
```python
EMAIL_ENABLED = True
EMAIL_TO = "your@email.com"
EMAIL_FROM = "your@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Gmail App Password
```

## 💡 Why These Sources Beat Indian Job Boards

| Source | Advantage |
|--------|-----------|
| **RemoteOK** | JSON API, US/EU companies pay $30-80/hr for interns |
| **Remotive** | Curated, remote-first companies that hire globally |
| **WeWorkRemotely** | Premium board, real companies, no spam |
| **Hacker News** | Direct from hiring managers, lowest competition |

## 🏆 Tips for Landing International Remote Internships

1. **GitHub > Resume** — Active profile with AI/ML projects wins
2. **Speed matters** — Run daily, apply within 24 hours
3. **Timezone flex** — Mention willingness to overlap with US/EU hours
4. **Cover letter** — 3 sentences: who you are, what you built, why them
5. **Portfolio site** — Even a simple one with 2-3 projects helps

## License

MIT — Use freely, star if useful ⭐

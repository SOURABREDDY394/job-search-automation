"""
HTML Dashboard Generator
=========================
Creates a beautiful HTML page to browse job results.
Open dashboard.html in your browser to view jobs.
"""

import os
from datetime import datetime

from config import DASHBOARD_FILE


def generate_dashboard(jobs, new_count=0):
    """Generate an HTML dashboard from job results."""
    if not jobs:
        return

    # Stats
    total = len(jobs)
    with_salary = len([j for j in jobs if j.get("salary_monthly_usd", 0) > 0])
    sources = {}
    for j in jobs:
        src = j.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1

    # Build job rows
    job_rows = ""
    for i, job in enumerate(jobs):
        salary = job.get("salary", "Not specified")
        salary_usd = job.get("salary_monthly_usd", 0)
        inr_display = f"₹{salary_usd * 83:,}/mo" if salary_usd > 0 else "—"
        link = job.get("link", "#")
        source = job.get("source", "")
        score = job.get("relevance_score", 0)
        is_entry = job.get("is_entry_level", False)

        # Badge colors
        source_colors = {
            "RemoteOK": "#10b981",
            "Remotive": "#6366f1",
            "WeWorkRemotely": "#f59e0b",
            "HackerNews": "#ef4444",
        }
        badge_color = source_colors.get(source, "#6b7280")
        entry_badge = '<span class="badge badge-entry">Intern/Junior</span>' if is_entry else ""

        job_rows += f"""
        <tr class="job-row" data-source="{source}" data-entry="{str(is_entry).lower()}">
            <td class="job-title">
                <a href="{link}" target="_blank">{job.get('title', 'N/A')}</a>
                {entry_badge}
            </td>
            <td>{job.get('company', 'N/A')}</td>
            <td class="salary">{salary}</td>
            <td class="inr">{inr_display}</td>
            <td><span class="badge" style="background: {badge_color}">{source}</span></td>
            <td>{job.get('location', 'Remote')}</td>
            <td class="score">{score}</td>
        </tr>
        """

    # Source filter buttons
    source_buttons = ""
    for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        source_buttons += f'<button class="filter-btn" onclick="filterSource(\'{src}\')">{src} ({count})</button>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Search Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
        }}
        .stat-card h3 {{ color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }}
        .stat-card .number {{ font-size: 2rem; font-weight: 700; color: #f1f5f9; margin-top: 4px; }}
        .stat-card .number.green {{ color: #34d399; }}
        .stat-card .number.blue {{ color: #60a5fa; }}
        .stat-card .number.purple {{ color: #a78bfa; }}
        .filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-btn {{
            background: #334155;
            color: #e2e8f0;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: #6366f1;
            color: white;
        }}
        .search-box {{
            background: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            width: 250px;
        }}
        .search-box:focus {{ outline: none; border-color: #6366f1; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 12px;
            overflow: hidden;
        }}
        th {{
            background: #334155;
            padding: 14px 16px;
            text-align: left;
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #94a3b8;
            cursor: pointer;
        }}
        th:hover {{ color: #e2e8f0; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #1e293b; }}
        tr {{ background: #1e293b; transition: background 0.2s; }}
        tr:hover {{ background: #334155; }}
        .job-title a {{
            color: #60a5fa;
            text-decoration: none;
            font-weight: 500;
        }}
        .job-title a:hover {{ text-decoration: underline; }}
        .salary {{ color: #34d399; font-weight: 600; }}
        .inr {{ color: #fbbf24; }}
        .score {{ color: #94a3b8; text-align: center; }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            color: white;
            font-weight: 500;
        }}
        .badge-entry {{
            background: #6366f1;
            margin-left: 8px;
        }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 24px;
            font-size: 0.85rem;
        }}
        @media (max-width: 768px) {{
            .stats {{ grid-template-columns: 1fr 1fr; }}
            table {{ font-size: 0.8rem; }}
            td, th {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Job Search Dashboard</h1>
        <p class="subtitle">International Remote Internships — Last updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Jobs</h3>
                <div class="number blue">{total}</div>
            </div>
            <div class="stat-card">
                <h3>New This Run</h3>
                <div class="number green">{new_count}</div>
            </div>
            <div class="stat-card">
                <h3>With Salary Info</h3>
                <div class="number purple">{with_salary}</div>
            </div>
            <div class="stat-card">
                <h3>Sources</h3>
                <div class="number">{len(sources)}</div>
            </div>
        </div>

        <div class="filters">
            <button class="filter-btn active" onclick="filterSource('all')">All ({total})</button>
            {source_buttons}
            <button class="filter-btn" onclick="filterEntry()">🎯 Intern/Junior Only</button>
            <input type="text" class="search-box" placeholder="Search jobs..." oninput="searchJobs(this.value)">
        </div>

        <table id="jobTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Role ↕</th>
                    <th onclick="sortTable(1)">Company ↕</th>
                    <th onclick="sortTable(2)">Salary ↕</th>
                    <th onclick="sortTable(3)">INR Equiv ↕</th>
                    <th onclick="sortTable(4)">Source ↕</th>
                    <th onclick="sortTable(5)">Location ↕</th>
                    <th onclick="sortTable(6)">Score ↕</th>
                </tr>
            </thead>
            <tbody>
                {job_rows}
            </tbody>
        </table>

        <p class="footer">
            Auto-generated by Job Search Automation | {total} jobs from {len(sources)} sources
        </p>
    </div>

    <script>
        function filterSource(source) {{
            const rows = document.querySelectorAll('.job-row');
            const btns = document.querySelectorAll('.filter-btn');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            rows.forEach(row => {{
                if (source === 'all' || row.dataset.source === source) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        function filterEntry() {{
            const rows = document.querySelectorAll('.job-row');
            rows.forEach(row => {{
                if (row.dataset.entry === 'true') {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        function searchJobs(query) {{
            const rows = document.querySelectorAll('.job-row');
            const q = query.toLowerCase();
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(q) ? '' : 'none';
            }});
        }}

        function sortTable(col) {{
            const table = document.getElementById('jobTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            rows.sort((a, b) => {{
                const aVal = a.cells[col].textContent.trim();
                const bVal = b.cells[col].textContent.trim();
                if (!isNaN(aVal) && !isNaN(bVal)) return bVal - aVal;
                return aVal.localeCompare(bVal);
            }});

            rows.forEach(row => tbody.appendChild(row));
        }}
    </script>
</body>
</html>"""

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  📊 Dashboard generated: {DASHBOARD_FILE}")
    print(f"     Open in browser to view results")

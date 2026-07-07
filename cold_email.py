"""
Cold Email Generator
=====================
Generates personalized cold emails for job applications.
Extracts potential contact info and generates email templates
tailored to each company/role based on Sourab's profile.

Usage:
    from cold_email import generate_cold_emails
    emails = generate_cold_emails(jobs)
"""

import re
import os
from datetime import datetime


# Your profile (from resume)
MY_PROFILE = {
    "name": "Sourab Reddy",
    "role": "AI Engineer",
    "location": "Hyderabad, India",
    "education": "BCA candidate, FSB Degree College",
    "experience": "AI Engineer Intern at Welerix (Remote, Jun 2025 – Jan 2026)",
    "key_skills": "Python, FastAPI, React, RAG pipelines, LLM integration, PostgreSQL, pgvector, Docker, AWS",
    "projects": [
        "CareCircle AI – AI-driven blood support coordination system (Python, FastAPI, React, PostgreSQL, AWS)",
        "FastRAG – Multi-PDF knowledge assistant with pgvector semantic search",
        "EventOS – AI-assisted event management platform (Top 10 SummerShip Challenge)",
    ],
    "github": "https://github.com/SOURABREDDY394",
    "linkedin": "LinkedIn profile",
    "email": "sourabreddimalla@gmail.com",
    "timezone": "IST (flexible, can overlap with US/EU timezones)",
}


# Email templates for different scenarios
TEMPLATES = {
    "startup_intern": """Subject: Excited to contribute as {role} – Available for remote internship

Hi {name},

I came across {company}'s work{about_company} and I'd love to contribute as a {role}.

I'm an AI engineer with hands-on experience building production systems:
• Built RAG pipelines with FastAPI, pgvector, and LLM integration at Welerix (remote internship)
• Created CareCircle AI – an autonomous coordination system using Python, FastAPI, React, and AWS
• Top 10 in SummerShip Challenge with EventOS (AI-assisted event platform)

My stack: {relevant_skills}

I'm available remotely from India (IST), flexible with timezone overlap. Happy to do a trial task or pair programming session.

GitHub: {github}

Would love to chat if there's a fit. Thanks for your time!

Best,
Sourab Reddy""",

    "hn_direct": """Subject: Re: Who is Hiring – {role} at {company}

Hi,

Saw your post on the HN July 2026 hiring thread. The {role} role caught my attention{about_company}.

Quick background:
• AI Engineer Intern at Welerix – built retrieval pipelines, automation, and ML features (remote)
• Projects: RAG systems with pgvector, AI coordination platform, event management with Groq
• Stack: Python, FastAPI, React, PostgreSQL, Docker, AWS, LLM/RAG

I work remotely from India and am flexible on timezones. GitHub: {github}

Would love to learn more about the role. Happy to do a take-home or chat.

Sourab""",

    "general_apply": """Subject: {role} application – AI Engineer with RAG/LLM experience

Hi {name},

I'm reaching out about the {role} position at {company}. I believe my background in AI engineering and full-stack development makes me a strong fit.

Relevant experience:
• 8 months as AI Engineer Intern at Welerix – Python, FastAPI, REST APIs, document intelligence
• Built production RAG pipelines with semantic search (pgvector, embeddings, retrieval)
• Full-stack projects with React, PostgreSQL, Docker, AWS deployment

I'm particularly drawn to {company} because {about_company}.

Available for remote work, flexible timezones. Let me know if you'd like to see more of my work.

GitHub: {github}
Portfolio: Built 4+ production AI systems (details on GitHub)

Best regards,
Sourab Reddy
sourabreddimalla@gmail.com""",
}


def generate_cold_emails(jobs, output_file="cold_emails.md"):
    """
    Generate personalized cold emails for the top jobs.
    Saves to a markdown file for easy copy-paste.
    """
    if not jobs:
        return []

    emails = []
    # Focus on top-scored jobs and HN jobs (where cold email works best)
    priority_jobs = sorted(
        jobs,
        key=lambda x: x.get("relevance_score", 0),
        reverse=True,
    )[:30]  # Top 30 jobs

    for job in priority_jobs:
        email = create_email_for_job(job)
        if email:
            emails.append(email)

    # Save to file
    save_emails(emails, output_file)
    return emails


def create_email_for_job(job):
    """Create a personalized cold email for a specific job."""
    title = job.get("title", "")
    company = job.get("company", "").replace(" (Startup)", "").replace(" (YC)", "")
    source = job.get("source", "")
    link = job.get("link", "")
    tags = job.get("tags", "")

    # Choose template based on source
    if source == "HackerNews":
        template_key = "hn_direct"
    elif "startup" in tags.lower() or source in ("Wellfound", "YCombinator"):
        template_key = "startup_intern"
    else:
        template_key = "general_apply"

    # Extract relevant skills based on job tags
    relevant_skills = extract_relevant_skills(tags, title)

    # Generate "about company" snippet
    about_company = generate_about_company(company, tags, title)

    # Guess hiring manager name (default to generic)
    name = guess_contact_name(company, source)

    # Generate email
    template = TEMPLATES[template_key]
    email_text = template.format(
        name=name,
        company=company,
        role=title if len(title) < 50 else title[:50],
        about_company=about_company,
        relevant_skills=relevant_skills,
        github=MY_PROFILE["github"],
    )

    # Generate possible email addresses
    email_guesses = guess_emails(company)

    return {
        "job_title": title,
        "company": company,
        "source": source,
        "job_link": link,
        "email_guesses": email_guesses,
        "email_text": email_text,
        "template_used": template_key,
    }


def extract_relevant_skills(tags, title):
    """Pick skills from your profile that match the job."""
    all_text = f"{tags} {title}".lower()

    skill_map = {
        "python": "Python",
        "fastapi": "FastAPI",
        "react": "React",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "node": "Node.js",
        "aws": "AWS",
        "docker": "Docker",
        "postgresql": "PostgreSQL",
        "ai": "AI/LLM integration",
        "machine learning": "Machine Learning",
        "ml": "ML",
        "llm": "LLM/RAG",
        "rag": "RAG pipelines",
        "nlp": "NLP",
        "data": "Data pipelines",
        "full stack": "Full Stack (React + FastAPI)",
        "backend": "Backend (Python, FastAPI, PostgreSQL)",
        "frontend": "Frontend (React, Tailwind)",
        "api": "REST API design",
        "vector": "Vector search (pgvector)",
    }

    matched = []
    for key, display in skill_map.items():
        if key in all_text and display not in matched:
            matched.append(display)

    if not matched:
        matched = ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"]

    return ", ".join(matched[:6])


def generate_about_company(company, tags, title):
    """Generate a short blurb about why you're interested."""
    company_lower = company.lower()
    tags_lower = tags.lower()
    title_lower = title.lower()

    if "ai" in tags_lower or "ai" in title_lower:
        return " in AI/ML"
    elif "startup" in tags_lower:
        return " – love the startup energy and pace of shipping"
    elif "full stack" in title_lower:
        return " – the full-stack role aligns perfectly with my experience"
    elif "python" in tags_lower or "backend" in title_lower:
        return " – Python backend is exactly where I thrive"
    elif "yc" in tags_lower:
        return " (YC-backed) – big fan of the YC approach to building"
    else:
        return ""


def guess_contact_name(company, source):
    """Return a greeting name."""
    if source == "HackerNews":
        return ""  # HN posts are often anonymous
    return "Hiring Manager"


def guess_emails(company):
    """
    Generate possible email patterns for cold outreach.
    Most tech companies use these patterns.
    """
    # Clean company name
    clean = company.lower().strip()
    clean = re.sub(r"[^a-z0-9\s]", "", clean)
    clean = clean.replace(" ", "")

    # Common patterns
    patterns = [
        f"jobs@{clean}.com",
        f"careers@{clean}.com",
        f"hiring@{clean}.com",
        f"hello@{clean}.com",
        f"team@{clean}.com",
    ]

    return patterns[:3]  # Return top 3 guesses


def save_emails(emails, output_file):
    """Save generated emails to a markdown file."""
    if not emails:
        return

    content = f"""# 📧 Cold Emails - Generated {datetime.now().strftime('%B %d, %Y')}

> Personalized outreach emails for top job matches.
> Copy-paste and customize further before sending.

---

"""

    for i, email in enumerate(emails, 1):
        content += f"""## {i}. {email['job_title']} at {email['company']}

**Source:** {email['source']} | **Link:** {email['job_link']}

**Try these emails:**
"""
        for guess in email['email_guesses']:
            content += f"- `{guess}`\n"

        content += f"""
**Email:**

```
{email['email_text']}
```

---

"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  📧 Cold emails saved to: {output_file} ({len(emails)} emails)")


def find_emails_from_hn_posts(jobs):
    """
    Extract actual email addresses from HN job posts.
    HN posts often include the hiring manager's email directly.
    """
    import requests

    emails_found = []

    hn_jobs = [j for j in jobs if j.get("source") == "HackerNews"][:20]

    for job in hn_jobs:
        link = job.get("link", "")
        if not link:
            continue

        # Extract comment ID
        match = re.search(r"id=(\d+)", link)
        if not match:
            continue

        comment_id = match.group(1)

        try:
            # Fetch the actual HN comment to find emails
            url = f"https://hn.algolia.com/api/v1/items/{comment_id}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            data = response.json()
            text = data.get("text", "")

            # Find emails in the text
            found = re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                text,
            )

            if found:
                emails_found.append({
                    "job_title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "emails": list(set(found)),
                    "link": link,
                })

        except Exception:
            continue

    return emails_found

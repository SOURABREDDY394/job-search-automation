# Job Search Configuration - Personalized for Sourab's Profile
# Skills: Python, FastAPI, React, RAG, LLM, pgvector, Docker, AWS

# === YOUR SKILLS (used for relevance scoring) ===
MY_SKILLS = [
    "python", "fastapi", "react", "javascript", "sql", "c++",
    "rag", "vector search", "embeddings", "prompt engineering",
    "retrieval", "llm", "machine learning", "nlp",
    "node.js", "express", "html", "css", "tailwind",
    "postgresql", "supabase", "pgvector", "mysql", "redis",
    "aws", "ec2", "docker", "git", "vercel", "render",
    "rest api", "api", "n8n", "automation",
    "langchain", "openai", "groq", "ai", "tensorflow", "pytorch",
]

# === SEARCH KEYWORDS (what you want to find) ===
SEARCH_KEYWORDS = [
    # AI/ML roles
    "AI engineer intern",
    "AI engineer",
    "machine learning intern",
    "machine learning engineer",
    "LLM engineer",
    "NLP engineer",
    "AI developer",
    "generative AI",
    "RAG",
    "prompt engineer",
    # Full Stack
    "full stack intern",
    "full stack developer",
    "full stack engineer",
    # Backend
    "backend intern",
    "backend developer",
    "backend engineer",
    "python developer",
    "fastapi",
    "node.js developer",
    # Web Development
    "web developer intern",
    "web developer",
    "react developer",
    "frontend intern",
    # General SWE
    "software engineer intern",
    "software developer intern",
    "junior software engineer",
]

# === ENTRY LEVEL TERMS ===
ENTRY_LEVEL_TERMS = [
    "intern", "internship", "junior", "jr", "entry level",
    "entry-level", "graduate", "trainee", "associate",
    "early career", "new grad", "fresher", "0-2 years",
    "0-3 years", "1-2 years", "no experience required",
]

# === EXCLUDE (senior roles you can't land yet) ===
EXCLUDE_TERMS = [
    "senior", "sr.", "sr ", "lead", "principal", "staff",
    "director", "manager", "head of", "vp ", "architect",
    "10+ years", "8+ years", "7+ years", "6+ years", "5+ years",
]

# === SCAM DETECTION (red flags) ===
SCAM_INDICATORS = [
    # Payment scams
    "pay to apply", "registration fee", "deposit required",
    "send money", "western union", "money order",
    "processing fee", "training fee",
    # Too good to be true
    "earn $5000 per day", "no experience needed $",
    "guaranteed income", "get rich", "unlimited earning",
    # Fake companies
    "work from home stuffing envelopes",
    "data entry $50/hr", "typing jobs",
    # Crypto scams disguised as jobs
    "crypto trading", "forex trading", "binary options",
    # MLM / network marketing
    "network marketing", "mlm", "multi-level",
    "be your own boss", "passive income opportunity",
]

# === STARTUP INDICATORS (these hire fast — YOUR best bet) ===
STARTUP_SIGNALS = [
    "yc", "y combinator", "seed", "series a", "series b",
    "startup", "early stage", "founding", "first hire",
    "small team", "fast-paced", "equity", "stock options",
    "growing team", "venture backed", "funded",
    "pre-seed", "techstars", "accelerator",
    "5-10 people", "10-50 people", "1-10 employees",
    "11-50 employees", "51-200 employees",
]

# === BIG COMPANIES TO SKIP (too competitive, won't respond) ===
SKIP_BIG_COMPANIES = [
    "google", "microsoft", "meta", "amazon", "apple", "nvidia",
    "tiktok", "bytedance", "salesforce", "adobe", "intel",
    "citadel", "jane street", "goldman sachs", "morgan stanley",
    "walmart", "cisco", "oracle", "ibm", "qualcomm",
]

# === WORK TYPE ===
WORK_TYPE = "remote"

# === TARGET (companies from these regions that hire remote globally) ===
TARGET_COUNTRIES = ["US", "UK", "Canada", "Germany", "Netherlands", "Australia", "EU", "Singapore"]

# === SALARY FILTERS ===
MIN_MONTHLY_USD = 250   # Minimum $250/month (approx INR 20,000)
MIN_HOURLY_USD = 10     # Minimum $10/hour
INCLUDE_HOURLY = True

# === OUTPUT ===
OUTPUT_FILE = "jobs_found.csv"
HISTORY_FILE = "seen_jobs.json"
LOG_FILE = "search_log.txt"
DASHBOARD_FILE = "dashboard.html"

# === SCHEDULE ===
SEARCH_INTERVAL_HOURS = 6

# === NOTIFICATIONS ===
ENABLE_DESKTOP_NOTIFICATIONS = True
OPEN_DASHBOARD_AFTER_SEARCH = True  # Auto-open dashboard in browser
EMAIL_ENABLED = False
EMAIL_TO = ""
EMAIL_FROM = ""
EMAIL_PASSWORD = ""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

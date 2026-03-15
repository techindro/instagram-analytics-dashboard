"""
config/settings.py
──────────────────
Central configuration loaded from .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ─── API Credentials ────────────────────────────────────────────────────────
ACCESS_TOKEN            = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
BUSINESS_ACCOUNT_ID     = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
FACEBOOK_APP_ID         = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET     = os.getenv("FACEBOOK_APP_SECRET", "")

# ─── API Config ─────────────────────────────────────────────────────────────
API_VERSION  = os.getenv("API_VERSION", "v19.0")
BASE_URL     = os.getenv("BASE_URL", "https://graph.facebook.com")
API_BASE     = f"{BASE_URL}/{API_VERSION}"

# ─── Directories ────────────────────────────────────────────────────────────
DATA_DIR      = BASE_DIR / os.getenv("DATA_DIR", "data")
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR   = BASE_DIR / os.getenv("REPORTS_DIR", "reports")

# Auto-create dirs
for d in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Plot Defaults ───────────────────────────────────────────────────────────
PLOT_THEME    = "plotly_dark"
BRAND_COLORS  = {
    "primary":   "#E1306C",
    "secondary": "#833AB4",
    "blue":      "#405DE6",
    "orange":    "#F77737",
    "yellow":    "#FCAF45",
    "green":     "#12B886",
}

INSTAGRAM_PALETTE = [
    "#405DE6", "#5851DB", "#833AB4",
    "#C13584", "#E1306C", "#FD1D1D",
    "#F56040", "#F77737", "#FCAF45",
]

# ─── Analysis Defaults ───────────────────────────────────────────────────────
DEFAULT_PERIOD  = 30    # days
MAX_POSTS       = 100   # posts to fetch
TOP_HASHTAGS    = 10    # top N hashtags to analyse

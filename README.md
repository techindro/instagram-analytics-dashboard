# 📊 Instagram Analytics Dashboard

A complete Python data analysis project for Instagram Business/Creator accounts using the **Instagram Graph API**.

Produces interactive charts, processed CSV exports, and a self-contained HTML report — all from a single command.

## ✨ Features

| Module | What it does |
|---|---|
| `src/api/instagram_client.py` | Full Instagram Graph API wrapper with retry, pagination, rate-limit handling |
| `src/analysis/data_processor.py` | Raw JSON → clean pandas DataFrames + computed KPIs |
| `src/analysis/engagement_analysis.py` | Deep-dive engagement stats, correlations, caption analysis |
| `src/visualization/charts.py` | 13 Plotly charts (growth, heatmaps, choropleth, bubble) |
| `src/visualization/report_generator.py` | Auto-generates a polished self-contained HTML report |
| `notebooks/Instagram_Analytics.ipynb` | Step-by-step Jupyter notebook (generated via `generate_notebook.py`) |
| `run_analysis.py` | One-command full pipeline CLI |
| `tests/` | pytest unit tests (no API calls needed) |

---

## 📁 Project Structure

```
instagram-analytics/
├── .env.example                  # Credentials template
├── .gitignore
├── requirements.txt
├── run_analysis.py               # ← Main entry point
├── generate_notebook.py          # Generates the .ipynb file
│
├── config/
│   ├── __init__.py
│   └── settings.py               # All config loaded from .env
│
├── src/
│   ├── api/
│   │   └── instagram_client.py   # Graph API client
│   ├── analysis/
│   │   ├── data_processor.py     # Raw → DataFrames
│   │   └── engagement_analysis.py
│   └── visualization/
│       ├── charts.py             # All Plotly figures
│       └── report_generator.py   # HTML report builder
│
├── notebooks/
│   └── Instagram_Analytics.ipynb # Interactive analysis notebook
│
├── data/
│   ├── raw/                      # API JSON responses (git-ignored)
│   └── processed/                # Clean CSVs (git-ignored)
│
├── reports/                      # HTML reports output (git-ignored)
│
└── tests/
    ├── test_data_processor.py
    └── test_engagement.py
```

---

## 🚀 Quick Start

### Step 1 — Clone & install

```bash
git clone https://github.com/your-username/instagram-analytics.git
cd instagram-analytics
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Set up credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_account_id
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

> **How to get credentials** → see [Credentials Guide](#-getting-api-credentials) below.

### Step 3 — Run the full pipeline

```bash
python run_analysis.py
```

Options:

```bash
python run_analysis.py --days 60        # Extend look-back to 60 days
python run_analysis.py --posts 100      # Fetch up to 100 posts
python run_analysis.py --skip-fetch     # Use cached data/raw/ (no API call)
python run_analysis.py --no-report      # Skip HTML report generation
```

### Step 4 — Open the Jupyter Notebook

```bash
python generate_notebook.py    # creates notebooks/Instagram_Analytics.ipynb
jupyter notebook notebooks/Instagram_Analytics.ipynb
```

---

## 🔑 Getting API Credentials

### 1. Create a Facebook Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com/apps/) → **Create App**
2. Choose **Business** type
3. Note your **App ID** and **App Secret**

### 2. Connect your Instagram Business / Creator Account

- Your Instagram account must be a **Business** or **Creator** account
- It must be linked to a **Facebook Page**

### 3. Generate a Long-Lived Access Token

```
https://www.facebook.com/dialog/oauth?
  client_id=YOUR_APP_ID
  &redirect_uri=https://localhost
  &scope=instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement
```

Exchange the short-lived token for a long-lived one (60 days):

```bash
curl "https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=APP_ID
  &client_secret=APP_SECRET
  &fb_exchange_token=SHORT_LIVED_TOKEN"
```

### 4. Find your Instagram Business Account ID

```bash
curl "https://graph.facebook.com/v19.0/me/accounts
  ?fields=instagram_business_account
  &access_token=YOUR_TOKEN"
```

Paste the returned `id` into `INSTAGRAM_BUSINESS_ACCOUNT_ID` in your `.env`.

---

## 📊 Charts & Analysis

### Follower Growth
- Cumulative followers over time (area chart)
- Daily gain bars (dual-axis)
- 7-day rolling average
- Best/worst growth days

### Engagement Analysis
- Per-post engagement rate scatter + rolling average
- Engagement by content type (IMAGE / REEL / CAROUSEL / STORY)
- Weekly stacked bar (likes + comments + saves + shares)
- Weekday × Hour heatmap (best posting times)
- Top 10 posts by engagement rate

### Audience Demographics
- Gender donut chart
- Age group distribution
- Top 10 cities bar chart
- Audience by country choropleth map

### Hashtag Strategy
- Bubble chart: IG volume vs our avg engagement (size = post count)
- Top hashtags by engagement bar chart
- Correlation: hashtag competition vs performance

### Bonus
- Caption length vs engagement rate
- Metric correlation matrix (Pearson)

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests use mock data — **no API calls or credentials needed**.

```
tests/test_data_processor.py   18 tests
tests/test_engagement.py       11 tests
```

---

## 📤 Output Files

| Path | Description |
|---|---|
| `data/raw/*.json` | Raw API responses |
| `data/processed/posts.csv` | Enriched posts with engagement metrics |
| `data/processed/follower_growth.csv` | Daily follower time-series |
| `data/processed/reach_impressions.csv` | Daily reach + impressions |
| `data/processed/hashtags.csv` | Hashtag performance table |
| `data/processed/best_times.csv` | Weekday × hour engagement heatmap |
| `reports/instagram_report_<user>_<ts>.html` | Self-contained interactive HTML report |

---

## ⚙️ Configuration

All settings are in `config/settings.py` and loaded from `.env`:

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_PERIOD` | `30` | Default look-back days |
| `MAX_POSTS` | `100` | Max posts to fetch |
| `TOP_HASHTAGS` | `10` | Top N hashtags to analyse |
| `PLOT_THEME` | `plotly_dark` | Plotly theme |
| `API_VERSION` | `v19.0` | Graph API version |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **requests** — HTTP client for Graph API
- **pandas / numpy** — Data processing
- **plotly** — Interactive charts
- **Jinja2** — HTML report templating
- **python-dotenv** — Environment variable management
- **pytest** — Unit testing
- **jupyter** — Interactive notebook

---

## 📌 Notes

- The Instagram Graph API only works with **Business** or **Creator** accounts.
- Insights data (reach, impressions, saves) requires the account to have **100+ followers**.
- Story insights are only available for **24 hours** after posting.
- Long-lived tokens expire after **60 days** — refresh them before running.
- Rate limits: ~200 calls/hour. The client automatically retries on rate-limit errors.

---

## 📄 License

MIT — free to use, modify and distribute.


"""
generate_notebook.py
────────────────────
Run this once to create the Instagram_Analytics.ipynb notebook file.
    python generate_notebook.py
"""

import json
from pathlib import Path

cells = []

def code(src, tags=None):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": tags or []},
        "outputs": [],
        "source": src if isinstance(src, list) else [src],
    })

def md(src):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": src if isinstance(src, list) else [src],
    })

# ── Cell 0: Title ─────────────────────────────────────────────────────────────
md("""# 📊 Instagram Analytics Dashboard
### Complete analysis using the Instagram Graph API
---
**What this notebook covers:**
- 🔐 API setup & authentication
- 📈 Follower growth analysis
- 💡 Engagement rate deep-dive
- 🎬 Content performance by type
- 👥 Audience demographics
- `#` Hashtag strategy analysis
- ⏰ Best posting time recommendations
- 📄 Automated HTML report export
""")

# ── Cell 1: Installs ──────────────────────────────────────────────────────────
md("## 0. Install Dependencies")
code("""# Run once to install all required packages
# !pip install -r requirements.txt
print("✓ All packages ready")
""")

# ── Cell 2: Imports ───────────────────────────────────────────────────────────
md("## 1. Imports & Configuration")
code("""import sys, json, warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, str(Path('.').resolve()))

import pandas as pd
import numpy as np
import plotly.io as pio
pio.renderers.default = "notebook"

from config.settings import (
    RAW_DIR, PROCESSED_DIR, REPORTS_DIR,
    ACCESS_TOKEN, BUSINESS_ACCOUNT_ID, BRAND_COLORS
)
from src.api.instagram_client import InstagramClient
from src.analysis.data_processor import DataProcessor
from src.analysis.engagement_analysis import EngagementAnalyzer
from src.visualization import charts as C
from src.visualization.report_generator import ReportGenerator

print(f"✓ Project root: {Path('.').resolve()}")
print(f"✓ Token configured: {'Yes ✅' if ACCESS_TOKEN else 'No ❌  — check .env'}")
print(f"✓ Account ID:   {'Yes ✅' if BUSINESS_ACCOUNT_ID else 'No ❌  — check .env'}")
""")

# ── Cell 3: Auth check ────────────────────────────────────────────────────────
md("""## 2. Authenticate & Fetch Data
> **Setup:** copy `.env.example` → `.env` and fill in your credentials.
> See README for step-by-step instructions.
""")
code("""# Initialise the API client
client = InstagramClient()

# Verify connection
profile = client.get_profile()
print(f"\\n✅ Connected as @{profile['username']}")
print(f"   Followers : {profile['followers_count']:,}")
print(f"   Following : {profile['follows_count']:,}")
print(f"   Posts     : {profile['media_count']:,}")
""")

# ── Cell 4: Fetch all data ────────────────────────────────────────────────────
code("""# Fetch everything (this may take 1-2 minutes due to per-post insights)
DAYS       = 30   # <-- change look-back window
POST_LIMIT = 50   # <-- change number of posts

raw = client.fetch_all(days=DAYS, post_limit=POST_LIMIT)
print("\\n📦 Data fetched:")
for k, v in raw.items():
    n = len(v) if isinstance(v, (list, dict)) else "—"
    print(f"  {k:30s} {n} records")
""")

# ── Cell 5: Process ───────────────────────────────────────────────────────────
md("## 3. Process Raw Data → DataFrames")
code("""dp = DataProcessor()

posts_df      = dp.process_posts(raw['posts'])
follower_df   = dp.process_follower_growth(raw['follower_growth'])
reach_df      = dp.process_reach_impressions(raw['reach_impressions'])
audience      = dp.process_audience_demographics(raw['audience_demographics'])
hashtag_df    = dp.process_hashtags(raw['hashtag_analysis'])
best_times_df = dp.compute_best_times(posts_df)
summary       = dp.compute_summary(raw['profile'], posts_df, follower_df)

print(f"✓ Posts DataFrame       : {posts_df.shape}")
print(f"✓ Follower Growth       : {follower_df.shape}")
print(f"✓ Reach/Impressions     : {reach_df.shape}")
print(f"✓ Audience keys         : {list(audience.keys())}")
print(f"✓ Hashtags              : {hashtag_df.shape}")
print(f"✓ Best Times            : {best_times_df.shape}")
""")

# ── Cell 6: Preview ───────────────────────────────────────────────────────────
code("""# Preview the posts DataFrame
posts_df[['timestamp','media_type','like_count','comments_count',
          'reach','engagement_rate']].head(10)
""")

# ── Cell 7: Summary KPIs ─────────────────────────────────────────────────────
md("## 4. Summary KPIs")
code("""print("=" * 45)
print(f"  INSTAGRAM ANALYTICS SUMMARY")
print("=" * 45)
for k, v in summary.items():
    if k == 'best_post': continue
    print(f"  {k:35s} {v}")
print("=" * 45)
""")

# ── Cell 8: Follower Growth ───────────────────────────────────────────────────
md("## 5. Follower Growth Analysis")
code("""fig = C.follower_growth_chart(follower_df)
fig.show()
""")

code("""# Key stats
latest = follower_df.iloc[-1]
thirty_day_gain = follower_df['daily_gain'].tail(30).sum()
avg_daily = follower_df['daily_gain'].tail(30).mean()

print(f"Current followers : {latest['followers']:,}")
print(f"30-day gain       : +{thirty_day_gain:,}")
print(f"Avg daily gain    : +{avg_daily:.0f}")
print(f"Best single day   : +{follower_df['daily_gain'].max():,} on {follower_df.loc[follower_df['daily_gain'].idxmax(), 'date']}")
""")

# ── Cell 9: Reach & Impressions ───────────────────────────────────────────────
md("## 6. Reach & Impressions")
code("""fig = C.reach_impressions_chart(reach_df)
fig.show()
""")

code("""if 'reach' in reach_df and 'impressions' in reach_df:
    print(f"Total reach (30d)       : {reach_df['reach'].sum():,}")
    print(f"Total impressions (30d) : {reach_df['impressions'].sum():,}")
    print(f"Avg frequency           : {reach_df['freq'].mean():.2f}x")
""")

# ── Cell 10: Engagement ───────────────────────────────────────────────────────
md("## 7. Engagement Rate Analysis")
code("""ea = EngagementAnalyzer(posts_df)
kpis = ea.overall_kpis()

for k, v in kpis.items():
    print(f"  {k:35s} {v:,}" if isinstance(v, int) else f"  {k:35s} {v}")
""")

code("""fig = C.engagement_trend_chart(posts_df)
fig.show()
""")

code("""# Engagement by weekday
by_day = ea.by_weekday()
print("Engagement by day of week:")
print(by_day.to_string(index=False))
""")

code("""fig = C.best_times_heatmap(best_times_df)
fig.show()
""")

# ── Cell 11: Content Type ─────────────────────────────────────────────────────
md("## 8. Content Performance by Type")
code("""by_type = ea.by_content_type()
print(by_type.to_string(index=False))
""")

code("""fig = C.content_type_chart(by_type)
fig.show()
""")

code("""fig = C.engagement_mix_chart(posts_df)
fig.show()
""")

code("""# Top 10 posts
top10 = ea.top_posts(n=10)
fig = C.top_posts_chart(top10)
fig.show()
""")

# ── Cell 12: Audience ─────────────────────────────────────────────────────────
md("## 9. Audience Demographics")
code("""fig = C.gender_pie_chart(audience.get('gender', pd.DataFrame()))
fig.show()
""")

code("""fig = C.age_distribution_chart(audience.get('age', pd.DataFrame()))
fig.show()
""")

code("""fig = C.top_cities_chart(audience.get('city', pd.DataFrame()))
fig.show()
""")

code("""fig = C.country_map_chart(audience.get('country', pd.DataFrame()))
fig.show()
""")

# ── Cell 13: Hashtags ─────────────────────────────────────────────────────────
md("## 10. Hashtag Strategy Analysis")
code("""print(hashtag_df[['hashtag','our_post_count','avg_engagement',
               'ig_media_count']].head(15).to_string(index=False))
""")

code("""fig = C.hashtag_bubble_chart(hashtag_df)
fig.show()
""")

code("""fig = C.hashtag_bar_chart(hashtag_df)
fig.show()
""")

# ── Cell 14: Caption analysis ─────────────────────────────────────────────────
md("## 11. Caption Length vs Engagement")
code("""cap_analysis = ea.caption_length_analysis()
print(cap_analysis.to_string(index=False))
""")

# ── Cell 15: Correlation ──────────────────────────────────────────────────────
md("## 12. Metric Correlation Matrix")
code("""import plotly.express as px
corr = ea.correlation_matrix()
if corr is not None:
    fig = px.imshow(
        corr,
        color_continuous_scale=[[0,'#405DE6'],[0.5,'#16162a'],[1,'#E1306C']],
        text_auto='.2f', title='Metric Correlations',
        template='plotly_dark',
    )
    fig.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='DM Sans'))
    fig.show()
""")

# ── Cell 16: Save CSVs ────────────────────────────────────────────────────────
md("## 13. Save Processed Data to CSV")
code("""saved = []
for name, df in {
    'posts':            posts_df,
    'follower_growth':  follower_df,
    'reach_impressions':reach_df,
    'hashtags':         hashtag_df,
    'best_times':       best_times_df,
}.items():
    if not df.empty:
        path = dp.save_processed(df, name, PROCESSED_DIR)
        saved.append(str(path))

print("Saved CSVs:")
for p in saved:
    print(f"  {p}")
""")

# ── Cell 17: HTML Report ──────────────────────────────────────────────────────
md("## 14. Export HTML Report")
code("""charts = {
    'follower_growth':   C.follower_growth_chart(follower_df)    if not follower_df.empty else None,
    'reach_impressions': C.reach_impressions_chart(reach_df)     if not reach_df.empty    else None,
    'engagement_trend':  C.engagement_trend_chart(posts_df)      if not posts_df.empty    else None,
    'content_type':      C.content_type_chart(by_type)           if not by_type.empty     else None,
    'top_posts':         C.top_posts_chart(top10)                if not top10.empty       else None,
    'engagement_mix':    C.engagement_mix_chart(posts_df)        if not posts_df.empty    else None,
    'gender_pie':        C.gender_pie_chart(audience.get('gender', pd.DataFrame())),
    'age_dist':          C.age_distribution_chart(audience.get('age', pd.DataFrame())),
    'top_cities':        C.top_cities_chart(audience.get('city', pd.DataFrame())),
    'country_map':       C.country_map_chart(audience.get('country', pd.DataFrame())),
    'hashtag_bubble':    C.hashtag_bubble_chart(hashtag_df)      if not hashtag_df.empty  else None,
    'hashtag_bar':       C.hashtag_bar_chart(hashtag_df)         if not hashtag_df.empty  else None,
    'best_times':        C.best_times_heatmap(best_times_df)     if not best_times_df.empty else None,
}

username = raw['profile'].get('username', 'account')
rg   = ReportGenerator(summary, charts, REPORTS_DIR, username)
path = rg.build()
print(f"\\n✅ Report exported → {path}")
print("   Open in your browser to view the full interactive dashboard!")
""")

md("""---
## ✅ Analysis Complete!

Your report is in the `reports/` directory. Open it in any browser for the full interactive dashboard.

**Next steps:**
- Schedule `run_analysis.py` via cron for automated weekly reports
- Extend `InstagramClient.get_posts()` to pull older data
- Add competitor benchmarking by tracking public hashtag metrics
""")

# ── Write notebook ────────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": cells,
}

out = Path("notebooks/Instagram_Analytics.ipynb")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"✓ Notebook written → {out}")

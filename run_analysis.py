"""
run_analysis.py
───────────────
Main entry point.

Usage
-----
    python run_analysis.py                   # full run (fetch + analyse + report)
    python run_analysis.py --skip-fetch      # use cached raw data
    python run_analysis.py --days 60         # change look-back window
    python run_analysis.py --posts 100       # fetch more posts
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# ── project imports ──────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    RAW_DIR, PROCESSED_DIR, REPORTS_DIR, ACCESS_TOKEN, BUSINESS_ACCOUNT_ID
)
from src.api.instagram_client import InstagramClient, InstagramAPIError
from src.analysis.data_processor import DataProcessor
from src.analysis.engagement_analysis import EngagementAnalyzer
from src.visualization.charts import (
    follower_growth_chart, reach_impressions_chart,
    engagement_trend_chart, content_type_chart,
    top_posts_chart, gender_pie_chart, age_distribution_chart,
    top_cities_chart, country_map_chart,
    hashtag_bubble_chart, hashtag_bar_chart,
    best_times_heatmap, engagement_mix_chart,
)
from src.visualization.report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────

def load_raw_or_fetch(client: InstagramClient, days: int, post_limit: int,
                      skip_fetch: bool) -> dict:
    """Either load cached raw JSON or call the API."""
    if skip_fetch:
        logger.info("--skip-fetch: loading from data/raw/")
        dp = DataProcessor()
        return {
            "profile":               dp.load_raw_json(RAW_DIR / "profile.json"),
            "posts":                 dp.load_raw_json(RAW_DIR / "posts.json"),
            "follower_growth":       dp.load_raw_json(RAW_DIR / "account_insights.json").get("follower_count", []),
            "reach_impressions":     dp.load_raw_json(RAW_DIR / "account_insights.json"),
            "profile_activity":      {},
            "audience_demographics": dp.load_raw_json(RAW_DIR / "audience_demographics.json"),
            "hashtag_analysis":      dp.load_raw_json(RAW_DIR / "hashtag_analysis.json"),
        }
    return client.fetch_all(days=days, post_limit=post_limit)


def main():
    parser = argparse.ArgumentParser(description="Instagram Analytics Pipeline")
    parser.add_argument("--days",         type=int, default=30,  help="Look-back window in days")
    parser.add_argument("--posts",        type=int, default=50,  help="Number of posts to fetch")
    parser.add_argument("--skip-fetch",   action="store_true",   help="Use cached raw data")
    parser.add_argument("--no-report",    action="store_true",   help="Skip HTML report generation")
    args = parser.parse_args()

    # ── 1. Validate credentials ───────────────────────────────────────
    if not ACCESS_TOKEN or not BUSINESS_ACCOUNT_ID:
        logger.error(
            "Missing credentials. Copy .env.example → .env and add your tokens.\n"
            "See README.md → Quick Start for instructions."
        )
        sys.exit(1)

    # ── 2. Fetch data ─────────────────────────────────────────────────
    logger.info("═══ Instagram Analytics Pipeline ═══")
    client = InstagramClient()
    raw    = load_raw_or_fetch(client, args.days, args.posts, args.skip_fetch)

    # ── 3. Process data ───────────────────────────────────────────────
    dp = DataProcessor()

    posts_df      = dp.process_posts(raw.get("posts", []))
    follower_df   = dp.process_follower_growth(raw.get("follower_growth", []))
    reach_df      = dp.process_reach_impressions(raw.get("reach_impressions", {}))
    audience      = dp.process_audience_demographics(raw.get("audience_demographics", {}))
    hashtag_df    = dp.process_hashtags(raw.get("hashtag_analysis", []))
    best_times_df = dp.compute_best_times(posts_df)
    summary       = dp.compute_summary(raw.get("profile", {}), posts_df, follower_df)

    # Save processed CSVs
    for name, df in {
        "posts":           posts_df,
        "follower_growth": follower_df,
        "reach_impressions": reach_df,
        "hashtags":        hashtag_df,
        "best_times":      best_times_df,
    }.items():
        if not df.empty:
            dp.save_processed(df, name, PROCESSED_DIR)

    # ── 4. Engagement analysis ────────────────────────────────────────
    if not posts_df.empty:
        ea       = EngagementAnalyzer(posts_df)
        eng_data = ea.full_report()
        logger.info(f"Overall KPIs: {json.dumps(eng_data['kpis'], indent=2)}")
    else:
        eng_data = {}

    # ── 5. Build charts ───────────────────────────────────────────────
    by_type_df  = eng_data.get("by_content_type", __import__("pandas").DataFrame())
    top_df      = eng_data.get("top_posts",        __import__("pandas").DataFrame())

    charts = {
        "follower_growth":  follower_growth_chart(follower_df)    if not follower_df.empty  else None,
        "reach_impressions":reach_impressions_chart(reach_df)     if not reach_df.empty     else None,
        "engagement_trend": engagement_trend_chart(posts_df)      if not posts_df.empty     else None,
        "content_type":     content_type_chart(by_type_df)        if not by_type_df.empty   else None,
        "top_posts":        top_posts_chart(top_df)               if not top_df.empty       else None,
        "engagement_mix":   engagement_mix_chart(posts_df)        if not posts_df.empty     else None,
        "gender_pie":       gender_pie_chart(audience.get("gender", __import__("pandas").DataFrame())),
        "age_dist":         age_distribution_chart(audience.get("age", __import__("pandas").DataFrame())),
        "top_cities":       top_cities_chart(audience.get("city", __import__("pandas").DataFrame())),
        "country_map":      country_map_chart(audience.get("country", __import__("pandas").DataFrame())),
        "hashtag_bubble":   hashtag_bubble_chart(hashtag_df)      if not hashtag_df.empty   else None,
        "hashtag_bar":      hashtag_bar_chart(hashtag_df)         if not hashtag_df.empty   else None,
        "best_times":       best_times_heatmap(best_times_df)     if not best_times_df.empty else None,
    }

    # ── 6. HTML report ────────────────────────────────────────────────
    if not args.no_report:
        username = raw.get("profile", {}).get("username", "account")
        rg   = ReportGenerator(summary, charts, REPORTS_DIR, username)
        path = rg.build()
        logger.info(f"\n✅ Report ready → open in browser:\n   {path}\n")
    else:
        logger.info("--no-report: skipping HTML generation")

    logger.info("═══ Pipeline complete ═══")
    return summary, charts


if __name__ == "__main__":
    main()

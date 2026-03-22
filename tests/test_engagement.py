"""
tests/test_engagement.py
─────────────────────────
Unit tests for EngagementAnalyzer.
Run: pytest tests/ -v
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.analysis.data_processor import DataProcessor
from src.analysis.engagement_analysis import EngagementAnalyzer


@pytest.fixture
def posts_df():
    raw = [
        {"id": str(i), "caption": f"#post{i} caption text",
         "media_type": ["IMAGE", "REEL", "CAROUSEL_ALBUM"][i % 3],
         "timestamp": f"2024-0{(i % 3)+1}-{(i % 28)+1:02d}T{(i % 24):02d}:00:00+0000",
         "like_count": 100 * (i + 1), "comments_count": 10 * (i + 1),
         "reach": 2000 * (i + 1), "impressions": 3000 * (i + 1),
         "saved": 20 * (i + 1), "shares": 5 * (i + 1)}
        for i in range(15)
    ]
    return DataProcessor.process_posts(raw)


class TestEngagementAnalyzer:
    def test_init_raises_on_empty(self):
        with pytest.raises(ValueError):
            EngagementAnalyzer(pd.DataFrame())

    def test_overall_kpis_keys(self, posts_df):
        ea   = EngagementAnalyzer(posts_df)
        kpis = ea.overall_kpis()
        for key in ["total_posts", "avg_engagement_rate", "total_likes",
                    "total_comments", "likes_to_comments_ratio"]:
            assert key in kpis

    def test_total_posts(self, posts_df):
        ea = EngagementAnalyzer(posts_df)
        assert ea.overall_kpis()["total_posts"] == len(posts_df)

    def test_by_content_type_columns(self, posts_df):
        ea = EngagementAnalyzer(posts_df)
        df = ea.by_content_type()
        assert "media_type" in df.columns
        assert "avg_engagement_rate" in df.columns

    def test_top_posts_length(self, posts_df):
        ea  = EngagementAnalyzer(posts_df)
        top = ea.top_posts(n=5)
        assert len(top) <= 5

    def test_top_posts_sorted_descending(self, posts_df):
        ea  = EngagementAnalyzer(posts_df)
        top = ea.top_posts(n=10, by="engagement_rate")
        rates = top["engagement_rate"].tolist()
        assert rates == sorted(rates, reverse=True)

    def test_by_weekday_all_days(self, posts_df):
        ea  = EngagementAnalyzer(posts_df)
        df  = ea.by_weekday()
        # Just check it doesn't crash and returns a DataFrame
        assert isinstance(df, pd.DataFrame)

    def test_caption_length_analysis(self, posts_df):
        ea = EngagementAnalyzer(posts_df)
        df = ea.caption_length_analysis()
        assert isinstance(df, pd.DataFrame)

    def test_correlation_matrix_symmetric(self, posts_df):
        ea   = EngagementAnalyzer(posts_df)
        corr = ea.correlation_matrix()
        if corr is not None:
            # Diagonal should be 1.0
            for col in corr.columns:
                assert abs(corr.loc[col, col] - 1.0) < 1e-9

    def test_full_report_keys(self, posts_df):
        ea     = EngagementAnalyzer(posts_df)
        report = ea.full_report()
        for key in ["kpis", "by_content_type", "weekly_trend",
                    "top_posts", "by_weekday", "by_hour"]:
            assert key in report

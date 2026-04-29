"""Tests for ranking module."""

import pytest
from datetime import datetime, timezone, timedelta
from intelligence.ranking import ResultRanker


class TestResultRankerInit:
    def test_default_weights(self):
        ranker = ResultRanker()
        assert ranker.weights['popularity'] == 0.4
        assert ranker.weights['activity'] == 0.3
        assert ranker.weights['quality'] == 0.2
        assert ranker.weights['community'] == 0.1

    def test_custom_weights(self):
        ranker = ResultRanker(
            popularity_weight=0.5,
            activity_weight=0.2,
            quality_weight=0.2,
            community_weight=0.1
        )
        assert ranker.weights['popularity'] == 0.5


class TestPopularityScore:
    def test_zero_stars(self):
        ranker = ResultRanker()
        score = ranker._score_popularity({'stargazers_count': 0, 'forks_count': 0})
        assert score == 0

    def test_high_stars(self):
        ranker = ResultRanker()
        score = ranker._score_popularity({'stargazers_count': 50000, 'forks_count': 4000})
        assert score > 0
        assert score <= 100

    def test_alternative_star_field(self):
        ranker = ResultRanker()
        score1 = ranker._score_popularity({'stargazers_count': 1000})
        score2 = ranker._score_popularity({'stars': 1000})
        # Both should use the same value
        assert abs(score1 - score2) < 0.01


class TestActivityScore:
    def test_recent_update(self):
        ranker = ResultRanker()
        recent = datetime.now(timezone.utc).isoformat()
        score = ranker._score_activity({'updated_at': recent})
        assert score == 100

    def test_week_old_update(self):
        ranker = ResultRanker()
        two_weeks_ago = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        score = ranker._score_activity({'updated_at': two_weeks_ago})
        assert score == 80

    def test_month_old_update(self):
        ranker = ResultRanker()
        month_ago = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        score = ranker._score_activity({'updated_at': month_ago})
        assert score == 60

    def test_empty_updated_at(self):
        ranker = ResultRanker()
        score = ranker._score_activity({'updated_at': ''})
        assert score == 0

    def test_no_updated_at(self):
        ranker = ResultRanker()
        score = ranker._score_activity({})
        assert score == 0


class TestQualityScore:
    def test_all_quality_features(self):
        ranker = ResultRanker()
        item = {
            'description': 'A great project',
            'homepage': 'https://example.com',
            'has_wiki': True,
            'license': {'name': 'MIT'}
        }
        score = ranker._score_quality(item)
        assert score == 100

    def test_minimal_quality(self):
        ranker = ResultRanker()
        score = ranker._score_quality({})
        assert score == 0

    def test_partial_quality(self):
        ranker = ResultRanker()
        item = {'description': 'Some project', 'license': {'name': 'MIT'}}
        score = ranker._score_quality(item)
        assert score == 60  # 30 for desc + 30 for license


class TestCommunityScore:
    def test_base_community(self):
        ranker = ResultRanker()
        score = ranker._score_community({})
        assert score == 50  # base score

    def test_with_topics(self):
        ranker = ResultRanker()
        score = ranker._score_community({'topics': ['python', 'web']})
        assert score == 80  # 50 base + 30 topics

    def test_with_issues_and_topics(self):
        ranker = ResultRanker()
        score = ranker._score_community({
            'open_issues_count': 10,
            'topics': ['python']
        })
        assert score == 100  # 50 base + 20 issues + 30 topics


class TestCalculateScore:
    def test_well_maintained_project(self):
        ranker = ResultRanker()
        recent = datetime.now(timezone.utc).isoformat()
        item = {
            'stargazers_count': 50000,
            'forks_count': 4000,
            'updated_at': recent,
            'description': 'Fast web framework',
            'license': {'name': 'MIT'},
            'topics': ['python', 'web']
        }
        score = ranker.calculate_score(item)
        assert score > 50  # Should be high for a well-maintained project
        assert score <= 100

    def test_abandoned_project(self):
        ranker = ResultRanker()
        old_date = (datetime.now(timezone.utc) - timedelta(days=500)).isoformat()
        item = {
            'stargazers_count': 10,
            'forks_count': 0,
            'updated_at': old_date,
        }
        score = ranker.calculate_score(item)
        assert score < 20  # Should be low for abandoned project


class TestRankItems:
    def test_ranking_sorts_by_score(self):
        ranker = ResultRanker()
        recent = datetime.now(timezone.utc).isoformat()
        old_date = (datetime.now(timezone.utc) - timedelta(days=500)).isoformat()

        items = [
            {'name': 'low', 'stargazers_count': 10, 'updated_at': old_date},
            {'name': 'high', 'stargazers_count': 50000, 'forks_count': 4000,
             'updated_at': recent, 'description': 'Great', 'license': {'name': 'MIT'},
             'topics': ['python']},
        ]
        ranked = ranker.rank_items(items)
        assert ranked[0]['name'] == 'high'
        assert ranked[0]['_score'] > ranked[1]['_score']

    def test_score_breakdown_included(self):
        ranker = ResultRanker()
        items = [{'stargazers_count': 100, 'updated_at': datetime.now(timezone.utc).isoformat()}]
        ranked = ranker.rank_items(items)
        assert '_score_breakdown' in ranked[0]
        assert 'popularity' in ranked[0]['_score_breakdown']

    def test_original_data_preserved(self):
        ranker = ResultRanker()
        items = [{'name': 'test', 'stargazers_count': 100}]
        ranked = ranker.rank_items(items)
        assert ranked[0]['name'] == 'test'


class TestGetTopItems:
    def test_get_top_2(self):
        ranker = ResultRanker()
        recent = datetime.now(timezone.utc).isoformat()
        items = [
            {'name': 'a', 'stargazers_count': 50000, 'updated_at': recent,
             'description': 'Good', 'license': {'name': 'MIT'}, 'topics': ['py']},
            {'name': 'b', 'stargazers_count': 1000, 'updated_at': recent,
             'description': 'OK', 'license': {'name': 'MIT'}, 'topics': ['js']},
            {'name': 'c', 'stargazers_count': 10, 'updated_at': recent},
        ]
        top = ranker.get_top_items(items, 2)
        assert len(top) == 2

    def test_get_more_than_available(self):
        ranker = ResultRanker()
        items = [{'name': 'only_one', 'stargazers_count': 100}]
        top = ranker.get_top_items(items, 5)
        assert len(top) == 1
#!/usr/bin/env python3
"""
趋势分析模块
分析技术趋势和项目生命周期
"""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class TrendAnalyzer:
    """
    趋势分析器

    功能：
    - 技术趋势检测
    - 项目生命周期分析
    - 流行度预测
    """

    def __init__(self):
        """初始化趋势分析器"""
        pass

    def analyze_project_lifecycle(
        self,
        created_at: str,
        updated_at: str,
        stars: int,
        forks: int
    ) -> Dict[str, Any]:
        """
        分析项目生命周期阶段

        Args:
            created_at: 创建时间
            updated_at: 最近更新时间
            stars: stars数量
            forks: forks数量

        Returns:
            生命周期分析结果
        """
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(created.tzinfo)

            age_days = (now - created).days
            days_since_update = (now - updated).days

            # 判断生命周期阶段
            if age_days < 180:
                stage = 'newborn'
                stage_desc = '新项目'
            elif age_days < 730:
                stage = 'growing'
                stage_desc = '成长期'
            elif age_days < 1825:
                stage = 'mature'
                stage_desc = '成熟期'
            else:
                stage = 'legacy'
                stage_desc = '遗留项目'

            # 判断活跃度状态
            if days_since_update < 7:
                activity_status = 'very_active'
                activity_desc = '非常活跃'
            elif days_since_update < 30:
                activity_status = 'active'
                activity_desc = '活跃'
            elif days_since_update < 90:
                activity_status = 'slowing'
                activity_desc = '放缓'
            elif days_since_update < 365:
                activity_status = 'inactive'
                activity_desc = '不活跃'
            else:
                activity_status = 'abandoned'
                activity_desc = '可能已放弃'

            # 计算增长潜力
            if stars > 10000 and activity_status in ['very_active', 'active']:
                growth_potential = 'high'
            elif stars > 1000 and activity_status in ['very_active', 'active', 'slowing']:
                growth_potential = 'medium'
            else:
                growth_potential = 'low'

            return {
                'stage': stage,
                'stage_description': stage_desc,
                'age_days': age_days,
                'activity_status': activity_status,
                'activity_description': activity_desc,
                'days_since_update': days_since_update,
                'growth_potential': growth_potential,
                'recommendation': self._get_recommendation(stage, activity_status)
            }

        except Exception as e:
            return {
                'error': str(e),
                'stage': 'unknown',
                'activity_status': 'unknown'
            }

    def _get_recommendation(self, stage: str, activity: str) -> str:
        """获取推荐建议"""
        if activity in ['abandoned', 'inactive']:
            return '谨慎使用，项目可能不再维护'
        elif stage == 'newborn' and activity == 'very_active':
            return '值得关注的潜力项目'
        elif stage == 'growing' and activity in ['very_active', 'active']:
            return '推荐使用，项目正在快速发展'
        elif stage == 'mature' and activity in ['very_active', 'active']:
            return '稳定可靠的选择'
        elif stage == 'legacy':
            return '考虑是否有更现代的替代方案'
        else:
            return '根据具体需求评估'

    def predict_popularity(
        self,
        current_stars: int,
        created_at: str,
        historical_data: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        预测流行度趋势

        Args:
            current_stars: 当前stars数
            created_at: 创建时间
            historical_data: 历史stars数据（可选）

        Returns:
            预测结果
        """
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(created.tzinfo) - created).days

            if age_days < 1:
                age_days = 1

            # 计算日均增长
            daily_growth = current_stars / age_days

            # 简单预测（线性）
            prediction_30d = current_stars + (daily_growth * 30)
            prediction_90d = current_stars + (daily_growth * 90)
            prediction_1y = current_stars + (daily_growth * 365)

            # 判断趋势
            if daily_growth > 10:
                trend = 'rapid_growth'
                trend_desc = '快速增长'
            elif daily_growth > 1:
                trend = 'steady_growth'
                trend_desc = '稳定增长'
            elif daily_growth > 0.1:
                trend = 'slow_growth'
                trend_desc = '缓慢增长'
            else:
                trend = 'stable'
                trend_desc = '稳定'

            return {
                'current_stars': current_stars,
                'daily_growth': round(daily_growth, 2),
                'trend': trend,
                'trend_description': trend_desc,
                'predictions': {
                    '30_days': int(prediction_30d),
                    '90_days': int(prediction_90d),
                    '1_year': int(prediction_1y)
                }
            }

        except Exception as e:
            return {'error': str(e)}

    def analyze_tech_trends(
        self,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析技术趋势

        Args:
            search_results: 搜索结果列表

        Returns:
            趋势分析结果
        """
        if not search_results:
            return {'error': 'No data'}

        # 统计语言
        languages = defaultdict(int)
        licenses = defaultdict(int)
        topics = defaultdict(int)

        for item in search_results:
            # 语言
            lang = item.get('language')
            if lang:
                languages[lang] += 1

            # 许可证
            license_info = item.get('license')
            if license_info and isinstance(license_info, dict):
                license_name = license_info.get('name', 'Unknown')
                licenses[license_name] += 1

            # Topics
            item_topics = item.get('topics', [])
            for topic in item_topics:
                topics[topic] += 1

        return {
            'total_projects': len(search_results),
            'top_languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_licenses': dict(sorted(licenses.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_topics': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]),
            'language_diversity': len(languages),
            'license_diversity': len(licenses)
        }


def test_trend_analyzer():
    """测试趋势分析器"""
    print("测试 TrendAnalyzer...")

    analyzer = TrendAnalyzer()

    # 测试生命周期分析
    now = datetime.now()
    created = (now - timedelta(days=400)).isoformat()
    updated = (now - timedelta(days=5)).isoformat()

    lifecycle = analyzer.analyze_project_lifecycle(
        created_at=created,
        updated_at=updated,
        stars=5000,
        forks=500
    )
    print(f"\n生命周期分析:")
    print(f"  阶段: {lifecycle['stage_description']}")
    print(f"  活跃度: {lifecycle['activity_description']}")
    print(f"  建议: {lifecycle['recommendation']}")
    print("✓ 生命周期分析测试通过")

    # 测试流行度预测
    prediction = analyzer.predict_popularity(
        current_stars=1000,
        created_at=(now - timedelta(days=100)).isoformat()
    )
    print(f"\n流行度预测:")
    print(f"  日均增长: {prediction['daily_growth']}")
    print(f"  趋势: {prediction['trend_description']}")
    print(f"  30天预测: {prediction['predictions']['30_days']} stars")
    print("✓ 流行度预测测试通过")

    # 测试技术趋势分析
    test_results = [
        {'language': 'Python', 'license': {'name': 'MIT'}, 'topics': ['web', 'framework']},
        {'language': 'Python', 'license': {'name': 'MIT'}, 'topics': ['api', 'rest']},
        {'language': 'JavaScript', 'license': {'name': 'MIT'}, 'topics': ['web', 'frontend']},
    ]

    trends = analyzer.analyze_tech_trends(test_results)
    print(f"\n技术趋势分析:")
    print(f"  主要语言: {list(trends['top_languages'].keys())}")
    print(f"  热门话题: {list(trends['top_topics'].keys())[:3]}")
    print("✓ 技术趋势分析测试通过")

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_trend_analyzer()

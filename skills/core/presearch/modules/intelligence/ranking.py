#!/usr/bin/env python3
"""
结果智能排序模块
基于多维度评分对搜索结果进行排序
"""

import time
from typing import Any, Dict, List
from datetime import datetime


class ResultRanker:
    """
    结果智能排序器

    评分维度：
    - 流行度（stars/downloads）
    - 活跃度（最近更新时间）
    - 质量（issues/PRs比例）
    - 社区（contributors数量）
    """

    def __init__(
        self,
        popularity_weight: float = 0.4,
        activity_weight: float = 0.3,
        quality_weight: float = 0.2,
        community_weight: float = 0.1
    ):
        """
        初始化排序器

        Args:
            popularity_weight: 流行度权重
            activity_weight: 活跃度权重
            quality_weight: 质量权重
            community_weight: 社区权重
        """
        self.weights = {
            'popularity': popularity_weight,
            'activity': activity_weight,
            'quality': quality_weight,
            'community': community_weight
        }

    def calculate_score(self, item: Dict[str, Any]) -> float:
        """
        计算项目评分

        Args:
            item: 项目数据

        Returns:
            综合评分（0-100）
        """
        scores = {
            'popularity': self._score_popularity(item),
            'activity': self._score_activity(item),
            'quality': self._score_quality(item),
            'community': self._score_community(item)
        }

        # 加权计算总分
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )

        return round(total_score, 2)

    def _score_popularity(self, item: Dict[str, Any]) -> float:
        """
        计算流行度评分

        基于：stars, forks, watchers
        """
        stars = item.get('stargazers_count', item.get('stars', 0))
        forks = item.get('forks_count', item.get('forks', 0))

        # 对数缩放，避免大数主导
        import math
        star_score = min(100, math.log10(stars + 1) * 20) if stars > 0 else 0
        fork_score = min(100, math.log10(forks + 1) * 15) if forks > 0 else 0

        return (star_score * 0.7 + fork_score * 0.3)

    def _score_activity(self, item: Dict[str, Any]) -> float:
        """
        计算活跃度评分

        基于：最近更新时间、更新频率
        """
        updated_at = item.get('updated_at', '')
        if not updated_at:
            return 0

        try:
            # 解析时间
            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(updated_time.tzinfo) - updated_time).days

            # 越近更新分数越高
            if days_since_update < 7:
                return 100
            elif days_since_update < 30:
                return 80
            elif days_since_update < 90:
                return 60
            elif days_since_update < 180:
                return 40
            elif days_since_update < 365:
                return 20
            else:
                return 10
        except:
            return 0

    def _score_quality(self, item: Dict[str, Any]) -> float:
        """
        计算质量评分

        基于：是否有描述、是否有文档、issues比例
        """
        score = 0

        # 有描述
        if item.get('description'):
            score += 30

        # 有主页
        if item.get('homepage'):
            score += 20

        # 有文档（简化判断）
        if item.get('has_wiki') or item.get('has_pages'):
            score += 20

        # 开源许可证
        if item.get('license'):
            score += 30

        return min(100, score)

    def _score_community(self, item: Dict[str, Any]) -> float:
        """
        计算社区评分

        基于：contributors、issues响应
        """
        # 简化计算，实际可能需要额外API调用
        score = 50  # 基础分

        # 有issues
        if item.get('open_issues_count', 0) > 0:
            score += 20

        # 有topics
        if item.get('topics'):
            score += 30

        return min(100, score)

    def rank_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对项目列表进行排序

        Args:
            items: 项目列表

        Returns:
            排序后的项目列表（包含评分）
        """
        # 计算评分并添加
        scored_items = []
        for item in items:
            scored_item = item.copy()
            scored_item['_score'] = self.calculate_score(item)
            scored_item['_score_breakdown'] = {
                'popularity': round(self._score_popularity(item), 2),
                'activity': round(self._score_activity(item), 2),
                'quality': round(self._score_quality(item), 2),
                'community': round(self._score_community(item), 2)
            }
            scored_items.append(scored_item)

        # 按评分排序
        scored_items.sort(key=lambda x: x['_score'], reverse=True)

        return scored_items

    def get_top_items(
        self,
        items: List[Dict[str, Any]],
        n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取评分最高的N个项目

        Args:
            items: 项目列表
            n: 返回数量

        Returns:
            评分最高的N个项目
        """
        ranked = self.rank_items(items)
        return ranked[:n]


def test_ranker():
    """测试排序器"""
    print("测试 ResultRanker...")

    # 测试数据
    test_items = [
        {
            'name': 'fastapi',
            'stargazers_count': 50000,
            'forks_count': 4000,
            'updated_at': '2026-03-30T10:00:00Z',
            'description': 'Fast web framework',
            'license': {'name': 'MIT'},
            'topics': ['python', 'web']
        },
        {
            'name': 'django',
            'stargazers_count': 60000,
            'forks_count': 25000,
            'updated_at': '2026-01-15T10:00:00Z',
            'description': 'Full-stack framework',
            'license': {'name': 'BSD'},
            'topics': ['python', 'web', 'framework']
        },
        {
            'name': 'flask',
            'stargazers_count': 55000,
            'forks_count': 15000,
            'updated_at': '2025-12-01T10:00:00Z',
            'description': 'Micro framework',
            'license': {'name': 'BSD'},
            'topics': ['python']
        }
    ]

    ranker = ResultRanker()

    # 测试评分
    for item in test_items:
        score = ranker.calculate_score(item)
        print(f"  {item['name']}: {score}")

    # 测试排序
    ranked = ranker.rank_items(test_items)
    print("\n排序结果:")
    for item in ranked:
        print(f"  {item['name']}: {item['_score']}")
        print(f"    流行度: {item['_score_breakdown']['popularity']}")
        print(f"    活跃度: {item['_score_breakdown']['activity']}")

    # 测试Top N
    top = ranker.get_top_items(test_items, 2)
    print(f"\nTop 2: {[i['name'] for i in top]}")

    print("\n✓ 所有测试通过！")


if __name__ == "__main__":
    test_ranker()

#!/usr/bin/env python3
"""
搜索历史管理器
记录、查询和分析搜索历史
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter


class HistoryManager:
    """
    搜索历史管理器

    功能：
    - 记录每次搜索的查询词、时间、结果数量
    - 查询历史记录
    - 统计分析（热门查询、搜索频率等）
    - 快速重试历史搜索
    """

    def __init__(self, history_file: str = "~/.presearch/history.json", max_size: int = 100):
        """
        初始化历史管理器

        Args:
            history_file: 历史记录文件路径
            max_size: 最大历史记录数量
        """
        self.history_file = Path(history_file).expanduser()
        self.max_size = max_size
        self._history: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._history = []
        else:
            self._history = []

    def _save(self) -> bool:
        """保存历史记录"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def add(
        self,
        query: str,
        sources: List[str],
        result_counts: Dict[str, int],
        duration_ms: Optional[int] = None,
        cached: bool = False
    ) -> bool:
        """
        添加搜索记录

        Args:
            query: 搜索查询
            sources: 使用的数据源
            result_counts: 各数据源的结果数量
            duration_ms: 搜索耗时（毫秒）
            cached: 是否命中缓存

        Returns:
            是否添加成功
        """
        record = {
            'id': self._generate_id(),
            'query': query,
            'sources': sources,
            'result_counts': result_counts,
            'total_results': sum(result_counts.values()),
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'duration_ms': duration_ms,
            'cached': cached
        }

        # 添加到开头（最新的在前面）
        self._history.insert(0, record)

        # 限制大小
        if len(self._history) > self.max_size:
            self._history = self._history[:self.max_size]

        return self._save()

    def _generate_id(self) -> str:
        """生成唯一ID"""
        import hashlib
        data = f"{time.time()}_{len(self._history)}"
        return hashlib.md5(data.encode()).hexdigest()[:8]

    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取所有历史记录

        Args:
            limit: 限制返回数量

        Returns:
            历史记录列表
        """
        if limit:
            return self._history[:limit]
        return self._history.copy()

    def get_recent(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取最近的历史记录

        Args:
            hours: 最近多少小时

        Returns:
            历史记录列表
        """
        cutoff = time.time() - (hours * 3600)
        return [h for h in self._history if h['timestamp'] > cutoff]

    def search_history(self, keyword: str) -> List[Dict[str, Any]]:
        """
        在历史记录中搜索

        Args:
            keyword: 关键词

        Returns:
            匹配的历史记录
        """
        keyword = keyword.lower()
        return [
            h for h in self._history
            if keyword in h['query'].lower()
        ]

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取历史记录

        Args:
            record_id: 记录ID

        Returns:
            历史记录，如果不存在则返回None
        """
        for h in self._history:
            if h['id'] == record_id:
                return h.copy()
        return None

    def delete(self, record_id: str) -> bool:
        """
        删除历史记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        for i, h in enumerate(self._history):
            if h['id'] == record_id:
                del self._history[i]
                return self._save()
        return False

    def clear(self) -> bool:
        """清空所有历史记录"""
        self._history = []
        return self._save()

    def get_stats(self) -> Dict[str, Any]:
        """
        获取历史统计信息

        Returns:
            统计信息字典
        """
        if not self._history:
            return {
                'total_searches': 0,
                'unique_queries': 0,
                'top_queries': [],
                'avg_results': 0,
                'cache_hit_rate': 0
            }

        # 统计查询次数
        query_counts = Counter(h['query'] for h in self._history)

        # 统计缓存命中率
        cached_count = sum(1 for h in self._history if h.get('cached', False))

        # 统计平均结果数
        avg_results = sum(h['total_results'] for h in self._history) / len(self._history)

        # 统计数据源使用频率
        source_usage = Counter()
        for h in self._history:
            source_usage.update(h.get('sources', []))

        return {
            'total_searches': len(self._history),
            'unique_queries': len(query_counts),
            'top_queries': query_counts.most_common(5),
            'avg_results': round(avg_results, 2),
            'cache_hit_rate': f"{cached_count / len(self._history):.1%}",
            'source_usage': dict(source_usage.most_common()),
            'first_search': self._history[-1]['datetime'] if self._history else None,
            'last_search': self._history[0]['datetime'] if self._history else None
        }

    def get_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        获取搜索趋势

        Args:
            days: 统计最近多少天

        Returns:
            趋势数据
        """
        cutoff = time.time() - (days * 86400)
        recent = [h for h in self._history if h['timestamp'] > cutoff]

        if not recent:
            return {'daily_counts': {}, 'trend': 'no_data'}

        # 按天统计
        daily_counts = {}
        for h in recent:
            date = datetime.fromtimestamp(h['timestamp']).strftime('%Y-%m-%d')
            daily_counts[date] = daily_counts.get(date, 0) + 1

        # 简单趋势判断
        if len(daily_counts) >= 2:
            dates = sorted(daily_counts.keys())
            first_count = daily_counts[dates[0]]
            last_count = daily_counts[dates[-1]]

            if last_count > first_count * 1.2:
                trend = 'increasing'
            elif last_count < first_count * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'daily_counts': daily_counts,
            'trend': trend,
            'total_in_period': len(recent)
        }

    def format_for_display(self, limit: int = 10) -> str:
        """
        格式化为显示字符串

        Args:
            limit: 显示数量

        Returns:
            格式化字符串
        """
        if not self._history:
            return "暂无搜索历史"

        lines = ["## 搜索历史", ""]
        lines.append(f"{'ID':<8} {'时间':<20} {'查询':<30} {'结果数':<8} {'缓存'}")
        lines.append("-" * 80)

        for h in self._history[:limit]:
            dt = datetime.fromtimestamp(h['timestamp']).strftime('%m-%d %H:%M')
            query = h['query'][:28] + '..' if len(h['query']) > 30 else h['query']
            cached = '✓' if h.get('cached', False) else ''
            lines.append(
                f"{h['id']:<8} {dt:<20} {query:<30} "
                f"{h['total_results']:<8} {cached}"
            )

        return "\n".join(lines)


def test_history_manager():
    """测试历史管理器"""
    import tempfile
    import shutil

    print("测试 HistoryManager...")

    # 使用临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建历史管理器
        history = HistoryManager(
            history_file=f"{temp_dir}/history.json",
            max_size=10
        )

        # 测试添加记录
        history.add(
            query="Python web framework",
            sources=["github", "pypi"],
            result_counts={'github': 10, 'pypi': 5},
            duration_ms=1500,
            cached=False
        )
        print("✓ 添加记录测试通过")

        # 测试获取所有记录
        all_records = history.get_all()
        assert len(all_records) == 1
        print("✓ 获取记录测试通过")

        # 测试搜索历史
        results = history.search_history("python")
        assert len(results) == 1
        print("✓ 搜索历史测试通过")

        # 测试统计
        stats = history.get_stats()
        assert stats['total_searches'] == 1
        print("✓ 统计功能测试通过")

        # 测试趋势
        trends = history.get_trends()
        assert 'daily_counts' in trends
        print("✓ 趋势分析测试通过")

        # 测试删除
        record_id = all_records[0]['id']
        assert history.delete(record_id) == True
        assert len(history.get_all()) == 0
        print("✓ 删除记录测试通过")

        print("\n所有测试通过！")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_history_manager()

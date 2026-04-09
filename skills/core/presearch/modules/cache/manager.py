#!/usr/bin/env python3
"""
缓存管理器模块
统一接口管理内存缓存和文件缓存
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List
from pathlib import Path

# 导入现有缓存模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

from memory_cache import MemoryCache
from file_cache import FileCache


class CacheManager:
    """
    缓存管理器 - 统一管理内存缓存和文件缓存

    特性：
    - 两级缓存：内存（快）+ 文件（持久化）
    - 自动缓存键生成
    - 缓存统计和监控
    - 线程安全
    """

    def __init__(
        self,
        memory_ttl: int = 300,  # 5分钟
        disk_ttl: int = 86400,  # 24小时
        memory_max_size: int = 100,
        cache_dir: str = "~/.cache/presearch"
    ):
        """
        初始化缓存管理器

        Args:
            memory_ttl: 内存缓存TTL（秒）
            disk_ttl: 磁盘缓存TTL（秒）
            memory_max_size: 内存缓存最大条目数
            cache_dir: 磁盘缓存目录
        """
        self.memory_cache = MemoryCache(
            max_size=memory_max_size,
            ttl_seconds=memory_ttl
        )
        self.file_cache = FileCache(
            cache_dir=cache_dir,
            ttl_hours=disk_ttl // 3600
        )

        # 统计信息
        self._stats = {
            'memory_hits': 0,
            'memory_misses': 0,
            'disk_hits': 0,
            'disk_misses': 0,
            'total_requests': 0
        }

    def _generate_cache_key(self, query: str, sources: List[str], params: Optional[Dict] = None) -> str:
        """
        生成缓存键

        Args:
            query: 搜索查询
            sources: 数据源列表
            params: 搜索参数

        Returns:
            缓存键（MD5哈希）
        """
        cache_data = {
            'query': query.lower().strip(),
            'sources': sorted(sources),
            'params': params or {}
        }

        data_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def get(
        self,
        query: str,
        sources: List[str],
        params: Optional[Dict] = None
    ) -> Optional[Any]:
        """
        获取缓存结果

        先查内存，再查磁盘。如果磁盘命中，回填内存。

        Args:
            query: 搜索查询
            sources: 数据源列表
            params: 搜索参数

        Returns:
            缓存的结果，如果没有则返回None
        """
        self._stats['total_requests'] += 1
        cache_key = self._generate_cache_key(query, sources, params)

        # 先查内存缓存
        result = self.memory_cache.get(cache_key)
        if result is not None:
            self._stats['memory_hits'] += 1
            return result

        self._stats['memory_misses'] += 1

        # 再查文件缓存
        result = self.file_cache.get(cache_key)
        if result is not None:
            self._stats['disk_hits'] += 1
            # 回填内存缓存
            self.memory_cache.set(cache_key, result)
            return result

        self._stats['disk_misses'] += 1
        return None

    def set(
        self,
        query: str,
        sources: List[str],
        result: Any,
        params: Optional[Dict] = None
    ) -> str:
        """
        设置缓存结果

        同时写入内存缓存和文件缓存

        Args:
            query: 搜索查询
            sources: 数据源列表
            result: 搜索结果
            params: 搜索参数

        Returns:
            缓存键
        """
        cache_key = self._generate_cache_key(query, sources, params)

        # 写入内存缓存
        self.memory_cache.set(cache_key, result)

        # 写入文件缓存
        self.file_cache.set(cache_key, result)

        return cache_key

    def delete(
        self,
        query: str,
        sources: List[str],
        params: Optional[Dict] = None
    ) -> bool:
        """
        删除缓存条目

        Args:
            query: 搜索查询
            sources: 数据源列表
            params: 搜索参数

        Returns:
            是否成功删除
        """
        cache_key = self._generate_cache_key(query, sources, params)

        # 删除内存缓存
        memory_deleted = self.memory_cache.delete(cache_key)

        # 删除文件缓存
        file_deleted = self.file_cache.delete(cache_key)

        return memory_deleted or file_deleted

    def clear_all(self) -> None:
        """清空所有缓存（内存+文件）"""
        self.memory_cache.clear()
        self.file_cache.clear()

        # 重置统计
        self._stats = {
            'memory_hits': 0,
            'memory_misses': 0,
            'disk_hits': 0,
            'disk_misses': 0,
            'total_requests': 0
        }

    def cleanup(self) -> int:
        """
        清理过期缓存

        Returns:
            清理的条目数量
        """
        # 清理内存缓存
        memory_cleaned = self.memory_cache.cleanup()

        # 清理文件缓存
        file_cleaned = self.file_cache.cleanup()

        return memory_cleaned + file_cleaned

    def get_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        # 获取文件缓存的持久化统计
        file_stats = self.file_cache.get_stats()
        file_hits = file_stats.get('hits', 0)
        file_misses = file_stats.get('misses', 0)

        # 合并内存统计和文件统计
        memory_total = self._stats['memory_hits'] + self._stats['memory_misses']
        disk_total = file_hits + file_misses

        memory_hit_rate = (
            self._stats['memory_hits'] / memory_total
            if memory_total > 0 else 0.0
        )

        disk_hit_rate = (
            file_hits / disk_total
            if disk_total > 0 else 0.0
        )

        # 总体统计：内存统计 + 文件持久化统计
        total_hits = self._stats['memory_hits'] + file_hits
        total_requests = self._stats['total_requests'] + file_hits + file_misses
        overall_hit_rate = (
            total_hits / total_requests
            if total_requests > 0 else 0.0
        )

        return {
            'total_requests': total_requests,
            'memory_hits': self._stats['memory_hits'],
            'memory_misses': self._stats['memory_misses'],
            'memory_hit_rate': f"{memory_hit_rate:.2%}",
            'disk_hits': file_hits,
            'disk_misses': file_misses,
            'disk_hit_rate': f"{disk_hit_rate:.2%}",
            'overall_hit_rate': f"{overall_hit_rate:.2%}",
            'memory_size': self.memory_cache.size(),
            'file_stats': file_stats
        }

    def get_cache_dir(self) -> str:
        """获取缓存目录路径"""
        return self.file_cache.cache_dir


def test_cache_manager():
    """测试缓存管理器"""
    print("测试 CacheManager...")

    import tempfile
    import shutil

    # 使用临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建缓存管理器
        cache = CacheManager(
            memory_ttl=2,  # 2秒TTL便于测试
            disk_ttl=3600,
            memory_max_size=10,
            cache_dir=temp_dir
        )

        # 测试数据
        query = "Python web framework"
        sources = ["github", "pypi"]
        result = {"items": ["fastapi", "django", "flask"]}

        # 测试设置缓存
        cache_key = cache.set(query, sources, result)
        print(f"✓ 缓存设置成功，key: {cache_key[:8]}...")

        # 测试获取缓存（应该从内存命中）
        cached = cache.get(query, sources)
        assert cached == result
        print("✓ 内存缓存命中")

        # 等待内存缓存过期
        time.sleep(3)

        # 再次获取（应该从磁盘命中并回填内存）
        cached = cache.get(query, sources)
        assert cached == result
        print("✓ 磁盘缓存命中并回填内存")

        # 检查统计
        stats = cache.get_stats()
        assert stats['memory_hits'] >= 1
        assert stats['disk_hits'] >= 1
        print(f"✓ 缓存统计正常: {stats['overall_hit_rate']} 命中率")

        # 测试删除
        cache.delete(query, sources)
        cached = cache.get(query, sources)
        assert cached is None
        print("✓ 缓存删除成功")

        # 测试清空
        cache.set(query, sources, result)
        cache.clear_all()
        stats = cache.get_stats()
        assert stats['total_requests'] == 0
        print("✓ 缓存清空成功")

        print("\n所有测试通过！")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_cache_manager()

#!/usr/bin/env python3
"""
内存缓存模块
基于LRU算法的内存缓存，支持TTL
"""

import time
from collections import OrderedDict
from typing import Any, Optional, Tuple
import threading

class MemoryCache:
    """
    基于LRU算法的内存缓存

    特性：
    - LRU（最近最少使用）淘汰策略
    - TTL（生存时间）支持
    - 线程安全
    - 最大容量限制
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        初始化内存缓存

        Args:
            max_size: 最大缓存条目数，默认100
            ttl_seconds: 缓存条目生存时间（秒），默认300秒（5分钟）
        """
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = threading.RLock()  # 可重入锁，支持嵌套调用

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        with self.lock:
            if key not in self.cache:
                return None

            value, timestamp = self.cache[key]

            # 检查是否过期
            if time.time() - timestamp > self.ttl:
                del self.cache[key]
                return None

            # 移动到最近使用位置（LRU特性）
            self.cache.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        with self.lock:
            # 如果键已存在，先删除（为了正确更新位置）
            if key in self.cache:
                del self.cache[key]

            # 如果达到最大容量，移除最久未使用的项
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)

            # 添加新条目
            self.cache[key] = (value, time.time())

    def delete(self, key: str) -> bool:
        """
        删除缓存条目

        Args:
            key: 缓存键

        Returns:
            是否成功删除（True表示删除成功，False表示键不存在）
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空所有缓存"""
        with self.lock:
            self.cache.clear()

    def size(self) -> int:
        """获取当前缓存大小"""
        with self.lock:
            return len(self.cache)

    def cleanup(self) -> int:
        """
        清理过期缓存条目

        Returns:
            清理的条目数量
        """
        with self.lock:
            current_time = time.time()
            expired_keys = []

            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > self.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

    def keys(self) -> list[str]:
        """获取所有缓存键"""
        with self.lock:
            return list(self.cache.keys())

    def has(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        with self.lock:
            if key not in self.cache:
                return False

            _, timestamp = self.cache[key]
            return time.time() - timestamp <= self.ttl

    def get_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            包含统计信息的字典
        """
        with self.lock:
            current_time = time.time()
            total = len(self.cache)
            expired = 0

            for _, timestamp in self.cache.values():
                if current_time - timestamp > self.ttl:
                    expired += 1

            return {
                'total_entries': total,
                'expired_entries': expired,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl,
                'hit_ratio': self._calculate_hit_ratio() if hasattr(self, '_hits') else None
            }

    def _calculate_hit_ratio(self) -> float:
        """计算命中率（如果启用了命中率统计）"""
        if hasattr(self, '_hits') and hasattr(self, '_misses'):
            total = self._hits + self._misses
            return self._hits / total if total > 0 else 0.0
        return 0.0

    def enable_stats(self) -> None:
        """启用命中率统计"""
        with self.lock:
            self._hits = 0
            self._misses = 0
            self._original_get = self.get
            self._original_set = self.set

            def counting_get(key):
                result = self._original_get(key)
                if result is not None:
                    self._hits += 1
                else:
                    self._misses += 1
                return result

            def counting_set(key, value):
                return self._original_set(key, value)

            self.get = counting_get
            self.set = counting_set


def test_memory_cache():
    """测试内存缓存功能"""
    print("测试MemoryCache...")

    # 创建缓存实例
    cache = MemoryCache(max_size=3, ttl_seconds=2)

    # 测试基本设置和获取
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    print("✓ 基本设置和获取测试通过")

    # 测试LRU淘汰
    cache.set("key4", "value4")  # 应该淘汰key1（最久未使用）
    assert cache.get("key1") is None
    assert cache.get("key4") == "value4"
    print("✓ LRU淘汰测试通过")

    # 测试TTL过期
    cache.set("key5", "value5")
    time.sleep(3)  # 等待过期
    assert cache.get("key5") is None
    print("✓ TTL过期测试通过")

    # 测试访问更新LRU位置
    cache.set("key6", "value6")
    cache.set("key7", "value7")
    cache.get("key6")  # 访问key6，使其成为最近使用
    cache.set("key8", "value8")  # 应该淘汰key2（最久未使用）
    assert cache.get("key2") is None
    assert cache.get("key6") == "value6"  # key6应该还在
    print("✓ 访问更新LRU位置测试通过")

    # 测试清理功能
    cache.set("expired1", "value1")
    time.sleep(3)
    cleaned = cache.cleanup()
    assert cleaned > 0
    assert cache.get("expired1") is None
    print(f"✓ 清理过期条目测试通过（清理了{cleaned}个条目）")

    # 测试统计信息
    stats = cache.get_stats()
    assert 'total_entries' in stats
    assert 'expired_entries' in stats
    print("✓ 统计信息测试通过")

    print("所有测试通过！")


if __name__ == "__main__":
    test_memory_cache()
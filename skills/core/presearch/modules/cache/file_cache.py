#!/usr/bin/env python3
"""
文件缓存模块
基于文件的持久化缓存，支持TTL和自动清理
"""

import os
import json
import time
import hashlib
import shutil
from typing import Any, Optional, Dict
from pathlib import Path


class FileCache:
    """
    基于文件的持久化缓存

    特性：
    - JSON格式存储
    - TTL（生存时间）支持
    - 自动清理过期缓存
    - 基于hash的缓存键
    """

    def __init__(self, cache_dir: str = "~/.cache/presearch", ttl_hours: int = 24):
        """
        初始化文件缓存

        Args:
            cache_dir: 缓存目录路径，默认 ~/.cache/presearch
            ttl_hours: 缓存条目生存时间（小时），默认24小时
        """
        self.cache_dir = os.path.expanduser(cache_dir)
        self.ttl = ttl_hours * 3600  # 转换为秒

        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)

        # 元数据文件路径
        self.meta_file = os.path.join(self.cache_dir, ".metadata.json")

        # 加载或初始化元数据
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """加载缓存元数据"""
        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # 如果元数据文件损坏，重新初始化
                return self._init_metadata()
        else:
            return self._init_metadata()

    def _init_metadata(self) -> Dict:
        """初始化元数据"""
        metadata = {
            'version': '1.0',
            'created_at': time.time(),
            'total_entries': 0,
            'hits': 0,
            'misses': 0,
            'last_cleanup': time.time()
        }
        self._save_metadata(metadata)
        return metadata

    def _save_metadata(self, metadata: Dict) -> None:
        """保存元数据"""
        try:
            with open(self.meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except IOError:
            # 如果无法保存元数据，继续但不记录统计
            pass

    def _generate_cache_key(self, data: Any) -> str:
        """
        生成缓存键

        Args:
            data: 要缓存的数据

        Returns:
            基于数据hash的缓存键
        """
        # 将数据转换为可hash的字符串
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        # 生成MD5 hash作为缓存键
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def _get_cache_file_path(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用两级目录结构避免单个目录文件过多
        dir_name = key[:2]
        dir_path = os.path.join(self.cache_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, f"{key}.json")

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        cache_file = self._get_cache_file_path(key)

        if not os.path.exists(cache_file):
            self.metadata['misses'] += 1
            self._save_metadata(self.metadata)
            return None

        try:
            # 检查文件修改时间
            file_mtime = os.path.getmtime(cache_file)
            if time.time() - file_mtime > self.ttl:
                # 文件已过期，删除
                os.remove(cache_file)
                self.metadata['misses'] += 1
                self._save_metadata(self.metadata)
                return None

            # 读取缓存文件
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 更新命中统计
            self.metadata['hits'] += 1
            self._save_metadata(self.metadata)

            return cache_data.get('value')

        except (json.JSONDecodeError, IOError, KeyError):
            # 如果文件损坏或格式错误，删除它
            try:
                os.remove(cache_file)
            except OSError:
                pass

            self.metadata['misses'] += 1
            self._save_metadata(self.metadata)
            return None

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 要缓存的值
        """
        cache_file = self._get_cache_file_path(key)

        try:
            # 准备缓存数据
            cache_data = {
                'key': key,
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + self.ttl
            }

            # 写入文件
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            # 更新元数据
            self.metadata['total_entries'] += 1
            self._save_metadata(self.metadata)

        except IOError as e:
            # 记录错误但继续执行
            print(f"警告：无法写入缓存文件 {cache_file}: {e}")

    def delete(self, key: str) -> bool:
        """
        删除缓存条目

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        cache_file = self._get_cache_file_path(key)

        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                # 更新元数据
                self.metadata['total_entries'] = max(0, self.metadata['total_entries'] - 1)
                self._save_metadata(self.metadata)
                return True
            except OSError:
                return False
        return False

    def clear(self) -> None:
        """清空所有缓存"""
        try:
            # 删除整个缓存目录
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)

            # 重新创建目录
            os.makedirs(self.cache_dir, exist_ok=True)

            # 重置元数据
            self.metadata = self._init_metadata()

        except OSError as e:
            print(f"警告：无法清空缓存目录 {self.cache_dir}: {e}")

    def cleanup(self, force: bool = False) -> int:
        """
        清理过期缓存条目

        Args:
            force: 是否强制清理（即使最近清理过）

        Returns:
            清理的条目数量
        """
        current_time = time.time()

        # 检查是否需要清理（至少1小时一次，除非强制）
        last_cleanup = self.metadata.get('last_cleanup', 0)
        if not force and current_time - last_cleanup < 3600:
            return 0

        cleaned_count = 0

        try:
            # 遍历所有缓存文件
            for root, dirs, files in os.walk(self.cache_dir):
                # 跳过隐藏文件和元数据文件
                files = [f for f in files if not f.startswith('.') and f.endswith('.json')]

                for file in files:
                    file_path = os.path.join(root, file)

                    try:
                        # 检查文件修改时间
                        file_mtime = os.path.getmtime(file_path)
                        if current_time - file_mtime > self.ttl:
                            os.remove(file_path)
                            cleaned_count += 1
                    except (OSError, FileNotFoundError):
                        # 文件可能已被删除，继续处理下一个
                        continue

            # 更新元数据
            self.metadata['last_cleanup'] = current_time
            self.metadata['total_entries'] = max(0, self.metadata['total_entries'] - cleaned_count)
            self._save_metadata(self.metadata)

            return cleaned_count

        except OSError as e:
            print(f"警告：清理缓存时出错: {e}")
            return 0

    def size(self) -> int:
        """获取当前缓存条目数量"""
        # 触发一次清理，确保计数准确
        self.cleanup()
        return self.metadata.get('total_entries', 0)

    def get_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            包含统计信息的字典
        """
        # 触发清理以更新统计
        cleaned = self.cleanup()

        stats = {
            'cache_dir': self.cache_dir,
            'total_entries': self.metadata.get('total_entries', 0),
            'hits': self.metadata.get('hits', 0),
            'misses': self.metadata.get('misses', 0),
            'hit_ratio': self._calculate_hit_ratio(),
            'ttl_hours': self.ttl / 3600,
            'last_cleanup': time.strftime('%Y-%m-%d %H:%M:%S',
                                         time.localtime(self.metadata.get('last_cleanup', 0))),
            'cleaned_in_last_run': cleaned,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(self.metadata.get('created_at', 0)))
        }

        # 计算目录大小
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.cache_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            stats['total_size_bytes'] = total_size
            stats['total_size_mb'] = total_size / (1024 * 1024)
        except OSError:
            stats['total_size_bytes'] = 0
            stats['total_size_mb'] = 0

        return stats

    def _calculate_hit_ratio(self) -> float:
        """计算命中率"""
        hits = self.metadata.get('hits', 0)
        misses = self.metadata.get('misses', 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0

    def cache_search_result(self, query: str, sources: list, params: dict, result: Any) -> str:
        """
        缓存搜索结果（便捷方法）

        Args:
            query: 搜索查询
            sources: 数据源列表
            params: 搜索参数
            result: 搜索结果

        Returns:
            缓存键
        """
        # 生成缓存数据
        cache_data = {
            'query': query,
            'sources': sorted(sources),
            'params': params,
            'timestamp': time.time()
        }

        # 生成缓存键
        cache_key = self._generate_cache_key(cache_data)

        # 缓存结果
        self.set(cache_key, result)

        return cache_key

    def get_cached_search(self, query: str, sources: list, params: dict) -> Optional[Any]:
        """
        获取缓存的搜索结果（便捷方法）

        Args:
            query: 搜索查询
            sources: 数据源列表
            params: 搜索参数

        Returns:
            缓存的结果，如果没有则返回None
        """
        # 生成缓存数据
        cache_data = {
            'query': query,
            'sources': sorted(sources),
            'params': params,
            'timestamp': time.time()
        }

        # 生成缓存键
        cache_key = self._generate_cache_key(cache_data)

        # 获取缓存结果
        return self.get(cache_key)


def test_file_cache():
    """测试文件缓存功能"""
    print("测试FileCache...")

    # 使用临时目录进行测试
    import tempfile
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建缓存实例
        cache = FileCache(cache_dir=os.path.join(temp_dir, "test_cache"), ttl_hours=0.01)  # 36秒TTL

        # 测试基本设置和获取
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        assert result == {"data": "test_value"}
        print("✓ 基本设置和获取测试通过")

        # 测试TTL过期
        import time
        time.sleep(40)  # 等待过期
        result = cache.get("test_key")
        assert result is None
        print("✓ TTL过期测试通过")

        # 测试缓存搜索结果的便捷方法
        query = "Python web framework"
        sources = ["github", "npm"]
        params = {"limit": 10}
        test_result = {"items": ["result1", "result2"]}

        cache_key = cache.cache_search_result(query, sources, params, test_result)
        cached = cache.get_cached_search(query, sources, params)
        assert cached == test_result
        print("✓ 缓存搜索结果测试通过")

        # 测试统计信息
        stats = cache.get_stats()
        assert 'total_entries' in stats
        assert 'hit_ratio' in stats
        print("✓ 统计信息测试通过")

        # 测试清理功能
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        time.sleep(40)  # 等待过期
        cleaned = cache.cleanup(force=True)
        assert cleaned >= 2  # 至少清理2个过期条目
        print(f"✓ 清理功能测试通过（清理了{cleaned}个条目）")

        print("所有测试通过！")

    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_file_cache()
#!/usr/bin/env python3
"""
配置设置模块
使用 pydantic-settings 管理配置
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class PresearchConfig(BaseSettings):
    """
    Presearch 配置类

    支持配置文件、环境变量和默认值
    """

    # 数据源配置
    sources: List[str] = Field(
        default=['github', 'arxiv', 'npm', 'pypi', 'docker'],
        description="启用的数据源列表"
    )

    # 缓存配置
    cache_enabled: bool = Field(
        default=True,
        description="是否启用缓存"
    )
    cache_ttl: int = Field(
        default=86400,
        description="缓存TTL（秒），默认24小时"
    )
    cache_max_size: int = Field(
        default=100,
        description="内存缓存最大条目数"
    )
    cache_dir: str = Field(
        default="~/.cache/presearch",
        description="缓存目录路径"
    )

    # 搜索配置
    default_per_page: int = Field(
        default=10,
        description="默认每页结果数量"
    )
    timeout: int = Field(
        default=10,
        description="API请求超时时间（秒）"
    )
    max_retries: int = Field(
        default=3,
        description="请求失败最大重试次数"
    )

    # 输出配置
    default_format: str = Field(
        default="table",
        description="默认输出格式（table/json/csv）"
    )
    color_enabled: bool = Field(
        default=True,
        description="是否启用颜色输出"
    )

    # 历史记录配置
    history_enabled: bool = Field(
        default=True,
        description="是否启用搜索历史"
    )
    history_max_size: int = Field(
        default=20,
        description="最大历史记录数量"
    )

    class Config:
        """Pydantic 配置"""
        env_prefix = 'PRESEARCH_'
        case_sensitive = False
        # 配置文件路径（按优先级排序）
        config_file_paths = [
            '~/.presearch/config.json',
            '~/.presearch/config.yaml',
            '~/.presearch/config.yml',
            './.presearch.json',
            './.presearch.yaml',
        ]

    def get_enabled_sources(self) -> List[str]:
        """获取启用的数据源列表"""
        return [s for s in self.sources if s in ['github', 'arxiv', 'npm', 'pypi', 'docker']]

    def is_source_enabled(self, source: str) -> bool:
        """检查数据源是否启用"""
        return source in self.sources

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'sources': self.sources,
            'cache_enabled': self.cache_enabled,
            'cache_ttl': self.cache_ttl,
            'cache_max_size': self.cache_max_size,
            'cache_dir': self.cache_dir,
            'default_per_page': self.default_per_page,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'default_format': self.default_format,
            'color_enabled': self.color_enabled,
            'history_enabled': self.history_enabled,
            'history_max_size': self.history_max_size,
        }


# 全局配置实例
_config_instance: Optional[PresearchConfig] = None


def get_config() -> PresearchConfig:
    """
    获取配置实例（单例模式）

    Returns:
        PresearchConfig 实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = PresearchConfig()
    return _config_instance


def reload_config() -> PresearchConfig:
    """
    重新加载配置

    Returns:
        新的 PresearchConfig 实例
    """
    global _config_instance
    _config_instance = PresearchConfig()
    return _config_instance


def test_config():
    """测试配置系统"""
    print("测试 PresearchConfig...")

    # 测试默认配置
    config = PresearchConfig()
    assert config.cache_enabled == True
    assert config.cache_ttl == 86400
    assert 'github' in config.sources
    print("✓ 默认配置测试通过")

    # 测试环境变量
    os.environ['PRESEARCH_CACHE_TTL'] = '3600'
    os.environ['PRESEARCH_DEFAULT_FORMAT'] = 'json'

    config2 = PresearchConfig()
    assert config2.cache_ttl == 3600
    assert config2.default_format == 'json'
    print("✓ 环境变量测试通过")

    # 清理环境变量
    del os.environ['PRESEARCH_CACHE_TTL']
    del os.environ['PRESEARCH_DEFAULT_FORMAT']

    # 测试单例
    config3 = get_config()
    config4 = get_config()
    assert config3 is config4
    print("✓ 单例模式测试通过")

    print("\n所有测试通过！")
    print(f"\n默认配置:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_config()

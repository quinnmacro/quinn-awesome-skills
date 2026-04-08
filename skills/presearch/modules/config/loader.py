#!/usr/bin/env python3
"""
配置加载器模块
支持从文件、环境变量加载配置
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .settings import PresearchConfig
from .presets import apply_preset


class ConfigLoader:
    """
    配置加载器

    支持多种配置来源（按优先级从低到高）：
    1. 默认配置
    2. 预设配置
    3. 配置文件
    4. 环境变量
    """

    # 配置文件搜索路径
    CONFIG_PATHS = [
        '~/.presearch/config.json',
        '~/.presearch/config.yaml',
        '~/.presearch/config.yml',
        './.presearch.json',
        './.presearch.yaml',
    ]

    def __init__(self):
        self.config_dir = Path.home() / '.presearch'
        self.config_file = self.config_dir / 'config.json'

    def load(
        self,
        preset: Optional[str] = None,
        config_path: Optional[str] = None
    ) -> PresearchConfig:
        """
        加载配置

        Args:
            preset: 预设配置名称
            config_path: 自定义配置文件路径

        Returns:
            PresearchConfig 实例
        """
        # 从环境变量创建基础配置
        config_dict = {}

        # 应用预设（如果指定）
        if preset:
            config_dict = apply_preset(config_dict, preset)

        # 加载配置文件
        file_config = self._load_from_file(config_path)
        config_dict.update(file_config)

        # 创建配置实例（会自动加载环境变量）
        config = PresearchConfig(**config_dict)

        return config

    def _load_from_file(self, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """
        从文件加载配置

        Args:
            custom_path: 自定义配置文件路径

        Returns:
            配置字典
        """
        # 如果指定了自定义路径，优先使用
        if custom_path:
            path = Path(custom_path).expanduser()
            if path.exists():
                return self._parse_config_file(path)
            return {}

        # 按顺序搜索配置文件
        for config_path in self.CONFIG_PATHS:
            path = Path(config_path).expanduser()
            if path.exists():
                return self._parse_config_file(path)

        return {}

    def _parse_config_file(self, path: Path) -> Dict[str, Any]:
        """
        解析配置文件

        Args:
            path: 配置文件路径

        Returns:
            配置字典
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix in ['.yaml', '.yml']:
                    try:
                        import yaml
                        return yaml.safe_load(f) or {}
                    except ImportError:
                        print(f"警告: 无法解析YAML文件 {path}，请安装PyYAML")
                        return {}
                else:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法加载配置文件 {path}: {e}")
            return {}

    def save_config(self, config: PresearchConfig, path: Optional[str] = None) -> bool:
        """
        保存配置到文件

        Args:
            config: 配置实例
            path: 保存路径，默认使用 ~/.presearch/config.json

        Returns:
            是否保存成功
        """
        save_path = Path(path).expanduser() if path else self.config_file

        try:
            # 确保目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存为JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

            return True
        except IOError as e:
            print(f"错误: 无法保存配置到 {save_path}: {e}")
            return False

    def init_config_file(self, preset: Optional[str] = None) -> bool:
        """
        初始化配置文件

        Args:
            preset: 预设配置名称

        Returns:
            是否初始化成功
        """
        # 确保目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 加载配置（应用预设）
        config = self.load(preset=preset)

        # 保存到文件
        return self.save_config(config)

    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_file)

    def config_exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_file.exists()


def test_loader():
    """测试配置加载器"""
    print("测试 ConfigLoader...")

    import tempfile
    import shutil

    # 使用临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        loader = ConfigLoader()
        loader.config_dir = Path(temp_dir)
        loader.config_file = Path(temp_dir) / 'config.json'

        # 测试加载默认配置
        config = loader.load()
        assert config.cache_enabled == True
        print("✓ 默认配置加载测试通过")

        # 测试预设配置
        config = loader.load(preset='frontend')
        assert config.sources == ['github', 'npm']
        print("✓ 预设配置加载测试通过")

        # 测试保存配置
        config.cache_ttl = 7200
        success = loader.save_config(config)
        assert success
        assert loader.config_file.exists()
        print("✓ 配置保存测试通过")

        # 测试从文件加载
        config2 = loader.load()
        assert config2.cache_ttl == 7200
        print("✓ 配置文件加载测试通过")

        # 测试初始化配置
        loader.config_file.unlink()
        success = loader.init_config_file(preset='backend')
        assert success
        config3 = loader.load()
        assert 'pypi' in config3.sources
        print("✓ 配置初始化测试通过")

        print("\n所有测试通过！")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_loader()

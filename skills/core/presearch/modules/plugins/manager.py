#!/usr/bin/env python3
"""
插件管理器模块
管理插件的加载、注册和执行
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .base import Plugin, DataSourcePlugin, ProcessorPlugin, OutputPlugin


class PluginManager:
    """
    插件管理器

    功能：
    - 加载插件（从目录或模块）
    - 注册插件
    - 管理插件生命周期
    - 执行插件
    """

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        初始化插件管理器

        Args:
            plugin_dirs: 插件目录列表
        """
        self.plugin_dirs = plugin_dirs or [
            '~/.presearch/plugins',
            './plugins'
        ]

        # 插件存储
        self._datasources: Dict[str, DataSourcePlugin] = {}
        self._processors: List[ProcessorPlugin] = []
        self._outputs: Dict[str, OutputPlugin] = {}

        # 加载插件
        self._load_all_plugins()

    def _load_all_plugins(self) -> None:
        """加载所有插件"""
        for plugin_dir in self.plugin_dirs:
            path = Path(plugin_dir).expanduser()
            if path.exists():
                self._load_from_directory(path)

    def _load_from_directory(self, directory: Path) -> None:
        """
        从目录加载插件

        Args:
            directory: 插件目录
        """
        for file_path in directory.glob('*.py'):
            if file_path.name.startswith('_'):
                continue

            try:
                self._load_from_file(file_path)
            except Exception as e:
                print(f"加载插件失败 {file_path}: {e}")

    def _load_from_file(self, file_path: Path) -> None:
        """
        从文件加载插件

        Args:
            file_path: 插件文件路径
        """
        spec = importlib.util.spec_from_file_location(
            file_path.stem,
            file_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找插件类
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, Plugin) and
                attr != Plugin and
                attr != DataSourcePlugin and
                attr != ProcessorPlugin and
                attr != OutputPlugin):

                self.register_plugin(attr)

    def register_plugin(self, plugin_class: Type[Plugin], config: Optional[Dict] = None) -> bool:
        """
        注册插件

        Args:
            plugin_class: 插件类
            config: 插件配置

        Returns:
            是否注册成功
        """
        try:
            instance = plugin_class(config)

            if not instance.initialize():
                return False

            # 根据类型分类存储
            if isinstance(instance, DataSourcePlugin):
                self._datasources[instance.name] = instance
            elif isinstance(instance, ProcessorPlugin):
                self._processors.append(instance)
                # 按优先级排序
                self._processors.sort(key=lambda p: p.get_priority())
            elif isinstance(instance, OutputPlugin):
                self._outputs[instance.get_format_name()] = instance

            return True

        except Exception as e:
            print(f"注册插件失败: {e}")
            return False

    def get_datasource(self, name: str) -> Optional[DataSourcePlugin]:
        """
        获取数据源插件

        Args:
            name: 插件名称

        Returns:
            数据源插件实例
        """
        return self._datasources.get(name)

    def get_all_datasources(self) -> Dict[str, DataSourcePlugin]:
        """获取所有数据源插件"""
        return self._datasources.copy()

    def get_output(self, format_name: str) -> Optional[OutputPlugin]:
        """
        获取输出格式插件

        Args:
            format_name: 格式名称

        Returns:
            输出插件实例
        """
        return self._outputs.get(format_name)

    def process_results(self, results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        使用所有处理器插件处理结果

        Args:
            results: 原始结果
            **kwargs: 其他参数

        Returns:
            处理后的结果
        """
        for processor in self._processors:
            try:
                results = processor.process(results, **kwargs)
            except Exception as e:
                print(f"处理器 {processor.name} 执行失败: {e}")

        return results

    def list_plugins(self) -> Dict[str, List[str]]:
        """
        列出所有已加载的插件

        Returns:
            插件分类列表
        """
        return {
            'datasources': list(self._datasources.keys()),
            'processors': [p.name for p in self._processors],
            'outputs': list(self._outputs.keys())
        }

    def get_plugin_info(self, name: str) -> Optional[Dict[str, str]]:
        """
        获取插件信息

        Args:
            name: 插件名称

        Returns:
            插件信息
        """
        # 在所有类型中查找
        if name in self._datasources:
            return self._datasources[name].get_info()

        for p in self._processors:
            if p.name == name:
                return p.get_info()

        for fmt, plugin in self._outputs.items():
            if plugin.name == name:
                return plugin.get_info()

        return None

    def shutdown_all(self) -> None:
        """关闭所有插件"""
        for plugin in self._datasources.values():
            plugin.shutdown()

        for plugin in self._processors:
            plugin.shutdown()

        for plugin in self._outputs.values():
            plugin.shutdown()


def test_plugin_manager():
    """测试插件管理器"""
    print("测试 PluginManager...")

    from .base import ExampleDataSource, ExampleProcessor, ExampleOutput

    # 创建管理器
    manager = PluginManager(plugin_dirs=[])

    # 注册插件
    assert manager.register_plugin(ExampleDataSource) == True
    assert manager.register_plugin(ExampleProcessor) == True
    assert manager.register_plugin(ExampleOutput) == True
    print("✓ 插件注册测试通过")

    # 测试获取数据源
    ds = manager.get_datasource('example')
    assert ds is not None
    result = ds.search("test")
    assert result['source'] == 'example'
    print("✓ 数据源获取测试通过")

    # 测试处理器执行
    test_data = {'items': []}
    processed = manager.process_results(test_data)
    assert '_processed_by' in processed
    print("✓ 处理器执行测试通过")

    # 测试获取输出格式
    output = manager.get_output('example')
    assert output is not None
    formatted = output.format("test")
    assert '[EXAMPLE]' in formatted
    print("✓ 输出格式获取测试通过")

    # 测试列出插件
    plugins = manager.list_plugins()
    assert 'example' in plugins['datasources']
    print("✓ 列出插件测试通过")

    # 测试插件信息
    info = manager.get_plugin_info('example')
    assert info is not None
    assert 'name' in info
    print("✓ 插件信息测试通过")

    # 关闭插件
    manager.shutdown_all()
    print("✓ 插件关闭测试通过")

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_plugin_manager()

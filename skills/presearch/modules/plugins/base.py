#!/usr/bin/env python3
"""
插件基类模块
定义插件接口和基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Plugin(ABC):
    """
    插件基类

    所有插件必须继承此类
    """

    # 插件元数据
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化插件

        Args:
            config: 插件配置
        """
        self.config = config or {}
        self.enabled = True

    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化插件

        Returns:
            是否初始化成功
        """
        pass

    def shutdown(self) -> None:
        """关闭插件"""
        pass

    def get_info(self) -> Dict[str, str]:
        """获取插件信息"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': str(self.enabled)
        }


class DataSourcePlugin(Plugin):
    """
    数据源插件基类

    用于添加新的搜索数据源
    """

    @abstractmethod
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询
            **kwargs: 其他参数

        Returns:
            搜索结果
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查数据源是否可用

        Returns:
            是否可用
        """
        pass


class ProcessorPlugin(Plugin):
    """
    处理器插件基类

    用于处理搜索结果
    """

    @abstractmethod
    def process(self, results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        处理结果

        Args:
            results: 搜索结果
            **kwargs: 其他参数

        Returns:
            处理后的结果
        """
        pass

    def get_priority(self) -> int:
        """
        获取处理优先级

        Returns:
            优先级（数字越小优先级越高）
        """
        return 100


class OutputPlugin(Plugin):
    """
    输出格式插件基类

    用于自定义输出格式
    """

    @abstractmethod
    def format(self, data: Any, **kwargs) -> str:
        """
        格式化数据

        Args:
            data: 要格式化的数据
            **kwargs: 其他参数

        Returns:
            格式化后的字符串
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """
        获取格式名称

        Returns:
            格式名称
        """
        pass


# 示例插件实现
class ExampleDataSource(DataSourcePlugin):
    """示例数据源插件"""

    name = "example"
    version = "1.0.0"
    description = "示例数据源插件"
    author = "presearch-team"

    def initialize(self) -> bool:
        print(f"初始化 {self.name} 插件")
        return True

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        return {
            'source': self.name,
            'query': query,
            'items': [
                {'name': f'Example result for {query}'}
            ]
        }

    def is_available(self) -> bool:
        return True


class ExampleProcessor(ProcessorPlugin):
    """示例处理器插件"""

    name = "example-processor"
    version = "1.0.0"
    description = "示例处理器插件"
    author = "presearch-team"

    def initialize(self) -> bool:
        return True

    def process(self, results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # 添加处理标记
        results['_processed_by'] = self.name
        return results

    def get_priority(self) -> int:
        return 50


class ExampleOutput(OutputPlugin):
    """示例输出插件"""

    name = "example-output"
    version = "1.0.0"
    description = "示例输出格式插件"
    author = "presearch-team"

    def initialize(self) -> bool:
        return True

    def format(self, data: Any, **kwargs) -> str:
        return f"[EXAMPLE] {data}"

    def get_format_name(self) -> str:
        return "example"


def test_plugins():
    """测试插件基类"""
    print("测试插件基类...")

    # 测试数据源插件
    ds = ExampleDataSource()
    assert ds.initialize() == True
    result = ds.search("test")
    assert result['source'] == 'example'
    print("✓ 数据源插件测试通过")

    # 测试处理器插件
    proc = ExampleProcessor()
    assert proc.initialize() == True
    test_data = {'items': []}
    processed = proc.process(test_data)
    assert '_processed_by' in processed
    print("✓ 处理器插件测试通过")

    # 测试输出插件
    out = ExampleOutput()
    assert out.initialize() == True
    formatted = out.format("test data")
    assert '[EXAMPLE]' in formatted
    print("✓ 输出插件测试通过")

    # 测试插件信息
    info = ds.get_info()
    assert 'name' in info
    print("✓ 插件信息测试通过")

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_plugins()

#!/usr/bin/env python3
"""
插件系统模块
支持数据源插件、处理器插件、输出格式插件
"""

from .base import Plugin, DataSourcePlugin, ProcessorPlugin, OutputPlugin
from .manager import PluginManager

__all__ = [
    'Plugin',
    'DataSourcePlugin',
    'ProcessorPlugin',
    'OutputPlugin',
    'PluginManager'
]

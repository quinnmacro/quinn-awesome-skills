#!/usr/bin/env python3
"""
配置系统模块
使用 pydantic-settings 管理配置
"""

from .settings import PresearchConfig, get_config
from .loader import ConfigLoader
from .presets import PRESETS, get_preset

__all__ = ['PresearchConfig', 'get_config', 'ConfigLoader', 'PRESETS', 'get_preset']

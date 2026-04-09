#!/usr/bin/env python3
"""
预设配置模块
提供针对不同场景的预设配置
"""

from typing import Dict, Any

# 预设配置定义
PRESETS: Dict[str, Dict[str, Any]] = {
    "frontend": {
        "name": "前端开发",
        "description": "适用于前端开发场景，重点关注GitHub和npm",
        "sources": ["github", "npm"],
        "default_per_page": 10,
        "cache_ttl": 86400,
        "default_format": "table",
        "color_enabled": True,
    },
    "backend": {
        "name": "后端开发",
        "description": "适用于后端开发场景，重点关注GitHub、PyPI和Docker",
        "sources": ["github", "pypi", "docker"],
        "default_per_page": 10,
        "cache_ttl": 86400,
        "default_format": "table",
        "color_enabled": True,
    },
    "datascience": {
        "name": "数据科学",
        "description": "适用于数据科学场景，重点关注GitHub、PyPI和arXiv论文",
        "sources": ["github", "pypi", "arxiv"],
        "default_per_page": 5,
        "cache_ttl": 172800,  # 2天，论文更新较慢
        "default_format": "table",
        "color_enabled": True,
    },
    "devops": {
        "name": "DevOps",
        "description": "适用于DevOps场景，重点关注Docker和GitHub",
        "sources": ["docker", "github", "npm"],
        "default_per_page": 10,
        "cache_ttl": 43200,  # 12小时，镜像更新较快
        "default_format": "table",
        "color_enabled": True,
    },
    "minimal": {
        "name": "最小化",
        "description": "最小化配置，仅使用GitHub",
        "sources": ["github"],
        "default_per_page": 5,
        "cache_ttl": 86400,
        "default_format": "table",
        "color_enabled": False,
    },
    "full": {
        "name": "完整",
        "description": "使用所有数据源",
        "sources": ["github", "arxiv", "npm", "pypi", "docker"],
        "default_per_page": 10,
        "cache_ttl": 86400,
        "default_format": "table",
        "color_enabled": True,
    },
}


def get_preset(name: str) -> Dict[str, Any]:
    """
    获取预设配置

    Args:
        name: 预设名称

    Returns:
        预设配置字典，如果不存在则返回空字典
    """
    return PRESETS.get(name, {}).copy()


def list_presets() -> Dict[str, str]:
    """
    列出所有可用的预设

    Returns:
        预设名称和描述的字典
    """
    return {name: info["description"] for name, info in PRESETS.items()}


def apply_preset(config_dict: Dict[str, Any], preset_name: str) -> Dict[str, Any]:
    """
    将预设配置应用到配置字典

    Args:
        config_dict: 当前配置字典
        preset_name: 预设名称

    Returns:
        应用预设后的配置字典
    """
    preset = get_preset(preset_name)
    if not preset:
        return config_dict

    # 创建新字典，预设值作为基础，当前配置覆盖
    result = preset.copy()
    result.update(config_dict)

    return result


def test_presets():
    """测试预设配置"""
    print("测试预设配置...")

    # 测试获取预设
    frontend = get_preset("frontend")
    assert frontend["sources"] == ["github", "npm"]
    print("✓ frontend预设测试通过")

    backend = get_preset("backend")
    assert "pypi" in backend["sources"]
    print("✓ backend预设测试通过")

    # 测试列出预设
    presets = list_presets()
    assert "frontend" in presets
    assert "backend" in presets
    print(f"✓ 列出预设测试通过，共{len(presets)}个预设")

    # 测试应用预设
    config = {"cache_ttl": 3600}
    applied = apply_preset(config, "frontend")
    assert applied["sources"] == ["github", "npm"]
    assert applied["cache_ttl"] == 3600  # 保留原配置
    print("✓ 应用预设测试通过")

    print("\n所有测试通过！")
    print("\n可用预设:")
    for name, desc in presets.items():
        print(f"  - {name}: {desc}")


if __name__ == "__main__":
    test_presets()

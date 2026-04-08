#!/usr/bin/env python3
"""
npm Registry API客户端
用于搜索npm包
"""

import json
import sys
from typing import Dict, List, Any
from urllib.parse import quote

from http_client import HTTPClient, HTTPClientError

class NPMClient:
    """npm Registry API客户端"""

    def __init__(self):
        """初始化"""
        self.http_client = HTTPClient(max_retries=2, timeout=10)
        self.base_url = "https://registry.npmjs.org/-/v1/search"

    def search(self, query: str, size: int = 10) -> Dict[str, Any]:
        """
        搜索npm包

        Args:
            query: 搜索查询
            size: 返回结果数量

        Returns:
            npm API返回的JSON数据，或错误信息
        """
        try:
            # URL编码查询参数
            encoded_query = quote(query, safe='')
            url = f"{self.base_url}?text={encoded_query}&size={size}"

            response = self.http_client.request_json(url)
            return response
        except HTTPClientError as e:
            return {'error': 'npm_api_error', 'message': str(e)}
        except Exception as e:
            return {'error': 'npm_unknown_error', 'message': str(e)}

    def format_results(self, results: Dict[str, Any], query: str) -> str:
        """
        格式化npm搜索结果

        Args:
            results: npm API返回的JSON数据
            query: 搜索查询

        Returns:
            格式化后的Markdown字符串
        """
        if 'error' in results:
            error_msg = results.get('message', '未知错误')
            return f"## npm搜索结果错误\n\n{error_msg}\n"

        if not results or 'objects' not in results or not results['objects']:
            return "## npm搜索结果\n\n未找到相关npm包。\n"

        objects = results['objects']
        total = results.get('total', 0)

        output = [
            f"## npm搜索结果：{query}",
            f"找到 {total} 个相关npm包，显示前 {len(objects)} 个：\n",
            "| 包名 | 版本 | 周下载量 | 描述 |",
            "|------|------|---------|------|"
        ]

        for obj in objects[:10]:  # 限制显示10个结果
            pkg = obj.get('package', {})
            name = pkg.get('name', 'N/A')
            version = pkg.get('version', 'N/A')
            description = pkg.get('description', '无描述') or '无描述'

            # 获取下载量
            downloads = 'N/A'
            if 'npm' in pkg:
                weekly_downloads = pkg['npm'].get('downloads', [{}])[0].get('count')
                if weekly_downloads:
                    if weekly_downloads >= 1000000:
                        downloads = f"{weekly_downloads/1000000:.1f}M/周"
                    elif weekly_downloads >= 1000:
                        downloads = f"{weekly_downloads/1000:.1f}k/周"
                    else:
                        downloads = f"{weekly_downloads}/周"

            # 限制描述长度
            if len(description) > 60:
                description = description[:57] + "..."

            npm_url = f"https://www.npmjs.com/package/{name}"
            output.append(
                f"| [{name}]({npm_url}) | {version} | {downloads} | {description} |"
            )

        output.append("")  # 空行
        return "\n".join(output)

    def get_package_health(self, package_data: Dict[str, Any]) -> str:
        """
        获取npm包健康度评估

        Args:
            package_data: 包数据

        Returns:
            健康度评估字符串
        """
        # 简单健康度评估
        try:
            pkg = package_data.get('package', {})

            # 检查是否有维护信息
            if 'maintainers' in pkg and pkg['maintainers']:
                maintainer_count = len(pkg['maintainers'])
            else:
                maintainer_count = 0

            # 检查版本数量（近似于更新频率）
            if 'versions' in pkg:
                version_count = len(pkg['versions'])
            else:
                version_count = 0

            # 下载量
            weekly_downloads = 0
            if 'npm' in pkg:
                downloads = pkg['npm'].get('downloads', [{}])[0].get('count', 0)
                weekly_downloads = downloads or 0

            # 评估
            if weekly_downloads > 10000 and maintainer_count > 0 and version_count > 10:
                return "🟢 优秀"
            elif weekly_downloads > 1000 and maintainer_count > 0:
                return "🟡 良好"
            elif weekly_downloads > 100:
                return "🟠 一般"
            else:
                return "🔴 新包"
        except Exception:
            return "⚪ 未知"

def test_npm_client():
    """测试npm客户端"""
    client = NPMClient()

    # 测试搜索
    print("测试npm搜索...")
    results = client.search("react", size=3)

    if 'error' in results:
        print(f"错误: {results['message']}")
    else:
        formatted = client.format_results(results, "react")
        print(formatted)

if __name__ == "__main__":
    test_npm_client()
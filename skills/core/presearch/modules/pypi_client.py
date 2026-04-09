#!/usr/bin/env python3
"""
PyPI客户端
用于搜索Python包
注意：PyPI没有官方JSON搜索API，需要解析HTML
"""

import re
import sys
from typing import Dict, List, Any
from urllib.parse import quote

from http_client import HTTPClient, HTTPClientError

class PyPIClient:
    """PyPI客户端（通过HTML解析）"""

    def __init__(self):
        """初始化"""
        self.http_client = HTTPClient(max_retries=2, timeout=10)
        self.base_url = "https://pypi.org/search"

    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        搜索PyPI包

        Args:
            query: 搜索查询
            max_results: 最大结果数量

        Returns:
            解析后的包列表，或错误信息
        """
        try:
            # URL编码查询参数
            encoded_query = quote(query, safe='')
            url = f"{self.base_url}/?q={encoded_query}"

            response = self.http_client.request(url)

            # 解析HTML响应
            packages = self._parse_html_response(response, max_results)

            return {
                'packages': packages,
                'total': len(packages),
                'query': query
            }
        except HTTPClientError as e:
            return {'error': 'pypi_api_error', 'message': str(e)}
        except Exception as e:
            return {'error': 'pypi_unknown_error', 'message': str(e)}

    def _parse_html_response(self, html: str, max_results: int) -> List[Dict[str, Any]]:
        """
        解析PyPI搜索页面的HTML响应

        Args:
            html: HTML响应
            max_results: 最大结果数量

        Returns:
            包字典列表
        """
        packages = []

        # 尝试解析新的HTML结构（2026年PyPI可能已更新）
        # 查找包卡片
        package_patterns = [
            # 尝试匹配包卡片
            r'<a[^>]*class="[^"]*package-snippet[^"]*"[^>]*>.*?<span[^>]*class="[^"]*package-snippet__name[^"]*"[^>]*>([^<]+)</span>.*?<span[^>]*class="[^"]*package-snippet__version[^"]*"[^>]*>([^<]+)</span>.*?<p[^>]*class="[^"]*package-snippet__description[^"]*"[^>]*>([^<]*)</p>',
            # 备用模式：更宽松的匹配
            r'<a[^>]*href="/project/([^/"]+)/"[^>]*>.*?<span[^>]*>([^<]+)</span>.*?<span[^>]*>([^<]+)</span>.*?<p[^>]*>([^<]*)</p>'
        ]

        for pattern in package_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                for match in matches[:max_results]:
                    if len(match) >= 3:
                        name = match[0].strip()
                        version = match[1].strip() if len(match) > 1 else 'N/A'
                        description = match[2].strip() if len(match) > 2 else '无描述'

                        packages.append({
                            'name': name,
                            'version': version,
                            'description': description,
                            'url': f"https://pypi.org/project/{name}/"
                        })
                break

        # 如果未找到匹配，尝试更简单的解析
        if not packages:
            # 查找项目链接
            project_links = re.findall(r'href="/project/([^/"]+)/"', html)
            for name in project_links[:max_results]:
                packages.append({
                    'name': name,
                    'version': 'N/A',
                    'description': '无描述',
                    'url': f"https://pypi.org/project/{name}/"
                })

        return packages

    def format_results(self, results: Dict[str, Any], query: str) -> str:
        """
        格式化PyPI搜索结果

        Args:
            results: 解析后的包数据
            query: 搜索查询

        Returns:
            格式化后的Markdown字符串
        """
        if 'error' in results:
            error_msg = results.get('message', '未知错误')
            return f"## PyPI搜索结果错误\n\n{error_msg}\n"

        packages = results.get('packages', [])
        total = results.get('total', 0)

        if not packages:
            return "## PyPI搜索结果\n\n未找到相关Python包。\n"

        output = [
            f"## PyPI搜索结果：{query}",
            f"找到 {total} 个相关Python包，显示前 {len(packages)} 个：\n",
            "| 包名 | 版本 | 描述 |",
            "|------|------|------|"
        ]

        for pkg in packages[:10]:  # 限制显示10个结果
            name = pkg.get('name', 'N/A')
            version = pkg.get('version', 'N/A')
            description = pkg.get('description', '无描述') or '无描述'
            url = pkg.get('url', f"https://pypi.org/project/{name}/")

            # 限制描述长度
            if len(description) > 60:
                description = description[:57] + "..."

            output.append(
                f"| [{name}]({url}) | {version} | {description} |"
            )

        output.append("")  # 空行
        return "\n".join(output)

    def get_package_health(self, package_data: Dict[str, Any]) -> str:
        """
        获取PyPI包健康度评估（简化版）

        Args:
            package_data: 包数据

        Returns:
            健康度评估字符串
        """
        # 由于HTML解析限制，这里使用简化评估
        version = package_data.get('version', '')

        if version and version != 'N/A':
            # 有版本信息，假设是活跃的
            return "🟡 良好"
        else:
            return "⚪ 未知"

def test_pypi_client():
    """测试PyPI客户端"""
    client = PyPIClient()

    # 测试搜索
    print("测试PyPI搜索...")
    results = client.search("django", max_results=3)

    if 'error' in results:
        print(f"错误: {results['message']}")
    else:
        formatted = client.format_results(results, "django")
        print(formatted)

if __name__ == "__main__":
    test_pypi_client()
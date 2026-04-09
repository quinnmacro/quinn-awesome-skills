#!/usr/bin/env python3
"""
Docker Hub API客户端
用于搜索Docker镜像
"""

import json
import sys
from typing import Dict, List, Any
from urllib.parse import quote

from http_client import HTTPClient, HTTPClientError

class DockerClient:
    """Docker Hub API客户端"""

    def __init__(self):
        """初始化"""
        self.http_client = HTTPClient(max_retries=2, timeout=10)
        self.base_url = "https://hub.docker.com/v2/search/repositories"

    def search(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """
        搜索Docker镜像

        Args:
            query: 搜索查询
            page_size: 每页结果数量

        Returns:
            Docker Hub API返回的JSON数据，或错误信息
        """
        try:
            # URL编码查询参数
            encoded_query = quote(query, safe='')
            url = f"{self.base_url}?query={encoded_query}&page_size={page_size}"

            response = self.http_client.request_json(url)
            return response
        except HTTPClientError as e:
            return {'error': 'docker_api_error', 'message': str(e)}
        except Exception as e:
            return {'error': 'docker_unknown_error', 'message': str(e)}

    def format_results(self, results: Dict[str, Any], query: str) -> str:
        """
        格式化Docker搜索结果

        Args:
            results: Docker Hub API返回的JSON数据
            query: 搜索查询

        Returns:
            格式化后的Markdown字符串
        """
        if 'error' in results:
            error_msg = results.get('message', '未知错误')
            return f"## Docker Hub搜索结果错误\n\n{error_msg}\n"

        if not results or 'results' not in results or not results['results']:
            return "## Docker Hub搜索结果\n\n未找到相关Docker镜像。\n"

        items = results['results']
        total = results.get('count', 0)

        output = [
            f"## Docker Hub搜索结果：{query}",
            f"找到 {total} 个相关Docker镜像，显示前 {len(items)} 个：\n",
            "| 镜像名称 | Pulls | Stars | 描述 |",
            "|----------|-------|-------|------|"
        ]

        for item in items[:10]:  # 限制显示10个结果
            name = item.get('repo_name', 'N/A')
            pull_count = item.get('pull_count', 0)
            star_count = item.get('star_count', 0)
            description = item.get('short_description', '无描述') or '无描述'

            # 格式化pull次数
            if pull_count >= 1000000:
                pulls = f"{pull_count/1000000:.1f}M"
            elif pull_count >= 1000:
                pulls = f"{pull_count/1000:.1f}k"
            else:
                pulls = str(pull_count)

            # 格式化star数量
            stars = str(star_count)

            # 限制描述长度
            if len(description) > 60:
                description = description[:57] + "..."

            docker_url = f"https://hub.docker.com/r/{name}"
            output.append(
                f"| [{name}]({docker_url}) | {pulls} | {stars} | {description} |"
            )

        output.append("")  # 空行
        return "\n".join(output)

    def get_image_health(self, image_data: Dict[str, Any]) -> str:
        """
        获取Docker镜像健康度评估

        Args:
            image_data: 镜像数据

        Returns:
            健康度评估字符串
        """
        try:
            pull_count = image_data.get('pull_count', 0)
            star_count = image_data.get('star_count', 0)
            is_automated = image_data.get('is_automated', False)
            is_official = image_data.get('is_official', False)

            # 评估逻辑
            if is_official:
                return "🟢 官方"  # 绿色，官方镜像
            elif pull_count > 1000000:
                return "🟢 优秀"  # 绿色，非常流行
            elif pull_count > 100000 or star_count > 100:
                return "🟡 良好"  # 黄色，比较流行
            elif pull_count > 1000:
                return "🟠 一般"  # 橙色，有一定使用量
            elif is_automated:
                return "🟠 自动构建"  # 橙色，有自动构建
            else:
                return "🔴 新镜像"  # 红色，新镜像
        except Exception:
            return "⚪ 未知"

def test_docker_client():
    """测试Docker客户端"""
    client = DockerClient()

    # 测试搜索
    print("测试Docker Hub搜索...")
    results = client.search("nginx", page_size=3)

    if 'error' in results:
        print(f"错误: {results['message']}")
    else:
        formatted = client.format_results(results, "nginx")
        print(formatted)

if __name__ == "__main__":
    test_docker_client()
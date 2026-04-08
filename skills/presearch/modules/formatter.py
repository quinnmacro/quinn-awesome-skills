#!/usr/bin/env python3
"""
输出格式化模块
用于格式化搜索结果
"""

import datetime
from typing import Dict, List, Any

class ResultFormatter:
    """结果格式化器"""

    @staticmethod
    def format_timestamp(timestamp_str):
        """
        格式化时间戳

        Args:
            timestamp_str: ISO格式时间字符串

        Returns:
            格式化后的时间字符串
        """
        if not timestamp_str:
            return "未知"

        try:
            # 尝试解析ISO格式时间
            dt = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            # 如果解析失败，返回原始值
            return str(timestamp_str)

    @staticmethod
    def format_stars(stars):
        """
        格式化star数量

        Args:
            stars: star数量

        Returns:
            格式化的star字符串
        """
        if stars is None:
            return "0"

        try:
            stars_int = int(stars)
            if stars_int >= 1000:
                return f"{stars_int/1000:.1f}k"
            else:
                return str(stars_int)
        except (ValueError, TypeError):
            return str(stars)

    @staticmethod
    def get_health_indicator(project_data):
        """
        获取项目健康度指示器

        Args:
            project_data: 项目数据

        Returns:
            健康度指示器字符串
        """
        # 简单健康度评估
        stars = project_data.get('stars', 0) or project_data.get('stargazers_count', 0)
        updated_at = project_data.get('updated_at') or project_data.get('last_updated')

        try:
            stars_int = int(stars)
        except (ValueError, TypeError):
            stars_int = 0

        # 评估活跃度
        is_active = False
        if updated_at:
            try:
                dt = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_ago = (datetime.datetime.now(datetime.timezone.utc) - dt).days
                is_active = days_ago < 180  # 6个月内更新过
            except (ValueError, AttributeError):
                pass

        # 综合评估
        if stars_int >= 1000 and is_active:
            return "🟢 优秀"  # 绿色
        elif stars_int >= 100 and is_active:
            return "🟡 良好"  # 黄色
        elif stars_int >= 10:
            return "🟠 一般"  # 橙色
        else:
            return "🔴 新项目"  # 红色

    @staticmethod
    def format_github_results(results, query):
        """
        格式化GitHub搜索结果

        Args:
            results: GitHub API返回的JSON数据
            query: 搜索查询

        Returns:
            格式化后的Markdown字符串
        """
        if not results or 'items' not in results or not results['items']:
            return "## GitHub搜索结果\n\n未找到相关项目。\n"

        items = results['items']
        total_count = results.get('total_count', 0)

        output = [
            f"## GitHub搜索结果：{query}",
            f"找到 {total_count} 个相关项目，显示前 {len(items)} 个：\n",
            "| 项目 | Stars | 最近更新 | 健康度 | 描述 |",
            "|------|-------|---------|--------|------|"
        ]

        for item in items[:10]:  # 限制显示10个结果
            name = item.get('full_name', 'N/A')
            url = item.get('html_url', '#')
            stars = ResultFormatter.format_stars(item.get('stargazers_count'))
            updated = ResultFormatter.format_timestamp(item.get('updated_at'))
            description = item.get('description', '无描述') or '无描述'
            health = ResultFormatter.get_health_indicator(item)

            # 限制描述长度
            if len(description) > 60:
                description = description[:57] + "..."

            output.append(
                f"| [{name}]({url}) | {stars} | {updated} | {health} | {description} |"
            )

        output.append("")  # 空行
        return "\n".join(output)

    @staticmethod
    def format_arxiv_results(results, query):
        """
        格式化arXiv搜索结果

        Args:
            results: arXiv API返回的XML数据（已解析为字典列表）
            query: 搜索查询

        Returns:
            格式化后的Markdown字符串
        """
        if not results:
            return "## arXiv搜索结果\n\n未找到相关论文。\n"

        output = [
            f"## arXiv搜索结果：{query}",
            f"找到 {len(results)} 篇相关论文：\n",
            "| 标题 | 作者 | 发表日期 | 链接 |",
            "|------|------|---------|------|"
        ]

        for paper in results[:5]:  # 限制显示5个结果
            title = paper.get('title', '无标题')
            authors = paper.get('authors', '未知作者')
            published = ResultFormatter.format_timestamp(paper.get('published'))
            link = paper.get('link', '#')

            # 限制标题长度
            if len(title) > 80:
                title = title[:77] + "..."

            # 限制作者长度
            if isinstance(authors, list):
                authors_str = ', '.join(authors)
            else:
                authors_str = str(authors)

            if len(authors_str) > 40:
                authors_str = authors_str[:37] + "..."

            output.append(
                f"| {title} | {authors_str} | {published} | [链接]({link}) |"
            )

        output.append("")  # 空行
        return "\n".join(output)

    @staticmethod
    def format_summary(github_count, arxiv_count):
        """
        格式化搜索摘要

        Args:
            github_count: GitHub结果数量
            arxiv_count: arXiv结果数量

        Returns:
            摘要字符串
        """
        total = github_count + arxiv_count

        if total == 0:
            return "## 总结\n\n未找到任何相关资源。\n"

        output = ["## 总结"]

        if github_count > 0:
            output.append(f"- 找到 {github_count} 个GitHub项目")
        if arxiv_count > 0:
            output.append(f"- 找到 {arxiv_count} 篇arXiv论文")

        output.append("\n### 建议")
        if github_count >= 3:
            output.append("✅ **有多个成熟项目可供选择**，建议：")
            output.append("1. 查看前3个项目的README和文档")
            output.append("2. 比较项目活跃度和社区支持")
            output.append("3. 选择最适合需求的项目")
        elif github_count > 0:
            output.append("⚠️ **找到少量相关项目**，建议：")
            output.append("1. 仔细评估项目是否满足需求")
            output.append("2. 考虑自行开发或寻找替代方案")
        else:
            output.append("🔍 **未找到现成项目**，建议：")
            output.append("1. 考虑自行开发")
            output.append("2. 搜索相关论文获取算法思路")
            output.append("3. 在技术社区寻求帮助")

        output.append("")  # 空行
        return "\n".join(output)

def test_formatter():
    """测试格式化器"""
    # 测试数据
    test_timestamp = "2026-03-15T10:30:00Z"
    print(f"格式化时间戳: {ResultFormatter.format_timestamp(test_timestamp)}")

    print(f"格式化stars: {ResultFormatter.format_stars(1234)}")
    print(f"格式化stars: {ResultFormatter.format_stars(42)}")

    test_project = {
        'stars': 1500,
        'updated_at': '2026-03-15T10:30:00Z'
    }
    print(f"健康度指示器: {ResultFormatter.get_health_indicator(test_project)}")

if __name__ == "__main__":
    test_formatter()
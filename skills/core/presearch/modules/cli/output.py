#!/usr/bin/env python3
"""
输出格式化模块
使用 rich 库美化输出
"""

import json
import csv
import io
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_console(color_enabled: bool = True) -> Any:
    """
    获取 Console 实例

    Args:
        color_enabled: 是否启用颜色

    Returns:
        Console 实例或标准输出
    """
    if RICH_AVAILABLE:
        return Console(color_system="auto" if color_enabled else None)
    return None


def print_table(
    data: List[Dict[str, Any]],
    columns: List[str],
    headers: Optional[Dict[str, str]] = None,
    title: Optional[str] = None,
    color_enabled: bool = True
) -> str:
    """
    打印表格

    Args:
        data: 数据列表
        columns: 列名列表
        headers: 列标题映射
        title: 表格标题
        color_enabled: 是否启用颜色

    Returns:
        格式化后的表格字符串
    """
    if not RICH_AVAILABLE or not color_enabled:
        # 回退到简单表格
        return _simple_table(data, columns, headers, title)

    console = get_console(color_enabled)
    table = Table(title=title, show_header=True, header_style="bold magenta")

    # 添加列
    for col in columns:
        header = headers.get(col, col) if headers else col
        table.add_column(header)

    # 添加行
    for row in data:
        row_data = [str(row.get(col, '')) for col in columns]
        table.add_row(*row_data)

    # 捕获输出
    output = io.StringIO()
    console = Console(file=output, color_system="auto" if color_enabled else None)
    console.print(table)
    return output.getvalue()


def _simple_table(
    data: List[Dict[str, Any]],
    columns: List[str],
    headers: Optional[Dict[str, str]] = None,
    title: Optional[str] = None
) -> str:
    """简单表格实现（无rich时回退）"""
    lines = []

    if title:
        lines.append(f"## {title}")
        lines.append("")

    # 表头
    header_cols = [headers.get(col, col) if headers else col for col in columns]
    lines.append(" | ".join(header_cols))
    lines.append("-" * len(" | ".join(header_cols)))

    # 数据行
    for row in data:
        row_data = [str(row.get(col, '')) for col in columns]
        lines.append(" | ".join(row_data))

    return "\n".join(lines)


def print_json(data: Any, indent: int = 2) -> str:
    """
    打印 JSON 格式

    Args:
        data: 数据
        indent: 缩进空格数

    Returns:
        JSON 字符串
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def print_csv(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
    """
    打印 CSV 格式

    Args:
        data: 数据列表
        columns: 列名列表，默认使用所有键

    Returns:
        CSV 字符串
    """
    if not data:
        return ""

    if columns is None:
        columns = list(data[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def format_output(
    results: Dict[str, Any],
    format_type: str = 'table',
    color_enabled: bool = True
) -> str:
    """
    格式化输出

    Args:
        results: 搜索结果
        format_type: 输出格式（table/json/csv/markdown）
        color_enabled: 是否启用颜色

    Returns:
        格式化后的字符串
    """
    if format_type == 'json':
        return print_json(results)

    if format_type == 'csv':
        # 提取可表格化的数据
        if 'items' in results:
            return print_csv(results['items'])
        return print_csv([results])

    if format_type == 'markdown':
        return _format_markdown(results)

    # 默认表格格式
    return _format_table(results, color_enabled)


def _format_table(results: Dict[str, Any], color_enabled: bool) -> str:
    """格式化为表格"""
    output_parts = []

    for source, data in results.items():
        if isinstance(data, dict) and 'items' in data:
            items = data['items']
            if items:
                output_parts.append(f"\n## {source.upper()} 搜索结果")
                # 简化显示，只显示关键字段
                simplified = []
                for item in items[:10]:  # 只显示前10个
                    simplified.append({
                        'name': item.get('name', item.get('full_name', 'N/A')),
                        'stars': item.get('stargazers_count', item.get('stars', 'N/A')),
                        'description': item.get('description', 'N/A')[:50] + '...'
                    })

                table_str = print_table(
                    simplified,
                    ['name', 'stars', 'description'],
                    color_enabled=color_enabled
                )
                output_parts.append(table_str)

    return "\n".join(output_parts)


def _format_markdown(results: Dict[str, Any]) -> str:
    """格式化为 Markdown"""
    lines = []

    for source, data in results.items():
        lines.append(f"## {source.upper()}")

        if isinstance(data, dict) and 'items' in data:
            for item in data['items'][:5]:  # 只显示前5个
                name = item.get('name', item.get('full_name', 'Unknown'))
                url = item.get('html_url', item.get('url', ''))
                desc = item.get('description', 'No description')

                lines.append(f"\n### {name}")
                lines.append(f"{desc}")
                if url:
                    lines.append(f"[链接]({url})")

        lines.append("")

    return "\n".join(lines)


def print_success(message: str, color_enabled: bool = True):
    """打印成功消息"""
    if RICH_AVAILABLE and color_enabled:
        console = get_console(color_enabled)
        console.print(f"✓ {message}", style="green")
    else:
        print(f"✓ {message}")


def print_error(message: str, color_enabled: bool = True):
    """打印错误消息"""
    if RICH_AVAILABLE and color_enabled:
        console = get_console(color_enabled)
        console.print(f"✗ {message}", style="red")
    else:
        print(f"✗ {message}")


def print_warning(message: str, color_enabled: bool = True):
    """打印警告消息"""
    if RICH_AVAILABLE and color_enabled:
        console = get_console(color_enabled)
        console.print(f"⚠ {message}", style="yellow")
    else:
        print(f"⚠ {message}")


def print_info(message: str, color_enabled: bool = True):
    """打印信息消息"""
    if RICH_AVAILABLE and color_enabled:
        console = get_console(color_enabled)
        console.print(f"ℹ {message}", style="blue")
    else:
        print(f"ℹ {message}")


def test_output():
    """测试输出格式化"""
    print("测试输出格式化...")

    # 测试数据
    test_data = [
        {'name': 'fastapi', 'stars': 50000, 'description': 'Fast web framework'},
        {'name': 'django', 'stars': 60000, 'description': 'Full-stack framework'},
        {'name': 'flask', 'stars': 55000, 'description': 'Micro framework'},
    ]

    # 测试表格
    table_str = print_table(
        test_data,
        ['name', 'stars', 'description'],
        title="Python Web Frameworks"
    )
    assert 'fastapi' in table_str
    print("✓ 表格输出测试通过")

    # 测试 JSON
    json_str = print_json(test_data)
    assert '"name": "fastapi"' in json_str
    print("✓ JSON输出测试通过")

    # 测试 CSV
    csv_str = print_csv(test_data)
    assert 'fastapi' in csv_str
    print("✓ CSV输出测试通过")

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_output()

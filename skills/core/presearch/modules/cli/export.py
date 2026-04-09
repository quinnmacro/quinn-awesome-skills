#!/usr/bin/env python3
"""
结果导出模块
支持多种格式导出搜索结果
"""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List


def export_to_json(data: Any, filepath: str) -> bool:
    """
    导出为 JSON 文件

    Args:
        data: 要导出的数据
        filepath: 文件路径

    Returns:
        是否导出成功
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except (IOError, TypeError) as e:
        print(f"导出JSON失败: {e}")
        return False


def export_to_csv(data: List[Dict], filepath: str, columns: List[str] = None) -> bool:
    """
    导出为 CSV 文件

    Args:
        data: 要导出的数据列表
        filepath: 文件路径
        columns: 指定列名，默认使用所有键

    Returns:
        是否导出成功
    """
    try:
        if not data:
            print("没有数据可导出")
            return False

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if columns is None:
            columns = list(data[0].keys())

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

        return True
    except (IOError, TypeError) as e:
        print(f"导出CSV失败: {e}")
        return False


def export_to_markdown(data: Any, filepath: str) -> bool:
    """
    导出为 Markdown 文件

    Args:
        data: 要导出的数据
        filepath: 文件路径

    Returns:
        是否导出成功
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        lines.append("# Presearch 搜索结果")
        lines.append("")
        lines.append(f"生成时间: {__import__('datetime').datetime.now().isoformat()}")
        lines.append("")

        if isinstance(data, dict):
            for source, results in data.items():
                lines.append(f"## {source.upper()}")
                lines.append("")

                if isinstance(results, dict) and 'items' in results:
                    for item in results['items']:
                        name = item.get('name', item.get('full_name', 'Unknown'))
                        url = item.get('html_url', item.get('url', ''))
                        desc = item.get('description', 'No description')

                        lines.append(f"### {name}")
                        lines.append(f"{desc}")
                        if url:
                            lines.append(f"[链接]({url})")
                        lines.append("")

        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return True
    except (IOError, TypeError) as e:
        print(f"导出Markdown失败: {e}")
        return False


def export_results(
    data: Any,
    filepath: str,
    format_type: str = 'json'
) -> bool:
    """
    导出搜索结果

    Args:
        data: 要导出的数据
        filepath: 文件路径
        format_type: 导出格式（json/csv/markdown）

    Returns:
        是否导出成功
    """
    format_type = format_type.lower()

    if format_type == 'json':
        return export_to_json(data, filepath)
    elif format_type == 'csv':
        if isinstance(data, dict) and 'items' in data:
            return export_to_csv(data['items'], filepath)
        elif isinstance(data, list):
            return export_to_csv(data, filepath)
        else:
            print("CSV导出需要列表数据")
            return False
    elif format_type in ['markdown', 'md']:
        return export_to_markdown(data, filepath)
    else:
        print(f"不支持的导出格式: {format_type}")
        return False


def test_export():
    """测试导出功能"""
    import tempfile
    import shutil

    print("测试导出功能...")

    # 使用临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 测试数据
        test_data = {
            'github': {
                'items': [
                    {'name': 'fastapi', 'stars': 50000, 'description': 'Fast web framework'},
                    {'name': 'django', 'stars': 60000, 'description': 'Full-stack framework'},
                ]
            }
        }

        # 测试 JSON 导出
        json_path = f"{temp_dir}/results.json"
        assert export_to_json(test_data, json_path) == True
        assert Path(json_path).exists()
        print("✓ JSON导出测试通过")

        # 测试 CSV 导出
        csv_path = f"{temp_dir}/results.csv"
        assert export_to_csv(test_data['github']['items'], csv_path) == True
        assert Path(csv_path).exists()
        print("✓ CSV导出测试通过")

        # 测试 Markdown 导出
        md_path = f"{temp_dir}/results.md"
        assert export_results(test_data, md_path, 'markdown') == True
        assert Path(md_path).exists()
        print("✓ Markdown导出测试通过")

        print("\n所有测试通过！")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_export()

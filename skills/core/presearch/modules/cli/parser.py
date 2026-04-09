#!/usr/bin/env python3
"""
CLI 参数解析模块
使用 argparse 构建命令行接口
"""

import argparse
from typing import Optional, List


def create_parser() -> argparse.ArgumentParser:
    """
    创建参数解析器

    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='presearch',
        description='Presearch - 智能开发资源搜索工具',
        epilog='示例: presearch "Python web framework" --preset backend',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 位置参数：搜索查询
    parser.add_argument(
        'query',
        nargs='?',
        help='搜索关键词'
    )

    # 数据源选项
    parser.add_argument(
        '-s', '--sources',
        nargs='+',
        choices=['github', 'arxiv', 'npm', 'pypi', 'docker'],
        metavar='SOURCE',
        help='指定数据源（默认：全部）'
    )

    # 预设配置
    parser.add_argument(
        '--preset',
        metavar='PRESET',
        help='使用预设配置（使用 "list" 查看所有可用预设）'
    )

    # 输出格式
    parser.add_argument(
        '-f', '--format',
        choices=['table', 'json', 'csv', 'markdown', 'emoji', 'meme', 'poetry', 'fortune'],
        default='table',
        help='输出格式（默认：table，趣味格式：emoji/meme/poetry/fortune）'
    )

    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='输出到文件'
    )

    # 缓存选项
    cache_group = parser.add_argument_group('缓存选项')
    cache_group.add_argument(
        '--no-cache',
        action='store_true',
        help='禁用缓存'
    )
    cache_group.add_argument(
        '--cache-stats',
        action='store_true',
        help='显示缓存统计'
    )
    cache_group.add_argument(
        '--clear-cache',
        action='store_true',
        help='清空缓存'
    )
    cache_group.add_argument(
        '--cache-dir',
        action='store_true',
        help='显示缓存目录'
    )

    # 配置选项
    config_group = parser.add_argument_group('配置选项')
    config_group.add_argument(
        '--config',
        metavar='FILE',
        help='指定配置文件'
    )
    config_group.add_argument(
        '--init-config',
        action='store_true',
        help='初始化配置文件'
    )
    config_group.add_argument(
        '--config-path',
        action='store_true',
        help='显示配置文件路径'
    )

    # 搜索选项
    search_group = parser.add_argument_group('搜索选项')
    search_group.add_argument(
        '-n', '--limit',
        type=int,
        default=10,
        help='每页结果数量（默认：10）'
    )
    search_group.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='请求超时时间（秒，默认：10）'
    )

    # 历史记录选项
    history_group = parser.add_argument_group('历史记录选项')
    history_group.add_argument(
        '-H', '--history',
        action='store_true',
        help='显示搜索历史'
    )
    history_group.add_argument(
        '--history-stats',
        action='store_true',
        help='显示历史统计'
    )
    history_group.add_argument(
        '--clear-history',
        action='store_true',
        help='清空搜索历史'
    )
    history_group.add_argument(
        '--history-trends',
        action='store_true',
        help='显示搜索趋势'
    )

    # 运行模式
    mode_group = parser.add_argument_group('运行模式')
    mode_group.add_argument(
        '--tui',
        action='store_true',
        help='启动交互式 TUI 界面'
    )
    mode_group.add_argument(
        '--agent',
        action='store_true',
        help='Agent 模式，输出稳定 JSON 格式（适用于脚本/CI/AI 集成）'
    )

    # Agent 选项
    agent_group = parser.add_argument_group('Agent 选项')
    agent_group.add_argument(
        '--pretty',
        action='store_true',
        help='Agent 模式下美化 JSON 输出'
    )

    # 其他选项
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用颜色输出'
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='显示版本信息'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    return parser


def parse_args(args: Optional[List[str]] = None):
    """
    解析命令行参数

    Args:
        args: 命令行参数列表，默认为 sys.argv

    Returns:
        解析后的参数命名空间
    """
    parser = create_parser()
    return parser.parse_args(args)


def test_parser():
    """测试参数解析器"""
    print("测试参数解析器...")

    # 测试基本搜索
    args = parse_args(['Python web framework'])
    assert args.query == 'Python web framework'
    print("✓ 基本搜索参数测试通过")

    # 测试数据源选项
    args = parse_args(['React', '-s', 'github', 'npm'])
    assert args.sources == ['github', 'npm']
    print("✓ 数据源选项测试通过")

    # 测试预设配置
    args = parse_args(['ML', '--preset', 'datascience'])
    assert args.preset == 'datascience'
    print("✓ 预设配置测试通过")

    # 测试输出格式
    args = parse_args(['Docker', '-f', 'json', '-o', 'results.json'])
    assert args.format == 'json'
    assert args.output == 'results.json'
    print("✓ 输出格式测试通过")

    # 测试缓存选项
    args = parse_args(['--cache-stats'])
    assert args.cache_stats == True
    print("✓ 缓存选项测试通过")

    # 测试配置选项
    args = parse_args(['--init-config'])
    assert args.init_config == True
    print("✓ 配置选项测试通过")

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_parser()

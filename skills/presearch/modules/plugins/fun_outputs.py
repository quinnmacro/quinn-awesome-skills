#!/usr/bin/env python3
"""
表情包输出插件
让搜索结果变得更有趣
"""

try:
    from plugins.base import OutputPlugin
except ImportError:
    from base import OutputPlugin


class EmojiOutputPlugin(OutputPlugin):
    """
    表情包输出插件

    用表情符号装饰搜索结果
    """

    name = "emoji-output"
    version = "1.0.0"
    description = "用表情符号让搜索结果更有趣"
    author = "presearch-fun"

    # 健康度对应的表情
    HEALTH_EMOJI = {
        'excellent': '🌟',
        'good': '✨',
        'fair': '📊',
        'poor': '🌱',
        'unknown': '❓'
    }

    # 数据源对应的表情
    SOURCE_EMOJI = {
        'github': '🐙',
        'arxiv': '📄',
        'npm': '📦',
        'pypi': '🐍',
        'docker': '🐳'
    }

    def initialize(self) -> bool:
        return True

    def format(self, data, **kwargs):
        """格式化为表情包风格"""
        lines = ["🚀 Presearch 搜索结果 🚀", ""]

        if isinstance(data, dict):
            for source, results in data.items():
                emoji = self.SOURCE_EMOJI.get(source, '🔍')
                lines.append(f"{emoji} {source.upper()}")

                if isinstance(results, dict) and 'items' in results:
                    for i, item in enumerate(results['items'][:5], 1):
                        name = item.get('name', item.get('full_name', 'Unknown'))
                        stars = item.get('stargazers_count', item.get('stars', 0))
                        desc = item.get('description', 'No description')

                        # 根据stars选择表情
                        if stars > 10000:
                            star_emoji = '🔥'
                        elif stars > 1000:
                            star_emoji = '⭐'
                        elif stars > 100:
                            star_emoji = '✨'
                        else:
                            star_emoji = '💫'

                        lines.append(f"  {i}. {star_emoji} {name} ({stars} stars)")
                        lines.append(f"     📝 {desc[:50]}...")

                lines.append("")

        return "\n".join(lines)

    def get_format_name(self) -> str:
        return "emoji"


class MemeOutputPlugin(OutputPlugin):
    """
    梗图风格输出插件

    用程序员梗的方式展示结果
    """

    name = "meme-output"
    version = "1.0.0"
    description = "用程序员梗的方式展示搜索结果"
    author = "presearch-fun"

    # 梗图模板
    TEMPLATES = [
        "当你找到 {name} 时：这简直就是我想要的！",
        "{name}：听说你在找框架？",
        "使用 {name} 前 🐛 使用后 ✨",
        "{name}：我们不一样，不一样...",
        "当你发现 {name} 有 {stars} stars 时：震惊！",
    ]

    def initialize(self) -> bool:
        import random
        self.random = random
        return True

    def format(self, data, **kwargs):
        """格式化为梗图风格"""
        lines = ["😎 程序员专属搜索结果 😎", ""]

        if isinstance(data, dict):
            for source, results in data.items():
                lines.append(f"📌 {source.upper()}")

                if isinstance(results, dict) and 'items' in results:
                    for item in results['items'][:3]:
                        name = item.get('name', item.get('full_name', 'Unknown'))
                        stars = item.get('stargazers_count', item.get('stars', 0))

                        # 随机选择一个模板
                        template = self.random.choice(self.TEMPLATES)
                        meme = template.format(name=name, stars=stars)

                        lines.append(f"  💭 {meme}")
                        lines.append(f"     👍 {stars} 人觉得很赞")
                        lines.append("")

        lines.append("---")
        lines.append("🎉 这就是程序员的快乐！")

        return "\n".join(lines)

    def get_format_name(self) -> str:
        return "meme"


class PoetryOutputPlugin(OutputPlugin):
    """
    诗意输出插件

    用诗歌的方式描述技术项目
    """

    name = "poetry-output"
    version = "1.0.0"
    description = "用诗歌的方式描述技术项目"
    author = "presearch-fun"

    def initialize(self) -> bool:
        return True

    def format(self, data, **kwargs):
        """格式化为诗歌"""
        lines = [
            "🎭 代码的诗篇 🎭",
            "",
            "在数字的海洋里，",
            "我寻找着答案的光芒，",
            "每一个项目都是一首诗，",
            "每一行代码都在歌唱。",
            ""
        ]

        if isinstance(data, dict):
            for source, results in data.items():
                if isinstance(results, dict) and 'items' in results:
                    for item in results['items'][:3]:
                        name = item.get('name', 'Unknown')
                        desc = item.get('description', '')
                        stars = item.get('stargazers_count', item.get('stars', 0))

                        # 生成一首小诗
                        lines.append(f"《{name}》")
                        lines.append(f"  你是{source}世界的明珠，")
                        lines.append(f"  {stars}颗星星为你闪耀，")
                        if desc:
                            lines.append(f"  人们说：{desc[:30]}...")
                        lines.append("  在开源的天空下，")
                        lines.append("  你静静地绽放。")
                        lines.append("")

        lines.append("---")
        lines.append("✍️  技术，本就是最美的诗")

        return "\n".join(lines)

    def get_format_name(self) -> str:
        return "poetry"


class FortuneCookieOutputPlugin(OutputPlugin):
    """
    幸运饼干输出插件

    给每个结果一个 fortune cookie 式的预言
    """

    name = "fortune-output"
    version = "1.0.0"
    description = "给每个结果一个幸运预言"
    author = "presearch-fun"

    FORTUNES = [
        "这个项目将为你带来代码的宁静 🧘",
        "使用它，bug 将远离你 🐛➡️✨",
        "星星说：这是你的命中注定 ⭐",
        "今天适合学习这个框架 📚",
        "你的代码将因此而优雅 💎",
        "这是开源社区送给你的礼物 🎁",
        "掌握它，你将变得更强 💪",
        "这个项目会给你带来灵感 💡",
        "你的项目将因此腾飞 🚀",
        "这是程序员的最佳选择 🏆",
    ]

    def initialize(self) -> bool:
        import random
        self.random = random
        return True

    def format(self, data, **kwargs):
        """格式化为幸运饼干风格"""
        lines = ["🥠 幸运代码饼干 🥠", ""]

        if isinstance(data, dict):
            for source, results in data.items():
                if isinstance(results, dict) and 'items' in results:
                    for item in results['items'][:5]:
                        name = item.get('name', 'Unknown')
                        fortune = self.random.choice(self.FORTUNES)

                        lines.append("┌" + "─" * 40 + "┐")
                        lines.append(f"│ 🥠 {name:<35} │")
                        lines.append("├" + "─" * 40 + "┤")
                        lines.append(f"│ {fortune:<38} │")
                        lines.append("└" + "─" * 40 + "┘")
                        lines.append("")

        lines.append("🍀 愿代码与你同在")

        return "\n".join(lines)

    def get_format_name(self) -> str:
        return "fortune"


# 测试
if __name__ == "__main__":
    print("测试趣味输出插件...")

    # 测试数据
    test_data = {
        'github': {
            'items': [
                {'name': 'fastapi', 'stargazers_count': 50000, 'description': 'Fast web framework'},
                {'name': 'django', 'stargazers_count': 60000, 'description': 'Full-stack framework'},
            ]
        }
    }

    # 测试表情包插件
    emoji = EmojiOutputPlugin()
    emoji.initialize()
    print(emoji.format(test_data))
    print("\n" + "="*50 + "\n")

    # 测试梗图插件
    meme = MemeOutputPlugin()
    meme.initialize()
    print(meme.format(test_data))
    print("\n" + "="*50 + "\n")

    # 测试诗歌插件
    poetry = PoetryOutputPlugin()
    poetry.initialize()
    print(poetry.format(test_data))
    print("\n" + "="*50 + "\n")

    # 测试幸运饼干插件
    fortune = FortuneCookieOutputPlugin()
    fortune.initialize()
    print(fortune.format(test_data))

    print("\n✓ 所有趣味插件测试通过！")

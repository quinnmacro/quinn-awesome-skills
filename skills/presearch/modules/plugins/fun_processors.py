#!/usr/bin/env python3
"""
毒舌代码评论插件
用程序员的方式"吐槽"搜索结果
"""

try:
    from plugins.base import ProcessorPlugin
except ImportError:
    from base import ProcessorPlugin


class RoastProcessorPlugin(ProcessorPlugin):
    """
    毒舌吐槽处理器

    给每个项目一个程序员式的吐槽
    """

    name = "roast-processor"
    version = "1.0.0"
    description = "用程序员的方式吐槽搜索结果"
    author = "presearch-fun"

    ROASTS = {
        'high_stars': [
            "⭐ 这么多star，一定有很多issue吧？",
            "🔥 热门项目，意味着更多坑等你踩",
            "📈 大家都用，出问题搜不到解决方案",
        ],
        'low_stars': [
            "🌱 小众项目，文档可能只有一行README",
            "🤔 这么少star，要么太新要么太坑",
            "💀 可能是作者自己用的玩具项目",
        ],
        'no_description': [
            "📝 连描述都懒得写，代码能好到哪去？",
            "❓ 神秘项目，用之前先读源码吧",
        ],
        'old_project': [
            "⏰ 老项目了，依赖可能比你年龄还大",
            "🦕 技术债的博物馆，参观请买票",
        ],
        'new_project': [
            "🍼 新项目，API明天可能就变了",
            "🧪 小白鼠专用，生产环境慎用",
        ],
        'no_license': [
            "⚠️  没许可证？小心律师函警告",
            "🚨 开源界的黑户，用之前想清楚",
        ]
    }

    def initialize(self) -> bool:
        import random
        self.random = random
        return True

    def process(self, results, **kwargs):
        """添加毒舌评论"""
        import time
        from datetime import datetime

        if not isinstance(results, dict):
            return results

        for source, data in results.items():
            if isinstance(data, dict) and 'items' in data:
                for item in data['items']:
                    roasts = []

                    stars = item.get('stargazers_count', item.get('stars', 0))
                    if stars > 10000:
                        roasts.append(self.random.choice(self.ROASTS['high_stars']))
                    elif stars < 100:
                        roasts.append(self.random.choice(self.ROASTS['low_stars']))

                    if not item.get('description'):
                        roasts.append(self.random.choice(self.ROASTS['no_description']))

                    if not item.get('license'):
                        roasts.append(self.random.choice(self.ROASTS['no_license']))

                    # 检查项目年龄
                    created = item.get('created_at', '')
                    if created:
                        try:
                            created_year = int(created[:4])
                            current_year = datetime.now().year
                            age = current_year - created_year

                            if age > 5:
                                roasts.append(self.random.choice(self.ROASTS['old_project']))
                            elif age < 1:
                                roasts.append(self.random.choice(self.ROASTS['new_project']))
                        except:
                            pass

                    if roasts:
                        item['_roasts'] = roasts
                        item['_roast_summary'] = " ".join(roasts)

        return results

    def get_priority(self) -> int:
        return 200  # 最后执行


class HypeProcessorPlugin(ProcessorPlugin):
    """
     hype 处理器

    给每个项目加上夸张的赞美
    """

    name = "hype-processor"
    version = "1.0.0"
    description = "用夸张的方式赞美项目"
    author = "presearch-fun"

    HYPES = [
        "🚀 这绝对是你今年见过的最棒的项目！",
        "💯 用了它，你的代码质量直接起飞！",
        "🔥 社区都在疯传，不用就out了！",
        "⭐ GitHub星标证明了一切！",
        "🎯 这就是你一直在寻找的完美解决方案！",
        "💎 代码界的钻石，闪闪发光！",
        "🏆 年度最佳项目候选！",
        "🌟 用了它，老板都夸你技术牛！",
    ]

    def initialize(self) -> bool:
        import random
        self.random = random
        return True

    def process(self, results, **kwargs):
        """添加 hype 评论"""
        if not isinstance(results, dict):
            return results

        for source, data in results.items():
            if isinstance(data, dict) and 'items' in data:
                for item in data['items']:
                    hype = self.random.choice(self.HYPES)
                    item['_hype'] = hype

        return results

    def get_priority(self) -> int:
        return 200


class DadJokeProcessorPlugin(ProcessorPlugin):
    """
    程序员 dad joke 处理器

    给结果加上程序员冷笑话
    """

    name = "dadjoke-processor"
    version = "1.0.0"
    description = "添加程序员冷笑话"
    author = "presearch-fun"

    JOKES = [
        "为什么程序员总是分不清圣诞节和万圣节？因为 Oct 31 = Dec 25",
        "一个程序员走进酒吧，举起双手说：'我要一杯啤酒。' 酒保问：'一杯还是两杯？' 程序员：'是的。'",
        "为什么程序员不喜欢户外活动？因为那里有太多bugs",
        "程序员最讨厌的歌是什么？'Hello World'",
        "为什么Java开发者总是戴着眼镜？因为他们不能C#",
        "一个SQL查询走进酒吧，走到两张桌子中间问：'可以join你们吗？'",
        "为什么Python程序员不会锁门？因为他们相信缩进",
        "程序员的妻子让他去买牛奶，他说：'如果有鸡蛋，买12个。' 他带回了12盒牛奶。",
        "为什么程序员总是把万圣节和圣诞节搞混？因为 31 OCT = 25 DEC",
        "一个程序员对他的朋友说：'我改变了灯，现在它不发光了。' 朋友：'你确定吗？' 程序员：'不，我只是改了灯。'",
    ]

    def initialize(self) -> bool:
        import random
        self.random = random
        return True

    def process(self, results, **kwargs):
        """添加 dad joke"""
        if not isinstance(results, dict):
            return results

        # 随机选一个笑话添加到结果中
        joke = self.random.choice(self.JOKES)
        results['_dadjoke'] = joke

        return results

    def get_priority(self) -> int:
        return 100


if __name__ == "__main__":
    print("测试趣味处理器插件...")

    # 测试数据
    test_results = {
        'github': {
            'items': [
                {
                    'name': 'tiny-project',
                    'stargazers_count': 5,
                    'description': '',
                    'created_at': '2026-01-01T00:00:00Z'
                },
                {
                    'name': 'popular-project',
                    'stargazers_count': 50000,
                    'description': 'A great project',
                    'created_at': '2015-01-01T00:00:00Z',
                    'license': {'name': 'MIT'}
                }
            ]
        }
    }

    # 测试毒舌插件
    roast = RoastProcessorPlugin()
    roast.initialize()
    roasted = roast.process(test_results.copy())
    print("\n🌶️ 毒舌吐槽:")
    for item in roasted['github']['items']:
        if '_roasts' in item:
            print(f"  {item['name']}: {item['_roast_summary']}")
    print("✓ 毒舌插件测试通过")

    # 测试 hype 插件
    hype = HypeProcessorPlugin()
    hype.initialize()
    hyped = hype.process(test_results.copy())
    print("\n🎉 Hype评论:")
    for item in hyped['github']['items'][:2]:
        print(f"  {item['name']}: {item['_hype']}")
    print("✓ Hype插件测试通过")

    # 测试 dad joke 插件
    dad = DadJokeProcessorPlugin()
    dad.initialize()
    joked = dad.process(test_results.copy())
    print(f"\n😄 Dad Joke: {joked['_dadjoke']}")
    print("✓ Dad joke插件测试通过")

    print("\n所有趣味处理器插件测试通过！")

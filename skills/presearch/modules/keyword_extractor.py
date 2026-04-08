#!/usr/bin/env python3
"""
关键词提取模块
用于从用户输入中提取有效的搜索关键词
支持中英文翻译和 jieba 分词
"""

import re
import sys
from typing import List, Tuple, Optional

# 导入翻译模块
try:
    from translator import TechTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# 导入 jieba 分词
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

class KeywordExtractor:
    """关键词提取器"""

    def __init__(self, enable_translation: bool = True, enable_api: bool = True, use_jieba: bool = True):
        """
        初始化关键词提取器

        Args:
            enable_translation: 是否启用中文到英文翻译
            enable_api: 是否启用翻译API
            use_jieba: 是否使用jieba分词
        """
        self.enable_translation = enable_translation and TRANSLATOR_AVAILABLE
        self.enable_api = enable_api
        self.use_jieba = use_jieba and JIEBA_AVAILABLE

        if self.enable_translation:
            self.translator = TechTranslator(enable_api=enable_api)
        else:
            self.translator = None

        # 配置 jieba
        if self.use_jieba:
            # 添加技术词汇到 jieba 词典
            self._init_jieba_dict()

    # 中文技术词汇（用于分词）
    CHINESE_TECH_WORDS = {
        '机器学习', '深度学习', '神经网络', '人工智能',
        '自然语言处理', '计算机视觉', '图像识别', '语音识别',
        '数据库', '关系型', '非关系型', '连接池',
        '前端', '后端', '全栈', '中间件',
        '微服务', '容器', '容器化', '编排', '负载均衡',
        '持续集成', '持续部署', '自动化', '监控',
        '单元测试', '集成测试', '端到端测试', '测试框架',
        '加密', '解密', '认证', '授权', '令牌',
        '区块链', '加密货币', '智能合约',
        '数据处理', '数据分析', '数据可视化', '爬虫',
        '游戏引擎', '物理引擎',
        '消息队列', '推送', '通知',
        '定时任务', '定时器',
        '图像处理', '视频处理', '音频处理',
        '验证码', '二维码', '条形码', '水印',
        '错误处理', '异常处理',
        '序列化', '反序列化', '压缩', '解压',
    }

    # 中文停用词
    CHINESE_STOP_WORDS = {
        '的', '地', '得', '了', '在', '是', '我', '有', '和', '就',
        '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说',
        '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
        '那', '哪', '谁', '什么', '怎么', '为什么', '如何', '怎样',
        '可以', '可能', '应该', '需要', '想要', '希望', '最好', '怎么',
        '为什么', '如何', '怎样', '什么', '哪个', '哪些', '哪里',
        '什么时候', '多少', '几个', '一些', '一点', '一下', '一起',
        '一样', '一般', '一直', '一定', '一些', '一点', '一下',
        '帮我', '帮我找', '给我', '帮我查', '我想', '我要', '请帮我',
        '帮忙', '寻找', '查找', '搜索', '查一下', '找一下',
        '帮', '找', '个', '请', '让', '能', '够', '用', '做', '写',
    }

    # 英文停用词
    ENGLISH_STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
        'over', 'after', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'doing',
        'can', 'could', 'may', 'might', 'must', 'shall', 'should',
        'will', 'would', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
        'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
        'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'doing', 'will', 'would', 'should', 'could', 'may', 'might', 'must',
        'shall', 'can', 'what', 'which', 'who', 'whom', 'whose', 'where',
        'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now'
    }

    # 技术相关停用词（保留）
    TECH_KEYWORDS = {
        'library', 'framework', 'tool', 'package', 'module', 'plugin',
        'extension', 'api', 'sdk', 'cli', 'gui', 'ui', 'ux', 'web',
        'mobile', 'desktop', 'server', 'client', 'backend', 'frontend',
        'database', 'cache', 'queue', 'message', 'auth', 'authn', 'authz',
        'log', 'monitor', 'metric', 'trace', 'test', 'test', 'test',
        'dev', 'development', 'deploy', 'deployment', 'ci', 'cd',
        'docker', 'kubernetes', 'cloud', 'aws', 'azure', 'gcp',
        'python', 'javascript', 'java', 'go', 'rust', 'c++', 'c#', 'php',
        'ruby', 'swift', 'kotlin', 'typescript', 'html', 'css', 'sql',
        'nosql', 'graphql', 'rest', 'grpc', 'http', 'https', 'tcp', 'udp'
    }

    def _init_jieba_dict(self):
        """初始化 jieba 词典，添加技术词汇"""
        if not self.use_jieba:
            return

        # 添加中文技术词汇到 jieba 词典
        for word in self.CHINESE_TECH_WORDS:
            jieba.add_word(word)

        # 添加翻译器词典中的词汇
        if self.translator:
            for word in self.translator.TECH_DICTIONARY.keys():
                jieba.add_word(word)

    def segment_chinese(self, text: str) -> list:
        """
        中文分词（优先使用 jieba，备用简单分词）

        Args:
            text: 中文文本

        Returns:
            分词后的列表
        """
        # 优先使用 jieba 分词
        if self.use_jieba:
            try:
                words = list(jieba.cut(text))
                # 过滤停用词
                return [w for w in words if w.strip() and w not in self.CHINESE_STOP_WORDS]
            except Exception:
                pass  # 回退到简单分词

        # 备用: 简单的最大匹配法
        if not self.translator:
            return list(text)

        # 合并词典词汇
        all_words = self.CHINESE_TECH_WORDS | set(self.translator.TECH_DICTIONARY.keys())

        # 按长度降序排序，优先匹配长词
        sorted_words = sorted(all_words, key=len, reverse=True)

        result = []
        remaining = text

        while remaining:
            matched = False

            # 尝试匹配最长词
            for word in sorted_words:
                if remaining.startswith(word):
                    result.append(word)
                    remaining = remaining[len(word):]
                    matched = True
                    break

            if not matched:
                # 没有匹配，按单字处理
                if remaining[0] not in self.CHINESE_STOP_WORDS:
                    result.append(remaining[0])
                remaining = remaining[1:]

        # 合并连续的单字
        merged = []
        single_chars = []

        for item in result:
            if len(item) == 1:
                single_chars.append(item)
            else:
                if single_chars:
                    # 如果连续单字超过2个，合并为一个词
                    if len(single_chars) > 2:
                        merged.append(''.join(single_chars))
                    else:
                        merged.extend(single_chars)
                    single_chars = []
                merged.append(item)

        if single_chars:
            if len(single_chars) > 2:
                merged.append(''.join(single_chars))
            else:
                merged.extend(single_chars)

        return merged

    def extract_keywords(self, text, max_keywords=5):
        """
        从文本中提取关键词

        Args:
            text: 输入文本
            max_keywords: 最大关键词数量

        Returns:
            关键词列表
        """
        if not text:
            return []

        # 判断文本语言（简单基于字符范围）
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)

        # 清理文本
        text = text.lower().strip()

        # 移除特殊字符，保留字母、数字、中文、空格、连字符、下划线
        if has_chinese:
            # 中文文本：保留中文、英文、数字、空格
            text = re.sub(r'[^\u4e00-\u9fffa-zA-Z0-9\s\-_]', ' ', text)
        else:
            # 英文文本：保留英文、数字、空格、连字符、下划线
            text = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', text)

        # 分割单词
        if has_chinese:
            # 分离中文和非中文部分
            parts = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9\-_]+', text)
            words = []
            for part in parts:
                if any('\u4e00' <= c <= '\u9fff' for c in part):
                    # 中文部分：使用分词器
                    if self.translator:
                        words.extend(self.segment_chinese(part))
                    else:
                        words.append(part)
                else:
                    # 非中文部分
                    words.append(part)
        else:
            # 英文分词：按空格分割
            words = text.split()

        # 过滤停用词
        filtered_words = []
        for word in words:
            word = word.strip()
            if not word:
                continue

            # 检查是否为停用词
            if has_chinese:
                if word in KeywordExtractor.CHINESE_STOP_WORDS:
                    continue
            else:
                if word in KeywordExtractor.ENGLISH_STOP_WORDS:
                    continue

            # 保留技术关键词
            if word in KeywordExtractor.TECH_KEYWORDS:
                filtered_words.append(word)
                continue

            # 过滤过短的词（中文单字词除外）
            if has_chinese:
                if len(word) == 1 and not ('\u4e00' <= word <= '\u9fff'):
                    continue
            else:
                if len(word) < 3:
                    continue

            filtered_words.append(word)

        # 去重并限制数量
        unique_words = []
        seen = set()
        for word in filtered_words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)

        return unique_words[:max_keywords]

    @staticmethod
    def build_search_query(keywords, language='mixed'):
        """
        构建搜索查询字符串（静态方法，向后兼容）

        Args:
            keywords: 关键词列表
            language: 搜索语言偏好（'mixed', 'en', 'zh'）

        Returns:
            搜索查询字符串
        """
        if not keywords:
            return ""

        # 简单连接关键词
        query = ' '.join(keywords)

        # 如果有关键词是中文，添加中文搜索优化
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)

        # 对于GitHub搜索，可以添加语言过滤
        if language == 'en' and has_chinese:
            # 如果有中文但需要英文搜索，尝试翻译或添加英文关键词
            pass
        elif language == 'zh' and not has_chinese:
            # 如果需要中文搜索但没有中文，保持原样
            pass

        return query

    def translate_keywords(self, keywords: List[str]) -> List[Tuple[str, str]]:
        """
        翻译关键词列表

        Args:
            keywords: 关键词列表

        Returns:
            [(原文, 翻译)] 元组列表
        """
        if not self.translator:
            return [(kw, kw) for kw in keywords]

        results = []
        for kw in keywords:
            if self.translator.is_chinese(kw):
                translated = self.translator.translate(kw)
                results.append((kw, translated))
            else:
                results.append((kw, kw))

        return results

    def build_english_query(self, keywords: List[str]) -> str:
        """
        构建英文搜索查询（自动翻译中文关键词）

        Args:
            keywords: 关键词列表

        Returns:
            英文搜索查询字符串
        """
        if not keywords:
            return ""

        if not self.translator:
            return ' '.join(keywords)

        english_keywords = []
        for kw in keywords:
            if self.translator.is_chinese(kw):
                translated = self.translator.translate(kw)
                english_keywords.append(translated)
            else:
                english_keywords.append(kw)

        return ' '.join(english_keywords)

    def extract_and_translate(self, text: str, max_keywords: int = 5) -> Tuple[List[str], List[str]]:
        """
        提取关键词并翻译

        Args:
            text: 输入文本
            max_keywords: 最大关键词数量

        Returns:
            (原始关键词列表, 翻译后关键词列表)
        """
        original_keywords = self.extract_keywords(text, max_keywords)

        if not self.translator:
            return original_keywords, original_keywords

        translated_keywords = []
        for kw in original_keywords:
            if self.translator.is_chinese(kw):
                translated = self.translator.translate(kw)
                translated_keywords.append(translated)
            else:
                translated_keywords.append(kw)

        return original_keywords, translated_keywords

def main():
    """测试函数"""
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        text = "我需要一个Python的Web框架来构建REST API"

    # 测试翻译功能
    print("=== 关键词提取与翻译测试 ===\n")

    extractor = KeywordExtractor(enable_translation=True, enable_api=True)
    keywords = extractor.extract_keywords(text)
    query = extractor.build_search_query(keywords)
    english_query = extractor.build_english_query(keywords)

    print(f"输入文本: {text}")
    print(f"提取关键词: {keywords}")
    print(f"搜索查询: {query}")
    print(f"英文查询: {english_query}")

    # 显示翻译详情
    if extractor.translator:
        print("\n翻译详情:")
        original, translated = extractor.extract_and_translate(text)
        for o, t in zip(original, translated):
            if o != t:
                print(f"  {o} -> {t}")
            else:
                print(f"  {o} (无需翻译)")

if __name__ == "__main__":
    main()
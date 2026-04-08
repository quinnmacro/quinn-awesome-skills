#!/usr/bin/env python3
"""
轻量级中英文翻译模块
支持本地词典映射 + 免费翻译API (deep-translator)
"""

import re
import json
import os
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Optional, Tuple

# 尝试导入 deep-translator
try:
    from deep_translator import GoogleTranslator as DeepGoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False

class TechTranslator:
    """技术词汇翻译器"""

    # 本地技术词典：中文 -> 英文
    TECH_DICTIONARY = {
        # 编程语言
        '编程语言': 'programming language',
        '编程': 'programming',
        '代码': 'code',
        '脚本': 'script',
        '函数': 'function',
        '变量': 'variable',
        '类': 'class',
        '对象': 'object',
        '接口': 'interface',
        '模块': 'module',
        '包': 'package',
        '库': 'library',
        '框架': 'framework',
        '插件': 'plugin',
        '组件': 'component',

        # Web开发
        '网页': 'web',
        '网站': 'website',
        '前端': 'frontend',
        '后端': 'backend',
        '全栈': 'fullstack',
        '接口': 'api',
        '路由': 'router',
        '中间件': 'middleware',
        '请求': 'request',
        '响应': 'response',
        '会话': 'session',
        '缓存': 'cache',
        '跨域': 'cors',

        # 数据库
        '数据库': 'database',
        '表': 'table',
        '字段': 'field',
        '索引': 'index',
        '查询': 'query',
        '事务': 'transaction',
        '存储': 'storage',
        '关系型': 'relational',
        '非关系型': 'nosql',

        # 移动开发
        '移动端': 'mobile',
        '安卓': 'android',
        '苹果': 'ios',
        '小程序': 'mini program',
        '应用': 'app',

        # 机器学习/AI
        '机器学习': 'machine learning',
        '深度学习': 'deep learning',
        '神经网络': 'neural network',
        '人工智能': 'ai',
        '模型': 'model',
        '训练': 'training',
        '推理': 'inference',
        '自然语言处理': 'nlp',
        '计算机视觉': 'computer vision',
        '图像识别': 'image recognition',
        '语音识别': 'speech recognition',
        '文本处理': 'text processing',
        '情感分析': 'sentiment analysis',

        # DevOps
        '容器': 'container',
        '容器化': 'containerization',
        '编排': 'orchestration',
        '部署': 'deployment',
        '持续集成': 'ci',
        '持续部署': 'cd',
        '自动化': 'automation',
        '监控': 'monitoring',
        '日志': 'logging',
        '负载均衡': 'load balancing',

        # 安全
        '安全': 'security',
        '加密': 'encryption',
        '解密': 'decryption',
        '认证': 'authentication',
        '授权': 'authorization',
        '令牌': 'token',
        '密码': 'password',
        '哈希': 'hash',

        # 网络
        '网络': 'network',
        '协议': 'protocol',
        '套接字': 'socket',
        '代理': 'proxy',
        '防火墙': 'firewall',

        # 测试
        '测试': 'testing',
        '单元测试': 'unit test',
        '集成测试': 'integration test',
        '端到端测试': 'e2e test',
        '测试框架': 'test framework',
        '模拟': 'mock',

        # 工具
        '工具': 'tool',
        '命令行': 'cli',
        '编辑器': 'editor',
        '调试': 'debug',
        '编译': 'compile',
        '构建': 'build',

        # 通用
        '解析器': 'parser',
        '生成器': 'generator',
        '转换器': 'converter',
        '验证器': 'validator',
        '格式化': 'formatter',
        '序列化': 'serialization',
        '反序列化': 'deserialization',
        '压缩': 'compression',
        '解压': 'decompression',
        '上传': 'upload',
        '下载': 'download',
        '导入': 'import',
        '导出': 'export',
        '配置': 'config',
        '日志': 'log',
        '错误处理': 'error handling',
        '异常处理': 'exception handling',

        # 文件格式
        '文件': 'file',
        '图片': 'image',
        '视频': 'video',
        '音频': 'audio',
        '文档': 'document',
        '表格': 'spreadsheet',
        '电子表格': 'spreadsheet',

        # 数据处理
        '数据': 'data',
        '数据处理': 'data processing',
        '数据分析': 'data analysis',
        '数据可视化': 'data visualization',
        '爬虫': 'crawler',
        '抓取': 'scraping',
        '清洗': 'cleaning',
        '转换': 'transform',
        '提取': 'extract',

        # 消息/通信
        '消息': 'message',
        '队列': 'queue',
        '推送': 'push',
        '通知': 'notification',
        '邮件': 'email',
        '短信': 'sms',
        '聊天': 'chat',

        # 时间/日期
        '时间': 'time',
        '日期': 'date',
        '日历': 'calendar',
        '定时': 'scheduler',
        '定时任务': 'cron job',

        # 加密货币/区块链
        '区块链': 'blockchain',
        '加密货币': 'cryptocurrency',
        '比特币': 'bitcoin',
        '以太坊': 'ethereum',
        '智能合约': 'smart contract',
        '钱包': 'wallet',

        # 游戏
        '游戏': 'game',
        '游戏引擎': 'game engine',
        '物理引擎': 'physics engine',
        '渲染': 'rendering',

        # 算法
        '算法': 'algorithm',
        '排序': 'sorting',
        '搜索': 'search',
        '图算法': 'graph algorithm',
        '动态规划': 'dynamic programming',

        # 架构
        '微服务': 'microservice',
        '服务': 'service',
        '网关': 'gateway',
        '服务发现': 'service discovery',
        '配置中心': 'config center',

        # 其他常见
        '模板': 'template',
        '主题': 'theme',
        '样式': 'style',
        '布局': 'layout',
        '动画': 'animation',
        '图表': 'chart',
        '地图': 'map',
        '二维码': 'qr code',
        '条形码': 'barcode',
        '验证码': 'captcha',
        '水印': 'watermark',
        '截图': 'screenshot',
        '录屏': 'screen recording',

        # 操作
        '创建': 'create',
        '读取': 'read',
        '更新': 'update',
        '删除': 'delete',
        '复制': 'copy',
        '粘贴': 'paste',
        '拖拽': 'drag drop',
        '缩放': 'zoom',
        '滚动': 'scroll',
    }

    # 翻译缓存
    _cache: Dict[str, str] = {}

    # API 配置
    MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"
    _MODULES_PATH = os.environ.get('PRESEARCH_MODULES', os.path.dirname(os.path.abspath(__file__)))
    CACHE_FILE = os.path.join(_MODULES_PATH, "cache", "translations.json")

    def __init__(self, enable_api: bool = True, cache_ttl: int = 86400 * 7):
        """
        初始化翻译器

        Args:
            enable_api: 是否启用API翻译
            cache_ttl: 缓存TTL（秒），默认7天
        """
        self.enable_api = enable_api
        self.cache_ttl = cache_ttl
        self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = {}

    def _save_cache(self):
        """保存缓存"""
        try:
            import os
            os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def is_chinese(self, text: str) -> bool:
        """检查文本是否包含中文"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)

    def translate_local(self, text: str) -> Optional[str]:
        """
        使用本地词典翻译

        Args:
            text: 中文文本

        Returns:
            英文翻译，如果词典中没有则返回None
        """
        # 直接匹配
        if text in self.TECH_DICTIONARY:
            return self.TECH_DICTIONARY[text]

        # 尝试部分匹配（最长匹配）
        best_match = None
        best_length = 0

        for cn, en in self.TECH_DICTIONARY.items():
            if cn in text:
                if len(cn) > best_length:
                    best_length = len(cn)
                    best_match = (cn, en)

        if best_match:
            return text.replace(best_match[0], best_match[1])

        return None

    def translate_api(self, text: str) -> Optional[str]:
        """
        使用翻译API翻译（优先 deep-translator，备用 MyMemory）

        Args:
            text: 中文文本

        Returns:
            英文翻译，失败返回None
        """
        if not self.enable_api:
            return None

        # 检查缓存
        if text in self._cache:
            return self._cache[text]

        # 优先使用 deep-translator (同步，稳定)
        if DEEP_TRANSLATOR_AVAILABLE:
            try:
                translator = DeepGoogleTranslator(source='zh-CN', target='en')
                translation = translator.translate(text)
                if translation and translation != text:
                    self._cache[text] = translation
                    self._save_cache()
                    return translation
            except Exception:
                pass  # 回退到 MyMemory

        # 备用: MyMemory API
        try:
            params = {
                'q': text,
                'langpair': 'zh|en'
            }
            url = f"{self.MYMEMORY_API_URL}?{urllib.parse.urlencode(params)}"

            req = urllib.request.Request(url, headers={'User-Agent': 'presearch-tool'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

                if data.get('responseStatus') == 200:
                    translation = data.get('responseData', {}).get('translatedText')
                    if translation and translation != text:
                        self._cache[text] = translation
                        self._save_cache()
                        return translation

        except Exception:
            pass

        return None

    def translate(self, text: str) -> str:
        """
        翻译文本（本地词典优先，API备用）

        Args:
            text: 输入文本

        Returns:
            翻译结果（如果不需要翻译或翻译失败，返回原文）
        """
        # 如果不是中文，直接返回
        if not self.is_chinese(text):
            return text

        # 尝试本地翻译
        local_result = self.translate_local(text)
        if local_result:
            return local_result

        # 尝试API翻译
        api_result = self.translate_api(text)
        if api_result:
            return api_result

        # 翻译失败，返回原文
        return text

    def translate_keywords(self, keywords: List[str]) -> List[Tuple[str, str]]:
        """
        翻译关键词列表

        Args:
            keywords: 关键词列表

        Returns:
            [(原文, 翻译)] 元组列表
        """
        results = []
        for kw in keywords:
            translated = self.translate(kw)
            results.append((kw, translated))
        return results

    def build_english_query(self, keywords: List[str]) -> str:
        """
        构建英文搜索查询

        Args:
            keywords: 关键词列表（可能包含中文）

        Returns:
            英文搜索查询字符串
        """
        english_keywords = []
        for kw in keywords:
            if self.is_chinese(kw):
                translated = self.translate(kw)
                english_keywords.append(translated)
            else:
                english_keywords.append(kw)

        return ' '.join(english_keywords)


def translate_to_english(text: str, enable_api: bool = True) -> str:
    """
    便捷函数：将中文文本翻译为英文

    Args:
        text: 输入文本
        enable_api: 是否启用API翻译

    Returns:
        英文翻译结果
    """
    translator = TechTranslator(enable_api=enable_api)
    return translator.translate(text)


def main():
    """测试函数"""
    import sys

    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        # 测试用例
        test_cases = [
            "机器学习",
            "数据库连接池",
            "图像处理",
            "这是一个测试",
            "web framework",
        ]
        print("=== 技术词汇翻译测试 ===\n")

        translator = TechTranslator(enable_api=True)

        for text in test_cases:
            result = translator.translate(text)
            print(f"{text} -> {result}")

        return

    translator = TechTranslator(enable_api=True)
    result = translator.translate(text)
    print(f"原文: {text}")
    print(f"翻译: {result}")


if __name__ == "__main__":
    main()

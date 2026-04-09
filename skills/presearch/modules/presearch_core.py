#!/usr/bin/env python3
"""
presearch核心模块 - 第二阶段优化版
支持多数据源并行搜索
"""

import sys
import warnings

# 抑制第三方库警告
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', message='.*pkg_resources.*')
warnings.filterwarnings('ignore', message='.*logfire.*')
warnings.filterwarnings('ignore', message='.*opentelemetry.*')

import concurrent.futures
import os
from typing import Dict, List, Any, Tuple
from urllib.parse import quote

# 导入自定义模块
MODULES_PATH = os.environ.get('PRESEARCH_MODULES', os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MODULES_PATH)

try:
    from keyword_extractor import KeywordExtractor
    from translator import TechTranslator
    from http_client import HTTPClient, NetworkError, APIError, RateLimitError
    from formatter import ResultFormatter
    from npm_client import NPMClient
    from pypi_client import PyPIClient
    from docker_client import DockerClient
    from cache.manager import CacheManager
    from config import get_config, ConfigLoader
    from config.presets import list_presets
    from cli.parser import create_parser
    from cli.output import print_success, print_error, print_info
    from cli.export import export_results
    from history.manager import HistoryManager
    from __version__ import __version__
except ImportError as e:
    print(f"错误: 无法导入模块 - {e}", file=sys.stderr)
    print("请确保所有模块文件都存在", file=sys.stderr)
    sys.exit(1)

class PresearchCore:
    """presearch核心类 - 支持多数据源并行搜索和缓存"""

    def __init__(
        self,
        enable_npm=True,
        enable_pypi=True,
        enable_docker=True,
        cache_enabled=True,
        cache_ttl=86400,
        enable_translation=True,
        translation_api=True
    ):
        """
        初始化

        Args:
            enable_npm: 是否启用npm搜索
            enable_pypi: 是否启用PyPI搜索
            enable_docker: 是否启用Docker搜索
            cache_enabled: 是否启用缓存
            cache_ttl: 缓存TTL（秒），默认24小时
            enable_translation: 是否启用中文到英文翻译
            translation_api: 是否启用翻译API
        """
        self.keyword_extractor = KeywordExtractor(
            enable_translation=enable_translation,
            enable_api=translation_api
        )
        self.http_client = HTTPClient(max_retries=2, timeout=10)
        self.enable_translation = enable_translation

        # 初始化各API客户端
        self.clients = {}

        # GitHub和arXiv是核心客户端
        self.clients['github'] = {'name': 'GitHub', 'enabled': True}
        self.clients['arxiv'] = {'name': 'arXiv', 'enabled': True}

        # 可选客户端
        if enable_npm:
            self.clients['npm'] = {'name': 'npm', 'client': NPMClient(), 'enabled': True}
        if enable_pypi:
            self.clients['pypi'] = {'name': 'PyPI', 'client': PyPIClient(), 'enabled': True}
        if enable_docker:
            self.clients['docker'] = {'name': 'Docker Hub', 'client': DockerClient(), 'enabled': True}

        # 初始化缓存管理器
        self.cache_enabled = cache_enabled
        if cache_enabled:
            self.cache_manager = CacheManager(
                memory_ttl=300,  # 5分钟
                disk_ttl=cache_ttl,
                memory_max_size=100
            )
        else:
            self.cache_manager = None

        # 初始化历史管理器
        self.history_manager = HistoryManager()

    def extract_search_query(self, user_input):
        """
        从用户输入提取搜索查询（自动翻译中文为英文）

        Args:
            user_input: 用户输入

        Returns:
            搜索查询字符串（英文）
        """
        keywords = self.keyword_extractor.extract_keywords(user_input)

        # 如果启用翻译，构建英文查询
        if self.enable_translation and hasattr(self.keyword_extractor, 'build_english_query'):
            query = self.keyword_extractor.build_english_query(keywords)
        else:
            query = self.keyword_extractor.build_search_query(keywords)

        # 如果提取失败，使用原始输入
        if not query:
            query = user_input.strip()

        return query

    def extract_search_query_with_original(self, user_input):
        """
        从用户输入提取搜索查询，返回原文和英文翻译

        Args:
            user_input: 用户输入

        Returns:
            (原始查询, 英文查询) 元组
        """
        keywords = self.keyword_extractor.extract_keywords(user_input)
        original_query = self.keyword_extractor.build_search_query(keywords)

        if self.enable_translation and hasattr(self.keyword_extractor, 'build_english_query'):
            english_query = self.keyword_extractor.build_english_query(keywords)
        else:
            english_query = original_query

        if not original_query:
            original_query = user_input.strip()
        if not english_query:
            english_query = original_query

        return original_query, english_query

    def search_github(self, query, per_page=10):
        """
        搜索GitHub

        Args:
            query: 搜索查询
            per_page: 每页结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            encoded_query = quote(query, safe='')
            url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={per_page}"
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'presearch-tool'
            }
            results = self.http_client.request_json(url, headers=headers)
            return ('github', results)
        except RateLimitError as e:
            return ('github', {'error': 'github_rate_limit', 'message': str(e)})
        except (NetworkError, APIError) as e:
            return ('github', {'error': 'github_api_error', 'message': str(e)})
        except Exception as e:
            return ('github', {'error': 'github_unknown_error', 'message': str(e)})

    def search_arxiv(self, query, max_results=5):
        """
        搜索arXiv - 使用 arxiv Python 包

        Args:
            query: 搜索查询
            max_results: 最大结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            import arxiv

            # 使用 arxiv 包搜索（新 API）
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            client = arxiv.Client()
            papers = []
            for result in client.results(search):
                paper = {
                    'title': result.title,
                    'link': result.entry_id,
                    'published': str(result.published)[:10] if result.published else '',
                    'authors': [author.name for author in result.authors] if result.authors else ['未知作者'],
                    'summary': result.summary[:200] + '...' if result.summary and len(result.summary) > 200 else (result.summary or '')
                }
                papers.append(paper)

            return ('arxiv', papers)
        except ImportError:
            # 回退到 HTTP 方式
            return self._search_arxiv_http(query, max_results)
        except Exception as e:
            return ('arxiv', {'error': 'arxiv_unknown_error', 'message': str(e)})

    def _search_arxiv_http(self, query, max_results=5):
        """
        回退方法：通过HTTP搜索arXiv

        Args:
            query: 搜索查询
            max_results: 最大结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            encoded_query = quote(query, safe='')
            url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={max_results}"
            response = self.http_client.request(url)
            papers = self._parse_arxiv_response(response)
            return ('arxiv', papers)
        except RateLimitError as e:
            return ('arxiv', {'error': 'arxiv_rate_limit', 'message': str(e)})
        except (NetworkError, APIError) as e:
            return ('arxiv', {'error': 'arxiv_api_error', 'message': str(e)})
        except Exception as e:
            return ('arxiv', {'error': 'arxiv_unknown_error', 'message': str(e)})

    def _parse_arxiv_response(self, xml_response):
        """
        解析arXiv API的XML响应

        Args:
            xml_response: XML响应字符串

        Returns:
            论文字典列表
        """
        import xml.etree.ElementTree as ET

        papers = []

        try:
            root = ET.fromstring(xml_response)
            namespace = '{http://www.w3.org/2005/Atom}'

            for entry in root.findall(f'{namespace}entry'):
                paper = {
                    'title': self._get_element_text(entry, f'{namespace}title'),
                    'link': self._get_element_text(entry, f'{namespace}id'),
                    'published': self._get_element_text(entry, f'{namespace}published'),
                    'authors': []
                }

                # 提取作者
                author_elements = entry.findall(f'{namespace}author')
                for author_elem in author_elements:
                    name = self._get_element_text(author_elem, f'{namespace}name')
                    if name:
                        paper['authors'].append(name)

                # 如果没有作者，设置为未知
                if not paper['authors']:
                    paper['authors'] = ['未知作者']

                papers.append(paper)
        except ET.ParseError as e:
            return {'error': 'arxiv_parse_error', 'message': str(e)}

        return papers

    def _get_element_text(self, parent, tag_name):
        """
        获取XML元素的文本内容

        Args:
            parent: 父元素
            tag_name: 标签名

        Returns:
            元素文本，或空字符串
        """
        elem = parent.find(tag_name)
        if elem is not None and elem.text:
            return elem.text.strip()
        return ''

    def search_npm(self, query, size=10):
        """
        搜索npm包

        Args:
            query: 搜索查询
            size: 结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            client = self.clients['npm']['client']
            results = client.search(query, size)
            return ('npm', results)
        except Exception as e:
            return ('npm', {'error': 'npm_search_error', 'message': str(e)})

    def search_pypi(self, query, max_results=10):
        """
        搜索PyPI包

        Args:
            query: 搜索查询
            max_results: 最大结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            client = self.clients['pypi']['client']
            results = client.search(query, max_results)
            return ('pypi', results)
        except Exception as e:
            return ('pypi', {'error': 'pypi_search_error', 'message': str(e)})

    def search_docker(self, query, page_size=10):
        """
        搜索Docker镜像

        Args:
            query: 搜索查询
            page_size: 每页结果数量

        Returns:
            (source_name, results) 元组
        """
        try:
            client = self.clients['docker']['client']
            results = client.search(query, page_size)
            return ('docker', results)
        except Exception as e:
            return ('docker', {'error': 'docker_search_error', 'message': str(e)})

    def parallel_search(self, query):
        """
        并行搜索所有数据源

        Args:
            query: 搜索查询

        Returns:
            字典：{source_name: results}
        """
        all_results = {}

        # 准备搜索任务
        search_tasks = []

        # 核心搜索任务
        search_tasks.append(('github', lambda: self.search_github(query)))
        search_tasks.append(('arxiv', lambda: self.search_arxiv(query)))

        # 可选搜索任务
        if 'npm' in self.clients and self.clients['npm']['enabled']:
            search_tasks.append(('npm', lambda: self.search_npm(query)))
        if 'pypi' in self.clients and self.clients['pypi']['enabled']:
            search_tasks.append(('pypi', lambda: self.search_pypi(query)))
        if 'docker' in self.clients and self.clients['docker']['enabled']:
            search_tasks.append(('docker', lambda: self.search_docker(query)))

        # 使用线程池执行并行搜索
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(search_tasks)) as executor:
            # 提交所有任务
            future_to_source = {}
            for source_name, task_func in search_tasks:
                future = executor.submit(task_func)
                future_to_source[future] = source_name

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    source_name, results = future.result()
                    all_results[source_name] = results
                except Exception as e:
                    all_results[source_name] = {'error': f'search_exception: {str(e)}'}

        return all_results

    def search(self, user_input, use_cache=True):
        """
        执行完整搜索（多数据源并行）

        Args:
            user_input: 用户输入
            use_cache: 是否使用缓存

        Returns:
            格式化后的搜索结果
        """
        import time
        start_time = time.time()

        print(f"搜索: {user_input}", file=sys.stderr)

        # 提取搜索查询（支持翻译）
        if self.enable_translation:
            original_query, english_query = self.extract_search_query_with_original(user_input)
            query = english_query
            if original_query != english_query:
                print(f"翻译查询: {original_query} -> {english_query}", file=sys.stderr)
        else:
            query = self.extract_search_query(user_input)

        print(f"搜索查询: {query}", file=sys.stderr)
        print(f"启用数据源: {', '.join([c['name'] for c in self.clients.values() if c['enabled']])}", file=sys.stderr)

        # 检查缓存
        cached_result = None
        if use_cache and self.cache_enabled and self.cache_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            cached_result = self.cache_manager.get(query, enabled_sources)
            if cached_result:
                print("✓ 缓存命中", file=sys.stderr)
                # 记录历史（缓存命中）
                if self.history_manager:
                    self.history_manager.add(
                        query=query,
                        sources=enabled_sources,
                        result_counts={},  # 缓存命中时不重新计算
                        duration_ms=int((time.time() - start_time) * 1000),
                        cached=True
                    )
                return cached_result
            print("✗ 缓存未命中", file=sys.stderr)

        # 执行并行搜索
        all_results = self.parallel_search(query)

        # 处理结果
        output_parts = []
        result_counts = {}

        # GitHub结果
        github_results = all_results.get('github')
        if github_results and 'error' in github_results:
            error_msg = github_results.get('message', '未知错误')
            output_parts.append(f"## GitHub搜索错误\n\n{error_msg}\n")
            result_counts['github'] = 0
        elif github_results:
            github_output = ResultFormatter.format_github_results(github_results, query)
            output_parts.append(github_output)
            result_counts['github'] = len(github_results.get('items', [])) if github_results else 0

        # arXiv结果
        arxiv_results = all_results.get('arxiv')
        if arxiv_results and isinstance(arxiv_results, dict) and 'error' in arxiv_results:
            error_msg = arxiv_results.get('message', '未知错误')
            output_parts.append(f"## arXiv搜索错误\n\n{error_msg}\n")
            result_counts['arxiv'] = 0
        elif arxiv_results:
            arxiv_output = ResultFormatter.format_arxiv_results(arxiv_results, query)
            output_parts.append(arxiv_output)
            result_counts['arxiv'] = len(arxiv_results) if isinstance(arxiv_results, list) else 0

        # npm结果
        npm_results = all_results.get('npm')
        if npm_results and 'error' in npm_results:
            error_msg = npm_results.get('message', '未知错误')
            output_parts.append(f"## npm搜索错误\n\n{error_msg}\n")
            result_counts['npm'] = 0
        elif npm_results and 'npm' in self.clients:
            client = self.clients['npm']['client']
            npm_output = client.format_results(npm_results, query)
            output_parts.append(npm_output)
            result_counts['npm'] = len(npm_results.get('objects', [])) if npm_results else 0

        # PyPI结果
        pypi_results = all_results.get('pypi')
        if pypi_results and 'error' in pypi_results:
            error_msg = pypi_results.get('message', '未知错误')
            output_parts.append(f"## PyPI搜索错误\n\n{error_msg}\n")
            result_counts['pypi'] = 0
        elif pypi_results and 'pypi' in self.clients:
            client = self.clients['pypi']['client']
            pypi_output = client.format_results(pypi_results, query)
            output_parts.append(pypi_output)
            result_counts['pypi'] = len(pypi_results.get('packages', [])) if pypi_results else 0

        # Docker结果
        docker_results = all_results.get('docker')
        if docker_results and 'error' in docker_results:
            error_msg = docker_results.get('message', '未知错误')
            output_parts.append(f"## Docker Hub搜索错误\n\n{error_msg}\n")
            result_counts['docker'] = 0
        elif docker_results and 'docker' in self.clients:
            client = self.clients['docker']['client']
            docker_output = client.format_results(docker_results, query)
            output_parts.append(docker_output)
            result_counts['docker'] = len(docker_results.get('results', [])) if docker_results else 0

        # 总结
        summary = self._format_summary(result_counts)
        output_parts.append(summary)

        # 建议
        recommendations = self._generate_recommendations(result_counts)
        output_parts.append(recommendations)

        result = "\n".join(output_parts)

        # 写入缓存
        if use_cache and self.cache_enabled and self.cache_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            self.cache_manager.set(query, enabled_sources, result)
            print("✓ 结果已缓存", file=sys.stderr)

        # 记录历史
        duration_ms = int((time.time() - start_time) * 1000)
        if self.history_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            self.history_manager.add(
                query=query,
                sources=enabled_sources,
                result_counts=result_counts,
                duration_ms=duration_ms,
                cached=False
            )

        return result

    def search_with_raw(self, user_input, use_cache=True):
        """
        执行完整搜索并返回格式化结果和原始结果

        Args:
            user_input: 用户输入
            use_cache: 是否使用缓存

        Returns:
            (formatted_result, raw_results) 元组
        """
        import time
        start_time = time.time()

        print(f"搜索: {user_input}", file=sys.stderr)

        # 提取搜索查询（支持翻译）
        if self.enable_translation:
            original_query, english_query = self.extract_search_query_with_original(user_input)
            query = english_query
            if original_query != english_query:
                print(f"翻译查询: {original_query} -> {english_query}", file=sys.stderr)
        else:
            query = self.extract_search_query(user_input)

        print(f"搜索查询: {query}", file=sys.stderr)
        print(f"启用数据源: {', '.join([c['name'] for c in self.clients.values() if c['enabled']])}", file=sys.stderr)

        # 检查缓存
        cached_result = None
        if use_cache and self.cache_enabled and self.cache_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            cached_result = self.cache_manager.get(query, enabled_sources)
            if cached_result:
                print("✓ 缓存命中", file=sys.stderr)
                # 返回缓存结果，原始结果为空
                return cached_result, {'cached': True, 'query': query}

        print("✗ 缓存未命中", file=sys.stderr)

        # 执行并行搜索
        all_results = self.parallel_search(query)

        # 处理结果（格式化）
        output_parts = []
        result_counts = {}

        # GitHub结果
        github_results = all_results.get('github')
        if github_results and 'error' in github_results:
            error_msg = github_results.get('message', '未知错误')
            output_parts.append(f"## GitHub搜索错误\n\n{error_msg}\n")
            result_counts['github'] = 0
        elif github_results:
            github_output = ResultFormatter.format_github_results(github_results, query)
            output_parts.append(github_output)
            result_counts['github'] = len(github_results.get('items', [])) if github_results else 0

        # arXiv结果
        arxiv_results = all_results.get('arxiv')
        if arxiv_results and isinstance(arxiv_results, dict) and 'error' in arxiv_results:
            error_msg = arxiv_results.get('message', '未知错误')
            output_parts.append(f"## arXiv搜索错误\n\n{error_msg}\n")
            result_counts['arxiv'] = 0
        elif arxiv_results:
            arxiv_output = ResultFormatter.format_arxiv_results(arxiv_results, query)
            output_parts.append(arxiv_output)
            result_counts['arxiv'] = len(arxiv_results) if isinstance(arxiv_results, list) else 0

        # npm结果
        npm_results = all_results.get('npm')
        if npm_results and 'error' in npm_results:
            error_msg = npm_results.get('message', '未知错误')
            output_parts.append(f"## npm搜索错误\n\n{error_msg}\n")
            result_counts['npm'] = 0
        elif npm_results and 'npm' in self.clients:
            client = self.clients['npm']['client']
            npm_output = client.format_results(npm_results, query)
            output_parts.append(npm_output)
            result_counts['npm'] = len(npm_results.get('objects', [])) if npm_results else 0

        # PyPI结果
        pypi_results = all_results.get('pypi')
        if pypi_results and 'error' in pypi_results:
            error_msg = pypi_results.get('message', '未知错误')
            output_parts.append(f"## PyPI搜索错误\n\n{error_msg}\n")
            result_counts['pypi'] = 0
        elif pypi_results and 'pypi' in self.clients:
            client = self.clients['pypi']['client']
            pypi_output = client.format_results(pypi_results, query)
            output_parts.append(pypi_output)
            result_counts['pypi'] = len(pypi_results.get('packages', [])) if pypi_results else 0

        # Docker结果
        docker_results = all_results.get('docker')
        if docker_results and 'error' in docker_results:
            error_msg = docker_results.get('message', '未知错误')
            output_parts.append(f"## Docker Hub搜索错误\n\n{error_msg}\n")
            result_counts['docker'] = 0
        elif docker_results and 'docker' in self.clients:
            client = self.clients['docker']['client']
            docker_output = client.format_results(docker_results, query)
            output_parts.append(docker_output)
            result_counts['docker'] = len(docker_results.get('results', [])) if docker_results else 0

        # 总结
        summary = self._format_summary(result_counts)
        output_parts.append(summary)

        # 建议
        recommendations = self._generate_recommendations(result_counts)
        output_parts.append(recommendations)

        result = "\n".join(output_parts)

        # 写入缓存
        if use_cache and self.cache_enabled and self.cache_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            self.cache_manager.set(query, enabled_sources, result)
            print("✓ 结果已缓存", file=sys.stderr)

        # 记录历史
        duration_ms = int((time.time() - start_time) * 1000)
        if self.history_manager:
            enabled_sources = [name for name, client in self.clients.items() if client['enabled']]
            self.history_manager.add(
                query=query,
                sources=enabled_sources,
                result_counts=result_counts,
                duration_ms=duration_ms,
                cached=False
            )

        # 构建原始结果
        raw_results = {
            'query': query,
            'github': github_results,
            'arxiv': arxiv_results,
            'npm': npm_results,
            'pypi': pypi_results,
            'docker': docker_results,
            'result_counts': result_counts,
            'duration_ms': duration_ms
        }

        return result, raw_results

    def _format_summary(self, result_counts):
        """
        格式化搜索摘要

        Args:
            result_counts: 各数据源结果数量字典

        Returns:
            摘要字符串
        """
        total = sum(result_counts.values())

        if total == 0:
            return "## 总结\n\n未找到任何相关资源。\n"

        output = ["## 总结"]

        for source_name, count in result_counts.items():
            if count > 0:
                source_display = self.clients.get(source_name, {}).get('name', source_name)
                output.append(f"- 从 {source_display} 找到 {count} 个结果")

        output.append("\n### 建议")
        if result_counts.get('github', 0) >= 3 or result_counts.get('npm', 0) >= 3:
            output.append("✅ **有多个成熟项目可供选择**，建议：")
            output.append("1. 查看前3个项目的README和文档")
            output.append("2. 比较项目活跃度和社区支持")
            output.append("3. 选择最适合需求的项目")
        elif any(count > 0 for count in result_counts.values()):
            output.append("⚠️ **找到少量相关资源**，建议：")
            output.append("1. 仔细评估资源是否满足需求")
            output.append("2. 考虑自行开发或寻找替代方案")
        else:
            output.append("🔍 **未找到现成资源**，建议：")
            output.append("1. 考虑自行开发")
            output.append("2. 搜索相关论文获取算法思路")
            output.append("3. 在技术社区寻求帮助")

        output.append("")  # 空行
        return "\n".join(output)

    def _generate_recommendations(self, result_counts):
        """
        生成推荐建议

        Args:
            result_counts: 各数据源结果数量字典

        Returns:
            建议字符串
        """
        recommendations = ["### 后续步骤"]

        if result_counts.get('github', 0) > 0 or result_counts.get('npm', 0) > 0:
            recommendations.append("- [ ] 查看推荐项目的README和文档")
            recommendations.append("- [ ] 检查项目许可证是否符合要求")
            recommendations.append("- [ ] 评估项目活跃度和社区支持")

        if result_counts.get('pypi', 0) > 0:
            recommendations.append("- [ ] 检查Python包的依赖和兼容性")

        if result_counts.get('docker', 0) > 0:
            recommendations.append("- [ ] 检查Docker镜像的安全性和大小")

        if result_counts.get('arxiv', 0) > 0:
            recommendations.append("- [ ] 阅读相关论文了解算法原理")
            recommendations.append("- [ ] 检查论文中的代码实现")

        if all(count == 0 for count in result_counts.values()):
            recommendations.append("- [ ] 尝试不同的搜索关键词")
            recommendations.append("- [ ] 考虑自行开发解决方案")
            recommendations.append("- [ ] 在技术社区寻求建议")

        recommendations.append("")  # 空行
        return "\n".join(recommendations)

    def get_cache_stats(self):
        """获取缓存统计信息"""
        if self.cache_manager:
            return self.cache_manager.get_stats()
        return None

    def clear_cache(self):
        """清空缓存"""
        if self.cache_manager:
            self.cache_manager.clear_all()
            return True
        return False

    def cleanup_cache(self):
        """清理过期缓存"""
        if self.cache_manager:
            return self.cache_manager.cleanup()
        return 0

def main():
    """主函数 - 增强版CLI"""
    # 预处理参数：支持 "query" format 的简写形式
    args_list = sys.argv[1:]

    # 检查是否是简写格式：最后一个参数是格式名且没有 -f 标志
    valid_formats = ['table', 'json', 'csv', 'markdown', 'emoji', 'meme', 'poetry', 'fortune']

    # 处理 Claude Code skill 传递参数的方式
    # 如果只有一个参数且包含空格，尝试拆分
    if len(args_list) == 1 and ' ' in args_list[0]:
        # 检查是否以格式名结尾
        for fmt in valid_formats:
            if args_list[0].endswith(' ' + fmt):
                # 拆分查询和格式
                query = args_list[0][:-(len(fmt)+1)]
                args_list = [query, fmt]
                break

    if len(args_list) >= 2 and args_list[-1] in valid_formats:
        # 检查是否已经有 -f 或 --format
        has_format_flag = '-f' in args_list or '--format' in args_list
        if not has_format_flag:
            # 将最后一个参数转换为 -f 格式
            format_name = args_list.pop()
            args_list.extend(['-f', format_name])

    # 如果只有一个参数且不以 - 开头，将其作为查询
    if len(args_list) == 1 and not args_list[0].startswith('-'):
        # 作为位置参数传递，不需要修改
        pass

    parser = create_parser()
    args = parser.parse_args(args_list)

    # 显示版本
    if args.version:
        print(f"presearch v{__version__}")
        return

    # TUI 模式
    if args.tui:
        try:
            from tui.app import run_tui
            run_tui()
        except ImportError as e:
            print_error(f"TUI 模式不可用: {e}")
            print_info("请安装 textual: pip install textual>=0.47.0")
            sys.exit(1)
        return

    # Agent 模式
    if args.agent:
        if not args.query:
            print_error("Agent 模式需要提供搜索查询")
            sys.exit(1)
        try:
            from agent.executor import execute_agent_search
            result = execute_agent_search(
                query=args.query,
                sources=args.sources,
                cache_enabled=not args.no_cache
            )
            # Agent 模式输出到 stdout（不使用 stderr）
            print(result)
        except ImportError as e:
            print_error(f"Agent 模式不可用: {e}")
            sys.exit(1)
        return

    # 显示预设列表
    if args.preset == 'list':
        print("可用预设配置:")
        for name, desc in list_presets().items():
            print(f"  - {name}: {desc}")
        return

    # 验证预设名称
    valid_presets = ['frontend', 'backend', 'datascience', 'devops', 'minimal', 'full']
    if args.preset and args.preset not in valid_presets:
        print_error(f"无效的预设: {args.preset}")
        print_info(f"可用预设: {', '.join(valid_presets)}")
        print_info("使用 --preset list 查看所有预设详情")
        sys.exit(1)

    # 初始化配置
    config_loader = ConfigLoader()

    if args.init_config:
        if config_loader.init_config_file(preset=args.preset):
            print_success(f"配置文件已初始化: {config_loader.get_config_path()}")
        else:
            print_error("配置文件初始化失败")
        return

    if args.config_path:
        print(f"配置文件路径: {config_loader.get_config_path()}")
        return

    # 加载配置
    config = config_loader.load(preset=args.preset, config_path=args.config)

    # 处理缓存相关命令
    if args.cache_stats or args.clear_cache or args.cache_dir:
        core = PresearchCore(
            enable_npm='npm' in config.sources,
            enable_pypi='pypi' in config.sources,
            enable_docker='docker' in config.sources,
            cache_enabled=config.cache_enabled
        )

        if args.cache_stats:
            stats = core.get_cache_stats()
            if stats:
                print("## 缓存统计")
                print(f"总请求数: {stats['total_requests']}")
                print(f"内存命中: {stats['memory_hits']} ({stats['memory_hit_rate']})")
                print(f"磁盘命中: {stats['disk_hits']} ({stats['disk_hit_rate']})")
                print(f"总体命中率: {stats['overall_hit_rate']}")
                print(f"内存缓存大小: {stats['memory_size']}")
            else:
                print("缓存未启用")
            return

        if args.clear_cache:
            if core.clear_cache():
                print_success("缓存已清空")
            else:
                print_error("缓存未启用")
            return

        if args.cache_dir:
            if core.cache_manager:
                print(f"缓存目录: {core.cache_manager.get_cache_dir()}")
            else:
                print("缓存未启用")
            return

    # 处理历史记录相关命令
    if args.history or args.history_stats or args.clear_history or args.history_trends:
        core = PresearchCore(
            enable_npm='npm' in config.sources,
            enable_pypi='pypi' in config.sources,
            enable_docker='docker' in config.sources,
            cache_enabled=config.cache_enabled
        )

        if args.history:
            print(core.history_manager.format_for_display())
            return

        if args.history_stats:
            stats = core.history_manager.get_stats()
            print("## 搜索历史统计")
            print(f"总搜索次数: {stats['total_searches']}")
            print(f"唯一查询数: {stats['unique_queries']}")
            print(f"平均结果数: {stats['avg_results']}")
            print(f"缓存命中率: {stats['cache_hit_rate']}")
            if stats['top_queries']:
                print("\n热门查询:")
                for query, count in stats['top_queries']:
                    print(f"  - {query}: {count}次")
            if stats['source_usage']:
                print("\n数据源使用:")
                for source, count in stats['source_usage'].items():
                    print(f"  - {source}: {count}次")
            return

        if args.history_trends:
            trends = core.history_manager.get_trends(days=7)
            print("## 搜索趋势（最近7天）")
            print(f"趋势: {trends['trend']}")
            print(f"期间总搜索: {trends['total_in_period']}")
            if trends['daily_counts']:
                print("\n每日统计:")
                for date, count in sorted(trends['daily_counts'].items()):
                    print(f"  {date}: {count}次")
            return

        if args.clear_history:
            if core.history_manager.clear():
                print_success("搜索历史已清空")
            else:
                print_error("清空历史失败")
            return

    # 执行搜索
    if not args.query:
        parser.print_help()
        sys.exit(1)

    # 根据配置创建核心实例
    core = PresearchCore(
        enable_npm='npm' in config.sources,
        enable_pypi='pypi' in config.sources,
        enable_docker='docker' in config.sources,
        cache_enabled=config.cache_enabled and not args.no_cache,
        cache_ttl=config.cache_ttl,
        enable_translation=True,
        translation_api=True
    )

    try:
        print_info(f"搜索: {args.query}")

        # 根据输出格式选择搜索方法
        if args.format == 'json' and args.output:
            # JSON 输出使用原始结果
            result, raw_results = core.search_with_raw(args.query, use_cache=config.cache_enabled and not args.no_cache)
        else:
            result = core.search(args.query, use_cache=config.cache_enabled and not args.no_cache)
            raw_results = None

        # 处理趣味输出格式
        fun_formats = ['emoji', 'meme', 'poetry', 'fortune']
        if args.format in fun_formats:
            # 导入趣味输出插件
            from plugins.fun_outputs import (
                EmojiOutputPlugin, MemeOutputPlugin,
                PoetryOutputPlugin, FortuneCookieOutputPlugin
            )

            # 构建结果数据
            search_results = {
                'query': args.query,
                'github': {'items': []}  # 简化示例
            }

            # 根据格式选择插件
            if args.format == 'emoji':
                plugin = EmojiOutputPlugin()
            elif args.format == 'meme':
                plugin = MemeOutputPlugin()
            elif args.format == 'poetry':
                plugin = PoetryOutputPlugin()
            elif args.format == 'fortune':
                plugin = FortuneCookieOutputPlugin()

            plugin.initialize()

            # 解析结果提取项目信息
            import re
            projects = []
            for line in result.split('\n'):
                if '| [' in line and 'github.com' in line:
                    # 提取项目名称和stars
                    match = re.search(r'\[([^\]]+)\].*?(\d+(?:\.\d+)?[kM]?)\s*\|', line)
                    if match:
                        name = match.group(1).split('/')[-1]
                        stars_str = match.group(2)
                        # 转换k/M
                        if 'k' in stars_str:
                            stars = int(float(stars_str.replace('k', '')) * 1000)
                        elif 'M' in stars_str:
                            stars = int(float(stars_str.replace('M', '')) * 1000000)
                        else:
                            stars = int(stars_str) if stars_str.isdigit() else 0
                        projects.append({'name': name, 'stargazers_count': stars, 'description': ''})

            if projects:
                search_results['github']['items'] = projects[:5]
                result = plugin.format(search_results)

        # 输出到文件或控制台
        if args.output:
            if args.format == 'json' and raw_results:
                # JSON 格式输出原始结构化数据
                export_data = {
                    'query': raw_results.get('query', args.query),
                    'result_counts': raw_results.get('result_counts', {}),
                    'duration_ms': raw_results.get('duration_ms', 0),
                    'github': raw_results.get('github'),
                    'arxiv': raw_results.get('arxiv'),
                    'npm': raw_results.get('npm'),
                    'pypi': raw_results.get('pypi'),
                    'docker': raw_results.get('docker')
                }
            else:
                export_data = {
                    'query': args.query,
                    'results': result,
                    'config': config.to_dict()
                }
            if export_results(export_data, args.output, args.format):
                print_success(f"结果已导出到: {args.output}")
            else:
                print_error("导出失败")
        else:
            print(result)

    except Exception as e:
        print_error(f"搜索失败: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
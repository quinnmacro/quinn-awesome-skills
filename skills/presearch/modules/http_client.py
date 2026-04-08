#!/usr/bin/env python3
"""
HTTP客户端模块
使用 urllib 实现，无需外部依赖
"""

import json
import time
import urllib.request
import urllib.error
import sys


class HTTPClientError(Exception):
    """HTTP客户端错误基类"""
    pass


class NetworkError(HTTPClientError):
    """网络错误"""
    pass


class APIError(HTTPClientError):
    """API错误"""
    pass


class RateLimitError(APIError):
    """API速率限制错误"""
    pass


class HTTPClient:
    """HTTP客户端，使用 urllib 实现"""

    def __init__(self, max_retries=3, timeout=10):
        """
        初始化HTTP客户端

        Args:
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        self.max_retries = max_retries
        self.timeout = timeout

    def request(self, url, method='GET', headers=None, data=None):
        """
        执行HTTP请求

        Args:
            url: 请求URL
            method: HTTP方法
            headers: 请求头字典
            data: 请求数据

        Returns:
            响应内容（字符串）

        Raises:
            NetworkError: 网络错误
            APIError: API错误
            RateLimitError: 速率限制错误
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    # 指数退避
                    wait_time = 2 ** attempt
                    print(f"第{attempt}次重试，等待{wait_time}秒...", file=sys.stderr)
                    time.sleep(wait_time)

                # 构建请求
                req = urllib.request.Request(url, method=method)

                # 添加请求头
                if headers:
                    for key, value in headers.items():
                        req.add_header(key, value)

                # 添加请求数据
                if data:
                    if isinstance(data, str):
                        req.data = data.encode('utf-8')
                    else:
                        req.data = data

                # 发送请求
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return response.read().decode('utf-8')

            except urllib.error.HTTPError as e:
                # HTTP 错误
                if e.code == 429:
                    raise RateLimitError(f"API速率限制: {e.code} {e.reason}")
                elif e.code >= 500:
                    last_error = APIError(f"服务器错误: {e.code} {e.reason}")
                    if attempt == self.max_retries:
                        raise last_error
                    continue
                elif e.code >= 400:
                    raise APIError(f"客户端错误: {e.code} {e.reason}")

            except urllib.error.URLError as e:
                # 网络错误
                if "timed out" in str(e.reason).lower():
                    last_error = NetworkError(f"请求超时: {url}")
                elif "name or service not known" in str(e.reason).lower():
                    raise NetworkError(f"无法解析主机: {url}")
                else:
                    last_error = NetworkError(f"网络错误: {e.reason}")

                if attempt == self.max_retries:
                    raise last_error
                continue

            except Exception as e:
                last_error = NetworkError(f"未知错误: {str(e)}")
                if attempt == self.max_retries:
                    raise last_error
                continue

        # 所有重试都失败
        raise last_error

    def request_json(self, url, method='GET', headers=None, data=None):
        """
        执行HTTP请求并解析JSON响应

        Args:
            url: 请求URL
            method: HTTP方法
            headers: 请求头字典
            data: 请求数据

        Returns:
            解析后的JSON数据

        Raises:
            HTTPClientError: HTTP错误
            ValueError: JSON解析错误
        """
        response = self.request(url, method, headers, data)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # 尝试从HTML响应中提取错误信息
            if "<html" in response.lower() or "<!doctype" in response.lower():
                raise APIError(f"服务器返回HTML错误页面: {response[:200]}...")
            else:
                raise ValueError(f"JSON解析错误: {str(e)}，响应: {response[:200]}...")


def test_http_client():
    """测试HTTP客户端"""
    client = HTTPClient(max_retries=2, timeout=5)

    # 测试GitHub API
    print("测试GitHub API...")
    try:
        data = client.request_json("https://api.github.com/search/repositories?q=python&per_page=1")
        print(f"成功！找到 {data.get('total_count', 0)} 个仓库")
    except HTTPClientError as e:
        print(f"错误: {e}")

    # 测试不存在的URL
    print("\n测试不存在的URL...")
    try:
        client.request("https://nonexistent.example.com")
    except HTTPClientError as e:
        print(f"预期错误: {e}")


if __name__ == "__main__":
    test_http_client()

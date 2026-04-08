"""
Presearch TUI 主应用
"""

import sys
import os
import asyncio
from typing import Dict, List, Any, Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive
from textual.binding import Binding

# 添加模块路径
MODULES_PATH = os.environ.get('PRESEARCH_MODULES', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, MODULES_PATH)

from .widgets.search_input import SearchInput
from .widgets.result_list import ResultList, ResultItemWidget
from .widgets.detail_panel import DetailPanel
from .widgets.source_tabs import SourceTabs


class PresearchTUI(App):
    """
    Presearch 交互式 TUI

    特性:
    - 实时搜索 (防抖 300ms)
    - Vim 风格快捷键
    - 数据源切换
    - 详情面板
    """

    CSS_PATH = "styles/presearch.tcss"

    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("/", "focus_search", "搜索"),
        Binding("j", "cursor_down", "下一条"),
        Binding("k", "cursor_up", "上一条"),
        Binding("enter", "select", "选择"),
        Binding("d", "toggle_detail", "详情"),
        Binding("1", "source_github", "GitHub"),
        Binding("2", "source_npm", "npm"),
        Binding("3", "source_pypi", "PyPI"),
        Binding("4", "source_docker", "Docker"),
        Binding("5", "source_arxiv", "arXiv"),
        Binding("0", "source_all", "全部"),
        Binding("c", "clear", "清空"),
        Binding("r", "refresh", "刷新"),
        Binding("escape", "clear_focus", "取消"),
    ]

    # 响应式状态
    search_query = reactive("")
    is_loading = reactive(False)
    current_source = reactive("all")
    show_detail = reactive(True)

    def __init__(self):
        super().__init__()
        self._raw_results: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header()
        yield SearchInput()
        yield SourceTabs()
        yield ResultList()
        yield DetailPanel()
        yield Footer()

    def on_mount(self) -> None:
        """应用挂载"""
        self.title = "Presearch"
        self.sub_title = "智能开发资源搜索"

    # 搜索事件处理
    def on_search_input_search_submitted(self, event: SearchInput.SearchSubmitted) -> None:
        """处理搜索提交"""
        self.search_query = event.query
        self._perform_search(event.query)

    def on_search_input_search_cleared(self, event: SearchInput.SearchCleared) -> None:
        """处理搜索清空"""
        self.search_query = ""
        self._clear_results()

    def on_source_tabs_source_changed(self, event: SourceTabs.SourceChanged) -> None:
        """处理数据源切换"""
        self.current_source = event.source
        result_list = self.query_one(ResultList)
        result_list.set_source(event.source)

    def _perform_search(self, query: str) -> None:
        """执行搜索"""
        self.is_loading = True
        self.sub_title = f"搜索中: {query}..."

        # 使用 run_worker 在后台执行搜索
        def do_search():
            from presearch_core import PresearchCore
            core = PresearchCore()
            formatted, raw_results = core.search_with_raw(query, use_cache=True)
            return raw_results

        async def on_search_done(result):
            self._raw_results = result
            self._update_results(result)
            self.is_loading = False
            self.sub_title = f"搜索: {query}"

        async def on_search_error(error):
            self._show_error(str(error))
            self.is_loading = False
            self.sub_title = "搜索失败"

        # 在工作线程中执行搜索
        self.run_worker(do_search(), name="search", thread=True).then(on_search_done, on_search_error)

    def _update_results(self, raw_results: Dict[str, Any]) -> None:
        """更新结果列表"""
        result_list = self.query_one(ResultList)

        # 提取各数据源的结果
        results = {}

        # GitHub
        github_data = raw_results.get('github', {})
        if isinstance(github_data, dict) and 'items' in github_data:
            results['github'] = github_data['items'][:10]

        # npm
        npm_data = raw_results.get('npm', {})
        if isinstance(npm_data, dict) and 'objects' in npm_data:
            results['npm'] = [obj.get('package', {}) for obj in npm_data.get('objects', [])[:10]]

        # PyPI
        pypi_data = raw_results.get('pypi', {})
        if isinstance(pypi_data, dict) and 'packages' in pypi_data:
            results['pypi'] = pypi_data.get('packages', [])[:10]

        # Docker
        docker_data = raw_results.get('docker', {})
        if isinstance(docker_data, dict) and 'results' in docker_data:
            results['docker'] = docker_data.get('results', [])[:10]

        # arXiv
        arxiv_data = raw_results.get('arxiv', [])
        if isinstance(arxiv_data, list):
            results['arxiv'] = arxiv_data[:5]

        result_list.update_results(results)

        # 更新数据源标签计数
        source_tabs = self.query_one(SourceTabs)
        counts = {source: len(items) for source, items in results.items()}
        source_tabs.update_counts(counts)

    def _clear_results(self) -> None:
        """清空结果"""
        result_list = self.query_one(ResultList)
        result_list.update_results({})

        detail_panel = self.query_one(DetailPanel)
        detail_panel.clear()

        source_tabs = self.query_one(SourceTabs)
        source_tabs.update_counts({})

        self.sub_title = "智能开发资源搜索"

    def _show_error(self, message: str) -> None:
        """显示错误"""
        self.notify(f"搜索失败: {message}", severity="error")

    # 结果选择处理
    def on_result_list_item_selected(self, event: ResultList.ItemSelected) -> None:
        """处理结果项选择"""
        detail_panel = self.query_one(DetailPanel)
        detail_panel.update(event.item, event.source)

    # 快捷键动作
    def action_focus_search(self) -> None:
        """聚焦搜索框"""
        search_input = self.query_one(SearchInput)
        search_input.focus_input()

    def action_cursor_down(self) -> None:
        """向下移动光标"""
        # 文本化列表会自动处理 j/k
        pass

    def action_cursor_up(self) -> None:
        """向上移动光标"""
        pass

    def action_select(self) -> None:
        """选择当前项"""
        # Enter 键会自动触发列表选择
        pass

    def action_toggle_detail(self) -> None:
        """切换详情面板"""
        detail_panel = self.query_one(DetailPanel)
        detail_panel.toggle()

    def action_source_github(self) -> None:
        """切换到 GitHub"""
        self._set_source("github")

    def action_source_npm(self) -> None:
        """切换到 npm"""
        self._set_source("npm")

    def action_source_pypi(self) -> None:
        """切换到 PyPI"""
        self._set_source("pypi")

    def action_source_docker(self) -> None:
        """切换到 Docker"""
        self._set_source("docker")

    def action_source_arxiv(self) -> None:
        """切换到 arXiv"""
        self._set_source("arxiv")

    def action_source_all(self) -> None:
        """显示全部"""
        self._set_source("all")

    def _set_source(self, source: str) -> None:
        """设置当前数据源"""
        self.current_source = source
        result_list = self.query_one(ResultList)
        result_list.set_source(source)

        source_tabs = self.query_one(SourceTabs)
        source_tabs.set_source(source)

    def action_clear(self) -> None:
        """清空搜索"""
        search_input = self.query_one(SearchInput)
        search_input.clear()

    def action_refresh(self) -> None:
        """刷新搜索"""
        if self.search_query:
            self._perform_search(self.search_query)

    def action_clear_focus(self) -> None:
        """取消焦点"""
        self.set_focus(None)


def run_tui():
    """运行 TUI 应用"""
    app = PresearchTUI()
    app.run()


if __name__ == "__main__":
    run_tui()

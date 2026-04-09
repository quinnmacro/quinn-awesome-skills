"""
结果列表组件 - 展示搜索结果
"""

from typing import List, Dict, Any, Optional
from textual.widget import Widget
from textual.message import Message
from textual.widgets import ListView, ListItem, Static, Label
from textual.reactive import reactive
from textual.containers import Vertical


class ResultItemWidget(ListItem):
    """
    单个结果项组件
    """

    def __init__(self, data: Dict[str, Any], source: str, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.source = source

    def compose(self):
        # 项目名称
        name = self.data.get('name', self.data.get('full_name', self.data.get('title', 'Unknown')))
        yield Label(self._format_name(name), classes="name")

        # 描述
        description = self.data.get('description', self.data.get('short_description', 'No description'))
        if len(description) > 80:
            description = description[:77] + "..."
        yield Label(description, classes="description")

        # 元信息行
        meta = self._format_meta()
        yield Label(meta, classes="meta")

    def _format_name(self, name: str) -> str:
        """格式化项目名称"""
        health = self._get_health_indicator()
        return f"{name} {health}"

    def _get_health_indicator(self) -> str:
        """获取健康度指示器"""
        stars = self.data.get('stars', self.data.get('stargazers_count', 0))
        updated = self.data.get('updated_at', '')

        # 简化版健康度
        is_active = self._is_active(updated)

        if stars >= 1000 and is_active:
            return "🟢"  # 优秀
        elif stars >= 100 and is_active:
            return "🟡"  # 良好
        elif stars >= 10:
            return "🟠"  # 一般
        return "🔴"  # 新项目

    def _is_active(self, updated_at: str) -> bool:
        """检查项目是否活跃"""
        import datetime
        if not updated_at:
            return False
        try:
            dt = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_ago = (datetime.datetime.now(datetime.timezone.utc) - dt).days
            return days_ago < 180
        except:
            return False

    def _format_meta(self) -> str:
        """格式化元信息"""
        parts = []

        # Stars
        stars = self.data.get('stars', self.data.get('stargazers_count', 0))
        if stars >= 1000:
            parts.append(f"★ {stars/1000:.1f}k")
        else:
            parts.append(f"★ {stars}")

        # Language
        language = self.data.get('language')
        if language:
            parts.append(f"│ {language}")

        # Source
        parts.append(f"│ {self.source.upper()}")

        return "  ".join(parts)


class ResultList(Widget):
    """
    结果列表组件

    特性:
    - 分数据源显示
    - 键盘导航
    - 选中高亮
    """

    DEFAULT_CSS = """
    ResultList {
        height: 1fr;
        overflow-y: auto;
    }

    ResultList ListView {
        height: auto;
    }
    """

    class ItemSelected(Message):
        """结果项选中消息"""
        def __init__(self, item: Dict[str, Any], source: str):
            super().__init__()
            self.item = item
            self.source = source

    # 响应式数据
    results = reactive({})
    current_source = reactive("all")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items: List[ResultItemWidget] = []

    def compose(self):
        yield ListView(id="result-list")

    def on_mount(self):
        """组件挂载"""
        pass

    def watch_results(self, results: Dict[str, List[Dict]]) -> None:
        """监听结果变化"""
        self._render_results()

    def watch_current_source(self, source: str) -> None:
        """监听数据源变化"""
        self._render_results()

    def update_results(self, results: Dict[str, List[Dict]]) -> None:
        """更新结果"""
        self.results = results

    def _render_results(self) -> None:
        """渲染结果列表"""
        try:
            list_view = self.query_one(ListView)
        except:
            return

        # 清空现有项
        self._items.clear()
        list_view.clear()

        # 获取要显示的结果
        if self.current_source == "all":
            sources_to_show = list(self.results.keys())
        else:
            sources_to_show = [self.current_source] if self.current_source in self.results else []

        # 创建结果项
        for source in sources_to_show:
            items = self.results.get(source, [])
            for item_data in items:
                result_item = ResultItemWidget(item_data, source)
                self._items.append(result_item)
                list_view.append(result_item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """列表项选中"""
        item = event.item
        if isinstance(item, ResultItemWidget):
            self.post_message(self.ItemSelected(item.data, item.source))

    def set_source(self, source: str) -> None:
        """设置当前数据源"""
        self.current_source = source

    def get_item_count(self) -> int:
        """获取结果数量"""
        return len(self._items)

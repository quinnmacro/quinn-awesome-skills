"""
详情面板组件 - 显示选中项目的详细信息
"""

from typing import Dict, Any, Optional
from textual.widget import Widget
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.containers import Vertical, ScrollableContainer


class DetailPanel(Widget):
    """
    详情面板

    显示选中项目的完整信息
    """

    DEFAULT_CSS = """
    DetailPanel {
        dock: right;
        width: 40;
        min-width: 30;
        max-width: 50;
        background: $panel;
        border-left: tall $primary;
        padding: 1 2;
        overflow-y: auto;
    }

    DetailPanel.hidden {
        display: none;
    }

    DetailPanel .title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    DetailPanel .section {
        margin-top: 1;
        padding-top: 1;
        border-top: dashed $primary;
    }

    DetailPanel .label {
        color: $text-muted;
    }

    DetailPanel .value {
        color: $text;
    }

    DetailPanel .url {
        color: $primary;
        text-style: underline;
    }
    """

    item_data = reactive(None)
    item_source = reactive(None)
    visible = reactive(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self):
        with ScrollableContainer():
            yield Static(self._get_empty_content(), id="detail-content")

    def watch_item_data(self, data: Dict[str, Any]) -> None:
        """监听数据变化"""
        self._render()

    def watch_visible(self, visible: bool) -> None:
        """监听可见性变化"""
        self.set_class(not visible, "hidden")

    def update(self, data: Dict[str, Any], source: str) -> None:
        """更新详情"""
        self.item_data = data
        self.item_source = source

    def _render(self) -> None:
        """渲染详情"""
        try:
            content = self.query_one("#detail-content", Static)
        except:
            return

        if not self.item_data:
            content.update(self._get_empty_content())
            return

        content.update(self._format_detail())

    def _format_detail(self) -> str:
        """格式化详情内容"""
        data = self.item_data
        source = self.item_source or "unknown"

        lines = []

        # 标题
        name = data.get('name', data.get('full_name', data.get('title', 'Unknown')))
        lines.append(f"[bold cyan]{name}[/bold cyan]")
        lines.append("")

        # 描述
        description = data.get('description', data.get('short_description', 'No description'))
        lines.append(f"{description}")
        lines.append("")

        # 分隔线
        lines.append("[dim]─────────────────────────[/dim]")
        lines.append("")

        # 基本信息
        stars = data.get('stars', data.get('stargazers_count', 0))
        if stars:
            lines.append(f"[yellow]★ Stars:[/yellow] {self._format_number(stars)}")

        language = data.get('language')
        if language:
            lines.append(f"[blue]Language:[/blue] {language}")

        # URL
        url = data.get('html_url', data.get('url', data.get('link', '')))
        if url:
            lines.append(f"[link]{url}[/link]")

        # 更新时间
        updated = data.get('updated_at', data.get('published', ''))
        if updated:
            lines.append(f"[dim]Updated: {self._format_date(updated)}[/dim]")

        # 健康度
        health = self._calculate_health()
        health_label = {
            'excellent': '🟢 优秀',
            'good': '🟡 良好',
            'fair': '🟠 一般',
            'new': '🔴 新项目'
        }
        lines.append(f"[bold]Health:[/bold] {health_label.get(health, 'Unknown')}")

        # 来源
        lines.append("")
        lines.append(f"[dim]Source: {source.upper()}[/dim]")

        return "\n".join(lines)

    def _format_number(self, num: int) -> str:
        """格式化数字"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}k"
        return str(num)

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        import datetime
        try:
            dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str

    def _calculate_health(self) -> str:
        """计算健康度"""
        if not self.item_data:
            return 'unknown'

        stars = self.item_data.get('stars', self.item_data.get('stargazers_count', 0))
        updated = self.item_data.get('updated_at', '')

        is_active = False
        if updated:
            import datetime
            try:
                dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                days_ago = (datetime.datetime.now(datetime.timezone.utc) - dt).days
                is_active = days_ago < 180
            except:
                pass

        if stars >= 1000 and is_active:
            return 'excellent'
        elif stars >= 100 and is_active:
            return 'good'
        elif stars >= 10:
            return 'fair'
        return 'new'

    def _get_empty_content(self) -> str:
        """空状态内容"""
        return """
[dim]─────────────────────────[/dim]

  [dim]选择一个项目查看详情[/dim]

  [dim]快捷键:[/dim]
  [dim]  j/k - 上下导航[/dim]
  [dim]  Enter - 选择项目[/dim]
  [dim]  d - 切换详情面板[/dim]

[dim]─────────────────────────[/dim]
"""

    def clear(self) -> None:
        """清空详情"""
        self.item_data = None
        self.item_source = None
        try:
            content = self.query_one("#detail-content", Static)
            content.update(self._get_empty_content())
        except:
            pass

    def toggle(self) -> None:
        """切换可见性"""
        self.visible = not self.visible

"""
数据源标签组件 - 切换不同数据源
"""

from typing import Optional
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button
from textual.containers import Horizontal


class SourceTabs(Widget):
    """
    数据源标签组件

    特性:
    - 点击切换数据源
    - 键盘快捷键支持
    """

    DEFAULT_CSS = """
    SourceTabs {
        dock: top;
        height: 3;
        margin: 0 2;
        background: $panel;
        align: center middle;
    }

    SourceTabs Horizontal {
        align: center middle;
    }

    SourceTabs Button {
        margin: 0 1;
        min-width: 8;
        background: transparent;
        border: none;
        color: $text-muted;
    }

    SourceTabs Button.active {
        background: $primary;
        color: $text-on-primary;
    }

    SourceTabs Button:hover {
        background: $primary-darken-1;
        color: $text-on-primary;
    }
    """

    class SourceChanged(Message):
        """数据源切换消息"""
        def __init__(self, source: str):
            super().__init__()
            self.source = source

    current_source = reactive("all")

    SOURCES = [
        ("all", "全部 (0)"),
        ("github", "GitHub (1)"),
        ("npm", "npm (2)"),
        ("pypi", "PyPI (3)"),
        ("docker", "Docker (4)"),
        ("arxiv", "arXiv (5)"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buttons = {}

    def compose(self):
        with Horizontal():
            for source_id, label in self.SOURCES:
                btn = Button(label, id=f"tab-{source_id}", classes="source-tab")
                self._buttons[source_id] = btn
                yield btn

    def on_mount(self) -> None:
        """组件挂载后设置初始状态"""
        self._update_button_styles()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        button_id = event.button.id
        if button_id and button_id.startswith("tab-"):
            source = button_id[4:]
            self.current_source = source
            self._update_button_styles()
            self.post_message(self.SourceChanged(source))

    def _update_button_styles(self) -> None:
        """更新按钮样式"""
        for source_id, btn in self._buttons.items():
            if source_id == self.current_source:
                btn.add_class("active")
            else:
                btn.remove_class("active")

    def set_source(self, source: str) -> None:
        """设置当前数据源"""
        if source in [s[0] for s in self.SOURCES]:
            self.current_source = source
            self._update_button_styles()

    def update_counts(self, counts: dict) -> None:
        """更新标签计数"""
        for source_id, btn in self._buttons.items():
            if source_id == "all":
                total = sum(counts.values())
                btn.label = f"全部 ({total})"
            else:
                count = counts.get(source_id, 0)
                # 更新标签文本
                label_map = {
                    "github": "GitHub",
                    "npm": "npm",
                    "pypi": "PyPI",
                    "docker": "Docker",
                    "arxiv": "arXiv"
                }
                base_label = label_map.get(source_id, source_id)
                btn.label = f"{base_label} ({count})"

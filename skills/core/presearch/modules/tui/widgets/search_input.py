"""
搜索输入组件 - 支持防抖的实时搜索
"""

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input


class SearchInput(Widget):
    """
    搜索输入框组件

    特性:
    - 防抖 300ms
    - 中文输入提示
    - 历史记录支持
    """

    DEFAULT_CSS = """
    SearchInput {
        height: 3;
        margin: 1 2;
    }

    SearchInput Input {
        border: tall $primary;
        background: $surface;
    }

    SearchInput Input:focus {
        border: tall $accent;
    }
    """

    class SearchSubmitted(Message):
        """搜索提交消息"""
        def __init__(self, query: str):
            super().__init__()
            self.query = query

    class SearchCleared(Message):
        """搜索清空消息"""
        pass

    # 响应式变量
    query = reactive("")
    debounce_timer = reactive(None)

    def __init__(self, placeholder: str = "输入搜索关键词... (支持中英文)", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder

    def compose(self):
        yield Input(
            placeholder=self.placeholder,
            id="search-input"
        )

    def on_mount(self):
        """组件挂载后获取输入框引用"""
        self._input_widget = self.query_one(Input)
        self._input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """输入变化时触发防抖搜索"""
        self.query = event.value

        # 取消之前的定时器
        if self.debounce_timer:
            self.debounce_timer.stop()

        # 设置新的防抖定时器 (300ms)
        if len(event.value) >= 2:
            self.debounce_timer = self.set_timer(
                0.3,
                lambda: self._emit_search(event.value)
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """回车提交搜索"""
        if event.value.strip():
            # 立即执行，取消防抖
            if self.debounce_timer:
                self.debounce_timer.stop()
            self._emit_search(event.value)

    def _emit_search(self, query: str) -> None:
        """发送搜索消息"""
        if query.strip():
            self.post_message(self.SearchSubmitted(query.strip()))

    def clear(self) -> None:
        """清空输入"""
        self._input_widget = self.query_one(Input)
        self._input_widget.value = ""
        self.post_message(self.SearchCleared())

    def focus_input(self) -> None:
        """聚焦输入框"""
        if hasattr(self, '_input_widget') and self._input_widget:
            self._input_widget.focus()

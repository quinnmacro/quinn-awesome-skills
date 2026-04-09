"""
TUI 模块 - 基于 Textual 的交互式界面

使用方法:
    from tui import PresearchTUI

    app = PresearchTUI()
    app.run()
"""

from .app import PresearchTUI, run_tui

__all__ = ['PresearchTUI', 'run_tui']

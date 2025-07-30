"""CodingConverse MCP Server

一个MCP服务，为AI代码编辑器提供与用户对话的能力。
"""

__version__ = "2.0.0"

from .dialog_pyqt import show_message_dialog

__all__ = ['show_message_dialog']
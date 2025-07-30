#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5/PyQt6 实现的现代化消息对话框

提供更专业和美观的UI界面
"""

import os
import sys

# 确保正确的编码设置
if sys.platform.startswith('win'):
    import locale
    # 设置控制台编码为UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # 设置环境变量确保Qt使用UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

from typing import Tuple, Optional

# 尝试导入PyQt
try:
    # 优先尝试PyQt6
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
        QLabel, QTextEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QPalette, QColor
    PYQT_VERSION = 6
except ImportError:
    try:
        # 回退到PyQt5
        from PyQt5.QtWidgets import (
            QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
            QLabel, QTextEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
        )
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QPalette, QColor
        PYQT_VERSION = 5
    except ImportError:
        raise ImportError("PyQt5 或 PyQt6 未安装")


class ModernMessageDialog(QDialog):
    """现代化的消息对话框"""
    
    def __init__(self, message: str, title: str = "消息对话框", placeholder: str = "按Ctrl+Enter键进行回复", parent=None):
        super().__init__(parent)
        self.message = message
        self.title = title
        self.placeholder = "按Ctrl+Enter键进行回复"
        self.response = ""
        self.ignored = False
        
        # 用于拖拽窗口的变量
        self.drag_position = None
        
        # 设置窗口标题（虽然是无边框窗口，但设置标题有助于任务栏显示）
        self.setWindowTitle(self.title)
        
        self.setup_ui()
        self.setup_styles()
        self.center_window()
        
    def setup_ui(self):
        """设置UI界面"""
        # 去掉标题栏，设置为无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(600, 500)  # 增大窗口尺寸
        self.setModal(True)
        
        # 主布局 - 适应更大窗口的间距
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 增加间距
        main_layout.setContentsMargins(30, 25, 30, 25)  # 增加边距
        
        # 添加自定义标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel(self.title)
        title_font = QFont("Microsoft YaHei UI", 11)
        try:
            if PYQT_VERSION == 6:
                title_font.setWeight(QFont.Weight.Bold)
            else:  # PyQt5
                title_font.setWeight(QFont.Bold)
        except AttributeError:
            title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 5px 0px;
                margin-bottom: 10px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_font = QFont("Arial", 14)
        try:
            if PYQT_VERSION == 6:
                close_font.setWeight(QFont.Weight.Bold)
            else:  # PyQt5
                close_font.setWeight(QFont.Bold)
        except AttributeError:
            close_font.setBold(True)
        close_button.setFont(close_font)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6c757d;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #495057;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
        """)
        close_button.clicked.connect(self.ignore_response)
        title_layout.addWidget(close_button)
        
        main_layout.addLayout(title_layout)
        
        # 消息标签 - 增大显示区域
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message_label.setFont(QFont("Microsoft YaHei", 11))  # 增大字体
        self.message_label.setMinimumHeight(200)  # 设置最小高度
        self.message_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background-color: #f8f9fa;
                padding: 20px;  /* 增大内边距 */
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        main_layout.addWidget(self.message_label, 1)  # 设置拉伸因子
        

        
        # 文本输入框 - 增大尺寸
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.placeholder)
        self.text_edit.setFont(QFont("Microsoft YaHei", 10))  # 增大字体
        self.text_edit.setMinimumHeight(120)  # 增大高度
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;  /* 增大圆角 */
                padding: 12px;  /* 增大内边距 */
                background-color: white;
                selection-background-color: #007bff;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
            }
        """)
        main_layout.addWidget(self.text_edit, 1)  # 设置拉伸因子
        

        self.setLayout(main_layout)
        
        # 设置焦点
        QTimer.singleShot(100, self.text_edit.setFocus)
        
    def setup_styles(self):
        """设置整体样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #dee2e6;  /* 添加边框替代标题栏 */
                border-radius: 8px;
            }
        """)
        
    def center_window(self):
        """居中显示窗口"""
        if QApplication.instance():
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
    
    def submit_response(self):
        """提交回复"""
        self.response = self.text_edit.toPlainText().strip()
        self.ignored = False
        self.accept()
    
    def ignore_response(self):
        """忽略消息"""
        self.response = ""
        self.ignored = True
        self.accept()
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 如果按下Shift+Enter，则插入换行
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                cursor = self.text_edit.textCursor()
                cursor.insertText("\n")
                event.accept()
                return
            # 否则发送消息（普通回车键）
            event.accept()
            self.submit_response()
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.ignore_response()  # ESC键关闭对话框
            return
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽"""
        if PYQT_VERSION == 6:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        else:  # PyQt5
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽窗口"""
        if PYQT_VERSION == 6:
            if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
        else:  # PyQt5
            if event.buttons() == Qt.LeftButton and self.drag_position is not None:
                self.move(event.globalPos() - self.drag_position)
                event.accept()


def show_message_dialog(message: str, title: str = "消息对话框", placeholder: str = "按Ctrl+Enter键进行回复") -> str:
    """显示消息对话框
    
    Args:
        message: 要显示的消息内容
        title: 对话框标题
        placeholder: 输入框占位符文本
        
    Returns:
        str: 用户回复内容，如果用户取消则返回空字符串
    """
    # 确保有QApplication实例
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app_created = True
        
        # 设置应用程序属性以支持中文显示
        try:
            if PYQT_VERSION == 6:
                app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
                app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            else:  # PyQt5
                app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
                app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # 如果属性不存在，忽略错误
            pass
        
        # 设置默认字体以确保中文正确显示
        if sys.platform.startswith('win'):
            font = QFont("Microsoft YaHei UI", 9)
            try:
                if PYQT_VERSION == 6:
                    font.setStyleHint(QFont.StyleHint.SansSerif)
                else:  # PyQt5
                    font.setStyleHint(QFont.SansSerif)
            except AttributeError:
                pass
            app.setFont(font)
    else:
        app_created = False
    
    try:
        # 创建并显示对话框
        dialog = ModernMessageDialog(message, title, placeholder)
        dialog.exec()
        
        return dialog.response if not dialog.ignored else ""
        
    finally:
        # 如果是我们创建的应用实例，则退出
        if app_created:
            app.quit()


if __name__ == "__main__":
    # 测试代码
    test_message = """这是一个PyQt实现的现代化对话框！

特性：
• 现代化的Material Design风格
• 流畅的动画效果
• 专业的UI组件
• 更好的字体渲染
特性：
• 现代化的Material Design风格
• 流畅的动画效果
• 专业的UI组件
• 更好的字体渲染
请输入您的反馈："""
    
    response = show_message_dialog(
        message=test_message,
        title="PyQt对话框测试",
        placeholder="按Ctrl+Enter键进行回复"
    )
    
    if response:
        print(f"用户回复：{response}")
    else:
        print("Continue")
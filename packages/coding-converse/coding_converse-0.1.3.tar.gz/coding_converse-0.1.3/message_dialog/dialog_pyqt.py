#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 实现的现代化消息对话框
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

# 优先尝试PyQt6
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

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
        
        # 设置窗口图标
        self.setup_icon()
        
        self.setup_ui()
        self.setup_styles()
        self.center_window()
    
    def setup_icon(self):
        """设置窗口图标"""
        try:
            # 获取图标文件路径
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
            if os.path.exists(icon_path):
                # 创建SVG渲染器
                renderer = QSvgRenderer(icon_path)
                # 创建像素图
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.GlobalColor.transparent)
                # 渲染SVG到像素图
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                # 设置图标
                icon = QIcon(pixmap)
                self.setWindowIcon(icon)
        except Exception as e:
            # 如果加载图标失败，使用默认图标
            pass
        
    def setup_ui(self):
        """设置UI界面"""
        # 去掉标题栏，设置为无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(500, 450)  # 增加高度以容纳更大的内容区域
        self.setModal(True)
        
        # 主布局 - 调整间距分配
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)  # 减少整体间距
        main_layout.setContentsMargins(20, 15, 20, 20)  # 减少顶部边距
        
        # 更紧凑的标题栏
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title_label = QLabel(self.title)
        title_font = QFont("Segoe UI", 12)  # 减小字体
        try:
            title_font.setWeight(QFont.Weight.Medium)
        except AttributeError:
            title_font.setBold(False)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #374151;
                padding: 0px;
                margin: 0px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 更小的关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)  # 减小按钮尺寸
        close_font = QFont("Segoe UI", 14)  # 减小字体
        close_button.setFont(close_font)
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9CA3AF;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #F3F4F6;
                color: #374151;
            }
            QPushButton:pressed {
                background: #E5E7EB;
            }
        """)
        close_button.clicked.connect(self.ignore_response)
        title_layout.addWidget(close_button)
        
        main_layout.addLayout(title_layout)
        
        # 添加标题下方的小间距
        main_layout.addSpacing(8)
        
        # ChatGPT风格的消息区域（支持滚动）- 增加占比
        self.message_display = QTextEdit()
        self.message_display.setPlainText(self.message)
        self.message_display.setReadOnly(True)
        self.message_display.setFont(QFont("Segoe UI", 10))
        self.message_display.setMinimumHeight(220)  # 增加最小高度
        self.message_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.message_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_display.setStyleSheet("""
            QTextEdit {
                color: #374151;
                background: #F9FAFB;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                line-height: 1.5;
            }
            QTextEdit QScrollBar:vertical {
                background: #F3F4F6;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 4px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        main_layout.addWidget(self.message_display, 2)  # 给消息区域更大的拉伸权重
        
        # 添加消息区域和输入框之间的间距
        main_layout.addSpacing(8)
        
        # ChatGPT风格的输入框 - 增加占比
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.placeholder)
        self.text_edit.setFont(QFont("Segoe UI", 10))
        self.text_edit.setMinimumHeight(100)  # 增加最小高度
        self.text_edit.setMaximumHeight(140)  # 增加最大高度
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 12px;
                background: white;
                selection-background-color: #3B82F6;
                color: #374151;
            }
            QTextEdit:focus {
                border: 1px solid #3B82F6;
                outline: none;
            }
            QTextEdit:hover {
                border-color: #9CA3AF;
            }
        """)
        main_layout.addWidget(self.text_edit)
        

        self.setLayout(main_layout)
        
        # 设置焦点
        QTimer.singleShot(100, self.text_edit.setFocus)
        
    def setup_styles(self):
        """设置整体样式"""
        self.setStyleSheet("""
            QDialog {
                background: white;
                border: none;
                border-radius: 12px;
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
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
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # 如果属性不存在，忽略错误
            pass
        
        # 设置应用程序级别的图标
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
            if os.path.exists(icon_path):
                renderer = QSvgRenderer(icon_path)
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                app_icon = QIcon(pixmap)
                app.setWindowIcon(app_icon)
        except Exception:
            pass
        
        # 设置默认字体以确保中文正确显示
        if sys.platform.startswith('win'):
            font = QFont("Microsoft YaHei UI", 9)
            try:
                font.setStyleHint(QFont.StyleHint.SansSerif)
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
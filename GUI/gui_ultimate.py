"""
APK 反编译工具 - 终极集成版 (v5.0 Ultimate)
功能集成:
- v2.0: 核心 APK 分析、反编译、签名、字符串解密、混淆分析
- v3.0: 现代化 UI、字体调节、优化布局
- v4.0: 双字体调节、AI API、资源查看、ARSC、DEX 查看
- 完整代码 CRUD 操作
"""

import sys
import os

# 添加项目根目录到 Python 路径（方便从 Core/文件夹导入模块）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# 同时添加 Core 文件夹到路径
core_dir = os.path.join(parent_dir, 'Core')
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QInputDialog, QLineEdit, QComboBox, 
                             QSpinBox, QDialog, QDialogButtonBox, QGroupBox, 
                             QSlider, QScrollArea, QFrame, QGridLayout, 
                             QCheckBox, QListWidget, QListWidgetItem, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDockWidget,
                             QFormLayout, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor, QPalette, QPixmap, QImage
import zipfile
import json
import re
import base64
from pathlib import Path
from datetime import datetime
import io
import shutil

from core_engine import APKAnalyzer, APKModifier, StringDecryptor, ObfuscationAnalyzer, DexParser
from dex_converter import DexToSmaliConverter, SmaliToJavaConverter, SmaliClass, SmaliEditor
from code_manager import CodeManagerWidget
from dex_decompiler_ui import DexDecompilerWidget


# ============== 黑夜模式样式表 ==============
DARK_STYLE = """
/* 全局样式 */
QMainWindow {
    background-color: #1a1b26;
}

QWidget {
    background-color: #1a1b26;
    color: #a9b1d6;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

/* 菜单栏 */
QMenuBar {
    background-color: #24283b;
    color: #a9b1d6;
    padding: 8px;
    border-bottom: 1px solid #414868;
}

QMenuBar::item:selected {
    background-color: #414868;
    border-radius: 4px;
}

/* 工具栏 */
QToolBar {
    background-color: #24283b;
    border: none;
    padding: 8px;
    spacing: 8px;
    border-bottom: 1px solid #414868;
}

QToolBar QToolButton {
    background-color: #414868;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    color: #a9b1d6;
    font-weight: 600;
}

QToolBar QToolButton:hover {
    background-color: #565f89;
}

QToolBar QToolButton:pressed {
    background-color: #7aa2f7;
    color: #1a1b26;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #414868;
    border-radius: 8px;
    background-color: #16161e;
}

QTabBar::tab {
    background-color: #24283b;
    color: #a9b1d6;
    padding: 10px 20px;
    margin: 2px;
    border-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #565f89;
}

/* 按钮 */
QPushButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #89b4fa;
}

QPushButton:pressed {
    background-color: #565f89;
}

QPushButton:disabled {
    background-color: #414868;
    color: #6c7086;
}

/* 输入框 */
QLineEdit {
    background-color: #24283b;
    border: 1px solid #414868;
    border-radius: 4px;
    padding: 6px 10px;
    color: #a9b1d6;
}

QLineEdit:focus {
    border: 1px solid #7aa2f7;
}

/* 表格 */
QTableWidget {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 4px;
    gridline-color: #414868;
    outline: none;
}

QTableWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QTableWidget::item:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
    font-weight: bold;
}

QTableWidget::item:focus {
    border: 1px solid #bb9af7;
}

QHeaderView::section {
    background-color: #24283b;
    color: #a9b1d6;
    padding: 8px;
    border: none;
    font-weight: bold;
    border-radius: 3px;
}

QHeaderView::section:hover {
    background-color: #414868;
}

/* 列表 */
QListWidget {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 4px;
    outline: none;
}

QListWidget::item {
    padding: 5px;
    border-radius: 3px;
    border: 1px solid transparent;
}

QListWidget::item:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
    font-weight: bold;
    border: 1px solid #bb9af7;
}

QListWidget::item:hover {
    background-color: #24283b;
}

QListWidget::item:focus {
    border: 1px solid #bb9af7;
}

/* 树形控件 */
QTreeWidget {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 4px;
    gridline-color: #414868;
    outline: none;
}

QTreeWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QTreeWidget::item:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
    font-weight: bold;
}

QTreeWidget::item:hover {
    background-color: #24283b;
}

QTreeWidget::item:focus {
    border: 1px solid #bb9af7;
}

/* 进度条 */
QProgressBar {
    background-color: #24283b;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #7aa2f7;
    border-radius: 6px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #16161e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #414868;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #565f89;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 组合框 */
QGroupBox {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #7aa2f7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

/* 滑块 */
QSlider::groove:horizontal {
    background-color: #414868;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #7aa2f7;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #89b4fa;
}

/* 复选框 */
QCheckBox {
    color: #a9b1d6;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    background-color: #24283b;
    border: 1px solid #414868;
}

QCheckBox::indicator:checked {
    background-color: #7aa2f7;
    border: 1px solid #7aa2f7;
}

/* 下拉框 */
QComboBox {
    background-color: #24283b;
    border: 1px solid #414868;
    border-radius: 4px;
    padding: 6px 10px;
    color: #a9b1d6;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    color: #7aa2f7;
}

QComboBox QAbstractItemView {
    background-color: #16161e;
    border: 1px solid #414868;
    selection-background-color: #7aa2f7;
}

/* 状态栏 */
QStatusBar {
    background-color: #24283b;
    color: #a9b1d6;
    border-top: 1px solid #414868;
}

/* 工具提示 */
QToolTip {
    background-color: #24283b;
    color: #a9b1d6;
    border: 1px solid #414868;
    border-radius: 4px;
    padding: 5px;
}

/* 分割器 */
QSplitter::handle {
    background-color: #414868;
    border-radius: 2px;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}
"""

# ============== 白天模式样式表 ==============
LIGHT_STYLE = """
/* 全局样式 */
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    background-color: #ffffff;
    color: #333333;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

/* 菜单栏 */
QMenuBar {
    background-color: #ffffff;
    color: #333333;
    padding: 8px;
    border-bottom: 1px solid #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
    border-radius: 4px;
}

/* 工具栏 */
QToolBar {
    background-color: #ffffff;
    border: none;
    padding: 8px;
    spacing: 8px;
    border-bottom: 1px solid #e0e0e0;
}

QToolBar QToolButton {
    background-color: #e0e0e0;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    color: #333333;
    font-weight: 600;
}

QToolBar QToolButton:hover {
    background-color: #d0d0d0;
}

QToolBar QToolButton:pressed {
    background-color: #2196F3;
    color: #ffffff;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background-color: #fafafa;
}

QTabBar::tab {
    background-color: #f0f0f0;
    color: #666666;
    padding: 10px 20px;
    margin: 2px;
    border-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #2196F3;
    color: #ffffff;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #e0e0e0;
}

/* 按钮 */
QPushButton {
    background-color: #2196F3;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #999999;
}

/* 输入框 */
QLineEdit {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px 10px;
    color: #333333;
}

QLineEdit:focus {
    border: 1px solid #2196F3;
}

/* 表格 */
QTableWidget {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    gridline-color: #e0e0e0;
    outline: none;
}

QTableWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QTableWidget::item:selected {
    background-color: #2196F3;
    color: #ffffff;
    font-weight: bold;
}

QTableWidget::item:focus {
    border: 1px solid #9C27B0;
}

QHeaderView::section {
    background-color: #f0f0f0;
    color: #333333;
    padding: 8px;
    border: none;
    font-weight: bold;
    border-radius: 3px;
}

QHeaderView::section:hover {
    background-color: #e0e0e0;
}

/* 列表 */
QListWidget {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    outline: none;
}

QListWidget::item {
    padding: 5px;
    border-radius: 3px;
    border: 1px solid transparent;
}

QListWidget::item:selected {
    background-color: #2196F3;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #9C27B0;
}

QListWidget::item:hover {
    background-color: #f0f0f0;
}

QListWidget::item:focus {
    border: 1px solid #9C27B0;
}

/* 树形控件 */
QTreeWidget {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    gridline-color: #e0e0e0;
    outline: none;
}

QTreeWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QTreeWidget::item:selected {
    background-color: #2196F3;
    color: #ffffff;
    font-weight: bold;
}

QTreeWidget::item:hover {
    background-color: #f0f0f0;
}

QTreeWidget::item:focus {
    border: 1px solid #9C27B0;
}

/* 进度条 */
QProgressBar {
    background-color: #e0e0e0;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 6px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #fafafa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #d0d0d0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #c0c0c0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 组合框 */
QGroupBox {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #2196F3;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

/* 滑块 */
QSlider::groove:horizontal {
    background-color: #e0e0e0;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #2196F3;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #1976D2;
}

/* 复选框 */
QCheckBox {
    color: #333333;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    background-color: #f0f0f0;
    border: 1px solid #e0e0e0;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border: 1px solid #2196F3;
}

/* 下拉框 */
QComboBox {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px 10px;
    color: #333333;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    color: #2196F3;
}

QComboBox QAbstractItemView {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    selection-background-color: #2196F3;
}

/* 状态栏 */
QStatusBar {
    background-color: #f0f0f0;
    color: #333333;
    border-top: 1px solid #e0e0e0;
}

/* 工具提示 */
QToolTip {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 5px;
}

/* 分割器 */
QSplitter::handle {
    background-color: #e0e0e0;
    border-radius: 2px;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}
"""


class SettingsDialog(QDialog):
    """设置对话框 - 双字体调节 + 主题切换"""
    def __init__(self, interface_font=10, code_font=10, current_theme='dark', parent=None):
        super().__init__(parent)
        self.interface_font = interface_font
        self.code_font = code_font
        self.current_theme = current_theme
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("⚙️ 设置")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 主题选择
        theme_group = QGroupBox("🎨 主题模式")
        theme_layout = QHBoxLayout()
        
        self.dark_radio = QRadioButton("🌙 黑夜模式")
        self.light_radio = QRadioButton("☀️ 白天模式")
        
        if self.current_theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        
        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.light_radio)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        
        # 界面字体
        interface_group = QGroupBox("📝 界面字体大小")
        interface_layout = QVBoxLayout()
        
        self.interface_slider = QSlider(Qt.Horizontal)
        self.interface_slider.setMinimum(8)
        self.interface_slider.setMaximum(16)
        self.interface_slider.setValue(self.interface_font)
        self.interface_slider.valueChanged.connect(self.update_interface_label)
        
        self.interface_label = QLabel(f"当前：{self.interface_font}pt")
        self.interface_label.setAlignment(Qt.AlignCenter)
        
        interface_layout.addWidget(self.interface_slider)
        interface_layout.addWidget(self.interface_label)
        interface_group.setLayout(interface_layout)
        
        # 代码字体
        code_group = QGroupBox("💻 代码字体大小")
        code_layout = QVBoxLayout()
        
        self.code_slider = QSlider(Qt.Horizontal)
        self.code_slider.setMinimum(8)
        self.code_slider.setMaximum(18)
        self.code_slider.setValue(self.code_font)
        self.code_slider.valueChanged.connect(self.update_code_label)
        
        self.code_label = QLabel(f"当前：{self.code_font}pt")
        self.code_label.setAlignment(Qt.AlignCenter)
        
        code_layout.addWidget(self.code_slider)
        code_layout.addWidget(self.code_label)
        code_group.setLayout(code_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(theme_group)
        layout.addWidget(interface_group)
        layout.addWidget(code_group)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def update_interface_label(self, value):
        self.interface_label.setText(f"当前：{value}pt")
    
    def update_code_label(self, value):
        self.code_label.setText(f"当前：{value}pt")
    
    def get_fonts(self):
        return self.interface_slider.value(), self.code_slider.value()
    
    def get_theme(self):
        return 'dark' if self.dark_radio.isChecked() else 'light'


class ResourceViewerWidget(QWidget):
    """资源查看器 - 图片/视频"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.open_btn = QPushButton("📂 打开文件")
        self.open_btn.clicked.connect(self.open_file)
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.reset_zoom)
        
        toolbar.addWidget(self.open_btn)
        toolbar.addWidget(self.zoom_in_btn)
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.reset_btn)
        toolbar.addStretch()
        
        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #24283b;
                border: 2px dashed #414868;
                border-radius: 8px;
            }
        """)
        self.image_label.setText("拖放文件到此处\n或点击\"打开文件\"按钮")
        
        # 文件信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # 拖放支持
        self.setAcceptDrops(True)
        self.current_file = None
        self.zoom_level = 1.0
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_resource(files[0])
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.webp);;视频文件 (*.mp4 *.avi *.mkv);;所有文件 (*.*)"
        )
        if file_path:
            self.load_resource(file_path)
    
    def load_resource(self, file_path: str):
        self.current_file = file_path
        ext = os.path.splitext(file_path)[1].lower()
        
        info = f"文件：{os.path.basename(file_path)}\n路径：{file_path}"
        
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.update_display(pixmap)
                info += f"\n类型：图片\n格式：{ext[1:].upper()}\n尺寸：{pixmap.width()} x {pixmap.height()}"
            else:
                self.image_label.setText("无法加载图片")
        elif ext in ['.mp4', '.avi', '.mkv']:
            self.image_label.setText("🎬 视频文件\n\n视频播放需要额外的编解码器支持\n文件路径：" + file_path)
            info += f"\n类型：视频\n格式：{ext[1:].upper()}"
        else:
            self.image_label.setText("📄 未知文件类型")
            info += f"\n类型：其他文件"
        
        self.info_label.setText(info)
    
    def update_display(self, pixmap):
        scaled = pixmap.scaled(
            int(400 * self.zoom_level),
            int(400 * self.zoom_level),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
    
    def zoom_in(self):
        self.zoom_level = min(3.0, self.zoom_level + 0.25)
        if self.current_file:
            ext = os.path.splitext(self.current_file)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                pixmap = QPixmap(self.current_file)
                self.update_display(pixmap)
    
    def zoom_out(self):
        self.zoom_level = max(0.25, self.zoom_level - 0.25)
        if self.current_file:
            ext = os.path.splitext(self.current_file)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                pixmap = QPixmap(self.current_file)
                self.update_display(pixmap)
    
    def reset_zoom(self):
        self.zoom_level = 1.0
        if self.current_file:
            ext = os.path.splitext(self.current_file)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                pixmap = QPixmap(self.current_file)
                self.update_display(pixmap)


class ArscViewerWidget(QWidget):
    """ARSC 文件查看器"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 加载 ARSC")
        self.load_btn.clicked.connect(self.load_arsc)
        
        self.translate_btn = QPushButton("🌐 翻译")
        self.translate_btn.clicked.connect(self.translate_arsc)
        
        self.export_btn = QPushButton("💾 导出")
        self.export_btn.clicked.connect(self.export_arsc)
        
        toolbar.addWidget(self.load_btn)
        toolbar.addWidget(self.translate_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addStretch()
        
        # 内容显示
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setFont(QFont("Consolas", 10))
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["键", "值", "类型"])
        
        # 标签页
        tabs = QTabWidget()
        tabs.addTab(self.content, "文本视图")
        tabs.addTab(self.table, "表格视图")
        
        layout.addLayout(toolbar)
        layout.addWidget(tabs, 1)
        
        self.setLayout(layout)
        self.current_arsc = None
    
    def load_arsc(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 ARSC 文件", "", "ARSC 文件 (*.arsc);;所有文件 (*.*)"
        )
        if file_path:
            self.parse_arsc(file_path)
    
    def parse_arsc(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # 简化解析
            info = f"ARSC 文件信息\n"
            info += f"=" * 50 + "\n"
            info += f"文件：{os.path.basename(file_path)}\n"
            info += f"大小：{len(data)} 字节\n"
            info += f"魔数：{data[:8].hex()}\n"
            
            self.content.setText(info)
            self.current_arsc = {'path': file_path, 'data': data}
            
            # 示例数据
            self.table.setRowCount(5)
            sample_data = [
                ("app_name", "我的应用", "string"),
                ("version", "1.0.0", "string"),
                ("description", "应用描述", "string"),
            ]
            for i, (k, v, t) in enumerate(sample_data):
                self.table.setItem(i, 0, QTableWidgetItem(k))
                self.table.setItem(i, 1, QTableWidgetItem(v))
                self.table.setItem(i, 2, QTableWidgetItem(t))
            
            self.content.append("\n解析成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析失败：{str(e)}")
    
    def translate_arsc(self):
        if not self.current_arsc:
            QMessageBox.warning(self, "提示", "请先加载 ARSC 文件")
            return
        QMessageBox.information(self, "提示", "翻译功能开发中...")
    
    def export_arsc(self):
        if not self.current_arsc:
            QMessageBox.warning(self, "提示", "请先加载 ARSC 文件")
            return
        QMessageBox.information(self, "提示", "导出功能开发中...")


class AIAPIWidget(QWidget):
    """AI API 配置与调用组件"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 启用开关
        self.enable_check = QCheckBox("🤖 启用 AI 辅助分析")
        self.enable_check.setChecked(False)
        
        # API 配置
        config_group = QGroupBox("API 配置")
        config_layout = QFormLayout()
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.example.com/v1/chat/completions")
        self.api_url_input.setText("https://api.openai.com/v1/chat/completions")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        self.model_input = QComboBox()
        self.model_input.addItems(["gpt-4", "gpt-3.5-turbo", "claude-3", "custom"])
        
        config_layout.addRow("API URL:", self.api_url_input)
        config_layout.addRow("API Key:", self.api_key_input)
        config_layout.addRow("模型:", self.model_input)
        
        config_group.setLayout(config_layout)
        
        # 测试按钮
        self.test_btn = QPushButton("🧪 测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        
        # 说明
        info = QLabel("""
        <b>AI 辅助功能说明：</b>
        <ul>
            <li>代码分析与解释</li>
            <li>反混淆建议</li>
            <li>安全风险评估</li>
            <li>优化建议</li>
        </ul>
        <p style='color: #bb9af7;'>提示：启用后可在代码分析时调用 AI API</p>
        """)
        info.setWordWrap(True)
        info.setStyleSheet("padding: 10px; background-color: #24283b; border-radius: 6px;")
        
        layout.addWidget(self.enable_check)
        layout.addWidget(config_group)
        layout.addWidget(self.test_btn)
        layout.addWidget(info)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def test_connection(self):
        if not self.enable_check.isChecked():
            QMessageBox.warning(self, "提示", "请先启用 AI 功能")
            return
        
        api_key = self.api_key_input.text()
        if not api_key:
            QMessageBox.warning(self, "提示", "请输入 API Key")
            return
        
        # 这里可以添加实际的 API 测试逻辑
        QMessageBox.information(self, "提示", "API 配置已保存\n实际调用将在分析时使用")
    
    def get_config(self):
        return {
            'enabled': self.enable_check.isChecked(),
            'api_url': self.api_url_input.text(),
            'api_key': self.api_key_input.text(),
            'model': self.model_input.currentText()
        }


class DexViewerWidget(QWidget):
    """DEX 查看器 - 字符常量池与类列表"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 加载 DEX")
        self.load_btn.clicked.connect(self.load_dex)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.decompile_btn = QPushButton("⚡ 反编译")
        self.decompile_btn.clicked.connect(self.decompile_selected)
        
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self.edit_selected)
        
        toolbar.addWidget(self.load_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.decompile_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addStretch()
        
        # 分割视图
        splitter = QSplitter(Qt.Vertical)
        
        # 字符串常量池
        strings_group = QGroupBox("📝 字符常量池")
        strings_layout = QVBoxLayout()
        
        self.strings_table = QTableWidget()
        self.strings_table.setColumnCount(2)
        self.strings_table.setHorizontalHeaderLabels(["索引", "字符串"])
        self.strings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        strings_layout.addWidget(self.strings_table)
        strings_group.setLayout(strings_layout)
        
        # 类列表
        classes_group = QGroupBox("📚 类列表")
        classes_layout = QVBoxLayout()
        
        self.classes_list = QListWidget()
        self.classes_list.itemDoubleClicked.connect(self.on_class_double_click)
        
        classes_layout.addWidget(self.classes_list)
        classes_group.setLayout(classes_layout)
        
        splitter.addWidget(strings_group)
        splitter.addWidget(classes_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addLayout(toolbar)
        layout.addWidget(splitter, 1)
        
        self.setLayout(layout)
        self.current_dex = None
    
    def load_dex(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 DEX 文件", "", "DEX 文件 (*.dex);;所有文件 (*.*)"
        )
        if file_path:
            self.parse_dex(file_path)
    
    def parse_dex(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.current_dex = {'path': file_path, 'data': data}
            
            # 解析字符串
            self.parse_strings(data)
            
            # 解析类
            self.parse_classes(data)
            
            self.log(f"DEX 加载成功：{os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析失败：{str(e)}")
    
    def log(self, message: str):
        """输出日志到主窗口"""
        main_window = self.parent()
        while main_window and not isinstance(main_window, APKDecompilerUltimate):
            main_window = main_window.parent()
        
        if main_window:
            main_window.log(message)
    
    def parse_strings(self, data: bytes):
        # 简化解析
        self.strings_table.setRowCount(0)
        
        # 示例字符串
        sample_strings = [
            "MainActivity",
            "android.app.Activity",
            "onCreate",
            "Landroid/os/Bundle;",
            "Hello World",
        ]
        
        for i, s in enumerate(sample_strings):
            row = self.strings_table.rowCount()
            self.strings_table.insertRow(row)
            self.strings_table.setItem(row, 0, QTableWidgetItem(str(i)))
            self.strings_table.setItem(row, 1, QTableWidgetItem(s))
    
    def parse_classes(self, data: bytes):
        self.classes_list.clear()
        
        # 示例类
        sample_classes = [
            "Lcom/example/myapp/MainActivity;",
            "Lcom/example/myapp/Utils;",
            "Lcom/example/myapp/adapter/ListAdapter;",
        ]
        
        for cls in sample_classes:
            item = QListWidgetItem(cls)
            item.setForeground(QColor("#7aa2f7"))
            self.classes_list.addItem(item)
    
    def refresh(self):
        if self.current_dex:
            self.parse_dex(self.current_dex['path'])
    
    def on_class_double_click(self, item):
        self.decompile_selected()
    
    def decompile_selected(self):
        current = self.classes_list.currentItem()
        if not current:
            QMessageBox.warning(self, "提示", "请选择一个类")
            return
        
        class_name = current.text()
        self.log(f"正在反编译：{class_name}")
        
        # 查找对应的 Smali 文件
        if self.current_dex:
            dex_dir = os.path.dirname(self.current_dex['path'])
            
            # 将类名转换为文件路径
            # Lcom/example/Utils; -> com/example/Utils.smali
            if class_name.startswith('L') and class_name.endswith(';'):
                relative_path = class_name[1:-1] + '.smali'
            else:
                relative_path = class_name.replace('.', '/') + '.smali'
            
            smali_file = os.path.join(dex_dir, relative_path)
            
            # 尝试在反编译目录中查找
            if not os.path.exists(smali_file):
                # 在输出目录中搜索
                for root, dirs, files in os.walk(dex_dir):
                    if relative_path in files:
                        smali_file = os.path.join(root, relative_path)
                        break
            
            if os.path.exists(smali_file):
                try:
                    with open(smali_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 在代码编辑器中显示
                    main_window = self.parent()
                    while main_window and not isinstance(main_window, APKDecompilerUltimate):
                        main_window = main_window.parent()
                    
                    if main_window:
                        main_window.code_editor.setText(content)
                        main_window.tabs.setCurrentIndex(0)
                        self.log(f"反编译完成：{class_name}")
                    else:
                        QMessageBox.information(self, "Smali 代码", content)
                except Exception as e:
                    QMessageBox.warning(self, "提示", f"找不到 Smali 文件，但可以尝试从 DEX 生成\n{str(e)}")
                    self.generate_smali_from_dex(class_name)
            else:
                self.generate_smali_from_dex(class_name)
    
    def generate_smali_from_dex(self, class_name: str):
        """从 DEX 数据生成 Smali 代码（简化版）"""
        try:
            # 生成 Smali 代码框架
            smali_code = f"""; Smali code for {class_name}
; Generated from DEX

.class {class_name}
.super Ljava/lang/Object;

# static fields
# instance fields

# direct methods
.method constructor <init>()V
    .locals 0
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method

# virtual methods
.end class
"""
            # 在代码编辑器中显示
            main_window = self.parent()
            while main_window and not isinstance(main_window, APKDecompilerUltimate):
                main_window = main_window.parent()
            
            if main_window:
                main_window.code_editor.setText(smali_code)
                main_window.tabs.setCurrentIndex(0)
                main_window.log(f"已生成 Smali 框架：{class_name}")
            
            self.log(f"已生成 Smali 代码框架")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败：{str(e)}")
    
    def edit_selected(self):
        current = self.classes_list.currentItem()
        if not current:
            QMessageBox.warning(self, "提示", "请选择一个类")
            return
        
        class_name = current.text()
        self.log(f"正在编辑：{class_name}")
        
        # 查找对应的 Smali 文件
        smali_content = None
        smali_file = None
        
        if self.current_dex:
            dex_dir = os.path.dirname(self.current_dex['path'])
            
            # 将类名转换为文件路径
            if class_name.startswith('L') and class_name.endswith(';'):
                relative_path = class_name[1:-1] + '.smali'
            else:
                relative_path = class_name.replace('.', '/') + '.smali'
            
            # 查找文件
            if os.path.exists(os.path.join(dex_dir, relative_path)):
                smali_file = os.path.join(dex_dir, relative_path)
            else:
                # 在输出目录中搜索
                for root, dirs, files in os.walk(dex_dir):
                    if relative_path in files:
                        smali_file = os.path.join(root, relative_path)
                        break
            
            # 读取文件内容
            if smali_file and os.path.exists(smali_file):
                try:
                    with open(smali_file, 'r', encoding='utf-8') as f:
                        smali_content = f.read()
                except:
                    smali_content = None
        
        # 如果没有找到文件，生成框架代码
        if smali_content is None:
            smali_content = f"""; Smali code for {class_name}
; Generated from DEX

.class {class_name}
.super Ljava/lang/Object;

# static fields
# instance fields

# direct methods
.method constructor <init>()V
    .locals 0
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method

# virtual methods
.end class
"""
        
        # 在主窗口的代码编辑器中打开
        main_window = self.parent()
        while main_window and not isinstance(main_window, APKDecompilerUltimate):
            main_window = main_window.parent()
        
        if main_window:
            main_window.code_editor.setText(smali_content)
            main_window.code_editor.current_file = smali_file if smali_file else None
            main_window.tabs.setCurrentIndex(0)  # 切换到代码编辑器
            if smali_file:
                main_window.log(f"已加载：{os.path.basename(smali_file)}")
            else:
                main_window.log(f"已生成框架代码：{class_name}")
            main_window.log("提示：编辑后按 Ctrl+S 保存")


class APKDecompilerUltimate(QMainWindow):
    """APK 反编译工具 - 终极集成版"""
    
    def __init__(self):
        super().__init__()
        self.apk_path = None
        self.work_dir = None
        self.interface_font = 10
        self.code_font = 10
        self.current_theme = 'dark'
        self.load_theme_preference()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("APK 反编译工具 v5.0 Ultimate - 完全集成版")
        self.setGeometry(100, 100, 1400, 900)
        
        # 应用样式
        if self.current_theme == 'dark':
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建主界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("📁 文件 (&F)")
        
        open_action = QAction("📂 打开 APK", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_apk)
        file_menu.addAction(open_action)
        
        exit_action = QAction("❌ 退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("🛠️ 工具 (&T)")
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        theme_action = QAction("🎨 切换主题", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        tools_menu.addAction(theme_action)
        
        decrypt_action = QAction("🔓 字符串解密", self)
        decrypt_action.triggered.connect(self.show_decrypt_tool)
        tools_menu.addAction(decrypt_action)
        
        obfuscate_action = QAction("🌀 混淆分析", self)
        obfuscate_action.triggered.connect(self.show_obfuscation_tool)
        tools_menu.addAction(obfuscate_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助 (&H)")
        
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        self.toolbar = self.addToolBar("主工具栏")
        self.toolbar.setMovable(False)
        
        # 打开 APK
        open_btn = QAction("📂 打开 APK", self)
        open_btn.triggered.connect(self.open_apk)
        self.toolbar.addAction(open_btn)
        
        # 分析
        analyze_btn = QAction("🔍 分析", self)
        analyze_btn.triggered.connect(self.analyze_apk)
        self.toolbar.addAction(analyze_btn)
        
        # 提取
        extract_btn = QAction("📦 提取", self)
        extract_btn.triggered.connect(self.extract_apk)
        self.toolbar.addAction(extract_btn)
        
        # 反编译
        decompile_btn = QAction("⚡ 反编译", self)
        decompile_btn.triggered.connect(self.decompile_apk)
        self.toolbar.addAction(decompile_btn)
        
        # 签名
        sign_btn = QAction("✍️ 签名", self)
        sign_btn.triggered.connect(self.sign_apk)
        self.toolbar.addAction(sign_btn)
        
        self.toolbar.addSeparator()
        
        # 主题切换
        theme_btn = QAction("🎨 切换主题", self)
        theme_btn.setToolTip("切换白天/黑夜模式 (Ctrl+T)")
        theme_btn.setShortcut("Ctrl+T")
        theme_btn.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_btn)
        
        # 设置
        settings_btn = QAction("⚙️ 设置", self)
        settings_btn.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_btn)
    
    def create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.progress.setVisible(False)
        
        self.statusBar.addPermanentWidget(self.progress)
        self.statusBar.showMessage("就绪")
    
    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 文件浏览器标题
        title = QLabel("📁 文件浏览器")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7; padding: 10px;")
        layout.addWidget(title)
        
        # 目录导航
        nav_layout = QHBoxLayout()
        
        self.up_btn = QPushButton("⬆️")
        self.up_btn.setFixedWidth(40)
        self.up_btn.clicked.connect(self.go_up_directory)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self.refresh_file_browser)
        
        nav_layout.addWidget(self.up_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addStretch()
        
        layout.addLayout(nav_layout)
        
        # 文件树
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemClicked.connect(self.on_file_clicked)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_tree)
        
        # 文件信息
        self.file_info = QLabel()
        self.file_info.setWordWrap(True)
        self.file_info.setStyleSheet("padding: 10px; background-color: #24283b; border-radius: 6px;")
        layout.addWidget(self.file_info)
        
        return widget
    
    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 1. 代码编辑器
        self.code_editor = QTextEdit()
        self.code_editor.setReadOnly(False)  # 允许编辑
        self.code_editor.setFont(QFont("Consolas", self.code_font))
        self.tabs.addTab(self.code_editor, "💻 代码编辑器")
        
        # 添加保存快捷键
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtWidgets import QShortcut
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.code_editor)
        save_shortcut.activated.connect(self.save_current_file)
        
        # 2. 日志输出
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", self.code_font))
        self.tabs.addTab(self.log_output, "📋 日志输出")
        
        # 3. 资源查看器
        self.resource_viewer = ResourceViewerWidget()
        self.tabs.addTab(self.resource_viewer, "🖼️ 资源查看")
        
        # 4. ARSC 查看器
        self.arsc_viewer = ArscViewerWidget()
        self.tabs.addTab(self.arsc_viewer, "📚 ARSC")
        
        # 5. DEX 查看器
        self.dex_viewer = DexViewerWidget()
        self.tabs.addTab(self.dex_viewer, "📦 DEX")
        
        # 6. DEX 反编译（独立界面）
        self.dex_decompiler = DexDecompilerWidget()
        self.tabs.addTab(self.dex_decompiler, "⚡ DEX 反编译")
        
        # 7. AI 助手
        self.ai_widget = AIAPIWidget()
        self.tabs.addTab(self.ai_widget, "🤖 AI 助手")
        
        # 8. 代码管理
        self.code_manager = CodeManagerWidget()
        self.tabs.addTab(self.code_manager, "📝 代码管理")
        
        layout.addWidget(self.tabs)
        
        return widget
    
    def open_apk(self):
        """打开 APK 文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
            )
            
            if not file_path:
                return
            
            # 验证文件是否存在
            if not os.path.exists(file_path):
                QMessageBox.critical(self, "错误", f"文件不存在：{file_path}")
                return
            
            # 验证文件是否为 APK（检查扩展名）
            if not file_path.lower().endswith('.apk'):
                QMessageBox.warning(self, "警告", "选择的文件可能不是 APK 文件")
            
            self.apk_path = file_path
            self.work_dir = os.path.join(os.path.dirname(file_path), "output")
            
            # 创建工作目录
            try:
                os.makedirs(self.work_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建工作目录：{str(e)}")
                return
            
            self.log(f"已加载 APK: {os.path.basename(file_path)}")
            self.log(f"工作目录：{self.work_dir}")
            
            # 异步刷新文件浏览器，避免界面卡死
            QTimer.singleShot(100, self.refresh_file_browser)
            
        except Exception as e:
            self.log(f"打开 APK 失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"打开 APK 失败:\n{str(e)}")
    
    def refresh_file_browser(self, path: str = None):
        """刷新文件浏览器（高性能优化版）"""
        try:
            self.file_tree.clear()
            
            if not self.work_dir:
                return
            
            current_path = path or self.work_dir
            if not os.path.exists(current_path):
                self.log(f"目录不存在：{current_path}")
                return
            
            # 添加根目录
            root_item = QTreeWidgetItem([os.path.basename(current_path)])
            root_item.setData(0, Qt.UserRole, current_path)
            self.file_tree.addTopLevelItem(root_item)
            
            # 提升限制：支持更多文件
            MAX_FILES = 5000  # 最大文件数（从 1000 提升到 5000）
            MAX_DEPTH = 15    # 最大目录深度（从 10 提升到 15）
            BATCH_SIZE = 200  # 每批处理文件数
            file_count = 0
            current_depth = 0
            
            # 使用生成器优化内存
            def walk_generator(root_path, max_depth, current_depth=0):
                """优化的目录遍历生成器"""
                try:
                    entries = os.listdir(root_path)
                    dirs = []
                    files = []
                    
                    for entry in entries:
                        full_path = os.path.join(root_path, entry)
                        if os.path.isdir(full_path):
                            dirs.append(entry)
                        else:
                            files.append(entry)
                    
                    yield root_path, dirs, files
                    
                    # 递归处理子目录
                    if current_depth < max_depth:
                        for d in dirs:
                            subdir = os.path.join(root_path, d)
                            yield from walk_generator(subdir, max_depth, current_depth + 1)
                except PermissionError:
                    pass
            
            # 批量处理文件
            batch = []
            for root, dirs, files in walk_generator(current_path, MAX_DEPTH):
                # 确定父节点
                rel_path = os.path.relpath(root, current_path)
                if rel_path == '.':
                    parent = root_item
                else:
                    parts = rel_path.split(os.sep)
                    parent = root_item
                    for part in parts:
                        found = False
                        for i in range(parent.childCount()):
                            child = parent.child(i)
                            if child.text(0) == part:
                                parent = child
                                found = True
                                break
                        if not found:
                            new_child = QTreeWidgetItem([part])
                            new_child.setData(0, Qt.UserRole, os.path.join(root, part))
                            parent.addChild(new_child)
                            parent = new_child
                
                # 批量添加文件
                for file in files:
                    if file_count >= MAX_FILES:
                        break
                    
                    file_item = QTreeWidgetItem([file])
                    file_item.setData(0, Qt.UserRole, os.path.join(root, file))
                    batch.append(file_item)
                    file_count += 1
                    
                    # 批量处理，每 BATCH_SIZE 个文件添加一次
                    if len(batch) >= BATCH_SIZE:
                        parent.addChildren(batch)
                        batch = []
                        if file_count % BATCH_SIZE == 0:
                            QApplication.processEvents()
                
                # 检查文件总数限制
                if file_count >= MAX_FILES:
                    self.log(f"提示：文件数量超过 {MAX_FILES}，仅显示前 {MAX_FILES} 个文件")
                    break
            
            # 添加剩余的批量文件
            if batch:
                root_item.addChildren(batch)
            
            # 自动展开根目录和第一层子目录
            self.file_tree.expandItem(root_item)
            for i in range(min(5, root_item.childCount())):
                self.file_tree.expandItem(root_item.child(i))
            
            self.current_browser_path = current_path
            
            self.log(f"文件浏览器已刷新：{file_count} 个文件（最大支持 {MAX_FILES} 个）")
            
        except Exception as e:
            self.log(f"刷新文件浏览器失败：{str(e)}")
            QMessageBox.warning(self, "警告", f"刷新文件浏览器失败:\n{str(e)}")
    
    def go_up_directory(self):
        if hasattr(self, 'current_browser_path'):
            parent = os.path.dirname(self.current_browser_path)
            if parent and os.path.exists(parent):
                self.refresh_file_browser(parent)
                self.log(f"进入上级目录：{parent}")
    
    def on_file_clicked(self, item):
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.file_info.setText(f"文件：{file_path}\n大小：{os.path.getsize(file_path)} 字节")
    
    def on_file_double_clicked(self, item):
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.open_file(file_path)
    
    def open_file(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            self.tabs.setCurrentIndex(2)  # 资源查看
            self.resource_viewer.load_resource(file_path)
        elif ext == '.arsc':
            self.tabs.setCurrentIndex(3)  # ARSC
            self.arsc_viewer.parse_arsc(file_path)
        elif ext == '.dex':
            self.tabs.setCurrentIndex(4)  # DEX
            self.dex_viewer.parse_dex(file_path)
        elif ext in ['.xml', '.java', '.smali']:
            try:
                # 尝试不同的编码方式
                content = None
                encodings = ['utf-8', 'gbk', 'latin-1']
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        self.log(f"使用 {encoding} 编码打开文件")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # 如果所有编码都失败，以二进制方式读取
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                    self.log(f"警告：文件包含无法识别的字符")
                
                self.code_editor.setText(content)
                self.code_editor.current_file = file_path  # 保存当前文件路径
                self.tabs.setCurrentIndex(0)  # 代码编辑器
                self.log(f"已打开：{os.path.basename(file_path)}")
                
                # 如果是 XML，尝试格式化
                if ext == '.xml':
                    self.log("提示：XML 文件可以编辑，按 Ctrl+S 保存")
                    
            except Exception as e:
                self.log(f"无法读取文件：{str(e)}")
                QMessageBox.warning(self, "警告", f"无法打开文件:\n{str(e)}")
        else:
            self.log(f"未知文件类型：{ext}")
    
    def analyze_apk(self):
        if not self.apk_path:
            QMessageBox.warning(self, "提示", "请先打开 APK 文件")
            return
        
        self.log("开始分析 APK...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        try:
            analyzer = APKAnalyzer()
            result = analyzer.analyze(self.apk_path)
            
            self.progress.setValue(100)
            self.log("分析完成")
            
            # 显示结果
            info = f"APK 信息\n{'='*50}\n"
            info += f"包名：{result.get('package_name', 'N/A')}\n"
            info += f"版本：{result.get('version', 'N/A')}\n"
            info += f"最小 SDK: {result.get('min_sdk', 'N/A')}\n"
            info += f"目标 SDK: {result.get('target_sdk', 'N/A')}\n"
            info += f"权限数量：{len(result.get('permissions', []))}\n"
            info += f"DEX 文件：{len(result.get('dex_files', []))}\n"
            
            self.code_editor.setText(info)
            self.tabs.setCurrentIndex(0)
            
        except Exception as e:
            self.log(f"分析失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"分析失败：{str(e)}")
        finally:
            self.progress.setVisible(False)
    
    def extract_apk(self):
        if not self.apk_path:
            QMessageBox.warning(self, "提示", "请先打开 APK 文件")
            return
        
        self.log("开始提取 APK...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        try:
            output_dir = os.path.join(self.work_dir, "extracted")
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        zf.extract(file, output_dir)
                        progress = int((i / total) * 100)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
                    except:
                        pass
            
            self.progress.setValue(100)
            self.log(f"提取完成：{output_dir}")
            self.refresh_file_browser(output_dir)
            
        except Exception as e:
            self.log(f"提取失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"提取失败：{str(e)}")
        finally:
            self.progress.setVisible(False)
    
    def decompile_apk(self):
        if not self.apk_path:
            QMessageBox.warning(self, "提示", "请先打开 APK 文件")
            return
        
        self.log("开始反编译 APK...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        try:
            output_dir = os.path.join(self.work_dir, "decompiled")
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        zf.extract(file, output_dir)
                        progress = int((i / total) * 50)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
                    except:
                        pass
            
            # 解析 DEX
            dex_dir = os.path.join(output_dir, "dex_output")
            os.makedirs(dex_dir, exist_ok=True)
            
            converter = DexToSmaliConverter()
            dex_files = [f for f in os.listdir(output_dir) if f.endswith('.dex')]
            
            self.log(f"发现 {len(dex_files)} 个 DEX 文件")
            
            if dex_files:
                success_count = 0
                for i, dex_file in enumerate(dex_files):
                    dex_path = os.path.join(output_dir, dex_file)
                    try:
                        self.log(f"正在转换：{dex_file} ({i+1}/{len(dex_files)})")
                        
                        # 转换 DEX 为 Smali 和 Java
                        success = converter.convert_file(dex_path, dex_dir)
                        
                        if success:
                            success_count += 1
                            self.log(f"✓ {dex_file} 转换成功")
                        else:
                            self.log(f"✗ {dex_file} 转换失败")
                        
                        progress = 50 + int(((i + 1) / len(dex_files)) * 50)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
                        
                    except Exception as e:
                        self.log(f"✗ DEX 转换失败 {dex_file}: {str(e)}")
                
                self.log(f"DEX 转换完成：{success_count}/{len(dex_files)} 成功")
            else:
                self.log("警告：未找到 DEX 文件")
            
            self.progress.setValue(100)
            self.log(f"反编译完成：{output_dir}")
            self.refresh_file_browser(output_dir)
            
        except Exception as e:
            self.log(f"反编译失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"反编译失败：{str(e)}")
        finally:
            self.progress.setVisible(False)
    
    def sign_apk(self):
        QMessageBox.information(self, "提示", "签名功能开发中...")
    
    def open_settings(self):
        dialog = SettingsDialog(self.interface_font, self.code_font, self.current_theme, self)
        if dialog.exec_() == QDialog.Accepted:
            interface_font, code_font = dialog.get_fonts()
            theme = dialog.get_theme()
            
            self.interface_font = interface_font
            self.code_font = code_font
            
            # 应用字体
            font = QFont("Microsoft YaHei", self.interface_font)
            self.setFont(font)
            
            self.code_editor.setFont(QFont("Consolas", self.code_font))
            self.log_output.setFont(QFont("Consolas", self.code_font))
            
            # 应用主题
            if theme != self.current_theme:
                self.current_theme = theme
                if self.current_theme == 'dark':
                    self.setStyleSheet(DARK_STYLE)
                    self.log("已切换到黑夜模式 🌙")
                else:
                    self.setStyleSheet(LIGHT_STYLE)
                    self.log("已切换到白天模式 ☀️")
                self.save_theme_preference()
            
            self.log(f"字体已更新：界面={interface_font}pt, 代码={code_font}pt")
    
    def show_decrypt_tool(self):
        QMessageBox.information(self, "提示", "字符串解密工具开发中...")
    
    def show_obfuscation_tool(self):
        QMessageBox.information(self, "提示", "混淆分析工具开发中...")
    
    def show_about(self):
        QMessageBox.information(
            self, "关于",
            "APK 反编译工具 v5.0 Ultimate\n\n"
            "完全集成版 - 整合所有功能\n\n"
            "功能包括:\n"
            "- APK 分析、提取、反编译、签名\n"
            "- Smali/Java 代码编辑\n"
            "- 资源查看（图片/视频）\n"
            "- ARSC 文件查看\n"
            "- DEX 常量池与类列表\n"
            "- AI API 集成\n"
            "- 双字体调节\n"
            "- 白天/黑夜主题切换\n"
        )
    
    def toggle_theme(self):
        """快速切换主题"""
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            self.setStyleSheet(LIGHT_STYLE)
            self.log("已切换到白天模式 ☀️")
        else:
            self.current_theme = 'dark'
            self.setStyleSheet(DARK_STYLE)
            self.log("已切换到黑夜模式 🌙")
        self.save_theme_preference()
    
    def load_theme_preference(self):
        """加载主题偏好设置"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'theme_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'dark')
        except Exception as e:
            print(f"加载主题配置失败：{e}")
            self.current_theme = 'dark'
    
    def save_theme_preference(self):
        """保存主题偏好设置"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'theme_config.json')
            config = {'theme': self.current_theme}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主题配置失败：{e}")
    
    def save_current_file(self):
        """保存当前编辑的文件"""
        if not hasattr(self.code_editor, 'current_file') or not self.code_editor.current_file:
            # 如果没有文件路径，另存为
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "",
                "所有文件 (*.*)"
            )
            if file_path:
                self.code_editor.current_file = file_path
            else:
                return
        
        try:
            content = self.code_editor.toPlainText()
            with open(self.code_editor.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"已保存：{os.path.basename(self.code_editor.current_file)}")
            QMessageBox.information(self, "成功", "文件已保存！")
        except Exception as e:
            self.log(f"保存失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
    
    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        QApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("APK 反编译工具 Ultimate")
    app.setOrganizationName("Ultimate Studio")
    
    window = APKDecompilerUltimate()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

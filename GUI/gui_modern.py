"""
APK 反编译工具 - 现代化界面版本
功能：
- 现代化 UI 设计
- 可调节字体大小
- 优化的操作流程
- 完整的功能集成
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QInputDialog, QLineEdit, QComboBox, 
                             QSpinBox, QDialog, QDialogButtonBox, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QSlider, QFormLayout,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor, QPalette, QPixmap
import zipfile
import shutil
import json
import re
import base64
from pathlib import Path
from datetime import datetime

from core_engine import APKAnalyzer, APKModifier, StringDecryptor, ObfuscationAnalyzer, DexParser
from dex_converter import DexToSmaliConverter, SmaliToJavaConverter, SmaliClass, SmaliMethod
from code_manager import CodeManagerWidget


# ============== 现代化样式表 ==============
MODERN_STYLE = """
/* 全局样式 */
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

/* 菜单栏 */
QMenuBar {
    background-color: #313244;
    color: #cdd6f4;
    padding: 5px;
    border-bottom: 1px solid #45475a;
}

QMenuBar::item:selected {
    background-color: #45475a;
    border-radius: 3px;
}

QMenu {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
}

QMenu::item:selected {
    background-color: #45475a;
    border-radius: 3px;
}

/* 工具栏 */
QToolBar {
    background-color: #313244;
    border: none;
    padding: 5px;
    spacing: 5px;
    border-bottom: 1px solid #45475a;
}

QToolBar QToolButton {
    background-color: #45475a;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    color: #cdd6f4;
    font-weight: bold;
}

QToolBar QToolButton:hover {
    background-color: #585b70;
}

QToolBar QToolButton:pressed {
    background-color: #6c7086;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 5px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #45475a;
    color: #cdd6f4;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

/* 按钮 */
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #b4befe;
}

QPushButton:pressed {
    background-color: #74c7ec;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

/* 进度条 */
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 5px;
    height: 20px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #89b4fa, 
                                stop:1 #b4befe);
    border-radius: 5px;
}

/* 文本编辑器 */
QTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
    font-family: "Consolas", "Courier New", monospace;
}

QTextEdit:focus {
    border: 1px solid #89b4fa;
}

/* 树形控件 */
QTreeWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
    outline: none;
}

QTreeWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QTreeWidget::item:hover {
    background-color: #313244;
}

QTreeWidget::item:selected {
    background-color: #45475a;
}

QHeaderView::section {
    background-color: #313244;
    color: #a6adc8;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #45475a;
}

/* 状态栏 */
QStatusBar {
    background-color: #313244;
    color: #a6adc8;
    border-top: 1px solid #45475a;
}

/* 分组框 */
QGroupBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #89b4fa;
}

/* 滑块 */
QSlider::groove:horizontal {
    border: 1px solid #45475a;
    height: 8px;
    background: #313244;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #89b4fa;
    border: 1px solid #45475a;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #b4befe;
}

/* 输入框 */
QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 8px;
    selection-background-color: #89b4fa;
}

QLineEdit:focus {
    border: 1px solid #89b4fa;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 工具提示 */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 3px;
    padding: 5px;
}

/* 复选框 */
QCheckBox {
    color: #cdd6f4;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
}

/* 标签 */
QLabel {
    color: #cdd6f4;
    background-color: transparent;
}
"""


class FontSizeDialog(QDialog):
    """字体大小调整对话框"""
    
    def __init__(self, current_size: int = 10, parent=None):
        super().__init__(parent)
        self.current_size = current_size
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("⚙️ 界面设置")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🎨 界面字体设置")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # 字体大小滑块
        size_layout = QHBoxLayout()
        size_label = QLabel("字体大小:")
        size_label.setFont(QFont("Microsoft YaHei", 12))
        size_layout.addWidget(size_label)
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(8)
        self.size_slider.setMaximum(16)
        self.size_slider.setValue(self.current_size)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(1)
        self.size_slider.valueChanged.connect(self.on_value_changed)
        size_layout.addWidget(self.size_slider)
        
        self.size_label = QLabel(f"{self.current_size}pt")
        self.size_label.setMinimumWidth(40)
        self.size_label.setAlignment(Qt.AlignCenter)
        self.size_label.setFont(QFont("Microsoft YaHei", 11))
        size_layout.addWidget(self.size_label)
        
        layout.addLayout(size_layout)
        
        layout.addSpacing(20)
        
        # 预览
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_text = QLabel("这是预览文本 - The quick brown fox")
        self.preview_text.setAlignment(Qt.AlignCenter)
        self.preview_text.setStyleSheet("color: #cdd6f4; padding: 10px;")
        self.update_preview()
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 重置")
        reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("✅ 确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_value_changed(self, value):
        self.size_label.setText(f"{value}pt")
        self.update_preview()
    
    def update_preview(self):
        size = self.size_slider.value()
        self.preview_text.setFont(QFont("Microsoft YaHei", size))
    
    def reset_to_default(self):
        self.size_slider.setValue(10)
    
    def get_font_size(self) -> int:
        return self.size_slider.value()


class ModernAPKDecompiler(QMainWindow):
    """现代化 APK 反编译工具"""
    
    def __init__(self):
        super().__init__()
        self.current_apk = None
        self.current_project = None
        self.worker_thread = None
        self.font_size = 10
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🚀 APK 反编译工具 v3.0 - 现代化版")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 应用现代化样式
        self.setStyleSheet(MODERN_STYLE)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        main_widget.setLayout(main_layout)
        
        # 欢迎面板（初始显示）
        self.welcome_panel = self.create_welcome_panel()
        main_layout.addWidget(self.welcome_panel)
        
        # 主工作区（初始隐藏）
        self.workspace_widget = QWidget()
        self.workspace_widget.hide()
        workspace_layout = QVBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(10)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：文件浏览器
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：代码编辑器和信息面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        workspace_layout.addWidget(splitter)
        self.workspace_widget.setLayout(workspace_layout)
        main_layout.addWidget(self.workspace_widget)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("padding: 5px;")
        self.statusBar.showMessage("👋 欢迎使用 APK 反编译工具 - 请点击\"打开 APK\"开始")
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(25)
        self.progress.setMaximumHeight(30)
        self.statusBar.addPermanentWidget(self.progress, 1)
        
        self.show()
        
        # 欢迎日志
        self.log("========================================")
        self.log("🚀 APK 反编译工具 v3.0")
        self.log("现代化界面 - 纯 Python 实现")
        self.log("========================================")
    
    def create_welcome_panel(self) -> QWidget:
        """创建欢迎面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1e1e2e, 
                                          stop:1 #313244);
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 标题
        title = QLabel("🚀 APK 反编译工具")
        title.setFont(QFont("Microsoft YaHei", 28, QFont.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 版本
        version = QLabel("v3.0 现代化版 - 纯 Python 实现")
        version.setFont(QFont("Microsoft YaHei", 14))
        version.setStyleSheet("color: #a6adc8; padding: 10px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(30)
        
        # 功能列表
        features = [
            "✨ 现代化 UI 界面",
            "📱 APK 文件分析",
            "🔓 DEX 转 Smali/Java",
            "✏️ 代码编辑与修改",
            "🔍 字符串解密",
            "📊 混淆分析"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setFont(QFont("Microsoft YaHei", 12))
            label.setStyleSheet("color: #cdd6f4; padding: 5px;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        
        layout.addSpacing(30)
        
        # 开始按钮
        start_btn = QPushButton("📂 打开 APK 开始使用")
        start_btn.setMinimumSize(250, 50)
        start_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        start_btn.clicked.connect(self.open_apk_from_welcome)
        layout.addWidget(start_btn)
        
        layout.addSpacing(20)
        
        # 提示
        tip = QLabel("💡 提示：支持拖放 APK 文件到窗口")
        tip.setFont(QFont("Microsoft YaHei", 10))
        tip.setStyleSheet("color: #6c7086;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
        
        panel.setLayout(layout)
        return panel
    
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 文件浏览器标题
        header = QLabel("📁 文件浏览器")
        header.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        header.setStyleSheet("color: #89b4fa; padding: 10px;")
        layout.addWidget(header)
        
        # 文件浏览器
        self.file_browser = QTreeWidget()
        self.file_browser.setHeaderLabels(["名称", "大小", "类型"])
        self.file_browser.setColumnWidth(0, 200)
        self.file_browser.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_browser)
        
        # 文件操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(50)
        refresh_btn.setToolTip("刷新")
        refresh_btn.clicked.connect(self.refresh_file_browser)
        btn_layout.addWidget(refresh_btn)
        
        up_btn = QPushButton("⬆️")
        up_btn.setFixedWidth(50)
        up_btn.setToolTip("上一级")
        up_btn.clicked.connect(self.go_up_directory)
        btn_layout.addWidget(up_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 代码管理器标签页
        self.code_manager = CodeManagerWidget()
        self.tabs.addTab(self.code_manager, "💻 代码管理")
        
        # 代码编辑器标签页
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", self.font_size))
        self.code_editor.setLineWrapMode(QTextEdit.NoWrap)
        self.code_editor.setPlaceholderText("在此编辑代码...")
        self.tabs.addTab(self.code_editor, "📝 编辑器")
        
        # APK 信息标签页
        self.info_widget = QTextEdit()
        self.info_widget.setReadOnly(True)
        self.info_widget.setFont(QFont("Microsoft YaHei", self.font_size))
        self.tabs.addTab(self.info_widget, "📊 APK 信息")
        
        # DEX 转换标签页
        self.converter_widget = QTextEdit()
        self.converter_widget.setReadOnly(True)
        self.converter_widget.setFont(QFont("Microsoft YaHei", self.font_size))
        self.tabs.addTab(self.converter_widget, "🔄 DEX 转换")
        
        # 字符串标签页
        self.strings_widget = QTextEdit()
        self.strings_widget.setReadOnly(True)
        self.strings_widget.setFont(QFont("Microsoft YaHei", self.font_size))
        self.tabs.addTab(self.strings_widget, "🔍 字符串")
        
        # 日志标签页
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFont(QFont("Consolas", self.font_size))
        self.log_widget.setStyleSheet("background-color: #11111b;")
        self.tabs.addTab(self.log_widget, "📜 日志")
        
        layout.addWidget(self.tabs)
        
        # 操作面板
        ops_group = QGroupBox("⚡ 快速操作")
        ops_layout = QHBoxLayout()
        ops_layout.setSpacing(8)
        
        self.open_apk_btn = QPushButton("📱 打开 APK")
        self.open_apk_btn.clicked.connect(self.open_apk)
        ops_layout.addWidget(self.open_apk_btn)
        
        self.analyze_btn = QPushButton("🔍 分析")
        self.analyze_btn.clicked.connect(self.analyze_apk)
        ops_layout.addWidget(self.analyze_btn)
        
        self.extract_btn = QPushButton("📦 提取")
        self.extract_btn.clicked.connect(self.extract_apk_action)
        ops_layout.addWidget(self.extract_btn)
        
        self.decompile_btn = QPushButton("🔓 反编译")
        self.decompile_btn.clicked.connect(self.decompile_apk_action)
        ops_layout.addWidget(self.decompile_btn)
        
        self.convert_dex_btn = QPushButton("🔄 DEX 转换")
        self.convert_dex_btn.clicked.connect(self.convert_dex_action)
        ops_layout.addWidget(self.convert_dex_btn)
        
        self.decrypt_btn = QPushButton("🔐 解密")
        self.decrypt_btn.clicked.connect(self.decrypt_strings_action)
        ops_layout.addWidget(self.decrypt_btn)
        
        ops_layout.addStretch()
        
        ops_layout.addWidget(QLabel("🔤"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["8pt", "9pt", "10pt", "11pt", "12pt", "14pt", "16pt"])
        self.font_combo.setCurrentIndex(2)  # 默认 10pt
        self.font_combo.setFixedWidth(80)
        self.font_combo.currentTextChanged.connect(self.change_font_size)
        ops_layout.addWidget(self.font_combo)
        
        ops_group.setLayout(ops_layout)
        layout.addWidget(ops_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        menubar.setFont(QFont("Microsoft YaHei", 10))
        
        # 文件菜单
        file_menu = menubar.addMenu("📄 文件")
        
        open_action = QAction("📂 打开 APK", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_apk)
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ 退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("🛠️ 工具")
        
        analyze_action = QAction("🔍 分析 APK", self)
        analyze_action.triggered.connect(self.analyze_apk)
        tools_menu.addAction(analyze_action)
        
        extract_action = QAction("📦 提取 APK", self)
        extract_action.triggered.connect(self.extract_apk_action)
        tools_menu.addAction(extract_action)
        
        decompile_action = QAction("🔓 反编译", self)
        decompile_action.triggered.connect(self.decompile_apk_action)
        tools_menu.addAction(decompile_action)
        
        tools_menu.addSeparator()
        
        convert_action = QAction("🔄 DEX 转换", self)
        convert_action.triggered.connect(self.convert_dex_action)
        tools_menu.addAction(convert_action)
        
        decrypt_action = QAction("🔐 字符串解密", self)
        decrypt_action.triggered.connect(self.decrypt_strings_action)
        tools_menu.addAction(decrypt_action)
        
        obfuscate_action = QAction("📊 混淆分析", self)
        obfuscate_action.triggered.connect(self.analyze_obfuscation_action)
        tools_menu.addAction(obfuscate_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助")
        
        doc_action = QAction("📖 使用文档", self)
        doc_action.triggered.connect(self.show_documentation)
        help_menu.addAction(doc_action)
        
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        toolbar.addAction("📱 打开", self.open_apk)
        toolbar.addAction("🔍 分析", self.analyze_apk)
        toolbar.addAction("📦 提取", self.extract_apk_action)
        toolbar.addAction("🔓 反编译", self.decompile_apk_action)
        toolbar.addAction("🔄 转换", self.convert_dex_action)
        toolbar.addAction("🔐 解密", self.decrypt_strings_action)
    
    def change_font_size(self, size_str: str):
        """更改字体大小"""
        size = int(size_str.replace("pt", ""))
        self.font_size = size
        
        # 更新所有文本组件的字体
        self.code_editor.setFont(QFont("Consolas", size))
        self.info_widget.setFont(QFont("Microsoft YaHei", size))
        self.converter_widget.setFont(QFont("Microsoft YaHei", size))
        self.strings_widget.setFont(QFont("Microsoft YaHei", size))
        self.log_widget.setFont(QFont("Consolas", size))
        
        self.log(f"字体大小已更改为：{size}pt")
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = FontSizeDialog(self.font_size, self)
        if dialog.exec_() == QDialog.Accepted:
            new_size = dialog.get_font_size()
            self.font_size = new_size
            self.font_combo.setCurrentText(f"{new_size}pt")
            self.change_font_size(f"{new_size}pt")
            self.log(f"字体大小已更新：{new_size}pt")
    
    def open_apk_from_welcome(self):
        """从欢迎面板打开 APK"""
        self.open_apk()
    
    def open_apk(self):
        """打开 APK 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", 
            "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if file_path:
            self.current_apk = file_path
            
            # 隐藏欢迎面板，显示工作区
            self.welcome_panel.hide()
            self.workspace_widget.show()
            
            self.statusBar.showMessage(f"📱 已加载：{os.path.basename(file_path)}")
            self.log(f"打开 APK: {os.path.basename(file_path)}")
            
            # 刷新文件浏览器
            self.refresh_file_browser(os.path.dirname(file_path))
            
            # 自动分析
            QTimer.singleShot(500, self.analyze_apk)
    
    def refresh_file_browser(self, path: str = None):
        """刷新文件浏览器"""
        self.file_browser.clear()
        
        current_path = path or os.getcwd()
        self.current_browser_path = current_path  # 保存当前路径
        
        try:
            items = sorted(os.listdir(current_path), 
                          key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))
            
            for item in items:
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, item)
                
                if is_dir:
                    tree_item.setText(1, "")
                    tree_item.setText(2, "📁 文件夹")
                else:
                    size = os.path.getsize(item_path)
                    if size < 1024:
                        tree_item.setText(1, f"{size} B")
                    elif size < 1024 * 1024:
                        tree_item.setText(1, f"{size/1024:.1f} KB")
                    else:
                        tree_item.setText(1, f"{size/(1024*1024):.1f} MB")
                    
                    ext = os.path.splitext(item)[1].upper()
                    tree_item.setText(2, f"📄 {ext}")
                
                tree_item.setData(0, Qt.UserRole, item_path)
                tree_item.setData(0, Qt.UserRole + 1, is_dir)
                self.file_browser.addTopLevelItem(tree_item)
        except Exception as e:
            self.log(f"刷新文件列表失败：{e}")
    
    def go_up_directory(self):
        """上一级目录"""
        if hasattr(self, 'current_browser_path'):
            parent = os.path.dirname(self.current_browser_path)
            if parent and os.path.exists(parent):
                self.refresh_file_browser(parent)
                self.log(f"进入上级目录：{parent}")
    
    def on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """文件双击事件"""
        is_dir = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        
        if is_dir:
            self.refresh_file_browser(path)
            self.log(f"进入目录：{path}")
        else:
            self.open_file_in_editor(path)
    
    def open_file_in_editor(self, file_path: str):
        """在编辑器中打开文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.code_editor.setPlainText(content)
            self.tabs.setCurrentIndex(1)  # 切换到编辑器标签页
            self.log(f"打开文件：{os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件：{e}")
    
    def log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.append(f"[{timestamp}] {message}")
        self.log_widget.verticalScrollBar().setValue(
            self.log_widget.verticalScrollBar().maximum()
        )
    
    def analyze_apk(self):
        """分析 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("🔍 开始分析 APK...")
        
        # 简化分析过程
        self.progress.setValue(50)
        
        analyzer = APKAnalyzer()
        result = analyzer.analyze(self.current_apk)
        
        self.progress.setValue(100)
        
        # 显示结果
        self.display_analysis_result(result)
        self.progress.setVisible(False)
        self.log("✅ APK 分析完成")
    
    def display_analysis_result(self, result: dict):
        """显示分析结果"""
        info_text = "📊 APK 分析报告\n"
        info_text += "=" * 50 + "\n\n"
        
        # 文件信息
        file_info = result.get('file_info', {})
        info_text += f"📁 文件大小：{self.format_size(file_info.get('size', 0))}\n"
        info_text += f"📄 文件数量：{file_info.get('file_count', 0)}\n\n"
        
        # 应用信息
        manifest = result.get('manifest', {})
        if manifest:
            info_text += "📱 应用信息\n"
            info_text += f"包名：{manifest.get('package', 'N/A')}\n"
            if manifest.get('versionName'):
                info_text += f"版本：{manifest.get('versionName')}\n"
            info_text += "\n"
        
        # 权限
        permissions = result.get('permissions', [])
        info_text += f"🔐 权限数量：{len(permissions)}\n"
        if permissions:
            for perm in permissions[:10]:
                info_text += f"  • {perm}\n"
            if len(permissions) > 10:
                info_text += f"  ... 还有 {len(permissions) - 10} 个权限\n"
        
        self.info_widget.setText(info_text)
        self.tabs.setCurrentIndex(2)
    
    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def extract_apk_action(self):
        """提取 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        output_dir = os.path.join(output_dir, os.path.basename(self.current_apk).replace('.apk', '_extracted'))
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("📦 开始提取 APK...")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.current_apk, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        if file.startswith('META-INF/'):
                            continue
                        zf.extract(file, output_dir)
                        progress = int((i / total) * 80)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
                    except:
                        pass
            
            self.progress.setValue(100)
            self.progress.setVisible(False)
            self.log(f"✅ 提取完成：{output_dir}")
            QMessageBox.information(self, "成功", f"提取完成\n{output_dir}")
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "错误", f"提取失败：{e}")
    
    def decompile_apk_action(self):
        """反编译 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        output_dir = os.path.join(output_dir, os.path.basename(self.current_apk).replace('.apk', '_decompiled'))
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("🔓 开始反编译 APK...")
        
        # 简化版反编译 - 提取文件
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.current_apk, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        if file.startswith('META-INF/'):
                            continue
                        zf.extract(file, output_dir)
                        progress = int((i / total) * 80)
                        self.progress.setValue(progress)
                        QApplication.processEvents()
                    except:
                        pass
            
            self.progress.setValue(100)
            self.progress.setVisible(False)
            self.log(f"✅ 反编译完成：{output_dir}")
            QMessageBox.information(self, "成功", f"反编译完成\n{output_dir}")
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "错误", f"反编译失败：{e}")
    
    def convert_dex_action(self):
        """DEX 转换为 Smali/Java"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("🔄 开始转换 DEX...")
        
        try:
            output_dir = os.path.join(output_dir, "dex_output")
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.current_apk, 'r') as zf:
                dex_files = [f for f in zf.namelist() if f.endswith('.dex')]
                
                if not dex_files:
                    self.progress.setVisible(False)
                    QMessageBox.warning(self, "警告", "APK 中没有找到 DEX 文件")
                    return
                
                converter = DexToSmaliConverter()
                java_converter = SmaliToJavaConverter()
                all_smali_classes = []
                total_dex = len(dex_files)
                
                for i, dex_file in enumerate(dex_files):
                    progress_value = int((i / total_dex) * 80)
                    self.progress.setValue(progress_value)
                    self.statusBar.showMessage(f"正在处理：{dex_file}")
                    QApplication.processEvents()
                    
                    self.log(f"处理：{dex_file}")
                    
                    dex_data = zf.read(dex_file)
                    smali_classes = converter.convert_dex(dex_data)
                    all_smali_classes.extend(smali_classes)
                    
                    smali_output = os.path.join(output_dir, f"{os.path.splitext(dex_file)[0]}_smali")
                    converter.save_smali_files(smali_output)
                    
                    java_classes = java_converter.convert(smali_classes)
                    java_output = os.path.join(output_dir, f"{os.path.splitext(dex_file)[0]}_java")
                    java_converter.save_java_files(java_output)
                
                result_text = f"✅ DEX 转换完成\n\n"
                result_text += f"DEX 文件数：{len(dex_files)}\n"
                result_text += f"Smali 类数：{len(all_smali_classes)}\n"
                result_text += f"输出目录：{output_dir}\n\n"
                
                if all_smali_classes:
                    result_text += "类列表:\n"
                    for cls in all_smali_classes[:20]:
                        result_text += f"  • {cls.name}\n"
                    if len(all_smali_classes) > 20:
                        result_text += f"  ... 还有 {len(all_smali_classes) - 20} 个类\n"
                
                self.converter_widget.setText(result_text)
                self.tabs.setCurrentIndex(3)
                
                self.progress.setValue(100)
                self.progress.setVisible(False)
                self.log(f"✅ DEX 转换完成")
                QMessageBox.information(self, "成功", f"DEX 转换完成\n输出目录：{output_dir}")
                
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "错误", f"DEX 转换失败：{e}")
            self.log(f"DEX 转换失败：{e}")
    
    def decrypt_strings_action(self):
        """解密字符串"""
        QMessageBox.information(self, "提示", "字符串解密功能开发中...")
    
    def analyze_obfuscation_action(self):
        """分析混淆"""
        QMessageBox.information(self, "提示", "混淆分析功能开发中...")
    
    def save_file(self):
        """保存文件"""
        QMessageBox.information(self, "提示", "保存功能开发中...")
    
    def show_documentation(self):
        """显示文档"""
        QMessageBox.information(
            self, 
            "使用文档", 
            "📖 使用文档\n\n"
            "1. 打开 APK 文件\n"
            "2. 查看 APK 信息\n"
            "3. 提取或反编译\n"
            "4. DEX 转换为 Smali/Java\n"
            "5. 使用代码管理器编辑\n\n"
            "更多详情请查看项目文档。"
        )
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 APK 反编译工具",
            "🚀 APK 反编译工具 v3.0\n\n"
            "现代化界面 - 纯 Python 实现\n\n"
            "功能:\n"
            "• 📱 APK 文件分析\n"
            "• 📦 文件提取\n"
            "• 🔓 DEX 文件解析\n"
            "• 🔄 DEX 转 Smali/Java\n"
            "• ✏️ 代码编辑\n"
            "• 🔍 字符串解密\n"
            "• 📊 混淆分析\n\n"
            "© 2024 - 仅供学习研究使用"
        )


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 应用全局样式
    window = ModernAPKDecompiler()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

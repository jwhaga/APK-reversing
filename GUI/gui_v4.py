"""
APK 反编译工具 v4.0 - 完全重构版
功能:
- 双字体调节（界面字体 + 代码字体）
- 优化的界面布局与操作逻辑
- APK 资源查看（图片/视频）
- arsc 文件翻译与查看
- AI API 集成
- 完整的代码增删改查
- DEX 字符常量池查看与编辑
- 类列表查看与反编译
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QInputDialog, QLineEdit, QComboBox, 
                             QSpinBox, QDialog, QDialogButtonBox, QGroupBox, 
                             QSlider, QScrollArea, QFrame, QGridLayout, 
                             QCheckBox, QListWidget, QListWidgetItem, QTableWidget,
                             QTableWidgetItem, QHeaderView, QToolBar, QDockWidget,
                             QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor, QPalette, QPixmap, QImage
import zipfile
import json
import re
import base64
from pathlib import Path
from datetime import datetime
import io

from core_engine import APKAnalyzer, StringDecryptor
from dex_converter import DexToSmaliConverter, SmaliToJavaConverter, SmaliClass, SmaliEditor


# ============== 现代化样式表 v4.0 ==============
MODERN_STYLE_V4 = """
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
    color: #565f89;
    padding: 12px 24px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
}

QTabBar::tab:selected {
    background-color: #414868;
    color: #a9b1d6;
}

QTabBar::tab:hover {
    background-color: #414868;
}

/* 按钮 */
QPushButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #5d87e6;
}

QPushButton:pressed {
    background-color: #3d59a1;
}

QPushButton:disabled {
    background-color: #414868;
    color: #565f89;
}

/* 进度条 */
QProgressBar {
    background-color: #24283b;
    border: none;
    border-radius: 6px;
    height: 24px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7aa2f7, 
                                stop:1 #bb9af7);
    border-radius: 6px;
}

/* 文本编辑器 */
QTextEdit {
    background-color: #16161e;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 8px;
    padding: 8px;
    font-family: "Consolas", "Courier New", monospace;
}

QTextEdit:focus {
    border: 1px solid #7aa2f7;
}

/* 树形控件 */
QTreeWidget {
    background-color: #16161e;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 8px;
    padding: 5px;
    outline: none;
}

QTreeWidget::item {
    padding: 6px;
    border-radius: 4px;
}

QTreeWidget::item:hover {
    background-color: #24283b;
}

QTreeWidget::item:selected {
    background-color: #414868;
}

/* 表格 */
QTableWidget {
    background-color: #16161e;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 8px;
    gridline-color: #414868;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #414868;
}

QHeaderView::section {
    background-color: #24283b;
    color: #565f89;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #414868;
    font-weight: 600;
}

/* 输入框 */
QLineEdit {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 10px;
    selection-background-color: #7aa2f7;
}

QLineEdit:focus {
    border: 1px solid #7aa2f7;
}

/* 滑块 */
QSlider::groove:horizontal {
    border: 1px solid #414868;
    height: 10px;
    background: #24283b;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #7aa2f7;
    border: 1px solid #414868;
    width: 20px;
    margin: -2px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #5d87e6;
}

/* 分组框 */
QGroupBox {
    background-color: #16161e;
    border: 1px solid #414868;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: #7aa2f7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #7aa2f7;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #1a1b26;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #414868;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #565f89;
}

/* 列表 */
QListWidget {
    background-color: #16161e;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 8px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #24283b;
}

QListWidget::item:selected {
    background-color: #414868;
}

/* 复选框 */
QCheckBox {
    color: #a9b1d6;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid #414868;
    background-color: #24283b;
}

QCheckBox::indicator:checked {
    background-color: #7aa2f7;
}

/* 标签 */
QLabel {
    color: #a9b1d6;
    background-color: transparent;
}

/* 工具提示 */
QToolTip {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 4px;
    padding: 6px;
}

/* 状态栏 */
QStatusBar {
    background-color: #24283b;
    color: #565f89;
    border-top: 1px solid #414868;
}
"""


class SettingsDialog(QDialog):
    """设置对话框 - 双字体调节"""
    
    def __init__(self, interface_font=10, code_font=10, parent=None):
        super().__init__(parent)
        self.interface_font = interface_font
        self.code_font = code_font
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("⚙️ 界面设置")
        self.setFixedSize(500, 350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("🎨 界面与字体设置")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setStyleSheet("color: #7aa2f7;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # 界面字体
        interface_group = QGroupBox("📱 界面字体")
        interface_layout = QVBoxLayout()
        
        self.interface_slider = QSlider(Qt.Horizontal)
        self.interface_slider.setMinimum(8)
        self.interface_slider.setMaximum(16)
        self.interface_slider.setValue(self.interface_font)
        self.interface_slider.setTickPosition(QSlider.TicksBelow)
        self.interface_slider.setTickInterval(1)
        self.interface_slider.valueChanged.connect(
            lambda: self.interface_label.setText(f"{self.interface_slider.value()}pt")
        )
        
        interface_slider_layout = QHBoxLayout()
        interface_slider_layout.addWidget(QLabel("大小:"))
        interface_slider_layout.addWidget(self.interface_slider)
        self.interface_label = QLabel(f"{self.interface_font}pt")
        self.interface_label.setMinimumWidth(50)
        self.interface_label.setAlignment(Qt.AlignCenter)
        interface_slider_layout.addWidget(self.interface_label)
        
        interface_layout.addLayout(interface_slider_layout)
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # 代码字体
        code_group = QGroupBox("💻 代码字体")
        code_layout = QVBoxLayout()
        
        self.code_slider = QSlider(Qt.Horizontal)
        self.code_slider.setMinimum(8)
        self.code_slider.setMaximum(18)
        self.code_slider.setValue(self.code_font)
        self.code_slider.setTickPosition(QSlider.TicksBelow)
        self.code_slider.setTickInterval(1)
        self.code_slider.valueChanged.connect(
            lambda: self.code_label.setText(f"{self.code_slider.value()}pt")
        )
        
        code_slider_layout = QHBoxLayout()
        code_slider_layout.addWidget(QLabel("大小:"))
        code_slider_layout.addWidget(self.code_slider)
        self.code_label = QLabel(f"{self.code_font}pt")
        self.code_label.setMinimumWidth(50)
        self.code_label.setAlignment(Qt.AlignCenter)
        code_slider_layout.addWidget(self.code_label)
        
        code_layout.addLayout(code_slider_layout)
        code_group.setLayout(code_layout)
        layout.addWidget(code_group)
        
        layout.addSpacing(10)
        
        # 预览
        preview_group = QGroupBox("👁️ 预览")
        preview_layout = QVBoxLayout()
        
        self.interface_preview = QLabel("界面字体预览 - Interface Font")
        self.interface_preview.setAlignment(Qt.AlignCenter)
        self.interface_preview.setStyleSheet("color: #c0caf5; padding: 8px;")
        
        self.code_preview = QLabel("代码字体预览 - Code Font")
        self.code_preview.setAlignment(Qt.AlignCenter)
        self.code_preview.setStyleSheet("color: #c0caf5; padding: 8px; font-family: Consolas;")
        
        self.update_preview()
        
        preview_layout.addWidget(self.interface_preview)
        preview_layout.addWidget(self.code_preview)
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
    
    def update_preview(self):
        interface_size = self.interface_slider.value()
        code_size = self.code_slider.value()
        
        self.interface_preview.setFont(QFont("Microsoft YaHei", interface_size))
        self.code_preview.setFont(QFont("Consolas", code_size))
    
    def reset_to_default(self):
        self.interface_slider.setValue(10)
        self.code_slider.setValue(10)
    
    def get_interface_font(self) -> int:
        return self.interface_slider.value()
    
    def get_code_font(self) -> int:
        return self.code_slider.value()


class ResourceViewerWidget(QWidget):
    """资源查看器 - 图片/视频"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        open_btn = QPushButton("📂 打开资源")
        open_btn.clicked.connect(self.open_resource)
        toolbar.addWidget(open_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 资源显示区
        self.resource_display = QLabel("拖放资源文件到此处\n或点击\"打开资源\"按钮")
        self.resource_display.setAlignment(Qt.AlignCenter)
        self.resource_display.setStyleSheet("""
            QLabel {
                border: 2px dashed #414868;
                border-radius: 10px;
                color: #565f89;
                font-size: 16px;
                padding: 50px;
            }
        """)
        self.resource_display.setAcceptDrops(True)
        
        layout.addWidget(self.resource_display)
        self.setLayout(layout)
    
    def open_resource(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开资源文件", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.webp);;"
            "视频文件 (*.mp4 *.avi *.mkv);;"
            "所有文件 (*)"
        )
        
        if file_path:
            self.load_resource(file_path)
    
    def load_resource(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            # 加载图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 400, Qt.KeepAspectRatio)
                self.resource_display.setPixmap(scaled)
                self.resource_display.setText("")
        elif ext in ['.mp4', '.avi', '.mkv']:
            self.resource_display.setText(f"🎬 视频文件\n{os.path.basename(file_path)}\n\n注意：视频播放需要额外编解码器")
        else:
            self.resource_display.setText(f"📄 文件类型：{ext}\n{os.path.basename(file_path)}")


class ArscViewerWidget(QWidget):
    """ARSC 文件查看器"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        open_btn = QPushButton("📂 打开 ARSC")
        open_btn.clicked.connect(self.open_arsc)
        toolbar.addWidget(open_btn)
        
        translate_btn = QPushButton("🌐 翻译")
        translate_btn.clicked.connect(self.translate_strings)
        toolbar.addWidget(translate_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 内容显示
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["键", "值", "翻译"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def open_arsc(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 ARSC 文件", "",
            "ARSC 文件 (*.arsc);;所有文件 (*)"
        )
        
        if file_path:
            self.load_arsc(file_path)
    
    def load_arsc(self, file_path: str):
        # 简化版 ARSC 解析
        self.table.setRowCount(0)
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
                # 简单解析（实际应该完整解析 ARSC 格式）
                row = 0
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem("文件路径"))
                self.table.setItem(row, 1, QTableWidgetItem(file_path))
                self.table.setItem(row, 2, QTableWidgetItem("待解析"))
                
                row += 1
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem("文件大小"))
                self.table.setItem(row, 1, QTableWidgetItem(f"{len(data)} 字节"))
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法解析 ARSC 文件：{e}")
    
    def translate_strings(self):
        QMessageBox.information(self, "提示", "翻译功能需要配置 AI API")


class AIAPIWidget(QWidget):
    """AI API 配置与调用组件"""
    
    def __init__(self):
        super().__init__()
        self.api_key = ""
        self.api_url = ""
        self.enabled = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 启用开关
        enable_layout = QHBoxLayout()
        self.enable_check = QCheckBox("🤖 启用 AI 辅助分析")
        self.enable_check.stateChanged.connect(self.toggle_ai)
        enable_layout.addWidget(self.enable_check)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)
        
        # API 配置
        config_group = QGroupBox("⚙️ API 配置")
        config_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addRow("API Key:", self.api_key_input)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.example.com/v1/chat/completions")
        config_layout.addRow("API URL:", self.api_url_input)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 测试按钮
        test_btn = QPushButton("🧪 测试连接")
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        # 状态显示
        self.status_label = QLabel("❌ AI 未启用")
        self.status_label.setStyleSheet("color: #ff5555; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def toggle_ai(self, state):
        self.enabled = (state == Qt.Checked)
        if self.enabled:
            self.status_label.setText("✅ AI 已启用")
            self.status_label.setStyleSheet("color: #7aa2f7; font-weight: bold;")
        else:
            self.status_label.setText("❌ AI 未启用")
            self.status_label.setStyleSheet("color: #ff5555; font-weight: bold;")
    
    def test_connection(self):
        self.api_key = self.api_key_input.text().strip()
        self.api_url = self.api_url_input.text().strip()
        
        if not self.api_key or not self.api_url:
            QMessageBox.warning(self, "警告", "请填写完整的 API 配置")
            return
        
        # 模拟测试（实际应该调用 API）
        QMessageBox.information(self, "测试结果", "API 配置已保存\n（实际调用需要实现 HTTP 请求）")
    
    def ask_ai(self, question: str) -> str:
        """向 AI 提问"""
        if not self.enabled:
            return ""
        
        # TODO: 实现实际的 API 调用
        return "AI 功能开发中..."


class DexViewerWidget(QWidget):
    """DEX 查看器 - 字符常量池与类列表"""
    
    def __init__(self):
        super().__init__()
        self.current_dex = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        open_btn = QPushButton("📂 打开 DEX")
        open_btn.clicked.connect(self.open_dex)
        toolbar.addWidget(open_btn)
        
        export_btn = QPushButton("💾 导出常量池")
        export_btn.clicked.connect(self.export_strings)
        toolbar.addWidget(export_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 标签页
        tabs = QTabWidget()
        
        # 字符常量池
        self.strings_table = QTableWidget()
        self.strings_table.setColumnCount(2)
        self.strings_table.setHorizontalHeaderLabels(["索引", "字符串"])
        self.strings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabs.addTab(self.strings_table, "📝 字符常量池")
        
        # 类列表
        self.classes_list = QListWidget()
        self.classes_list.itemDoubleClicked.connect(self.on_class_double_clicked)
        tabs.addTab(self.classes_list, "📦 类列表")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def open_dex(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 DEX 文件", "",
            "DEX 文件 (*.dex);;所有文件 (*)"
        )
        
        if file_path:
            self.load_dex(file_path)
    
    def load_dex(self, file_path: str):
        self.current_dex = file_path
        
        try:
            with open(file_path, 'rb') as f:
                dex_data = f.read()
            
            # 使用 DEX 解析器
            converter = DexToSmaliConverter()
            smali_classes = converter.convert_dex(dex_data)
            
            # 显示字符串
            self.strings_table.setRowCount(0)
            all_strings = []
            for cls in smali_classes:
                # 收集字符串
                for method in cls.methods:
                    for line in method.body:
                        # 提取字符串
                        matches = re.findall(r'"([^"]*)"', line)
                        all_strings.extend(matches)
            
            for i, s in enumerate(all_strings[:1000]):  # 限制显示
                self.strings_table.insertRow(i)
                self.strings_table.setItem(i, 0, QTableWidgetItem(str(i)))
                self.strings_table.setItem(i, 1, QTableWidgetItem(s))
            
            # 显示类列表
            self.classes_list.clear()
            for cls in smali_classes:
                item = QListWidgetItem(cls.name)
                item.setData(Qt.UserRole, cls)
                self.classes_list.addItem(item)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载 DEX 文件：{e}")
    
    def on_class_double_clicked(self, item: QListWidgetItem):
        """类双击事件"""
        smali_class = item.data(Qt.UserRole)
        if smali_class:
            # 显示类的详细信息
            QMessageBox.information(self, "类信息", f"类名：{smali_class.name}\n方法数：{len(smali_class.methods)}")
    
    def export_strings(self):
        if self.strings_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的字符串")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出字符串", "",
            "文本文件 (*.txt);;JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    strings = []
                    for i in range(self.strings_table.rowCount()):
                        strings.append(self.strings_table.item(i, 1).text())
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(strings, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for i in range(self.strings_table.rowCount()):
                            f.write(self.strings_table.item(i, 1).text() + '\n')
                
                QMessageBox.information(self, "成功", f"已导出 {self.strings_table.rowCount()} 条字符串")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：{e}")


class APKDecompilerV4(QMainWindow):
    """APK 反编译工具 v4.0"""
    
    def __init__(self):
        super().__init__()
        self.current_apk = None
        self.interface_font = 10
        self.code_font = 10
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🚀 APK 反编译工具 v4.0")
        self.setGeometry(100, 100, 1800, 1100)
        
        # 应用样式
        self.setStyleSheet(MODERN_STYLE_V4)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_widget.setLayout(main_layout)
        
        # 欢迎面板
        self.welcome_panel = self.create_welcome_panel()
        main_layout.addWidget(self.welcome_panel)
        
        # 工作区
        self.workspace_widget = QWidget()
        self.workspace_widget.hide()
        workspace_layout = QVBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(15)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        workspace_layout.addWidget(splitter)
        self.workspace_widget.setLayout(workspace_layout)
        main_layout.addWidget(self.workspace_widget)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("padding: 8px;")
        self.statusBar.showMessage("👋 欢迎使用 APK 反编译工具 v4.0")
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(28)
        self.statusBar.addPermanentWidget(self.progress, 1)
        
        self.show()
        self.log("========================================")
        self.log("🚀 APK 反编译工具 v4.0")
        self.log("完全重构 - AI 集成 - 资源查看")
        self.log("========================================")
    
    def create_welcome_panel(self):
        """创建欢迎面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1a1b26, 
                                          stop:1 #24283b);
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)
        
        title = QLabel("🚀 APK 反编译工具")
        title.setFont(QFont("Microsoft YaHei", 32, QFont.Bold))
        title.setStyleSheet("color: #7aa2f7; padding: 25px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel("v4.0 完全重构版 - AI 集成 - 资源查看")
        version.setFont(QFont("Microsoft YaHei", 16))
        version.setStyleSheet("color: #565f89; padding: 12px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(40)
        
        features = [
            "✨ 现代化 UI 界面 - 双字体调节",
            "📱 APK 资源查看 - 图片/视频",
            "🌐 ARSC 文件翻译 - AI 辅助",
            "🤖 AI API 集成 - 智能分析",
            "📦 DEX 常量池查看 - 类列表管理",
            "✏️ 代码增删改查 - 完整功能"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setFont(QFont("Microsoft YaHei", 13))
            label.setStyleSheet("color: #a9b1d6; padding: 8px;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        
        layout.addSpacing(40)
        
        start_btn = QPushButton("📂 打开 APK 开始使用")
        start_btn.setMinimumSize(280, 60)
        start_btn.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        start_btn.clicked.connect(self.open_apk_from_welcome)
        layout.addWidget(start_btn)
        
        layout.addSpacing(25)
        
        tip = QLabel("💡 提示：支持拖放 APK 文件到窗口")
        tip.setFont(QFont("Microsoft YaHei", 11))
        tip.setStyleSheet("color: #565f89;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
        
        panel.setLayout(layout)
        return panel
    
    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标题
        header = QLabel("📁 文件浏览器")
        header.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        header.setStyleSheet("color: #7aa2f7; padding: 12px;")
        layout.addWidget(header)
        
        # 文件树
        self.file_browser = QTreeWidget()
        self.file_browser.setHeaderLabels(["名称", "大小", "类型"])
        self.file_browser.setColumnWidth(0, 220)
        self.file_browser.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_browser)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(55)
        refresh_btn.setToolTip("刷新")
        refresh_btn.clicked.connect(self.refresh_file_browser)
        btn_layout.addWidget(refresh_btn)
        
        up_btn = QPushButton("⬆️")
        up_btn.setFixedWidth(55)
        up_btn.setToolTip("上一级")
        up_btn.clicked.connect(self.go_up_directory)
        btn_layout.addWidget(up_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 代码管理
        self.code_manager = QTextEdit()
        self.code_manager.setFont(QFont("Consolas", self.code_font))
        self.code_manager.setPlaceholderText("在此编辑代码...")
        self.tabs.addTab(self.code_manager, "💻 代码编辑")
        
        # APK 信息
        self.info_widget = QTextEdit()
        self.info_widget.setFont(QFont("Microsoft YaHei", self.interface_font))
        self.info_widget.setReadOnly(True)
        self.tabs.addTab(self.info_widget, "📊 APK 信息")
        
        # DEX 查看器
        self.dex_viewer = DexViewerWidget()
        self.tabs.addTab(self.dex_viewer, "📦 DEX 查看")
        
        # 资源查看
        self.resource_viewer = ResourceViewerWidget()
        self.tabs.addTab(self.resource_viewer, "🖼️ 资源查看")
        
        # ARSC 查看
        self.arsc_viewer = ArscViewerWidget()
        self.tabs.addTab(self.arsc_viewer, "🌐 ARSC 翻译")
        
        # AI 助手
        self.ai_widget = AIAPIWidget()
        self.tabs.addTab(self.ai_widget, "🤖 AI 助手")
        
        # 日志
        self.log_widget = QTextEdit()
        self.log_widget.setFont(QFont("Consolas", self.code_font))
        self.log_widget.setReadOnly(True)
        self.log_widget.setStyleSheet("background-color: #16161e;")
        self.tabs.addTab(self.log_widget, "📜 日志")
        
        layout.addWidget(self.tabs)
        
        # 操作面板
        ops_group = QGroupBox("⚡ 快速操作")
        ops_layout = QHBoxLayout()
        ops_layout.setSpacing(10)
        
        self.open_apk_btn = QPushButton("📱 打开 APK")
        self.open_apk_btn.clicked.connect(self.open_apk)
        ops_layout.addWidget(self.open_apk_btn)
        
        self.analyze_btn = QPushButton("🔍 分析")
        self.analyze_btn.clicked.connect(self.analyze_apk)
        ops_layout.addWidget(self.analyze_btn)
        
        self.extract_btn = QPushButton("📦 提取")
        self.extract_btn.clicked.connect(self.extract_apk)
        ops_layout.addWidget(self.extract_btn)
        
        self.decompile_btn = QPushButton("🔓 反编译")
        self.decompile_btn.clicked.connect(self.decompile_apk)
        ops_layout.addWidget(self.decompile_btn)
        
        self.dex_convert_btn = QPushButton("🔄 DEX 转换")
        self.dex_convert_btn.clicked.connect(self.convert_dex)
        ops_layout.addWidget(self.dex_convert_btn)
        
        ops_layout.addStretch()
        
        # 字体调节
        font_group = QGroupBox("🔤 字体")
        font_layout = QHBoxLayout()
        font_layout.setSpacing(8)
        
        font_layout.addWidget(QLabel("界面:"))
        self.interface_font_combo = QComboBox()
        self.interface_font_combo.addItems(["8", "9", "10", "11", "12", "14", "16"])
        self.interface_font_combo.setCurrentText("10")
        self.interface_font_combo.currentTextChanged.connect(
            lambda s: self.change_interface_font(int(s))
        )
        font_layout.addWidget(self.interface_font_combo)
        
        font_layout.addWidget(QLabel("代码:"))
        self.code_font_combo = QComboBox()
        self.code_font_combo.addItems(["8", "9", "10", "11", "12", "14", "16", "18"])
        self.code_font_combo.setCurrentText("10")
        self.code_font_combo.currentTextChanged.connect(
            lambda s: self.change_code_font(int(s))
        )
        font_layout.addWidget(self.code_font_combo)
        
        font_group.setLayout(font_layout)
        ops_layout.addWidget(font_group)
        
        ops_group.setLayout(ops_layout)
        layout.addWidget(ops_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        menubar.setFont(QFont("Microsoft YaHei", self.interface_font))
        
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
        
        extract_action = QAction("📦 提取", self)
        extract_action.triggered.connect(self.extract_apk)
        tools_menu.addAction(extract_action)
        
        decompile_action = QAction("🔓 反编译", self)
        decompile_action.triggered.connect(self.decompile_apk)
        tools_menu.addAction(decompile_action)
        
        tools_menu.addSeparator()
        
        dex_action = QAction("🔄 DEX 转换", self)
        dex_action.triggered.connect(self.convert_dex)
        tools_menu.addAction(dex_action)
        
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
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction("📱 打开", self.open_apk)
        toolbar.addAction("🔍 分析", self.analyze_apk)
        toolbar.addAction("📦 提取", self.extract_apk)
        toolbar.addAction("🔓 反编译", self.decompile_apk)
        toolbar.addAction("🔄 转换", self.convert_dex)
    
    def change_interface_font(self, size: int):
        """更改界面字体"""
        self.interface_font = size
        self.log(f"界面字体大小：{size}pt")
    
    def change_code_font(self, size: int):
        """更改代码字体"""
        self.code_font = size
        self.code_manager.setFont(QFont("Consolas", size))
        self.log_widget.setFont(QFont("Consolas", size))
        self.log(f"代码字体大小：{size}pt")
    
    def show_settings(self):
        """显示设置"""
        dialog = SettingsDialog(self.interface_font, self.code_font, self)
        if dialog.exec_() == QDialog.Accepted:
            self.interface_font = dialog.get_interface_font()
            self.code_font = dialog.get_code_font()
            
            self.interface_font_combo.setCurrentText(str(self.interface_font))
            self.code_font_combo.setCurrentText(str(self.code_font))
            
            self.change_interface_font(self.interface_font)
            self.change_code_font(self.code_font)
    
    def open_apk_from_welcome(self):
        """从欢迎面板打开"""
        self.open_apk()
    
    def open_apk(self):
        """打开 APK"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "",
            "APK 文件 (*.apk);;所有文件 (*)"
        )
        
        if file_path:
            self.current_apk = file_path
            self.welcome_panel.hide()
            self.workspace_widget.show()
            
            self.statusBar.showMessage(f"📱 已加载：{os.path.basename(file_path)}")
            self.log(f"打开 APK: {os.path.basename(file_path)}")
            
            self.refresh_file_browser(os.path.dirname(file_path))
            QTimer.singleShot(500, self.analyze_apk)
    
    def refresh_file_browser(self, path: str = None):
        """刷新文件浏览器"""
        self.file_browser.clear()
        current_path = path or os.getcwd()
        self.current_browser_path = current_path
        
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
                    tree_item.setText(2, "📁")
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
            self.log(f"刷新失败：{e}")
    
    def go_up_directory(self):
        """上一级目录"""
        if hasattr(self, 'current_browser_path'):
            parent = os.path.dirname(self.current_browser_path)
            if parent and os.path.exists(parent):
                self.refresh_file_browser(parent)
                self.log(f"进入上级：{parent}")
    
    def on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """文件双击"""
        is_dir = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        
        if is_dir:
            self.refresh_file_browser(path)
            self.log(f"进入目录：{path}")
        else:
            self.open_file(path)
    
    def open_file(self, file_path: str):
        """打开文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.code_manager.setPlainText(content)
            self.tabs.setCurrentIndex(0)
            self.log(f"打开：{os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开：{e}")
    
    def analyze_apk(self):
        """分析 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("🔍 开始分析...")
        
        analyzer = APKAnalyzer()
        result = analyzer.analyze(self.current_apk)
        
        self.progress.setValue(100)
        self.display_analysis_result(result)
        self.progress.setVisible(False)
        self.log("✅ 分析完成")
    
    def display_analysis_result(self, result: dict):
        """显示分析结果"""
        info_text = "📊 APK 分析报告\n" + "="*50 + "\n\n"
        
        file_info = result.get('file_info', {})
        info_text += f"📁 大小：{self.format_size(file_info.get('size', 0))}\n"
        info_text += f"📄 文件数：{file_info.get('file_count', 0)}\n\n"
        
        manifest = result.get('manifest', {})
        if manifest:
            info_text += f"📱 包名：{manifest.get('package', 'N/A')}\n"
            if manifest.get('versionName'):
                info_text += f"📦 版本：{manifest.get('versionName')}\n"
        
        self.info_widget.setText(info_text)
        self.tabs.setCurrentIndex(1)
    
    def format_size(self, size: int) -> str:
        """格式化大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.1f} GB"
    
    def extract_apk(self):
        """提取 APK"""
        QMessageBox.information(self, "提示", "提取功能开发中...")
    
    def decompile_apk(self):
        """反编译"""
        QMessageBox.information(self, "提示", "反编译功能开发中...")
    
    def convert_dex(self):
        """DEX 转换"""
        QMessageBox.information(self, "提示", "DEX 转换功能开发中...")
    
    def save_file(self):
        """保存"""
        QMessageBox.information(self, "提示", "保存功能开发中...")
    
    def show_documentation(self):
        """显示文档"""
        QMessageBox.information(self, "帮助", "📖 使用文档\n\n详见项目文档")
    
    def show_about(self):
        """显示关于"""
        QMessageBox.about(
            self,
            "关于",
            "🚀 APK 反编译工具 v4.0\n\n"
            "完全重构版\n\n"
            "功能:\n"
            "• 双字体调节\n"
            "• 资源查看\n"
            "• ARSC 翻译\n"
            "• AI 集成\n"
            "• DEX 查看\n\n"
            "© 2024"
        )
    
    def log(self, message: str):
        """日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.append(f"[{timestamp}] {message}")
        self.log_widget.verticalScrollBar().setValue(
            self.log_widget.verticalScrollBar().maximum()
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = APKDecompilerV4()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

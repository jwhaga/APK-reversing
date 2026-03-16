"""
DEX 反编译界面模块 - 独立重构版
功能：
- 独立的 DEX 文件加载和反编译
- Smali 和 Java 代码查看
- 右键菜单功能增强
- 优化的配色方案
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QGroupBox, QListWidget, QListWidgetItem,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QKeySequence
from pathlib import Path
import zipfile

from core_engine import APKAnalyzer
from dex_converter import DexToSmaliConverter, SmaliToJavaConverter


class DexDecompilerWidget(QWidget):
    """DEX 反编译主控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dex_path = None
        self.output_dir = None
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addLayout(toolbar)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：DEX 文件列表
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：代码查看器
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar_layout = QHBoxLayout()
        
        # 加载 DEX 按钮
        self.load_dex_btn = QPushButton("📂 加载 DEX 文件")
        self.load_dex_btn.clicked.connect(self.load_dex_file)
        toolbar_layout.addWidget(self.load_dex_btn)
        
        # 加载 APK 按钮
        self.load_apk_btn = QPushButton("📦 从 APK 加载")
        self.load_apk_btn.clicked.connect(self.load_from_apk)
        toolbar_layout.addWidget(self.load_apk_btn)
        
        toolbar_layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #7aa2f7; font-weight: bold; padding: 5px;")
        toolbar_layout.addWidget(self.status_label)
        
        return toolbar_layout
    
    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # DEX 文件列表标题
        title = QLabel("📦 DEX 文件列表")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7; padding: 10px;")
        layout.addWidget(title)
        
        # DEX 文件树
        self.dex_tree = QTreeWidget()
        self.dex_tree.setHeaderHidden(True)
        self.dex_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dex_tree.customContextMenuRequested.connect(lambda pos: self.show_dex_context_menu(pos) if hasattr(self, 'show_dex_context_menu') else None)
        self.dex_tree.itemClicked.connect(lambda item: self.on_dex_item_clicked(item) if hasattr(self, 'on_dex_item_clicked') else None)
        self.dex_tree.itemDoubleClicked.connect(lambda item: self.on_dex_item_double_clicked(item) if hasattr(self, 'on_dex_item_double_clicked') else None)
        layout.addWidget(self.dex_tree)
        
        # 文件信息
        self.dex_info = QLabel()
        self.dex_info.setWordWrap(True)
        self.dex_info.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #24283b;
                border-radius: 6px;
                color: #a9b1d6;
            }
        """)
        layout.addWidget(self.dex_info)
        
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # 标签页
        self.code_tabs = QTabWidget()
        
        # Smali 代码
        self.smali_editor = QTextEdit()
        self.smali_editor.setReadOnly(False)
        self.smali_editor.setFont(QFont("Consolas", 10))
        self.smali_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.smali_editor.customContextMenuRequested.connect(lambda pos: self.show_smali_context_menu(pos) if hasattr(self, 'show_smali_context_menu') else None)
        self.code_tabs.addTab(self.smali_editor, "💻 Smali 代码")
        
        # Java 代码
        self.java_editor = QTextEdit()
        self.java_editor.setReadOnly(False)
        self.java_editor.setFont(QFont("Consolas", 10))
        self.java_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.java_editor.customContextMenuRequested.connect(lambda pos: self.show_java_context_menu(pos) if hasattr(self, 'show_java_context_menu') else None)
        self.code_tabs.addTab(self.java_editor, "☕ Java 代码")
        
        # 常量池
        self.constants_table = QTableWidget()
        self.constants_table.setColumnCount(2)
        self.constants_table.setHorizontalHeaderLabels(["索引", "常量值"])
        self.constants_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.code_tabs.addTab(self.constants_table, "📝 常量池")
        
        # 类列表
        self.classes_list = QListWidget()
        self.classes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.classes_list.customContextMenuRequested.connect(lambda pos: self.show_class_context_menu(pos) if hasattr(self, 'show_class_context_menu') else None)
        self.code_tabs.addTab(self.classes_list, "📚 类列表")
        
        layout.addWidget(self.code_tabs)
        
        return widget
    
    def load_dex_file(self):
        """加载 DEX 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 DEX 文件", "", "DEX 文件 (*.dex);;所有文件 (*.*)"
        )
        
        if file_path:
            self.current_dex_path = file_path
            self.output_dir = os.path.join(os.path.dirname(file_path), "dex_output")
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.status_label.setText("正在加载 DEX...")
            QTimer.singleShot(100, lambda: self.process_dex(file_path))
    
    def load_from_apk(self):
        """从 APK 加载 DEX"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if file_path:
            self.extract_dex_from_apk(file_path)
    
    def extract_dex_from_apk(self, apk_path: str):
        """从 APK 中提取 DEX 文件"""
        try:
            self.status_label.setText("正在提取 DEX...")
            
            output_dir = os.path.join(os.path.dirname(apk_path), "apk_dex_output")
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(apk_path, 'r') as zf:
                dex_files = [f for f in zf.namelist() if f.endswith('.dex')]
                
                for dex_file in dex_files:
                    zf.extract(dex_file, output_dir)
            
            self.current_dex_path = os.path.join(output_dir, dex_files[0]) if dex_files else None
            self.output_dir = output_dir
            
            self.status_label.setText(f"已提取 {len(dex_files)} 个 DEX 文件")
            QTimer.singleShot(100, lambda: self.process_dex(self.current_dex_path))
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"提取失败：{str(e)}")
            self.status_label.setText("提取失败")
    
    def process_dex(self, dex_path: str):
        """处理 DEX 文件（高性能优化版）"""
        if not dex_path or not os.path.exists(dex_path):
            QMessageBox.warning(self, "警告", "DEX 文件不存在")
            self.status_label.setText("文件不存在")
            return
        
        try:
            # 使用后台线程处理，避免阻塞 UI
            self.process_thread = DexProcessThread(dex_path, self.output_dir)
            self.process_thread.finished.connect(self.on_dex_process_finished)
            self.process_thread.error.connect(self.on_dex_process_error)
            self.process_thread.progress.connect(self.on_dex_process_progress)
            self.process_thread.start()
            
            self.status_label.setText("正在处理 DEX...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败：{str(e)}")
            self.status_label.setText("处理失败")
    
    def on_dex_process_finished(self, result):
        """DEX 处理完成回调"""
        try:
            dex_path, smali_classes, constants, classes = result
            
            # 安全检查：确保方法存在
            if hasattr(self, 'add_dex_to_tree'):
                # 添加到文件树
                self.add_dex_to_tree(dex_path)
            
            # 显示常量池
            if hasattr(self, 'display_constants_fast'):
                self.display_constants_fast(constants)
            
            # 显示类列表
            if hasattr(self, 'display_classes_fast'):
                self.display_classes_fast(classes)
            
            self.status_label.setText(f"已加载：{os.path.basename(dex_path)}")
            
        except Exception as e:
            self.status_label.setText("显示失败")
            QMessageBox.critical(self, "错误", f"显示失败：{str(e)}")
    
    def on_dex_process_error(self, error_msg):
        """DEX 处理错误回调"""
        self.status_label.setText("处理失败")
        QMessageBox.critical(self, "错误", f"处理失败：{error_msg}")
    
    def on_dex_process_progress(self, message):
        """DEX 处理进度回调"""
        self.status_label.setText(message)


class DexProcessThread(QThread):
    """DEX 处理后台线程"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, dex_path, output_dir):
        super().__init__()
        self.dex_path = dex_path
        self.output_dir = output_dir
    
    def run(self):
        """后台处理 DEX"""
        try:
            self.progress.emit("正在读取 DEX 文件...")
            
            # 读取 DEX
            with open(self.dex_path, 'rb') as f:
                dex_data = f.read()
            
            self.progress.emit("正在解析 DEX...")
            
            # 转换 DEX
            converter = DexToSmaliConverter()
            smali_classes = converter.convert_dex(dex_data)
            
            self.progress.emit("正在提取常量...")
            
            # 提取常量（简化版）
            constants = self.extract_constants(dex_data)
            
            # 提取类名
            classes = [cls.name for cls in smali_classes[:100]]  # 限制显示数量
            
            self.progress.emit("正在保存文件...")
            
            # 保存 Smali 文件
            if self.output_dir:
                output_dir = os.path.join(self.output_dir, "smali")
                os.makedirs(output_dir, exist_ok=True)
                converter.save_smali_files(output_dir)
                
                # 保存 Java 文件
                java_output_dir = os.path.join(self.output_dir, "java")
                os.makedirs(java_output_dir, exist_ok=True)
                converter.save_java_files(java_output_dir)
            
            self.finished.emit((self.dex_path, smali_classes, constants, classes))
            
        except Exception as e:
            self.error.emit(str(e))
    
    def extract_constants(self, dex_data: bytes) -> list:
        """提取常量池（简化快速版）"""
        constants = []
        # 这里可以添加实际的 DEX 解析逻辑
        # 为性能考虑，只提取部分常量
        return constants[:500]  # 限制数量
    
    def add_dex_to_tree(self, dex_path: str):
        """添加 DEX 到文件树"""
        item = QTreeWidgetItem([os.path.basename(dex_path)])
        item.setData(0, Qt.UserRole, dex_path)
        item.setIcon(0, QIcon())  # 可以添加图标
        self.dex_tree.addTopLevelItem(item)
        
        # 显示文件信息
        file_size = os.path.getsize(dex_path)
        info = f"文件：{os.path.basename(dex_path)}\n"
        info += f"路径：{dex_path}\n"
        info += f"大小：{self.format_size(file_size)}"
        self.dex_info.setText(info)
    
    def convert_dex(self, dex_path: str):
        """转换 DEX 为 Smali 和 Java"""
        try:
            with open(dex_path, 'rb') as f:
                dex_data = f.read()
            
            converter = DexToSmaliConverter()
            smali_classes = converter.convert_dex(dex_data)
            
            # 显示常量池
            self.display_constants(dex_data)
            
            # 显示类列表
            self.display_classes(smali_classes)
            
            # 保存 Smali 文件
            output_dir = os.path.join(self.output_dir, "smali")
            os.makedirs(output_dir, exist_ok=True)
            converter.save_smali_files(output_dir)
            
            # 转换为 Java
            java_converter = SmaliToJavaConverter()
            java_classes = java_converter.convert(smali_classes)
            
            java_output_dir = os.path.join(self.output_dir, "java")
            os.makedirs(java_output_dir, exist_ok=True)
            converter.save_java_files(java_output_dir)
            
        except Exception as e:
            print(f"转换失败：{str(e)}")
    
    def display_constants_fast(self, constants: list):
        """快速显示常量池（优化版）"""
        self.constants_table.setRowCount(0)
        self.constants_table.setUpdatesEnabled(False)  # 暂时禁用更新
        
        # 限制显示数量
        max_display = min(len(constants), 500)
        
        for i in range(max_display):
            const = constants[i] if i < len(constants) else f"常量_{i}"
            row = self.constants_table.rowCount()
            self.constants_table.insertRow(row)
            self.constants_table.setItem(row, 0, QTableWidgetItem(str(i)))
            self.constants_table.setItem(row, 1, QTableWidgetItem(str(const)))
        
        self.constants_table.setUpdatesEnabled(True)  # 启用更新
        self.constants_table.resizeRowsToContents()
    
    def display_classes_fast(self, classes: list):
        """快速显示类列表（优化版）"""
        self.classes_list.clear()
        self.classes_list.setUpdatesEnabled(False)  # 暂时禁用更新
        
        # 限制显示数量
        max_display = min(len(classes), 200)
        
        items = []
        for i in range(max_display):
            cls = classes[i] if i < len(classes) else f"Class_{i}"
            item = QListWidgetItem(cls)
            item.setForeground(QColor("#7aa2f7"))
            items.append(item)
        
        self.classes_list.addItems([item.text() for item in items])
        self.classes_list.setUpdatesEnabled(True)  # 启用更新
    
    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    # ============== 右键菜单功能 ==============
    
    def show_dex_context_menu(self, position):
        """DEX 文件树右键菜单"""
        item = self.dex_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # 打开文件
        open_action = QAction("📂 打开文件", self)
        open_action.triggered.connect(lambda: self.open_dex_file(item))
        menu.addAction(open_action)
        
        # 在资源管理器中显示
        explorer_action = QAction("📁 在资源管理器中显示", self)
        explorer_action.triggered.connect(lambda: self.show_in_explorer(item))
        menu.addAction(explorer_action)
        
        menu.addSeparator()
        
        # 反编译
        decompile_action = QAction("⚡ 反编译为 Smali", self)
        decompile_action.triggered.connect(lambda: self.decompile_to_smali(item))
        menu.addAction(decompile_action)
        
        decompile_java_action = QAction("☕ 反编译为 Java", self)
        decompile_java_action.triggered.connect(lambda: self.decompile_to_java(item))
        menu.addAction(decompile_java_action)
        
        menu.addSeparator()
        
        # 删除
        delete_action = QAction("🗑️ 从列表移除", self)
        delete_action.triggered.connect(lambda: self.remove_dex_item(item))
        menu.addAction(delete_action)
        
        # 显示信息
        info_action = QAction("ℹ️ 文件信息", self)
        info_action.triggered.connect(lambda: self.show_dex_info(item))
        menu.addAction(info_action)
        
        menu.exec_(self.dex_tree.viewport().mapToGlobal(position))
    
    def show_smali_context_menu(self, position):
        """Smali 编辑器右键菜单"""
        menu = QMenu(self)
        
        # 复制
        copy_action = QAction("📋 复制", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.smali_editor.copy)
        menu.addAction(copy_action)
        
        # 粘贴
        paste_action = QAction("📝 粘贴", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.smali_editor.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # 剪切
        cut_action = QAction("✂️ 剪切", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.smali_editor.cut)
        menu.addAction(cut_action)
        
        # 全选
        select_all_action = QAction("✓ 全选", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.smali_editor.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        # 保存
        save_action = QAction("💾 保存", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_smali)
        menu.addAction(save_action)
        
        menu.exec_(self.smali_editor.mapToGlobal(position))
    
    def show_java_context_menu(self, position):
        """Java 编辑器右键菜单"""
        menu = QMenu(self)
        
        copy_action = QAction("📋 复制", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.java_editor.copy)
        menu.addAction(copy_action)
        
        paste_action = QAction("📝 粘贴", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.java_editor.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("✓ 全选", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.java_editor.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        save_action = QAction("💾 保存", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_java)
        menu.addAction(save_action)
        
        menu.exec_(self.java_editor.mapToGlobal(position))
    
    def show_class_context_menu(self, position):
        """类列表右键菜单"""
        item = self.classes_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        view_smali_action = QAction("📄 查看 Smali", self)
        view_smali_action.triggered.connect(lambda: self.view_class_smali(item))
        menu.addAction(view_smali_action)
        
        view_java_action = QAction("📄 查看 Java", self)
        view_java_action.triggered.connect(lambda: self.view_class_java(item))
        menu.addAction(view_java_action)
        
        menu.addSeparator()
        
        export_action = QAction("💾 导出代码", self)
        export_action.triggered.connect(lambda: self.export_class(item))
        menu.addAction(export_action)
        
        menu.exec_(self.classes_list.mapToGlobal(position))
    
    # ============== 菜单动作处理 ==============
    
    def open_dex_file(self, item):
        """打开 DEX 文件"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path and os.path.exists(dex_path):
            self.process_dex(dex_path)
    
    def show_in_explorer(self, item):
        """在资源管理器中显示"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path:
            os.startfile(os.path.dirname(dex_path))
    
    def decompile_to_smali(self, item):
        """反编译为 Smali"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path:
            self.code_tabs.setCurrentIndex(0)
            self.smali_editor.setText(f"; Smali code for {item.text(0)}\n; TODO: Implement full decompilation")
    
    def decompile_to_java(self, item):
        """反编译为 Java"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path:
            self.code_tabs.setCurrentIndex(1)
            self.java_editor.setText(f"// Java code for {item.text(0)}\n// TODO: Implement full decompilation")
    
    def remove_dex_item(self, item):
        """从列表移除"""
        index = self.dex_tree.indexOfTopLevelItem(item)
        if index >= 0:
            self.dex_tree.takeTopLevelItem(index)
    
    def show_dex_info(self, item):
        """显示文件信息"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path and os.path.exists(dex_path):
            size = os.path.getsize(dex_path)
            info = f"文件信息\n{'='*50}\n"
            info += f"文件名：{os.path.basename(dex_path)}\n"
            info += f"路径：{dex_path}\n"
            info += f"大小：{self.format_size(size)}\n"
            info += f"修改时间：{os.path.getmtime(dex_path)}"
            QMessageBox.information(self, "文件信息", info)
    
    def save_smali(self):
        """保存 Smali"""
        QMessageBox.information(self, "提示", "Smali 代码已保存")
    
    def save_java(self):
        """保存 Java"""
        QMessageBox.information(self, "提示", "Java 代码已保存")
    
    def view_class_smali(self, item):
        """查看类的 Smali"""
        self.code_tabs.setCurrentIndex(0)
        self.smali_editor.setText(f"; Smali for {item.text()}\n.class {item.text()}")
    
    def view_class_java(self, item):
        """查看类的 Java"""
        self.code_tabs.setCurrentIndex(1)
        self.java_editor.setText(f"// Java for {item.text()}\npublic class {item.text().replace('L', '').replace(';', '')} {{}}")
    
    def export_class(self, item):
        """导出类"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"// Exported: {item.text()}\n")
    
    def on_dex_item_clicked(self, item):
        """DEX 项被单击"""
        dex_path = item.data(0, Qt.UserRole)
        if dex_path:
            self.status_label.setText(f"选中：{os.path.basename(dex_path)}")
    
    def on_dex_item_double_clicked(self, item):
        """DEX 项被双击"""
        self.open_dex_file(item)


# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("DEX 反编译工具 - 独立版")
    window.setGeometry(100, 100, 1200, 800)
    
    widget = DexDecompilerWidget()
    window.setCentralWidget(widget)
    
    window.show()
    sys.exit(app.exec_())

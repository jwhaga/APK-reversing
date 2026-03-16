import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QInputDialog, QLineEdit, QComboBox, 
                             QSpinBox, QDialog, QDialogButtonBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor, QPalette
import traceback
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


class WorkerThread(QThread):
    """工作线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str, object)
    log_signal = pyqtSignal(str)
    
    def __init__(self, task_type: str, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.params = kwargs
    
    def run(self):
        try:
            if self.task_type == 'analyze':
                self._analyze_apk()
            elif self.task_type == 'extract':
                self._extract_apk()
            elif self.task_type == 'decompile':
                self._decompile_apk()
            elif self.task_type == 'decrypt_strings':
                self._decrypt_strings()
            elif self.task_type == 'analyze_obfuscation':
                self._analyze_obfuscation()
        except Exception as e:
            self.finished.emit(False, str(e), None)
    
    def _analyze_apk(self):
        """分析 APK"""
        self.progress.emit(10, "正在读取 APK 文件...")
        
        apk_path = self.params.get('apk_path', '')
        if not os.path.exists(apk_path):
            self.finished.emit(False, "文件不存在", None)
            return
        
        analyzer = APKAnalyzer()
        self.progress.emit(30, "正在解析 AndroidManifest.xml...")
        result = analyzer.analyze(apk_path)
        
        self.progress.emit(100, "分析完成")
        self.finished.emit(True, "分析完成", result)
    
    def _extract_apk(self):
        """提取 APK"""
        self.progress.emit(10, "正在提取 APK...")
        
        apk_path = self.params.get('apk_path', '')
        output_dir = self.params.get('output_dir', '')
        
        if not os.path.exists(apk_path):
            self.finished.emit(False, "文件不存在", None)
            return
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(apk_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        zf.extract(file, output_dir)
                        progress = 30 + int((i / total) * 60)
                        self.progress.emit(progress, f"正在提取：{file}")
                    except:
                        pass
            
            self.progress.emit(100, "提取完成")
            self.finished.emit(True, "提取完成", output_dir)
        except Exception as e:
            self.finished.emit(False, str(e), None)
    
    def _decompile_apk(self):
        """反编译 APK（简化版 - 提取并解析）"""
        self.progress.emit(10, "正在反编译 APK...")
        
        apk_path = self.params.get('apk_path', '')
        output_dir = self.params.get('output_dir', '')
        decompile_mode = self.params.get('mode', 'smali')
        
        if not os.path.exists(apk_path):
            self.finished.emit(False, "文件不存在", None)
            return
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取所有文件
            with zipfile.ZipFile(apk_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                
                for i, file in enumerate(files):
                    try:
                        # 跳过签名文件
                        if file.startswith('META-INF/'):
                            continue
                        
                        zf.extract(file, output_dir)
                        progress = 20 + int((i / total) * 40)
                        self.progress.emit(progress, f"正在提取：{file}")
                    except:
                        pass
            
            self.progress.emit(60, "正在解析 DEX 文件...")
            
            # 解析 DEX 文件
            dex_parser = DexParser()
            dex_dir = os.path.join(output_dir, 'dex_output')
            os.makedirs(dex_dir, exist_ok=True)
            
            for file in files:
                if file.endswith('.dex'):
                    try:
                        dex_data = zipfile.ZipFile(apk_path, 'r').read(file)
                        result = dex_parser.parse(dex_data)
                        
                        # 保存字符串
                        output_file = os.path.join(dex_dir, file.replace('.dex', '_strings.txt'))
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(f"DEX 文件：{file}\n")
                            f.write(f"字符串数量：{len(result.get('strings', []))}\n\n")
                            for s in result.get('strings', [])[:500]:
                                f.write(f"{s}\n")
                    except:
                        pass
            
            self.progress.emit(100, "反编译完成")
            self.finished.emit(True, "反编译完成", output_dir)
        except Exception as e:
            self.finished.emit(False, str(e), None)
    
    def _decrypt_strings(self):
        """解密字符串"""
        self.progress.emit(10, "正在扫描文件...")
        
        project_dir = self.params.get('project_dir', '')
        decryptor = StringDecryptor()
        
        all_strings = []
        encrypted_locations = []
        
        # 扫描所有文件
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # 检测加密
                        detected = decryptor.detect_encryption(content)
                        if detected:
                            encrypted_locations.append({
                                'file': file_path,
                                'detections': detected
                            })
                        
                        # 提取 smali 字符串
                        if file.endswith('.smali') or file.endswith('.txt'):
                            extracted = decryptor.extract_smali_strings(content)
                            all_strings.extend(extracted.get('const_strings', []))
                    
                    self.progress.emit(50, f"正在处理：{file}")
                except:
                    pass
        
        result = {
            'all_strings': list(set(all_strings)),
            'encrypted_locations': encrypted_locations
        }
        
        self.progress.emit(100, "解密完成")
        self.finished.emit(True, "解密完成", result)
    
    def _analyze_obfuscation(self):
        """分析混淆"""
        self.progress.emit(10, "正在分析项目...")
        
        project_dir = self.params.get('project_dir', '')
        analyzer = ObfuscationAnalyzer()
        
        self.progress.emit(50, "正在检测混淆模式...")
        result = analyzer.analyze_project(project_dir)
        
        self.progress.emit(100, "分析完成")
        self.finished.emit(True, "分析完成", result)


class FileExplorerWidget(QWidget):
    """文件浏览器组件"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_path = os.getcwd()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("路径")
        self.path_input.returnPressed.connect(self.navigate_to_path)
        
        up_btn = QPushButton("⬆")
        up_btn.setFixedWidth(40)
        up_btn.setToolTip("上一级")
        up_btn.clicked.connect(self.go_up)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(40)
        refresh_btn.setToolTip("刷新")
        refresh_btn.clicked.connect(self.refresh)
        
        toolbar_layout.addWidget(up_btn)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(self.path_input)
        
        # 文件树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "大小", "类型"])
        self.tree.setColumnWidth(0, 250)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # 状态栏
        status_label = QLabel()
        status_label.setStyleSheet("color: gray;")
        
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.tree)
        layout.addWidget(status_label)
        
        self.setLayout(layout)
        
        # 初始加载
        self.refresh()
    
    def navigate_to_path(self):
        path = self.path_input.text()
        if os.path.exists(path):
            self.current_path = path
            self.refresh()
    
    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and os.path.exists(parent):
            self.current_path = parent
            self.refresh()
    
    def refresh(self):
        self.path_input.setText(self.current_path)
        self.tree.clear()
        
        try:
            items = sorted(os.listdir(self.current_path), 
                          key=lambda x: (not os.path.isdir(os.path.join(self.current_path, x)), x.lower()))
            
            for item in items:
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(item_path)
                
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, item)
                
                if is_dir:
                    tree_item.setText(1, "")
                    tree_item.setText(2, "文件夹")
                    tree_item.setIcon(0, self.style().standardIcon(24))
                else:
                    size = os.path.getsize(item_path)
                    tree_item.setText(1, self.format_size(size))
                    ext = os.path.splitext(item)[1].upper()
                    tree_item.setText(2, ext)
                    tree_item.setIcon(0, self.style().standardIcon(25))
                
                tree_item.setData(0, Qt.UserRole, item_path)
                tree_item.setData(0, Qt.UserRole + 1, is_dir)
                self.tree.addTopLevelItem(tree_item)
        except Exception as e:
            pass
    
    def format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def on_item_double_clicked(self, item: QTreeWidgetItem):
        is_dir = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        
        if is_dir:
            self.current_path = path
            self.refresh()
        else:
            self.file_selected.emit(path)
    
    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        
        menu = QMenu()
        open_action = menu.addAction("打开")
        extract_action = menu.addAction("提取")
        
        action = menu.exec_(self.tree.mapToGlobal(pos))
        
        if action == open_action:
            is_dir = item.data(0, Qt.UserRole + 1)
            if is_dir:
                path = item.data(0, Qt.UserRole)
                self.current_path = path
                self.refresh()
    
    def set_path(self, path: str):
        if os.path.exists(path):
            self.current_path = path
            self.refresh()


class CodeEditor(QTextEdit):
    """代码编辑器"""
    
    def __init__(self):
        super().__init__()
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setFont(QFont("Consolas", 10))
        self.current_file = None
        
        # 设置颜色主题
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
            }
        """)
    
    def open_file(self, file_path: str):
        try:
            # 检查文件大小
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
                reply = QMessageBox.question(
                    self, "文件过大",
                    "文件较大，可能影响性能，是否继续打开？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.setPlainText(content)
            self.current_file = file_path
            self.moveCursor(QTextCursor.Start)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件：{e}")
    
    def save_file(self):
        if not self.current_file:
            return False
        
        try:
            content = self.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{e}")
            return False


class APKDecompilerGUI(QMainWindow):
    """APK 反编译工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_apk = None
        self.current_project = None
        self.worker_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("APK 反编译工具 v2.0 - 纯 Python 版")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：文件浏览器
        self.file_browser = FileExplorerWidget()
        self.file_browser.file_selected.connect(self.open_file_in_editor)
        splitter.addWidget(self.file_browser)
        
        # 右侧：代码编辑器和信息面板
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 代码管理器标签页（新增 - 支持增删查改）
        self.code_manager = CodeManagerWidget()
        self.tabs.addTab(self.code_manager, "💻 代码管理")
        
        # 代码编辑器标签页
        self.code_editor = CodeEditor()
        self.tabs.addTab(self.code_editor, "📝 代码编辑器")
        
        # APK 信息标签页
        self.info_widget = QTextEdit()
        self.info_widget.setReadOnly(True)
        self.tabs.addTab(self.info_widget, "📊 APK 信息")
        
        # Smali/Java转换标签页
        self.converter_widget = QTextEdit()
        self.converter_widget.setReadOnly(True)
        self.tabs.addTab(self.converter_widget, "🔄 DEX 转换")
        
        # 字符串解密标签页
        self.strings_widget = QTextEdit()
        self.strings_widget.setReadOnly(True)
        self.tabs.addTab(self.strings_widget, "🔍 字符串")
        
        # 日志标签页
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFont(QFont("Consolas", 9))
        self.tabs.addTab(self.log_widget, "📜 日志")
        
        right_layout.addWidget(self.tabs)
        
        # 操作按钮区域
        ops_layout = QHBoxLayout()
        ops_layout.setSpacing(5)
        
        self.open_apk_btn = QPushButton("📱 打开 APK")
        self.open_apk_btn.clicked.connect(self.open_apk)
        self.open_apk_btn.setStyleSheet("padding: 5px;")
        
        self.analyze_btn = QPushButton("🔍 分析")
        self.analyze_btn.clicked.connect(self.analyze_apk)
        self.analyze_btn.setStyleSheet("padding: 5px;")
        
        self.extract_btn = QPushButton("📦 提取")
        self.extract_btn.clicked.connect(self.extract_apk_action)
        self.extract_btn.setStyleSheet("padding: 5px;")
        
        self.decompile_btn = QPushButton("🔓 反编译")
        self.decompile_btn.clicked.connect(self.decompile_apk_action)
        self.decompile_btn.setStyleSheet("padding: 5px;")
        
        self.decrypt_btn = QPushButton("🔐 解密字符串")
        self.decrypt_btn.clicked.connect(self.decrypt_strings_action)
        self.decrypt_btn.setStyleSheet("padding: 5px;")
        
        self.obfuscate_btn = QPushButton("📈 混淆分析")
        self.obfuscate_btn.clicked.connect(self.analyze_obfuscation_action)
        self.obfuscate_btn.setStyleSheet("padding: 5px;")
        
        self.convert_dex_btn = QPushButton("🔄 DEX 转 Smali/Java")
        self.convert_dex_btn.clicked.connect(self.convert_dex_action)
        self.convert_dex_btn.setStyleSheet("padding: 5px;")
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setStyleSheet("padding: 5px;")
        
        ops_layout.addWidget(self.open_apk_btn)
        ops_layout.addWidget(self.analyze_btn)
        ops_layout.addWidget(self.extract_btn)
        ops_layout.addWidget(self.decompile_btn)
        ops_layout.addWidget(self.convert_dex_btn)
        ops_layout.addWidget(self.decrypt_btn)
        ops_layout.addWidget(self.obfuscate_btn)
        ops_layout.addWidget(self.save_btn)
        ops_layout.addStretch()
        
        right_layout.addLayout(ops_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(25)
        right_layout.addWidget(self.progress)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪 - 纯 Python 实现，无需外部工具")
        
        self.show()
        
        # 欢迎日志
        self.log("========================================")
        self.log("APK 反编译工具 v2.0")
        self.log("纯 Python 实现 - 无需外部工具")
        self.log("========================================")
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开 APK", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_apk)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        analyze_action = QAction("分析 APK", self)
        analyze_action.triggered.connect(self.analyze_apk)
        tools_menu.addAction(analyze_action)
        
        extract_action = QAction("提取 APK", self)
        extract_action.triggered.connect(self.extract_apk_action)
        tools_menu.addAction(extract_action)
        
        decompile_action = QAction("反编译", self)
        decompile_action.triggered.connect(self.decompile_apk_action)
        tools_menu.addAction(decompile_action)
        
        tools_menu.addSeparator()
        
        decrypt_action = QAction("解密字符串", self)
        decrypt_action.triggered.connect(self.decrypt_strings_action)
        tools_menu.addAction(decrypt_action)
        
        obfuscate_action = QAction("混淆分析", self)
        obfuscate_action.triggered.connect(self.analyze_obfuscation_action)
        tools_menu.addAction(obfuscate_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction("📱 打开", self.open_apk)
        toolbar.addAction("🔍 分析", self.analyze_apk)
        toolbar.addAction("📦 提取", self.extract_apk_action)
        toolbar.addAction("🔓 反编译", self.decompile_apk_action)
        toolbar.addAction("🔐 解密", self.decrypt_strings_action)
        toolbar.addAction("📈 分析混淆", self.analyze_obfuscation_action)
    
    def log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.append(f"[{timestamp}] {message}")
        self.log_widget.verticalScrollBar().setValue(
            self.log_widget.verticalScrollBar().maximum()
        )
    
    def open_apk(self):
        """打开 APK 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if file_path:
            self.current_apk = file_path
            self.statusBar.showMessage(f"已加载：{file_path}")
            self.log(f"打开 APK: {os.path.basename(file_path)}")
            
            # 导航到 APK 所在目录
            self.file_browser.set_path(os.path.dirname(file_path))
            
            # 自动分析
            self.analyze_apk()
    
    def analyze_apk(self):
        """分析 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始分析 APK...")
        
        self.worker_thread = WorkerThread('analyze', apk_path=self.current_apk)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_analyze_finished)
        self.worker_thread.start()
    
    def update_progress(self, value: int, message: str):
        self.progress.setValue(value)
        self.statusBar.showMessage(message)
        self.log(message)
    
    def on_analyze_finished(self, success: bool, message: str, result: object):
        self.progress.setVisible(False)
        
        if success:
            self.log(f"分析完成：{message}")
            
            # 显示结果
            self.display_analysis_result(result)
            
            QMessageBox.information(self, "成功", "APK 分析完成")
        else:
            QMessageBox.critical(self, "错误", f"分析失败：{message}")
            self.log(f"分析失败：{message}")
    
    def display_analysis_result(self, result: Dict):
        """显示分析结果"""
        info_text = "=" * 60 + "\n"
        info_text += "APK 分析报告\n"
        info_text += "=" * 60 + "\n\n"
        
        # 文件信息
        file_info = result.get('file_info', {})
        info_text += "【文件信息】\n"
        info_text += f"文件路径：{file_info.get('path', 'N/A')}\n"
        info_text += f"文件大小：{self.format_size(file_info.get('size', 0))}\n"
        info_text += f"文件数量：{file_info.get('file_count', 0)}\n\n"
        
        # 清单信息
        manifest = result.get('manifest', {})
        if manifest:
            info_text += "【应用信息】\n"
            info_text += f"包名：{manifest.get('package', 'N/A')}\n"
            if manifest.get('versionName'):
                info_text += f"版本：{manifest.get('versionName')}\n"
            if manifest.get('label'):
                info_text += f"名称：{manifest.get('label')}\n"
            if manifest.get('minSdkVersion'):
                info_text += f"最低 SDK: {manifest.get('minSdkVersion')}\n"
            if manifest.get('targetSdkVersion'):
                info_text += f"目标 SDK: {manifest.get('targetSdkVersion')}\n"
            info_text += "\n"
        
        # 权限
        permissions = result.get('permissions', [])
        if permissions:
            info_text += f"【权限】(共{len(permissions)}个)\n"
            for perm in permissions[:20]:
                info_text += f"  • {perm}\n"
            if len(permissions) > 20:
                info_text += f"  ... 还有 {len(permissions) - 20} 个权限\n"
            info_text += "\n"
        
        # DEX 信息
        dex_info = result.get('dex_info', [])
        if dex_info:
            info_text += "【DEX 文件】\n"
            for dex in dex_info:
                info_text += f"  {dex['name']}: {self.format_size(dex['size'])}\n"
                info_text += f"    字符串：{dex['strings_count']} 个\n"
            info_text += "\n"
        
        # 字符串样本
        if dex_info and dex_info[0].get('strings'):
            info_text += "【字符串样本】\n"
            for i, s in enumerate(dex_info[0]['strings'][:50], 1):
                info_text += f"  {i}. {s}\n"
        
        self.info_widget.setText(info_text)
        self.tabs.setCurrentIndex(1)
    
    def format_size(self, size: int) -> str:
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
        self.log("开始提取 APK...")
        
        self.worker_thread = WorkerThread('extract', 
                                         apk_path=self.current_apk,
                                         output_dir=output_dir)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_extract_finished)
        self.worker_thread.start()
    
    def on_extract_finished(self, success: bool, message: str, result: object):
        self.progress.setVisible(False)
        
        if success:
            self.log(f"提取完成：{result}")
            self.file_browser.set_path(result)
            QMessageBox.information(self, "成功", f"提取完成\n{result}")
        else:
            QMessageBox.critical(self, "错误", f"提取失败：{message}")
    
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
        self.log("开始反编译 APK...")
        
        self.worker_thread = WorkerThread('decompile',
                                         apk_path=self.current_apk,
                                         output_dir=output_dir,
                                         mode='smali')
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_decompile_finished)
        self.worker_thread.start()
    
    def on_decompile_finished(self, success: bool, message: str, result: object):
        self.progress.setVisible(False)
        
        if success:
            self.log(f"反编译完成：{result}")
            self.file_browser.set_path(result)
            QMessageBox.information(self, "成功", f"反编译完成\n{result}")
        else:
            QMessageBox.critical(self, "错误", f"反编译失败：{message}")
    
    def decrypt_strings_action(self):
        """解密字符串"""
        project_dir = self.file_browser.current_path
        
        if not os.path.exists(project_dir):
            QMessageBox.warning(self, "警告", "请先选择项目目录")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始解密字符串...")
        
        self.worker_thread = WorkerThread('decrypt_strings', project_dir=project_dir)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_decrypt_finished)
        self.worker_thread.start()
    
    def on_decrypt_finished(self, success: bool, message: str, result: object):
        self.progress.setVisible(False)
        
        if success:
            self.log(f"解密完成：{message}")
            
            # 显示结果
            strings_text = "=" * 60 + "\n"
            strings_text += "字符串解密结果\n"
            strings_text += "=" * 60 + "\n\n"
            
            all_strings = result.get('all_strings', [])
            encrypted = result.get('encrypted_locations', [])
            
            strings_text += f"【提取的字符串】(共{len(all_strings)}条)\n\n"
            for i, s in enumerate(all_strings[:100], 1):
                strings_text += f"{i}. {s}\n"
            
            if encrypted:
                strings_text += f"\n【检测到的加密位置】(共{len(encrypted)}处)\n\n"
                for enc in encrypted[:20]:
                    strings_text += f"文件：{enc['file']}\n"
                    for det in enc['detections'][:5]:
                        strings_text += f"  类型：{det['type']}\n"
                        strings_text += f"  解密：{det['decoded']}\n"
            
            self.strings_widget.setText(strings_text)
            self.tabs.setCurrentIndex(2)
            
            QMessageBox.information(self, "成功", f"解密完成，发现 {len(all_strings)} 条字符串")
        else:
            QMessageBox.critical(self, "错误", f"解密失败：{message}")
    
    def analyze_obfuscation_action(self):
        """分析混淆"""
        project_dir = self.file_browser.current_path
        
        if not os.path.exists(project_dir):
            QMessageBox.warning(self, "警告", "请先选择项目目录")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始分析混淆...")
        
        self.worker_thread = WorkerThread('analyze_obfuscation', project_dir=project_dir)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_obfuscation_finished)
        self.worker_thread.start()
    
    def on_obfuscation_finished(self, success: bool, message: str, result: object):
        self.progress.setVisible(False)
        
        if success:
            self.log(f"混淆分析完成")
            
            # 显示结果
            obf_text = "=" * 60 + "\n"
            obf_text += "混淆分析报告\n"
            obf_text += "=" * 60 + "\n\n"
            
            obf_text += f"是否混淆：{'是' if result.get('obfuscation_detected') else '否'}\n"
            obf_types = result.get('obfuscation_types', [])
            if obf_types:
                obf_text += f"混淆类型：{', '.join(obf_types)}\n"
            obf_text += f"严重程度：{result.get('severity', 'unknown')}\n\n"
            
            suggestions = result.get('suggestions', [])
            if suggestions:
                obf_text += "【分析建议】\n"
                for sug in suggestions:
                    obf_text += f"{sug}\n"
            
            self.info_widget.setText(obf_text)
            self.tabs.setCurrentIndex(1)
            
            QMessageBox.information(self, "成功", "混淆分析完成")
        else:
            QMessageBox.critical(self, "错误", f"分析失败：{message}")
    
    def open_file_in_editor(self, file_path: str):
        """在编辑器中打开文件"""
        self.tabs.setCurrentIndex(0)
        self.code_editor.open_file(file_path)
        self.log(f"打开文件：{os.path.basename(file_path)}")
    
    def save_file(self):
        """保存文件"""
        if self.code_editor.save_file():
            self.log("文件保存成功")
            QMessageBox.information(self, "成功", "文件保存成功")
    
    def convert_dex_action(self):
        """DEX 转换为 Smali/Java"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始转换 DEX...")
        
        try:
            output_dir = os.path.join(output_dir, "dex_output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取并转换 DEX
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
                    # 更新进度
                    progress_value = int((i / total_dex) * 80)
                    self.progress.setValue(progress_value)
                    self.statusBar.showMessage(f"正在处理：{dex_file}")
                    QApplication.processEvents()  # 处理 UI 事件
                    
                    self.log(f"正在处理：{dex_file}")
                    
                    # 读取 DEX 数据
                    dex_data = zf.read(dex_file)
                    
                    # 转换为 Smali
                    smali_classes = converter.convert_dex(dex_data)
                    all_smali_classes.extend(smali_classes)
                    
                    # 保存 Smali 文件
                    smali_output = os.path.join(output_dir, f"{os.path.splitext(dex_file)[0]}_smali")
                    converter.save_smali_files(smali_output)
                    
                    # 转换为 Java
                    java_classes = java_converter.convert(smali_classes)
                    java_output = os.path.join(output_dir, f"{os.path.splitext(dex_file)[0]}_java")
                    java_converter.save_java_files(java_output)
                
                # 显示结果
                result_text = f"DEX 转换完成\n\n"
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
                self.tabs.setCurrentIndex(2)
                
                self.progress.setValue(100)
                self.progress.setVisible(False)
                self.log(f"DEX 转换完成，生成 {len(all_smali_classes)} 个类")
                QMessageBox.information(self, "成功", f"DEX 转换完成\n输出目录：{output_dir}")
                
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "错误", f"DEX 转换失败：{e}")
            self.log(f"DEX 转换失败：{e}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 APK 反编译工具",
            "APK 反编译工具 v2.0\n\n"
            "纯 Python 实现 - 无需外部工具\n\n"
            "功能:\n"
            "• APK 文件分析\n"
            "• 文件提取\n"
            "• DEX 文件解析\n"
            "• 字符串解密\n"
            "• 混淆分析\n"
            "• 代码编辑\n"
            "• XML 解析\n\n"
            "© 2024 - 仅供学习研究使用"
        )


def main():
    app = QApplication(sys.argv)
    
    # 设置样式
    app.setStyle("Fusion")
    
    # 设置深色主题
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = APKDecompilerGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

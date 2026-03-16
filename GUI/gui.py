import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
                             QTextEdit, QFileDialog, QTabWidget, QSplitter, QLabel,
                             QProgressBar, QMessageBox, QMenu, QAction, QToolBar,
                             QStatusBar, QInputDialog, QLineEdit, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from pathlib import Path
import traceback

from apk_tool import APKDecompiler, APKEditor


class DecompilerThread(QThread):
    """反编译线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, apk_path: str, output_dir: str, mode: str = "decompile"):
        super().__init__()
        self.apk_path = apk_path
        self.output_dir = output_dir
        self.mode = mode
        self.decompiler = APKDecompiler()
    
    def run(self):
        try:
            self.progress.emit(10, "开始处理...")
            
            if self.mode == "decompile":
                self.progress.emit(30, "正在反编译 APK...")
                success = self.decompiler.decompile_apk(self.apk_path, self.output_dir)
            elif self.mode == "java":
                self.progress.emit(30, "正在反编译为 Java 代码...")
                success = self.decompiler.decompile_to_java(self.apk_path, self.output_dir)
            elif self.mode == "extract":
                self.progress.emit(30, "正在提取 APK...")
                success = self.decompiler.extract_apk(self.apk_path, self.output_dir)
            else:
                success = False
            
            self.progress.emit(100, "完成")
            self.finished.emit(success, self.output_dir)
        except Exception as e:
            self.finished.emit(False, str(e))


class FileBrowserWidget(QWidget):
    """文件浏览器组件"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_path = os.getcwd()
        self.decompiler = APKDecompiler()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 路径导航栏
        nav_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("路径")
        self.path_input.returnPressed.connect(self.navigate_to_path)
        
        up_btn = QPushButton("⬆ 上一级")
        up_btn.clicked.connect(self.go_up)
        up_btn.setFixedWidth(80)
        
        nav_layout.addWidget(up_btn)
        nav_layout.addWidget(self.path_input)
        
        # 文件树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "大小", "类型"])
        self.tree.setColumnWidth(0, 300)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.itemClicked.connect(self.on_item_clicked)
        
        # 右键菜单
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh)
        
        extract_btn = QPushButton("📦 提取")
        extract_btn.clicked.connect(self.extract_file)
        
        edit_btn = QPushButton("✏️ 编辑")
        edit_btn.clicked.connect(self.edit_file)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(extract_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addStretch()
        
        layout.addLayout(nav_layout)
        layout.addWidget(self.tree)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
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
        
        items = self.decompiler.list_directory(self.current_path)
        for item in items:
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, item['name'])
            tree_item.setText(1, self.format_size(item['size']))
            tree_item.setText(2, "文件夹" if item['is_dir'] else "文件")
            
            if item['is_dir']:
                tree_item.setIcon(0, self.style().standardIcon(10))  # 文件夹图标
            else:
                tree_item.setIcon(0, self.style().standardIcon(11))  # 文件图标
            
            tree_item.setData(0, Qt.UserRole, item['path'])
            tree_item.setData(0, Qt.UserRole + 1, item['is_dir'])
            self.tree.addTopLevelItem(tree_item)
    
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
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        pass
    
    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        
        menu = QMenu()
        
        open_action = menu.addAction("打开")
        extract_action = menu.addAction("提取")
        edit_action = menu.addAction("编辑")
        
        action = menu.exec_(self.tree.mapToGlobal(pos))
        
        if action == open_action:
            is_dir = item.data(0, Qt.UserRole + 1)
            if is_dir:
                path = item.data(0, Qt.UserRole)
                self.current_path = path
                self.refresh()
        elif action == extract_action:
            self.extract_file()
        elif action == edit_action:
            self.edit_file()
    
    def extract_file(self):
        items = self.tree.selectedItems()
        if not items:
            return
        
        item = items[0]
        path = item.data(0, Qt.UserRole)
        is_dir = item.data(0, Qt.UserRole + 1)
        
        if is_dir:
            QMessageBox.information(self, "提示", "暂不支持提取文件夹")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", os.path.basename(path), "所有文件 (*.*)"
        )
        
        if output_path:
            try:
                import shutil
                shutil.copy2(path, output_path)
                QMessageBox.information(self, "成功", "文件提取成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"提取失败：{e}")
    
    def edit_file(self):
        items = self.tree.selectedItems()
        if not items:
            return
        
        item = items[0]
        path = item.data(0, Qt.UserRole)
        is_dir = item.data(0, Qt.UserRole + 1)
        
        if is_dir:
            return
        
        self.file_selected.emit(path)
    
    def set_path(self, path: str):
        if os.path.exists(path):
            self.current_path = path
            self.refresh()


class CodeEditorWidget(QTextEdit):
    """代码编辑器组件"""
    
    def __init__(self):
        super().__init__()
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setFont(QFont("Consolas", 10))
        self.current_file = None
    
    def open_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.setPlainText(content)
            self.current_file = file_path
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
        self.editor = APKEditor()
        self.decompiler = APKDecompiler()
        self.current_apk = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("APK 反编译工具 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
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
        self.file_browser = FileBrowserWidget()
        self.file_browser.file_selected.connect(self.open_file_in_editor)
        splitter.addWidget(self.file_browser)
        
        # 右侧：代码编辑器和信息面板
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 代码编辑器标签页
        self.code_editor = CodeEditorWidget()
        self.tabs.addTab(self.code_editor, "代码编辑器")
        
        # APK 信息标签页
        self.info_widget = QTextEdit()
        self.info_widget.setReadOnly(True)
        self.tabs.addTab(self.info_widget, "APK 信息")
        
        # 日志标签页
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.tabs.addTab(self.log_widget, "日志")
        
        right_layout.addWidget(self.tabs)
        
        # 操作按钮区域
        ops_layout = QHBoxLayout()
        
        self.open_apk_btn = QPushButton("📱 打开 APK")
        self.open_apk_btn.clicked.connect(self.open_apk)
        
        self.decompile_btn = QPushButton("🔍 反编译")
        self.decompile_btn.clicked.connect(self.decompile_apk)
        
        self.java_btn = QPushButton("☕ 转 Java")
        self.java_btn.clicked.connect(self.decompile_to_java)
        
        self.compile_btn = QPushButton("📦 编译")
        self.compile_btn.clicked.connect(self.compile_apk)
        
        self.sign_btn = QPushButton("✍️ 签名")
        self.sign_btn.clicked.connect(self.sign_apk_action)
        
        self.remove_sig_btn = QPushButton("❌ 去签名")
        self.remove_sig_btn.clicked.connect(self.remove_signature_action)
        
        self.deobf_btn = QPushButton("🔓 反混淆")
        self.deobf_btn.clicked.connect(self.deobfuscate)
        
        self.analyze_btn = QPushButton("📊 分析混淆")
        self.analyze_btn.clicked.connect(self.analyze_obfuscation)
        
        ops_layout.addWidget(self.open_apk_btn)
        ops_layout.addWidget(self.decompile_btn)
        ops_layout.addWidget(self.java_btn)
        ops_layout.addWidget(self.compile_btn)
        ops_layout.addWidget(self.sign_btn)
        ops_layout.addWidget(self.remove_sig_btn)
        ops_layout.addWidget(self.deobf_btn)
        ops_layout.addWidget(self.analyze_btn)
        ops_layout.addStretch()
        
        right_layout.addLayout(ops_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
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
        self.statusBar.showMessage("就绪")
        
        self.show()
    
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
        
        decompile_action = QAction("反编译 APK", self)
        decompile_action.triggered.connect(self.decompile_apk)
        tools_menu.addAction(decompile_action)
        
        java_action = QAction("反编译为 Java", self)
        java_action.triggered.connect(self.decompile_to_java)
        tools_menu.addAction(java_action)
        
        compile_action = QAction("编译 APK", self)
        compile_action.triggered.connect(self.compile_apk)
        tools_menu.addAction(compile_action)
        
        tools_menu.addSeparator()
        
        sign_action = QAction("签名 APK", self)
        sign_action.triggered.connect(self.sign_apk_action)
        tools_menu.addAction(sign_action)
        
        remove_sign_action = QAction("去除签名", self)
        remove_sign_action.triggered.connect(self.remove_signature_action)
        tools_menu.addAction(remove_sign_action)
        
        tools_menu.addSeparator()
        
        deobf_action = QAction("反混淆", self)
        deobf_action.triggered.connect(self.deobfuscate)
        tools_menu.addAction(deobf_action)
        
        analyze_action = QAction("分析混淆", self)
        analyze_action.triggered.connect(self.analyze_obfuscation)
        tools_menu.addAction(analyze_action)
        
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
        toolbar.addAction("🔍 反编译", self.decompile_apk)
        toolbar.addAction("☕ Java", self.decompile_to_java)
        toolbar.addAction("📦 编译", self.compile_apk)
        toolbar.addAction("✍️ 签名", self.sign_apk_action)
        toolbar.addAction("❌ 去签名", self.remove_signature_action)
    
    def log(self, message: str):
        """添加日志"""
        self.log_widget.append(f"[{self.get_timestamp()}] {message}")
    
    def get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def open_apk(self):
        """打开 APK 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if file_path:
            self.current_apk = file_path
            self.statusBar.showMessage(f"已加载：{file_path}")
            self.log(f"打开 APK: {file_path}")
            
            # 显示 APK 信息
            self.show_apk_info(file_path)
            
            # 自动导航到 APK 所在目录
            self.file_browser.set_path(os.path.dirname(file_path))
    
    def show_apk_info(self, apk_path: str):
        """显示 APK 信息"""
        info = self.decompiler.get_apk_info(apk_path)
        
        info_text = f"APK 文件：{apk_path}\n"
        info_text += f"文件数量：{info.get('file_count', 0)}\n"
        info_text += f"DEX 文件：{len(info.get('dex_files', []))}\n"
        info_text += f"资源文件：{len(info.get('res_files', []))}\n\n"
        
        if info.get('dex_files'):
            info_text += "DEX 文件列表:\n"
            for dex in info['dex_files']:
                info_text += f"  - {dex}\n"
        
        self.info_widget.setText(info_text)
    
    def decompile_apk(self):
        """反编译 APK"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        output_dir = os.path.join(output_dir, os.path.basename(self.current_apk).replace('.apk', ''))
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始反编译...")
        
        self.thread = DecompilerThread(self.current_apk, output_dir, "decompile")
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_decompile_finished)
        self.thread.start()
    
    def decompile_to_java(self):
        """反编译为 Java 代码"""
        if not self.current_apk:
            QMessageBox.warning(self, "警告", "请先打开 APK 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.dirname(self.current_apk)
        )
        
        if not output_dir:
            return
        
        output_dir = os.path.join(output_dir, "java_output")
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log("开始反编译为 Java...")
        
        self.thread = DecompilerThread(self.current_apk, output_dir, "java")
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_decompile_finished)
        self.thread.start()
    
    def update_progress(self, value: int, message: str):
        self.progress.setValue(value)
        self.statusBar.showMessage(message)
        self.log(message)
    
    def on_decompile_finished(self, success: bool, result: str):
        self.progress.setVisible(False)
        if success:
            QMessageBox.information(self, "成功", f"反编译完成\n输出目录：{result}")
            self.file_browser.set_path(result)
            self.log(f"反编译成功：{result}")
        else:
            QMessageBox.critical(self, "错误", f"反编译失败：{result}")
            self.log(f"反编译失败：{result}")
    
    def compile_apk(self):
        """编译 APK"""
        project_dir = QFileDialog.getExistingDirectory(
            self, "选择项目目录", ""
        )
        
        if not project_dir:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存 APK", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if not output_path:
            return
        
        self.log(f"开始编译：{project_dir}")
        success = self.decompiler.compile_apk(project_dir, output_path)
        
        if success:
            QMessageBox.information(self, "成功", f"编译完成\n输出：{output_path}")
            self.log(f"编译成功：{output_path}")
        else:
            QMessageBox.critical(self, "错误", "编译失败")
            self.log("编译失败")
    
    def sign_apk_action(self):
        """签名 APK"""
        apk_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if not apk_path:
            return
        
        keystore_path, _ = QFileDialog.getOpenFileName(
            self, "选择密钥库", "", "密钥库文件 (*.jks *.keystore);;所有文件 (*.*)"
        )
        
        if not keystore_path:
            return
        
        # 输入密码
        keystore_password, ok = QInputDialog.getText(
            self, "密钥库密码", "请输入密钥库密码:", QLineEdit.Password
        )
        
        if not ok:
            return
        
        alias, ok = QInputDialog.getText(
            self, "别名", "请输入密钥别名:"
        )
        
        if not ok:
            return
        
        alias_password, ok = QInputDialog.getText(
            self, "密钥密码", "请输入密钥密码:", QLineEdit.Password
        )
        
        if not ok:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存签名后的 APK", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if not output_path:
            return
        
        self.log("开始签名...")
        success = self.decompiler.sign_apk(
            apk_path, keystore_path, keystore_password, 
            alias, alias_password, output_path
        )
        
        if success:
            QMessageBox.information(self, "成功", f"签名完成\n输出：{output_path}")
            self.log(f"签名成功：{output_path}")
        else:
            QMessageBox.critical(self, "错误", "签名失败")
            self.log("签名失败")
    
    def remove_signature_action(self):
        """去除 APK 签名"""
        apk_path, _ = QFileDialog.getOpenFileName(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if not apk_path:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存未签名的 APK", "", "APK 文件 (*.apk);;所有文件 (*.*)"
        )
        
        if not output_path:
            return
        
        self.log("开始去除签名...")
        success = self.decompiler.remove_signature(apk_path, output_path)
        
        if success:
            QMessageBox.information(self, "成功", f"去除签名完成\n输出：{output_path}")
            self.log(f"去除签名成功：{output_path}")
        else:
            QMessageBox.critical(self, "错误", "去除签名失败")
            self.log("去除签名失败")
    
    def deobfuscate(self):
        """反混淆"""
        project_dir = QFileDialog.getExistingDirectory(
            self, "选择项目目录", ""
        )
        
        if not project_dir:
            return
        
        self.log("开始反混淆...")
        success = self.decompiler.deobfuscate_resources(project_dir)
        
        if success:
            QMessageBox.information(self, "成功", "反混淆完成")
            self.log("反混淆成功")
            self.file_browser.refresh()
        else:
            QMessageBox.warning(self, "警告", "反混淆失败或未找到 mapping 文件")
            self.log("反混淆失败")
    
    def analyze_obfuscation(self):
        """分析混淆"""
        project_dir = QFileDialog.getExistingDirectory(
            self, "选择项目目录", ""
        )
        
        if not project_dir:
            return
        
        self.log("开始分析混淆...")
        analysis = self.decompiler.analyze_obfuscation(project_dir)
        
        if analysis:
            result = "混淆分析报告:\n\n"
            result += f"类数量：{analysis.get('class_count', 0)}\n"
            result += f"方法数量：{analysis.get('method_count', 0)}\n"
            result += f"使用反射：{'是' if analysis.get('reflection_usage') else '否'}\n"
            result += f"包含 Native 代码：{'是' if analysis.get('native_code') else '否'}\n\n"
            
            suspicious = analysis.get('suspicious_patterns', [])
            if suspicious:
                result += "可疑模式:\n"
                for pattern in suspicious:
                    result += f"  - {pattern}\n"
            
            self.info_widget.setText(result)
            self.log("混淆分析完成")
        else:
            QMessageBox.warning(self, "警告", "分析失败")
            self.log("混淆分析失败")
    
    def open_file_in_editor(self, file_path: str):
        """在编辑器中打开文件"""
        self.tabs.setCurrentIndex(0)  # 切换到编辑器标签页
        self.code_editor.open_file(file_path)
        self.log(f"打开文件：{file_path}")
    
    def save_file(self):
        """保存文件"""
        if self.code_editor.save_file():
            self.log("文件保存成功")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 APK 反编译工具",
            "APK 反编译工具 v1.0\n\n"
            "功能:\n"
            "- 查看文件目录\n"
            "- 提取 APK 包\n"
            "- 反编译 APK (smali/java)\n"
            "- 解析和修改 XML 文件\n"
            "- APK 签名与去除签名\n"
            "- 资源反混淆\n"
            "- 字符串解密与混淆对抗\n\n"
            "© 2024"
        )


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = APKDecompilerGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

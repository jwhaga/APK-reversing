"""
代码管理和编辑器组件
支持 Smali/Java 代码的增删查改操作
"""

import os
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QTreeWidget, QTreeWidgetItem, QFileDialog,
                             QLabel, QLineEdit, QComboBox, QGroupBox, QFormLayout,
                             QDialog, QDialogButtonBox, QTabWidget, QSplitter,
                             QMessageBox, QToolBar, QAction, QMenu, QInputDialog,
                             QApplication, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence, QColor

from dex_converter import (SmaliClass, SmaliMethod, SmaliEditor, 
                          JavaClass, JavaMethod, JavaEditor,
                          DexToSmaliConverter, SmaliToJavaConverter)


class CodeManagerWidget(QWidget):
    """代码管理器组件 - 支持增删查改"""
    
    code_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.smali_class = None
        self.java_class = None
        self.smali_editor = None
        self.java_editor = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：代码结构树
        structure_widget = QWidget()
        structure_layout = QVBoxLayout()
        structure_layout.setContentsMargins(0, 0, 0, 0)
        
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["结构", "类型"])
        self.structure_tree.setColumnWidth(0, 200)
        self.structure_tree.itemClicked.connect(self.on_structure_item_clicked)
        structure_layout.addWidget(self.structure_tree)
        
        structure_widget.setLayout(structure_layout)
        main_splitter.addWidget(structure_widget)
        
        # 右侧：代码编辑区
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # Smali 编辑器
        self.smali_editor_widget = QTextEdit()
        self.smali_editor_widget.setFont(QFont("Consolas", 10))
        self.smali_editor_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.tabs.addTab(self.smali_editor_widget, "Smali")
        
        # Java 编辑器
        self.java_editor_widget = QTextEdit()
        self.java_editor_widget.setFont(QFont("Consolas", 10))
        self.java_editor_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.tabs.addTab(self.java_editor_widget, "Java")
        
        editor_layout.addWidget(self.tabs)
        
        # 操作面板
        ops_group = QGroupBox("代码操作")
        ops_layout = QFormLayout()
        
        # 添加方法按钮
        self.add_method_btn = QPushButton("➕ 添加方法")
        self.add_method_btn.clicked.connect(self.add_method)
        ops_layout.addRow(self.add_method_btn)
        
        # 删除方法按钮
        self.delete_method_btn = QPushButton("➖ 删除方法")
        self.delete_method_btn.clicked.connect(self.delete_method)
        ops_layout.addRow(self.delete_method_btn)
        
        # 修改方法按钮
        self.modify_method_btn = QPushButton("✏️ 修改方法")
        self.modify_method_btn.clicked.connect(self.modify_method)
        ops_layout.addRow(self.modify_method_btn)
        
        # 注入代码按钮
        self.inject_code_btn = QPushButton("💉 注入代码")
        self.inject_code_btn.clicked.connect(self.inject_code)
        ops_layout.addRow(self.inject_code_btn)
        
        # 搜索替换按钮
        self.search_replace_btn = QPushButton("🔍 搜索替换")
        self.search_replace_btn.clicked.connect(self.search_and_replace)
        ops_layout.addRow(self.search_replace_btn)
        
        ops_group.setLayout(ops_layout)
        editor_layout.addWidget(ops_group)
        
        editor_widget.setLayout(editor_layout)
        main_splitter.addWidget(editor_widget)
        
        # 设置分割器比例
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        
        # 快捷键
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_code)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_code)
    
    def create_toolbar(self) -> QToolBar:
        """创建工具栏"""
        toolbar = QToolBar()
        
        # 打开文件
        open_action = QAction("📂 打开", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # 保存
        save_action = QAction("💾 保存", self)
        save_action.triggered.connect(self.save_code)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 转换为 Smali
        to_smali_action = QAction("📝 转 Smali", self)
        to_smali_action.triggered.connect(self.convert_to_smali)
        toolbar.addAction(to_smali_action)
        
        # 转换为 Java
        to_java_action = QAction("☕ 转 Java", self)
        to_java_action.triggered.connect(self.convert_to_java)
        toolbar.addAction(to_java_action)
        
        toolbar.addSeparator()
        
        # 刷新结构
        refresh_action = QAction("🔄 刷新结构", self)
        refresh_action.triggered.connect(self.refresh_structure)
        toolbar.addAction(refresh_action)
        
        return toolbar
    
    def open_file(self):
        """打开代码文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开代码文件", "", 
            "Smali 文件 (*.smali);;Java 文件 (*.java);;所有文件 (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """加载文件"""
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 设置编辑器内容
            self.smali_editor_widget.setPlainText(content)
            self.java_editor_widget.setPlainText(content)
            
            # 解析文件结构
            if file_path.endswith('.smali'):
                self.smali_class = SmaliClass.from_smali(content)
                self.smali_editor = SmaliEditor(self.smali_class)
                self.refresh_structure()
                
                # 转换为 Java
                self.convert_to_java()
            elif file_path.endswith('.java'):
                # Java 文件解析（简化版）
                self.java_editor_widget.setPlainText(content)
            
            self.log(f"已加载：{os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载文件失败：{e}")
    
    def refresh_structure(self):
        """刷新代码结构树"""
        self.structure_tree.clear()
        
        if not self.smali_class:
            return
        
        # 类节点
        class_item = QTreeWidgetItem()
        class_item.setText(0, f"类：{self.smali_class.name}")
        class_item.setText(1, "class")
        class_item.setIcon(0, self.style().standardIcon(24))
        self.structure_tree.addTopLevelItem(class_item)
        
        # 字段节点
        if self.smali_class.fields:
            fields_item = QTreeWidgetItem()
            fields_item.setText(0, "字段")
            fields_item.setText(1, "fields")
            fields_item.setIcon(0, self.style().standardIcon(25))
            
            for field_info in self.smali_class.fields:
                field_item = QTreeWidgetItem()
                field_item.setText(0, f"{field_info.get('name', '')}:{field_info.get('type', '')}")
                field_item.setText(1, "field")
                fields_item.addChild(field_item)
            
            class_item.addChild(fields_item)
        
        # 方法节点
        if self.smali_class.methods:
            methods_item = QTreeWidgetItem()
            methods_item.setText(0, "方法")
            methods_item.setText(1, "methods")
            methods_item.setIcon(0, self.style().standardIcon(26))
            
            for method in self.smali_class.methods:
                method_item = QTreeWidgetItem()
                method_item.setText(0, f"{method.name}({method.descriptor})")
                method_item.setText(1, "method")
                methods_item.addChild(method_item)
            
            class_item.addChild(methods_item)
        
        self.structure_tree.expandAll()
    
    def on_structure_item_clicked(self, item: QTreeWidgetItem, column: int):
        """结构树项点击事件"""
        item_type = item.text(1)
        
        if item_type == "method":
            method_name = item.text(0).split('(')[0]
            self.jump_to_method(method_name)
    
    def jump_to_method(self, method_name: str):
        """跳转到方法"""
        if not self.smali_editor:
            return
        
        content = self.smali_editor_widget.toPlainText()
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if f".method" in line and method_name in line:
                # 找到方法位置
                cursor = self.smali_editor_widget.textCursor()
                cursor.setPosition(0)
                
                # 移动到行
                for _ in range(i):
                    cursor.movePosition(cursor.NextBlock)
                
                self.smali_editor_widget.setTextCursor(cursor)
                self.smali_editor_widget.setFocus()
                break
    
    def add_method(self):
        """添加方法"""
        if not self.smali_editor:
            QMessageBox.warning(self, "警告", "请先加载 Smali 文件")
            return
        
        # 输入方法信息
        method_name, ok = QInputDialog.getText(self, "添加方法", "方法名:")
        if not ok or not method_name:
            return
        
        return_type, ok = QInputDialog.getText(self, "添加方法", "返回类型 (如 V, I, Ljava/lang/String;):")
        if not ok or not return_type:
            return
        
        params_str, ok = QInputDialog.getText(self, "添加方法", "参数类型 (如 ZBSCIJFD, 多个用空格分隔):")
        if not ok:
            return
        
        # 解析参数
        params = params_str.split() if params_str else []
        
        # 创建方法
        method = SmaliMethod(
            name=method_name,
            descriptor="".join(params),
            return_type=return_type,
            parameters=params,
            access_flags=0x9,  # public static
            registers=len(params) + 1,
            body=["return-void"]
        )
        
        # 添加到编辑器
        self.smali_editor.add_method(method)
        self.smali_editor_widget.setPlainText(self.smali_editor.to_smali())
        
        self.refresh_structure()
        self.log(f"已添加方法：{method_name}")
    
    def delete_method(self):
        """删除方法"""
        if not self.smali_editor:
            QMessageBox.warning(self, "警告", "请先加载 Smali 文件")
            return
        
        # 选择要删除的方法
        cursor = self.smali_editor_widget.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            QMessageBox.information(self, "提示", "请先在编辑器中选择要删除的方法")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除选中的方法吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从编辑器中删除（简化实现）
            cursor.removeSelectedText()
            self.smali_editor_widget.setPlainText(self.smali_editor_widget.toPlainText())
            self.log("已删除方法")
    
    def modify_method(self):
        """修改方法"""
        if not self.smali_editor:
            QMessageBox.warning(self, "警告", "请先加载 Smali 文件")
            return
        
        # 获取当前光标位置的方法
        cursor = self.smali_editor_widget.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            QMessageBox.information(self, "提示", "请先在编辑器中选择要修改的方法")
            return
        
        # 显示修改对话框
        dialog = ModifyMethodDialog(selected_text, self)
        if dialog.exec_() == QDialog.Accepted:
            new_code = dialog.get_code()
            cursor.insertText(new_code)
            self.log("已修改方法")
    
    def inject_code(self):
        """注入代码"""
        if not self.smali_editor:
            QMessageBox.warning(self, "警告", "请先加载 Smali 文件")
            return
        
        # 输入注入位置
        method_name, ok = QInputDialog.getText(self, "注入代码", "目标方法名:")
        if not ok or not method_name:
            return
        
        position, ok = QInputDialog.getItem(
            self, "注入位置", "注入位置:",
            ["方法开始", "方法结束", "在指令前", "在指令后"],
            0, False
        )
        
        # 输入注入的代码
        code, ok = QInputDialog.getMultiLineText(
            self, "注入代码", 
            "输入要注入的代码 (每行一条指令):",
            "const-string v0, \"Injected\""
        )
        
        if ok and code:
            code_lines = code.split('\n')
            
            # 确定注入位置
            pos_map = {
                "方法开始": "start",
                "方法结束": "end",
                "在指令前": "before",
                "在指令后": "after"
            }
            
            position_value = pos_map.get(position, "end")
            
            # 如果需要指定指令，询问
            pattern = None
            if position in ["在指令前", "在指令后"]:
                pattern, _ = QInputDialog.getText(self, "目标指令", "匹配指令的正则表达式:")
            
            # 注入代码
            self.smali_editor.inject_code(
                method_name, code_lines, 
                position=position_value,
                pattern=pattern
            )
            
            self.smali_editor_widget.setPlainText(self.smali_editor.to_smali())
            self.log(f"已向 {method_name} 注入代码")
    
    def search_and_replace(self):
        """搜索和替换"""
        if not self.smali_editor:
            QMessageBox.warning(self, "警告", "请先加载 Smali 文件")
            return
        
        # 显示搜索替换对话框
        dialog = SearchReplaceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pattern = dialog.get_pattern()
            replacement = dialog.get_replacement()
            
            # 执行替换
            self.smali_editor.replace_code(pattern, replacement)
            self.smali_editor_widget.setPlainText(self.smali_editor.to_smali())
            
            self.log(f"已替换：{pattern} -> {replacement}")
    
    def search_code(self):
        """搜索代码"""
        # 简单的搜索功能
        text, ok = QInputDialog.getText(self, "搜索", "搜索内容:")
        if ok and text:
            cursor = self.smali_editor_widget.textCursor()
            cursor.setPosition(0)
            
            found = self.smali_editor_widget.find(text)
            if not found:
                QMessageBox.information(self, "搜索结果", "未找到匹配内容")
    
    def convert_to_smali(self):
        """转换为 Smali"""
        if self.smali_editor:
            self.smali_editor_widget.setPlainText(self.smali_editor.to_smali())
            self.tabs.setCurrentIndex(0)
    
    def convert_to_java(self):
        """转换为 Java"""
        if self.smali_class and self.smali_editor:
            try:
                java_class = JavaClass.from_smali_class(self.smali_class)
                java_code = java_class.to_java()
                self.java_editor_widget.setPlainText(java_code)
                self.tabs.setCurrentIndex(1)
            except Exception as e:
                QMessageBox.warning(self, "转换失败", f"无法转换为 Java: {e}")
    
    def save_code(self):
        """保存代码"""
        if not self.current_file:
            # 另存为
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存代码", "", 
                "Smali 文件 (*.smali);;Java 文件 (*.java);;所有文件 (*)"
            )
            if file_path:
                self.current_file = file_path
            else:
                return
        
        try:
            # 获取当前标签页的内容
            if self.tabs.currentIndex() == 0:
                content = self.smali_editor_widget.toPlainText()
            else:
                content = self.java_editor_widget.toPlainText()
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"已保存：{os.path.basename(self.current_file)}")
            QMessageBox.information(self, "成功", "代码已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{e}")
    
    def log(self, message: str):
        """日志输出（简化版）"""
        print(f"[CodeManager] {message}")


class ModifyMethodDialog(QDialog):
    """修改方法对话框"""
    
    def __init__(self, original_code: str, parent=None):
        super().__init__(parent)
        self.original_code = original_code
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("修改方法")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # 代码编辑器
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 10))
        self.code_editor.setPlainText(self.original_code)
        layout.addWidget(self.code_editor)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_code(self) -> str:
        """获取修改后的代码"""
        return self.code_editor.toPlainText()


class SearchReplaceDialog(QDialog):
    """搜索替换对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("搜索和替换")
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        
        # 搜索
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 替换
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("替换:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # 选项
        self.regex_check = QCheckBox("使用正则表达式")
        layout.addWidget(self.regex_check)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_pattern(self) -> str:
        """获取搜索模式"""
        return self.search_input.text()
    
    def get_replacement(self) -> str:
        """获取替换内容"""
        return self.replace_input.text()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = CodeManagerWidget()
    widget.show()
    sys.exit(app.exec_())

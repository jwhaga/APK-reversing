import os
import sys
import zipfile
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
import base64
import re
import json


class APKDecompiler:
    """APK 反编译工具类"""
    
    def __init__(self, work_dir: str = None):
        self.work_dir = work_dir or os.path.join(os.getcwd(), "output")
        self.apktool_path = self._find_apktool()
        self.jadx_path = self._find_jadx()
        
    def _find_apktool(self) -> str:
        """查找 apktool"""
        paths = [
            "apktool.jar",
            os.path.join(os.path.dirname(__file__), "tools", "apktool.jar"),
            "tools\\apktool.jar"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return "apktool.jar"
    
    def _find_jadx(self) -> str:
        """查找 jadx"""
        paths = [
            "jadx",
            "jadx/bin/jadx",
            os.path.join(os.path.dirname(__file__), "tools", "jadx", "bin", "jadx")
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return "jadx"
    
    def extract_apk(self, apk_path: str, output_dir: str = None) -> bool:
        """提取 APK 文件"""
        try:
            if not os.path.exists(apk_path):
                return False
            
            output_dir = output_dir or self.work_dir
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            return True
        except Exception as e:
            print(f"提取 APK 失败：{e}")
            return False
    
    def decompile_apk(self, apk_path: str, output_dir: str = None, no_src: bool = False) -> bool:
        """反编译 APK 文件"""
        try:
            output_dir = output_dir or self.work_dir
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = ["java", "-jar", self.apktool_path, "d", apk_path, "-o", output_dir]
            if no_src:
                cmd.append("-s")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"反编译失败：{e}")
            return False
    
    def compile_apk(self, project_dir: str, output_apk: str = None) -> bool:
        """重新编译 APK"""
        try:
            output_apk = output_apk or os.path.join(self.work_dir, "output.apk")
            
            cmd = ["java", "-jar", self.apktool_path, "b", project_dir, "-o", output_apk]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"编译失败：{e}")
            return False
    
    def decompile_to_java(self, apk_path: str, output_dir: str = None) -> bool:
        """将 dex 文件反编译为 Java 代码"""
        try:
            output_dir = output_dir or os.path.join(self.work_dir, "java")
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [self.jadx_path, "-d", output_dir, apk_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Java 反编译失败：{e}")
            return False
    
    def parse_xml(self, xml_path: str) -> Dict[str, Any]:
        """解析 XML 文件"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            return self._element_to_dict(root)
        except Exception as e:
            print(f"XML 解析失败：{e}")
            return {}
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """将 XML 元素转换为字典"""
        result = {
            'tag': element.tag,
            'attribs': dict(element.attrib),
            'text': element.text.strip() if element.text else None,
            'children': []
        }
        for child in element:
            result['children'].append(self._element_to_dict(child))
        return result
    
    def sign_apk(self, apk_path: str, keystore_path: str, keystore_password: str, 
                 alias: str, alias_password: str, output_path: str = None) -> bool:
        """签名 APK 文件"""
        try:
            output_path = output_path or apk_path.replace(".apk", "_signed.apk")
            
            cmd = [
                "jarsigner", "-verbose",
                "-keystore", keystore_path,
                "-storepass", keystore_password,
                "-keypass", alias_password,
                "-sigalg", "SHA256withRSA",
                "-digestalg", "SHA-256",
                apk_path, alias
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"签名失败：{e}")
            return False
    
    def remove_signature(self, apk_path: str, output_path: str = None) -> bool:
        """去除 APK 签名"""
        try:
            output_path = output_path or apk_path.replace(".apk", "_unsigned.apk")
            
            with zipfile.ZipFile(apk_path, 'r') as zip_in:
                with zipfile.ZipFile(output_path, 'w') as zip_out:
                    for item in zip_in.infolist():
                        # 跳过签名相关文件
                        if item.filename.startswith('META-INF/'):
                            continue
                        buffer = zip_in.read(item.filename)
                        zip_out.writestr(item, buffer)
            
            return True
        except Exception as e:
            print(f"去除签名失败：{e}")
            return False
    
    def get_apk_info(self, apk_path: str) -> Dict[str, Any]:
        """获取 APK 基本信息"""
        try:
            info = {}
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                # 读取 AndroidManifest.xml
                if 'AndroidManifest.xml' in zip_ref.namelist():
                    manifest = zip_ref.read('AndroidManifest.xml')
                    info['manifest_size'] = len(manifest)
                
                # 获取文件列表
                info['files'] = zip_ref.namelist()
                info['file_count'] = len(info['files'])
                
                # 获取 dex 文件
                info['dex_files'] = [f for f in info['files'] if f.endswith('.dex')]
                
                # 获取资源文件
                info['res_files'] = [f for f in info['files'] if f.startswith('res/')]
            
            return info
        except Exception as e:
            print(f"获取 APK 信息失败：{e}")
            return {}
    
    def deobfuscate_resources(self, project_dir: str) -> bool:
        """反混淆资源文件"""
        try:
            # 查找 mapping.txt 文件
            mapping_files = []
            for root, dirs, files in os.walk(project_dir):
                if 'mapping.txt' in files:
                    mapping_files.append(os.path.join(root, 'mapping.txt'))
            
            if not mapping_files:
                print("未找到 mapping.txt 文件")
                return False
            
            # 解析 mapping 文件
            mapping = {}
            for mapping_file in mapping_files:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '->' in line:
                            parts = line.strip().split('->')
                            if len(parts) == 2:
                                original = parts[0].strip()
                                obfuscated = parts[1].strip().rstrip(':')
                                mapping[obfuscated] = original
            
            # 重命名资源文件
            res_dir = os.path.join(project_dir, 'res')
            if os.path.exists(res_dir):
                self._rename_files_with_mapping(res_dir, mapping)
            
            return True
        except Exception as e:
            print(f"反混淆失败：{e}")
            return False
    
    def _rename_files_with_mapping(self, directory: str, mapping: Dict[str, str]):
        """使用 mapping 重命名文件"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file in mapping:
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, mapping[file])
                    try:
                        os.rename(old_path, new_path)
                    except:
                        pass
    
    def decrypt_strings(self, dex_path: str, output_path: str = None) -> List[str]:
        """解密 dex 文件中的字符串"""
        try:
            strings = []
            # 这里需要实际的 dex 解析逻辑
            # 简化版本：读取文件中的可打印字符串
            with open(dex_path, 'rb') as f:
                content = f.read()
                # 查找长度大于 4 的字符串
                current_string = b''
                for byte in content:
                    if 32 <= byte <= 126:  # 可打印 ASCII 字符
                        current_string += bytes([byte])
                    else:
                        if len(current_string) >= 4:
                            try:
                                strings.append(current_string.decode('ascii'))
                            except:
                                pass
                        current_string = b''
            
            return strings
        except Exception as e:
            print(f"字符串解密失败：{e}")
            return []
    
    def analyze_obfuscation(self, project_dir: str) -> Dict[str, Any]:
        """分析混淆情况"""
        try:
            analysis = {
                'class_count': 0,
                'method_count': 0,
                'suspicious_patterns': [],
                'string_encryption': False,
                'reflection_usage': False,
                'native_code': False
            }
            
            # 分析 smali 文件
            smali_dir = os.path.join(project_dir, 'smali')
            if os.path.exists(smali_dir):
                for root, dirs, files in os.walk(smali_dir):
                    for file in files:
                        if file.endswith('.smali'):
                            analysis['class_count'] += 1
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # 检测方法
                                analysis['method_count'] += content.count('.method')
                                # 检测可疑模式
                                if 'Landroid/util/Log;' in content:
                                    analysis['suspicious_patterns'].append('日志调用')
                                if 'Runtime.getRuntime().exec' in content:
                                    analysis['suspicious_patterns'].append('命令执行')
                                if 'getDeclaredMethod' in content or 'getMethod' in content:
                                    analysis['reflection_usage'] = True
                                    analysis['suspicious_patterns'].append('反射调用')
            
            # 检测 native 代码
            if os.path.exists(os.path.join(project_dir, 'lib')):
                analysis['native_code'] = True
                analysis['suspicious_patterns'].append('包含 native 库')
            
            return analysis
        except Exception as e:
            print(f"混淆分析失败：{e}")
            return {}
    
    def modify_xml(self, xml_path: str, modifications: Dict[str, str]) -> bool:
        """修改 XML 文件"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # 应用修改
            for xpath, value in modifications.items():
                elements = root.findall(xpath)
                for elem in elements:
                    if '.' in xpath:  # 属性修改
                        attr = xpath.split('.')[-1]
                        elem.set(attr, value)
                    else:  # 文本修改
                        elem.text = value
            
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            print(f"XML 修改失败：{e}")
            return False
    
    def get_file_content(self, file_path: str) -> str:
        """获取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败：{e}")
            return ""
    
    def save_file_content(self, file_path: str, content: str) -> bool:
        """保存文件内容"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存文件失败：{e}")
            return False
    
    def list_directory(self, directory: str) -> List[Dict[str, Any]]:
        """列出目录内容"""
        try:
            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                items.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            return sorted(items, key=lambda x: (not x['is_dir'], x['name']))
        except Exception as e:
            print(f"列出目录失败：{e}")
            return []


class APKEditor:
    """APK 编辑器"""
    
    def __init__(self):
        self.decompiler = APKDecompiler()
        self.current_project = None
    
    def open_apk(self, apk_path: str, output_dir: str = None) -> bool:
        """打开 APK 文件进行编辑"""
        try:
            self.current_project = output_dir or os.path.join(
                os.path.dirname(apk_path), 
                os.path.basename(apk_path).replace('.apk', '_decompiled')
            )
            
            # 反编译 APK
            if not self.decompiler.decompile_apk(apk_path, self.current_project):
                return False
            
            return True
        except Exception as e:
            print(f"打开 APK 失败：{e}")
            return False
    
    def save_apk(self, output_path: str = None) -> bool:
        """保存修改后的 APK"""
        if not self.current_project:
            return False
        
        try:
            # 编译项目
            temp_apk = os.path.join(self.current_project, "temp.apk")
            if not self.decompiler.compile_apk(self.current_project, temp_apk):
                return False
            
            # 签名 APK
            if output_path:
                shutil.copy(temp_apk, output_path)
            
            return True
        except Exception as e:
            print(f"保存 APK 失败：{e}")
            return False
    
    def close(self):
        """关闭当前项目"""
        self.current_project = None


if __name__ == "__main__":
    # 测试代码
    decompiler = APKDecompiler()
    print("APK 反编译工具初始化完成")

import os
import sys
import zipfile
import shutil
import struct
import hashlib
import base64
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES, DES3
from Crypto.Util.Padding import unpad
import io
import json


class AXMLParser:
    """Android XML 二进制解析器"""
    
    def __init__(self):
        self.string_pool = []
        self.resource_ids = {}
        
    def parse(self, data: bytes) -> str:
        """解析二进制 XML 为文本 XML"""
        try:
            return self._parse_axml(data)
        except Exception as e:
            return f"解析失败：{e}"
    
    def _parse_axml(self, data: bytes) -> str:
        """解析 AXML 格式"""
        result = ['<?xml version="1.0" encoding="utf-8"?>\n']
        
        # 简单的 AXML 解析
        # 实际实现需要完整的 AXML 解析逻辑
        # 这里提供一个简化版本
        
        try:
            # 尝试作为普通 XML 读取
            xml_str = data.decode('utf-8', errors='ignore')
            if xml_str.strip().startswith('<?xml') or xml_str.strip().startswith('<'):
                return xml_str
        except:
            pass
        
        # 如果是二进制格式，返回提示
        if data[:4] == b'\x03\x00\x08\x00':
            return "<!-- 二进制 XML 文件，需要专门的解析器 -->\n" + data.decode('utf-8', errors='ignore')
        
        return data.decode('utf-8', errors='ignore')


class DexParser:
    """DEX 文件解析器"""
    
    def __init__(self):
        self.strings = []
        self.methods = []
        self.classes = []
        
    def parse(self, dex_data: bytes) -> Dict[str, Any]:
        """解析 DEX 文件"""
        result = {
            'strings': [],
            'methods': [],
            'classes': [],
            'header': {}
        }
        
        try:
            # 检查 DEX 魔数
            if len(dex_data) < 36 or dex_data[:8] != b'dex\n035\x00':
                # 尝试解析字符串
                result['strings'] = self._extract_strings(dex_data)
                return result
            
            # 解析 DEX 头部
            header = self._parse_header(dex_data)
            result['header'] = header
            
            # 解析字符串池
            if header.get('string_ids_off') and header.get('string_ids_size'):
                result['strings'] = self._parse_string_pool(
                    dex_data,
                    header['string_ids_off'],
                    header['string_ids_size']
                )
            
            # 解析方法
            result['methods'] = self._parse_methods(dex_data, header)
            
            # 解析类
            result['classes'] = self._parse_classes(dex_data, header)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _parse_header(self, data: bytes) -> Dict:
        """解析 DEX 头部"""
        header = {}
        
        if len(data) >= 112:
            header['magic'] = data[0:8].decode('ascii', errors='ignore')
            header['checksum'] = struct.unpack('<I', data[8:12])[0]
            header['signature'] = data[12:32].hex()
            header['file_size'] = struct.unpack('<I', data[32:36])[0]
            header['header_size'] = struct.unpack('<I', data[36:40])[0]
            header['endian_tag'] = struct.unpack('<I', data[40:44])[0]
            header['link_size'] = struct.unpack('<I', data[44:48])[0]
            header['link_off'] = struct.unpack('<I', data[48:52])[0]
            header['map_off'] = struct.unpack('<I', data[52:56])[0]
            header['string_ids_size'] = struct.unpack('<I', data[56:60])[0]
            header['string_ids_off'] = struct.unpack('<I', data[60:64])[0]
            header['type_ids_size'] = struct.unpack('<I', data[64:68])[0]
            header['type_ids_off'] = struct.unpack('<I', data[68:72])[0]
            header['proto_ids_size'] = struct.unpack('<I', data[72:76])[0]
            header['proto_ids_off'] = struct.unpack('<I', data[76:80])[0]
            header['field_ids_size'] = struct.unpack('<I', data[80:84])[0]
            header['field_ids_off'] = struct.unpack('<I', data[84:88])[0]
            header['method_ids_size'] = struct.unpack('<I', data[88:92])[0]
            header['method_ids_off'] = struct.unpack('<I', data[92:96])[0]
            header['class_defs_size'] = struct.unpack('<I', data[96:100])[0]
            header['class_defs_off'] = struct.unpack('<I', data[100:104])[0]
        
        return header
    
    def _parse_string_pool(self, data: bytes, offset: int, size: int) -> List[str]:
        """解析字符串池"""
        strings = []
        
        try:
            for i in range(size):
                str_offset = struct.unpack('<I', data[offset + i*4:offset + (i+1)*4])[0]
                if str_offset < len(data):
                    string = self._read_string(data, str_offset)
                    if string:
                        strings.append(string)
        except:
            pass
        
        return strings
    
    def _read_string(self, data: bytes, offset: int) -> str:
        """读取 MUTF-8 字符串"""
        try:
            # 读取长度
            length, skip = self._read_uleb128(data, offset)
            offset += skip
            
            # 读取字符串
            string_bytes = data[offset:offset + length]
            return string_bytes.decode('utf-8', errors='ignore')
        except:
            return ""
    
    def _read_uleb128(self, data: bytes, offset: int) -> Tuple[int, int]:
        """读取 ULEB128 编码"""
        result = 0
        shift = 0
        skip = 0
        
        for i in range(5):
            byte = data[offset + i]
            skip += 1
            result |= (byte & 0x7f) << shift
            shift += 7
            if not (byte & 0x80):
                break
        
        return result, skip
    
    def _parse_methods(self, data: bytes, header: Dict) -> List[Dict]:
        """解析方法"""
        methods = []
        
        # 简化实现
        return methods
    
    def _parse_classes(self, data: bytes, header: Dict) -> List[Dict]:
        """解析类"""
        classes = []
        
        # 简化实现
        return classes
    
    def _extract_strings(self, data: bytes) -> List[str]:
        """从数据中提取可读字符串"""
        strings = []
        current = b''
        
        for byte in data:
            if 32 <= byte <= 126:
                current += bytes([byte])
            else:
                if len(current) >= 4:
                    try:
                        strings.append(current.decode('ascii'))
                    except:
                        pass
                current = b''
        
        return strings


class APKAnalyzer:
    """APK 分析器"""
    
    def __init__(self):
        self.axml_parser = AXMLParser()
        self.dex_parser = DexParser()
    
    def analyze(self, apk_path: str) -> Dict[str, Any]:
        """分析 APK 文件"""
        result = {
            'file_info': {},
            'manifest': {},
            'dex_info': [],
            'resources': [],
            'permissions': [],
            'activities': [],
            'services': [],
            'receivers': []
        }
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                # 文件信息
                result['file_info'] = {
                    'path': apk_path,
                    'size': os.path.getsize(apk_path),
                    'files': zf.namelist(),
                    'file_count': len(zf.namelist())
                }
                
                # 解析 AndroidManifest.xml
                if 'AndroidManifest.xml' in zf.namelist():
                    manifest_data = zf.read('AndroidManifest.xml')
                    manifest_xml = self.axml_parser.parse(manifest_data)
                    result['manifest'] = self._parse_manifest_content(manifest_xml)
                    
                    # 提取权限
                    result['permissions'] = self._extract_permissions(manifest_xml)
                    
                    # 提取组件
                    result['activities'] = self._extract_components(manifest_xml, 'activity')
                    result['services'] = self._extract_components(manifest_xml, 'service')
                    result['receivers'] = self._extract_components(manifest_xml, 'receiver')
                
                # DEX 文件信息
                for name in zf.namelist():
                    if name.endswith('.dex'):
                        dex_data = zf.read(name)
                        dex_info = self.dex_parser.parse(dex_data)
                        result['dex_info'].append({
                            'name': name,
                            'size': len(dex_data),
                            'strings_count': len(dex_info.get('strings', [])),
                            'strings': dex_info.get('strings', [])[:100]  # 只取前 100 个
                        })
                
                # 资源文件
                result['resources'] = [f for f in zf.namelist() if f.startswith('res/')]
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _parse_manifest_content(self, xml_content: str) -> Dict:
        """解析清单内容"""
        info = {}
        
        try:
            # 提取包名
            package_match = re.search(r'package="([^"]+)"', xml_content)
            if package_match:
                info['package'] = package_match.group(1)
            
            # 提取版本
            version_match = re.search(r'versionName="([^"]+)"', xml_content)
            if version_match:
                info['versionName'] = version_match.group(1)
            
            # 提取应用名称
            label_match = re.search(r'label="([^"]+)"', xml_content)
            if label_match:
                info['label'] = label_match.group(1)
            
            # 提取 SDK 版本
            min_sdk = re.search(r'minSdkVersion="([^"]+)"', xml_content)
            if min_sdk:
                info['minSdkVersion'] = min_sdk.group(1)
            
            target_sdk = re.search(r'targetSdkVersion="([^"]+)"', xml_content)
            if target_sdk:
                info['targetSdkVersion'] = target_sdk.group(1)
                
        except:
            pass
        
        return info
    
    def _extract_permissions(self, xml_content: str) -> List[str]:
        """提取权限列表"""
        permissions = []
        
        matches = re.findall(r'uses-permission.*?name="([^"]+)"', xml_content)
        permissions.extend(matches)
        
        return permissions
    
    def _extract_components(self, xml_content: str, component_type: str) -> List[str]:
        """提取组件列表"""
        components = []
        
        # 简单的正则匹配
        pattern = rf'{component_type}.*?name="([^"]+)"'
        matches = re.findall(pattern, xml_content, re.IGNORECASE)
        components.extend(matches)
        
        return components


class APKModifier:
    """APK 修改器"""
    
    def __init__(self):
        pass
    
    def modify_manifest(self, apk_path: str, modifications: Dict[str, str], output_path: str) -> bool:
        """修改 AndroidManifest.xml"""
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf_in:
                # 创建临时目录
                temp_dir = os.path.join(os.path.dirname(apk_path), 'temp_extract')
                os.makedirs(temp_dir, exist_ok=True)
                
                # 提取所有文件
                zf_in.extractall(temp_dir)
                
                # 修改清单文件
                manifest_path = os.path.join(temp_dir, 'AndroidManifest.xml')
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 应用修改
                    for key, value in modifications.items():
                        pattern = rf'{key}="[^"]*"'
                        replacement = f'{key}="{value}"'
                        content = re.sub(pattern, replacement, content)
                    
                    with open(manifest_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # 重新打包
                self._zip_directory(temp_dir, output_path)
                
                # 清理临时文件
                shutil.rmtree(temp_dir)
                
                return True
        except Exception as e:
            print(f"修改失败：{e}")
            return False
    
    def _zip_directory(self, directory: str, output_path: str):
        """将目录压缩为 ZIP"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory)
                    zf.write(file_path, arcname)
    
    def add_file(self, apk_path: str, file_path: str, archive_path: str, output_path: str) -> bool:
        """添加文件到 APK"""
        try:
            shutil.copy2(apk_path, output_path)
            
            with zipfile.ZipFile(output_path, 'a') as zf:
                zf.write(file_path, archive_path)
            
            return True
        except Exception as e:
            print(f"添加文件失败：{e}")
            return False
    
    def remove_file(self, apk_path: str, archive_path: str, output_path: str) -> bool:
        """从 APK 中删除文件"""
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf_in:
                with zipfile.ZipFile(output_path, 'w') as zf_out:
                    for item in zf_in.infolist():
                        if item.filename != archive_path:
                            buffer = zf_in.read(item.filename)
                            zf_out.writestr(item, buffer)
            return True
        except Exception as e:
            print(f"删除文件失败：{e}")
            return False


class StringDecryptor:
    """字符串解密器 - 纯 Python 实现"""
    
    def __init__(self):
        pass
    
    def decrypt_base64(self, encoded: str) -> str:
        """Base64 解密"""
        try:
            decoded = base64.b64decode(encoded)
            return decoded.decode('utf-8', errors='ignore')
        except:
            return ""
    
    def decrypt_xor(self, data: bytes, key: int) -> bytes:
        """XOR 解密"""
        return bytes([b ^ key for b in data])
    
    def detect_encryption(self, content: str) -> List[Dict]:
        """检测加密模式"""
        results = []
        
        # 检测 Base64
        base64_pattern = r'[A-Za-z0-9+/=]{20,}'
        matches = re.findall(base64_pattern, content)
        for match in matches:
            try:
                decoded = base64.b64decode(match)
                if decoded.decode('utf-8', errors='ignore').isprintable():
                    results.append({
                        'type': 'Base64',
                        'original': match,
                        'decoded': decoded.decode('utf-8', errors='ignore')
                    })
            except:
                pass
        
        return results
    
    def extract_smali_strings(self, smali_content: str) -> Dict:
        """从 smali 内容提取字符串"""
        result = {
            'const_strings': [],
            'encrypted_strings': [],
            'methods': []
        }
        
        # 提取 const-string
        const_matches = re.findall(r'const-string.*?,\s*"([^"]*)"', smali_content)
        result['const_strings'] = const_matches
        
        # 检测可能的加密调用
        encrypted_patterns = [
            r'invoke-static.*?Base64\.decode',
            r'invoke-static.*?decrypt',
            r'xor-int.*?aput-char'
        ]
        
        for pattern in encrypted_patterns:
            matches = re.findall(pattern, smali_content)
            result['encrypted_strings'].extend(matches)
        
        # 提取方法名
        method_matches = re.findall(r'\.method\s+(?:public|private|protected)?\s*(\w+)\(', smali_content)
        result['methods'] = list(set(method_matches))
        
        return result


class ObfuscationAnalyzer:
    """混淆分析器 - 纯 Python 实现"""
    
    def __init__(self):
        self.string_decryptor = StringDecryptor()
    
    def analyze_project(self, project_dir: str) -> Dict[str, Any]:
        """分析项目混淆情况"""
        result = {
            'obfuscation_detected': False,
            'obfuscation_types': [],
            'severity': 'low',
            'details': {},
            'suggestions': []
        }
        
        # 分析 smali 文件
        smali_dir = os.path.join(project_dir, 'smali')
        if os.path.exists(smali_dir):
            class_stats = self._analyze_classes(smali_dir)
            result['details']['classes'] = class_stats
            
            if class_stats['obfuscated_ratio'] > 0.3:
                result['obfuscation_detected'] = True
                result['obfuscation_types'].append('类名混淆')
        
        # 计算严重程度
        score = len(result['obfuscation_types']) * 30
        if score > 80:
            result['severity'] = 'high'
        elif score > 50:
            result['severity'] = 'medium'
        
        # 生成建议
        result['suggestions'] = self._generate_suggestions(result)
        
        return result
    
    def _analyze_classes(self, smali_dir: str) -> Dict:
        """分析类名"""
        stats = {
            'total': 0,
            'obfuscated': 0,
            'obfuscated_ratio': 0.0
        }
        
        meaningless_pattern = re.compile(r'^[a-z]{1,3}$|^[a-z]\d+$')
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    stats['total'] += 1
                    class_name = os.path.basename(file).replace('.smali', '')
                    
                    if meaningless_pattern.match(class_name):
                        stats['obfuscated'] += 1
        
        if stats['total'] > 0:
            stats['obfuscated_ratio'] = stats['obfuscated'] / stats['total']
        
        return stats
    
    def _generate_suggestions(self, result: Dict) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if not result['obfuscation_detected']:
            suggestions.append("未检测到明显混淆")
            return suggestions
        
        if '类名混淆' in result['obfuscation_types']:
            suggestions.append("• 检测到类名混淆，建议通过方法调用关系推断功能")
            suggestions.append("• 关注 Android API 调用和系统服务")
        
        if result['severity'] == 'high':
            suggestions.append("• 混淆程度较高，建议使用专业工具辅助分析")
        
        return suggestions


if __name__ == "__main__":
    # 测试
    analyzer = APKAnalyzer()
    print("APK 分析器初始化完成")

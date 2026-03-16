"""
DEX 转 Smali/Java 转换器与编辑器
纯 Python 实现 - 无需外部工具
支持对生成的代码进行增删查改操作
"""

import os
import re
import struct
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class AccessFlags(Enum):
    """访问标志"""
    ACC_PUBLIC = 0x1
    ACC_PRIVATE = 0x2
    ACC_PROTECTED = 0x4
    ACC_STATIC = 0x8
    ACC_FINAL = 0x10
    ACC_SYNCHRONIZED = 0x20
    ACC_VOLATILE = 0x40
    ACC_BRIDGE = 0x40
    ACC_TRANSIENT = 0x80
    ACC_VARARGS = 0x80
    ACC_NATIVE = 0x100
    ACC_INTERFACE = 0x200
    ACC_ABSTRACT = 0x400
    ACC_STRICT = 0x800
    ACC_SYNTHETIC = 0x1000
    ACC_ANNOTATION = 0x2000
    ACC_ENUM = 0x4000


@dataclass
class SmaliMethod:
    """Smali 方法"""
    name: str
    descriptor: str
    access_flags: int = 0
    registers: int = 0
    parameters: List[str] = field(default_factory=list)
    return_type: str = "V"
    body: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    
    def to_smali(self) -> str:
        """转换为 Smali 文本"""
        lines = []
        
        # 访问标志
        access = self._access_to_string()
        
        # 方法声明
        params_str = ''.join(self.parameters)
        decl = f".method {access} {self.name}({params_str}){self.return_type}"
        lines.append(decl)
        
        # 寄存器
        if self.registers > 0:
            lines.append(f"    .registers {self.registers}")
        
        # 注解
        for annot in self.annotations:
            lines.append(f"    {annot}")
        
        # 方法体
        for line in self.body:
            if not line.startswith('    '):
                lines.append(f"    {line}")
            else:
                lines.append(line)
        
        lines.append(".end method")
        return '\n'.join(lines)
    
    def _access_to_string(self) -> str:
        """访问标志转字符串"""
        flags = []
        for flag in AccessFlags:
            if self.access_flags & flag.value:
                if flag.name.startswith('ACC_'):
                    flag_name = flag.name[4:].lower()
                    if flag_name not in ['bridge', 'synthetic', 'annotation']:
                        flags.append(flag_name)
        return ' '.join(flags) if flags else 'package-private'
    
    @classmethod
    def from_smali(cls, smali_text: str) -> 'SmaliMethod':
        """从 Smali 文本解析"""
        method = cls(name="", descriptor="")
        lines = smali_text.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 方法声明
            if line.startswith('.method'):
                match = re.search(r'\.method\s+(.*?)\s+(\S+)\((.*?)\)(\S+)', line)
                if match:
                    access_str = match.group(1)
                    method.name = match.group(2)
                    params = match.group(3)
                    method.return_type = match.group(4)
                    
                    # 解析访问标志
                    method.access_flags = cls._parse_access(access_str)
                    
                    # 解析参数
                    method.parameters = cls._parse_params(params)
            
            # 寄存器
            elif line.startswith('.registers'):
                match = re.search(r'\.registers\s+(\d+)', line)
                if match:
                    method.registers = int(match.group(1))
            
            # 方法体
            elif not line.startswith('.end method'):
                method.body.append(line)
            
            i += 1
        
        return method
    
    @staticmethod
    def _parse_access(access_str: str) -> int:
        """解析访问标志"""
        flags = 0
        access_map = {
            'public': AccessFlags.ACC_PUBLIC.value,
            'private': AccessFlags.ACC_PRIVATE.value,
            'protected': AccessFlags.ACC_PROTECTED.value,
            'static': AccessFlags.ACC_STATIC.value,
            'final': AccessFlags.ACC_FINAL.value,
            'synchronized': AccessFlags.ACC_SYNCHRONIZED.value,
            'native': AccessFlags.ACC_NATIVE.value,
            'abstract': AccessFlags.ACC_ABSTRACT.value,
        }
        
        for key, value in access_map.items():
            if key in access_str.lower():
                flags |= value
        
        return flags
    
    @staticmethod
    def _parse_params(params_str: str) -> List[str]:
        """解析参数类型"""
        params = []
        i = 0
        while i < len(params_str):
            char = params_str[i]
            if char == 'L':
                # 对象类型
                end = params_str.find(';', i)
                if end != -1:
                    params.append(params_str[i:end+1])
                    i = end + 1
                else:
                    break
            elif char == '[':
                # 数组类型
                array_dim = 0
                while i < len(params_str) and params_str[i] == '[':
                    array_dim += 1
                    i += 1
                if i < len(params_str):
                    base_type = params_str[i]
                    if base_type == 'L':
                        end = params_str.find(';', i)
                        if end != -1:
                            params.append('[' * array_dim + params_str[i:end+1])
                            i = end + 1
                    else:
                        params.append('[' * array_dim + base_type)
                        i += 1
            elif char in 'ZBSCIJFDV':
                params.append(char)
                i += 1
            else:
                i += 1
        
        return params


@dataclass
class SmaliClass:
    """Smali 类"""
    name: str
    super_class: str = "Ljava/lang/Object;"
    access_flags: int = 0
    interfaces: List[str] = field(default_factory=list)
    fields: List[Dict] = field(default_factory=list)
    methods: List[SmaliMethod] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    source_file: str = ""
    
    def to_smali(self) -> str:
        """转换为 Smali 文本"""
        lines = []
        
        # 类声明
        access = self._access_to_string()
        lines.append(f".class {access} {self.name}")
        lines.append(f".super {self.super_class}")
        
        # 接口
        for iface in self.interfaces:
            lines.append(f".implements {iface}")
        
        # 注解
        for annot in self.annotations:
            lines.append(annot)
        
        # 源文件
        if self.source_file:
            lines.append(f".source {self.source_file}")
        
        lines.append("")
        
        # 字段
        for field_info in self.fields:
            lines.append(self._field_to_smali(field_info))
        
        lines.append("")
        
        # 方法
        for method in self.methods:
            lines.append(method.to_smali())
            lines.append("")
        
        return '\n'.join(lines)
    
    def _access_to_string(self) -> str:
        """访问标志转字符串"""
        flags = []
        for flag in AccessFlags:
            if self.access_flags & flag.value:
                if flag.name.startswith('ACC_'):
                    flag_name = flag.name[4:].lower()
                    if flag_name not in ['bridge', 'synthetic', 'annotation']:
                        flags.append(flag_name)
        return ' '.join(flags) if flags else 'package-private'
    
    @staticmethod
    def _field_to_smali(field_info: Dict) -> str:
        """字段转 Smali"""
        access = field_info.get('access', 'field')
        name = field_info.get('name', '')
        type_ = field_info.get('type', '')
        value = field_info.get('value', '')
        
        line = f".field {access} {name}:{type_}"
        if value:
            line += f" = {value}"
        return line
    
    def add_method(self, method: SmaliMethod):
        """添加方法"""
        self.methods.append(method)
    
    def remove_method(self, method_name: str, descriptor: str = None):
        """删除方法"""
        self.methods = [
            m for m in self.methods 
            if not (m.name == method_name and (descriptor is None or m.descriptor == descriptor))
        ]
    
    def find_method(self, method_name: str, descriptor: str = None) -> Optional[SmaliMethod]:
        """查找方法"""
        for method in self.methods:
            if method.name == method_name:
                if descriptor is None or method.descriptor == descriptor:
                    return method
        return None
    
    def add_field(self, name: str, field_type: str, access: str = "field", value: str = ""):
        """添加字段"""
        self.fields.append({
            'name': name,
            'type': field_type,
            'access': access,
            'value': value
        })
    
    def remove_field(self, name: str):
        """删除字段"""
        self.fields = [f for f in self.fields if f['name'] != name]
    
    @classmethod
    def from_smali(cls, smali_text: str) -> 'SmaliClass':
        """从 Smali 文本解析"""
        class_obj = cls(name="")
        lines = smali_text.strip().split('\n')
        
        i = 0
        current_method_lines = []
        in_method = False
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 类声明
            if line.startswith('.class'):
                match = re.search(r'\.class\s+(.*?)\s+(\S+)', line)
                if match:
                    access_str = match.group(1)
                    class_obj.name = match.group(2)
                    class_obj.access_flags = SmaliMethod._parse_access(access_str)
            
            # 父类
            elif line.startswith('.super'):
                match = re.search(r'\.super\s+(\S+)', line)
                if match:
                    class_obj.super_class = match.group(1)
            
            # 接口
            elif line.startswith('.implements'):
                match = re.search(r'\.implements\s+(\S+)', line)
                if match:
                    class_obj.interfaces.append(match.group(1))
            
            # 源文件
            elif line.startswith('.source'):
                match = re.search(r'\.source\s+(\S+)', line)
                if match:
                    class_obj.source_file = match.group(1)
            
            # 字段
            elif line.startswith('.field'):
                field_info = cls._parse_field(line)
                class_obj.fields.append(field_info)
            
            # 方法开始
            elif line.startswith('.method'):
                in_method = True
                current_method_lines = [line]
            
            # 方法结束
            elif line.startswith('.end method'):
                current_method_lines.append(line)
                method = SmaliMethod.from_smali('\n'.join(current_method_lines))
                class_obj.methods.append(method)
                in_method = False
                current_method_lines = []
            
            # 方法体
            elif in_method:
                current_method_lines.append(line)
            
            i += 1
        
        return class_obj
    
    @staticmethod
    def _parse_field(field_line: str) -> Dict:
        """解析字段"""
        field_info = {
            'name': '',
            'type': '',
            'access': 'field',
            'value': ''
        }
        
        # 移除 .field 前缀
        content = field_line.replace('.field', '').strip()
        
        # 访问标志
        access_keywords = ['public', 'private', 'protected', 'static', 'final', 'volatile', 'transient']
        for keyword in access_keywords:
            if keyword in content.lower():
                field_info['access'] += f' {keyword}'
        
        field_info['access'] = field_info['access'].strip()
        
        # 名称和类型
        match = re.search(r'(\w+):(\S+)', content)
        if match:
            field_info['name'] = match.group(1)
            field_info['type'] = match.group(2)
        
        # 值
        if '=' in content:
            value_match = re.search(r'=\s*(\S+)', content)
            if value_match:
                field_info['value'] = value_match.group(1)
        
        return field_info


@dataclass
class JavaMethod:
    """Java 方法"""
    name: str
    return_type: str
    parameters: List[Tuple[str, str]]  # [(type, name), ...]
    access_modifiers: List[str] = field(default_factory=list)
    body: str = ""
    exceptions: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    
    def to_java(self, indent: int = 1) -> str:
        """转换为 Java 代码"""
        lines = []
        indent_str = "    " * indent
        
        # 注解
        for annot in self.annotations:
            lines.append(f"{indent_str}{annot}")
        
        # 方法声明
        access = ' '.join(self.access_modifiers) if self.access_modifiers else 'package-private'
        params = ', '.join([f"{t} {n}" for t, n in self.parameters])
        
        decl = f"{indent_str}{access} {self.return_type} {self.name}({params})"
        
        if self.exceptions:
            decl += f" throws {', '.join(self.exceptions)}"
        
        lines.append(decl)
        
        # 方法体
        if self.body:
            lines.append(f"{indent_str}{{")
            body_lines = self.body.strip().split('\n')
            for body_line in body_lines:
                if body_line.strip():
                    lines.append(f"{indent_str}    {body_line.strip()}")
            lines.append(f"{indent_str}}}")
        else:
            lines.append(f"{indent_str}{{")
            lines.append(f"{indent_str}}}")
        
        return '\n'.join(lines)
    
    @classmethod
    def from_smali(cls, smali_method: SmaliMethod) -> 'JavaMethod':
        """从 Smali 方法转换"""
        java_method = cls(
            name=smali_method.name,
            return_type=cls._descriptor_to_java_type(smali_method.return_type),
            parameters=[],
            access_modifiers=smali_method._access_to_string().split(),
            body="// TODO: Implement method body\n"
        )
        
        # 转换参数（简单版本，不处理参数名）
        for i, param_type in enumerate(smali_method.parameters):
            java_type = cls._descriptor_to_java_type(param_type)
            java_method.parameters.append((java_type, f"param{i}"))
        
        # 转换异常
        for line in smali_method.body:
            if 'catch' in line:
                match = re.search(r'catch\s+(L[^;]+;)', line)
                if match:
                    exc_type = cls._descriptor_to_java_type(match.group(1))
                    if exc_type not in java_method.exceptions:
                        java_method.exceptions.append(exc_type)
        
        return java_method
    
    @staticmethod
    def _descriptor_to_java_type(descriptor: str) -> str:
        """描述符转 Java 类型"""
        type_map = {
            'Z': 'boolean',
            'B': 'byte',
            'S': 'short',
            'C': 'char',
            'I': 'int',
            'J': 'long',
            'F': 'float',
            'D': 'double',
            'V': 'void'
        }
        
        if descriptor in type_map:
            return type_map[descriptor]
        elif descriptor.startswith('L') and descriptor.endswith(';'):
            return descriptor[1:-1].replace('/', '.')
        elif descriptor.startswith('['):
            array_dim = descriptor.count('[')
            base_type = descriptor.replace('[', '')
            java_base = JavaMethod._descriptor_to_java_type(base_type)
            return java_base + '[]' * array_dim
        
        return descriptor


@dataclass
class JavaClass:
    """Java 类"""
    name: str
    package: str = ""
    imports: List[str] = field(default_factory=list)
    access_modifiers: List[str] = field(default_factory=list)
    super_class: str = "Object"
    interfaces: List[str] = field(default_factory=list)
    fields: List[Dict] = field(default_factory=list)
    methods: List[JavaMethod] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    
    def to_java(self) -> str:
        """转换为 Java 代码"""
        lines = []
        
        # 包声明
        if self.package:
            lines.append(f"package {self.package};")
            lines.append("")
        
        # 导入
        for imp in sorted(set(self.imports)):
            lines.append(f"import {imp};")
        
        if self.imports:
            lines.append("")
        
        # 类声明
        access = ' '.join(self.access_modifiers) if self.access_modifiers else 'package-private'
        class_decl = f"{access} class {self.name.split('/')[-1]}"
        
        if self.super_class and self.super_class != "Object":
            class_decl += f" extends {self.super_class}"
        
        if self.interfaces:
            class_decl += f" implements {', '.join(self.interfaces)}"
        
        lines.append(f"public {class_decl} {{")
        lines.append("")
        
        # 字段
        for field_info in self.fields:
            lines.append(self._field_to_java(field_info))
        
        if self.fields:
            lines.append("")
        
        # 方法
        for method in self.methods:
            lines.append(method.to_java())
            lines.append("")
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def _field_to_java(field_info: Dict) -> str:
        """字段转 Java"""
        access = field_info.get('access', 'private')
        field_type = field_info.get('type', 'Object')
        name = field_info.get('name', 'field')
        value = field_info.get('value', '')
        
        line = f"    {access} {field_type} {name}"
        if value:
            line += f" = {value}"
        line += ";"
        
        return line
    
    def add_method(self, method: JavaMethod):
        """添加方法"""
        self.methods.append(method)
    
    def remove_method(self, method_name: str, param_types: List[str] = None):
        """删除方法"""
        if param_types is None:
            self.methods = [m for m in self.methods if m.name != method_name]
        else:
            def matches(m):
                if m.name != method_name:
                    return False
                m_types = [t for t, n in m.parameters]
                return m_types == param_types
            
            self.methods = [m for m in self.methods if not matches(m)]
    
    def find_method(self, method_name: str, param_types: List[str] = None) -> Optional[JavaMethod]:
        """查找方法"""
        for method in self.methods:
            if method.name == method_name:
                if param_types is None:
                    return method
                m_types = [t for t, n in method.parameters]
                if m_types == param_types:
                    return method
        return None
    
    @classmethod
    def from_smali_class(cls, smali_class: SmaliClass) -> 'JavaClass':
        """从 Smali 类转换"""
        java_class = cls(
            name=smali_class.name.replace('/', '.'),
            access_modifiers=smali_class._access_to_string().split(),
            super_class=smali_class.super_class.replace('L', '').replace(';', '').replace('/', '.'),
            interfaces=[i.replace('L', '').replace(';', '').replace('/', '.') for i in smali_class.interfaces]
        )
        
        # 转换包名
        if '.' in java_class.name:
            parts = java_class.name.rsplit('.', 1)
            java_class.package = parts[0]
            java_class.name = parts[1]
        
        # 转换字段
        for field_info in smali_class.fields:
            java_field = {
                'access': field_info.get('access', 'private'),
                'type': JavaMethod._descriptor_to_java_type(field_info.get('type', '')),
                'name': field_info.get('name', ''),
                'value': field_info.get('value', '')
            }
            java_class.fields.append(java_field)
            
            # 添加导入
            field_type = field_info.get('type', '')
            if field_type.startswith('L'):
                import_path = field_type[1:-1].replace('/', '.')
                java_class.imports.append(import_path)
        
        # 转换方法
        for smali_method in smali_class.methods:
            java_method = JavaMethod.from_smali(smali_method)
            java_class.methods.append(java_method)
            
            # 添加导入
            for param_type in smali_method.parameters:
                if param_type.startswith('L'):
                    import_path = param_type[1:-1].replace('/', '.')
                    java_class.imports.append(import_path)
            
            if smali_method.return_type.startswith('L'):
                import_path = smali_method.return_type[1:-1].replace('/', '.')
                java_class.imports.append(import_path)
        
        return java_class


class DexToSmaliConverter:
    """DEX 到 Smali 转换器"""
    
    def __init__(self):
        self.classes = []
    
    def convert_dex(self, dex_data: bytes) -> List[SmaliClass]:
        """转换 DEX 文件为 Smali 类列表"""
        smali_classes = []
        
        # 解析 DEX 头部
        if len(dex_data) < 112 or dex_data[:8] != b'dex\n035\x00':
            # 尝试作为普通数据解析
            return smali_classes
        
        # 读取头部信息
        string_ids_off = struct.unpack('<I', dex_data[60:64])[0]
        string_ids_size = struct.unpack('<I', dex_data[56:60])[0]
        type_ids_off = struct.unpack('<I', dex_data[68:72])[0]
        type_ids_size = struct.unpack('<I', dex_data[64:68])[0]
        class_defs_off = struct.unpack('<I', dex_data[100:104])[0]
        class_defs_size = struct.unpack('<I', dex_data[96:100])[0]
        
        # 读取字符串池
        strings = self._read_strings(dex_data, string_ids_off, string_ids_size)
        
        # 读取类型池
        types = self._read_types(dex_data, type_ids_off, type_ids_size, strings)
        
        # 读取类定义
        classes = self._read_classes(dex_data, class_defs_off, class_defs_size, types, strings)
        
        self.classes = classes
        return classes
    
    def _read_strings(self, dex_data: bytes, offset: int, size: int) -> List[str]:
        """读取字符串池"""
        strings = []
        
        for i in range(size):
            str_offset = struct.unpack('<I', dex_data[offset + i*4:offset + (i+1)*4])[0]
            string = self._read_string(dex_data, str_offset)
            strings.append(string)
        
        return strings
    
    def _read_string(self, dex_data: bytes, offset: int) -> str:
        """读取 MUTF-8 字符串"""
        try:
            # 读取长度
            length, skip = self._read_uleb128(dex_data, offset)
            offset += skip
            
            # 读取字符串
            string_bytes = dex_data[offset:offset + length]
            return string_bytes.decode('utf-8', errors='ignore')
        except:
            return ""
    
    def _read_uleb128(self, data: bytes, offset: int) -> Tuple[int, int]:
        """读取 ULEB128"""
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
    
    def _read_types(self, dex_data: bytes, offset: int, size: int, strings: List[str]) -> List[str]:
        """读取类型池"""
        types = []
        
        for i in range(size):
            type_idx = struct.unpack('<I', dex_data[offset + i*4:offset + (i+1)*4])[0]
            if type_idx < len(strings):
                types.append(strings[type_idx])
        
        return types
    
    def _read_classes(self, dex_data: bytes, offset: int, size: int, 
                     types: List[str], strings: List[str]) -> List[SmaliClass]:
        """读取类定义"""
        classes = []
        
        for i in range(size):
            class_offset = offset + i * 32
            
            class_idx = struct.unpack('<I', dex_data[class_offset:class_offset+4])[0]
            access_flags = struct.unpack('<I', dex_data[class_offset+4:class_offset+8])[0]
            super_class_idx = struct.unpack('<I', dex_data[class_offset+8:class_offset+12])[0]
            methods_off = struct.unpack('<I', dex_data[class_offset+20:class_offset+24])[0]
            methods_size = struct.unpack('<I', dex_data[class_offset+24:class_offset+28])[0]
            
            # 创建 Smali 类
            smali_class = SmaliClass(
                name=types[class_idx] if class_idx < len(types) else f"Unknown{i}",
                access_flags=access_flags,
            )
            
            # 父类
            if super_class_idx < len(types):
                smali_class.super_class = types[super_class_idx]
            
            # 读取方法
            if methods_size > 0 and methods_off > 0:
                methods = self._read_methods(dex_data, methods_off, methods_size, strings)
                smali_class.methods = methods
            
            classes.append(smali_class)
        
        return classes
    
    def _read_methods(self, dex_data: bytes, offset: int, size: int, strings: List[str]) -> List[SmaliMethod]:
        """读取方法定义（简化版）"""
        methods = []
        
        # 这里实现完整的方法解析逻辑
        # 由于 DEX 格式复杂，这里提供简化版本
        
        return methods
    
    def convert_file(self, dex_file_path: str, output_dir: str) -> bool:
        """
        转换 DEX 文件为 Smali
        
        Args:
            dex_file_path: DEX 文件路径
            output_dir: 输出目录
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 读取 DEX 文件
            with open(dex_file_path, 'rb') as f:
                dex_data = f.read()
            
            # 转换 DEX
            self.classes = self.convert_dex(dex_data)
            
            # 保存 Smali 文件
            self.save_smali_files(output_dir)
            
            # 同时生成 Java 文件（可选）
            java_output_dir = os.path.join(output_dir, 'java')
            os.makedirs(java_output_dir, exist_ok=True)
            self.save_java_files(java_output_dir)
            
            return True
            
        except Exception as e:
            print(f"转换失败：{str(e)}")
            return False
    
    def save_smali_files(self, output_dir: str):
        """保存 Smali 文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        for smali_class in self.classes:
            # 创建目录结构
            class_name = smali_class.name.replace('L', '').replace(';', '')
            file_path = class_name.replace('/', os.sep) + '.smali'
            full_path = os.path.join(output_dir, file_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 保存文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(smali_class.to_smali())
    
    def save_java_files(self, output_dir: str):
        """保存 Java 文件"""
        if not self.classes:
            return
        
        # 转换为 Java
        java_converter = SmaliToJavaConverter()
        java_classes = java_converter.convert(self.classes)
        
        os.makedirs(output_dir, exist_ok=True)
        
        for java_class in java_classes:
            # 创建目录结构
            class_name = java_class.name.replace('L', '').replace(';', '')
            file_path = class_name.replace('/', os.sep) + '.java'
            full_path = os.path.join(output_dir, file_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 保存文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(java_class.to_java())


class SmaliToJavaConverter:
    """Smali 到 Java 转换器"""
    
    def __init__(self):
        self.java_classes = []
    
    def convert(self, smali_classes: List[SmaliClass]) -> List[JavaClass]:
        """转换 Smali 类为 Java 类"""
        java_classes = []
        
        for smali_class in smali_classes:
            java_class = JavaClass.from_smali_class(smali_class)
            java_classes.append(java_class)
        
        self.java_classes = java_classes
        return java_classes
    
    def save_java_files(self, output_dir: str):
        """保存 Java 文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        for java_class in self.java_classes:
            # 创建目录结构
            package = java_class.package.replace('.', os.sep)
            if package:
                class_dir = os.path.join(output_dir, package)
            else:
                class_dir = output_dir
            
            os.makedirs(class_dir, exist_ok=True)
            
            file_path = os.path.join(class_dir, f"{java_class.name}.java")
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(java_class.to_java())


class SmaliEditor:
    """Smali 代码编辑器 - 支持增删查改"""
    
    def __init__(self, smali_class: SmaliClass):
        self.smali_class = smali_class
    
    # ========== 查询操作 ==========
    
    def find_methods(self, name_pattern: str = None, access_filter: int = None) -> List[SmaliMethod]:
        """查找方法"""
        results = []
        
        for method in self.smali_class.methods:
            # 名称匹配
            if name_pattern and not re.search(name_pattern, method.name):
                continue
            
            # 访问标志过滤
            if access_filter and not (method.access_flags & access_filter):
                continue
            
            results.append(method)
        
        return results
    
    def find_method_by_name(self, name: str, descriptor: str = None) -> Optional[SmaliMethod]:
        """按名称查找方法"""
        return self.smali_class.find_method(name, descriptor)
    
    def search_in_body(self, pattern: str) -> List[Tuple[SmaliMethod, List[int]]]:
        """在方法体中搜索"""
        results = []
        
        for method in self.smali_class.methods:
            line_numbers = []
            for i, line in enumerate(method.body):
                if re.search(pattern, line):
                    line_numbers.append(i)
            
            if line_numbers:
                results.append((method, line_numbers))
        
        return results
    
    # ========== 添加操作 ==========
    
    def add_method(self, method: SmaliMethod):
        """添加方法"""
        self.smali_class.add_method(method)
    
    def add_simple_method(self, name: str, return_type: str, 
                         params: List[str] = None, body: List[str] = None,
                         access: str = "public static"):
        """添加简单方法"""
        method = SmaliMethod(
            name=name,
            descriptor="".join(params) if params else "",
            return_type=return_type,
            parameters=params or [],
            access_flags=SmaliMethod._parse_access(access),
            registers=len(params) + 1 if params else 1,
            body=body or ["return-void"]
        )
        self.add_method(method)
    
    def add_field(self, name: str, field_type: str, access: str = "public static", value: str = ""):
        """添加字段"""
        self.smali_class.add_field(name, field_type, access, value)
    
    # ========== 删除操作 ==========
    
    def remove_method(self, name: str, descriptor: str = None):
        """删除方法"""
        self.smali_class.remove_method(name, descriptor)
    
    def remove_methods_by_pattern(self, name_pattern: str):
        """按名称模式删除方法"""
        methods_to_remove = self.find_methods(name_pattern)
        for method in methods_to_remove:
            self.remove_method(method.name, method.descriptor)
    
    def remove_field(self, name: str):
        """删除字段"""
        self.smali_class.remove_field(name)
    
    # ========== 修改操作 ==========
    
    def modify_method_body(self, method_name: str, new_body: List[str], descriptor: str = None):
        """修改方法体"""
        method = self.find_method_by_name(method_name, descriptor)
        if method:
            method.body = new_body
    
    def modify_method_access(self, method_name: str, new_access: str, descriptor: str = None):
        """修改方法访问标志"""
        method = self.find_method_by_name(method_name, descriptor)
        if method:
            method.access_flags = SmaliMethod._parse_access(new_access)
    
    def modify_method_registers(self, method_name: str, registers: int, descriptor: str = None):
        """修改寄存器数量"""
        method = self.find_method_by_name(method_name, descriptor)
        if method:
            method.registers = registers
    
    def inject_code(self, method_name: str, code_lines: List[str], 
                   position: str = "start", pattern: str = None, descriptor: str = None):
        """注入代码"""
        method = self.find_method_by_name(method_name, descriptor)
        if not method:
            return
        
        if position == "start":
            method.body = code_lines + method.body
        elif position == "end":
            method.body.extend(code_lines)
        elif position == "before" and pattern:
            new_body = []
            for line in method.body:
                if re.search(pattern, line):
                    new_body.extend(code_lines)
                new_body.append(line)
            method.body = new_body
        elif position == "after" and pattern:
            new_body = []
            for line in method.body:
                new_body.append(line)
                if re.search(pattern, line):
                    new_body.extend(code_lines)
            method.body = new_body
    
    def replace_code(self, old_pattern: str, new_code: str, method_name: str = None):
        """替换代码"""
        if method_name:
            method = self.find_method_by_name(method_name)
            if method:
                new_body = []
                for line in method.body:
                    new_body.append(re.sub(old_pattern, new_code, line))
                method.body = new_body
        else:
            # 替换所有方法中的代码
            for method in self.smali_class.methods:
                new_body = []
                for line in method.body:
                    new_body.append(re.sub(old_pattern, new_code, line))
                method.body = new_body
    
    def remove_code(self, pattern: str, method_name: str = None):
        """删除代码"""
        self.replace_code(pattern, "", method_name)
    
    # ========== 导出操作 ==========
    
    def to_smali(self) -> str:
        """导出为 Smali 文本"""
        return self.smali_class.to_smali()
    
    def save(self, file_path: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_smali())


class JavaEditor:
    """Java 代码编辑器 - 支持增删查改"""
    
    def __init__(self, java_class: JavaClass):
        self.java_class = java_class
    
    # ========== 查询操作 ==========
    
    def find_methods(self, name_pattern: str = None, return_type: str = None) -> List[JavaMethod]:
        """查找方法"""
        results = []
        
        for method in self.java_class.methods:
            if name_pattern and not re.search(name_pattern, method.name):
                continue
            if return_type and method.return_type != return_type:
                continue
            results.append(method)
        
        return results
    
    def find_method_by_signature(self, name: str, param_types: List[str] = None) -> Optional[JavaMethod]:
        """按签名查找方法"""
        return self.java_class.find_method(name, param_types)
    
    def search_in_body(self, pattern: str) -> List[Tuple[JavaMethod, List[str]]]:
        """在方法体中搜索"""
        results = []
        
        for method in self.java_class.methods:
            matches = []
            for line in method.body.split('\n'):
                if re.search(pattern, line):
                    matches.append(line)
            
            if matches:
                results.append((method, matches))
        
        return results
    
    # ========== 添加操作 ==========
    
    def add_method(self, method: JavaMethod):
        """添加方法"""
        self.java_class.add_method(method)
    
    def add_simple_method(self, name: str, return_type: str = "void",
                         params: List[Tuple[str, str]] = None, 
                         body: str = "", access: List[str] = None):
        """添加简单方法"""
        method = JavaMethod(
            name=name,
            return_type=return_type,
            parameters=params or [],
            access_modifiers=access or ["public"],
            body=body
        )
        self.add_method(method)
    
    def add_field(self, name: str, field_type: str, access: str = "private", value: str = ""):
        """添加字段"""
        self.java_class.fields.append({
            'name': name,
            'type': field_type,
            'access': access,
            'value': value
        })
    
    def add_import(self, import_path: str):
        """添加导入"""
        if import_path not in self.java_class.imports:
            self.java_class.imports.append(import_path)
    
    # ========== 删除操作 ==========
    
    def remove_method(self, name: str, param_types: List[str] = None):
        """删除方法"""
        self.java_class.remove_method(name, param_types)
    
    def remove_methods_by_pattern(self, name_pattern: str):
        """按名称模式删除方法"""
        methods_to_remove = self.find_methods(name_pattern)
        for method in methods_to_remove:
            self.remove_method(method.name)
    
    def remove_field(self, name: str):
        """删除字段"""
        self.java_class.fields = [f for f in self.java_class.fields if f['name'] != name]
    
    # ========== 修改操作 ==========
    
    def modify_method_body(self, method_name: str, new_body: str, param_types: List[str] = None):
        """修改方法体"""
        method = self.find_method_by_signature(method_name, param_types)
        if method:
            method.body = new_body
    
    def modify_method_access(self, method_name: str, new_access: List[str], 
                            param_types: List[str] = None):
        """修改方法访问标志"""
        method = self.find_method_by_signature(method_name, param_types)
        if method:
            method.access_modifiers = new_access
    
    def inject_code(self, method_name: str, code_lines: str, 
                   position: str = "start", pattern: str = None,
                   param_types: List[str] = None):
        """注入代码"""
        method = self.find_method_by_signature(method_name, param_types)
        if not method:
            return
        
        body_lines = method.body.split('\n')
        
        if position == "start":
            body_lines = code_lines.split('\n') + body_lines
        elif position == "end":
            body_lines.extend(code_lines.split('\n'))
        elif position == "before" and pattern:
            new_body = []
            for line in body_lines:
                if re.search(pattern, line):
                    new_body.extend(code_lines.split('\n'))
                new_body.append(line)
            body_lines = new_body
        elif position == "after" and pattern:
            new_body = []
            for line in body_lines:
                new_body.append(line)
                if re.search(pattern, line):
                    new_body.extend(code_lines.split('\n'))
            body_lines = new_body
        
        method.body = '\n'.join(body_lines)
    
    def replace_code(self, old_pattern: str, new_code: str, method_name: str = None):
        """替换代码"""
        if method_name:
            method = self.find_method_by_signature(method_name)
            if method:
                method.body = re.sub(old_pattern, new_code, method.body)
        else:
            # 替换所有方法中的代码
            for method in self.java_class.methods:
                method.body = re.sub(old_pattern, new_code, method.body)
    
    # ========== 导出操作 ==========
    
    def to_java(self) -> str:
        """导出为 Java 文本"""
        return self.java_class.to_java()
    
    def save(self, file_path: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_java())


if __name__ == "__main__":
    # 测试
    print("DEX 转 Smali/Java 转换器已就绪")
    
    # 创建测试 Smali 类
    test_class = SmaliClass(
        name="Lcom/example/Test;",
        super_class="Ljava/lang/Object;",
        access_flags=AccessFlags.ACC_PUBLIC.value
    )
    
    # 添加方法
    method = SmaliMethod(
        name="main",
        descriptor="([Ljava/lang/String;)V",
        return_type="V",
        parameters=["[Ljava/lang/String;"],
        access_flags=AccessFlags.ACC_PUBLIC.value | AccessFlags.ACC_STATIC.value,
        registers=1,
        body=[
            "const-string v0, \"Hello World\"",
            "sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;",
            "invoke-virtual {v1, v0}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V",
            "return-void"
        ]
    )
    test_class.add_method(method)
    
    # 转换为 Smali
    print("\n=== Smali 输出 ===")
    print(test_class.to_smali())
    
    # 转换为 Java
    print("\n=== Java 输出 ===")
    java_class = JavaClass.from_smali_class(test_class)
    print(java_class.to_java())
    
    # 测试编辑器
    print("\n=== 测试编辑器 ===")
    editor = SmaliEditor(test_class)
    
    # 查找方法
    methods = editor.find_methods()
    print(f"找到 {len(methods)} 个方法")
    
    # 注入代码
    editor.inject_code("main", [
        "const-string v0, \"Injected code\"",
        "sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;",
        "invoke-virtual {v1, v0}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V"
    ], position="start")
    
    print("\n=== 注入后的 Smali ===")
    print(editor.to_smali())

"""
高级反混淆和字符串解密模块
"""
import os
import re
import base64
import zipfile
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class StringDecryptor:
    """字符串解密器"""
    
    def __init__(self):
        self.encrypted_strings = []
        self.decrypted_strings = []
    
    def find_encrypted_strings(self, smali_dir: str) -> List[Dict]:
        """在 smali 文件中查找加密的字符串"""
        encrypted = []
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    results = self._analyze_smali_file(file_path)
                    encrypted.extend(results)
        
        return encrypted
    
    def _analyze_smali_file(self, file_path: str) -> List[Dict]:
        """分析单个 smali 文件"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # 查找常见的加密模式
                patterns = [
                    # Base64 解码
                    r'invoke-static.*?Landroid/util/Base64;->decode\((.*?)\)I?',
                    # 字符串解密函数调用
                    r'invoke-static.*?->decrypt\(.*?Ljava/lang/String;',
                    # XOR 解密
                    r'xor-int.*?/aput-char',
                    # 字符数组构造
                    r'new-array.*?\[C.*?aput'
                ]
                
                for i, line in enumerate(lines):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            results.append({
                                'file': file_path,
                                'line': i + 1,
                                'content': line.strip(),
                                'pattern': pattern
                            })
        except Exception as e:
            pass
        
        return results
    
    def decrypt_base64_strings(self, smali_dir: str) -> List[str]:
        """尝试解密 Base64 编码的字符串"""
        decrypted = []
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    strings = self._extract_base64_from_smali(file_path)
                    for b64_str in strings:
                        try:
                            decoded = base64.b64decode(b64_str).decode('utf-8')
                            if decoded.isprintable():
                                decrypted.append(decoded)
                        except:
                            pass
        
        return decrypted
    
    def _extract_base64_from_smali(self, file_path: str) -> List[str]:
        """从 smali 文件中提取 Base64 字符串"""
        base64_strings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # 匹配 const-string 指令中的 Base64 字符串
                pattern = r'const-string.*?,\s*"([A-Za-z0-9+/=]{20,})"'
                matches = re.findall(pattern, content)
                base64_strings.extend(matches)
        except:
            pass
        
        return base64_strings
    
    def find_string_decryption_methods(self, smali_dir: str) -> List[Dict]:
        """查找字符串解密方法"""
        decryption_methods = []
        
        # 常见的解密方法名
        decrypt_method_names = [
            'decrypt', 'decryptString', 'decode', 'decodeString',
            'unobfuscate', 'getString', 'decryptValue'
        ]
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for method_name in decrypt_method_names:
                                pattern = f'\.method.*?{method_name}.*?\('
                                if re.search(pattern, content, re.IGNORECASE):
                                    decryption_methods.append({
                                        'file': file_path,
                                        'method': method_name,
                                        'class': os.path.basename(file_path).replace('.smali', '')
                                    })
                    except:
                        pass
        
        return decryption_methods


class ObfuscationAnalyzer:
    """混淆分析器"""
    
    def __init__(self):
        self.analysis_result = {}
    
    def analyze(self, project_dir: str) -> Dict:
        """分析项目的混淆情况"""
        result = {
            'obfuscation_detected': False,
            'obfuscation_type': [],
            'severity': 'low',
            'details': {}
        }
        
        smali_dir = os.path.join(project_dir, 'smali')
        if not os.path.exists(smali_dir):
            return result
        
        # 分析类名
        class_analysis = self._analyze_class_names(smali_dir)
        result['details']['class_names'] = class_analysis
        
        # 分析方法名
        method_analysis = self._analyze_method_names(smali_dir)
        result['details']['method_names'] = method_analysis
        
        # 分析字符串
        string_analysis = self._analyze_strings(smali_dir)
        result['details']['strings'] = string_analysis
        
        # 分析控制流
        control_flow_analysis = self._analyze_control_flow(smali_dir)
        result['details']['control_flow'] = control_flow_analysis
        
        # 判断混淆类型
        if class_analysis['obfuscated']:
            result['obfuscation_detected'] = True
            result['obfuscation_type'].append('类名混淆')
        
        if method_analysis['obfuscated']:
            result['obfuscation_detected'] = True
            result['obfuscation_type'].append('方法名混淆')
        
        if string_analysis['encrypted']:
            result['obfuscation_detected'] = True
            result['obfuscation_type'].append('字符串加密')
        
        if control_flow_analysis['obfuscated']:
            result['obfuscation_type'].append('控制流混淆')
        
        # 计算严重程度
        score = sum([
            class_analysis['score'],
            method_analysis['score'],
            string_analysis['score'] * 2,
            control_flow_analysis['score']
        ])
        
        if score > 80:
            result['severity'] = 'high'
        elif score > 50:
            result['severity'] = 'medium'
        
        self.analysis_result = result
        return result
    
    def _analyze_class_names(self, smali_dir: str) -> Dict:
        """分析类名"""
        stats = {
            'total': 0,
            'obfuscated': 0,
            'score': 0,
            'obfuscated': False
        }
        
        # 无意义的类名模式
        meaningless_pattern = re.compile(r'^[a-z]{1,3}$|^[a-z]\d+$')
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    stats['total'] += 1
                    class_name = os.path.basename(file).replace('.smali', '')
                    
                    if meaningless_pattern.match(class_name):
                        stats['obfuscated'] += 1
        
        if stats['total'] > 0:
            ratio = stats['obfuscated'] / stats['total']
            stats['score'] = int(ratio * 100)
            stats['obfuscated'] = ratio > 0.3
        
        return stats
    
    def _analyze_method_names(self, smali_dir: str) -> Dict:
        """分析方法名"""
        stats = {
            'total': 0,
            'obfuscated': 0,
            'score': 0,
            'obfuscated': False
        }
        
        # 无意义的方法名模式
        meaningless_pattern = re.compile(r'^[a-z]{1,3}\d*$|^[a-z]\d+$')
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # 查找方法定义
                            method_pattern = r'\.method\s+(?:public|private|protected)?\s*(\w+)\('
                            matches = re.findall(method_pattern, content)
                            
                            for method_name in matches:
                                stats['total'] += 1
                                if meaningless_pattern.match(method_name):
                                    stats['obfuscated'] += 1
                    except:
                        pass
        
        if stats['total'] > 0:
            ratio = stats['obfuscated'] / stats['total']
            stats['score'] = int(ratio * 100)
            stats['obfuscated'] = ratio > 0.5
        
        return stats
    
    def _analyze_strings(self, smali_dir: str) -> Dict:
        """分析字符串"""
        stats = {
            'total': 0,
            'encrypted': 0,
            'score': 0,
            'encrypted': False
        }
        
        # 查找字符串解密特征
        decrypt_patterns = [
            'Base64.decode',
            'Cipher.doFinal',
            'SecretKeySpec',
            'IvParameterSpec'
        ]
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            stats['total'] += content.count('const-string')
                            
                            for pattern in decrypt_patterns:
                                if pattern in content:
                                    stats['encrypted'] += 1
                    except:
                        pass
        
        if stats['total'] > 0:
            ratio = min(stats['encrypted'] / 10, 1.0)  # 每 10 个解密特征算 10%
            stats['score'] = int(ratio * 100)
            stats['encrypted'] = stats['encrypted'] > 5
        
        return stats
    
    def _analyze_control_flow(self, smali_dir: str) -> Dict:
        """分析控制流"""
        stats = {
            'total_methods': 0,
            'complex_methods': 0,
            'score': 0,
            'obfuscated': False
        }
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            methods = re.findall(r'\.method.*?\.end method', content, re.DOTALL)
                            
                            for method in methods:
                                stats['total_methods'] += 1
                                
                                # 计算跳转指令数量
                                goto_count = len(re.findall(r'goto|if-', method))
                                label_count = len(re.findall(r':label\d+|:\d+', method))
                                
                                # 如果跳转指令过多，可能是控制流混淆
                                if goto_count > 20 or label_count > 30:
                                    stats['complex_methods'] += 1
                    except:
                        pass
        
        if stats['total_methods'] > 0:
            ratio = stats['complex_methods'] / stats['total_methods']
            stats['score'] = int(ratio * 100)
            stats['obfuscated'] = ratio > 0.3
        
        return stats


class AntiAntiObfuscation:
    """反混淆对抗工具"""
    
    def __init__(self):
        self.string_decryptor = StringDecryptor()
        self.analyzer = ObfuscationAnalyzer()
    
    def process(self, project_dir: str) -> Dict:
        """处理混淆的 APK"""
        result = {
            'analysis': None,
            'decrypted_strings': [],
            'decryption_methods': [],
            'suggestions': []
        }
        
        # 分析混淆
        result['analysis'] = self.analyzer.analyze(project_dir)
        
        # 解密字符串
        smali_dir = os.path.join(project_dir, 'smali')
        if os.path.exists(smali_dir):
            result['decrypted_strings'] = self.string_decryptor.decrypt_base64_strings(smali_dir)
            result['decryption_methods'] = self.string_decryptor.find_string_decryption_methods(smali_dir)
        
        # 生成建议
        result['suggestions'] = self._generate_suggestions(result['analysis'])
        
        return result
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成反混淆建议"""
        suggestions = []
        
        if not analysis.get('obfuscation_detected'):
            suggestions.append("未检测到明显的混淆，可以直接分析")
            return suggestions
        
        obf_types = analysis.get('obfuscation_type', [])
        
        if '字符串加密' in obf_types:
            suggestions.append("检测到字符串加密，建议:")
            suggestions.append("  1. 查找 Base64.decode 调用")
            suggestions.append("  2. 定位字符串解密方法")
            suggestions.append("  3. 编写脚本批量解密")
        
        if '类名混淆' in obf_types or '方法名混淆' in obf_types:
            suggestions.append("检测到名称混淆，建议:")
            suggestions.append("  1. 查看是否有 mapping.txt 文件")
            suggestions.append("  2. 通过方法调用关系推断功能")
            suggestions.append("  3. 关注 Android API 调用")
        
        if '控制流混淆' in obf_types:
            suggestions.append("检测到控制流混淆，建议:")
            suggestions.append("  1. 使用 IDA Pro 或 Ghidra 分析")
            suggestions.append("  2. 简化控制流图")
            suggestions.append("  3. 关注关键逻辑分支")
        
        severity = analysis.get('severity', 'low')
        if severity == 'high':
            suggestions.append("\n警告：混淆程度较高，可能需要专业工具辅助分析")
        elif severity == 'medium':
            suggestions.append("\n提示：存在中等程度混淆，需要耐心分析")
        
        return suggestions
    
    def export_report(self, project_dir: str, output_path: str):
        """导出分析报告"""
        result = self.process(project_dir)
        
        report = "=" * 60 + "\n"
        report += "APK 反混淆分析报告\n"
        report += "=" * 60 + "\n\n"
        
        # 分析结果
        analysis = result['analysis']
        report += "【混淆分析】\n"
        report += f"是否混淆：{'是' if analysis.get('obfuscation_detected') else '否'}\n"
        report += f"混淆类型：{', '.join(analysis.get('obfuscation_type', ['无']))}\n"
        report += f"严重程度：{analysis.get('severity', 'unknown')}\n\n"
        
        # 详细信息
        details = analysis.get('details', {})
        if 'class_names' in details:
            stats = details['class_names']
            report += f"【类名统计】\n"
            report += f"  总数：{stats.get('total', 0)}\n"
            report += f"  混淆数：{stats.get('obfuscated', 0)}\n\n"
        
        if 'method_names' in details:
            stats = details['method_names']
            report += f"【方法名统计】\n"
            report += f"  总数：{stats.get('total', 0)}\n"
            report += f"  混淆数：{stats.get('obfuscated', 0)}\n\n"
        
        # 解密的字符串
        decrypted = result['decrypted_strings']
        if decrypted:
            report += f"【解密的字符串】(共{len(decrypted)}条)\n"
            for i, s in enumerate(decrypted[:20], 1):  # 只显示前 20 条
                report += f"  {i}. {s}\n"
            if len(decrypted) > 20:
                report += f"  ... 还有 {len(decrypted) - 20} 条\n"
            report += "\n"
        
        # 建议
        report += "【分析建议】\n"
        for suggestion in result['suggestions']:
            report += f"{suggestion}\n"
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


if __name__ == "__main__":
    # 测试
    analyzer = AntiAntiObfuscation()
    print("反混淆对抗工具初始化完成")

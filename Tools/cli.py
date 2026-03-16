#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 反编译工具 - 命令行版本
支持批量处理和自动化操作
"""

import os
import sys
import argparse
import json
from pathlib import Path
from apk_tool import APKDecompiler, APKEditor
from advanced_tools import AntiAntiObfuscation, StringDecryptor, ObfuscationAnalyzer


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print(" " * 18 + "APK 反编译工具")
    print(" " * 20 + "v1.0")
    print("=" * 60)
    print()


def cmd_decompile(args):
    """反编译 APK"""
    print(f"[*] 开始反编译：{args.input}")
    
    decompiler = APKDecompiler()
    output_dir = args.output or os.path.join(
        os.path.dirname(args.input),
        Path(args.input).stem
    )
    
    if args.java:
        print("[*] 模式：反编译为 Java 代码")
        success = decompiler.decompile_to_java(args.input, output_dir)
    else:
        print("[*] 模式：反编译为 Smali 代码")
        success = decompiler.decompile_apk(args.input, output_dir, args.no_src)
    
    if success:
        print(f"[+] 反编译完成：{output_dir}")
    else:
        print("[-] 反编译失败")
        sys.exit(1)


def cmd_compile(args):
    """编译 APK"""
    print(f"[*] 开始编译：{args.input}")
    
    decompiler = APKDecompiler()
    output = args.output or os.path.join(
        os.path.dirname(args.input),
        "output.apk"
    )
    
    success = decompiler.compile_apk(args.input, output)
    
    if success:
        print(f"[+] 编译完成：{output}")
    else:
        print("[-] 编译失败")
        sys.exit(1)


def cmd_extract(args):
    """提取 APK"""
    print(f"[*] 开始提取：{args.input}")
    
    decompiler = APKDecompiler()
    output_dir = args.output or os.path.join(
        os.path.dirname(args.input),
        Path(args.input).stem + "_extracted"
    )
    
    success = decompiler.extract_apk(args.input, output_dir)
    
    if success:
        print(f"[+] 提取完成：{output_dir}")
        # 显示文件列表
        files = decompiler.list_directory(output_dir)
        print(f"[*] 共 {len(files)} 个文件/目录")
    else:
        print("[-] 提取失败")
        sys.exit(1)


def cmd_info(args):
    """显示 APK 信息"""
    print(f"[*] 分析 APK: {args.input}")
    
    decompiler = APKDecompiler()
    info = decompiler.get_apk_info(args.input)
    
    if not info:
        print("[-] 无法获取 APK 信息")
        sys.exit(1)
    
    print("\n[APK 信息]")
    print(f"文件数量：{info.get('file_count', 0)}")
    print(f"DEX 文件：{len(info.get('dex_files', []))}")
    print(f"资源文件：{len(info.get('res_files', []))}")
    
    if info.get('dex_files'):
        print("\n[DEX 文件列表]")
        for dex in info['dex_files']:
            print(f"  - {dex}")
    
    if args.verbose:
        print("\n[所有文件]")
        for file in info.get('files', [])[:50]:  # 只显示前 50 个
            print(f"  {file}")
        if len(info.get('files', [])) > 50:
            print(f"  ... 还有 {len(info['files']) - 50} 个文件")


def cmd_sign(args):
    """签名 APK"""
    print(f"[*] 开始签名：{args.input}")
    
    decompiler = APKDecompiler()
    output = args.output or args.input.replace(".apk", "_signed.apk")
    
    # 获取密码
    import getpass
    keystore_password = getpass.getpass("密钥库密码：")
    alias_password = getpass.getpass("密钥密码：")
    
    success = decompiler.sign_apk(
        args.input,
        args.keystore,
        keystore_password,
        args.alias,
        alias_password,
        output
    )
    
    if success:
        print(f"[+] 签名完成：{output}")
    else:
        print("[-] 签名失败")
        sys.exit(1)


def cmd_remove_signature(args):
    """去除 APK 签名"""
    print(f"[*] 开始去除签名：{args.input}")
    
    decompiler = APKDecompiler()
    output = args.output or args.input.replace(".apk", "_unsigned.apk")
    
    success = decompiler.remove_signature(args.input, output)
    
    if success:
        print(f"[+] 去除签名完成：{output}")
    else:
        print("[-] 去除签名失败")
        sys.exit(1)


def cmd_analyze(args):
    """分析混淆"""
    print(f"[*] 开始分析：{args.input}")
    
    analyzer = ObfuscationAnalyzer()
    result = analyzer.analyze(args.input)
    
    print("\n[混淆分析报告]")
    print(f"是否混淆：{'是' if result.get('obfuscation_detected') else '否'}")
    print(f"混淆类型：{', '.join(result.get('obfuscation_type', ['无']))}")
    print(f"严重程度：{result.get('severity', 'unknown')}")
    
    if args.verbose and result.get('details'):
        print("\n[详细信息]")
        details = result['details']
        
        if 'class_names' in details:
            stats = details['class_names']
            print(f"\n类名统计:")
            print(f"  总数：{stats.get('total', 0)}")
            print(f"  混淆数：{stats.get('obfuscated', 0)}")
        
        if 'method_names' in details:
            stats = details['method_names']
            print(f"\n方法名统计:")
            print(f"  总数：{stats.get('total', 0)}")
            print(f"  混淆数：{stats.get('obfuscated', 0)}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n[+] 报告已保存到：{args.output}")


def cmd_decrypt_strings(args):
    """解密字符串"""
    print(f"[*] 开始解密字符串：{args.input}")
    
    decryptor = StringDecryptor()
    
    # 查找加密的字符串
    print("[*] 查找加密字符串...")
    encrypted = decryptor.find_encrypted_strings(args.input)
    print(f"[+] 发现 {len(encrypted)} 处加密字符串")
    
    # 解密 Base64 字符串
    print("[*] 解密 Base64 字符串...")
    decrypted = decryptor.decrypt_base64_strings(args.input)
    print(f"[+] 解密 {len(decrypted)} 条字符串")
    
    if args.verbose:
        print("\n[解密的字符串]")
        for i, s in enumerate(decrypted[:20], 1):
            print(f"  {i}. {s}")
        if len(decrypted) > 20:
            print(f"  ... 还有 {len(decrypted) - 20} 条")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                'encrypted_locations': encrypted,
                'decrypted_strings': decrypted
            }, f, indent=2, ensure_ascii=False)
        print(f"\n[+] 结果已保存到：{args.output}")


def cmd_anti_obfuscation(args):
    """反混淆"""
    print(f"[*] 开始反混淆：{args.input}")
    
    tool = AntiAntiObfuscation()
    result = tool.process(args.input)
    
    # 显示结果
    analysis = result['analysis']
    print("\n[反混淆分析]")
    print(f"混淆程度：{analysis.get('severity', 'unknown')}")
    print(f"混淆类型：{', '.join(analysis.get('obfuscation_type', ['无']))}")
    
    print("\n[解密结果]")
    print(f"解密字符串：{len(result['decrypted_strings'])} 条")
    print(f"解密方法：{len(result['decryption_methods'])} 个")
    
    print("\n[分析建议]")
    for suggestion in result['suggestions']:
        print(f"  {suggestion}")
    
    if args.output:
        report = tool.export_report(args.input, args.output)
        print(f"\n[+] 报告已保存到：{args.output}")


def cmd_batch(args):
    """批量处理"""
    print(f"[*] 开始批量处理：{args.directory}")
    
    # 查找所有 APK 文件
    apk_files = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith('.apk'):
                apk_files.append(os.path.join(root, file))
    
    if not apk_files:
        print("[-] 未找到 APK 文件")
        sys.exit(1)
    
    print(f"[+] 找到 {len(apk_files)} 个 APK 文件")
    
    decompiler = APKDecompiler()
    output_base = args.output or os.path.join(args.directory, "decompiled")
    os.makedirs(output_base, exist_ok=True)
    
    success_count = 0
    for i, apk in enumerate(apk_files, 1):
        print(f"\n[{i}/{len(apk_files)}] 处理：{os.path.basename(apk)}")
        output_dir = os.path.join(output_base, Path(apk).stem)
        
        if args.java:
            success = decompiler.decompile_to_java(apk, output_dir)
        else:
            success = decompiler.decompile_apk(apk, output_dir)
        
        if success:
            success_count += 1
            print(f"[+] 完成：{output_dir}")
        else:
            print(f"[-] 失败")
    
    print(f"\n[汇总]")
    print(f"成功：{success_count}/{len(apk_files)}")


def main():
    parser = argparse.ArgumentParser(
        description='APK 反编译工具 - 命令行版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s decompile app.apk -o output
  %(prog)s compile ./project -o new.apk
  %(prog)s info app.apk -v
  %(prog)s analyze ./decompiled -v
  %(prog)s batch ./apks -o output
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 反编译命令
    decompile_parser = subparsers.add_parser('decompile', help='反编译 APK')
    decompile_parser.add_argument('input', help='输入 APK 文件')
    decompile_parser.add_argument('-o', '--output', help='输出目录')
    decompile_parser.add_argument('--java', action='store_true', help='反编译为 Java 代码')
    decompile_parser.add_argument('-s', '--no-src', action='store_true', help='仅反编译资源')
    decompile_parser.set_defaults(func=cmd_decompile)
    
    # 编译命令
    compile_parser = subparsers.add_parser('compile', help='编译 APK')
    compile_parser.add_argument('input', help='项目目录')
    compile_parser.add_argument('-o', '--output', help='输出 APK 文件')
    compile_parser.set_defaults(func=cmd_compile)
    
    # 提取命令
    extract_parser = subparsers.add_parser('extract', help='提取 APK')
    extract_parser.add_argument('input', help='输入 APK 文件')
    extract_parser.add_argument('-o', '--output', help='输出目录')
    extract_parser.set_defaults(func=cmd_extract)
    
    # 信息命令
    info_parser = subparsers.add_parser('info', help='显示 APK 信息')
    info_parser.add_argument('input', help='输入 APK 文件')
    info_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    info_parser.set_defaults(func=cmd_info)
    
    # 签名命令
    sign_parser = subparsers.add_parser('sign', help='签名 APK')
    sign_parser.add_argument('input', help='输入 APK 文件')
    sign_parser.add_argument('-k', '--keystore', required=True, help='密钥库文件')
    sign_parser.add_argument('-a', '--alias', required=True, help='密钥别名')
    sign_parser.add_argument('-o', '--output', help='输出文件')
    sign_parser.set_defaults(func=cmd_sign)
    
    # 去签名命令
    remove_sig_parser = subparsers.add_parser('remove-signature', help='去除 APK 签名')
    remove_sig_parser.add_argument('input', help='输入 APK 文件')
    remove_sig_parser.add_argument('-o', '--output', help='输出文件')
    remove_sig_parser.set_defaults(func=cmd_remove_signature)
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析混淆')
    analyze_parser.add_argument('input', help='项目目录')
    analyze_parser.add_argument('-o', '--output', help='输出报告文件')
    analyze_parser.add_argument('-v', '--verbose', action='store_true', help='详细信息')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # 解密字符串命令
    decrypt_parser = subparsers.add_parser('decrypt-strings', help='解密字符串')
    decrypt_parser.add_argument('input', help='项目目录')
    decrypt_parser.add_argument('-o', '--output', help='输出文件')
    decrypt_parser.add_argument('-v', '--verbose', action='store_true', help='显示结果')
    decrypt_parser.set_defaults(func=cmd_decrypt_strings)
    
    # 反混淆命令
    anti_obf_parser = subparsers.add_parser('anti-obfuscation', help='反混淆')
    anti_obf_parser.add_argument('input', help='项目目录')
    anti_obf_parser.add_argument('-o', '--output', help='输出报告')
    anti_obf_parser.set_defaults(func=cmd_anti_obfuscation)
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='批量处理')
    batch_parser.add_argument('directory', help='包含 APK 的目录')
    batch_parser.add_argument('-o', '--output', help='输出目录')
    batch_parser.add_argument('--java', action='store_true', help='反编译为 Java')
    batch_parser.set_defaults(func=cmd_batch)
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)
    
    print_banner()
    args.func(args)


if __name__ == "__main__":
    main()

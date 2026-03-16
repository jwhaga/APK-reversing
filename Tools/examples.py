#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK 反编译工具使用示例
演示如何使用 API 进行自动化操作
"""

import os
from apk_tool import APKDecompiler, APKEditor
from advanced_tools import AntiAntiObfuscation, StringDecryptor, ObfuscationAnalyzer


def example1_basic_decompile():
    """示例 1: 基本反编译"""
    print("=" * 60)
    print("示例 1: 基本反编译")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_path = "example.apk"
    
    if not os.path.exists(apk_path):
        print(f"[错误] 文件不存在：{apk_path}")
        return
    
    # 反编译为 smali
    output_dir = "output_smali"
    print(f"正在反编译：{apk_path}")
    success = decompiler.decompile_apk(apk_path, output_dir)
    
    if success:
        print(f"[成功] 反编译完成：{output_dir}")
        
        # 查看生成的文件
        files = decompiler.list_directory(output_dir)
        print(f"生成的文件数：{len(files)}")
    else:
        print("[失败] 反编译失败")


def example2_java_decompile():
    """示例 2: 反编译为 Java 代码"""
    print("\n" + "=" * 60)
    print("示例 2: 反编译为 Java 代码")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_path = "example.apk"
    
    if not os.path.exists(apk_path):
        return
    
    output_dir = "output_java"
    print(f"正在反编译为 Java: {apk_path}")
    success = decompiler.decompile_to_java(apk_path, output_dir)
    
    if success:
        print(f"[成功] Java 代码输出到：{output_dir}")
    else:
        print("[失败] Java 反编译失败")


def example3_extract_and_modify():
    """示例 3: 提取并修改文件"""
    print("\n" + "=" * 60)
    print("示例 3: 提取并修改文件")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_path = "example.apk"
    
    if not os.path.exists(apk_path):
        return
    
    # 提取 APK
    output_dir = "extracted"
    print(f"正在提取：{apk_path}")
    success = decompiler.extract_apk(apk_path, output_dir)
    
    if success:
        # 读取并修改 AndroidManifest.xml
        manifest_path = os.path.join(output_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            content = decompiler.get_file_content(manifest_path)
            print(f"Manifest 文件大小：{len(content)} 字节")
            
            # 这里可以修改 content
            # decompiler.save_file_content(manifest_path, modified_content)
    
    # 重新编译
    # decompiler.compile_apk(output_dir, "modified.apk")


def example4_sign_apk():
    """示例 4: 签名 APK"""
    print("\n" + "=" * 60)
    print("示例 4: 签名 APK")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_path = "unsigned.apk"
    keystore = "my-release-key.jks"
    
    if not os.path.exists(apk_path):
        print(f"[错误] APK 不存在：{apk_path}")
        return
    
    if not os.path.exists(keystore):
        print(f"[错误] 密钥库不存在：{keystore}")
        print("提示：使用 keytool 生成密钥库")
        return
    
    output_path = "signed.apk"
    print(f"正在签名：{apk_path}")
    success = decompiler.sign_apk(
        apk_path=apk_path,
        keystore_path=keystore,
        keystore_password="your_keystore_password",
        alias="your_alias",
        alias_password="your_alias_password",
        output_path=output_path
    )
    
    if success:
        print(f"[成功] 签名完成：{output_path}")
    else:
        print("[失败] 签名失败")


def example5_remove_signature():
    """示例 5: 去除 APK 签名"""
    print("\n" + "=" * 60)
    print("示例 5: 去除 APK 签名")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_path = "signed.apk"
    
    if not os.path.exists(apk_path):
        return
    
    output_path = "unsigned.apk"
    print(f"正在去除签名：{apk_path}")
    success = decompiler.remove_signature(apk_path, output_path)
    
    if success:
        print(f"[成功] 签名已去除：{output_path}")
    else:
        print("[失败] 去除签名失败")


def example6_analyze_obfuscation():
    """示例 6: 分析混淆"""
    print("\n" + "=" * 60)
    print("示例 6: 分析混淆")
    print("=" * 60)
    
    analyzer = ObfuscationAnalyzer()
    project_dir = "decompiled_app"
    
    if not os.path.exists(project_dir):
        print(f"[错误] 目录不存在：{project_dir}")
        return
    
    print(f"正在分析：{project_dir}")
    result = analyzer.analyze(project_dir)
    
    print(f"\n混淆检测结果：{'是' if result.get('obfuscation_detected') else '否'}")
    print(f"混淆类型：{', '.join(result.get('obfuscation_type', ['无']))}")
    print(f"严重程度：{result.get('severity', 'unknown')}")
    
    if result.get('details'):
        details = result['details']
        if 'class_names' in details:
            stats = details['class_names']
            print(f"\n类名混淆：{stats.get('obfuscated', 0)}/{stats.get('total', 0)}")
        
        if 'method_names' in details:
            stats = details['method_names']
            print(f"方法名混淆：{stats.get('obfuscated', 0)}/{stats.get('total', 0)}")


def example7_decrypt_strings():
    """示例 7: 解密字符串"""
    print("\n" + "=" * 60)
    print("示例 7: 解密字符串")
    print("=" * 60)
    
    decryptor = StringDecryptor()
    smali_dir = "decompiled_app/smali"
    
    if not os.path.exists(smali_dir):
        return
    
    print(f"正在查找加密字符串：{smali_dir}")
    
    # 查找加密字符串的位置
    encrypted = decryptor.find_encrypted_strings(smali_dir)
    print(f"发现 {len(encrypted)} 处加密字符串")
    
    # 解密 Base64 字符串
    decrypted = decryptor.decrypt_base64_strings(smali_dir)
    print(f"成功解密 {len(decrypted)} 条字符串")
    
    if decrypted:
        print("\n部分解密的字符串:")
        for i, s in enumerate(decrypted[:10], 1):
            print(f"  {i}. {s}")


def example8_anti_obfuscation():
    """示例 8: 完整反混淆"""
    print("\n" + "=" * 60)
    print("示例 8: 完整反混淆")
    print("=" * 60)
    
    tool = AntiAntiObfuscation()
    project_dir = "decompiled_app"
    
    if not os.path.exists(project_dir):
        return
    
    print(f"正在处理：{project_dir}")
    result = tool.process(project_dir)
    
    # 显示分析报告
    analysis = result['analysis']
    print(f"\n混淆程度：{analysis.get('severity', 'unknown')}")
    print(f"混淆类型：{', '.join(analysis.get('obfuscation_type', ['无']))}")
    
    print(f"\n解密结果:")
    print(f"  - 字符串：{len(result['decrypted_strings'])} 条")
    print(f"  - 解密方法：{len(result['decryption_methods'])} 个")
    
    print("\n分析建议:")
    for suggestion in result['suggestions']:
        print(f"  • {suggestion}")
    
    # 导出报告
    report_path = "analysis_report.txt"
    tool.export_report(project_dir, report_path)
    print(f"\n完整报告已保存到：{report_path}")


def example9_batch_processing():
    """示例 9: 批量处理"""
    print("\n" + "=" * 60)
    print("示例 9: 批量处理 APK 文件")
    print("=" * 60)
    
    decompiler = APKDecompiler()
    apk_directory = "apks"
    output_base = "batch_output"
    
    if not os.path.exists(apk_directory):
        print(f"[错误] 目录不存在：{apk_directory}")
        return
    
    # 查找所有 APK
    apk_files = []
    for file in os.listdir(apk_directory):
        if file.endswith('.apk'):
            apk_files.append(os.path.join(apk_directory, file))
    
    print(f"找到 {len(apk_files)} 个 APK 文件")
    
    os.makedirs(output_base, exist_ok=True)
    
    # 批量反编译
    success_count = 0
    for i, apk in enumerate(apk_files, 1):
        print(f"\n[{i}/{len(apk_files)}] 处理：{os.path.basename(apk)}")
        output_dir = os.path.join(output_base, os.path.splitext(os.path.basename(apk))[0])
        
        success = decompiler.decompile_apk(apk, output_dir)
        if success:
            success_count += 1
            print(f"[成功] 输出到：{output_dir}")
        else:
            print(f"[失败]")
    
    print(f"\n完成：{success_count}/{len(apk_files)} 成功")


def example10_full_workflow():
    """示例 10: 完整工作流程"""
    print("\n" + "=" * 60)
    print("示例 10: 完整工作流程")
    print("=" * 60)
    
    apk_path = "target.apk"
    
    if not os.path.exists(apk_path):
        print(f"[错误] 文件不存在：{apk_path}")
        return
    
    decompiler = APKDecompiler()
    output_dir = "analysis_output"
    
    # 步骤 1: 反编译
    print("\n[步骤 1/5] 反编译 APK...")
    decompiler.decompile_apk(apk_path, output_dir)
    
    # 步骤 2: 分析混淆
    print("\n[步骤 2/5] 分析混淆...")
    analyzer = ObfuscationAnalyzer()
    analysis = analyzer.analyze(output_dir)
    
    # 步骤 3: 解密字符串
    print("\n[步骤 3/5] 解密字符串...")
    decryptor = StringDecryptor()
    decrypted = decryptor.decrypt_base64_strings(os.path.join(output_dir, 'smali'))
    print(f"解密 {len(decrypted)} 条字符串")
    
    # 步骤 4: 生成报告
    print("\n[步骤 4/5] 生成分析报告...")
    tool = AntiAntiObfuscation()
    tool.export_report(output_dir, "full_analysis.txt")
    
    # 步骤 5: 重新编译和签名
    print("\n[步骤 5/5] 重新编译...")
    compiled_apk = "modified.apk"
    decompiler.compile_apk(output_dir, compiled_apk)
    
    print("\n[完成] 所有步骤已完成!")
    print(f"输出文件：{compiled_apk}")
    print(f"分析报告：full_analysis.txt")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print(" " * 18 + "APK 反编译工具示例集")
    print("=" * 60)
    
    # 可以选择运行特定示例
    examples = [
        example1_basic_decompile,
        example2_java_decompile,
        example3_extract_and_modify,
        example4_sign_apk,
        example5_remove_signature,
        example6_analyze_obfuscation,
        example7_decrypt_strings,
        example8_anti_obfuscation,
        example9_batch_processing,
        example10_full_workflow,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[错误] {example.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

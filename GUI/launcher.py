"""
APK 反编译工具启动器
"""
import os
import sys
import subprocess

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    # 添加项目根目录到 Python 路径
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    
    print("========================================")
    print("APK 反编译工具 - 全版本集成")
    print("Ultimate Edition - v5.0")
    print("========================================")
    print()
    
    # 检查 Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"[信息] Python 已安装：{result.stdout.strip()}")
    except:
        print("[错误] 未检测到 Python，请先安装 Python 3.8+")
        input("按回车键退出...")
        return
    
    print("[信息] 检查并安装依赖...")
    subprocess.run(['pip', 'install', 'PyQt5', 'pycryptodome', '-q'])
    
    print()
    print("请选择启动模式:")
    print()
    print("  1. v5.0 终极集成版 (推荐) - 整合所有功能")
    print("  2. v4.0 完全重构版 - AI 集成")
    print("  3. v3.0 现代化版 - 美化界面")
    print("  4. v2.0 经典版 - 稳定版本")
    print("  5. 退出")
    print()
    
    choice = input("请输入选项 (1-5): ").strip()
    
    scripts = {
        '1': 'gui_ultimate.py',
        '2': 'gui_v4.py',
        '3': 'gui_modern.py',
        '4': 'gui_standalone.py'
    }
    
    if choice in scripts:
        # 脚本在 GUI 文件夹中
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), scripts[choice])
        print(f"\n[信息] 启动 {scripts[choice]}...")
        print(f"[信息] 完整路径：{script_path}")
        
        # 检查文件是否存在
        if not os.path.exists(script_path):
            print(f"[错误] 文件不存在：{script_path}")
            return
        
        # 使用 python 而不是 pythonw，这样可以看到错误信息
        print("[信息] 正在启动 GUI 程序，请稍候...")
        proc = subprocess.Popen(['python', script_path], 
                               cwd=base_dir,  # 工作目录设为根目录，方便导入模块
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        
        # 等待 2 秒看是否有错误
        import time
        time.sleep(2)
        if proc.poll() is not None:
            # 程序已退出，显示错误
            stdout, stderr = proc.communicate()
            if stderr:
                print(f"[错误] GUI 程序启动失败:\n{stderr.decode('utf-8', errors='ignore')}")
            else:
                print(f"[错误] GUI 程序异常退出，返回码：{proc.returncode}")
        else:
            print(f"[信息] GUI 程序已启动！如果看不到界面，请检查任务栏是否有窗口最小化")
            print("[信息] 程序正在后台运行...")
    elif choice == '5':
        print("已退出")
        return
    else:
        print("无效选项")
        return
    
    print("\n程序已启动，按回车键退出...")
    try:
        input()
    except:
        pass

if __name__ == '__main__':
    main()

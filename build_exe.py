#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化打包脚本 - 将API稳定性测试脚本打包成exe可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"], check=True)
        print("✅ PyInstaller 安装完成")
    
    # 检查必要文件
    required_files = ["api_stability_test.py", "app.ico"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
        else:
            print(f"✅ 找到文件: {file}")
    
    return True

def clean_build_dirs():
    """清理之前的构建目录"""
    print("\n🧹 清理构建目录...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 删除目录: {dir_name}")
    
    # 删除spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✅ 删除文件: {spec_file}")

def build_exe():
    """构建exe文件"""
    print("\n🔨 开始构建exe文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 不显示控制台窗口（可选）
        "--icon=app.ico",              # 设置图标
        "--name=API稳定性测试工具",      # 设置exe文件名
        "--add-data=app.ico;.",        # 包含图标文件
        "--clean",                     # 清理临时文件
        "--noconfirm",                 # 不询问确认
        "api_stability_test.py"        # 主脚本文件
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_console_version():
    """创建控制台版本（显示命令行窗口）"""
    print("\n🔨 创建控制台版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--console",                    # 显示控制台窗口
        "--icon=app.ico",              # 设置图标
        "--name=API稳定性测试工具_控制台版", # 设置exe文件名
        "--add-data=app.ico;.",        # 包含图标文件
        "--clean",                     # 清理临时文件
        "--noconfirm",                 # 不询问确认
        "api_stability_test.py"        # 主脚本文件
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 控制台版本构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 控制台版本构建失败: {e}")
        return False

def copy_files():
    """复制必要文件到dist目录"""
    print("\n📁 复制必要文件...")
    
    if os.path.exists("dist"):
        # 复制README文件
        if os.path.exists("README.md"):
            shutil.copy2("README.md", "dist/")
            print("✅ 复制 README.md")
        
        # 复制图标文件
        if os.path.exists("app.ico"):
            shutil.copy2("app.ico", "dist/")
            print("✅ 复制 app.ico")
        
        # 创建使用说明
        usage_text = """
API稳定性测试工具使用说明
========================

1. 双击运行 "API稳定性测试工具.exe" 或 "API稳定性测试工具_控制台版.exe"
2. 程序会自动开始测试新浪财经API的稳定性
3. 每3秒更新一次数据，显示股票信息和统计数据
4. 按 Ctrl+C 停止测试
5. 测试结果会自动保存为JSON日志文件

注意事项：
- 确保网络连接正常
- 程序会持续运行直到手动停止
- 日志文件会保存在程序同目录下

如有问题，请查看 README.md 文件获取详细说明。
"""
        
        with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
            f.write(usage_text)
        print("✅ 创建使用说明.txt")

def main():
    """主函数"""
    print("🚀 API稳定性测试工具 - 自动打包脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        print("❌ 依赖检查失败，退出")
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建exe文件
    if not build_exe():
        print("❌ 构建失败，退出")
        return
    
    # 创建控制台版本
    create_console_version()
    
    # 复制文件
    copy_files()
    
    print("\n🎉 打包完成!")
    print("=" * 50)
    print("📁 输出目录: dist/")
    
    if os.path.exists("dist"):
        print("\n📦 生成的文件:")
        for file in os.listdir("dist"):
            file_path = os.path.join("dist", file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"  📄 {file} ({size:.1f} MB)")
    
    print("\n✅ 可以在 dist 目录中找到可执行文件!")
    print("💡 建议测试两个版本，选择适合的使用")

if __name__ == "__main__":
    main() 
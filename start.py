#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据测试工具 - 主入口
提供清晰的测试入口选择
"""

import os
import sys
import subprocess

def print_banner():
    """打印项目横幅"""
    print("=" * 60)
    print("🚀 股票数据测试工具")
    print("=" * 60)
    print("📊 日K线数据测试 | ⚡ 分时数据测试")
    print("=" * 60)

def print_menu():
    """打印菜单选项"""
    print("\n📋 请选择测试类型:")
    print("=" * 40)
    
    print("\n📊 日K线数据测试:")
    print("  1. 数据源可靠性测试 (kline_reliability_test.py)")
    
    print("\n⚡ 分时数据测试:")
    print("  2. 快速验证 (realtime_quick_validation.py)")
    print("  3. 综合测试 (realtime_comprehensive_test.py)")
    
    print("\n🔧 其他选项:")
    print("  4. 查看项目结构")
    print("  5. 退出")

def run_test(test_file, description):
    """运行指定的测试文件"""
    print(f"\n🚀 正在运行: {description}")
    print("=" * 50)
    
    try:
        # 构建文件路径 - 使用新的英文目录名
        if "kline" in test_file:
            file_path = os.path.join("kline", test_file)
        else:
            file_path = os.path.join("realtime", test_file)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 错误: 文件 {file_path} 不存在")
            return
        
        # 运行测试
        result = subprocess.run([sys.executable, file_path], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print(f"\n✅ {description} 运行完成")
        else:
            print(f"\n❌ {description} 运行失败")
            
    except Exception as e:
        print(f"❌ 运行出错: {e}")

def show_project_structure():
    """显示项目结构"""
    print("\n📁 项目结构:")
    print("=" * 40)
    
    structure = """
PythonSinacj/
├── 📁 core/
│   ├── kline_data_fetcher.py          # 日K线数据获取器
│   ├── realtime_data_fetcher.py       # 分时数据获取器
│   └── requirements.txt               # 依赖包
│
├── 📁 kline/
│   └── kline_reliability_test.py      # 数据源可靠性测试
│
├── 📁 realtime/
│   ├── realtime_quick_validation.py   # 快速验证
│   └── realtime_comprehensive_test.py # 综合测试
│
├── 📁 tools/
│   ├── build_exe.py                   # 打包工具
│   └── build.bat                      # 构建脚本
│
├── 📁 docs/
│   └── [各种文档文件]
│
├── 📁 resources/
│   └── app.ico                        # 应用图标
│
└── 测试入口.py                        # 主入口文件
"""
    print(structure)

def main():
    """主函数"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("\n请选择 (1-9): ").strip()
            
            if choice == "1":
                run_test("kline_reliability_test.py", "日K线数据源可靠性测试")
            elif choice == "2":
                run_test("realtime_quick_validation.py", "分时数据快速验证")
            elif choice == "3":
                run_test("realtime_comprehensive_test.py", "分时数据综合测试")
            elif choice == "4":
                show_project_structure()
            elif choice == "5":
                print("\n👋 再见!")
                break
            else:
                print("❌ 无效选择，请输入 1-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
        
        input("\n按回车键继续...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main() 
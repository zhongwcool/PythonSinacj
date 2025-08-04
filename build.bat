@echo off
chcp 65001 >nul
echo 🚀 API稳定性测试工具 - 快速打包
echo ================================
echo.

echo 📦 正在运行打包脚本...
python build_exe.py

echo.
echo ✅ 打包完成！
echo 📁 请查看 dist 目录中的可执行文件
echo.
pause 
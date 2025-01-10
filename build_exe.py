import os
import subprocess

# 项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# PyInstaller 打包命令
command = [
    "pyinstaller",
    "--noconfirm",          # 覆盖已有打包文件
    "--onefile",            # 打包成单个文件
    "--windowed",           # 隐藏命令行窗口（适用于 GUI 程序）
    "--icon=icon.ico",      # 指定图标文件
    "--name=ZipManager",    # 输出的可执行文件名称
    os.path.join(project_root, "Source", "main.py")  # 指定入口文件路径
]

# 执行打包命令
print("开始打包...")
result = subprocess.run(command, shell=True)

# 检查结果
if result.returncode == 0:
    print("打包成功！请查看 dist/ZipManager.exe")
else:
    print("打包失败！请检查输出信息。")

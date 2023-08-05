import sys
from cx_Freeze import setup, Executable

# 要打包的脚本文件
main_script = "main.py"

# 数据文件列表（如果有其他的数据文件，可以在这里添加）
data_files = ["memory.json"]

# 构建可执行文件
build_exe_options = {
    "include_files": data_files
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 如果你的脚本是一个 GUI 应用程序，设置为 "Win32GUI"，否则设置为 None

# 创建可执行文件配置
executables = [
    Executable(main_script, base=base)
]

# 设置 cx_Freeze 的参数
cx_Freeze_options = {
    "build_exe": build_exe_options
}

# 创建 setup
setup(
    name="YourApp",  # 应用程序的名称
    version="1.0",   # 版本号
    description="Your description",  # 描述
    options=cx_Freeze_options,
    executables=executables
)

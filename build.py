"""
ArchiveShell - 打包脚本
生成单个可执行文件
"""

import os
import sys
import subprocess
import shutil


def check_pyinstaller():
    """检查并安装 PyInstaller"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller 已安装：{PyInstaller.__version__}")
        return True
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True


def build_onefile():
    """打包成单个可执行文件"""
    print("=" * 60)
    print("ArchiveShell - 打包成单文件可执行程序")
    print("=" * 60)
    print()
    
    # 检查 PyInstaller
    check_pyinstaller()
    print()
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ArchiveShell",
        "--add-data", f"requirements.txt{os.pathsep}.",
        "--add-data", f"README.md{os.pathsep}.",
        "--hidden-import", "py7zr",
        "--hidden-import", "py7zr.helpers",
        "--hidden-import", "py7zr.compressor",
        "--hidden-import", "rarfile",
        "--hidden-import", "cryptography",
        "--hidden-import", "Cryptodome.Cipher",
        "--hidden-import", "Cryptodome.Util",
        "--hidden-import", "texttable",
        "--hidden-import", "multivolumefile",
        "--hidden-import", "pyzstd",
        "--hidden-import", "inflate64",
        "--hidden-import", "bcj",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--console",
        "--clean",
        "archive_handler.py"
    ]
    
    print("执行打包命令...")
    print()
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("[OK] 打包完成！")
        print("=" * 60)
        print()
        print(f"生成的文件：dist{os.sep}ArchiveShell.exe")
        
        # 显示文件大小
        exe_path = os.path.join("dist", "ArchiveShell.exe")
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            size_mb = size / (1024 * 1024)
            print(f"文件大小：{size_mb:.2f} MB")
        
        print()
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("[ERROR] 打包失败！")
        print("=" * 60)
        print()
        return False


def build_installer():
    """打包安装程序"""
    print()
    print("=" * 60)
    print("打包安装程序...")
    print("=" * 60)
    print()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ArchiveShell_Installer",
        "--hidden-import", "winreg",
        "--console",
        "--clean",
        "register.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("[OK] 安装程序打包完成！")
        print(f"生成的文件：dist{os.sep}ArchiveShell_Installer.exe")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] 安装程序打包失败！")
        return False


def build_gui():
    """打包 GUI 安装程序（窗口模式）"""
    print()
    print("=" * 60)
    print("打包 GUI 安装程序...")
    print("=" * 60)
    print()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "ArchiveShell_GUI",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--clean",
        "installer_gui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("[OK] GUI 安装程序打包完成！")
        print(f"生成的文件：dist{os.sep}ArchiveShell_GUI.exe")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] GUI 安装程序打包失败！")
        return False


def create_release_package():
    """创建发布包"""
    print()
    print("=" * 60)
    print("创建发布包...")
    print("=" * 60)
    print()
    
    release_dir = "dist\\release"
    
    # 清理旧目录
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制文件
    files_to_copy = [
        "dist\\ArchiveShell.exe",
        "dist\\ArchiveShell_Installer.exe",
        "dist\\ArchiveShell_GUI.exe",
        "README.md",
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, release_dir)
            print(f"[OK] 复制：{file}")
    
    # 创建说明文件
    readme_txt = os.path.join(release_dir, "使用说明.txt")
    with open(readme_txt, "w", encoding="utf-8") as f:
        f.write("""
================================================
ArchiveShell - Windows 资源管理器 7z/RAR 浏览扩展
================================================

文件说明:
  - ArchiveShell.exe           : 压缩文件浏览器主程序
  - ArchiveShell_Installer.exe : 命令行安装/卸载程序
  - ArchiveShell_GUI.exe       : 图形化安装程序

安装方法:
  方法 1 (推荐): 以管理员身份运行 ArchiveShell_GUI.exe
  方法 2: 以管理员身份运行命令行
         ArchiveShell_Installer.exe install

使用方法:
  安装完成后，双击 7z/RAR 文件即可在资源管理器中浏览

卸载方法:
  ArchiveShell_Installer.exe uninstall

================================================
""")
    
    print(f"[OK] 创建：{readme_txt}")
    print()
    print(f"发布包目录：{os.path.abspath(release_dir)}")
    print()
    
    # 打开发布目录
    os.startfile(os.path.abspath(release_dir))


def main():
    """主函数"""
    print()
    
    # 打包主程序
    if not build_onefile():
        print("主程序打包失败，退出")
        sys.exit(1)
    
    # 打包安装程序
    build_installer()
    
    # 打包 GUI
    build_gui()
    
    # 创建发布包
    create_release_package()
    
    print()
    print("=" * 60)
    print("所有打包操作完成！")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()

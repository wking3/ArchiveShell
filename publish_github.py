"""
GitHub Release 发布脚本
自动创建 GitHub Release 并上传文件
"""

import os
import sys
import subprocess
import json
from pathlib import Path

try:
    from github import Github
    from github.Repository import Repository
except ImportError:
    print("正在安装 PyGithub...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub"])
    from github import Github


def get_version() -> str:
    """获取版本号"""
    version_file = Path("release.ini")
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version = "):
                    return line.split("=")[1].strip()
    return "1.0.0"


def create_release_zip():
    """创建发布压缩包"""
    import zipfile
    
    release_dir = Path("dist/release")
    zip_path = Path("ArchiveShell.zip")
    
    if not release_dir.exists():
        print("错误：发布目录不存在，请先运行 build.py")
        return False
    
    print(f"创建发布压缩包：{zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in release_dir.iterdir():
            if file.is_file():
                zipf.write(file, file.name)
                print(f"  添加：{file.name}")
    
    print(f"完成：{zip_path}")
    return True


def create_github_release(token: str, tag: str = None):
    """创建 GitHub Release"""
    
    if not token:
        print("错误：请提供 GitHub Token")
        print("用法：python publish_github.py <GitHub_Token> [版本号]")
        return False
    
    # 获取版本
    version = tag if tag else f"v{get_version()}"
    if not version.startswith("v"):
        version = f"v{version}"
    
    print(f"准备发布版本：{version}")
    
    # 创建压缩包
    if not create_release_zip():
        return False
    
    # 连接 GitHub
    try:
        g = Github(token)
        repo = g.get_repo("wking3/ArchiveShell")
        print(f"仓库：{repo.full_name}")
    except Exception as e:
        print(f"连接 GitHub 失败：{e}")
        return False
    
    # 创建 Release
    release_body = """## 更新内容

### 功能特性
- ✅ 双击 7z/RAR 文件直接在资源管理器中浏览
- ✅ 支持复制/粘贴压缩包内文件
- ✅ 支持拖拽操作
- ✅ 显示压缩包内文件详细信息
- ✅ 支持子文件夹浏览

### 安装说明
1. 下载 `ArchiveShell.zip`
2. 解压到任意目录
3. 以管理员身份运行 `ArchiveShell_GUI.exe` 或 `ArchiveShell_Installer.exe install`

### 系统要求
- Windows 10/11 (64 位)
- 管理员权限

### 文件说明
- `ArchiveShell.exe` - 压缩文件浏览器主程序
- `ArchiveShell_Installer.exe` - 命令行安装/卸载程序
- `ArchiveShell_GUI.exe` - 图形化安装程序

### 卸载
运行 `ArchiveShell_Installer.exe uninstall`
"""
    
    try:
        release = repo.create_git_release(
            tag=version,
            name=f"ArchiveShell {version}",
            message=release_body,
            draft=False,
            prerelease=False
        )
        print(f"创建 Release: {release.html_url}")
    except Exception as e:
        print(f"创建 Release 失败：{e}")
        return False
    
    # 上传文件
    files_to_upload = [
        "ArchiveShell.zip",
        "dist/release/ArchiveShell.exe",
        "dist/release/ArchiveShell_Installer.exe",
        "dist/release/ArchiveShell_GUI.exe"
    ]
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            try:
                release.upload_asset(file_path)
                print(f"  上传：{file_path}")
            except Exception as e:
                print(f"  上传失败 {file_path}: {e}")
        else:
            print(f"  跳过（文件不存在）: {file_path}")
    
    print()
    print("=" * 60)
    print("发布完成！")
    print(f"Release 地址：{release.html_url}")
    print("=" * 60)
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("ArchiveShell - GitHub Release 发布工具")
    print("=" * 60)
    print()
    
    # 检查参数
    if len(sys.argv) < 2:
        print("用法：python publish_github.py <GitHub_Token> [版本号]")
        print()
        print("或者设置环境变量：")
        print("  set GITHUB_TOKEN=your_token")
        print("  python publish_github.py [版本号]")
        print()
        
        # 尝试从环境变量获取 token
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            print("错误：未提供 GitHub Token")
            sys.exit(1)
        version = sys.argv[1] if len(sys.argv) > 1 else None
    else:
        token = sys.argv[1]
        version = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 创建 Release
    if create_github_release(token, version):
        print()
        print("发布成功！")
    else:
        print()
        print("发布失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

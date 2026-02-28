"""
ArchiveShell - GitHub 推送脚本
"""

import os
import sys
import subprocess

GIT = r"C:\Program Files\Git\bin\git.exe"

def run(cmd, cwd=None):
    """运行命令"""
    print(f"> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("ArchiveShell - Push to GitHub")
    print("=" * 60)
    print()
    
    # 获取 token
    if len(sys.argv) < 2:
        print("Usage: python push_github.py <GitHub_Token>")
        print()
        print("Get token from: https://github.com/settings/tokens")
        print("Need 'repo' permission")
        sys.exit(1)
    
    token = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 初始化
    print("1. Initialize repository...")
    run([GIT, "init"], cwd=script_dir)
    run([GIT, "branch", "-M", "main"], cwd=script_dir)
    
    # 添加文件
    print("2. Add files...")
    run([GIT, "add", "."], cwd=script_dir)
    
    # 提交
    print("3. Commit...")
    run([GIT, "commit", "-m", "Initial release: ArchiveShell v1.0.0"], cwd=script_dir)
    
    # 设置远程
    print("4. Set remote...")
    run([GIT, "remote", "remove", "origin"], cwd=script_dir)
    run([GIT, "remote", "add", "origin", f"https://oauth2:{token}@github.com/wking3/ArchiveShell.git"], cwd=script_dir)
    
    # 推送
    print("5. Push to GitHub...")
    if not run([GIT, "push", "-u", "origin", "main", "-f"], cwd=script_dir):
        print()
        print("Push failed! Please check:")
        print("1. GitHub Token is correct")
        print("2. Repository exists: https://github.com/new")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Success!")
    print("https://github.com/wking3/ArchiveShell")
    print("=" * 60)

if __name__ == "__main__":
    main()

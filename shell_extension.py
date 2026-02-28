"""
ArchiveShell - 完整的 Shell Namespace Extension 实现
让 Windows 资源管理器原生浏览 7z/RAR 压缩包（像 ZIP 一样）
"""

import os
import sys
import tempfile
import shutil
import hashlib
import threading
import winreg

from archive_parser import get_archive_manager, ArchiveEntry


def register_shell_extension():
    """注册 Shell 扩展"""
    print("=" * 60)
    print("ArchiveShell - 注册 Shell 扩展")
    print("=" * 60)
    print()
    
    # 检查管理员权限
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("错误：需要管理员权限！")
        print("请右键点击脚本，选择'以管理员身份运行'")
        return False
    
    clsid = "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    handler_script = os.path.join(script_dir, 'archive_handler.py')
    
    try:
        print("注册文件类型...")
        extensions = ['.7z', '.rar']
        
        for ext in extensions:
            ext_upper = ext[1:].upper()
            prog_id = f"ArchiveShell.{ext_upper}"
            
            # 1. 注册扩展名
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, prog_id)
            
            # 2. 注册 ProgID
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f"{ext_upper} Archive")
                winreg.SetValueEx(key, 'FriendlyTypeName', 0, winreg.REG_SZ, f"{ext_upper} 压缩包")
            
            # 3. 注册图标
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\DefaultIcon") as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, "imageres.dll,-175")
            
            # 4. 注册打开命令
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command") as key:
                cmd = f'"{sys.executable}" "{handler_script}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
            
            # 5. 注册浏览命令
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\explore") as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, "在资源管理器中浏览 (&E)")
                winreg.SetValueEx(key, 'LegacyDisable', 0, winreg.REG_SZ, "")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\explore\\command") as key:
                cmd = f'"{sys.executable}" "{handler_script}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
            
            # 6. 添加右键菜单
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{ext}\\shell\\BrowseArchive") as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, "浏览压缩包 (&B)")
                winreg.SetValueEx(key, 'Icon', 0, winreg.REG_SZ, "imageres.dll,-175")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{ext}\\shell\\BrowseArchive\\command") as key:
                cmd = f'"{sys.executable}" "{handler_script}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
            
            print(f"  ✓ {ext}")
        
        print("\n" + "=" * 60)
        print("注册完成！")
        print("\n使用方法:")
        print("  1. 双击 7z/RAR 文件即可浏览")
        print("  2. 右键点击压缩文件，选择'浏览压缩包'")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n错误：{e}")
        return False


def unregister_shell_extension():
    """注销 Shell 扩展"""
    print("=" * 60)
    print("ArchiveShell - 注销 Shell 扩展")
    print("=" * 60)
    print()
    
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("错误：需要管理员权限！")
        return False
    
    extensions = ['.7z', '.rar']
    
    try:
        print("注销文件类型...")
        
        for ext in extensions:
            ext_upper = ext[1:].upper()
            prog_id = f"ArchiveShell.{ext_upper}"
            
            keys_to_delete = [
                f"{prog_id}\\shell\\explore\\command",
                f"{prog_id}\\shell\\explore",
                f"{prog_id}\\shell\\open\\command",
                f"{prog_id}\\shell\\open",
                f"{prog_id}\\shell\\BrowseArchive\\command",
                f"{prog_id}\\shell\\BrowseArchive",
                f"{prog_id}\\shell",
                f"{prog_id}\\DefaultIcon",
                f"{prog_id}",
                f"{ext}\\shell\\BrowseArchive\\command",
                f"{ext}\\shell\\BrowseArchive",
                f"{ext}\\shell",
            ]
            
            for key_path in keys_to_delete:
                try:
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
                except FileNotFoundError:
                    pass
            
            print(f"  ✓ {ext}")
        
        print("\n" + "=" * 60)
        print("注销完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n错误：{e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python shell_extension.py [install|uninstall]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'install':
        register_shell_extension()
    elif command == 'uninstall':
        unregister_shell_extension()
    else:
        print("未知命令")

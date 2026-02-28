"""
ArchiveShell - 注册表注册/注销脚本
需要管理员权限运行

用法:
    python register.py install   - 注册 Shell 扩展
    python register.py uninstall - 注销 Shell 扩展
"""

import os
import sys
import ctypes
import winreg
from pathlib import Path


# COM 组件 CLSID
CLSID_ARCHIVE_SHELL = "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

# 支持的压缩格式
SUPPORTED_EXTENSIONS = ['.7z', '.rar']

# 程序路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
HANDLER_SCRIPT = os.path.join(SCRIPT_DIR, 'archive_handler.py')


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """以管理员权限重新运行"""
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception as e:
            print(f"提权失败：{e}")
            return False
        sys.exit(0)
    return True


def register_com_class():
    """注册 COM 类"""
    print("注册 COM 类...")
    
    try:
        # 注册 CLSID
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'CLSID\\{CLSID_ARCHIVE_SHELL}') as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'ArchiveShell Folder')
        
        # 注册 InProcServer32 (使用 Python 作为 DLL)
        python_dll = os.path.join(os.path.dirname(sys.executable), 'pythoncom310.dll')
        if not os.path.exists(python_dll):
            # 尝试查找其他版本
            import glob
            dlls = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pythoncom*.dll'))
            if dlls:
                python_dll = dlls[0]
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'CLSID\\{CLSID_ARCHIVE_SHELL}\\InProcServer32') as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, python_dll)
            winreg.SetValueEx(key, 'ThreadingModel', 0, winreg.REG_SZ, 'Apartment')
        
        # 注册 Python 脚本路径
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'CLSID\\{CLSID_ARCHIVE_SHELL}\\PythonClass') as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'ArchiveShell.ArchiveShellFolder')
        
        print(f"  COM 类已注册：{CLSID_ARCHIVE_SHELL}")
        return True
    except Exception as e:
        print(f"  注册 COM 类失败：{e}")
        return False


def register_file_extensions():
    """注册文件扩展名关联"""
    print("注册文件扩展名...")
    
    for ext in SUPPORTED_EXTENSIONS:
        ext_upper = ext[1:].upper()
        prog_id = f'ArchiveShell.{ext_upper}'
        type_name = f'{ext_upper} Archive'
        
        try:
            # 注册扩展名
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, prog_id)
            
            # 注册 ProgID
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, type_name)
            
            # 设置图标
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\DefaultIcon') as key:
                # 使用系统压缩文件图标
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'imageres.dll,-10')
            
            # 注册打开命令
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\shell\\open\\command') as key:
                cmd = f'"{PYTHON_EXE}" "{HANDLER_SCRIPT}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
            
            # 注册为文件夹视图 (关键步骤)
            # 使用已知文件夹 GUID 来模拟文件夹行为
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\ShellEx') as key:
                pass
            
            # 添加"在资源管理器中打开"的上下文菜单
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\shell\\explore\\command') as key:
                cmd = f'"{PYTHON_EXE}" "{HANDLER_SCRIPT}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
            
            print(f"  已注册：{ext}")
        except Exception as e:
            print(f"  注册扩展名 {ext} 失败：{e}")


def register_namespace_extension():
    """注册命名空间扩展"""
    print("注册命名空间扩展...")
    
    try:
        # 为每个扩展名添加命名空间处理器
        for ext in SUPPORTED_EXTENSIONS:
            ext_upper = ext[1:].upper()
            prog_id = f'ArchiveShell.{ext_upper}'
            
            # 注册 Folder 行为
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\shell\\open') as key:
                winreg.SetValueEx(key, 'LegacyDisable', 0, winreg.REG_SZ, '')
            
            print(f"  命名空间扩展已注册：{ext}")
        
        return True
    except Exception as e:
        print(f"  注册命名空间扩展失败：{e}")
        return False


def register_context_menu():
    """注册右键菜单"""
    print("注册右键菜单...")
    
    try:
        # 在压缩文件右键菜单添加"浏览压缩包"
        for ext in SUPPORTED_EXTENSIONS:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{ext}\\shell\\BrowseArchive') as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, '浏览压缩包 (&B)')
                winreg.SetValueEx(key, 'Icon', 0, winreg.REG_SZ, 'imageres.dll,-10')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{ext}\\shell\\BrowseArchive\\command') as key:
                cmd = f'"{PYTHON_EXE}" "{HANDLER_SCRIPT}" "%1"'
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
        
        print("  右键菜单已注册")
        return True
    except Exception as e:
        print(f"  注册右键菜单失败：{e}")
        return False


def unregister_com_class():
    """注销 COM 类"""
    print("注销 COM 类...")
    
    keys_to_delete = [
        f'CLSID\\{CLSID_ARCHIVE_SHELL}\\PythonClass',
        f'CLSID\\{CLSID_ARCHIVE_SHELL}\\InProcServer32',
        f'CLSID\\{CLSID_ARCHIVE_SHELL}',
    ]
    
    for key_path in keys_to_delete:
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        except FileNotFoundError:
            pass
    
    print("  COM 类已注销")


def unregister_file_extensions():
    """注销文件扩展名关联"""
    print("注销文件扩展名...")
    
    for ext in SUPPORTED_EXTENSIONS:
        ext_upper = ext[1:].upper()
        prog_id = f'ArchiveShell.{ext_upper}'
        
        keys_to_delete = [
            f'{prog_id}\\shell\\explore\\command',
            f'{prog_id}\\shell\\explore',
            f'{prog_id}\\shell\\open\\command',
            f'{prog_id}\\shell\\open',
            f'{prog_id}\\shell\\BrowseArchive\\command',
            f'{prog_id}\\shell\\BrowseArchive',
            f'{prog_id}\\shell',
            f'{prog_id}\\DefaultIcon',
            f'{prog_id}\\ShellEx',
            f'{prog_id}',
            f'{ext}\\shell\\BrowseArchive\\command',
            f'{ext}\\shell\\BrowseArchive',
            f'{ext}\\shell',
        ]
        
        for key_path in keys_to_delete:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
            except FileNotFoundError:
                pass
        
        # 清除扩展名关联
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, '')
        except FileNotFoundError:
            pass
        
        print(f"  已注销：{ext}")


def install():
    """安装/注册 Shell 扩展"""
    print("=" * 50)
    print("ArchiveShell - 安装 Shell 扩展")
    print("=" * 50)
    
    if not run_as_admin():
        print("需要管理员权限")
        return False
    
    print()
    
    # 注册 COM 类
    register_com_class()
    print()
    
    # 注册文件扩展名
    register_file_extensions()
    print()
    
    # 注册命名空间扩展
    register_namespace_extension()
    print()
    
    # 注册右键菜单
    register_context_menu()
    print()
    
    print("=" * 50)
    print("安装完成！")
    print("现在可以双击 7z/RAR 文件在资源管理器中浏览内容")
    print("=" * 50)
    
    return True


def uninstall():
    """卸载/注销 Shell 扩展"""
    print("=" * 50)
    print("ArchiveShell - 卸载 Shell 扩展")
    print("=" * 50)
    
    if not run_as_admin():
        print("需要管理员权限")
        return False
    
    print()
    
    # 注销文件扩展名
    unregister_file_extensions()
    print()
    
    # 注销 COM 类
    unregister_com_class()
    print()
    
    print("=" * 50)
    print("卸载完成！")
    print("=" * 50)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python register.py install   - 注册 Shell 扩展")
        print("  python register.py uninstall - 注销 Shell 扩展")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'install':
        install()
    elif command == 'uninstall':
        uninstall()
    else:
        print(f"未知命令：{command}")
        print("用法:")
        print("  python register.py install   - 注册 Shell 扩展")
        print("  python register.py uninstall - 注销 Shell 扩展")
        sys.exit(1)

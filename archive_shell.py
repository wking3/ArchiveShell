"""
ArchiveShell - Windows Shell 命名空间扩展
实现 IShellFolder 接口让资源管理器能够浏览压缩文件

注意：这是一个简化版本的实现，使用 Shell 文件夹视图的方式
完整实现需要更复杂的 COM 接口和 PIDL 管理
"""

import os
import sys
import tempfile
import shutil
import hashlib
import ctypes
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import comtypes
from comtypes import COMObject, GUID, IUnknown
from comtypes.hresult import S_OK, S_FALSE, E_FAIL, E_NOTIMPL
import winreg

from archive_parser import get_archive_manager, ArchiveEntry


# Windows Shell 相关常量
MAX_PATH = 260
SHGFI_ICON = 0x000000100
SHGFI_LARGEICON = 0x000000000
SHGFI_SMALLICON = 0x000000001
SHGFI_SYSICONINDEX = 0x000004000

# IShellFolder 方法 ID
IShellFolder_Methods = [
    'ParseDisplayName',
    'EnumObjects',
    'BindToObject',
    'BindToStorage',
    'CreateViewObject',
    'GetAttributesOf',
    'GetUIObjectOf',
    'GetDisplayNameOf',
    'SetNameOf',
]

# 项目标识符常量
ITEMID_SIZE = 4  # PIDL 大小


class PIDLManager:
    """PIDL (Pointer to Item ID List) 管理器"""
    
    @staticmethod
    def create_pidl(entry_index: int) -> bytes:
        """创建简单的 PIDL"""
        # 简化版本：使用 4 字节存储索引
        return entry_index.to_bytes(4, byteorder='little')
    
    @staticmethod
    def parse_pidl(pidl: bytes) -> int:
        """解析 PIDL 获取索引"""
        if len(pidl) >= 4:
            return int.from_bytes(pidl[:4], byteorder='little')
        return -1
    
    @staticmethod
    def get_pidl_size(pidl: bytes) -> int:
        """获取 PIDL 大小"""
        return len(pidl)


@dataclass
class CacheEntry:
    """缓存的压缩包条目"""
    archive_path: str
    entries: List[ArchiveEntry]
    extract_dir: str
    timestamp: float
    lock: threading.Lock


class ArchiveShellFolder(COMObject):
    """
    压缩文件 Shell 文件夹
    实现 IShellFolder 接口以在资源管理器中显示压缩包内容
    """
    
    # COM 接口标识
    _com_interfaces_ = [IUnknown]  # 简化版本
    _reg_clsid_ = "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"
    _reg_progid_ = "ArchiveShell.Folder"
    _reg_clsctx_ = 0x1  # CLSCTX_INPROC_SERVER
    
    def __init__(self, archive_path: str = None):
        super().__init__()
        self.archive_path = archive_path
        self.entries: List[ArchiveEntry] = []
        self.extract_dir: Optional[str] = None
        self.manager = get_archive_manager()
        self._lock = threading.Lock()
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_timeout = 300  # 5 分钟缓存
    
    def _ensure_extracted(self) -> str:
        """确保压缩包已解压到临时目录，返回目录路径"""
        if not self.archive_path or not os.path.exists(self.archive_path):
            raise FileNotFoundError(f"压缩文件不存在：{self.archive_path}")
        
        # 检查缓存
        self._cleanup_cache()
        cache_key = hashlib.md5(self.archive_path.encode()).hexdigest()
        
        with self._lock:
            if cache_key in self._cache:
                cache = self._cache[cache_key]
                if os.path.exists(cache.extract_dir):
                    return cache.extract_dir
            
            # 创建临时目录
            temp_base = tempfile.gettempdir()
            archive_name = os.path.splitext(os.path.basename(self.archive_path))[0]
            extract_dir = os.path.join(temp_base, f"ArchiveShell_{archive_name}_{cache_key[:8]}")
            
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir, exist_ok=True)
            
            # 解压所有文件
            entries = self.manager.read_entries(self.archive_path)
            for entry in entries:
                if not entry.is_directory:
                    try:
                        dest_path = os.path.join(extract_dir, entry.full_path.replace('/', os.sep))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        data = self.manager.extract_file_to_stream(self.archive_path, entry.full_path)
                        if data:
                            with open(dest_path, 'wb') as f:
                                f.write(data)
                    except Exception as e:
                        print(f"解压文件失败 {entry.full_path}: {e}")
            
            # 更新缓存
            self._cache[cache_key] = CacheEntry(
                archive_path=self.archive_path,
                entries=entries,
                extract_dir=extract_dir,
                timestamp=datetime.now().timestamp(),
                lock=self._lock
            )
            
            self.entries = entries
            self.extract_dir = extract_dir
            return extract_dir
    
    def _cleanup_cache(self):
        """清理过期的缓存"""
        now = datetime.now().timestamp()
        expired = []
        
        with self._lock:
            for key, cache in self._cache.items():
                if now - cache.timestamp > self._cache_timeout:
                    expired.append(key)
            
            for key in expired:
                cache = self._cache.pop(key)
                try:
                    if os.path.exists(cache.extract_dir):
                        shutil.rmtree(cache.extract_dir)
                except Exception:
                    pass
    
    def get_entries(self) -> List[ArchiveEntry]:
        """获取压缩包内的文件列表"""
        self._ensure_extracted()
        return self.entries
    
    def get_entry_path(self, entry_index: int) -> str:
        """获取指定条目的完整路径"""
        self._ensure_extracted()
        if 0 <= entry_index < len(self.entries):
            return os.path.join(self.extract_dir, self.entries[entry_index].full_path.replace('/', os.sep))
        return ''
    
    def __del__(self):
        """析构函数 - 清理临时文件"""
        if self.extract_dir and os.path.exists(self.extract_dir):
            try:
                shutil.rmtree(self.extract_dir)
            except Exception:
                pass


class ShellLink:
    """Shell 链接工具"""
    
    @staticmethod
    def create_shortcut(target_path: str, shortcut_path: str, icon_path: str = ''):
        """创建快捷方式"""
        try:
            import pythoncom
            from win32com.shell import shell
            
            shortcut = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None,
                pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
            )
            shortcut.SetPath(target_path)
            if icon_path:
                shortcut.SetIconLocation(icon_path, 0)
            shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(shortcut_path)
        except Exception as e:
            print(f"创建快捷方式失败：{e}")


def register_archive_type(extension: str, clsid: str):
    """注册文件类型关联"""
    try:
        # 注册文件扩展名
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'ArchiveShell.{extension[1:].upper()}')
        
        # 注册文件类型
        prog_id = f'ArchiveShell.{extension[1:].upper()}'
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'Archive Shell {extension[1:].upper()} Archive')
        
        # 注册默认打开方式
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\shell\\open\\command') as key:
            python_path = sys.executable
            script_path = os.path.abspath(__file__)
            cmd = f'"{python_path}" "{script_path}" "%1"'
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, cmd)
        
        # 注册为文件夹视图
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{prog_id}\\ShellEx\\{{000214F2-0000-0000-C000-000000000046}}') as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, clsid)
        
        print(f"已注册文件类型：{extension}")
    except Exception as e:
        print(f"注册文件类型失败 {extension}: {e}")


def unregister_archive_type(extension: str):
    """注销文件类型关联"""
    try:
        prog_id = f'ArchiveShell.{extension[1:].upper()}'
        
        # 删除注册表项
        keys_to_delete = [
            f'{prog_id}\\shell\\open\\command',
            f'{prog_id}\\shell\\open',
            f'{prog_id}\\shell',
            f'{prog_id}\\ShellEx\\{{000214F2-0000-0000-C000-000000000046}}',
            f'{prog_id}\\ShellEx',
            prog_id,
        ]
        
        for key_path in keys_to_delete:
            try:
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
            except FileNotFoundError:
                pass
        
        # 删除扩展名关联
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, '')
        except FileNotFoundError:
            pass
        
        print(f"已注销文件类型：{extension}")
    except Exception as e:
        print(f"注销文件类型失败 {extension}: {e}")


if __name__ == '__main__':
    # 测试代码
    if len(sys.argv) > 1:
        archive_path = sys.argv[1]
        folder = ArchiveShellFolder(archive_path)
        entries = folder.get_entries()
        print(f"压缩包：{archive_path}")
        print(f"文件数量：{len(entries)}")
        for entry in entries:
            type_str = "目录" if entry.is_directory else "文件"
            print(f"  {type_str}: {entry.full_path} ({entry.size} 字节)")
    else:
        print("用法：python archive_shell.py <压缩文件路径>")

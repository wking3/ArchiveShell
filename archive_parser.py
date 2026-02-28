"""
ArchiveShell - 压缩文件解析器
支持 7z 和 RAR 格式的读取和提取
"""

import os
import io
from typing import List, Dict, Optional, BinaryIO
from dataclasses import dataclass
from datetime import datetime
import tempfile

try:
    import py7zr
    HAS_7ZR = True
except ImportError:
    HAS_7ZR = False

try:
    import rarfile
    HAS_RAR = True
except ImportError:
    HAS_RAR = False


@dataclass
class ArchiveEntry:
    """压缩包内文件条目"""
    name: str
    full_path: str
    size: int
    compressed_size: int
    last_modified: datetime
    is_directory: bool
    crc: int = 0
    attributes: int = 0


class ArchiveParser:
    """压缩文件解析器基类"""
    
    supported_extensions: List[str] = []
    
    def is_supported(self, file_path: str) -> bool:
        """检查是否支持该文件格式"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def read_entries(self, archive_path: str) -> List[ArchiveEntry]:
        """读取压缩包内的文件列表"""
        raise NotImplementedError
    
    def extract_file(self, archive_path: str, entry_path: str, dest_path: str) -> None:
        """提取文件到指定路径"""
        raise NotImplementedError
    
    def extract_file_to_stream(self, archive_path: str, entry_path: str) -> bytes:
        """提取文件到字节流"""
        raise NotImplementedError


class SevenZipParser(ArchiveParser):
    """7z 格式解析器"""
    
    supported_extensions = ['.7z']
    
    def __init__(self):
        if not HAS_7ZR:
            raise ImportError("py7zr 库未安装，请运行：pip install py7zr")
    
    def read_entries(self, archive_path: str) -> List[ArchiveEntry]:
        """读取 7z 压缩包内的文件列表"""
        entries = []
        
        with py7zr.SevenZipFile(archive_path, 'r') as zf:
            archive_info = zf.archiveinfo()
            
            for file_info in zf.files:
                entry = ArchiveEntry(
                    name=os.path.basename(file_info.filename),
                    full_path=file_info.filename,
                    size=file_info.uncompressed,
                    compressed_size=file_info.compressed,
                    last_modified=file_info.lastwritetime,
                    is_directory=file_info.is_directory,
                    crc=file_info.crc32 if hasattr(file_info, 'crc32') else 0
                )
                entries.append(entry)
        
        return entries
    
    def extract_file(self, archive_path: str, entry_path: str, dest_path: str) -> None:
        """从 7z 压缩包提取文件"""
        with py7zr.SevenZipFile(archive_path, 'r') as zf:
            # 创建目标目录
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            # 提取单个文件
            zf.extract(path=os.path.dirname(dest_path), targets=[entry_path])
            # 移动到正确位置
            extracted_path = os.path.join(os.path.dirname(dest_path), entry_path.replace('/', os.sep))
            if os.path.exists(extracted_path) and extracted_path != dest_path:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                os.rename(extracted_path, dest_path)
    
    def extract_file_to_stream(self, archive_path: str, entry_path: str) -> bytes:
        """提取 7z 文件到字节流"""
        with py7zr.SevenZipFile(archive_path, 'r') as zf:
            data = zf.read(targets=[entry_path])
            if entry_path in data:
                return data[entry_path].read()
            # 尝试查找文件
            for name, bio in data.items():
                if name == entry_path or name.replace('\\', '/') == entry_path.replace('/', '\\'):
                    return bio.read()
            return b''


class RarParser(ArchiveParser):
    """RAR 格式解析器"""
    
    supported_extensions = ['.rar', '.rar4', '.rar5']
    
    def __init__(self):
        if not HAS_RAR:
            raise ImportError("rarfile 库未安装，请运行：pip install rarfile")
    
    def read_entries(self, archive_path: str) -> List[ArchiveEntry]:
        """读取 RAR 压缩包内的文件列表"""
        entries = []
        
        with rarfile.RarFile(archive_path, 'r') as rf:
            for info in rf.infolist():
                entry = ArchiveEntry(
                    name=os.path.basename(info.filename),
                    full_path=info.filename,
                    size=info.file_size,
                    compressed_size=info.compress_size,
                    last_modified=datetime(*info.date_time),
                    is_directory=info.is_dir(),
                    crc=info.CRC
                )
                entries.append(entry)
        
        return entries
    
    def extract_file(self, archive_path: str, entry_path: str, dest_path: str) -> None:
        """从 RAR 压缩包提取文件"""
        with rarfile.RarFile(archive_path, 'r') as rf:
            # 创建目标目录
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            # 提取文件
            rf.extract(entry_path, path=os.path.dirname(dest_path))
            # 移动到正确位置
            extracted_path = os.path.join(os.path.dirname(dest_path), entry_path.replace('/', os.sep))
            if os.path.exists(extracted_path) and extracted_path != dest_path:
                os.rename(extracted_path, dest_path)
    
    def extract_file_to_stream(self, archive_path: str, entry_path: str) -> bytes:
        """提取 RAR 文件到字节流"""
        with rarfile.RarFile(archive_path, 'r') as rf:
            return rf.read(entry_path)


class ArchiveManager:
    """压缩文件管理器 - 统一管理不同格式"""
    
    def __init__(self):
        self.parsers: List[ArchiveParser] = []
        
        # 初始化支持的解析器
        if HAS_7ZR:
            try:
                self.parsers.append(SevenZipParser())
            except Exception as e:
                print(f"7z 解析器初始化失败：{e}")
        
        if HAS_RAR:
            try:
                self.parsers.append(RarParser())
            except Exception as e:
                print(f"RAR 解析器初始化失败：{e}")
    
    def get_parser(self, archive_path: str) -> Optional[ArchiveParser]:
        """获取合适的解析器"""
        for parser in self.parsers:
            if parser.is_supported(archive_path):
                return parser
        return None
    
    def is_archive(self, archive_path: str) -> bool:
        """检查文件是否为支持的压缩格式"""
        return self.get_parser(archive_path) is not None
    
    def read_entries(self, archive_path: str) -> List[ArchiveEntry]:
        """读取压缩包内的文件列表"""
        parser = self.get_parser(archive_path)
        if parser:
            return parser.read_entries(archive_path)
        return []
    
    def extract_file(self, archive_path: str, entry_path: str, dest_path: str) -> bool:
        """提取文件"""
        parser = self.get_parser(archive_path)
        if parser:
            try:
                parser.extract_file(archive_path, entry_path, dest_path)
                return True
            except Exception as e:
                print(f"提取文件失败：{e}")
        return False
    
    def extract_file_to_stream(self, archive_path: str, entry_path: str) -> Optional[bytes]:
        """提取文件到流"""
        parser = self.get_parser(archive_path)
        if parser:
            try:
                return parser.extract_file_to_stream(archive_path, entry_path)
            except Exception as e:
                print(f"提取文件到流失败：{e}")
        return None
    
    def get_supported_extensions(self) -> List[str]:
        """获取所有支持的扩展名"""
        extensions = []
        for parser in self.parsers:
            extensions.extend(parser.supported_extensions)
        return extensions


# 全局管理器实例
_archive_manager: Optional[ArchiveManager] = None


def get_archive_manager() -> ArchiveManager:
    """获取全局压缩文件管理器实例"""
    global _archive_manager
    if _archive_manager is None:
        _archive_manager = ArchiveManager()
    return _archive_manager


if __name__ == '__main__':
    # 测试代码
    manager = get_archive_manager()
    print(f"支持的格式：{manager.get_supported_extensions()}")
    
    if len(sys.argv) > 1:
        archive = sys.argv[1]
        if manager.is_archive(archive):
            entries = manager.read_entries(archive)
            print(f"\n压缩包内容 ({len(entries)} 个文件):")
            for entry in entries:
                type_str = "目录" if entry.is_directory else "文件"
                print(f"  {type_str}: {entry.full_path} ({entry.size} 字节)")

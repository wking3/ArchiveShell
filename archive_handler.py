"""
ArchiveShell - 压缩文件浏览处理器
用于在资源管理器中打开和浏览压缩文件
"""

import os
import sys
import tempfile
import shutil
import subprocess
import hashlib
from datetime import datetime

from archive_parser import get_archive_manager


class ArchiveBrowser:
    """压缩文件浏览器"""
    
    def __init__(self, archive_path: str):
        self.archive_path = os.path.abspath(archive_path)
        self.manager = get_archive_manager()
        self.temp_dir = None
    
    def is_supported(self) -> bool:
        """检查是否为支持的压缩格式"""
        return self.manager.is_archive(self.archive_path)
    
    def get_cache_dir(self) -> str:
        """获取或创建缓存目录"""
        if self.temp_dir is None:
            # 生成唯一的缓存目录名
            archive_name = os.path.splitext(os.path.basename(self.archive_path))[0]
            hash_key = hashlib.md5(self.archive_path.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            temp_base = tempfile.gettempdir()
            self.temp_dir = os.path.join(
                temp_base,
                f"ArchiveShell_{archive_name}_{hash_key}_{timestamp}"
            )
            os.makedirs(self.temp_dir, exist_ok=True)
        
        return self.temp_dir
    
    def extract_all(self) -> str:
        """解压所有文件到临时目录，返回目录路径"""
        if not self.is_supported():
            raise ValueError(f"不支持的压缩格式：{self.archive_path}")
        
        cache_dir = self.get_cache_dir()
        entries = self.manager.read_entries(self.archive_path)
        
        print(f"解压压缩包：{self.archive_path}")
        print(f"目标目录：{cache_dir}")
        print(f"文件数量：{len(entries)}")
        
        for entry in entries:
            if not entry.is_directory:
                try:
                    dest_path = os.path.join(cache_dir, entry.full_path.replace('/', os.sep))
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    data = self.manager.extract_file_to_stream(self.archive_path, entry.full_path)
                    if data:
                        with open(dest_path, 'wb') as f:
                            f.write(data)
                        print(f"  ✓ {entry.full_path}")
                    else:
                        print(f"  ✗ {entry.full_path} (提取失败)")
                except Exception as e:
                    print(f"  ✗ {entry.full_path}: {e}")
        
        return cache_dir
    
    def open_in_explorer(self):
        """在资源管理器中打开解压后的目录"""
        try:
            cache_dir = self.extract_all()
            # 使用资源管理器打开目录
            subprocess.run(['explorer.exe', cache_dir], check=True)
            print(f"\n已在资源管理器中打开：{cache_dir}")
            print("\n注意：临时文件将在程序退出后自动清理")
            return True
        except Exception as e:
            print(f"打开资源管理器失败：{e}")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"已清理临时目录：{self.temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败：{e}")
    
    def __del__(self):
        self.cleanup()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python archive_handler.py <压缩文件路径>")
        print("      python archive_handler.py list <压缩文件路径> - 列出文件")
        sys.exit(1)
    
    # 检查是否是 list 命令
    if len(sys.argv) >= 3 and sys.argv[1].lower() == 'list':
        archive_path = sys.argv[2]
        manager = get_archive_manager()
        
        if not manager.is_archive(archive_path):
            print(f"不支持的压缩格式：{archive_path}")
            sys.exit(1)
        
        entries = manager.read_entries(archive_path)
        print(f"\n压缩包内容 ({len(entries)} 个文件):\n")
        print(f"{'类型':<6} {'大小':>12} {'压缩后':>12} {'文件名'}")
        print("-" * 60)
        
        for entry in entries:
            type_str = "[DIR]" if entry.is_directory else "[FILE]"
            size_str = "-" if entry.is_directory else f"{entry.size:>12}"
            comp_str = "-" if entry.is_directory else f"{entry.compressed_size:>12}"
            print(f"{type_str:<6} {size_str} {comp_str} {entry.full_path}")
        
        return
    
    # 默认：在资源管理器中打开
    archive_path = sys.argv[1]
    
    if not os.path.exists(archive_path):
        print(f"文件不存在：{archive_path}")
        sys.exit(1)
    
    browser = ArchiveBrowser(archive_path)
    
    if not browser.is_supported():
        print(f"不支持的压缩格式：{archive_path}")
        print(f"支持的格式：{browser.manager.get_supported_extensions()}")
        sys.exit(1)
    
    browser.open_in_explorer()
    
    # 保持程序运行，让用户知道可以关闭
    print("\n按 Enter 键退出...")
    input()


if __name__ == '__main__':
    main()

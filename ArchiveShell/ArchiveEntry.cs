using System;
using System.Runtime.InteropServices;

namespace ArchiveShell
{
    /// <summary>
    /// 压缩包文件条目信息
    /// </summary>
    [ComVisible(true)]
    [Guid("E1A2B3C4-D5E6-F789-0123-456789ABCDEF")]
    public class ArchiveEntry
    {
        public string Name { get; set; } = string.Empty;
        public string FullPath { get; set; } = string.Empty;
        public long Size { get; set; }
        public long CompressedSize { get; set; }
        public DateTime LastModified { get; set; }
        public bool IsDirectory { get; set; }
        public uint Attributes { get; set; }
        public int Crc { get; set; }

        public ArchiveEntry() { }

        public ArchiveEntry Clone()
        {
            return new ArchiveEntry
            {
                Name = this.Name,
                FullPath = this.FullPath,
                Size = this.Size,
                CompressedSize = this.CompressedSize,
                LastModified = this.LastModified,
                IsDirectory = this.IsDirectory,
                Attributes = this.Attributes,
                Crc = this.Crc
            };
        }
    }
}

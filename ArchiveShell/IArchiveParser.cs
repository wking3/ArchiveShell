using System;
using System.Collections.Generic;
using System.IO;

namespace ArchiveShell
{
    /// <summary>
    /// 压缩文件解析器接口
    /// </summary>
    public interface IArchiveParser
    {
        /// <summary>
        /// 是否支持该文件格式
        /// </summary>
        bool IsSupported(string filePath);

        /// <summary>
        /// 读取压缩包内的文件列表
        /// </summary>
        List<ArchiveEntry> ReadEntries(string archivePath);

        /// <summary>
        /// 提取文件到指定路径
        /// </summary>
        void ExtractFile(string archivePath, string entryPath, string destinationPath);

        /// <summary>
        /// 获取压缩包内文件的流
        /// </summary>
        Stream ExtractFileToStream(string archivePath, string entryPath);
    }
}

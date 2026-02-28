# ArchiveShell

[![Release](https://img.shields.io/github/v/release/wking3/ArchiveShell)](https://github.com/wking3/ArchiveShell/releases)
[![License](https://img.shields.io/github/license/wking3/ArchiveShell)](LICENSE)

让 Windows 资源管理器像打开 ZIP 文件一样直接浏览 7z 和 RAR 压缩包内容。

## 功能特性

- ✅ 双击 7z/RAR 文件直接在资源管理器中浏览
- ✅ 支持复制/粘贴压缩包内文件
- ✅ 支持拖拽操作
- ✅ 显示压缩包内文件详细信息
- ✅ 支持子文件夹浏览
- ✅ 右键菜单快速访问

## 系统要求

- Windows 10/11 (64 位)
- Python 3.8+ (64 位)
- 管理员权限

## 快速开始

### 方式一：使用已编译的可执行文件

从 [releases](链接) 下载最新版本的 `ArchiveShell.exe`，无需安装 Python 环境。

### 方式二：从源码运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 安装 Shell 扩展

**方法 A: 使用批处理脚本（推荐）**

```bash
# 右键以管理员身份运行
install.bat
```

**方法 B: 使用 Python 脚本**

```bash
# 以管理员身份运行命令提示符
python register.py install
```

**方法 C: 使用图形界面**

```bash
python installer_gui.py
```

### 3. 使用

安装完成后：
- **双击** 7z/RAR 文件即可在资源管理器中浏览
- **右键** 点击压缩文件，选择"浏览压缩包"

### 4. 卸载

```bash
# 以管理员身份运行
python register.py uninstall
```

或运行：
```bash
uninstall.bat
```

## 打包成可执行文件

如果你想要生成独立的 `.exe` 文件（无需 Python 环境）：

```bash
# 运行打包脚本
python build.py

# 或使用批处理脚本
build_onefile.bat
```

生成的文件在 `dist/` 目录：
- `ArchiveShell.exe` - 主程序
- `ArchiveShell_Installer.exe` - 命令行安装程序
- `ArchiveShell_GUI.exe` - 图形化安装程序

## 项目结构

```
compress/
├── archive_parser.py      # 压缩文件解析器 (7z/RAR)
├── archive_shell.py       # Shell 命名空间扩展核心
├── archive_handler.py     # 压缩文件浏览处理器
├── register.py            # 注册表注册/注销脚本
├── installer_gui.py       # 图形化安装程序
├── build.py               # PyInstaller 打包脚本
├── build.bat              # 打包批处理脚本
├── build_onefile.bat      # 一键打包脚本
├── install.bat            # 一键安装脚本
├── uninstall.bat          # 一键卸载脚本
├── requirements.txt       # Python 依赖
├── *.spec                 # PyInstaller 配置文件
└── README.md              # 说明文档
```

## 技术说明

### 工作原理

由于 Windows Shell Namespace Extension 的完整实现较为复杂，本程序采用了一种实用的方法：

1. **文件关联**: 注册 7z/RAR 文件与处理程序的关联
2. **临时解压**: 双击文件时，将压缩包内容解压到临时目录
3. **资源管理器打开**: 在资源管理器中打开临时目录
4. **自动清理**: 程序退出后自动清理临时文件

### 支持的格式

| 格式 | 扩展名 | 库 |
|------|--------|-----|
| 7z   | .7z    | py7zr |
| RAR  | .rar, .rar4, .rar5 | rarfile |

### 依赖库

- **py7zr**: 7z 格式读写
- **rarfile**: RAR 格式读取（需要 unar 或 unrar 命令行工具）
- **comtypes**: COM 接口支持
- **pywin32**: Windows API 访问

## 故障排除

### 问题：双击文件没有反应

**解决方案：**
1. 确认已以管理员权限运行安装脚本
2. 检查注册表是否正确注册
3. 尝试重启资源管理器

### 问题：RAR 文件无法打开

**解决方案：**
1. 安装 unar 或 unrar 命令行工具
2. 从 https://theunarchiver.com/ 下载 unar
3. 或将 unar.exe 添加到系统 PATH

### 问题：Python 依赖安装失败

**解决方案：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 注意事项

⚠️ **安全提示**: 
- 临时文件存储在系统临时目录
- 敏感文件使用后请及时清理
- 不要打开来源不明的压缩包

⚠️ **性能提示**:
- 大型压缩包解压可能需要较长时间
- 临时文件会占用磁盘空间
- 建议定期清理临时目录

## 开发说明

### 添加新格式支持

1. 在 `archive_parser.py` 中添加新的解析器类
2. 继承 `ArchiveParser` 基类
3. 实现 `read_entries()` 和 `extract_file()` 方法
4. 在 `ArchiveManager` 中注册新解析器

### 调试

```bash
# 列出压缩包内容
python archive_handler.py list test.7z

# 查看详细日志
python -u archive_handler.py test.7z
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

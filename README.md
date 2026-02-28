# ArchiveShell

[![Release](https://img.shields.io/github/v/release/wking3/ArchiveShell)](https://github.com/wking3/ArchiveShell/releases)
[![License](https://img.shields.io/github/license/wking3/ArchiveShell)](LICENSE)

让 Windows 资源管理器像打开 ZIP 文件一样直接浏览 7z 和 RAR 压缩包内容。

## 功能特性

### 基础功能
- ✅ 双击 7z/RAR 文件直接在资源管理器中浏览
- ✅ 支持复制/粘贴压缩包内文件
- ✅ 支持拖拽操作
- ✅ 显示压缩包内文件详细信息
- ✅ 支持子文件夹浏览

### Shell 扩展功能 (完整版)
- ✅ Windows Shell Namespace Extension 实现
- ✅ IShellFolder 接口
- ✅ IEnumIDList 接口
- ✅ IContextMenu 右键菜单
- ✅ IExtractImage 图标提取
- ✅ 注册表自动注册

## 系统要求

- Windows 10/11 (64 位)
- Python 3.8+ (64 位)
- 管理员权限（用于注册 Shell 扩展）

## 快速开始

### 方式一：使用已编译的可执行文件

从 [Releases](https://github.com/wking3/ArchiveShell/releases) 下载最新版本的 `ArchiveShell.zip`。

### 方式二：从源码安装

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 注册 Shell 扩展

**以管理员身份运行：**

```bash
# 方法 1: 使用 Python 脚本
python shell_extension.py install

# 方法 2: 使用批处理
register_shell.bat
```

#### 3. 使用

安装完成后：
- **双击** 7z/RAR 文件即可在资源管理器中浏览
- **右键** 点击压缩文件，选择"浏览压缩包"

#### 4. 卸载

```bash
# 以管理员身份运行
python shell_extension.py uninstall
```

## 打包成可执行文件

生成独立的 `.exe` 文件（无需 Python 环境）：

```bash
# 运行打包脚本
python build.py

# 或使用批处理
build_onefile.bat
```

生成的文件在 `dist/` 目录：
- `ArchiveShell.exe` - 主程序 (约 12 MB)
- `ArchiveShell_Installer.exe` - 命令行安装程序
- `ArchiveShell_GUI.exe` - 图形化安装程序

## 项目结构

```
compress/
├── archive_parser.py       # 压缩文件解析器 (7z/RAR)
├── archive_handler.py      # 压缩文件浏览处理器
├── archive_shell.py        # Shell 命名空间扩展核心
├── shell_extension.py      # Shell 扩展注册脚本
├── shell_extension_full.py # 完整 Shell 扩展实现
├── register.py             # 基础注册表注册
├── register_com.py         # COM 服务器注册
├── register_shell.bat      # Shell 扩展注册批处理
├── build.py                # PyInstaller 打包脚本
├── installer_gui.py        # 图形化安装程序
├── install.bat             # 一键安装脚本
├── uninstall.bat           # 一键卸载脚本
├── requirements.txt        # Python 依赖
└── README.md               # 说明文档
```

## 技术说明

### Shell Namespace Extension 实现

本项目实现了完整的 Windows Shell Namespace Extension，包含以下核心组件：

1. **IShellFolder 接口** - 核心文件夹接口
   - `ParseDisplayName` - 解析显示名称为 PIDL
   - `EnumObjects` - 枚举文件夹内容
   - `BindToObject` - 绑定到子对象
   - `GetAttributesOf` - 获取文件属性
   - `GetDisplayNameOf` - 获取显示名称

2. **IEnumIDList 接口** - 枚举器
   - `Next` - 获取下一个 PIDL
   - `Skip` - 跳过指定数量
   - `Reset` - 重置枚举器
   - `Clone` - 克隆枚举器

3. **IPersistFolder2 接口** - 持久化文件夹
   - `Initialize` - 初始化文件夹
   - `GetCurFolder` - 获取当前文件夹 PIDL

4. **IContextMenu 接口** - 右键菜单
   - `QueryContextMenu` - 添加菜单项
   - `InvokeCommand` - 执行菜单命令

5. **IExtractImage 接口** - 图标提取
   - `GetLocation` - 获取图标位置
   - `Extract` - 提取图标

### 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                  Windows 资源管理器                       │
├─────────────────────────────────────────────────────────┤
│  Shell Namespace Extension (IShellFolder)               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ArchiveShellFolder                              │   │
│  │  ├─ IShellFolder                                 │   │
│  │  ├─ IEnumIDList                                  │   │
│  │  ├─ IPersistFolder2                              │   │
│  │  └─ IContextMenu                                 │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ArchiveParser                                          │
│  ├─ SevenZipParser (py7zr)                              │
│  └─ RarParser (rarfile)                                 │
├─────────────────────────────────────────────────────────┤
│  临时解压目录 (Temp Folder)                              │
│  └─ 压缩包内容 (解压后可直接访问)                         │
└─────────────────────────────────────────────────────────┘
```

### 支持的格式

| 格式 | 扩展名 | 库 |
|------|--------|-----|
| 7z   | .7z    | py7zr |
| RAR  | .rar, .rar4, .rar5 | rarfile |

### 依赖库

- **py7zr** - 7z 格式读写
- **rarfile** - RAR 格式读取（需要 unar 或 unrar）
- **comtypes** - COM 接口支持
- **pywin32** - Windows API 访问
- **pyinstaller** - 打包工具

## 故障排除

### 问题：双击文件没有反应

**解决方案：**
1. 确认已以管理员权限运行安装脚本
2. 重启 Windows 资源管理器
3. 右键选择"浏览压缩包"

### 问题：RAR 文件无法打开

**解决方案：**
1. 安装 unar：https://theunarchiver.com/
2. 或将 unar.exe 添加到系统 PATH

### 问题：Python 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --force-reinstall
```

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

# 注册 Shell 扩展
python shell_extension.py install

# 查看注册表
regedit HKEY_CLASSES_ROOT\.7z
```

## 相关资源

- [Microsoft Docs: Shell Namespace Extensions](https://docs.microsoft.com/en-us/windows/win32/shell/namespace-extensions)
- [Microsoft Docs: IShellFolder Interface](https://docs.microsoft.com/en-us/windows/win32/api/shlobj_core/nn-shlobj_core-ishellfolder)
- [GitHub: py7zr](https://github.com/miurahr/py7zr)
- [GitHub: rarfile](https://github.com/markokr/rarfile)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

感谢以下开源项目：
- [py7zr](https://github.com/miurahr/py7zr)
- [rarfile](https://github.com/markokr/rarfile)
- [SharpShell](https://github.com/dwmkerr/sharpshell)

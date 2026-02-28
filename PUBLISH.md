# ArchiveShell 发布说明

## 发布流程

### 方法一：使用 GitHub Actions（推荐）

1. 推送版本标签：
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. GitHub Actions 会自动构建并发布

### 方法二：本地构建发布

1. 安装依赖：
```bash
pip install -r requirements.txt
pip install PyGithub
```

2. 构建可执行文件：
```bash
python build.py
```

3. 发布到 GitHub：
```bash
# 使用命令行参数
publish.bat <GitHub_Token> v1.0.0

# 或使用环境变量
set GITHUB_TOKEN=your_token
publish.bat v1.0.0
```

## 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo`（完整仓库权限）
4. 生成并复制 token

## 手动上传 Release

如果不想使用脚本，可以手动操作：

1. 访问 https://github.com/wking3/ArchiveShell/releases
2. 点击 "Create a new release"
3. 输入版本号（如 v1.0.0）
4. 上传文件：
   - ArchiveShell.zip
   - ArchiveShell.exe
   - ArchiveShell_Installer.exe
   - ArchiveShell_GUI.exe
5. 点击 "Publish release"

## 文件清单

发布时应包含以下文件：

| 文件 | 说明 |
|------|------|
| `ArchiveShell.zip` | 完整发布包（包含所有文件和说明） |
| `ArchiveShell.exe` | 主程序（独立可执行） |
| `ArchiveShell_Installer.exe` | 命令行安装程序 |
| `ArchiveShell_GUI.exe` | 图形化安装程序 |

## 版本命名

遵循语义化版本规范：
- `v1.0.0` - 主版本.次版本.修订版
- `v1.0.0-beta.1` - 测试版
- `v1.0.0-rc.1` - 候选发布版

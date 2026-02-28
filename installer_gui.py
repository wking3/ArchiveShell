"""
ArchiveShell - 图形化安装程序
"""

import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class InstallerApp:
    """安装程序 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ArchiveShell 安装程序")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 检查管理员权限
        if not is_admin():
            self.show_admin_warning()
            return
        
        self.create_widgets()
        self.check_dependencies()
    
    def show_admin_warning(self):
        """显示管理员权限警告"""
        result = messagebox.askyesno(
            "需要管理员权限",
            "ArchiveShell 需要管理员权限来注册 Shell 扩展。\n\n"
            "是否以管理员身份重新运行？"
        )
        if result:
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, __file__, None, 1
                )
            except Exception:
                pass
        self.root.destroy()
    
    def create_widgets(self):
        """创建 GUI 组件"""
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="ArchiveShell",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Windows 资源管理器 7z/RAR 浏览扩展",
            font=("Microsoft YaHei UI", 9)
        )
        subtitle_label.pack()
        
        # 分隔线
        ttk.Separator(self.root).pack(fill=tk.X, padx=10)
        
        # 状态区域
        status_frame = ttk.LabelFrame(self.root, text="状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=10,
            font=("Consolas", 9),
            state='disabled'
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.install_btn = ttk.Button(
            button_frame,
            text="安装",
            command=self.install,
            width=10
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.uninstall_btn = ttk.Button(
            button_frame,
            text="卸载",
            command=self.uninstall,
            width=10
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)
        
        self.exit_btn = ttk.Button(
            button_frame,
            text="退出",
            command=self.root.quit,
            width=10
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # 依赖状态
        self.dep_label = ttk.Label(
            self.root,
            text="",
            font=("Microsoft YaHei UI", 8)
        )
        self.dep_label.pack(pady=(0, 10))
    
    def log(self, message):
        """添加日志"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def check_dependencies(self):
        """检查依赖"""
        missing = []
        
        try:
            import py7zr
            self.log("✓ py7zr 已安装")
        except ImportError:
            missing.append("py7zr")
            self.log("✗ py7zr 未安装")
        
        try:
            import rarfile
            self.log("✓ rarfile 已安装")
        except ImportError:
            missing.append("rarfile")
            self.log("✗ rarfile 未安装")
        
        try:
            import comtypes
            self.log("✓ comtypes 已安装")
        except ImportError:
            missing.append("comtypes")
            self.log("✗ comtypes 未安装")
        
        if missing:
            self.dep_label.config(
                text=f"缺少依赖：{', '.join(missing)}\n请运行：pip install -r requirements.txt",
                foreground="red"
            )
        else:
            self.dep_label.config(
                text="所有依赖已就绪",
                foreground="green"
            )
    
    def run_command(self, command, args):
        """运行命令并输出日志"""
        self.progress.start()
        self.install_btn.config(state='disabled')
        self.uninstall_btn.config(state='disabled')
        
        def run():
            try:
                cmd = [sys.executable, command] + args
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                for line in process.stdout:
                    self.root.after(0, lambda l=line: self.log(l.strip()))
                
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.log("操作完成!"))
                    self.root.after(0, lambda: messagebox.showinfo("成功", "操作已成功完成!"))
                else:
                    self.root.after(0, lambda: self.log(f"操作失败，返回码：{process.returncode}"))
                    self.root.after(0, lambda: messagebox.showerror("错误", f"操作失败，返回码：{process.returncode}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"错误：{e}"))
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
            finally:
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.install_btn.config(state='normal'))
                self.root.after(0, lambda: self.uninstall_btn.config(state='normal'))
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def install(self):
        """执行安装"""
        self.log("=" * 40)
        self.log("开始安装...")
        self.run_command("register.py", ["install"])
    
    def uninstall(self):
        """执行卸载"""
        self.log("=" * 40)
        self.log("开始卸载...")
        self.run_command("register.py", ["uninstall"])


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置图标（如果有的话）
    try:
        root.iconbitmap("icon.ico")
    except Exception:
        pass
    
    app = InstallerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

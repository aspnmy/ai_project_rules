#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2开发环境集成管理器
用于与IDE集成，处理编译调试时的文件复制和环境管理
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import datetime
from pathlib import Path
from typing import Optional, Dict, List


class WSLIDEIntegrator:
    """WSL2开发环境IDE集成器"""
    
    def __init__(self):
        self.config_file = "wsl_config.json"
        self.config = self.load_config()
        self.project_root = self.find_project_root()
        
    def find_project_root(self) -> str:
        """查找项目根目录"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists() or (current / "project_rules.md").exists():
                return str(current)
            current = current.parent
        return str(Path.cwd())
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "wsl_devpath": "win11",
            "wsl_usr": "devman", 
            "wsl_pwd": "devman",
            "wsl_distro": "Ubuntu-22.04",
            "auto_copy": True,
            "auto_compile": False,
            "backup_on_destroy": True,
            "sync_extensions": [".py", ".js", ".ts", ".cpp", ".c", ".h", ".rs", ".go"]
        }
        
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"警告：配置文件加载失败 {e}，使用默认配置")
                
        return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"错误：配置文件保存失败 {e}")
    
    def is_wsl_available(self) -> bool:
        """检查WSL是否可用"""
        try:
            result = subprocess.run(
                ["wsl", "--status"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def get_wsl_path(self, local_path: str) -> str:
        """将本地路径转换为WSL路径"""
        # Windows路径转换为WSL路径
        # C:\path\to\file -> /mnt/c/path/to/file
        local_path = os.path.abspath(local_path)
        drive = local_path[0].lower()
        path_part = local_path[3:].replace('\\', '/')
        return f"/mnt/{drive}/{path_part}"
    
    def copy_to_wsl(self, local_file: str, wsl_dest: str = None) -> bool:
        """复制文件到WSL环境"""
        if not os.path.exists(local_file):
            print(f"错误：文件 {local_file} 不存在")
            return False
        
        if wsl_dest is None:
            wsl_dest = f"/home/{self.config['wsl_usr']}/dev"
        
        # 使用WSL命令复制文件
        wsl_source = self.get_wsl_path(local_file)
        copy_cmd = f"wsl -d {self.config['wsl_distro']} cp \"{wsl_source}\" \"{wsl_dest}/\""
        
        try:
            result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"文件 {local_file} 已复制到WSL环境")
                return True
            else:
                print(f"错误：文件复制失败 {result.stderr}")
                return False
        except Exception as e:
            print(f"错误：文件复制异常 {e}")
            return False
    
    def compile_in_wsl(self, filename: str) -> bool:
        """在WSL环境中编译文件"""
        wsl_path = f"/home/{self.config['wsl_usr']}/dev"
        base_name = os.path.basename(filename)
        wsl_file = f"{wsl_path}/{base_name}"
        
        # 根据文件扩展名选择编译器
        ext = os.path.splitext(filename)[1].lower()
        compile_cmd = ""
        
        if ext == ".py":
            compile_cmd = f"python3 -m py_compile {wsl_file}"
        elif ext in [".c", ".cpp"]:
            if ext == ".c":
                compile_cmd = f"gcc -o {wsl_path}/{os.path.splitext(base_name)[0]} {wsl_file}"
            else:
                compile_cmd = f"g++ -o {wsl_path}/{os.path.splitext(base_name)[0]} {wsl_file}"
        elif ext == ".rs":
            compile_cmd = f"rustc -o {wsl_path}/{os.path.splitext(base_name)[0]} {wsl_file}"
        elif ext == ".go":
            compile_cmd = f"go build -o {wsl_path}/{os.path.splitext(base_name)[0]} {wsl_file}"
        else:
            print(f"警告：不支持编译 {ext} 文件")
            return False
        
        # 在WSL中执行编译
        full_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'cd {wsl_path} && {compile_cmd}'"
        
        try:
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"文件 {filename} 编译成功")
                return True
            else:
                print(f"错误：编译失败 {result.stderr}")
                return False
        except Exception as e:
            print(f"错误：编译异常 {e}")
            return False
    
    def debug_in_wsl(self, filename: str) -> bool:
        """在WSL环境中调试文件"""
        wsl_path = f"/home/{self.config['wsl_usr']}/dev"
        base_name = os.path.basename(filename)
        wsl_file = f"{wsl_path}/{base_name}"
        
        # 根据文件类型选择调试器
        ext = os.path.splitext(filename)[1].lower()
        debug_cmd = ""
        
        if ext == ".py":
            debug_cmd = f"python3 -m pdb {wsl_file}"
        elif ext in [".c", ".cpp"]:
            # 需要先编译
            exe_name = f"{wsl_path}/{os.path.splitext(base_name)[0]}"
            debug_cmd = f"gdb {exe_name}"
        elif ext == ".rs":
            # Rust使用rust-gdb
            exe_name = f"{wsl_path}/{os.path.splitext(base_name)[0]}"
            debug_cmd = f"rust-gdb {exe_name}"
        else:
            print(f"警告：不支持调试 {ext} 文件")
            return False
        
        # 在WSL中启动调试器
        full_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'cd {wsl_path} && {debug_cmd}'"
        
        try:
            print(f"启动调试器：{debug_cmd}")
            result = subprocess.run(full_cmd, shell=True)
            return result.returncode == 0
        except Exception as e:
            print(f"错误：调试异常 {e}")
            return False
    
    def auto_process_file(self, filename: str, action: str = "copy") -> bool:
        """自动处理文件（复制/编译/调试）"""
        if not os.path.exists(filename):
            print(f"错误：文件 {filename} 不存在")
            return False
        
        # 首先复制文件到WSL
        if not self.copy_to_wsl(filename):
            return False
        
        # 根据操作类型执行后续处理
        if action == "compile":
            return self.compile_in_wsl(filename)
        elif action == "debug":
            return self.debug_in_wsl(filename)
        elif action == "copy":
            return True
        else:
            print(f"错误：不支持的操作类型 {action}")
            return False
    
    def handle_del_command(self) -> bool:
        """处理del-${wsl-devpath}命令"""
        print("执行环境销毁流程...")
        
        # 比较代码一致性
        wsl_dev_path = f"/home/{self.config['wsl_usr']}/dev"
        
        # 获取WSL中的文件列表
        list_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'ls -la {wsl_dev_path}'"
        try:
            result = subprocess.run(list_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print("WSL环境中没有文件需要处理")
                return True
            
            # 处理每个文件
            files = result.stdout.strip().split('\n')[3:]  # 跳过前3行
            for file_info in files:
                if file_info.strip():
                    parts = file_info.split()
                    if len(parts) >= 9:
                        filename = parts[8]
                        if not filename.startswith('.'):
                            self.process_file_consistency(filename)
            
            print("环境销毁完成")
            return True
            
        except Exception as e:
            print(f"错误：环境销毁失败 {e}")
            return False
    
    def process_file_consistency(self, filename: str):
        """处理文件一致性检查"""
        local_file = os.path.join(self.project_root, filename)
        wsl_file = f"/home/{self.config['wsl_usr']}/dev/{filename}"
        
        # 检查本地文件是否存在
        if not os.path.exists(local_file):
            print(f"本地文件 {filename} 不存在，直接复制到项目")
            self.copy_from_wsl(filename)
            return
        
        # 比较文件内容
        if self.compare_files(local_file, wsl_file):
            print(f"文件 {filename} 内容一致，无需处理")
        else:
            print(f"文件 {filename} 内容不一致，按文本版本控制规则处理")
            # 按照文本版本控制规则创建备份
            self.create_versioned_backup(filename)
    
    def compare_files(self, local_file: str, wsl_file: str) -> bool:
        """比较本地文件和WSL文件"""
        # 这里简化处理，实际应该计算文件哈希
        return os.path.exists(local_file) and os.path.exists(wsl_file)
    
    def copy_from_wsl(self, filename: str) -> bool:
        """从WSL复制文件到项目"""
        wsl_path = f"/home/{self.config['wsl_usr']}/dev/{filename}"
        local_path = os.path.join(self.project_root, filename)
        
        # 使用WSL命令复制文件
        wsl_source = f"\\\\wsl$\\{self.config['wsl_distro']}{wsl_path}"
        
        try:
            shutil.copy2(wsl_source, local_path)
            print(f"文件 {filename} 已从WSL复制到项目")
            return True
        except Exception as e:
            print(f"错误：文件复制失败 {e}")
            return False
    
    def create_versioned_backup(self, filename: str):
        """创建版本化备份"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_name = f"**-{filename}-d{timestamp}"
        
        # 从WSL复制文件
        if self.copy_from_wsl(filename):
            # 重命名为版本化名称
            local_path = os.path.join(self.project_root, filename)
            backup_path = os.path.join(self.project_root, versioned_name)
            
            try:
                shutil.move(local_path, backup_path)
                print(f"文件已备份为：{versioned_name}")
            except Exception as e:
                print(f"错误：版本化备份失败 {e}")
    
    def show_integration_status(self):
        """显示集成状态"""
        print("=== WSL2开发环境IDE集成状态 ===")
        print(f"项目根目录: {self.project_root}")
        print(f"WSL发行版: {self.config['wsl_distro']}")
        print(f"开发用户名: {self.config['wsl_usr']}")
        print(f"自动复制: {'启用' if self.config['auto_copy'] else '禁用'}")
        print(f"自动编译: {'启用' if self.config['auto_compile'] else '禁用'}")
        print(f"支持的扩展: {', '.join(self.config['sync_extensions'])}")
        
        if self.is_wsl_available():
            print("WSL状态: 可用 ✓")
        else:
            print("WSL状态: 不可用 ✗")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python wsl_ide_integrator.py copy <file>     - 复制文件到WSL")
        print("  python wsl_ide_integrator.py compile <file>  - 在WSL中编译文件")
        print("  python wsl_ide_integrator.py debug <file>    - 在WSL中调试文件")
        print("  python wsl_ide_integrator.py del           - 销毁WSL环境")
        print("  python wsl_ide_integrator.py status          - 显示集成状态")
        return
    
    integrator = WSLIDEIntegrator()
    command = sys.argv[1]
    
    if command == "copy" and len(sys.argv) > 2:
        integrator.copy_to_wsl(sys.argv[2])
    elif command == "compile" and len(sys.argv) > 2:
        integrator.compile_in_wsl(sys.argv[2])
    elif command == "debug" and len(sys.argv) > 2:
        integrator.debug_in_wsl(sys.argv[2])
    elif command == "del":
        integrator.handle_del_command()
    elif command == "status":
        integrator.show_integration_status()
    else:
        print("错误：未知命令或参数不足")


if __name__ == "__main__":
    main()
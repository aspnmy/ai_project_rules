#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2纯净开发环境管理器
用于管理Win11 WSL2开发环境的创建、使用、销毁等操作
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


class WSLDevManager:
    """WSL2开发环境管理器"""
    
    def __init__(self):
        self.config_file = "wsl_config.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "wsl_devpath": "win11",
            "wsl_usr": "devman", 
            "wsl_pwd": "devman",
            "wsl_distro": "Ubuntu-22.04",
            "project_path": os.getcwd(),
            "backup_path": "wsl_backups"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
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
            
    def run_command(self, cmd: str, capture_output: bool = True) -> tuple:
        """执行系统命令"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, shell=True)
                return result.returncode, "", ""
        except Exception as e:
            return -1, "", str(e)
    
    def check_wsl_installed(self) -> bool:
        """检查WSL是否已安装"""
        code, stdout, stderr = self.run_command("wsl --status")
        return code == 0
    
    def check_distro_installed(self) -> bool:
        """检查发行版是否已安装"""
        code, stdout, stderr = self.run_command("wsl --list --quiet")
        if code == 0:
            distros = stdout.strip().split('\n')
            return self.config["wsl_distro"] in distros
        return False
    
    def create_wsl_environment(self) -> bool:
        """创建WSL开发环境"""
        print(f"正在创建WSL2开发环境：{self.config['wsl_devpath']}")
        
        # 检查WSL是否已安装
        if not self.check_wsl_installed():
            print("错误：WSL未安装，请先安装WSL2")
            return False
        
        # 安装WSL发行版
        if not self.check_distro_installed():
            print(f"正在安装 {self.config['wsl_distro']}...")
            install_cmd = f"wsl --install -d {self.config['wsl_distro']}"
            code, stdout, stderr = self.run_command(install_cmd, capture_output=False)
            if code != 0:
                print(f"错误：安装发行版失败 {stderr}")
                return False
        
        # 设置开发环境目录
        wsl_path = f"/home/{self.config['wsl_usr']}/dev"
        setup_cmd = f"wsl -d {self.config['wsl_distro']} bash -c \""
        setup_cmd += f"sudo useradd -m -s /bin/bash {self.config['wsl_usr']} && "
        setup_cmd += f"echo '{self.config['wsl_usr']}:{self.config['wsl_pwd']}' | sudo chpasswd && "
        setup_cmd += f"sudo mkdir -p {wsl_path} && "
        setup_cmd += f"sudo chown {self.config['wsl_usr']}:{self.config['wsl_usr']} {wsl_path}"
        setup_cmd += "\""
        
        print("正在配置开发环境...")
        code, stdout, stderr = self.run_command(setup_cmd)
        if code != 0:
            print(f"警告：环境配置可能失败 {stderr}")
        
        print(f"WSL2开发环境创建成功：{self.config['wsl_devpath']}")
        return True
    
    def copy_file_to_wsl(self, filename: str) -> bool:
        """复制文件到WSL环境"""
        if not os.path.exists(filename):
            print(f"错误：文件 {filename} 不存在")
            return False
        
        wsl_path = f"/home/{self.config['wsl_usr']}/dev"
        dest_path = f"\\\\wsl$\\{self.config['wsl_distro']}{wsl_path}"
        
        # 确保WSL路径存在
        os.makedirs(dest_path, exist_ok=True)
        
        try:
            shutil.copy2(filename, os.path.join(dest_path, os.path.basename(filename)))
            print(f"文件 {filename} 已复制到WSL环境")
            return True
        except Exception as e:
            print(f"错误：文件复制失败 {e}")
            return False
    
    def compare_files(self, local_file: str, wsl_file: str) -> bool:
        """比较本地文件和WSL文件内容是否一致"""
        try:
            # 获取WSL文件路径
            wsl_path = f"\\\\wsl$\\{self.config['wsl_distro']}{wsl_file}"
            
            if not os.path.exists(local_file) or not os.path.exists(wsl_path):
                return False
            
            # 计算文件MD5
            def calculate_md5(filepath):
                hash_md5 = hashlib.md5()
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            
            local_md5 = calculate_md5(local_file)
            wsl_md5 = calculate_md5(wsl_path)
            
            return local_md5 == wsl_md5
        except Exception as e:
            print(f"错误：文件比较失败 {e}")
            return False
    
    def backup_wsl_file(self, filename: str) -> str:
        """备份WSL文件到项目，按照文本版本控制规则"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(filename)
        backup_name = f"**-{base_name}-d{timestamp}"
        
        wsl_path = f"\\\\wsl$\\{self.config['wsl_distro']}/home/{self.config['wsl_usr']}/dev/{base_name}"
        backup_path = os.path.join(self.config.get("backup_path", "wsl_backups"), backup_name)
        
        # 确保备份目录存在
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        try:
            shutil.copy2(wsl_path, backup_path)
            print(f"WSL文件已备份为：{backup_name}")
            return backup_path
        except Exception as e:
            print(f"错误：文件备份失败 {e}")
            return ""
    
    def destroy_wsl_environment(self) -> bool:
        """销毁WSL开发环境"""
        print(f"正在销毁WSL开发环境：{self.config['wsl_devpath']}")
        
        # 检查WSL环境中的文件
        wsl_dev_path = f"/home/{self.config['wsl_usr']}/dev"
        check_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'ls -la {wsl_dev_path}'"
        code, stdout, stderr = self.run_command(check_cmd)
        
        if code == 0:
            print("发现WSL环境中的文件：")
            print(stdout)
            
            # 备份重要文件
            files = stdout.strip().split('\n')[3:]  # 跳过前3行（总用量、.、..）
            for file_info in files:
                if file_info.strip():
                    parts = file_info.split()
                    if len(parts) >= 9:
                        filename = parts[8]
                        if not filename.startswith('.'):
                            print(f"正在备份文件：{filename}")
                            self.backup_wsl_file(filename)
        
        # 删除用户
        delete_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'sudo userdel -r {self.config['wsl_usr']}'"
        code, stdout, stderr = self.run_command(delete_cmd)
        
        if code == 0:
            print(f"WSL开发环境已销毁：{self.config['wsl_devpath']}")
            return True
        else:
            print(f"警告：环境销毁可能不完全 {stderr}")
            return False
    
    def restart_wsl_environment(self) -> bool:
        """重启WSL开发环境"""
        print(f"正在重启WSL开发环境：{self.config['wsl_devpath']}")
        
        # 停止WSL
        stop_cmd = "wsl --shutdown"
        code, stdout, stderr = self.run_command(stop_cmd)
        
        if code == 0:
            # 重新启动并检查环境
            check_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'ls -la /home/{self.config['wsl_usr']}/dev'"
            code, stdout, stderr = self.run_command(check_cmd)
            
            if code == 0:
                print(f"WSL开发环境已重启：{self.config['wsl_devpath']}")
                return True
            else:
                print(f"警告：环境检查失败 {stderr}")
                return False
        else:
            print(f"错误：WSL停止失败 {stderr}")
            return False
    
    def stop_wsl_environment(self) -> bool:
        """停用WSL开发环境"""
        print(f"正在停用WSL开发环境：{self.config['wsl_devpath']}")
        
        stop_cmd = "wsl --shutdown"
        code, stdout, stderr = self.run_command(stop_cmd)
        
        if code == 0:
            print(f"WSL开发环境已停用：{self.config['wsl_devpath']}")
            return True
        else:
            print(f"错误：WSL停用失败 {stderr}")
            return False
    
    def show_status(self):
        """显示环境状态"""
        print("=== WSL2开发环境状态 ===")
        print(f"环境名称: {self.config['wsl_devpath']}")
        print(f"用户名: {self.config['wsl_usr']}")
        print(f"发行版: {self.config['wsl_distro']}")
        print(f"项目路径: {self.config['project_path']}")
        
        # 检查WSL状态
        if self.check_wsl_installed():
            print("WSL状态: 已安装 ✓")
            
            if self.check_distro_installed():
                print(f"发行版状态: 已安装 ✓")
                
                # 检查开发环境目录
                check_cmd = f"wsl -d {self.config['wsl_distro']} bash -c 'ls -la /home/{self.config['wsl_usr']}/dev 2>/dev/null'"
                code, stdout, stderr = self.run_command(check_cmd)
                
                if code == 0:
                    print("开发环境: 已就绪 ✓")
                    print(f"环境文件:\n{stdout}")
                else:
                    print("开发环境: 未创建 ✗")
            else:
                print(f"发行版状态: 未安装 ✗")
        else:
            print("WSL状态: 未安装 ✗")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python wsl_dev_manager.py create          - 创建WSL开发环境")
        print("  python wsl_dev_manager.py copy <file>     - 复制文件到WSL环境")
        print("  python wsl_dev_manager.py destroy           - 销毁WSL开发环境")
        print("  python wsl_dev_manager.py restart         - 重启WSL开发环境")
        print("  python wsl_dev_manager.py stop            - 停用WSL开发环境")
        print("  python wsl_dev_manager.py status          - 显示环境状态")
        return
    
    manager = WSLDevManager()
    command = sys.argv[1]
    
    if command == "create":
        manager.create_wsl_environment()
    elif command == "copy" and len(sys.argv) > 2:
        manager.copy_file_to_wsl(sys.argv[2])
    elif command == "destroy":
        manager.destroy_wsl_environment()
    elif command == "restart":
        manager.restart_wsl_environment()
    elif command == "stop":
        manager.stop_wsl_environment()
    elif command == "status":
        manager.show_status()
    else:
        print("错误：未知命令或参数不足")


if __name__ == "__main__":
    main()
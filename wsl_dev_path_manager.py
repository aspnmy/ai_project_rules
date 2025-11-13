#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2开发环境路径管理器
用于管理不同系统环境下的开发路径
"""

import os
import sys
import json
from pathlib import Path

class WSLDevPathManager:
    """WSL2开发环境路径管理器"""
    
    def __init__(self, config_file="wsl_config.json"):
        self.script_dir = Path(__file__).parent.absolute()
        self.config_file = self.script_dir / config_file
        self.config = self.load_config()
        self.current_distro = self.get_current_distro()
    
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "wsl_usr": "devman",
            "wsl_distro": "Debian",
            "dev_paths": {
                "windows_container": "c:\\\\${wsl-usr}\\\\git_data\\\\${gitbranch}",
                "linux_wsl": "${HOME}/git_data/${gitbranch}",
                "windows_wsl": "/mnt/c/Users/${wsl-usr}/git_data/${gitbranch}"
            },
            "supported_distros": {
                "windows": ["win11", "win11l", "win7u", "win2025"],
                "linux": ["Debian", "Ubuntu", "CentOS", "Arch"]
            }
        }
    
    def get_current_distro(self):
        """获取当前系统版本"""
        distro_file = self.script_dir / "wsl-distro.info"
        if distro_file.exists():
            try:
                with open(distro_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # 查找wsl-distro配置
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('wsl-distro='):
                            return line.split('=')[1].strip()
                        elif line and not line.startswith('#'):
                            return line
            except:
                pass
        return self.config.get("wsl_distro", "Debian")
    
    def is_windows_distro(self, distro=None):
        """检查是否为Windows容器版本"""
        if distro is None:
            distro = self.current_distro
        windows_distros = self.config.get("supported_distros", {}).get("windows", [])
        return distro in windows_distros
    
    def get_dev_path(self, gitbranch="main", distro=None):
        """获取开发路径"""
        if distro is None:
            distro = self.current_distro
        
        wsl_usr = self.config.get("wsl_usr", "devman")
        
        if self.is_windows_distro(distro):
            # Windows容器环境
            path_template = self.config.get("dev_paths", {}).get("windows_container", 
                                                                "c:\\\\${wsl-usr}\\\\git_data\\\\${gitbranch}")
            return path_template.replace("${wsl-usr}", wsl_usr).replace("${gitbranch}", gitbranch)
        else:
            # Linux/WSL环境
            if self.is_wsl_environment():
                # 在WSL中
                path_template = self.config.get("dev_paths", {}).get("linux_wsl", 
                                                                    "${HOME}/git_data/${gitbranch}")
                home_dir = os.environ.get("HOME", "/home/devman")
                return path_template.replace("${HOME}", home_dir).replace("${gitbranch}", gitbranch)
            else:
                # 在Windows上通过WSL访问
                path_template = self.config.get("dev_paths", {}).get("windows_wsl", 
                                                                    "/mnt/c/Users/${wsl-usr}/git_data/${gitbranch}")
                return path_template.replace("${wsl-usr}", wsl_usr).replace("${gitbranch}", gitbranch)
    
    def is_wsl_environment(self):
        """检查是否在WSL环境中"""
        return os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop") or \
               os.environ.get("WSL_DISTRO_NAME") is not None
    
    def get_container_ports(self):
        """获取容器端口配置"""
        return self.config.get("container_ports", {
            "rdp": 4489,
            "http": 4818,
            "vnc": 4777
        })
    
    def get_podman_compose_files(self):
        """获取Podman配置文件优先级列表"""
        podman_config = self.config.get("podman_config", {})
        priority_files = podman_config.get("compose_files_priority", [
            "podman-win-wsl2",
            "podman-win-wsl2-compose.yml"
        ])
        
        script_dir = Path(__file__).parent.absolute()
        available_files = []
        
        for file_name in priority_files:
            file_path = script_dir / file_name
            if file_path.exists():
                available_files.append(str(file_path))
        
        return available_files
    
    def get_active_compose_file(self):
        """获取当前使用的compose文件"""
        available_files = self.get_podman_compose_files()
        return available_files[0] if available_files else None
    
    def get_environment_info(self, gitbranch="main"):
        """获取完整的环境信息"""
        info = {
            "current_distro": self.current_distro,
            "is_windows_distro": self.is_windows_distro(),
            "is_wsl_environment": self.is_wsl_environment(),
            "dev_path": self.get_dev_path(gitbranch),
            "container_ports": self.get_container_ports(),
            "wsl_usr": self.config.get("wsl_usr", "devman"),
            "wsl_pwd": self.config.get("wsl_pwd", "devman"),
            "available_compose_files": self.get_podman_compose_files(),
            "active_compose_file": self.get_active_compose_file()
        }
        
        if self.is_windows_distro():
            podman_config = self.config.get("podman_config", {})
            info.update({
                "container_name": f"windows-{self.current_distro}",
                "rdp_port": info["container_ports"]["rdp"],
                "http_port": info["container_ports"]["http"],
                "vnc_port": info["container_ports"]["vnc"],
                "docker_image_gateway": podman_config.get("docker_image_gateway", "https://gateway.cf.shdrr.org/"),
                "windows_image": podman_config.get("windows_image", "dockurr/windows")
            })
        
        return info
    
    def print_environment_info(self, gitbranch="main"):
        """打印环境信息"""
        info = self.get_environment_info(gitbranch)
        
        print("=" * 60)
        print("WSL2开发环境路径信息")
        print("=" * 60)
        print(f"当前系统版本: {info['current_distro']}")
        print(f"环境类型: {'Windows容器' if info['is_windows_distro'] else 'Linux/WSL环境'}")
        print(f"WSL环境: {'是' if info['is_wsl_environment'] else '否'}")
        print(f"开发路径: {info['dev_path']}")
        
        # 显示配置文件信息
        if info['available_compose_files']:
            print(f"\n可用配置文件:")
            for i, file_path in enumerate(info['available_compose_files'], 1):
                file_name = os.path.basename(file_path)
                if file_path == info['active_compose_file']:
                    print(f"  {i}. {file_name} ✓ (当前使用)")
                else:
                    print(f"  {i}. {file_name}")
        
        if info['is_windows_distro']:
            print(f"\n容器端口:")
            print(f"  RDP端口: {info['rdp_port']}")
            print(f"  HTTP端口: {info['http_port']}")
            print(f"  VNC端口: {info['vnc_port']}")
            print(f"\n镜像信息:")
            print(f"  Docker镜像网关: {info['docker_image_gateway']}")
            print(f"  Windows镜像: {info['windows_image']}")
            print(f"\n连接信息:")
            print(f"  用户名: {info['wsl_usr']}")
            print(f"  密码: {info['wsl_pwd']}")
        
        print("=" * 60)
    
    def create_dev_directory(self, gitbranch="main"):
        """创建开发目录"""
        dev_path = self.get_dev_path(gitbranch)
        
        try:
            # 根据环境类型创建目录
            if self.is_windows_distro():
                # Windows容器环境 - 需要在容器内创建
                print(f"Windows容器路径: {dev_path}")
                print("注意: Windows容器目录需要在容器内部创建")
                return True
            else:
                # Linux/WSL环境
                path_obj = Path(dev_path)
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"已创建开发目录: {dev_path}")
                return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认显示环境信息
        manager = WSLDevPathManager()
        manager.print_environment_info()
        return
    
    command = sys.argv[1]
    manager = WSLDevPathManager()
    
    if command == "path":
        gitbranch = sys.argv[2] if len(sys.argv) > 2 else "main"
        print(manager.get_dev_path(gitbranch))
    elif command == "info":
        gitbranch = sys.argv[2] if len(sys.argv) > 2 else "main"
        manager.print_environment_info(gitbranch)
    elif command == "create":
        gitbranch = sys.argv[2] if len(sys.argv) > 2 else "main"
        manager.create_dev_directory(gitbranch)
    elif command == "check":
        distro = sys.argv[2] if len(sys.argv) > 2 else manager.current_distro
        print(f"系统版本: {distro}")
        print(f"是否Windows容器: {manager.is_windows_distro(distro)}")
        print(f"是否WSL环境: {manager.is_wsl_environment()}")
    else:
        print("用法:")
        print("  python wsl_dev_path_manager.py          - 显示环境信息")
        print("  python wsl_dev_path_manager.py path [branch] - 获取开发路径")
        print("  python wsl_dev_path_manager.py info [branch]  - 显示详细信息")
        print("  python wsl_dev_path_manager.py create [branch] - 创建开发目录")
        print("  python wsl_dev_path_manager.py check [distro] - 检查系统类型")

if __name__ == "__main__":
    main()
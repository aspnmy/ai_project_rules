#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Podman Windows容器环境安装脚本
用于在WSL2环境中安装和配置Windows开发容器
"""

import os
import sys
import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

class Colors:
    """终端颜色输出"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class PodmanWindowsInstaller:
    """Podman Windows容器安装器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.config_file = self.script_dir / "wsl-distro.info"
        self.podman_compose_file = self.script_dir / "podman-win-wsl2"
        self.container_uuid_file = self.script_dir / ".container_uuid"
        self.compose_file_path = self.script_dir / ".compose_file"
        self.download_gateway_file = self.script_dir / "download-gateway"
        self.dockerimage_gateway_file = self.script_dir / "dockerimage-gateway"
        
        # 默认配置
        self.wsl_distro = "Debian"
        self.wsl_usr = "devman"
        self.wsl_pwd = "devman"
        self.uuid = ""
        self.download_gateway = "gateway.cf.shdrr.org"
        self.dockerimage_gateway = "drrpull.shdrr.org"
        
        # 支持的Windows版本
        self.windows_distros = ["win11", "win11l", "win7u", "win2025"]
    
    def log_info(self, message):
        """输出信息日志"""
        print(f"{Colors.BLUE}{message}{Colors.NC}")
    
    def log_success(self, message):
        """输出成功日志"""
        print(f"{Colors.GREEN}{message}{Colors.NC}")
    
    def log_warning(self, message):
        """输出警告日志"""
        print(f"{Colors.YELLOW}{message}{Colors.NC}")
    
    def log_error(self, message):
        """输出错误日志"""
        print(f"{Colors.RED}{message}{Colors.NC}")
    
    def load_gateway_domains(self):
        """读取网关域名配置"""
        # 读取下载网关域名
        if self.download_gateway_file.exists():
            try:
                with open(self.download_gateway_file, 'r', encoding='utf-8') as f:
                    gateway = f.read().strip().split('\n')[0].strip()
                    if gateway:
                        self.download_gateway = gateway
                        self.log_success(f"下载网关域名: {self.download_gateway}")
            except Exception as e:
                self.log_warning(f"读取下载网关域名失败: {e}，使用默认值: {self.download_gateway}")
        else:
            self.log_info(f"使用默认下载网关域名: {self.download_gateway}")
        
        # 读取Docker镜像网关域名
        if self.dockerimage_gateway_file.exists():
            try:
                with open(self.dockerimage_gateway_file, 'r', encoding='utf-8') as f:
                    gateway = f.read().strip().split('\n')[0].strip()
                    if gateway:
                        self.dockerimage_gateway = gateway
                        self.log_success(f"Docker镜像网关域名: {self.dockerimage_gateway}")
            except Exception as e:
                self.log_warning(f"读取Docker镜像网关域名失败: {e}，使用默认值: {self.dockerimage_gateway}")
        else:
            self.log_info(f"使用默认Docker镜像网关域名: {self.dockerimage_gateway}")
        
        # 设置环境变量
        os.environ['DOWNLOAD_GATEWAY'] = self.download_gateway
        os.environ['DOCKERIMAGE_GATEWAY'] = self.dockerimage_gateway
    
    def load_config(self):
        """读取配置文件"""
        if self.config_file.exists():
            self.log_info(f"正在读取配置文件: {self.config_file}")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # 查找wsl-distro配置
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('wsl-distro='):
                            self.wsl_distro = line.split('=')[1].strip()
                            break
                        elif line and not line.startswith('#'):
                            # 如果没有wsl-distro=格式，直接读取第一行非注释内容
                            self.wsl_distro = line
                            break
                    
                    self.log_success(f"配置的系统版本: {self.wsl_distro}")
            except Exception as e:
                self.log_warning(f"读取配置文件失败: {e}，使用默认值: {self.wsl_distro}")
        else:
            self.log_warning(f"配置文件不存在，使用默认值: {self.wsl_distro}")
    
    def is_valid_compose_file(self, file_path):
        """检查是否为有效的compose文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查是否包含必要的YAML结构
                return 'version:' in content and 'services:' in content
        except:
            return False
    
    def generate_compose_file(self, source_file, output_file):
        """生成完整的compose文件"""
        self.log_info(f"正在生成完整的podman-compose文件: {output_file}")
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            compose_content = f"""# 自动生成的Podman Compose文件
# 基于: {source_file}
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

version: '3.8'

services:
{source_content}

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  ${{uuid}}-storage-${{wsl-distro}}:
  ${{uuid}}-data-${{wsl-distro}}:
"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(compose_content)
            
            self.log_success(f"已生成完整的compose文件: {output_file}")
            return True
        except Exception as e:
            self.log_error(f"生成compose文件失败: {e}")
            return False
    
    def is_windows_distro(self):
        """检查是否为Windows容器版本"""
        return self.wsl_distro in self.windows_distros
    
    def generate_uuid(self):
        """生成UUID"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        random_part = str(uuid.uuid4())[:8]
        self.uuid = f"{timestamp}-{random_part}"
        self.log_info(f"生成的容器UUID: {self.uuid}")
    
    def check_podman_installed(self):
        """检查Podman是否已安装"""
        try:
            result = subprocess.run(['podman', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log_success(f"Podman已安装: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_podman(self):
        """安装Podman"""
        self.log_info("正在检查Podman安装...")
        
        if self.check_podman_installed():
            return
        
        self.log_warning("Podman未安装，正在安装...")
        
        # 检测Linux发行版并安装
        try:
            if Path("/etc/debian_version").exists():
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'podman', 'podman-compose'], check=True)
            elif Path("/etc/redhat-release").exists():
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'podman', 'podman-compose'], check=True)
            elif Path("/etc/arch-release").exists():
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'podman', 'podman-compose'], check=True)
            else:
                self.log_error("不支持的Linux发行版")
                sys.exit(1)
            
            self.log_success("Podman安装完成")
        except subprocess.CalledProcessError as e:
            self.log_error(f"Podman安装失败: {e}")
            sys.exit(1)
    
    def setup_windows_container(self):
        """配置Windows容器"""
        if not self.is_windows_distro():
            self.log_warning("当前配置不是Windows容器版本，跳过容器配置")
            return

        self.log_info("正在配置Windows容器环境...")

        # 优先使用 podman-win-wsl2 配置文件
        primary_compose = self.script_dir / "podman-win-wsl2"
        fallback_compose = self.script_dir / "podman-win-wsl2-compose.yml"
        
        if primary_compose.exists():
            # 检查是否为完整的YAML文件
            if self.is_valid_compose_file(primary_compose):
                compose_source = primary_compose
                self.log_success(f"使用主配置文件: {compose_source}")
            else:
                # 不完整的YAML片段，需要生成完整的compose文件
                generated_compose = self.script_dir / "podman-win-wsl2-generated.yml"
                self.log_warning(f"主配置文件不完整，生成完整的compose文件: {generated_compose}")
                self.generate_compose_file(primary_compose, generated_compose)
                compose_source = generated_compose
        elif fallback_compose.exists():
            compose_source = fallback_compose
            self.log_warning(f"主配置文件不存在，使用备用配置文件: {compose_source}")
        else:
            self.log_error("错误: 未找到任何有效的 podman-compose 配置文件")
            return False
        
        # 生成UUID
        self.generate_uuid()
        
        # 创建临时docker-compose文件
        compose_file = self.script_dir / f"docker-compose-{self.uuid}.yml"
        
        try:
            # 读取并替换变量
            with open(self.podman_compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换变量
            content = content.replace('${uuid}', self.uuid)
            content = content.replace('${wsl-distro}', self.wsl_distro)
            content = content.replace('${wsl-usr}', self.wsl_usr)
            content = content.replace('${wsl-pwd}', self.wsl_pwd)
            
            # 写入临时文件
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_success(f"已生成docker-compose文件: {compose_file}")
            
            # 启动容器
            self.log_info("正在启动Windows容器...")
            result = subprocess.run(['podman-compose', '-f', str(compose_file), 'up', '-d'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_success("Windows容器启动成功!")
                self.log_success(f"容器名称: {self.uuid}-windows-{self.wsl_distro}")
                self.log_success("RDP端口: 4489")
                self.log_success("HTTP端口: 4818")
                self.log_success("VNC端口: 4777")
                self.log_success(f"用户名: {self.wsl_usr}")
                self.log_success(f"密码: {self.wsl_pwd}")
                
                # 保存容器信息
                with open(self.container_uuid_file, 'w', encoding='utf-8') as f:
                    f.write(self.uuid)
                
                with open(self.compose_file_path, 'w', encoding='utf-8') as f:
                    f.write(str(compose_file))
                
                return True
            else:
                self.log_error(f"Windows容器启动失败: {result.stderr}")
                compose_file.unlink(missing_ok=True)
                return False
                
        except Exception as e:
            self.log_error(f"配置Windows容器时出错: {e}")
            if compose_file.exists():
                compose_file.unlink(missing_ok=True)
            return False
    
    def cleanup_container(self):
        """清理容器"""
        if not self.container_uuid_file.exists():
            self.log_warning("没有找到运行的容器")
            return
        
        try:
            with open(self.container_uuid_file, 'r', encoding='utf-8') as f:
                container_uuid = f.read().strip()
            
            self.log_info(f"正在停止容器: {container_uuid}-windows-{self.wsl_distro}")
            
            # 停止容器
            if self.compose_file_path.exists():
                with open(self.compose_file_path, 'r', encoding='utf-8') as f:
                    compose_path = Path(f.read().strip())
                
                if compose_path.exists():
                    subprocess.run(['podman-compose', '-f', str(compose_path), 'down'], 
                                 capture_output=True)
                    compose_path.unlink(missing_ok=True)
            
            # 清理容器和卷
            container_name = f"{container_uuid}-windows-{self.wsl_distro}"
            subprocess.run(['podman', 'rm', '-f', container_name], capture_output=True)
            
            volume_storage = f"{container_uuid}-storage-{self.wsl_distro}"
            volume_data = f"{container_uuid}-data-{self.wsl_distro}"
            subprocess.run(['podman', 'volume', 'rm', volume_storage], capture_output=True)
            subprocess.run(['podman', 'volume', 'rm', volume_data], capture_output=True)
            
            # 清理文件
            self.container_uuid_file.unlink(missing_ok=True)
            self.compose_file_path.unlink(missing_ok=True)
            
            self.log_success("容器清理完成")
            
        except Exception as e:
            self.log_error(f"清理容器时出错: {e}")
    
    def show_status(self):
        """显示容器状态"""
        print(f"{Colors.BLUE}=== Podman Windows容器状态 ==={Colors.NC}")
        print(f"配置的系统版本: {Colors.GREEN}{self.wsl_distro}{Colors.NC}")
        
        if self.is_windows_distro():
            print(f"容器类型: {Colors.GREEN}Windows容器{Colors.NC}")
            
            if self.container_uuid_file.exists():
                with open(self.container_uuid_file, 'r', encoding='utf-8') as f:
                    container_uuid = f.read().strip()
                
                print(f"容器状态: {Colors.GREEN}正在运行{Colors.NC}")
                print(f"容器名称: {container_uuid}-windows-{self.wsl_distro}")
                print("RDP端口: 4489")
                print("HTTP端口: 4818")
                print("VNC端口: 4777")
                
                # 显示容器详细信息
                try:
                    result = subprocess.run(['podman', 'ps', '--filter', 
                                           f'name={container_uuid}-windows-{self.wsl_distro}', 
                                           '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                                          capture_output=True, text=True)
                    if result.stdout:
                        print("\n容器详细信息:")
                        print(result.stdout)
                except:
                    pass
            else:
                print(f"容器状态: {Colors.YELLOW}未运行{Colors.NC}")
        else:
            print(f"容器类型: {Colors.YELLOW}Linux开发环境{Colors.NC}")
            print("使用标准的WSL2环境，无需Podman容器")
    
    def show_help(self):
        """显示帮助信息"""
        print(f"{Colors.BLUE}=== Podman Windows容器安装脚本 ==={Colors.NC}")
        print(f"{Colors.GREEN}用法: python {Path(__file__).name} [命令]{Colors.NC}")
        print()
        print(f"{Colors.YELLOW}命令选项:{Colors.NC}")
        print("  install    - 安装Podman并配置Windows容器环境")
        print("  start      - 启动Windows容器")
        print("  stop       - 停止并清理容器")
        print("  status     - 显示容器状态")
        print("  cleanup    - 清理所有容器和配置")
        print("  help       - 显示此帮助信息")
        print()
        print(f"{Colors.YELLOW}配置文件:{Colors.NC}")
        print("  wsl-distro.info - 系统版本配置文件")
        print("  podman-win-wsl2 - Podman compose配置文件")
        print()
        print(f"{Colors.YELLOW}支持的系统版本:{Colors.NC}")
        print("  win11   - Windows 11 专业版")
        print("  win11l  - Windows 11 LTS版本")
        print("  win7u   - Windows 7 专业版")
        print("  win2025 - Windows Server 2025 专业版")
        print("  Debian  - Debian Linux (默认)")
        print("  Ubuntu  - Ubuntu Linux")
    
    def run(self, command):
        """运行命令"""
        if command == "install":
            self.install_podman()
            self.setup_windows_container()
        elif command == "start":
            self.setup_windows_container()
        elif command == "stop":
            self.cleanup_container()
        elif command == "status":
            self.show_status()
        elif command == "cleanup":
            self.cleanup_container()
        elif command in ["help", "--help", "-h"]:
            self.show_help()
        else:
            self.log_error(f"错误: 未知命令 '{command}'")
            self.show_help()
            sys.exit(1)

def main():
    """主函数"""
    installer = PodmanWindowsInstaller()
    installer.load_config()
    installer.load_gateway_domains()  # 加载网关域名配置
    
    # 获取命令参数
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    installer.run(command)

if __name__ == "__main__":
    main()
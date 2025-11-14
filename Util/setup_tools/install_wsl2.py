#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2安装与配置脚本
用于在Windows系统上安装、开启和支持WSL2功能

参数:
    无

返回:
    无
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path


class Colors:
    """终端颜色输出"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class WSL2Installer:
    """WSL2安装器类"""
    
    def __init__(self):
        """
        初始化WSL2安装器
        
        参数:
            无
            
        返回:
            无
        """
        self.script_dir = Path(__file__).parent.absolute()
        self.wsl_version = 2
    
    def log_info(self, message):
        """
        输出信息日志
        
        参数:
            message (str): 日志消息
            
        返回:
            无
        """
        print(f"{Colors.BLUE}{message}{Colors.NC}")
    
    def log_success(self, message):
        """
        输出成功日志
        
        参数:
            message (str): 日志消息
            
        返回:
            无
        """
        print(f"{Colors.GREEN}{message}{Colors.NC}")
    
    def log_warning(self, message):
        """
        输出警告日志
        
        参数:
            message (str): 日志消息
            
        返回:
            无
        """
        print(f"{Colors.YELLOW}{message}{Colors.NC}")
    
    def log_error(self, message):
        """
        输出错误日志
        
        参数:
            message (str): 日志消息
            
        返回:
            无
        """
        print(f"{Colors.RED}{message}{Colors.NC}")
    
    def check_os_version(self):
        """
        检查操作系统版本是否支持WSL2
        
        参数:
            无
            
        返回:
            bool: 操作系统是否支持WSL2
        """
        self.log_info("正在检查操作系统版本...")
        
        if platform.system() != "Windows":
            self.log_error("错误：当前系统不是Windows，WSL2仅支持Windows系统")
            return False
        
        # 获取Windows版本信息
        try:
            # 使用winver命令获取Windows版本信息
            result = subprocess.run(["powershell", "[System.Environment]::OSVersion.Version | ForEach-Object {\"$($_.Major).$($_.Minor)\"}"],
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            major, minor = map(int, version.split('.'))
            
            # WSL2需要Windows 10版本1903及以上或Windows 11
            if (major == 10 and minor >= 0) and (version >= "10.0.18362") or major >= 11:
                self.log_success(f"Windows版本检查通过: {version}")
                return True
            else:
                self.log_error(f"错误：Windows版本 {version} 不支持WSL2，请升级到Windows 10版本1903或更高版本")
                return False
        except Exception as e:
            self.log_error(f"检查Windows版本时出错: {e}")
            return False
    
    def is_admin(self):
        """
        检查脚本是否以管理员权限运行
        
        参数:
            无
            
        返回:
            bool: 是否以管理员权限运行
        """
        try:
            is_admin = os.name == 'nt' and (os.system('net session >nul 2>&1') == 0)
            if not is_admin:
                self.log_error("错误：脚本需要以管理员权限运行")
            return is_admin
        except:
            return False
    
    def check_wsl_installed(self):
        """
        检查WSL是否已安装
        
        参数:
            无
            
        返回:
            bool: WSL是否已安装
        """
        try:
            subprocess.run(["wsl", "--list", "--online"], capture_output=True, text=True, check=True)
            self.log_success("WSL已安装")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def enable_wsl_features(self):
        """
        启用Windows的WSL功能
        
        参数:
            无
            
        返回:
            bool: 功能是否启用成功
        """
        self.log_info("正在启用Windows Subsystem for Linux功能...")
        
        try:
            # 启用WSL功能
            result = subprocess.run(
                ["powershell", "-Command", "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart"],
                capture_output=True, text=True, check=True
            )
            
            # 启用虚拟机平台功能（WSL2需要）
            result = subprocess.run(
                ["powershell", "-Command", "Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart"],
                capture_output=True, text=True, check=True
            )
            
            self.log_success("Windows Subsystem for Linux和虚拟机平台功能已启用")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"启用WSL功能失败: {e.stderr}")
            return False
        except Exception as e:
            self.log_error(f"启用WSL功能时出错: {e}")
            return False
    
    def set_wsl2_default(self):
        """
        设置WSL2为默认版本
        
        参数:
            无
            
        返回:
            bool: 设置是否成功
        """
        self.log_info("正在将WSL2设置为默认版本...")
        
        try:
            result = subprocess.run(
                ["wsl", "--set-default-version", str(self.wsl_version)],
                capture_output=True, text=True, check=True
            )
            self.log_success("WSL2已设置为默认版本")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"设置WSL2为默认版本失败: {e.stderr}")
            self.log_warning("提示：可能需要安装WSL2内核更新包，访问微软官网下载：https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msu")
            return False
        except Exception as e:
            self.log_error(f"设置WSL2为默认版本时出错: {e}")
            return False
    
    def install_wsl2(self):
        """
        完整安装WSL2的流程
        
        参数:
            无
            
        返回:
            bool: 安装是否成功
        """
        self.log_info("开始安装WSL2...")
        
        # 检查是否以管理员权限运行
        if not self.is_admin():
            return False
        
        # 检查操作系统版本
        if not self.check_os_version():
            return False
        
        # 检查WSL是否已安装
        if not self.check_wsl_installed():
            # 启用WSL功能
            if not self.enable_wsl_features():
                return False
            
            self.log_warning("警告：WSL功能已启用，需要重启系统才能生效")
            restart = input("是否立即重启系统？(y/n): ")
            if restart.lower() == 'y':
                self.log_info("正在重启系统...")
                os.system("shutdown /r /t 0")
                return False  # 不会执行到这里，因为系统正在重启
            else:
                self.log_warning("请手动重启系统后再次运行此脚本")
                return False
        
        # 设置WSL2为默认版本
        if not self.set_wsl2_default():
            return False
        
        self.log_success("\nWSL2安装完成！")
        self.log_info("您可以通过以下步骤安装Linux发行版：")
        self.log_info("1. 打开Microsoft Store")
        self.log_info("2. 搜索并安装您喜欢的Linux发行版（如Ubuntu）")
        self.log_info("3. 安装完成后，启动该发行版并按照提示设置用户名和密码")
        
        return True


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        int: 退出码，0表示成功，1表示失败
    """
    installer = WSL2Installer()
    
    try:
        if installer.install_wsl2():
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        installer.log_error("\n安装过程被用户中断")
        return 1
    except Exception as e:
        installer.log_error(f"发生未预期的错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
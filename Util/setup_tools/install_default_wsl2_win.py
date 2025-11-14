#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2默认发行版安装脚本
用于在Windows系统上安装并配置指定的Linux发行版到WSL2环境中
"""

import os
import sys
import json
import subprocess
import time
import logging
import argparse
from pathlib import Path

# 配置日志记录 - 符合项目日志规范
# Logger声明为模块级别的常量
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "Logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "wsl2_install.log"

# 创建处理器
file_handler = logging.FileHandler(str(LOG_FILE), encoding='utf-8')
console_handler = logging.StreamHandler()

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到logger
LOGGER.addHandler(file_handler)
LOGGER.addHandler(console_handler)


class Colors:
    """
    终端颜色输出类，用于在终端中显示彩色文本
    """
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    RESET = '\033[0m'


class WSL2DefaultInstaller:
    """
    WSL2默认发行版安装器类
    负责从配置文件读取参数并安装指定的Linux发行版到WSL2环境
    """
    
    def __init__(self, config_file="../../wsl_config/wsl_default_config.json", args=None):
        """
        初始化WSL2默认发行版安装器
        
        参数:
            config_file (str): WSL配置文件的相对路径
            args (argparse.Namespace): 命令行参数对象
        """
        self.config_file = config_file
        self.config = None
        self.colors = Colors()
        self.args = args
        
        # 根据命令行参数设置调试模式
        if args and args.debug:
            LOGGER.setLevel(logging.DEBUG)
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug("调试模式已启用")
    
    def load_config(self):
        """
        从配置文件加载WSL配置参数
        
        返回:
            bool: 配置加载是否成功
        """
        try:
            # 获取脚本所在目录
            script_dir = Path(__file__).parent
            # 构建配置文件的绝对路径
            config_path = script_dir / self.config_file
            
            # 如果命令行参数指定了配置文件路径，则使用它
            if self.args and self.args.config:
                config_path = Path(self.args.config)
                logging.info(f"使用命令行指定的配置文件: {config_path}")
            else:
                logging.info(f"尝试加载配置文件: {config_path}")
            
            if not config_path.exists():
                if LOGGER.isEnabledFor(logging.ERROR):
                    LOGGER.error(f"配置文件不存在: {config_path}")
                print(f"{self.colors.RED}✗ 配置文件不存在: {config_path}{self.colors.RESET}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 使用命令行参数覆盖配置文件中的值
            self._override_config_with_args()
            
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"成功加载配置文件: {config_path}")
            print(f"{self.colors.GREEN}✓ 成功加载配置文件: {config_path}{self.colors.RESET}")
            return True
        except json.JSONDecodeError as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"配置文件格式错误: {str(e)}")
            print(f"{self.colors.RED}✗ 配置文件格式错误: {str(e)}{self.colors.RESET}")
            return False
        except PermissionError as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"无权限读取配置文件: {str(e)}")
            print(f"{self.colors.RED}✗ 无权限读取配置文件: {str(e)}{self.colors.RESET}")
            return False
        except Exception as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"加载配置文件失败: {str(e)}")
            print(f"{self.colors.RED}✗ 加载配置文件失败: {str(e)}{self.colors.RESET}")
            return False
    
    def _override_config_with_args(self):
        """
        使用命令行参数覆盖配置文件中的值
        """
        if not self.args or not self.config:
            return
        
        # 覆盖发行版名称
        if self.args.distro:
            old_distro = self.config.get('wsl_distro', 'Debian')
            self.config['wsl_distro'] = self.args.distro
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"使用命令行参数覆盖发行版: {old_distro} -> {self.args.distro}")
        
        # 覆盖用户名
        if self.args.username:
            old_user = self.config.get('wsl_usr', 'devman')
            self.config['wsl_usr'] = self.args.username
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"使用命令行参数覆盖用户名: {old_user} -> {self.args.username}")
        
        # 覆盖密码 - 不记录敏感信息
        if self.args.password:
            self.config['wsl_pwd'] = self.args.password
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info("使用命令行参数覆盖密码 (密码内容不记录)")
    
    def check_admin_privileges(self):
        """
        检查是否以管理员权限运行
        
        返回:
            bool: 是否具有管理员权限
        """
        try:
            # 在Windows上检查管理员权限
            if os.name == 'nt':
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                if not is_admin:
                    print(f"{self.colors.RED}✗ 脚本应该已经尝试自动提升权限，但仍然没有管理员权限{self.colors.RESET}")
                    print(f"{self.colors.YELLOW}! 请手动以管理员身份运行此脚本{self.colors.RESET}")
                    return False
                else:
                    print(f"{self.colors.GREEN}✓ 已获得管理员权限{self.colors.RESET}")
            return True
        except Exception as e:
            print(f"{self.colors.YELLOW}! 检查管理员权限时出错: {str(e)}{self.colors.RESET}")
            return False
            
    def run_command(self, cmd, timeout=300):
        """
        执行命令并返回结果
        
        参数:
            cmd (list): 要执行的命令
            timeout (int): 命令执行超时时间（秒）
        
        返回:
            tuple: (是否成功, 输出结果, 错误信息)
        """
        try:
            # 确保日志行大小不超过200K
            cmd_str = ' '.join(cmd)[:1000]  # 限制命令字符串长度
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"执行命令: {cmd_str}")
            
            result = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True, timeout=timeout)
            
            if result.returncode == 0:
                if LOGGER.isEnabledFor(logging.INFO):
                    LOGGER.info(f"命令执行成功: {cmd_str}")
            else:
                # 限制错误输出长度，避免日志过大
                error_output = result.stderr[:1000] if result.stderr else ""
                if LOGGER.isEnabledFor(logging.WARNING):
                    LOGGER.warning(f"命令执行失败 (返回码: {result.returncode}): {cmd_str}")
                    LOGGER.warning(f"错误输出: {error_output}")
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"命令执行超时: {cmd_str}")
            return False, "", f"命令执行超时（{timeout}秒）"
        except FileNotFoundError:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"命令未找到: {cmd[0]}")
            return False, "", f"命令未找到: {cmd[0]}"
        except Exception as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"执行命令时出错: {str(e)}")
            return False, "", str(e)
    
    def check_wsl_installed(self):
        """
        检查WSL是否已安装
        
        返回:
            bool: WSL是否已安装
        """
        success, stdout, stderr = self.run_command(['wsl', '--status'])
        if success:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info("WSL已安装")
            print(f"{self.colors.GREEN}✓ WSL已安装{self.colors.RESET}")
            return True
        else:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"WSL未安装或不可用: {stderr}")
            print(f"{self.colors.RED}✗ WSL未安装或不可用，请先安装WSL{self.colors.RESET}")
            print(f"{self.colors.YELLOW}提示：可以使用 'wsl --install' 命令安装WSL{self.colors.RESET}")
            return False
    
    def check_distro_available(self, distro_name):
        """
        检查指定的发行版是否可用
        
        参数:
            distro_name (str): 要检查的Linux发行版名称
        
        返回:
            bool: 发行版是否可用
        """
        success, stdout, stderr = self.run_command(['wsl', '--list', '--online'])
        if success:
            if distro_name.lower() in stdout.lower():
                if LOGGER.isEnabledFor(logging.INFO):
                    LOGGER.info(f"发行版 {distro_name} 可用")
                print(f"{self.colors.GREEN}✓ 发行版 {distro_name} 可用{self.colors.RESET}")
                return True
            else:
                if LOGGER.isEnabledFor(logging.WARNING):
                    LOGGER.warning(f"发行版 {distro_name} 不可用")
                print(f"{self.colors.RED}✗ 发行版 {distro_name} 不可用{self.colors.RESET}")
                print(f"{self.colors.YELLOW}可用的发行版:\n{stdout}{self.colors.RESET}")
                return False
        else:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"检查发行版可用性时出错: {stderr}")
            print(f"{self.colors.YELLOW}! 检查发行版可用性时出错: {stderr}{self.colors.RESET}")
            print(f"{self.colors.YELLOW}尝试直接安装，可能需要网络连接{self.colors.RESET}")
            return True  # 尝试直接安装，不阻止流程
    
    def install_distro(self, distro_name, username, password):
        """
        安装指定的Linux发行版到WSL2
        
        参数:
            distro_name (str): 要安装的Linux发行版名称
            username (str): 要创建的用户名
            password (str): 用户密码
        
        返回:
            bool: 安装是否成功
        """
        try:
            # 安装指定的发行版
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"开始安装发行版 {distro_name}")
            print(f"{self.colors.CYAN}正在安装发行版 {distro_name}...{self.colors.RESET}")
            print(f"{self.colors.YELLOW}注意：这可能需要几分钟时间，请耐心等待...{self.colors.RESET}")
            
            # 如果处于调试模式，输出更多信息
            if self.args and self.args.debug:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(f"安装命令: wsl --install -d {distro_name}")
                print(f"{self.colors.MAGENTA}[调试] 安装命令: wsl --install -d {distro_name}{self.colors.RESET}")
                
            install_cmd = ['wsl', '--install', '-d', distro_name]
            success, stdout, stderr = self.run_command(install_cmd, timeout=600)  # 安装可能需要更长时间
            
            if not success:
                if LOGGER.isEnabledFor(logging.ERROR):
                    LOGGER.error(f"安装发行版 {distro_name} 失败: {stderr}")
                print(f"{self.colors.RED}✗ 安装发行版 {distro_name} 失败: {stderr}{self.colors.RESET}")
                return False
            
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"发行版 {distro_name} 安装成功")
            print(f"{self.colors.GREEN}✓ 发行版 {distro_name} 安装成功{self.colors.RESET}")
            
            # 等待WSL初始化完成
            print(f"{self.colors.CYAN}等待WSL初始化完成...{self.colors.RESET}")
            time.sleep(5)
            
            # 设置默认用户和密码（通过WSL命令）
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"开始配置默认用户 {username}")
            print(f"{self.colors.CYAN}正在配置默认用户 {username}...{self.colors.RESET}")
            
            # 创建用户配置脚本
            user_setup_script = f"""
            if ! id -u {username} > /dev/null 2>&1; then
                useradd -m -s /bin/bash {username}
                echo "{username}:{password}" | chpasswd
                usermod -aG sudo {username}
                echo "{username} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/{username}
                chmod 0440 /etc/sudoers.d/{username}
            fi
            exit
            """
            
            # 如果处于调试模式，输出用户配置脚本
            if self.args and self.args.debug:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    # 不记录包含密码的脚本内容
                    LOGGER.debug("用户配置脚本将被执行")
                print(f"{self.colors.MAGENTA}[调试] 用户配置脚本内容:\n{user_setup_script}{self.colors.RESET}")
            
            # 以root用户运行配置脚本
            setup_cmd = ['wsl', '-d', distro_name, '-u', 'root', 'bash', '-c', user_setup_script]
            success, stdout, stderr = self.run_command(setup_cmd)
            
            if not success:
                if LOGGER.isEnabledFor(logging.ERROR):
                    LOGGER.error(f"配置用户 {username} 失败: {stderr}")
                print(f"{self.colors.RED}✗ 配置用户 {username} 失败: {stderr}{self.colors.RESET}")
                print(f"{self.colors.YELLOW}尝试手动设置默认用户...{self.colors.RESET}")
            
            # 设置默认用户
            set_user_cmd = ['wsl', '--set-default-user', username, '-d', distro_name]
            success, stdout, stderr = self.run_command(set_user_cmd)
            
            if success:
                if LOGGER.isEnabledFor(logging.INFO):
                    LOGGER.info(f"默认用户 {username} 配置成功")
                print(f"{self.colors.GREEN}✓ 默认用户 {username} 配置成功{self.colors.RESET}")
            else:
                if LOGGER.isEnabledFor(logging.WARNING):
                    LOGGER.warning(f"设置默认用户失败: {stderr}")
                print(f"{self.colors.YELLOW}! 设置默认用户失败，但安装仍继续: {stderr}{self.colors.RESET}")
            
            return True
        except subprocess.CalledProcessError as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"安装或配置发行版失败: {str(e)}")
            print(f"{self.colors.RED}✗ 安装或配置发行版失败: {str(e)}{self.colors.RESET}")
            return False
        except Exception as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"发生未知错误: {str(e)}")
            print(f"{self.colors.RED}✗ 发生未知错误: {str(e)}{self.colors.RESET}")
            return False
    
    def _configure_user(self, distro_name, username, password):
        """
        配置WSL中的用户权限
        
        参数:
            distro_name (str): 发行版名称
            username (str): 用户名
            password (str): 密码
        
        返回:
            bool: 配置是否成功
        """
        # 创建用户配置脚本
        user_setup_script = f"""
        if ! id -u {username} > /dev/null 2>&1; then
            useradd -m -s /bin/bash {username}
            echo "{username}:{password}" | chpasswd
            usermod -aG sudo {username}
            echo "{username} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/{username}
            chmod 0440 /etc/sudoers.d/{username}
        fi
        exit
        """
        
        # 以root用户运行配置脚本
        setup_cmd = ['wsl', '-d', distro_name, '-u', 'root', 'bash', '-c', user_setup_script]
        success, stdout, stderr = self.run_command(setup_cmd)
        
        if success:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(f"用户 {username} 权限配置成功")
            return True
        else:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"用户 {username} 权限配置失败: {stderr}")
            return False
    
    def set_wsl2_as_default(self):
        """
        设置WSL2为默认版本
        
        返回:
            bool: 设置是否成功
        """
        if LOGGER.isEnabledFor(logging.INFO):
            LOGGER.info("设置WSL2为默认版本")
        success, stdout, stderr = self.run_command(['wsl', '--set-default-version', '2'])
        if success:
            print(f"{self.colors.GREEN}✓ 已设置WSL2为默认版本{self.colors.RESET}")
            return True
        else:
            if LOGGER.isEnabledFor(logging.WARNING):
                LOGGER.warning(f"设置WSL2为默认版本失败: {stderr}")
            print(f"{self.colors.YELLOW}! 设置WSL2为默认版本失败: {stderr}{self.colors.RESET}")
            print(f"{self.colors.YELLOW}请确保已安装WSL2内核更新包{self.colors.RESET}")
            print(f"{self.colors.YELLOW}可以从微软官网下载WSL2 Linux内核更新包{self.colors.RESET}")
            return False
    
    def set_distro_version(self, distro_name):
        """
        设置指定发行版使用WSL2
        
        参数:
            distro_name (str): 发行版名称
        
        返回:
            bool: 设置是否成功
        """
        if LOGGER.isEnabledFor(logging.INFO):
            LOGGER.info(f"设置 {distro_name} 使用WSL2")
        print(f"{self.colors.CYAN}正在设置 {distro_name} 使用WSL2...{self.colors.RESET}")
        print(f"{self.colors.YELLOW}注意：这可能需要几分钟时间，请耐心等待...{self.colors.YELLOW}")
        
        success, stdout, stderr = self.run_command(['wsl', '--set-version', distro_name, '2'], timeout=600)
        if success:
            print(f"{self.colors.GREEN}✓ 已将 {distro_name} 设置为使用WSL2{self.colors.RESET}")
            return True
        else:
            if LOGGER.isEnabledFor(logging.WARNING):
                LOGGER.warning(f"设置 {distro_name} 使用WSL2失败: {stderr}")
            print(f"{self.colors.YELLOW}! 设置 {distro_name} 使用WSL2失败: {stderr}{self.colors.RESET}")
            return False
    
    def check_distro_installed(self, distro_name):
        """
        检查指定发行版是否已安装
        
        参数:
            distro_name (str): 要检查的发行版名称
        
        返回:
            bool: 发行版是否已安装
        """
        try:
            success, stdout, stderr = self.run_command(['wsl', '--list'])
            if success:
                is_installed = distro_name.lower() in stdout.lower()
                if LOGGER.isEnabledFor(logging.INFO):
                    LOGGER.info(f"检查发行版 {distro_name} 是否安装: {'是' if is_installed else '否'}")
                return is_installed
            else:
                if LOGGER.isEnabledFor(logging.ERROR):
                    LOGGER.error(f"检查发行版安装状态失败: {stderr}")
                return False
        except Exception as e:
            if LOGGER.isEnabledFor(logging.ERROR):
                LOGGER.error(f"检查发行版安装状态时出错: {str(e)}")
            return False
    
    def run(self):
        """
        运行WSL2默认发行版安装流程
        
        返回:
            int: 退出代码，0表示成功，非0表示失败
        """
        print(f"{self.colors.BLUE}========== WSL2默认发行版安装程序 =========={self.colors.RESET}")
        
        # 如果处于调试模式，显示调试信息
        if self.args and self.args.debug:
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug("调试模式已启用")
            print(f"{self.colors.MAGENTA}[调试] 调试模式已启用{self.colors.RESET}")
        
        # 检查管理员权限
        if not self.check_admin_privileges():
            return 1
        
        # 加载配置文件
        if not self.load_config():
            return 1
        
        # 提取配置参数
        distro_name = self.config.get('wsl_distro', 'Debian')
        username = self.config.get('wsl_usr', 'devman')
        password = self.config.get('wsl_pwd', 'devman')
        
        print(f"{self.colors.CYAN}配置信息:{self.colors.RESET}")
        print(f"  发行版: {distro_name}")
        print(f"  用户名: {username}")
        print(f"  密码: {'*' * len(password)}")
        
        # 检查WSL是否已安装
        if not self.check_wsl_installed():
            return 1
        
        # 设置WSL2为默认版本
        self.set_wsl2_as_default()
        
        # 检查发行版是否已安装
        if self.check_distro_installed(distro_name):
            # 如果指定了force参数，即使发行版已安装也重新安装
            if self.args and self.args.force:
                print(f"{self.colors.YELLOW}! 检测到 --force 参数，将重新安装发行版 {distro_name}{self.colors.RESET}")
                # 首先卸载已安装的发行版
                print(f"{self.colors.CYAN}正在卸载发行版 {distro_name}...{self.colors.RESET}")
                success, stdout, stderr = self.run_command(['wsl', '--unregister', distro_name])
                if not success:
                    print(f"{self.colors.YELLOW}! 卸载发行版失败: {stderr}，尝试直接安装{self.colors.RESET}")
                else:
                    print(f"{self.colors.GREEN}✓ 发行版 {distro_name} 已卸载{self.colors.RESET}")
            else:
                print(f"{self.colors.YELLOW}! 发行版 {distro_name} 已安装，跳过安装步骤{self.colors.RESET}")
                # 确保使用WSL2
                self.set_distro_version(distro_name)
                
                # 如果需要重新配置用户
                if self.args and (self.args.username or self.args.password):
                    print(f"{self.colors.CYAN}正在重新配置用户 {username}...{self.colors.RESET}")
                    self._configure_user(distro_name, username, password)
                
                # 跳过安装过程
                # 验证安装结果
                if self.check_distro_installed(distro_name):
                    print(f"{self.colors.GREEN}\n========== 配置完成 =========={self.colors.RESET}")
                    print(f"{self.colors.GREEN}✓ 发行版 {distro_name} 已配置为使用WSL2{self.colors.RESET}")
                    print(f"{self.colors.GREEN}✓ 默认用户 {username} 已配置{self.colors.RESET}")
                    print(f"\n{self.colors.CYAN}使用以下命令启动WSL:{self.colors.RESET}")
                    print(f"  wsl -d {distro_name}")
                    return 0
                else:
                    print(f"{self.colors.RED}\n✗ 配置验证失败，请检查错误信息{self.colors.RESET}")
                    return 1
        
        # 检查发行版是否可用
        if not self.check_distro_available(distro_name):
            return 1
        
        # 安装发行版
        if not self.install_distro(distro_name, username, password):
            return 1
        
        # 验证安装结果
        if self.check_distro_installed(distro_name):
            print(f"{self.colors.GREEN}\n========== 安装完成 =========={self.colors.RESET}")
            print(f"{self.colors.GREEN}✓ 发行版 {distro_name} 已成功安装到WSL2{self.colors.RESET}")
            print(f"{self.colors.GREEN}✓ 默认用户 {username} 已配置{self.colors.RESET}")
            print(f"\n{self.colors.CYAN}使用以下命令启动WSL:{self.colors.RESET}")
            print(f"  wsl -d {distro_name}")
            return 0
        else:
            print(f"{self.colors.RED}\n✗ 安装验证失败，请检查错误信息{self.colors.RESET}")
            return 1


def parse_args():
    """
    解析命令行参数
    
    返回:
        argparse.Namespace: 解析后的命令行参数
    """
    parser = argparse.ArgumentParser(description='WSL2默认发行版安装程序')
    
    # 配置文件路径参数
    parser.add_argument('--config', type=str,
                      help='指定配置文件路径')
    
    # 调试模式参数
    parser.add_argument('--debug', action='store_true',
                      help='启用调试模式，显示详细的执行信息')
    
    # 强制重新安装参数
    parser.add_argument('--force', action='store_true',
                      help='强制重新安装指定的发行版，即使它已经安装')
    
    # 覆盖配置文件中的参数
    parser.add_argument('--distro', type=str,
                      help='指定要安装的Linux发行版名称（覆盖配置文件）')
    
    parser.add_argument('--username', type=str,
                      help='指定要创建的用户名（覆盖配置文件）')
    
    parser.add_argument('--password', type=str,
                      help='指定用户密码（覆盖配置文件）')
    
    return parser.parse_args()


def run_as_admin():
    """
    检查是否以管理员权限运行，如果不是则尝试以管理员权限重新运行脚本
    
    返回:
        bool: 如果已以管理员权限运行或成功重新运行，则返回True；否则返回False
    """
    import ctypes
    
    # 检查当前是否已有管理员权限
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                return True
                
            # 尝试以管理员权限重新运行脚本
            script_path = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            
            # 使用ShellExecuteW以管理员权限启动新进程
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f"{script_path} {params}", None, 1
            )
            
            # 等待一段时间让新进程启动
            time.sleep(1)
            return False  # 原进程应该退出
            
        except Exception as e:
            print(f"尝试提升权限时出错: {str(e)}")
            return False
    
    # 非Windows系统不处理
    return True


def main():
    """
    主函数
    """
    # 尝试以管理员权限运行
    if os.name == 'nt' and not run_as_admin():
        # 如果run_as_admin返回False，说明已经启动了新的管理员权限进程
        # 原进程应该退出
        sys.exit(0)
    
    # 解析命令行参数
    args = parse_args()
    
    # 创建安装器实例
    if args.config:
        installer = WSL2DefaultInstaller(config_file=args.config, args=args)
    else:
        installer = WSL2DefaultInstaller(args=args)
    
    # 运行安装流程
    return installer.run()


if __name__ == "__main__":
    sys.exit(main())
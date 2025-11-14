#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则管理器 - 支持文件锁定、远程/本地模式

功能说明：
- 统一管理所有全局规则配置
- 支持多种配置模式（IDE、PATH、JSON）
- 自动检测工具安装需求
- 集成网关域名管理
- 新增规则文件状态管理（锁定、远程、本地模式）

作者：AI Assistant
创建时间：2024年
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any


class GlobalRulesManager:
    """全局规则管理器类"""
    
    def __init__(self, rules_dir: str = None):
        """
        初始化规则管理器
        
        参数：
            rules_dir: 规则文件目录路径，默认为当前文件所在目录的父目录下的.trae/rules
        """
        if rules_dir is None:
            self.rules_dir = Path(__file__).parent
        else:
            self.rules_dir = Path(rules_dir)
        
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 规则文件状态管理
        self.lock_file = self.rules_dir / "rules.lock"
        self.online_file = self.rules_dir / "rules.online"
        self.offline_file = self.rules_dir / "rules.offline"
        self.remote_rules_url = "https://raw.githubusercontent.com/aspnmy/ai_project_rules/refs/heads/master/project_rules.md"
        
        # 配置文件路径
        self.register_config_file = self.rules_dir / "registerConfig.json"
        self.build_tools_file = self.rules_dir / "build-image-tools"
        self.portainer_config_file = self.rules_dir / "portainerEE-Compose"
        self.download_gateway_file = self.rules_dir / "download-gateway"
        self.dockerimage_gateway_file = self.rules_dir / "dockerimage-gateway"
    
    def get_rules_status(self) -> Dict[str, Any]:
        """
        获取当前规则文件状态
        
        返回：
            Dict: 包含锁定状态、模式类型等状态信息
        """
        status = {
            "is_locked": self.lock_file.exists(),
            "is_online": self.online_file.exists(),
            "is_offline": self.offline_file.exists(),
            "mode": self._get_current_mode(),
            "rules_dir": str(self.rules_dir)
        }
        return status
    
    def _get_current_mode(self) -> str:
        """
        获取当前规则模式
        
        返回：
            str: 当前模式名称（lock/online/offline/default）
        """
        if self.lock_file.exists():
            return "lock"
        elif self.online_file.exists():
            return "online"
        elif self.offline_file.exists():
            return "offline"
        else:
            return "default"
    
    def check_rules_update_permission(self) -> bool:
        """
        检查是否允许更新规则文件
        
        返回：
            bool: True表示允许更新，False表示已锁定
        """
        if self.lock_file.exists():
            print(f"规则文件已锁定（{self.lock_file}存在），禁止更新")
            return False
        return True
    
    def get_remote_rules_content(self) -> Optional[str]:
        """
        获取远程规则文件内容
        
        返回：
            Optional[str]: 远程规则内容，失败时返回None
        """
        try:
            response = requests.get(self.remote_rules_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取远程规则失败: {e}")
            return None
    
    def update_rules_from_remote(self) -> bool:
        """
        从远程更新规则文件
        
        返回：
            bool: 更新成功返回True，失败返回False
        """
        if not self.check_rules_update_permission():
            return False
        
        if not self.online_file.exists():
            print("当前不是在线模式，跳过远程更新")
            return False
        
        content = self.get_remote_rules_content()
        if content is None:
            return False
        
        rules_file = self.rules_dir / "project_rules.md"
        try:
            # 备份原文件
            if rules_file.exists():
                backup_file = rules_file.with_suffix('.md.backup')
                rules_file.rename(backup_file)
                print(f"已备份原规则文件到: {backup_file}")
            
            # 写入新内容
            with open(rules_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"规则文件已从远程更新: {rules_file}")
            return True
        except Exception as e:
            print(f"更新规则文件失败: {e}")
            return False
    
    def ensure_local_rules_exists(self) -> bool:
        """
        确保本地规则文件存在（离线模式）
        
        返回：
            bool: 成功确保文件存在返回True
        """
        if not self.offline_file.exists():
            return True
        
        rules_file = self.rules_dir / "project_rules.md"
        if rules_file.exists():
            return True
        
        print("本地规则文件不存在，尝试从远程拉取...")
        content = self.get_remote_rules_content()
        if content is None:
            print("无法获取远程规则内容")
            return False
        
        try:
            with open(rules_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已从远程拉取规则文件到本地: {rules_file}")
            return True
        except Exception as e:
            print(f"保存规则文件失败: {e}")
            return False
    
    def get_register_mode(self) -> str:
        """
        获取容器仓库配置模式
        
        返回：
            str: 配置模式（IDE/PATH/JSON）
        """
        # 检查规则文件状态
        if not self.ensure_local_rules_exists():
            return "IDE"  # 默认模式
        
        # 原有的配置模式检测逻辑
        register_file = self.rules_dir / "register-docker-login"
        if not register_file.exists():
            return "IDE"
        
        try:
            with open(register_file, 'r', encoding='utf-8') as f:
                mode = f.read().strip()
                if mode in ["IDE", "PATH", "JSON"]:
                    return mode
        except Exception:
            pass
        
        return "IDE"
    
    def get_register_config(self) -> Dict[str, Any]:
        """
        获取容器仓库配置
        
        返回：
            Dict: 容器仓库配置信息
        """
        # 检查规则文件状态
        if not self.ensure_local_rules_exists():
            return {}
        
        mode = self.get_register_mode()
        config = {"mode": mode}
        
        if mode == "JSON" and self.register_config_file.exists():
            try:
                with open(self.register_config_file, 'r', encoding='utf-8') as f:
                    config.update(json.load(f))
            except Exception as e:
                print(f"读取JSON配置失败: {e}")
        
        return config
    
    def get_build_tools(self) -> List[str]:
        """
        获取开发工具列表
        
        返回：
            List[str]: 工具名称列表
        """
        # 检查规则文件状态
        if not self.ensure_local_rules_exists():
            return []
        
        if not self.build_tools_file.exists():
            return []
        
        try:
            with open(self.build_tools_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return [tool.strip() for tool in content.split(',') if tool.strip()]
        except Exception as e:
            print(f"读取构建工具列表失败: {e}")
        
        return []
    
    def has_portainer_ee(self) -> bool:
        """
        检查是否需要安装PortainerEE
        
        返回：
            bool: 需要安装返回True
        """
        tools = self.get_build_tools()
        return "portainerEE" in tools
    
    def get_portainer_config(self) -> Optional[str]:
        """
        获取Portainer配置
        
        返回：
            Optional[str]: 配置内容，不存在时返回None
        """
        # 检查规则文件状态
        if not self.ensure_local_rules_exists():
            return None
        
        if not self.has_portainer_ee():
            return None
        
        try:
            with open(self.portainer_config_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取Portainer配置失败: {e}")
            return None
    
    def get_gateway_domains(self) -> Dict[str, str]:
        """
        获取网关域名配置
        
        返回：
            Dict[str, str]: 网关域名配置
        """
        # 检查规则文件状态
        if not self.ensure_local_rules_exists():
            return {}
        
        domains = {}
        
        # 下载网关域名
        if self.download_gateway_file.exists():
            try:
                with open(self.download_gateway_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # 取第一行有效域名
                        first_line = content.split('\n')[0].strip()
                        if first_line and not first_line.startswith('#'):
                            domains["download"] = first_line
            except Exception as e:
                print(f"读取下载网关配置失败: {e}")
        
        # Docker镜像网关域名
        if self.dockerimage_gateway_file.exists():
            try:
                with open(self.dockerimage_gateway_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # 取第一行有效域名
                        first_line = content.split('\n')[0].strip()
                        if first_line and not first_line.startswith('#'):
                            domains["dockerimage"] = first_line
            except Exception as e:
                print(f"读取Docker镜像网关配置失败: {e}")
        
        # 默认值
        if "download" not in domains:
            domains["download"] = "gateway.cf.shdrr.org"
        if "dockerimage" not in domains:
            domains["dockerimage"] = "drrpull.shdrr.org"
        
        return domains
    
    def create_status_file(self, file_type: str) -> bool:
        """
        创建规则状态文件
        
        参数：
            file_type: 状态文件类型（lock/online/offline）
        
        返回：
            bool: 创建成功返回True
        """
        if file_type not in ["lock", "online", "offline"]:
            print(f"无效的状态文件类型: {file_type}")
            return False
        
        # 如果已锁定，不能创建其他状态文件
        if self.lock_file.exists() and file_type != "lock":
            print("规则文件已锁定，无法切换模式")
            return False
        
        # 删除其他状态文件（避免冲突）
        for status_file in [self.lock_file, self.online_file, self.offline_file]:
            if status_file.exists():
                status_file.unlink()
        
        # 创建新的状态文件
        target_file = {
            "lock": self.lock_file,
            "online": self.online_file,
            "offline": self.offline_file
        }[file_type]
        
        try:
            target_file.touch()
            print(f"已创建规则状态文件: {target_file.name}")
            return True
        except Exception as e:
            print(f"创建状态文件失败: {e}")
            return False
    
    def remove_status_files(self) -> bool:
        """
        移除所有状态文件（恢复到默认模式）
        
        返回：
            bool: 操作成功返回True
        """
        success = True
        for status_file in [self.lock_file, self.online_file, self.offline_file]:
            if status_file.exists():
                try:
                    status_file.unlink()
                    print(f"已删除状态文件: {status_file.name}")
                except Exception as e:
                    print(f"删除状态文件失败 {status_file.name}: {e}")
                    success = False
        
        return success


def main():
    """主函数 - 用于测试规则管理器功能"""
    manager = GlobalRulesManager()
    
    print("=== 规则管理器状态 ===")
    status = manager.get_rules_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n=== 容器仓库配置 ===")
    config = manager.get_register_config()
    print(f"配置模式: {config.get('mode', '未知')}")
    
    print("\n=== 开发工具列表 ===")
    tools = manager.get_build_tools()
    print(f"工具数量: {len(tools)}")
    if tools:
        print("工具列表:", ", ".join(tools))
    
    print("\n=== PortainerEE 状态 ===")
    has_portainer = manager.has_portainer_ee()
    print(f"需要安装PortainerEE: {has_portainer}")
    
    print("\n=== 网关域名配置 ===")
    domains = manager.get_gateway_domains()
    for key, value in domains.items():
        print(f"{key}网关: {value}")


if __name__ == "__main__":
    main()
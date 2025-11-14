#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局规则配置管理器
用于管理容器仓库配置、开发容器初始化工具等全局规则
"""

import os
import json
import sys
from pathlib import Path

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
rules_dir = current_dir

class GlobalRulesManager:
    """全局规则配置管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.rules_dir = rules_dir
        self.register_config_file = os.path.join(rules_dir, "registerConfig.json")
        self.build_tools_file = os.path.join(rules_dir, "build-image-tools")
        self.register_mode_file = os.path.join(rules_dir, "register-docker-login")
        self.portainer_compose_file = os.path.join(rules_dir, "portainerEE-Compose")
        
    def get_register_mode(self):
        """
        获取容器仓库配置模式
        
        Returns:
            str: 配置模式 (IDE, PATH, JSON)
        """
        try:
            with open(self.register_mode_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        return line
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.register_mode_file}", file=sys.stderr)
            return "IDE"
        except Exception as e:
            print(f"读取配置模式时出错: {e}", file=sys.stderr)
            return "IDE"
        return "IDE"
    
    def get_build_tools(self):
        """
        获取开发容器初始化工具列表
        
        Returns:
            list: 工具列表
        """
        try:
            with open(self.build_tools_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return [tool.strip() for tool in content.split(',') if tool.strip()]
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.build_tools_file}", file=sys.stderr)
        except Exception as e:
            print(f"读取工具列表时出错: {e}", file=sys.stderr)
        return []
    
    def get_register_config(self):
        """
        获取容器仓库配置
        
        Returns:
            dict: 配置字典
        """
        mode = self.get_register_mode()
        
        if mode == "JSON":
            return self._get_json_config()
        elif mode == "PATH":
            return self._get_env_config()
        else:  # IDE
            return self._get_default_config()
    
    def _get_json_config(self):
        """从JSON文件获取配置"""
        try:
            if os.path.exists(self.register_config_file):
                with open(self.register_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"警告: JSON配置文件不存在 {self.register_config_file}", file=sys.stderr)
                return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"JSON配置文件解析错误: {e}", file=sys.stderr)
            return self._get_default_config()
        except Exception as e:
            print(f"读取JSON配置时出错: {e}", file=sys.stderr)
            return self._get_default_config()
    
    def _get_env_config(self):
        """从环境变量获取配置"""
        config = {
            "docker_registry": {
                "url": os.environ.get("DOCKER_REGISTRY_URL", "https://registry.hub.docker.com"),
                "username": os.environ.get("DOCKER_REGISTRY_USERNAME", ""),
                "password": os.environ.get("DOCKER_REGISTRY_PASSWORD", ""),
                "email": os.environ.get("DOCKER_REGISTRY_EMAIL", "")
            },
            "private_registry": {
                "url": os.environ.get("PRIVATE_REGISTRY_URL", ""),
                "username": os.environ.get("PRIVATE_REGISTRY_USERNAME", ""),
                "password": os.environ.get("PRIVATE_REGISTRY_PASSWORD", ""),
                "email": os.environ.get("PRIVATE_REGISTRY_EMAIL", "")
            },
            "image_sources": {
                "portainerEE": os.environ.get("PORTAINER_EE_IMAGE", "ghcr.io/aspnmy/portainer-ee:2.34.0-alpine"),
                "portainerCE": os.environ.get("PORTAINER_CE_IMAGE", "portainer/portainer-ce:lts")
            },
            "socket_paths": {
                "podman": os.environ.get("PODMAN_SOCKET_PATH", "/run/podman/podman.sock"),
                "docker": os.environ.get("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
            }
        }
        return config
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "docker_registry": {
                "url": "https://registry.hub.docker.com",
                "username": "",
                "password": "",
                "email": ""
            },
            "private_registry": {
                "url": "",
                "username": "",
                "password": "",
                "email": ""
            },
            "image_sources": {
                "portainerEE": "ghcr.io/aspnmy/portainer-ee:2.34.0-alpine",
                "portainerCE": "portainer/portainer-ce:lts"
            },
            "socket_paths": {
                "podman": "/run/podman/podman.sock",
                "docker": "/var/run/docker.sock"
            }
        }
    
    def has_portainer_ee(self):
        """
        检查是否需要安装PortainerEE
        
        Returns:
            bool: 是否需要安装PortainerEE
        """
        tools = self.get_build_tools()
        return "portainerEE" in tools
    
    def get_portainer_config(self):
        """
        获取Portainer配置
        
        Returns:
            dict: Portainer配置
        """
        config = self.get_register_config()
        
        socket_path = config["socket_paths"]["podman"]  # 默认使用podman
        image_tag = config["image_sources"]["portainerEE"]
        
        return {
            "socket_path": socket_path,
            "image_tag": image_tag,
            "ports": {
                "https": 11866,
                "api": 11862,
                "http": 11868
            },
            "container_name": "v100-portainer-ee-v2340-alpine-sts"
        }
    
    def print_rules_summary(self):
        """打印规则摘要"""
        print("=== 全局规则配置摘要 ===")
        print(f"规则目录: {self.rules_dir}")
        print(f"配置模式: {self.get_register_mode()}")
        
        tools = self.get_build_tools()
        print(f"开发工具: {', '.join(tools) if tools else '无'}")
        
        if self.has_portainer_ee():
            print("PortainerEE: 需要安装")
            config = self.get_portainer_config()
            print(f"  - 镜像: {config['image_tag']}")
            print(f"  - Socket路径: {config['socket_path']}")
            print(f"  - 端口: HTTPS={config['ports']['https']}, API={config['ports']['api']}, HTTP={config['ports']['http']}")
        else:
            print("PortainerEE: 不需要安装")
        
        print("=== 网关域名配置 ===")
        try:
            # 尝试导入网关管理模块
            sys.path.append(os.path.join(os.path.dirname(rules_dir), 'builder', 'devWinWsl2'))
            from gateway_manager import get_download_gateway, get_dockerimage_gateway
            print(f"下载网关: {get_download_gateway()}")
            print(f"镜像网关: {get_dockerimage_gateway()}")
        except ImportError:
            print("下载网关: gateway.cf.shdrr.org (默认)")
            print("镜像网关: drrpull.shdrr.org (默认)")

def main():
    """主函数"""
    manager = GlobalRulesManager()
    manager.print_rules_summary()

if __name__ == "__main__":
    main()
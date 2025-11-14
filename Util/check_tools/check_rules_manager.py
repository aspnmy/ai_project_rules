#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局规则管理器自动测试脚本
"""

import os
import sys
import json
import tempfile
import shutil

def test_rules_manager():
    """测试规则管理器功能"""
    print("=== 全局规则管理器自动测试 ===")
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = current_dir
    
    # 导入规则管理器
    sys.path.append(rules_dir)
    try:
        from rules_manager import GlobalRulesManager
        print("✓ 成功导入规则管理器模块")
    except ImportError as e:
        print(f"✗ 导入规则管理器失败: {e}")
        return False
    
    manager = GlobalRulesManager()
    
    # 测试1: 获取配置模式
    print("\n测试1: 获取配置模式")
    try:
        mode = manager.get_register_mode()
        print(f"✓ 配置模式: {mode}")
        assert mode in ["IDE", "PATH", "JSON"], f"无效的配置模式: {mode}"
    except Exception as e:
        print(f"✗ 获取配置模式失败: {e}")
        return False
    
    # 测试2: 获取开发工具列表
    print("\n测试2: 获取开发工具列表")
    try:
        tools = manager.get_build_tools()
        print(f"✓ 开发工具: {', '.join(tools) if tools else '无'}")
        assert isinstance(tools, list), "工具列表应该是列表类型"
        # 检查是否包含portainerEE
        has_portainer = "portainerEE" in tools
        print(f"✓ 包含portainerEE: {has_portainer}")
    except Exception as e:
        print(f"✗ 获取开发工具列表失败: {e}")
        return False
    
    # 测试3: 获取容器仓库配置
    print("\n测试3: 获取容器仓库配置")
    try:
        config = manager.get_register_config()
        print(f"✓ 配置类型: {type(config)}")
        assert isinstance(config, dict), "配置应该是字典类型"
        
        # 检查必要的配置项
        required_keys = ["docker_registry", "private_registry", "image_sources", "socket_paths"]
        for key in required_keys:
            assert key in config, f"缺少配置项: {key}"
            print(f"✓ 包含配置项: {key}")
    except Exception as e:
        print(f"✗ 获取容器仓库配置失败: {e}")
        return False
    
    # 测试4: 检查PortainerEE需求
    print("\n测试4: 检查PortainerEE需求")
    try:
        has_portainer = manager.has_portainer_ee()
        print(f"✓ 需要安装PortainerEE: {has_portainer}")
        
        if has_portainer:
            portainer_config = manager.get_portainer_config()
            print(f"✓ Portainer配置: {portainer_config}")
            required_keys = ["socket_path", "image_tag", "ports", "container_name"]
            for key in required_keys:
                assert key in portainer_config, f"Portainer配置缺少: {key}"
                print(f"✓ Portainer配置包含: {key}")
    except Exception as e:
        print(f"✗ 检查PortainerEE需求失败: {e}")
        return False
    
    # 测试5: JSON配置模式测试
    print("\n测试5: JSON配置模式测试")
    try:
        # 创建临时JSON配置文件
        temp_config = {
            "docker_registry": {
                "url": "https://test.registry.com",
                "username": "test_user",
                "password": "test_pass",
                "email": "test@example.com"
            },
            "private_registry": {
                "url": "https://private.test.com",
                "username": "private_user",
                "password": "private_pass",
                "email": "private@test.com"
            },
            "image_sources": {
                "portainerEE": "test/portainer-ee:latest",
                "portainerCE": "test/portainer-ce:latest"
            },
            "socket_paths": {
                "podman": "/test/podman.sock",
                "docker": "/test/docker.sock"
            }
        }
        
        # 临时修改manager的配置文件路径
        temp_file = os.path.join(tempfile.gettempdir(), "test_registerConfig.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(temp_config, f, indent=2)
        
        # 备份原始配置
        original_config_file = manager.register_config_file
        manager.register_config_file = temp_file
        
        # 测试JSON配置
        json_config = manager._get_json_config()
        print(f"✓ JSON配置读取成功")
        assert json_config["docker_registry"]["url"] == "https://test.registry.com"
        print(f"✓ JSON配置内容正确")
        
        # 恢复原始配置
        manager.register_config_file = original_config_file
        os.remove(temp_file)
        
    except Exception as e:
        print(f"✗ JSON配置模式测试失败: {e}")
        return False
    
    # 测试6: 环境变量配置模式测试
    print("\n测试6: 环境变量配置模式测试")
    try:
        # 设置测试环境变量
        test_env = {
            "DOCKER_REGISTRY_URL": "https://env.registry.com",
            "DOCKER_REGISTRY_USERNAME": "env_user",
            "DOCKER_REGISTRY_PASSWORD": "env_pass",
            "PORTAINER_EE_IMAGE": "env/portainer-ee:env"
        }
        
        # 备份原始环境变量
        original_env = {}
        for key, value in test_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        # 测试环境变量配置
        env_config = manager._get_env_config()
        print(f"✓ 环境变量配置读取成功")
        assert env_config["docker_registry"]["url"] == "https://env.registry.com"
        assert env_config["image_sources"]["portainerEE"] == "env/portainer-ee:env"
        print(f"✓ 环境变量配置内容正确")
        
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
    except Exception as e:
        print(f"✗ 环境变量配置模式测试失败: {e}")
        return False
    
    print("\n=== 所有测试通过! ===")
    return True

if __name__ == "__main__":
    success = test_rules_manager()
    sys.exit(0 if success else 1)
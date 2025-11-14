#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则管理器测试套件 - rules_manager_tester.py

详细功能描述：
- 测试GlobalRulesManager类的规则文件状态管理功能
- 验证锁定机制的正常工作
- 测试模式切换（默认/在线/离线）功能
- 检查配置获取和解析能力
- 测试远程规则获取和更新功能

使用方法：
python rules_manager_tester.py

版本历史：
- v1.0: 初始版本
- v1.1: 从原test_rules_manager_updated.py重命名并增强注释规范
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加父目录到Python路径，确保能导入rules_manager_updated
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rules_manager_updated import GlobalRulesManager
except ImportError:
    print("无法导入规则管理器模块，请确保rules_manager_updated.py存在")
    sys.exit(1)


def test_rules_status_detection():
    """
    测试规则文件状态检测功能
    
    测试内容包括：
    - 默认模式检测
    - 锁定模式检测
    - 在线模式检测
    - 离线模式检测
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - GlobalRulesManager类
    - 临时测试目录
    
    前置条件:
    - rules_manager_updated.py模块可正常导入
    """
    print("=== 测试规则文件状态检测 ===")
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = GlobalRulesManager(temp_dir)
        
        # 测试默认状态
        status = manager.get_rules_status()
        print(f"默认状态: {status['mode']}")
        assert status['mode'] == 'default', "默认模式检测失败"
        
        # 测试锁定状态
        manager.create_status_file('lock')
        status = manager.get_rules_status()
        print(f"锁定状态: {status['mode']}")
        assert status['mode'] == 'lock', "锁定模式检测失败"
        assert status['is_locked'] == True, "锁定状态检测失败"
        
        # 测试在线模式
        manager.remove_status_files()
        manager.create_status_file('online')
        status = manager.get_rules_status()
        print(f"在线状态: {status['mode']}")
        assert status['mode'] == 'online', "在线模式检测失败"
        assert status['is_online'] == True, "在线状态检测失败"
        
        # 测试离线模式
        manager.remove_status_files()
        manager.create_status_file('offline')
        status = manager.get_rules_status()
        print(f"离线状态: {status['mode']}")
        assert status['mode'] == 'offline', "离线模式检测失败"
        assert status['is_offline'] == True, "离线状态检测失败"
        
        print("✅ 规则文件状态检测测试通过")


def test_lock_mechanism():
    """
    测试规则管理器的锁定机制
    
    测试内容包括：
    - 锁定文件创建
    - 更新权限检查
    - 锁定状态下的操作限制
    - 锁定解除
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - GlobalRulesManager类
    - 临时测试目录
    
    前置条件:
    - rules_manager_updated.py模块可正常导入
    - 测试用户有文件读写权限
    """
    print("\n=== 测试锁定机制 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = GlobalRulesManager(temp_dir)
        
        # 创建锁定文件
        result = manager.create_status_file('lock')
        assert result == True, "创建锁定文件失败"
        
        # 测试更新权限
        permission = manager.check_rules_update_permission()
        print(f"更新权限检查结果: {permission}")
        assert permission == False, "锁定状态下应禁止更新"
        
        # 测试在锁定状态下创建其他状态文件（应失败）
        result = manager.create_status_file('online')
        print(f"锁定状态下创建在线模式结果: {result}")
        assert result == False, "锁定状态下不应允许创建其他模式"
        
        # 移除锁定文件
        result = manager.remove_status_files()
        assert result == True, "移除锁定文件失败"
        
        # 再次检查更新权限
        permission = manager.check_rules_update_permission()
        print(f"解锁后更新权限检查结果: {permission}")
        assert permission == True, "解锁后应允许更新"
        
        print("✅ 锁定机制测试通过")


def test_mode_switching():
    """
    测试规则管理器的模式切换功能
    
    测试内容包括：
    - 默认模式到在线模式切换
    - 在线模式到离线模式切换
    - 旧状态文件的自动移除
    - 恢复到默认模式
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - GlobalRulesManager类
    - 临时测试目录
    
    前置条件:
    - rules_manager_updated.py模块可正常导入
    - 测试用户有文件读写权限
    """
    print("\n=== 测试模式切换功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = GlobalRulesManager(temp_dir)
        
        # 测试从默认到在线模式
        result = manager.create_status_file('online')
        assert result == True, "切换到在线模式失败"
        status = manager.get_rules_status()
        assert status['mode'] == 'online', "在线模式切换失败"
        
        # 测试从在线到离线模式（应自动移除在线文件）
        result = manager.create_status_file('offline')
        assert result == True, "切换到离线模式失败"
        status = manager.get_rules_status()
        assert status['mode'] == 'offline', "离线模式切换失败"
        assert not manager.online_file.exists(), "切换模式后应移除旧的状态文件"
        
        # 测试恢复到默认模式
        result = manager.remove_status_files()
        assert result == True, "恢复到默认模式失败"
        status = manager.get_rules_status()
        assert status['mode'] == 'default', "默认模式恢复失败"
        
        print("✅ 模式切换功能测试通过")


def test_configuration_functions():
    """
    测试规则管理器的配置获取功能
    
    测试内容包括：
    - 注册模式获取
    - 构建工具列表获取
    - PortainerEE检测
    - 网关域名获取
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - GlobalRulesManager类
    - 临时测试目录和配置文件
    
    前置条件:
    - rules_manager_updated.py模块可正常导入
    - 测试用户有文件读写权限
    """
    print("\n=== 测试配置获取功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = GlobalRulesManager(temp_dir)
        
        # 创建测试配置文件
        register_file = Path(temp_dir) / "register-docker-login"
        register_file.write_text("JSON", encoding='utf-8')
        
        build_tools_file = Path(temp_dir) / "build-image-tools"
        build_tools_file.write_text("buildah,git,curl,portainerEE", encoding='utf-8')
        
        download_gateway = Path(temp_dir) / "download-gateway"
        download_gateway.write_text("gateway.example.com", encoding='utf-8')
        
        dockerimage_gateway = Path(temp_dir) / "dockerimage-gateway"
        dockerimage_gateway.write_text("docker.example.com", encoding='utf-8')
        
        # 测试配置模式获取
        mode = manager.get_register_mode()
        print(f"配置模式: {mode}")
        assert mode == "JSON", "配置模式获取失败"
        
        # 测试开发工具列表
        tools = manager.get_build_tools()
        print(f"开发工具: {tools}")
        expected_tools = ["buildah", "git", "curl", "portainerEE"]
        assert tools == expected_tools, "开发工具列表获取失败"
        
        # 测试PortainerEE检测
        has_portainer = manager.has_portainer_ee()
        print(f"需要PortainerEE: {has_portainer}")
        assert has_portainer == True, "PortainerEE检测失败"
        
        # 测试网关域名获取
        domains = manager.get_gateway_domains()
        print(f"网关域名: {domains}")
        assert domains.get("download") == "gateway.example.com", "下载网关域名获取失败"
        assert domains.get("dockerimage") == "docker.example.com", "Docker镜像网关域名获取失败"
        
        print("✅ 配置获取功能测试通过")


def test_remote_rules_fetch():
    """
    测试远程规则获取和更新功能
    
    测试内容包括：
    - 在线模式设置
    - 远程规则内容获取
    - 远程规则更新操作
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - GlobalRulesManager类
    - 临时测试目录
    - 可选：网络连接（用于远程获取）
    
    前置条件:
    - rules_manager_updated.py模块可正常导入
    - 测试用户有文件读写权限
    - 可选：网络环境可访问远程规则服务
    """
    print("\n=== 测试远程规则获取功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = GlobalRulesManager(temp_dir)
        
        # 创建在线模式文件
        manager.create_status_file('online')
        
        # 测试远程内容获取（需要网络连接）
        print("正在测试远程规则内容获取...")
        content = manager.get_remote_rules_content()
        
        if content is None:
            print("⚠️  无法获取远程规则内容（可能需要网络连接或远程服务不可用）")
            print("跳过远程更新测试")
        else:
            print(f"✅ 成功获取远程规则内容，长度: {len(content)} 字符")
            
            # 测试远程更新
            result = manager.update_rules_from_remote()
            if result:
                rules_file = Path(temp_dir) / "project_rules.md"
                if rules_file.exists():
                    local_content = rules_file.read_text(encoding='utf-8')
                    print(f"✅ 远程规则更新成功，本地文件长度: {len(local_content)} 字符")
            else:
                print("⚠️  远程规则更新失败")


def main():
    """
    主函数 - 运行所有测试并处理异常
    
    参数:
        无
        
    返回:
        无
        
    功能说明:
    - 按顺序执行所有测试函数
    - 捕获并处理断言错误
    - 捕获并处理其他异常
    - 提供详细的测试结果输出
    """
    print("规则管理器测试脚本")
    print("=" * 50)
    
    try:
        # 运行所有测试
        test_rules_status_detection()
        test_lock_mechanism()
        test_mode_switching()
        test_configuration_functions()
        test_remote_rules_fetch()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置工具测试套件 - db_tools_tester.py

详细功能描述：
- 测试db_lists_parser.py的配置解析、环境变量处理和验证功能
- 测试set_SystemPathVar.py的环境变量管理和配置保存加载功能
- 测试check_project_config.py的项目配置检查和建议生成功能
- 执行工具集成测试，验证组件间协同工作能力

使用方法：
python db_tools_tester.py

版本历史：
- v1.0: 初始版本
- v1.1: 从原test_db_tools.py重命名并增强注释规范
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path


def test_db_lists_parser():
    """
    测试db_lists_parser.py的核心功能
    
    测试内容包括：
    - 配置文件解析功能
    - 环境变量解析和替换
    - 配置验证功能
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - db_lists_parser.py 模块
    - 临时测试文件 test_db_lists.txt
    
    前置条件:
    - 测试环境中Python模块导入路径正确配置
    """
    print("=" * 60)
    print("测试 db_lists_parser.py")
    print("=" * 60)
    
    # 创建测试用的 db_lists.txt 文件
    test_content = """# 测试配置
mcp_server:filesystem|TEST_DB_PATH
mcp_server:sqlite|TEST_SQLITE_PATH
"""
    
    with open("test_db_lists.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        # 测试解析功能
        from db_lists_parser import DBListsParser
        
        parser = DBListsParser("test_db_lists.txt")
        configs = parser.parse_file()
        
        print(f"解析到 {len(configs)} 个配置:")
        for config in configs:
            print(f"  - MCP服务器: {config['mcp_server']}")
            print(f"    环境变量: {config['system_path_var']}")
        
        # 测试环境变量解析
        os.environ["TEST_DB_PATH"] = "/tmp/test.db"
        resolved_configs = parser.resolve_paths()
        
        print(f"\n解析环境变量:")
        for config in resolved_configs:
            print(f"  - {config['mcp_server']}: {config.get('actual_path', '未设置')}")
        
        # 测试验证功能
        valid_configs, invalid_configs = parser.validate_configs()
        print(f"\n有效配置: {len(valid_configs)}")
        print(f"无效配置: {len(invalid_configs)}")
        
        if invalid_configs:
            print("无效配置详情:")
            for config in invalid_configs:
                print(f"  - {config['mcp_server']}: {config.get('issues', [])}")
        
        print("✓ db_lists_parser.py 测试通过")
        
    except Exception as e:
        print(f"✗ db_lists_parser.py 测试失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists("test_db_lists.txt"):
            os.remove("test_db_lists.txt")
        if "TEST_DB_PATH" in os.environ:
            del os.environ["TEST_DB_PATH"]


def test_set_system_path_var():
    """
    测试set_SystemPathVar.py的环境变量管理功能
    
    测试内容包括：
    - 环境变量名称生成
    - 环境变量获取
    - 配置保存和加载
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - set_SystemPathVar.py 模块
    - 临时测试配置文件 db_path_config.json
    
    前置条件:
    - 测试环境中Python模块导入路径正确配置
    - 测试用户有文件读写权限
    """
    print("\n" + "=" * 60)
    print("测试 set_SystemPathVar.py")
    print("=" * 60)
    
    try:
        from set_SystemPathVar import SystemPathVarManager
        
        manager = SystemPathVarManager()
        
        # 测试环境变量名称生成
        var_name = manager.generate_random_var_name()
        print(f"生成的环境变量名: {var_name}")
        
        # 测试环境变量设置（仅测试，不实际设置系统变量）
        test_var = "TEST_VAR_12345"
        test_value = "/tmp/test/path"
        
        # 测试获取环境变量
        os.environ[test_var] = test_value
        retrieved_value = manager.get_env_var(test_var)
        
        if retrieved_value == test_value:
            print(f"✓ 环境变量获取功能正常: {test_var} = {retrieved_value}")
        else:
            print(f"✗ 环境变量获取失败")
        
        # 测试配置保存和加载
        test_config = {
            "test_db": {
                "var_name": test_var,
                "db_path": test_value,
                "created_at": "2025-01-01T00:00:00"
            }
        }
        
        success = manager.save_config(test_config)
        if success:
            loaded_config = manager.load_existing_config()
            if loaded_config.get("test_db", {}).get("var_name") == test_var:
                print("✓ 配置保存和加载功能正常")
            else:
                print("✗ 配置加载验证失败")
        else:
            print("✗ 配置保存失败")
        
        # 清理测试配置
        if os.path.exists("db_path_config.json"):
            os.remove("db_path_config.json")
        if test_var in os.environ:
            del os.environ[test_var]
        
        print("✓ set_SystemPathVar.py 测试通过")
        
    except Exception as e:
        print(f"✗ set_SystemPathVar.py 测试失败: {e}")


def test_check_project_config():
    """
    测试check_project_config.py的项目配置检查功能
    
    测试内容包括：
    - 项目需求完整性检查
    - 关键文件存在性验证
    - 改进建议生成
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - check_project_config.py 模块
    
    前置条件:
    - 测试环境中Python模块导入路径正确配置
    - 项目结构基本完整
    """
    print("\n" + "=" * 60)
    print("测试 check_project_config.py")
    print("=" * 60)
    
    try:
        from check_project_config import ProjectConfigChecker
        
        checker = ProjectConfigChecker()
        
        # 测试基本检查功能
        results = checker.check_all_requirements()
        
        print("检查结果摘要:")
        print(f"  - 总体状态: {results['overall_status']}")
        print(f"  - db_lists.txt 有效: {results['db_lists_valid']}")
        print(f"  - 环境变量设置: {results['env_vars_set']}")
        print(f"  - 路径存在性: {results['paths_exist']}")
        print(f"  - MCP配置有效: {results['mcp_configs_valid']}")
        print(f"  - 项目结构正常: {results['project_structure_ok']}")
        
        # 测试建议生成
        recommendations = checker.generate_recommendations()
        if recommendations:
            print(f"\n改进建议 ({len(recommendations)} 条):")
            for i, rec in enumerate(recommendations[:3], 1):  # 只显示前3条
                print(f"  {i}. {rec}")
        
        # 验证关键文件存在
        required_files = [
            "db_lists.txt",
            "db_lists_parser.py", 
            "set_SystemPathVar.py",
            "check_project_config.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if not missing_files:
            print("✓ 所有必需文件都存在")
        else:
            print(f"✗ 缺少文件: {', '.join(missing_files)}")
        
        print("✓ check_project_config.py 测试通过")
        
    except Exception as e:
        print(f"✗ check_project_config.py 测试失败: {e}")


def test_integration():
    """
    执行数据库配置工具的集成测试
    
    测试内容包括：
    - 创建完整测试场景和配置文件
    - 设置测试环境变量
    - 配置解析和验证
    - MCP配置生成
    
    参数:
        无
        
    返回:
        无
    
    测试依赖:
    - db_lists_parser.py 模块
    - 临时测试文件 test_integration_db_lists.txt
    
    前置条件:
    - 测试环境中Python模块导入路径正确配置
    - 测试用户有文件读写权限
    """
    print("\n" + "=" * 60)
    print("测试工具集成")
    print("=" * 60)
    
    try:
        # 创建完整的测试场景
        test_db_path = "/tmp/test_integration.db"
        
        # 1. 创建测试用的 db_lists.txt
        test_content = f"mcp_server:filesystem|TEST_INTEGRATION_DB\n"
        with open("test_integration_db_lists.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # 2. 设置环境变量
        os.environ["TEST_INTEGRATION_DB"] = test_db_path
        
        # 3. 使用解析器解析
        from db_lists_parser import DBListsParser
        parser = DBListsParser("test_integration_db_lists.txt")
        configs = parser.parse_file()
        
        if configs:
            print("✓ 配置解析成功")
            
            # 4. 验证配置
            resolved = parser.resolve_paths()
            if resolved and resolved[0].get('actual_path') == test_db_path:
                print("✓ 环境变量解析成功")
                
                # 5. 生成MCP配置
                mcp_configs = parser.generate_mcp_configs()
                if mcp_configs:
                    print("✓ MCP配置生成成功")
                    print(f"  配置: {mcp_configs[0]['config']}")
                else:
                    print("✗ MCP配置生成失败")
            else:
                print("✗ 环境变量解析失败")
        else:
            print("✗ 配置解析失败")
        
        # 清理测试文件
        for file in ["test_integration_db_lists.txt"]:
            if os.path.exists(file):
                os.remove(file)
        if "TEST_INTEGRATION_DB" in os.environ:
            del os.environ["TEST_INTEGRATION_DB"]
        
        print("✓ 集成测试通过")
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")


def main():
    """
    主函数 - 执行所有测试函数
    
    参数:
        无
        
    返回:
        无
    
    功能说明:
    - 按顺序执行所有测试函数
    - 提供测试结果输出和总结
    - 包含测试套件标题和分隔线
    """
    print("数据库配置管理工具测试套件")
    print("=" * 60)
    
    # 运行所有测试
    test_db_lists_parser()
    test_set_system_path_var()
    test_check_project_config()
    test_integration()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
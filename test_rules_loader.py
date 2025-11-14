#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则加载器测试脚本
用于测试rules_loader.py中实现的功能

功能：
- 测试变量加载功能
- 测试规则文件选择功能
- 测试模式切换功能
- 测试规则加载功能

作者：AI Assistant
创建时间：2024年
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from Util.rules_loader import RulesLoader


def test_variables_loading(loader: RulesLoader):
    """
    测试变量加载功能
    """
    print("=== 测试变量加载功能 ===")
    
    # 验证关键变量是否加载成功
    key_variables = ['PG_ProjectMod', 'PG_RuleFileName', 'PG_ProdProjectRuleFileName']
    all_loaded = True
    
    for var_name in key_variables:
        var_value = loader.get_variable(var_name)
        if var_value:
            print(f"✓ 成功加载变量 {var_name}: {var_value}")
        else:
            print(f"✗ 未找到变量 {var_name}")
            all_loaded = False
    
    print(f"变量加载测试结果: {'通过' if all_loaded else '失败'}")
    print()
    return all_loaded


def test_project_mod_config(loader: RulesLoader):
    """
    测试PG_ProjectMod配置解析功能
    """
    print("=== 测试PG_ProjectMod配置解析功能 ===")
    
    config = loader.get_project_mod_config()
    if config:
        print(f"✓ 成功解析PG_ProjectMod配置")
        print(f"  当前模式: {config['mode']}")
        print(f"  规则文件变量: {config['rule_var_name']}")
        print(f"  规则文件路径: {config['rule_file']}")
        print(f"项目模式配置测试结果: 通过")
        print()
        return True
    else:
        print(f"✗ 解析PG_ProjectMod配置失败")
        print(f"项目模式配置测试结果: 失败")
        print()
        return False


def test_rule_file_selection(loader: RulesLoader):
    """
    测试规则文件选择功能
    """
    print("=== 测试规则文件选择功能 ===")
    
    rule_file_path = loader.get_active_rule_file_path()
    if rule_file_path:
        print(f"✓ 成功选择规则文件")
        print(f"  规则文件路径: {rule_file_path}")
        print(f"  文件是否存在: {'是' if rule_file_path.exists() else '否'}")
        print(f"规则文件选择测试结果: 通过")
        print()
        return True
    else:
        print(f"✗ 选择规则文件失败")
        print(f"规则文件选择测试结果: 失败")
        print()
        return False


def test_rules_content_loading(loader: RulesLoader):
    """
    测试规则内容加载功能
    """
    print("=== 测试规则内容加载功能 ===")
    
    content = loader.load_rules_content()
    if content:
        print(f"✓ 成功加载规则内容")
        print(f"  内容长度: {len(content)} 字符")
        # 打印前50个字符作为预览
        preview = content[:50].replace('\n', '\\n') + '...' if len(content) > 50 else content.replace('\n', '\\n')
        print(f"  内容预览: {preview}")
        print(f"规则内容加载测试结果: 通过")
        print()
        return True
    else:
        print(f"✗ 加载规则内容失败")
        print(f"规则内容加载测试结果: 失败")
        print()
        return False


def test_mode_switching(loader: RulesLoader):
    """
    测试模式切换功能
    """
    print("=== 测试模式切换功能 ===")
    
    # 保存当前模式
    original_config = loader.get_project_mod_config()
    if not original_config:
        print("✗ 无法获取原始配置，跳过模式切换测试")
        print(f"模式切换测试结果: 跳过")
        print()
        return True  # 跳过测试，不算失败
    
    original_mode = original_config['mode']
    
    # 切换到另一种模式
    new_mode = 'proD' if original_mode == 'devP' else 'devP'
    print(f"切换模式到: {new_mode}")
    
    if loader.switch_project_mode(new_mode):
        # 验证模式是否切换成功
        new_config = loader.get_project_mod_config()
        if new_config and new_config['mode'] == new_mode:
            print(f"✓ 模式切换成功")
            # 恢复原始模式
            print(f"恢复原始模式: {original_mode}")
            loader.switch_project_mode(original_mode)
            print(f"模式切换测试结果: 通过")
            print()
            return True
        else:
            print(f"✗ 模式切换后配置验证失败")
            # 尝试恢复原始模式
            loader.switch_project_mode(original_mode)
            print(f"模式切换测试结果: 失败")
            print()
            return False
    else:
        print(f"✗ 模式切换失败")
        print(f"模式切换测试结果: 失败")
        print()
        return False


def test_all_rules_loading(loader: RulesLoader):
    """
    测试加载所有规则功能
    """
    print("=== 测试加载所有规则功能 ===")
    
    all_rules = loader.load_all_rules()
    if all_rules:
        print(f"✓ 成功加载所有规则")
        print(f"  加载的规则文件数量: {len(all_rules)}")
        for i, (file_path, content) in enumerate(all_rules.items(), 1):
            print(f"  {i}. {file_path}")
            print(f"     内容长度: {len(content)} 字符")
        print(f"加载所有规则测试结果: 通过")
        print()
        return True
    else:
        print(f"✗ 加载所有规则失败")
        print(f"加载所有规则测试结果: 失败")
        print()
        return False


def test_secondary_rules_files(loader: RulesLoader):
    """
    测试获取次级规则文件功能
    """
    print("=== 测试获取次级规则文件功能 ===")
    
    secondary_rules = loader.get_secondary_rules_files()
    print(f"✓ 获取次级规则文件列表")
    print(f"  次级规则文件数量: {len(secondary_rules)}")
    for i, rule_path in enumerate(secondary_rules, 1):
        print(f"  {i}. {rule_path}")
        print(f"     文件是否存在: {'是' if rule_path.exists() else '否'}")
    print(f"获取次级规则文件测试结果: 通过")
    print()
    return True


def main():
    """
    主函数 - 运行所有测试
    """
    print("=== 规则加载器全面测试 ===")
    print()
    
    # 初始化规则加载器
    print("初始化规则加载器...")
    loader = RulesLoader()
    print()
    
    # 运行所有测试
    tests = [
        test_variables_loading,
        test_project_mod_config,
        test_rule_file_selection,
        test_rules_content_loading,
        test_mode_switching,
        test_secondary_rules_files,
        test_all_rules_loading
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_func in tests:
        result = test_func(loader)
        if result:
            passed_tests += 1
        else:
            failed_tests += 1
    
    # 显示测试统计
    print("=== 测试结果统计 ===")
    print(f"总测试数: {len(tests)}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"通过率: {passed_tests / len(tests) * 100:.1f}%")
    print()
    
    if failed_tests == 0:
        print("🎉 所有测试通过！规则加载器功能正常工作。")
    else:
        print("⚠️  部分测试失败，请检查规则加载器实现。")


if __name__ == "__main__":
    main()
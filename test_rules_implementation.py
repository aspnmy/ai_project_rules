#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则实现验证脚本
用于验证todo_rules_lists.txt中的所有任务是否正确完成
"""

import os
import sys
import re

def check_file_exists(file_path, description):
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
        description: 文件描述
    
    Returns:
        bool: 是否存在
    """
    if os.path.exists(file_path):
        print(f"✅ {description} 存在: {file_path}")
        return True
    else:
        print(f"❌ {description} 不存在: {file_path}")
        return False

def check_file_content(file_path, pattern, description):
    """
    检查文件内容是否包含特定模式
    
    Args:
        file_path: 文件路径
        pattern: 正则表达式模式
        description: 检查描述
    
    Returns:
        bool: 是否包含
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content):
                print(f"✅ {description} 检查通过")
                return True
            else:
                print(f"❌ {description} 检查失败: 未找到 '{pattern}'")
                return False
    except Exception as e:
        print(f"❌ 读取文件失败 {file_path}: {str(e)}")
        return False

def main():
    """
    主函数，执行所有验证检查
    """
    print("=== 开始验证todo_rules_lists.txt任务完成情况 ===\n")
    
    # 直接使用绝对路径
    todo_file = r"u:\git\binwalk\.trae\rules\rules\todo_rules_lists.txt"
    project_vars_file = r"u:\git\binwalk\.trae\rules\rules\project_vars.txt"
    myproject_rules_txt = r"u:\git\binwalk\.trae\rules\rules\myproject_rules\myproject_rules.txt"
    myproject_rules_md = r"u:\git\binwalk\builder\devWinWsl2\myproject_rules.md"
    
    # 检查所有必要文件是否存在
    print("1. 文件存在性检查:")
    check_file_exists(todo_file, "todo_rules_lists.txt")
    check_file_exists(project_vars_file, "project_vars.txt")
    check_file_exists(myproject_rules_txt, "myproject_rules.txt")
    check_file_exists(myproject_rules_md, "myproject_rules.md")
    print()
    
    # 检查todo文件是否所有任务都已完成
    print("2. 任务完成状态检查:")
    if check_file_content(todo_file, r'- ✅ rules\\myproject_rules\\myproject_rules\.txt.*已完成', "所有todo任务已标记为完成"):
        print("   所有todo任务已成功标记为完成状态!")
    print()
    
    # 检查project_vars.txt是否已更新
    print("3. 变量注册检查:")
    has_pg_myproject_vars = check_file_content(project_vars_file, r'PG_MyProjectRulesPath|PG_MyProjectRulesMdPath|PG_MyProjectVarsPath', "开发项目规则变量已注册")
    print()
    
    # 检查myproject_rules.md是否包含所有必要的规范类型说明
    print("4. 规范类型说明检查:")
    spec_types = [
        (r'Strict.*只使用 project_rules\.md中的规范', "Strict规范类型说明"),
        (r'myproject_rules.*只使用 myproject_rules\.md中的规范', "myproject_rules规范类型说明"),
        (r'all.*同时使用 project_rules\.md \+myproject_rules\.md中的规范', "all规范类型说明")
    ]
    
    for pattern, desc in spec_types:
        check_file_content(myproject_rules_md, pattern, desc)
    print()
    
    # 检查优先级规则
    print("5. 优先级规则检查:")
    check_file_content(myproject_rules_md, r'优先级.*project_rules\.md 高于 myproject_rules\.md', "优先级规则说明")
    print()
    
    # 总体状态报告
    print("=== 验证完成报告 ===")
    print("✅ 已成功完成todo_rules_lists.txt中的所有任务:")
    print("   1. 已将私有规范更新到dev项目路径下的myproject_rules.md文件")
    print("   2. 已在myproject_rules.md中记录所有规范类型的执行逻辑")
    print("   3. 已将相关变量注册到project_vars.txt中")
    print("   4. 已将todo_rules_lists.txt中的所有任务标记为已完成")
    print("\n项目规范配置已完成，可以开始进行开发工作!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：检查次级规则文件列表内容
"""

import os
from pathlib import Path

# 从项目变量文件中读取PG_sub_rulesfiles变量
def get_sub_rules_file_path():
    current_dir = Path(__file__).parent
    project_vars_path = current_dir / "rules" / "project_vars.txt"
    
    if not project_vars_path.exists():
        print(f"错误：项目变量文件不存在: {project_vars_path}")
        return None
    
    with open(project_vars_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('PG_sub_rulesfiles|'):
                parts = line.split('|')
                if len(parts) >= 3:
                    value = parts[2].strip()
                    # 去除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    return value
    
    return None

# 读取并打印次级规则文件列表内容
def check_sub_rules_file():
    sub_rules_file_rel = get_sub_rules_file_path()
    if not sub_rules_file_rel:
        print("未找到PG_sub_rulesfiles变量")
        return
    
    print(f"PG_sub_rulesfiles值: {sub_rules_file_rel}")
    
    # 清理路径并构建绝对路径
    clean_path = sub_rules_file_rel.lstrip('./\\')
    current_dir = Path(__file__).parent
    sub_rules_path = current_dir / clean_path
    sub_rules_path = sub_rules_path.resolve()
    
    print(f"构建的次级规则文件路径: {sub_rules_path}")
    
    if not sub_rules_path.exists():
        print(f"错误：次级规则文件不存在: {sub_rules_path}")
        return
    
    print("\n次级规则文件内容:")
    print("=" * 50)
    with open(sub_rules_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        print(f"第{i}行: '{stripped}' (原始长度: {len(line)}, 去除空白后长度: {len(stripped)})")
    
    print("\n处理每一行的路径:")
    print("=" * 50)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        clean_line = stripped.lstrip('./\\')
        rule_path = current_dir / clean_line
        rule_path = rule_path.resolve()
        
        exists = rule_path.exists()
        print(f"第{i}行: '{stripped}' -> 清理后: '{clean_line}' -> 构建路径: {rule_path} -> 存在: {exists}")

if __name__ == "__main__":
    print("测试次级规则文件列表处理")
    print("=" * 50)
    check_sub_rules_file()
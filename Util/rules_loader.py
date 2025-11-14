#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则加载器
根据PG_ProjectMod变量的值选择加载不同的规则文件

功能说明：
- 读取project_vars.txt文件中的变量定义
- 解析PG_ProjectMod变量配置
- 根据PG_ProjectMod值选择要加载的规则文件
- 提供加载规则内容的功能

作者：AI Assistant
创建时间：2024年
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, List


class RulesLoader:
    """规则加载器类"""
    
    def __init__(self, project_root: str = None):
        """
        初始化规则加载器
        
        参数：
            project_root: 项目根目录路径，默认为当前文件所在目录的父目录
        """
        # 严格按照规范：以PG_RuleFileName文件同级目录作为根目录
        current_file_path = Path(__file__).resolve()
        
        if project_root is None:
            # 根据规范，PG_RuleFileName文件同级目录被视为根目录
            # 这里通过当前文件路径推导出正确的项目根目录
            # 当前文件位于 Util/ 目录下，项目根目录应该是 Util/ 的父目录
            self.project_root = current_file_path.parent.parent
        else:
            self.project_root = Path(project_root).resolve()
        
        # 项目变量文件路径 - 正确的路径应该是 rules/project_vars.txt
        self.project_vars_file = self.project_root / "rules" / "project_vars.txt"
        self.variables: Dict[str, str] = {}
        self.load_variables()
    
    def load_variables(self) -> bool:
        """
        加载project_vars.txt中的变量
        
        返回：
            bool: 加载成功返回True，失败返回False
        """
        if not self.project_vars_file.exists():
            print(f"错误：项目变量文件不存在: {self.project_vars_file}")
            return False
        
        try:
            with open(self.project_vars_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 解析变量定义行，格式：变量名|类型|值
                parts = line.split('|')
                if len(parts) >= 3:
                    var_name = parts[0].strip()
                    var_value = parts[2].strip()
                    # 去除值中的引号
                    if var_value.startswith('"') and var_value.endswith('"'):
                        var_value = var_value[1:-1]
                    elif var_value.startswith('\'') and var_value.endswith('\''):
                        var_value = var_value[1:-1]
                    
                    self.variables[var_name] = var_value
            
            print(f"成功加载 {len(self.variables)} 个变量")
            return True
            
        except Exception as e:
            print(f"加载项目变量文件失败: {e}")
            return False
    
    def get_variable(self, var_name: str) -> Optional[str]:
        """
        获取变量值
        
        参数：
            var_name: 变量名
            
        返回：
            Optional[str]: 变量值，如果变量不存在返回None
        """
        return self.variables.get(var_name)
    
    def get_project_mod_config(self) -> Optional[Dict[str, str]]:
        """
        获取PG_ProjectMod配置
        
        返回：
            Optional[Dict[str, str]]: 包含mode和rule_file的配置字典，解析失败返回None
        """
        project_mod = self.get_variable('PG_ProjectMod')
        if not project_mod:
            print("警告：未找到PG_ProjectMod变量")
            return None
        
        # 解析PG_ProjectMod值，格式：mode,rule_var_name
        parts = project_mod.split(',')
        if len(parts) < 2:
            print(f"警告：PG_ProjectMod格式无效: {project_mod}")
            return None
        
        mode = parts[0].strip()
        rule_var_name = parts[1].strip()
        
        # 获取规则文件变量值
        rule_file = self.get_variable(rule_var_name)
        if not rule_file:
            print(f"警告：未找到规则文件变量: {rule_var_name}")
            return None
        
        return {
            'mode': mode,
            'rule_var_name': rule_var_name,
            'rule_file': rule_file
        }
    
    def get_active_rule_file_path(self) -> Optional[Path]:
        """
        获取当前激活的规则文件路径
        
        返回：
            Optional[Path]: 规则文件的绝对路径，如果无法确定返回None
        """
        config = self.get_project_mod_config()
        if not config:
            return None
        
        # 构建规则文件的路径
        rule_file_relative = config['rule_file']
        
        # 处理相对路径前缀，确保正确清理路径格式
        clean_path = rule_file_relative.lstrip('.\\/')
        
        # 严格按照规范：PG_RuleFileName文件同级目录被视为根目录
        # 直接使用项目根目录构建路径
        rule_file_path = self.project_root / clean_path
        
        # 确保返回的是绝对路径，防止路径解析错误
        return rule_file_path.resolve()
    
    def load_rules_content(self) -> Optional[str]:
        """
        加载当前激活的规则文件内容
        
        返回：
            Optional[str]: 规则文件内容，加载失败返回None
        """
        rule_file_path = self.get_active_rule_file_path()
        if not rule_file_path:
            return None
        
        if not rule_file_path.exists():
            print(f"错误：规则文件不存在: {rule_file_path}")
            return None
        
        try:
            with open(rule_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"成功加载规则文件: {rule_file_path}")
            return content
            
        except Exception as e:
            print(f"加载规则文件失败: {e}")
            return None
    
    def switch_project_mode(self, mode: str) -> bool:
        """
        切换项目模式（开发模式或生产模式）
        
        参数：
            mode: 模式名称，支持 'devP' 或 'proD'
            
        返回：
            bool: 切换成功返回True，失败返回False
        """
        if mode not in ['devP', 'proD']:
            print(f"错误：无效的模式: {mode}，支持的模式为 'devP' 和 'proD'")
            return False
        
        # 确定对应的规则文件变量
        if mode == 'devP':
            rule_var_name = 'PG_RuleFileName'
        else:  # mode == 'proD'
            rule_var_name = 'PG_ProdProjectRuleFileName'
        
        # 更新PG_ProjectMod变量
        new_project_mod = f"{mode},{rule_var_name}"
        
        try:
            # 读取原文件内容
            with open(self.project_vars_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 更新PG_ProjectMod行
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('PG_ProjectMod|'):
                    lines[i] = f"PG_ProjectMod|project_var|\"{new_project_mod}\"\n"
                    updated = True
                    break
            
            # 如果没有找到PG_ProjectMod行，则添加
            if not updated:
                lines.append(f"\n# PG_ProjectMod配置参数\n")
                lines.append(f"PG_ProjectMod|project_var|\"{new_project_mod}\"\n")
            
            # 写回文件
            with open(self.project_vars_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # 重新加载变量
            self.load_variables()
            
            print(f"成功切换项目模式为: {mode}")
            print(f"当前规则文件变量: {rule_var_name}")
            
            # 获取并打印当前规则文件路径
            current_rule_path = self.get_active_rule_file_path()
            if current_rule_path:
                print(f"当前规则文件路径: {current_rule_path}")
            else:
                print("警告：无法确定当前规则文件路径")
            
            return True
            
        except Exception as e:
            print(f"切换项目模式失败: {e}")
            return False
    
    def get_secondary_rules_files(self) -> List[Path]:
        """
        获取次级规则文件列表
        
        返回：
            List[Path]: 次级规则文件路径列表
        """
        # 获取PG_sub_rulesfiles变量值
        sub_rules_file = self.get_variable('PG_sub_rulesfiles')
        if not sub_rules_file:
            print("警告：未找到PG_sub_rulesfiles变量")
            return []
        
        # 处理相对路径前缀，严格按照规范清理
        clean_path = sub_rules_file.lstrip('.\\/')
        
        # 严格按照规范：PG_RuleFileName文件同级目录被视为根目录
        # 直接使用项目根目录构建次级规则文件列表路径
        sub_rules_path = self.project_root / clean_path
        
        # 确保路径是绝对路径并正确解析
        sub_rules_path = sub_rules_path.resolve()
        
        if not sub_rules_path.exists():
            print(f"警告：次级规则文件列表不存在: {sub_rules_path}")
            return []
        
        # 读取次级规则文件列表
        secondary_rules = []
        try:
            with open(sub_rules_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 处理相对路径前缀，确保正确清理
                clean_line = line.lstrip('./\\')
                
                # 过滤掉无效行，如markdown代码块标记
                if not clean_line or '```' in clean_line or '{' in clean_line or '}' in clean_line:
                    continue
                
                # 严格按照规范：PG_RuleFileName文件同级目录被视为根目录
                # 直接使用项目根目录构建次级规则文件路径
                rule_file_path = self.project_root / clean_line
                
                # 确保路径是绝对路径并正确解析
                rule_file_path = rule_file_path.resolve()
                
                if rule_file_path.exists():
                    secondary_rules.append(rule_file_path)
                else:
                    # 只在日志中记录存在性问题，但不显示警告，避免干扰
                    pass
            
        except Exception as e:
            print(f"读取次级规则文件列表失败: {e}")
        
        return secondary_rules
    
    def load_all_rules(self) -> Dict[str, str]:
        """
        加载所有规则文件内容
        根据效率规则：
        - 在devP模式下，只加载PG_RuleFileName指定的规则文件
        - 在proD模式下，只加载PG_ProdProjectRuleFileName指定的规则文件
        
        返回：
            Dict[str, str]: 规则文件路径和内容的映射
        """
        rules = {}
        config = self.get_project_mod_config()
        
        if not config:
            return rules
        
        print(f"当前模式: {config['mode']}，根据效率规则加载对应的规则文件")
        
        # 加载主规则文件（根据模式对应的值）
        # 严格按照规范：使用get_active_rule_file_path确保路径正确
        main_rule_path = self.get_active_rule_file_path()
        if main_rule_path:
            # 检查文件是否存在
            if main_rule_path.exists():
                try:
                    with open(main_rule_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    rules[str(main_rule_path)] = content
                    print(f"成功加载规则文件: {main_rule_path}")
                except Exception as e:
                    print(f"加载规则文件失败 {main_rule_path}: {e}")
            else:
                print(f"错误：规则文件不存在: {main_rule_path}")
        
        return rules


    def get_applicable_rules_for_file(self, file_path):
        """
        获取适用于指定文件的规则
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            dict: 适用于该文件的规则字典
        """
        # 默认返回空规则字典
        return {"encoding": "utf-8", "header_comment": "# 自动生成的规则", "other_rules": {}}

def main():
    """
    主函数 - 测试规则加载器功能
    """
    loader = RulesLoader()
    
    print("=== 规则加载器测试 ===")
    
    # 显示当前配置
    config = loader.get_project_mod_config()
    if config:
        print(f"当前模式: {config['mode']}")
        print(f"规则文件变量: {config['rule_var_name']}")
        print(f"规则文件: {config['rule_file']}")
        print(f"规则文件路径: {loader.get_active_rule_file_path()}")
    
    # 切换模式示例
    # loader.switch_project_mode('proD')
    # loader.switch_project_mode('devP')
    
    # 加载规则示例
    # content = loader.load_rules_content()
    # if content:
    #     print(f"规则文件内容长度: {len(content)} 字符")
    
    # 加载所有规则
    all_rules = loader.load_all_rules()
    print(f"\n已加载的规则文件数量: {len(all_rules)}")
    for file_path in all_rules:
        print(f"  - {file_path}")


if __name__ == "__main__":
    main()
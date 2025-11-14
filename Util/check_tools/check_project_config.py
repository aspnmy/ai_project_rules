#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件检查工具
根据db_lists.txt中的要求检查项目配置文件是否满足条件

参数:
    无
    
返回:
    无
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from db_lists_parser import DBListsParser


class ProjectConfigChecker:
    """
    项目配置文件检查器
    用于验证项目配置是否满足db_lists.txt中的要求
    """
    
    def __init__(self, project_root: str = "."):
        """
        初始化检查器
        
        参数:
            project_root (str): 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root)
        self.parser = DBListsParser()
        self.logger = self._setup_logger()
        self.issues = []
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        参数:
            无
            
        返回:
            logging.Logger: 日志记录器实例
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_all_requirements(self) -> Dict[str, any]:
        """
        检查所有项目配置要求
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果字典
        """
        self.issues = []
        results = {
            "db_lists_valid": False,
            "env_vars_set": False,
            "paths_exist": False,
            "mcp_configs_valid": False,
            "project_structure_ok": False,
            "overall_status": "FAILED",
            "issues": [],
            "recommendations": []
        }
        
        # 1. 检查db_lists.txt文件
        db_lists_result = self.check_db_lists_file()
        results["db_lists_valid"] = db_lists_result["valid"]
        if db_lists_result["issues"]:
            self.issues.extend(db_lists_result["issues"])
        
        # 2. 检查环境变量设置
        env_vars_result = self.check_environment_variables()
        results["env_vars_set"] = env_vars_result["all_set"]
        if env_vars_result["issues"]:
            self.issues.extend(env_vars_result["issues"])
        
        # 3. 检查路径存在性
        paths_result = self.check_paths_existence()
        results["paths_exist"] = paths_result["all_exist"]
        if paths_result["issues"]:
            self.issues.extend(paths_result["issues"])
        
        # 4. 检查MCP配置
        mcp_result = self.check_mcp_configurations()
        results["mcp_configs_valid"] = mcp_result["valid"]
        if mcp_result["issues"]:
            self.issues.extend(mcp_result["issues"])
        
        # 5. 检查项目结构
        structure_result = self.check_project_structure()
        results["project_structure_ok"] = structure_result["valid"]
        if structure_result["issues"]:
            self.issues.extend(structure_result["issues"])
        
        # 6. 生成建议
        results["recommendations"] = self.generate_recommendations()
        
        # 7. 总体状态
        all_checks_passed = (
            results["db_lists_valid"] and 
            results["env_vars_set"] and 
            results["paths_exist"] and 
            results["mcp_configs_valid"] and 
            results["project_structure_ok"]
        )
        
        results["overall_status"] = "PASSED" if all_checks_passed else "FAILED"
        results["issues"] = self.issues
        
        return results
    
    def check_db_lists_file(self) -> Dict[str, any]:
        """
        检查db_lists.txt文件
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果
        """
        result = {"valid": False, "issues": []}
        
        if not self.parser.db_lists_path.exists():
            result["issues"].append({
                "type": "FILE_NOT_FOUND",
                "message": "db_lists.txt 文件不存在",
                "severity": "ERROR",
                "fix": "创建 db_lists.txt 文件并添加MCP服务器配置"
            })
            return result
        
        # 解析文件
        configs = self.parser.parse_file()
        if not configs:
            result["issues"].append({
                "type": "EMPTY_FILE",
                "message": "db_lists.txt 文件为空或格式错误",
                "severity": "ERROR",
                "fix": "检查文件格式，确保使用正确的格式: mcp_server:server_name|env_var_name"
            })
            return result
        
        result["valid"] = True
        self.logger.info(f"db_lists.txt 文件有效，包含 {len(configs)} 个配置")
        return result
    
    def check_environment_variables(self) -> Dict[str, any]:
        """
        检查环境变量设置
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果
        """
        result = {"all_set": True, "missing_vars": [], "issues": []}
        
        configs = self.parser.parse_file()
        if not configs:
            result["all_set"] = False
            return result
        
        for config in configs:
            var_name = config['system_path_var']
            var_value = os.environ.get(var_name)
            
            if not var_value:
                result["missing_vars"].append(var_name)
                result["all_set"] = False
                result["issues"].append({
                    "type": "MISSING_ENV_VAR",
                    "message": f"环境变量 {var_name} 未设置",
                    "severity": "ERROR",
                    "fix": f"使用 set_SystemPathVar.py 工具设置环境变量 {var_name}"
                })
            else:
                self.logger.info(f"环境变量 {var_name} 已设置: {var_value}")
        
        return result
    
    def check_paths_existence(self) -> Dict[str, any]:
        """
        检查路径存在性
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果
        """
        result = {"all_exist": True, "missing_paths": [], "issues": []}
        
        resolved_configs = self.parser.resolve_paths()
        if not resolved_configs:
            result["all_exist"] = False
            return result
        
        for config in resolved_configs:
            actual_path = config.get('actual_path')
            if not actual_path:
                continue
            
            path_obj = Path(actual_path)
            if not path_obj.exists():
                result["missing_paths"].append(actual_path)
                result["all_exist"] = False
                result["issues"].append({
                    "type": "PATH_NOT_FOUND",
                    "message": f"路径不存在: {actual_path}",
                    "severity": "ERROR",
                    "fix": f"创建路径或检查环境变量设置: {config['system_path_var']}"
                })
            else:
                self.logger.info(f"路径存在: {actual_path}")
        
        return result
    
    def check_mcp_configurations(self) -> Dict[str, any]:
        """
        检查MCP配置
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果
        """
        result = {"valid": True, "issues": []}
        
        # 检查是否存在MCP配置文件
        mcp_config_files = [
            "mcp_filesystem_db_config.json",
            "db_config/mcp_config.json"
        ]
        
        existing_configs = []
        for config_file in mcp_config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                existing_configs.append(config_path)
        
        if not existing_configs:
            result["valid"] = False
            result["issues"].append({
                "type": "MISSING_MCP_CONFIG",
                "message": "未找到MCP配置文件",
                "severity": "WARNING",
                "fix": "运行 db_filesystem_manager.py 生成MCP配置"
            })
            return result
        
        # 验证配置文件内容
        for config_path in existing_configs:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 检查基本结构
                if 'mcpServers' not in config_data:
                    result["issues"].append({
                        "type": "INVALID_MCP_CONFIG",
                        "message": f"配置文件 {config_path} 缺少 mcpServers 字段",
                        "severity": "ERROR",
                        "fix": "重新生成MCP配置文件"
                    })
                    result["valid"] = False
                
                self.logger.info(f"MCP配置文件有效: {config_path}")
                
            except Exception as e:
                result["issues"].append({
                    "type": "CONFIG_READ_ERROR",
                    "message": f"读取配置文件失败 {config_path}: {e}",
                    "severity": "ERROR",
                    "fix": "检查配置文件格式和权限"
                })
                result["valid"] = False
        
        return result
    
    def check_project_structure(self) -> Dict[str, any]:
        """
        检查项目结构
        
        参数:
            无
            
        返回:
            Dict[str, any]: 检查结果
        """
        result = {"valid": True, "issues": []}
        
        # 检查必要的目录和文件
        required_items = [
            "db_lists.txt",
            "db_lists_parser.py",
            "set_SystemPathVar.py",
            "check_project_config.py"
        ]
        
        missing_items = []
        for item in required_items:
            item_path = self.project_root / item
            if not item_path.exists():
                missing_items.append(item)
        
        if missing_items:
            result["valid"] = False
            result["issues"].append({
                "type": "MISSING_FILES",
                "message": f"缺少必要文件: {', '.join(missing_items)}",
                "severity": "ERROR",
                "fix": "确保所有必要文件都存在"
            })
        
        # 检查配置文件目录
        config_dirs = ["db_config"]
        for config_dir in config_dirs:
            dir_path = self.project_root / config_dir
            if dir_path.exists():
                self.logger.info(f"配置目录存在: {config_dir}")
            else:
                self.logger.warning(f"配置目录不存在: {config_dir}")
        
        return result
    
    def generate_recommendations(self) -> List[str]:
        """
        生成改进建议
        
        参数:
            无
            
        返回:
            List[str]: 建议列表
        """
        recommendations = []
        
        # 基于检查结果生成建议
        if not self.parser.db_lists_path.exists():
            recommendations.append("创建 db_lists.txt 文件并添加MCP服务器配置")
        
        configs = self.parser.parse_file()
        if configs:
            missing_vars = []
            for config in configs:
                var_name = config['system_path_var']
                if not os.environ.get(var_name):
                    missing_vars.append(var_name)
            
            if missing_vars:
                recommendations.append(f"设置缺失的环境变量: {', '.join(missing_vars)}")
        
        # 检查路径
        resolved_configs = self.parser.resolve_paths()
        missing_paths = [c.get('actual_path') for c in resolved_configs 
                        if c.get('actual_path') and not Path(c['actual_path']).exists()]
        
        if missing_paths:
            recommendations.append(f"创建缺失的路径或修正环境变量: {', '.join(missing_paths)}")
        
        # MCP配置建议
        mcp_config_files = [
            "mcp_filesystem_db_config.json",
            "db_config/mcp_config.json"
        ]
        
        existing_configs = []
        for config_file in mcp_config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                existing_configs.append(config_path)
        
        if not existing_configs:
            recommendations.append("生成MCP配置文件以启用数据库管理功能")
        
        # 安全建议
        recommendations.append("定期备份数据库文件")
        recommendations.append("确保环境变量名称足够复杂以避免冲突")
        recommendations.append("使用强密码保护数据库文件")
        
        return recommendations
    
    def print_report(self):
        """
        打印检查报告
        
        参数:
            无
            
        返回:
            无
        """
        results = self.check_all_requirements()
        
        print("\n" + "=" * 70)
        print("项目配置检查报告")
        print("=" * 70)
        
        # 总体状态
        status_color = "✓" if results["overall_status"] == "PASSED" else "✗"
        print(f"总体状态: {status_color} {results['overall_status']}")
        print()
        
        # 详细检查结果
        checks = [
            ("db_lists_valid", "db_lists.txt 文件"),
            ("env_vars_set", "环境变量设置"),
            ("paths_exist", "路径存在性"),
            ("mcp_configs_valid", "MCP配置"),
            ("project_structure_ok", "项目结构")
        ]
        
        for check_key, check_name in checks:
            status = "✓" if results[check_key] else "✗"
            print(f"{status} {check_name}")
        
        print()
        
        # 问题列表
        if results["issues"]:
            print("发现的问题:")
            print("-" * 40)
            for i, issue in enumerate(results["issues"], 1):
                severity = issue.get("severity", "INFO")
                message = issue.get("message", "")
                fix = issue.get("fix", "")
                
                print(f"{i}. [{severity}] {message}")
                if fix:
                    print(f"   建议: {fix}")
                print()
        
        # 改进建议
        if results["recommendations"]:
            print("改进建议:")
            print("-" * 40)
            for i, recommendation in enumerate(results["recommendations"], 1):
                print(f"{i}. {recommendation}")
            print()
        
        print("=" * 70)


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        无
    """
    checker = ProjectConfigChecker()
    checker.print_report()


if __name__ == "__main__":
    main()